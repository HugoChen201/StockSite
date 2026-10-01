#!/usr/bin/env python3
"""One-time backfill: % of S&P 500 above 50-day / 200-day EMA (self-computed).

Fetches 1 year of daily closes for every S&P 500 constituent (constituent list
from hidden_files/universe/snapshot.json, refreshed monthly by
build-universe.py), seeds EMA-50/200 with the SMA of the first 50/200 closes,
walks forward, and aggregates the daily share of names with close > EMA.

Writes (via update-data.py under the shared lock):
  - UNIVERSE_EMA   {TICKER: {ema50, ema200, asof}}   (latest EMA state per name)
  - BREADTH_SERIES [{d, above50, above200, n}]       (daily series; only days
                                                     with n >= 400 names)

Never invents numbers: tickers whose history fetch fails are skipped (they
simply don't count toward n that day); a failed run aborts without patching.
"""
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path.home() / "workspace" / "StockSite"
SNAP_PATH = (Path.home() / "workspace" / "goals" / "stock-watchlist-website"
             / "hidden_files" / "universe" / "snapshot.json")
PATCH_PATH = Path("/tmp/breadth_backfill_patch.json")

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
ET = ZoneInfo("America/New_York")
MIN_NAMES = 400


def log(msg):
    print(f"[backfill-breadth] {msg}", flush=True)


def get_json(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def daily_closes(ticker):
    """Returns [(date_iso, close)] for the last ~2y, or None on failure."""
    try:
        url = ("https://query1.finance.yahoo.com/v8/finance/chart/%s"
               "?range=2y&interval=1d" % urllib.parse.quote(ticker))
        res = get_json(url)["chart"]["result"][0]
        ts = res.get("timestamp") or []
        closes = (res.get("indicators", {}).get("quote") or [{}])[0].get("close") or []
        out = []
        for t, c in zip(ts, closes):
            if c is None:
                continue
            d = datetime.fromtimestamp(t, ET).date().isoformat()
            out.append((d, float(c)))
        return out if len(out) >= 210 else None
    except Exception:
        return None


def ema_walk(closes):
    """closes: [(date, close)]. Returns {date: (ema50, ema200)} for days where
    both EMAs are seeded (needs 200 closes)."""
    n = len(closes)
    if n < 200:
        return {}
    k50, k200 = 2 / 51.0, 2 / 201.0
    e50 = sum(c for _, c in closes[:50]) / 50.0
    for i in range(50, 200):  # warm EMA-50 up to the EMA-200 seed point
        e50 = closes[i][1] * k50 + e50 * (1 - k50)
    e200 = sum(c for _, c in closes[:200]) / 200.0
    out = {}
    for i in range(200, n):
        d, c = closes[i]
        e50 = c * k50 + e50 * (1 - k50)
        e200 = c * k200 + e200 * (1 - k200)
        out[d] = (e50, e200)
    return out


def main():
    snap = json.load(open(SNAP_PATH))
    tickers = [e["ticker"] for e in snap["sp500"]]
    log(f"fetching 1y daily closes for {len(tickers)} S&P 500 names...")

    histories = {}
    with ThreadPoolExecutor(max_workers=12) as pool:
        for t, bars in zip(tickers, pool.map(daily_closes, tickers)):
            if bars:
                histories[t] = bars
    log(f"histories ok: {len(histories)}/{len(tickers)}")
    if len(histories) < MIN_NAMES:
        log("too few histories — aborting, no patch")
        return 1

    # per-ticker EMA walks
    per_date = {}   # date -> [above50_count, above200_count, n]
    ema_state = {}
    for t, bars in histories.items():
        walk = ema_walk(bars)
        if not walk:
            continue
        by_date = dict(bars)
        last_d = max(walk)
        e50, e200 = walk[last_d]
        ema_state[t] = {"ema50": round(e50, 4), "ema200": round(e200, 4),
                        "asof": last_d}
        for d, (a50, a200) in walk.items():
            c = by_date[d]
            cell = per_date.setdefault(d, [0, 0, 0])
            cell[2] += 1
            if c > a50:
                cell[0] += 1
            if c > a200:
                cell[1] += 1

    series = [{"d": d,
               "above50": round(100.0 * v[0] / v[2], 2),
               "above200": round(100.0 * v[1] / v[2], 2),
               "n": v[2]}
              for d, v in sorted(per_date.items()) if v[2] >= MIN_NAMES]
    log(f"series days: {len(series)} (first {series[0]['d']}, last {series[-1]['d']})")
    log(f"latest: {series[-1]['above50']}% above 50d EMA, "
        f"{series[-1]['above200']}% above 200d EMA (n={series[-1]['n']})")

    PATCH_PATH.write_text(json.dumps({"UNIVERSE_EMA": ema_state,
                                      "BREADTH_SERIES": series}))

    sys.path.insert(0, str(REPO / "scripts"))
    from git_lock import locked
    with locked():
        subprocess.run(["git", "pull", "--ff-only"], cwd=str(REPO),
                       capture_output=True, check=False)
        r = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "update-data.py"),
             str(PATCH_PATH)], cwd=str(REPO), capture_output=True, text=True,
            env={**dict(os.environ), "STOCKSITE_DATA_LOCK": "1"})
        print(r.stdout.strip())
        if r.returncode != 0:
            print(r.stderr.strip(), file=sys.stderr)
            return 1
        subprocess.run(["git", "add", "data.json"], cwd=str(REPO), check=True)
        cr = subprocess.run(
            ["git", "commit", "-m",
             f"Breadth EMA backfill: % of S&P 500 above 50/200d EMA "
             f"({len(series)} days, n~{series[-1]['n']})"],
            cwd=str(REPO), capture_output=True, text=True)
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
