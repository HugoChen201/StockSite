#!/usr/bin/env python3
"""Apply Nov 24, 2026 morning-refresh UI date labels to index.html."""
import json
from pathlib import Path

p = Path.home() / "workspace" / "StockSite" / "index.html"
html = p.read_text()
stamp = json.load(open("/tmp/patch.json"))["SCREEN_SNAPSHOT"]["updated"]
new_stamp = f"<strong>Updated {stamp}</strong>"

REPL = [
    ("14 ranked setups from the November 20 Finviz screen, with verified "
     "front-month options activity.",
     "15 ranked setups from the November 24 Finviz screen, with verified "
     "front-month options activity."),
    ("15 ranked setups from the November 23 Finviz screen, with verified "
     "front-month options activity.",
     "15 ranked setups from the November 24 Finviz screen, with verified "
     "front-month options activity."),
    ("Updated Nov 23, 2026 · optioncharts.io 30-day IV readings "
     "(51 of 63 refreshed; 12 carried last-good; IV percentile carried "
     "last-good for all 63); stale source pages are flagged in ticker detail",
     "Updated Nov 24, 2026 · optioncharts.io 30-day IV readings "
     "(62 of 63 refreshed; 1 carried last-good); stale source pages are "
     "flagged in ticker detail"),
    ("Nov 23 – Nov 29, 2026 window", "Nov 24 – Nov 30, 2026 window"),
]
for old, new in REPL:
    n = html.count(old)
    assert n in (0, 1), f"expected 0-1 occurrences of {old[:60]!r}, got {n}"
    if n == 1:
        html = html.replace(old, new)

old_stamp = "<strong>Updated Nov 23, 2026 7:42 AM ET</strong>"
assert html.count(old_stamp) == 3, f"expected 3 old stamps, got {html.count(old_stamp)}"
html = html.replace(old_stamp, new_stamp)

p.write_text(html)
print(f"index.html labels updated to {stamp}")
