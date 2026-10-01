#!/usr/bin/env python3
"""Build/refresh the extended display universe for Hugo's Stock Watchlist.

Display universe = S&P 100 + Nasdaq-100 (deduped, ~175 names), quotes-only tier.
Also snapshots the full S&P 500 constituent list (used by the breadth backfill /
daily updater scripts).

Sources (all Wikipedia, re-fetched each run):
  - https://en.wikipedia.org/wiki/S%26P_100                    -> Symbol, Name, Sector
  - https://en.wikipedia.org/wiki/List_of_NASDAQ-100_companies -> Ticker, Company, ICB Industry
  - https://en.wikipedia.org/wiki/List_of_S%26P_500_companies  -> Symbol, Security, GICS Sector

Writes:
  - /tmp/universe_patch.json : {"UNIVERSE": {TICKER: {name, sector, inSP100, inNDX}}}
  - ~/workspace/goals/stock-watchlist-website/hidden_files/universe/snapshot.json
      {asof, sp100: [...], ndx: [...], sp500: [...]}  (for monthly diff + breadth scripts)

Monthly cadence: exits quietly ("nothing to do") when the snapshot is < 30 days
old, unless --force is passed. Intended to be called by the morning refresh job.
On a real change it patches data.json via update-data.py under the shared lock,
refreshes the embedded `let UNIVERSE = ...` fallback line in app.js, commits and
pushes (same pattern as enrich-calendar-stocks.py). Never invents numbers: a
failed fetch aborts the run and keeps last-good data.
"""
import html
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path.home() / "workspace" / "StockSite"
DATA_PATH = REPO / "data.json"
APP_JS = REPO / "app.js"
SNAP_DIR = (Path.home() / "workspace" / "goals" / "stock-watchlist-website"
            / "hidden_files" / "universe")
SNAP_PATH = SNAP_DIR / "snapshot.json"
PATCH_PATH = Path("/tmp/universe_patch.json")

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}

PAGES = {
    "sp100": "https://en.wikipedia.org/wiki/S%26P_100",
    "ndx": "https://en.wikipedia.org/wiki/List_of_NASDAQ-100_companies",
    "sp500": "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
}

# Wikipedia sector vocab -> app sector vocab (matches the 63-name core list)
SECTOR_MAP = {
    "Information Technology": "Technology",
    "Technology": "Technology",
    "Health Care": "Healthcare",
    "Healthcare": "Healthcare",
    "Financials": "Financial Services",
    "Consumer Discretionary": "Consumer Cyclical",
    "Consumer Staples": "Consumer Defensive",
    "Industrials": "Industrials",
    "Communication Services": "Communication Services",
    "Telecommunications": "Communication Services",
    "Energy": "Energy",
    "Utilities": "Utilities",
    "Real Estate": "Real Estate",
    "Materials": "Basic Materials",
    "Basic Materials": "Basic Materials",
}


def log(msg):
    print(f"[build-universe] {msg}", flush=True)


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def cell_text(td):
    t = re.sub(r"<[^>]+>", "", td)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def parse_wikitable(html_text, idx=0):
    tables = re.findall(r'<table class="wikitable[^"]*"[^>]*>(.*?)</table>',
                        html_text, re.S)
    t = tables[idx]
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S):
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)
        if cells:
            rows.append([cell_text(c) for c in cells])
    return rows


def norm_ticker(sym):
    s = sym.strip().upper().replace(".", "-")
    # Yahoo uses BRK-B / BF-B for the class-B shares
    return {"BRK-B": "BRK-B", "BF-B": "BF-B"}.get(s, s)


def norm_sector(s):
    return SECTOR_MAP.get(s.strip(), s.strip() or "Other")


def build():
    pages = {k: fetch(u) for k, u in PAGES.items()}

    sp100_rows = parse_wikitable(pages["sp100"], 1)   # Symbol, Name, Sector
    ndx_rows = parse_wikitable(pages["ndx"], 0)       # Ticker, Company, ICB Industry
    sp500_rows = parse_wikitable(pages["sp500"], 0)   # Symbol, Security, GICS Sector

    sp100 = [(norm_ticker(r[0]), r[1], norm_sector(r[2]))
             for r in sp100_rows[1:] if r[0]]
    ndx = [(norm_ticker(r[0]), r[1], norm_sector(r[2]))
           for r in ndx_rows[1:] if r[0]]
    sp500 = [(norm_ticker(r[0]), r[1], norm_sector(r[2]))
             for r in sp500_rows[1:] if r[0]]

    # sanity checks — Wikipedia lists move a little over time, but not much
    assert 95 <= len(sp100) <= 110, f"S&P 100 count looks wrong: {len(sp100)}"
    assert 95 <= len(ndx) <= 110, f"Nasdaq-100 count looks wrong: {len(ndx)}"
    assert 480 <= len(sp500) <= 520, f"S&P 500 count looks wrong: {len(sp500)}"

    sp100_set = {t for t, _, _ in sp100}
    ndx_set = {t for t, _, _ in ndx}

    universe = {}
    for t, name, sector in sp100 + ndx:
        if t not in universe:
            universe[t] = {"name": name, "sector": sector,
                           "inSP100": t in sp100_set, "inNDX": t in ndx_set}
        else:
            universe[t]["inSP100"] = universe[t]["inSP100"] or t in sp100_set
            universe[t]["inNDX"] = universe[t]["inNDX"] or t in ndx_set

    log(f"S&P 100: {len(sp100)} | Nasdaq-100: {len(ndx)} | "
        f"display universe: {len(universe)} | S&P 500: {len(sp500)}")
    return universe, sp500


def snapshot_is_fresh():
    if not SNAP_PATH.exists():
        return False
    try:
        snap = json.load(open(SNAP_PATH))
        asof = datetime.strptime(snap["asof"], "%Y-%m-%d").date()
        return (date.today() - asof).days < 30
    except Exception:
        return False


def main():
    force = "--force" in sys.argv
    if not force and snapshot_is_fresh():
        log("constituents snapshot < 30 days old — nothing to do")
        return 0

    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    try:
        universe, sp500 = build()
    except Exception as e:
        log(f"fetch/parse failed ({e}) — keeping last-good data, no patch")
        return 1

    snap = {"asof": date.today().isoformat(),
            "sp100": sorted(t for t, v in universe.items() if v["inSP100"]),
            "ndx": sorted(t for t, v in universe.items() if v["inNDX"]),
            "sp500": [{"ticker": t, "name": n, "sector": s} for t, n, s in sp500]}
    SNAP_PATH.write_text(json.dumps(snap))

    PATCH_PATH.write_text(json.dumps({"UNIVERSE": universe}))
    log(f"patch written to {PATCH_PATH} ({len(universe)} names)")

    # apply under the shared lock (same discipline as the other writers)
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
        # refresh the embedded UNIVERSE fallback line in app.js
        new_data = json.load(open(DATA_PATH))
        lines = APP_JS.read_text().split("\n")
        new_line = ("let UNIVERSE = " +
                    json.dumps(new_data.get("UNIVERSE", {}),
                               separators=(",", ":")) + ";")
        hit = [i for i, ln in enumerate(lines)
               if ln.startswith("let UNIVERSE = ")]
        if len(hit) == 1:
            lines[hit[0]] = new_line
        elif not hit:
            cal = [i for i, ln in enumerate(lines)
                   if ln.startswith("let CALENDAR_META = ")]
            assert len(cal) == 1
            lines.insert(cal[0] + 1, new_line)
        else:
            raise AssertionError(f"unexpected UNIVERSE lines: {hit}")
        APP_JS.write_text("\n".join(lines))
        log("app.js embedded UNIVERSE fallback refreshed")
        subprocess.run(["git", "add", "data.json", "app.js"], cwd=str(REPO),
                       check=True)
        cr = subprocess.run(["git", "commit", "-m",
                             f"Extended universe refresh ({len(universe)} names, "
                             f"S&P 100 + Nasdaq-100)"],
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
