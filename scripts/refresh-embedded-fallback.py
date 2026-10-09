#!/usr/bin/env python3
"""Sync the embedded app.js fallback declarations from the current data.json.

Several `let KEY = ...;` lines at the top of app.js are offline fallbacks that
JavaScript only overwrites when the data.json fetch succeeds. Nothing was
refreshing them, so they froze at ~Sep 23, 2026 (stale COST earnings, old
screen snapshot, etc.). Run this after every morning refresh (and any
data.json patch that changes these keys) so the fallback never goes stale.

Owned elsewhere — do NOT touch here:
  HISTORY, CALENDAR_META (scripts/enrich-calendar-stocks.py),
  UNIVERSE (scripts/build-universe.py)
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA_PATH = REPO / "data.json"
APP_JS = REPO / "app.js"

# key -> regex matching the declaration line start (kept verbatim as prefix)
SYNC_KEYS = [
    "STOCKS",
    "EARNINGS_DATES",
    "EXPECTED_MOVES",
    "MACRO_EVENTS",
    "ANALYST_REVISIONS",
    "SCREEN_SNAPSHOT",
    "MARKET_INTERNALS",
]


def main() -> int:
    data = json.load(open(DATA_PATH))
    lines = APP_JS.read_text().split("\n")
    changed = []
    for key in SYNC_KEYS:
        if key not in data:
            print(f"skip {key}: not in data.json", file=sys.stderr)
            continue
        # match `let KEY = ` or `let KEY={` at line start
        pat = re.compile(rf"^let {key} ?= ?")
        hits = [i for i, ln in enumerate(lines) if pat.match(ln)]
        if len(hits) != 1:
            print(f"ERROR: expected 1 embedded {key} line, found {len(hits)}",
                  file=sys.stderr)
            return 1
        prefix = pat.match(lines[hits[0]]).group(0)
        lines[hits[0]] = prefix + json.dumps(data[key], separators=(",", ":")) + ";"
        changed.append(key)
    APP_JS.write_text("\n".join(lines))
    print(f"app.js embedded fallback synced: {', '.join(changed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
