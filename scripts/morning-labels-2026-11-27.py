#!/usr/bin/env python3
"""Apply Nov 27, 2026 morning-refresh UI date labels to index.html.

Screen is FRESH this run (live-browser Finviz fetch 7:29-7:30 AM ET, 102
results, 14 ranked), so the Potential Trades pane stamp and tradesDesc move
to Nov 27 too. Internals/calendar stamps use the run stamp (7:46 AM ET,
matching ASOF in data.json).
"""
from pathlib import Path

p = Path.home() / "workspace" / "StockSite" / "index.html"
html = p.read_text()
RUN_STAMP = "Nov 27, 2026 7:46 AM ET"
SCREEN_STAMP = "Nov 27, 2026 7:30 AM ET"

# Potential Trades pane: tradesDesc paragraph.
old_desc = ("15 ranked setups from the November 25 Finviz screen, with "
            "verified front-month options activity.")
assert html.count(old_desc) == 1, f"tradesDesc: {html.count(old_desc)}"
html = html.replace(old_desc,
                    "14 ranked setups from the November 27 Finviz screen, "
                    "with verified front-month options activity.")

# Potential Trades pane stamp (context: "Intraday scan" tag follows).
old_trades = ('<div class="pane-stamp"><strong>Updated Nov 25, 2026 7:43 AM ET'
              '</strong><br><span class="morning-tag">Intraday scan</span></div>')
assert html.count(old_trades) == 1, f"trades stamp ctx: {html.count(old_trades)}"
html = html.replace(old_trades, old_trades.replace(
    "Updated Nov 25, 2026 7:43 AM ET", f"Updated {SCREEN_STAMP}"))

# Market Internals pane stamp (context: "Closing snapshot" tag follows).
old_int = ('<div class="pane-stamp"><strong>Updated Nov 25, 2026 7:37 AM ET'
           '</strong><br><span class="morning-tag" '
           'data-i18n="closingSnapshot">Closing snapshot</span></div>')
assert html.count(old_int) == 1, f"internals stamp ctx: {html.count(old_int)}"
html = html.replace(old_int, old_int.replace(
    "Updated Nov 25, 2026 7:37 AM ET", f"Updated {RUN_STAMP}"))

# Earnings calendar stamp (context: calendar-source div).
old_cal = '<div class="calendar-source"><strong>Updated Nov 25, 2026 7:37 AM ET</strong>'
assert html.count(old_cal) == 1, f"calendar stamp ctx: {html.count(old_cal)}"
html = html.replace(old_cal, old_cal.replace(
    "Updated Nov 25, 2026 7:37 AM ET", f"Updated {RUN_STAMP}"))

# 7-day window text.
old_win = "Nov 25 – Dec 1, 2026 window"
assert html.count(old_win) == 1, f"window: {html.count(old_win)}"
html = html.replace(old_win, "Nov 27 – Dec 3, 2026 window")

# Overview IV note.
old_iv = ("Updated Nov 25, 2026 · optioncharts.io 30-day IV readings "
          "(62 of 63 refreshed; 1 carried last-good); stale source pages are "
          "flagged in ticker detail")
assert html.count(old_iv) == 1, f"iv note: {html.count(old_iv)}"
html = html.replace(old_iv,
                    "Updated Nov 27, 2026 · optioncharts.io 30-day IV readings "
                    "(62 of 63 refreshed; 1 carried last-good); stale source "
                    "pages are flagged in ticker detail")

# Final sanity: no Nov 25 stamps left in the four stamp spots.
assert "Updated Nov 25, 2026 7:43 AM ET" not in html
assert "Updated Nov 25, 2026 7:37 AM ET" not in html
assert html.count(f"Updated {SCREEN_STAMP}") == 1
assert html.count(f"Updated {RUN_STAMP}") == 2
assert "14 ranked setups from the November 27 Finviz screen" in html

p.write_text(html)
print(f"index.html labels updated: trades {SCREEN_STAMP}, "
      f"internals + calendar {RUN_STAMP}, IV note Nov 27")
