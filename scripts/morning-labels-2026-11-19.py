#!/usr/bin/env python3
"""Apply Nov 19, 2026 morning-refresh UI date labels to index.html."""
import json
from pathlib import Path

p = Path.home() / "workspace" / "StockSite" / "index.html"
html = p.read_text()
stamp = json.load(open("/tmp/patch.json"))["SCREEN_SNAPSHOT"]["updated"]
new_stamp = f"<strong>Updated {stamp}</strong>"

REPL = [
    ("13 ranked setups from the November 18 Finviz screen, with verified "
     "front-month options activity.",
     "15 ranked setups from the November 19 Finviz screen, with verified "
     "front-month options activity."),
    ("Updated Nov 18, 2026 · optioncharts.io 30-day IV readings "
     "(61 of 63 refreshed; 2 carried last-good; IV percentile carried "
     "last-good for all 63); stale source pages are flagged in ticker detail",
     "Updated Nov 19, 2026 · optioncharts.io 30-day IV readings "
     "(58 of 63 refreshed; 5 carried last-good; IV percentile carried "
     "last-good for all 63); stale source pages are flagged in ticker detail"),
    ("Nov 18 – Nov 24, 2026 window", "Nov 19 – Nov 25, 2026 window"),
]
for old, new in REPL:
    assert html.count(old) == 1, f"expected 1 occurrence of {old[:60]!r}, got {html.count(old)}"
    html = html.replace(old, new)

old_stamp = "<strong>Updated Nov 18, 2026 7:36 AM ET</strong>"
assert html.count(old_stamp) == 3, f"expected 3 old stamps, got {html.count(old_stamp)}"
html = html.replace(old_stamp, new_stamp)

p.write_text(html)
print(f"index.html labels updated to {stamp}")
