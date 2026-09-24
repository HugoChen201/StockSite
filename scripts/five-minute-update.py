#!/usr/bin/env python3
"""5-minute light refresh for Hugo's Stock Watchlist GitHub Pages site.

Priority order (Hugo's): (1) market internals, (2) earnings expected moves, (3) overview quotes.
Potential Trades stays on the 7:30 AM ET morning scan only.

Runs only Mon-Fri 9:30 AM-4:00 PM America/New_York on US trading days; exits quietly otherwise.
Never invents numbers: any unreachable source keeps its last-good value.
Usage: five-minute-update.py [--force]   (--force bypasses the market-hours guard, for testing)
"""

import json
import os
import subprocess
import sys
import http.cookiejar
import urllib.parse
import urllib.request
import datetime as dt
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from git_lock import locked

ET = ZoneInfo("America/New_York")
REPO = Path.home() / "workspace" / "StockSite"
LOG = Path.home() / "workspace" / "goals" / "stock-watchlist-website" / "hidden_files" / "five-minute-runs.log"
HOLIDAYS_2026 = {
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25",
    "2026-06-19", "2026-07-03", "2026-09-07", "2026-11-26", "2026-12-25",
}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}


def now_et():
    return dt.datetime.now(ET)


def stamp(d=None):
    return (d or now_et()).strftime("%b %d, %Y %-I:%M %p ET")


def market_open(d=None):
    d = d or now_et()
    if d.strftime("%Y-%m-%d") in HOLIDAYS_2026 or d.weekday() >= 5:
        return False
    mins = d.hour * 60 + d.minute
    return 9 * 60 + 30 <= mins < 16 * 60


def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"{stamp()} | {msg}\n")


def get_json(url, timeout=12):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def yahoo_meta(symbol):
    """(price, prev_close, volume) or None."""
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=1d&interval=1d" % urllib.parse.quote(symbol)
        meta = get_json(url)["chart"]["result"][0]["meta"]
        price = meta.get("regularMarketPrice")
        prev = meta.get("chartPreviousClose") or meta.get("previousClose")
        if price is None or prev is None or prev == 0:
            return None
        return (float(price), float(prev), meta.get("regularMarketVolume"))
    except Exception:
        return None


def batch_quotes(symbols):
    out = {}

    def one(s):
        out[s] = yahoo_meta(s)

    with ThreadPoolExecutor(max_workers=12) as ex:
        list(ex.map(one, symbols))
    return out


def spy_intraday_smi(series_last):
    """SMI intraday: series_last - first30min%gain + lastHour%change. Returns (value, inputs) or (None, None)."""
    try:
        d = get_json("https://query1.finance.yahoo.com/v8/finance/chart/SPY?range=1d&interval=1m")
        res = d["chart"]["result"][0]
        ts, q = res["timestamp"], res["indicators"]["quote"][0]
        opens, closes = q["open"], q["close"]
        bars = []
        for i, t in enumerate(ts):
            if opens[i] is None or closes[i] is None:
                continue
            bars.append((dt.datetime.fromtimestamp(t, ET), float(opens[i]), float(closes[i])))
        if len(bars) < 70:
            return None, None
        day = bars[0][0].date()
        m930 = next((b for b in bars if b[0].date() == day and (b[0].hour, b[0].minute) >= (9, 30)), None)
        m1000 = next((b for b in reversed(bars) if b[0].date() == day and (b[0].hour, b[0].minute) <= (10, 0)), None)
        if not m930 or not m1000:
            return None, None
        first30 = (m1000[2] - m930[1]) / m930[1] * 100
        last = bars[-1]
        ref_ts = last[0].timestamp() - 3600
        ref = next((b for b in reversed(bars) if b[0].timestamp() <= ref_ts), bars[0])
        last60 = (last[2] - ref[2]) / ref[2] * 100
        val = series_last - first30 + last60
        inputs = ("SPY open %.2f; 10:00 %.2f (%+.4f%%); last hour %.2f -> %.2f (%+.4f%%). "
                  "%.2f - %.4f + %.4f = %.2f." % (m930[1], m1000[2], first30, ref[2], last[2], last60,
                                                 series_last, first30, last60, val))
        return round(val, 2), inputs
    except Exception:
        return None, None


def fear_greed():
    try:
        fg = get_json("https://production.dataviz.cnn.io/index/fearandgreed/graphdata", timeout=10)["fear_and_greed"]
        return float(fg["score"]), str(fg["rating"])
    except Exception:
        return None, None


_crumb = None
_opener = None


def yahoo_options_json(url):
    """Yahoo v7 options endpoint requires a crumb; fetch via a cookie session. Raises on failure."""
    global _crumb, _opener
    last_err = None
    for attempt in range(2):  # one retry with a fresh session
        try:
            if _opener is None:
                jar = http.cookiejar.CookieJar()
                _opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
                _opener.open(urllib.request.Request("https://fc.yahoo.com", headers=UA), timeout=10)
                crumb_req = urllib.request.Request("https://query1.finance.yahoo.com/v1/test/getcrumb", headers=UA)
                _crumb = _opener.open(crumb_req, timeout=10).read().decode()
            sep = "&" if "?" in url else "?"
            req = urllib.request.Request(url + sep + "crumb=" + _crumb, headers=UA)
            with _opener.open(req, timeout=12) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            last_err = e
            _opener = None  # force a fresh session next attempt
    raise last_err


def expected_move(symbol, price):
    """Front-month ATM straddle-implied expected move %, or None."""
    try:
        sym = urllib.parse.quote(symbol)
        res = yahoo_options_json(
            f"https://query1.finance.yahoo.com/v7/finance/options/{sym}")["optionChain"]["result"][0]
        under = res["quote"].get("regularMarketPrice") or price
        today = now_et().date()
        exps = [e for e in res.get("expirationDates", [])
                if dt.datetime.fromtimestamp(e, ET).date() >= today + dt.timedelta(days=5)]
        if not exps:
            return None
        chain = yahoo_options_json(
            f"https://query1.finance.yahoo.com/v7/finance/options/{sym}?date={exps[0]}")["optionChain"]["result"][0]
        calls = chain["options"][0]["calls"]
        put_by_strike = {p["strike"]: p for p in chain["options"][0]["puts"]}

        def mid(o):
            b, a = o.get("bid"), o.get("ask")
            if b is not None and a is not None and a > 0:
                return (b + a) / 2
            return o.get("lastPrice")

        best = None
        for c in calls:
            p = put_by_strike.get(c["strike"])
            if not p:
                continue
            cm, pm = mid(c), mid(p)
            if cm is None or pm is None:
                continue
            diff = abs(c["strike"] - under)
            if best is None or diff < best[0]:
                best = (diff, cm + pm)
        if not best:
            return None
        return round(best[1] / under * 100, 1)
    except Exception:
        return None


def git(*args):
    return subprocess.run(["git"] + list(args), cwd=REPO, capture_output=True, text=True, timeout=60)


def main():
    force = "--force" in sys.argv
    t0 = now_et()
    if not force and not market_open(t0):
        log("SKIP market closed")
        print("SKIP market closed")
        return 0

    try:
        with locked(timeout=50):
            git("pull", "--ff-only")
            data = json.load(open(REPO / "data.json"))
            stages = []
            ts = stamp(t0)

            # ---------- one batch quote pull for watchlist + internals symbols ----------
            ysyms, y2t = [], {}
            for s in data["STOCKS"]:
                ys = s.get("yahoo_symbol") or s["ticker"]
                ysyms.append(ys)
                y2t[ys] = s["ticker"]
            # also quote earnings-calendar names not in the watchlist (future-proof)
            have_tickers = {s["ticker"] for s in data["STOCKS"]}
            for e in data.get("EARNINGS_DATES", []):
                t = e.get("ticker")
                if t and t not in have_tickers:
                    ysyms.append(t)
                    y2t[t] = t
                    have_tickers.add(t)
            etf_list = [s["etf"] for s in data["SECTOR_BREADTH"]]
            qmap = batch_quotes(ysyms + ["^VIX", "^VIX3M"] + etf_list)

            # ================= STAGE 1: market internals =================
            mi = data["MARKET_INTERNALS"]

            # VIX spot + 3M term structure
            vix, vix3m = qmap.get("^VIX"), qmap.get("^VIX3M")
            if vix and vix3m:
                sp, spp = vix[0], vix[1]
                tp, tpp = vix3m[0], vix3m[1]
                vt = mi["vixTerm"]
                vt["spot"] = round(sp, 2)
                vt["spotChange"] = round(sp - spp, 2)
                vt["spotChangePct"] = round((sp - spp) / spp * 100, 2)
                vt["threeMonth"] = round(tp, 2)
                vt["threeMonthChangePct"] = round((tp - tpp) / tpp * 100, 2)
                vt["ratio"] = round(tp / sp, 2)
                vt["state"] = "Contango (calm)" if tp > sp else "Backwardation (stress)"
                vt["asof"] = ts
                stages.append("vix")

            # CNN Fear & Greed
            score, rating = fear_greed()
            if score is not None:
                fg = mi["fearGreed"]
                fg["value"] = round(score, 2)
                fg["label"] = rating
                fg["asof"] = ts
                stages.append("fearGreed")

            # Sector breadth heatmap (intraday % vs previous close)
            n_sec = 0
            for s in data["SECTOR_BREADTH"]:
                m = qmap.get(s["etf"])
                if m:
                    p, prev = m[0], m[1]
                    s["close"] = round(p, 2)
                    s["previous"] = round(prev, 2)
                    s["change"] = round((p - prev) / prev * 100, 2)
                    n_sec += 1
            if n_sec:
                data["ASOF"]["sectorBreadth"] = ts
                stages.append(f"sectors({n_sec})")

            # SMI intraday (Don Hays-style, self-computed)
            series = mi["smi"].get("series", [])
            if series:
                val, inputs = spy_intraday_smi(series[-1]["value"])
                if val is not None:
                    mi["smi"]["intraday"] = val
                    mi["smi"]["intradayAsOf"] = ts
                    mi["smi"]["intradayInputs"] = inputs
                    stages.append("smi")
            data["ASOF"]["internals"] = ts
            # NOTE: breadth (A/D, new highs/lows, %above MA) and put/call come from Barchart/YCharts,
            # which block plain server requests; they stay on the 7:30 AM morning browser cycle.

            # ================= STAGE 2: earnings expected moves (7-day window) =================
            today = t0.date()
            window = [e for e in data["EARNINGS_DATES"]
                      if today <= dt.date.fromisoformat(e["date"]) <= today + dt.timedelta(days=7)]
            n_em = 0
            for e in window:
                tkr = e["ticker"]
                m = qmap.get(next((ys for ys, t in y2t.items() if t == tkr), tkr))
                price = m[0] if m else None
                if not price:
                    continue
                mv = expected_move(next((ys for ys, t in y2t.items() if t == tkr), tkr), price)
                if mv is not None:
                    e["expected_move"] = mv
                    e["move_as_of"] = today.isoformat()
                    if tkr in data.get("EXPECTED_MOVES", {}):
                        data["EXPECTED_MOVES"][tkr]["move"] = mv
                    n_em += 1
            if n_em:
                data["ASOF"]["expectedMoves"] = ts
                stages.append(f"expMoves({n_em})")

            # ================= STAGE 3: overview quotes =================
            quotes = {}
            for ys, tkr in y2t.items():
                m = qmap.get(ys)
                if m:
                    p, prev = m[0], m[1]
                    quotes[tkr] = {"price": round(p, 2), "changePct": round((p - prev) / prev * 100, 2),
                                   "volume": m[2], "asof": ts}
            data["QUOTES"] = quotes
            data["ASOF"]["quotes"] = ts
            stages.append(f"quotes({len(quotes)})")

            # ---------- publish ----------
            patch = {"MARKET_INTERNALS": mi, "SECTOR_BREADTH": data["SECTOR_BREADTH"],
                     "EARNINGS_DATES": data["EARNINGS_DATES"], "EXPECTED_MOVES": data["EXPECTED_MOVES"],
                     "QUOTES": quotes, "ASOF": data["ASOF"]}
            patch_path = "/tmp/five-minute-patch.json"
            json.dump(patch, open(patch_path, "w"))
            # update-data.py takes the shared lock itself; tell it we already hold
            # it (a child flock on a new fd would block forever against our lock).
            child_env = dict(os.environ, STOCKSITE_DATA_LOCK="1")
            r = subprocess.run(["python3", "scripts/update-data.py", patch_path], cwd=REPO,
                               capture_output=True, text=True, timeout=60, env=child_env)
            print(r.stdout.strip() or r.stderr.strip())
            if r.returncode != 0:
                log("ERROR update-data.py failed: " + r.stderr.strip()[:200])
                return 1
            version = json.load(open(REPO / "data.json"))["version"]

            git("add", "data.json")
            git("commit", "-m", f"5-min refresh {t0.strftime('%Y-%m-%d %H:%M')} ET")
            push = git("push")
            push_status = "ok"
            if push.returncode != 0:
                git("pull", "--rebase")
                push = git("push")
                push_status = "ok-after-rebase" if push.returncode == 0 else "FAILED"
            log(f"RUN stages={'+'.join(stages)} v={version} push={push_status}")
            print(f"RUN stages={'+'.join(stages)} v={version} push={push_status}")
            return 0 if push_status != "FAILED" else 1
    except TimeoutError:
        log("SKIP lock busy (another writer holds it; next run picks up)")
        print("SKIP lock busy")
        return 0

if __name__ == "__main__":
    sys.exit(main())
