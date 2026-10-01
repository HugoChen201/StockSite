#!/usr/bin/env python3
"""Daily roll-forward of the S&P 500 EMA-breadth series (self-computed).

Reads UNIVERSE_EMA + BREADTH_SERIES from data.json and the constituent list
from hidden_files/universe/snapshot.json, fetches the last few days of closes
per name (threaded Yahoo v8), rolls each EMA forward over new trading days,
recomputes the daily % above 50-day / 200-day EMA, and appends (or refreshes)
the latest reading.

Constituent changes (monthly refresh via build-universe.py):
  - new names: seeded from a 2y history fetch (same EMA seeding as the backfill)
  - removed names: dropped from UNIVERSE_EMA

Intended to be called by the morning refresh job after its push. Idempotent:
re-running the same day refreshes that day's reading in place. Never invents
numbers: names whose fetch fails keep their last-good EMA state and are left
out of the day's n.
"""
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path.home() / "workspace" / "StockSite"
SNAP_PATH = (Path.home() / "workspace" / "goals" / "stock-watchlist-website"
             / "hidden_files" / "universe" / "snapshot.json")
PATCH_PATH = Path("/tmp/breadth_daily_patch.json")

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
ET = ZoneInfo("America/New_York")
K50, K200 = 2 / 51.0, 2 / 201.0


def log(msg):
    print(f"[update-breadth] {msg}", flush=True)


def get_json(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def closes_for(ticker, rng):
    try:
        url = ("https://query1.finance.yahoo.com/v8/finance/chart/%s"
               "?range=%s&interval=1d" % (urllib.parse.quote(ticker), rng))
        res = get_json(url)["chart"]["result"][0]
        ts = res.get("timestamp") or []
        closes = (res.get("indicators", {}).get("quote") or [{}])[0].get("close") or []
        out = []
        for t, c in zip(ts, closes):
            if c is None:
                continue
            out.append((datetime.fromtimestamp(t, ET).date().isoformat(), float(c)))
        return out
    except Exception:
        return []


def seed_ema(bars):
    """bars: 2y of (date, close). Returns (ema50, ema200) warmed to last bar."""
    n = len(bars)
    if n < 200:
        return None
    e50 = sum(c for _, c in bars[:50]) / 50.0
    for i in range(50, 200):
        e50 = bars[i][1] * K50 + e50 * (1 - K50)
    e200 = sum(c for _, c in bars[:200]) / 200.0
    for i in range(200, n):
        c = bars[i][1]
        e50 = c * K50 + e50 * (1 - K50)
        e200 = c * K200 + e200 * (1 - K200)
    return e50, e200


def main():
    data = json.load(open(REPO / "data.json"))
    ema_state = data.get("UNIVERSE_EMA", {})
    series = data.get("BREADTH_SERIES", [])
    tickers = [e["ticker"] for e in json.load(open(SNAP_PATH))["sp500"]]
    have = set(ema_state)

    new_names = [t for t in tickers if t not in have]
    gone_names = [t for t in have if t not in set(tickers)]
    for t in gone_names:
        del ema_state[t]
    if gone_names:
        log(f"dropped {len(gone_names)} removed constituents: {gone_names[:8]}")

    # seed brand-new constituents from 2y history
    if new_names:
        log(f"seeding {len(new_names)} new constituents...")
        with ThreadPoolExecutor(max_workers=12) as pool:
            for t, bars in zip(new_names, pool.map(lambda x: closes_for(x, "2y"), new_names)):
                s = seed_ema(bars)
                if s and bars:
                    ema_state[t] = {"ema50": round(s[0], 4), "ema200": round(s[1], 4),
                                    "asof": bars[-1][0]}
        log(f"seeded ok: {sum(1 for t in new_names if t in ema_state)}/{len(new_names)}")

    # roll every name forward over new trading days
    log(f"rolling {len(tickers)} names...")
    with ThreadPoolExecutor(max_workers=12) as pool:
        recent = dict(zip(tickers, pool.map(lambda x: closes_for(x, "5d"), tickers)))

    per_name = {}  # ticker -> (date, close, ema50, ema200)
    for t in tickers:
        st = ema_state.get(t)
        bars = recent.get(t) or []
        if not st or not bars:
            continue
        e50, e200, asof = st["ema50"], st["ema200"], st["asof"]
        for d, c in bars:
            if d <= asof:
                continue
            e50 = c * K50 + e50 * (1 - K50)
            e200 = c * K200 + e200 * (1 - K200)
            asof = d
        ema_state[t] = {"ema50": round(e50, 4), "ema200": round(e200, 4),
                        "asof": asof}
        d_last, c_last = bars[-1]
        # EMAs are warmed through `asof`; the latest fetched bar is the
        # freshest known close (on reruns asof already equals it)
        per_name[t] = (d_last, c_last, e50, e200)
    if not per_name:
        log("no new trading days — nothing to append")
        return 0

    day = max(v[0] for v in per_name.values())
    todays = [v for v in per_name.values() if v[0] == day]
    n = len(todays)
    a50 = sum(1 for _, c, e50, _ in todays if c > e50)
    a200 = sum(1 for _, c, _, e200 in todays if c > e200)
    reading = {"d": day, "above50": round(100.0 * a50 / n, 2),
               "above200": round(100.0 * a200 / n, 2), "n": n}
    if series and series[-1]["d"] == day:
        series[-1] = reading
        log(f"refreshed {day}: {reading['above50']}% / {reading['above200']}% (n={n})")
    else:
        series.append(reading)
        log(f"appended {day}: {reading['above50']}% / {reading['above200']}% (n={n})")

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
        cr = subprocess.run(["git", "commit", "-m",
                             f"Daily breadth EMA roll ({day}: "
                             f"{reading['above50']}%/ {reading['above200']}%, n={n})"],
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
