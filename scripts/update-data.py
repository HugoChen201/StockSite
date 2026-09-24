#!/usr/bin/env python3
"""Apply a JSON patch to the StockSite data.json.

Usage: update-data.py patch.json
  patch.json: {"SCREEN_SNAPSHOT": {...}, "MARKET_INTERNALS": {...}, ...}
Top-level keys in the patch REPLACE the same keys in data.json.
Bumps data.json `version` by 1 and sets `updatedAt` (America/New_York).
The caller then does: git add data.json && git commit -m ... && git push

The read-modify-write runs under the shared git_lock so concurrent writers
(five-minute updater, morning/close scans, MomoEdge job) cannot interleave.
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from git_lock import locked  # noqa: E402

REPO = "/home/hatch/workspace/StockSite"
DATA_PATH = REPO + "/data.json"


def apply_patch(patch):
    """Apply patch dict to data.json under the shared lock. Returns (version, updatedAt)."""
    with locked():
        with open(DATA_PATH) as f:
            data = json.load(f)
        for k, v in patch.items():
            if k in ("version", "updatedAt"):
                continue
            data[k] = v
        data["version"] = int(data.get("version", 0)) + 1
        now_et = datetime.now(ZoneInfo("America/New_York"))
        data["updatedAt"] = now_et.strftime("%b %-d, %Y, %-I:%M %p ET").replace("  ", " ")
        with open(DATA_PATH, "w") as f:
            json.dump(data, f)
        return data["version"], data["updatedAt"]


def main():
    if len(sys.argv) != 2:
        print("usage: update-data.py patch.json", file=sys.stderr)
        sys.exit(2)
    patch = json.load(open(sys.argv[1]))
    version, updated = apply_patch(patch)
    print("data.json -> version", version, "| updatedAt:", updated)


if __name__ == "__main__":
    main()
