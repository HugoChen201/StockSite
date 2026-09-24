#!/usr/bin/env python3
"""Backfill real data for earnings-calendar tickers that are not full watchlist
members (e.g. ACN, NKE, DRI, SNX, JEF, JBL), so their overview detail pages show
a price chart, key stats, sector, and annual revenue/net-income history instead
of empty placeholders.

Idempotent. Safe to run daily (morning refresh cron): only tickers present in
EARNINGS_DATES but missing from STOCKS are processed, price history is topped
up by date, and fundamentals refresh when older than 7 days.

Sources (all keyless):
  - Yahoo Finance chart API v8 : 1y daily bars (adjusted close)
  - CNBC quote API             : market cap, P/E, forward P/E, EPS, beta, yield,
                                 margins, 52-week range, revenue/EBITDA TTM, exchange
  - Nasdaq financials API      : annual total revenue + net income (FY history)

Writes HISTORY (top-up) and CALENDAR_META into data.json via update-data.py,
refreshes the embedded HISTORY fallback line in app.js, then commits + pushes.
The whole pull -> patch -> commit -> push sequence holds the shared git lock.

Never invents numbers: any fetch failure keeps last-good values and the ticker
is skipped with a warning.
"""
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from git_lock import locked  # noqa: E402

REPO = Path("/home/hatch/workspace/StockSite")
DATA_PATH = REPO / "data.json"
APP_JS = REPO / "app.js"
ET = ZoneInfo("America/New_York")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

# Sector/industry verified 2026-09-23 via web research (digrin/finnhub/kraken).
# Tickers not listed here keep sector/industry null (graceful in the UI).
SECTOR_MAP = {
    "ACN": ("Technology", "Information Technology Services"),
    "NKE": ("Consumer Cyclical", "Footwear & Accessories"),
    "DRI": ("Consumer Cyclical", "Restaurants"),
    "SNX": ("Technology", "Electronics & Computer Distribution"),
    "JEF": ("Financial Services", "Capital Markets"),
    "JBL": ("Technology", "Electronic Components"),
}

FUND_TTL_DAYS = 7


def log(msg):
    print(f"[enrich-calendar] {msg}", flush=True)


def get_json(url, timeout=25):
    req = urllib.request.Request(url, headers={**UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def p_compact(s):
    """'112.304B' / '611.94M' -> float dollars."""
    if s is None:
        return None
    s = str(s).replace(",", "").strip()
    if not s:
        return None
    mult = {"T": 1e12, "B": 1e9, "M": 1e6, "K": 1e3}
    try:
        if s[-1] in mult:
            return float(s[:-1]) * mult[s[-1]]
        return float(s)
    except ValueError:
        return None


def p_pct(s):
    """'10.86%' -> 0.1086"""
    if s is None:
        return None
    try:
        return float(str(s).replace("%", "").strip()) / 100
    except ValueError:
        return None


def p_num(s):
    if s is None:
        return None
    try:
        return float(str(s).replace(",", "").strip())
    except ValueError:
        return None


def p_money(s):
    """'$69,672,977' -> 69672977.0"""
    if s is None:
        return None
    try:
        return float(str(s).replace("$", "").replace(",", "").strip())
    except ValueError:
        return None


def yahoo_daily(ticker):
    """Returns (bars, exchange_name). bars: [{d,o,h,l,c}] with c = adjusted close."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1y"
    d = get_json(url)
    r = d["chart"]["result"][0]
    ts = r["timestamp"]
    q = r["indicators"]["quote"][0]
    adj = r["indicators"]["adjclose"][0]["adjclose"]
    bars = []
    for i, epoch in enumerate(ts):
        c = adj[i] if i < len(adj) else None
        if c is None:
            continue
        day = datetime.fromtimestamp(epoch, ET).date().isoformat()
        o, h, l = (q[k][i] if i < len(q[k]) else None for k in ("open", "high", "low"))
        bars.append({
            "d": day,
            "o": round(o, 2) if o else None,
            "h": round(h, 2) if h else None,
            "l": round(l, 2) if l else None,
            "c": round(c, 2),
        })
    return bars, r["meta"].get("exchangeName")


def cnbc_quote(ticker):
    url = ("https://quote.cnbc.com/quote-html-webservice/restQuote/symbolType/symbol"
           f"?symbols={ticker}&requestMethod=itv&noform=1&partnerId=2&fund=1&exthrs=1&output=json")
    d = get_json(url)
    return d["FormattedQuoteResult"]["FormattedQuote"][0]


def nasdaq_annuals(ticker):
    """Returns (years, revenue_b, net_income_b, latest_period) or Nones."""
    url = f"https://api.nasdaq.com/api/company/{ticker}/financials?frequency=1"
    d = get_json(url)
    t = d["data"]["incomeStatementTable"]
    hdr = t["headers"]
    cols = [k for k in ("value2", "value3", "value4", "value5") if k in hdr]
    years, revs, nis = [], [], []
    latest_period = None
    for k in cols:
        per = hdr[k]  # '8/31/2025'
        try:
            m, day, y = per.split("/")
            years.append(int(y))
            if latest_period is None:
                latest_period = f"{y}-{int(m):02d}-{int(day):02d}"
        except ValueError:
            continue
    rows = {r["value1"]: [r.get(k) for k in cols] for r in t["rows"]}
    rev_raw = rows.get("Total Revenue", [])
    ni_raw = rows.get("Net Income", [])
    # values are in $thousands -> /1e6 = $billions
    revs = [p_money(v) / 1e6 if p_money(v) is not None else None for v in rev_raw[: len(years)]]
    nis = [p_money(v) / 1e6 if p_money(v) is not None else None for v in ni_raw[: len(years)]]
    return years, revs, nis, latest_period


def build_fundamentals(q):
    return {
        "marketCap": p_compact(q.get("mktcapView")),
        "trailingPE": p_num(q.get("pe")),
        "forwardPE": p_num(q.get("fpe")),
        "trailingEps": p_num(q.get("eps")),
        "forwardEps": p_num(q.get("feps")),
        "pegRatio": None,
        "priceToBook": None,
        "priceToSalesTrailing12Months": p_num(q.get("psales")),
        "enterpriseToEbitda": None,
        "beta": p_num(q.get("beta")),
        "dividendYield": p_pct(q.get("dividendyield")),
        "fiftyTwoWeekLow": p_num(q.get("yrloprice")),
        "fiftyTwoWeekHigh": p_num(q.get("yrhiprice")),
        "grossMargins": p_pct(q.get("GROSMGNTTM")),
        "operatingMargins": None,
        "profitMargins": p_pct(q.get("NETPROFTTM")),
        "returnOnEquity": p_pct(q.get("ROETTM")),
        "returnOnAssets": None,
        "revenueGrowth": None,
        "earningsGrowth": None,
    }


def enrich_ticker(ticker, existing_meta, existing_history):
    """Returns (bars_or_None, meta_or_None). Never raises."""
    today = datetime.now(ET).date()
    bars = None
    try:
        bars, _ex = yahoo_daily(ticker)
        log(f"{ticker}: {len(bars)} daily bars from Yahoo")
    except Exception as e:
        log(f"{ticker}: Yahoo history failed ({e}); keeping last-good")
    meta = dict(existing_meta) if existing_meta else None
    as_of = None
    if meta:
        try:
            as_of = datetime.strptime(meta.get("as_of", ""), "%Y-%m-%d").date()
        except ValueError:
            as_of = None
    stale = as_of is None or (today - as_of).days >= FUND_TTL_DAYS
    if stale:
        try:
            q = cnbc_quote(ticker)
            sector, industry = SECTOR_MAP.get(ticker, (None, None))
            exch = (q.get("exchange") or "").upper()
            tv = f"{exch}:{ticker}" if exch in ("NYSE", "NASDAQ", "AMEX") else ticker
            years, revs, nis, period = nasdaq_annuals(ticker)
            meta = {
                "sector": sector,
                "industry": industry,
                "tv_symbol": tv,
                "period": period,
                "fundamentals": build_fundamentals(q),
                "statements": {
                    "Total Revenue": p_compact(q.get("revenuettm")),
                    "EBITDA": p_compact(q.get("TTMEBITD")),
                },
                "earnings": {
                    "years": years,
                    "revenue_b": [round(v, 2) if v is not None else None for v in revs],
                    "eps": [None] * len(years),
                    "net_income_b": [round(v, 2) if v is not None else None for v in nis],
                },
                "as_of": today.isoformat(),
            }
            log(f"{ticker}: fundamentals refreshed (mcap={meta['fundamentals']['marketCap']})")
        except Exception as e:
            log(f"{ticker}: fundamentals refresh failed ({e}); keeping last-good")
            meta = dict(existing_meta) if existing_meta else None
    else:
        log(f"{ticker}: fundamentals fresh as of {as_of}")
    return bars, meta


def main():
    with locked():
        subprocess.run(["git", "pull", "--ff-only"], cwd=str(REPO),
                       capture_output=True)
        data = json.load(open(DATA_PATH))
        have = {s["ticker"] for s in data["STOCKS"]}
        targets = [e["ticker"] for e in data.get("EARNINGS_DATES", [])
                   if e.get("ticker") and e["ticker"] not in have]
        if not targets:
            log("no calendar-only tickers; nothing to do")
            return 0
        log(f"targets: {targets}")
        history = data.get("HISTORY", {})
        cmeta = data.get("CALENDAR_META", {})
        changed = False
        for t in targets:
            bars, meta = enrich_ticker(t, cmeta.get(t), history.get(t))
            if bars:
                merged = {b["d"]: b for b in history.get(t, [])}
                for b in bars:
                    merged[b["d"]] = b
                history[t] = sorted(merged.values(), key=lambda b: b["d"])[-260:]
                changed = True
            if meta:
                cmeta[t] = meta
                changed = True
        if not changed:
            log("all fetches failed; data.json untouched")
            return 0
        # apply patch under the same lock via update-data.py
        patch = {"HISTORY": history, "CALENDAR_META": cmeta}
        patch_path = "/tmp/enrich-calendar-patch.json"
        json.dump(patch, open(patch_path, "w"))
        r = subprocess.run([sys.executable, str(REPO / "scripts" / "update-data.py"),
                            patch_path], cwd=str(REPO), capture_output=True, text=True,
                           env={**dict(os.environ),
                                "STOCKSITE_DATA_LOCK": "1"})
        print(r.stdout.strip())
        if r.returncode != 0:
            print(r.stderr.strip(), file=sys.stderr)
            return 1
        # refresh the embedded HISTORY fallback line in app.js
        new_data = json.load(open(DATA_PATH))
        app_txt = APP_JS.read_text()
        lines = app_txt.split("\n")
        new_line = "let HISTORY = " + json.dumps(new_data["HISTORY"],
                                                 separators=(",", ":")) + ";"
        hit = [i for i, ln in enumerate(lines) if ln.startswith("let HISTORY = ")]
        assert len(hit) == 1, f"expected 1 embedded HISTORY line, found {len(hit)}"
        lines[hit[0]] = new_line
        # embedded CALENDAR_META fallback (single declaration lives here; the
        # code section only assigns to it on data.json refresh)
        cm_line = "let CALENDAR_META = " + json.dumps(new_data.get("CALENDAR_META", {}),
                                                      separators=(",", ":")) + ";"
        cm_hit = [i for i, ln in enumerate(lines) if ln.startswith("let CALENDAR_META = ")]
        if len(cm_hit) == 1:
            lines[cm_hit[0]] = cm_line
        else:
            assert not cm_hit, f"unexpected CALENDAR_META lines: {len(cm_hit)}"
            lines.insert(hit[0] + 1, cm_line)
        APP_JS.write_text("\n".join(lines))
        log(f"app.js embedded HISTORY refreshed ({len(new_data['HISTORY'])} tickers)")
        # commit + push
        subprocess.run(["git", "add", "data.json", "app.js", "index.html"], cwd=str(REPO),
                       check=True)
        msg = ("Enrich earnings-calendar names with price history + fundamentals "
               f"({', '.join(targets)})")
        cr = subprocess.run(["git", "commit", "-m", msg], cwd=str(REPO),
                            capture_output=True, text=True)
        if cr.returncode != 0:
            log("nothing to commit")
            return 0
        pr = subprocess.run(["git", "push", "origin", "main"], cwd=str(REPO),
                            capture_output=True, text=True)
        if pr.returncode != 0:
            log(f"push failed: {pr.stderr.strip()[:200]}")
            return 1
        log("pushed " + cr.stdout.strip().split("\n")[0])
        return 0


if __name__ == "__main__":
    sys.exit(main())
