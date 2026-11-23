#!/usr/bin/env python3
"""Apply Nov 23, 2026 morning-refresh UI date labels to index.html."""
import json
from pathlib import Path

p = Path.home() / "workspace" / "StockSite" / "index.html"
html = p.read_text()
stamp = json.load(open("/tmp/patch.json"))["SCREEN_SNAPSHOT"]["updated"]
new_stamp = f"<strong>Updated {stamp}</strong>"

REPL = [
    ("14 ranked setups from the November 20 Finviz screen, with verified "
     "front-month options activity.",
     "15 ranked setups from the November 23 Finviz screen, with verified "
     "front-month options activity."),
    ("Updated Nov 20, 2026 · optioncharts.io 30-day IV readings "
     "(58 of 63 refreshed; 5 carried last-good; IV percentile carried "
     "last-good for all 63); stale source pages are flagged in ticker detail",
     "Updated Nov 23, 2026 · optioncharts.io 30-day IV readings "
     "(51 of 63 refreshed; 12 carried last-good; IV percentile carried "
     "last-good for all 63); stale source pages are flagged in ticker detail"),
    ("Nov 20 – Nov 26, 2026 window", "Nov 23 – Nov 29, 2026 window"),
]
for old, new in REPL:
    assert html.count(old) == 1, f"expected 1 occurrence of {old[:60]!r}, got {html.count(old)}"
    html = html.replace(old, new)

old_stamp = "<strong>Updated Nov 20, 2026 7:34 AM ET</strong>"
assert html.count(old_stamp) == 3, f"expected 3 old stamps, got {html.count(old_stamp)}"
html = html.replace(old_stamp, new_stamp)

p.write_text(html)
print(f"index.html labels updated to {stamp}")
