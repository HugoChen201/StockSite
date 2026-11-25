#!/usr/bin/env python3
"""Apply Nov 25, 2026 morning-refresh UI date labels to index.html.

Note: the Finviz screen is CARRIED from Nov 24 this run (screener 403 on the
text fetch; no live browser), so the Potential Trades pane stamp and
tradesDesc stay Nov 24. Only the Market Internals pane stamp, the earnings
calendar stamp, the 7-day window, and the Overview IV note move to Nov 25.
"""
from pathlib import Path

p = Path.home() / "workspace" / "StockSite" / "index.html"
html = p.read_text()
stamp = Path("/tmp/run_stamp.txt").read_text().strip()
new_stamp = f"<strong>Updated {stamp}</strong>"
OLD = "<strong>Updated Nov 24, 2026 7:44 AM ET</strong>"

# Market Internals pane stamp (context: "Closing snapshot" tag follows).
old_int = (f'<div class="pane-stamp">{OLD}<br><span class="morning-tag" '
           'data-i18n="closingSnapshot">Closing snapshot</span></div>')
assert html.count(old_int) == 1, f"internals stamp ctx: {html.count(old_int)}"
html = html.replace(old_int, old_int.replace(OLD, new_stamp))

# Earnings calendar stamp (context: calendar-source div).
old_cal = f'<div class="calendar-source">{OLD}'
assert html.count(old_cal) == 1, f"calendar stamp ctx: {html.count(old_cal)}"
html = html.replace(old_cal, old_cal.replace(OLD, new_stamp))

# Potential Trades pane stamp must be UNTOUCHED (screen carried from Nov 24).
old_trades = (f'<div class="pane-stamp">{OLD}<br><span class="morning-tag">'
              "Intraday scan</span></div>")
assert html.count(old_trades) == 1, f"trades stamp ctx: {html.count(old_trades)}"

# 7-day window text.
old_win = "Nov 24 – Nov 30, 2026 window"
assert html.count(old_win) == 1, f"window: {html.count(old_win)}"
html = html.replace(old_win, "Nov 25 – Dec 1, 2026 window")

# Overview IV note.
old_iv = ("Updated Nov 24, 2026 · optioncharts.io 30-day IV readings "
          "(62 of 63 refreshed; 1 carried last-good); stale source pages are "
          "flagged in ticker detail")
assert html.count(old_iv) == 1, f"iv note: {html.count(old_iv)}"
html = html.replace(old_iv,
                    "Updated Nov 25, 2026 · optioncharts.io 30-day IV readings "
                    "(62 of 63 refreshed; 1 carried last-good); stale source "
                    "pages are flagged in ticker detail")

# Final sanity: exactly one Nov 24 7:44 stamp left (the carried trades pane),
# and exactly two Nov 25 stamps.
assert html.count(OLD) == 1, f"leftover old stamps: {html.count(OLD)}"
assert html.count(new_stamp) == 2, f"new stamps: {html.count(new_stamp)}"
assert "15 ranked setups from the November 24 Finviz screen" in html

p.write_text(html)
print(f"index.html labels updated to {stamp} (internals + calendar + IV note; "
      "trades pane kept Nov 24 — screen carried)")
