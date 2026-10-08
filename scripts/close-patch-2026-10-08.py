#!/usr/bin/env python3
"""Close-refresh patch builder for StockSite data.json (Thu 2026-10-08).

Loads data.json, replaces refreshed MARKET_INTERNALS blocks wholesale (every
unrefreshed block is carried verbatim), appends the finalized SMI reading,
dumps the changed top-level keys to /tmp/patch-close-2026-10-08.json.
Apply with: python3 scripts/update-data.py /tmp/patch-close-2026-10-08.json

VERIFIED VALUES (filled as verified; blocks marked "CARRY" fall back to
last-good values already in data.json):
- SMI: finalized vs 391 Yahoo SPY 1m bars, full Oct-08 session.
- vixTerm: Yahoo ^VIX / ^VIX3M daily closes, Oct 8, 2026.
- breadth, fearGreed, putCall, flows: from live-browser verification (Oct 8
  post-close). put/call Oct-8 finals post ~8 PM ET -> expect Oct-7 finals.
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
data = json.loads((REPO / "data.json").read_text())
mi = data["MARKET_INTERNALS"]

# ---------------------------------------------------------------- SMI (FINAL)
# Verified vs 391 SPY 1m Yahoo bars, full Oct-08-2026 session:
#   9:30 open 774.86; 10:00 close 775.38 (+0.0671%)
#   15:00 close 772.705; 16:00 close 773.93 (+0.1585%)
#   998.90 - 0.0671 + 0.1585 = 998.99
smi = mi["smi"]
series = smi.get("series", [])
series.append({"date": "Oct 08", "value": 998.99})
smi["series"] = series
smi["status"] = "Finalized"
smi["latest"] = 998.99
smi["change"] = 0.09
smi["asof"] = "Oct 08, 2026 close"
smi["note"] = ("Self-computed Don Hays-style (SPY proxy), never SentimenTrader. "
               "Oct 8: -first-30-min (-0.067%) + last-hour (+0.159%) = +0.091.")
smi["inputs"] = ("SPY open 774.86; 10:00 775.38 (+0.0671%); "
                 "15:00 772.705; close 773.93 (+0.1585%). "
                 "998.90 -0.0671 +0.1585 = 998.99. "
                 "391 verified 1m bars, full 10-08 session")

# --------------------------------------------------------------- VIX term (FINAL)
# Yahoo ^VIX / ^VIX3M daily closes, Oct 8, 2026:
#   ^VIX 15.41 (prev 15.08, +0.33 / +2.19%); ^VIX3M 18.08 (prev 17.72, +0.36 / +2.03%)
mi["vixTerm"] = {
    "spot": 15.41,
    "spotPrev": 15.08,       # Oct 7 close (verified Oct-7 close refresh)
    "spotChange": 0.33,
    "spotChangePct": 2.19,
    "threeMonth": 18.08,
    "threeMonthPrev": 17.72, # Oct 7 close (verified Oct-7 close refresh)
    "threeMonthChangePct": 2.03,
    "ratio": 1.17,
    "state": "Contango (calm)",
    "asof": "Oct 08, 2026 close (Yahoo ^VIX / ^VIX3M daily)",
    "note": "^VIX3M 3-month VIX. 18.08/15.41 = 1.17.",
}

# ------------------------------------------------------------- breadth (BROWSER)
# Verified via live browser, Oct 8, 2026 post-close:
#   $ADRN 1.97 (+535.48% on the day; prev 0.31), stamp 16:59 ET
#   $ADDN 598.00 (prev -957.00), stamp 16:45 ET
#   $S5FI 31.93 (prev 28.34), $S5TH 46.70 (prev 45.10), stamp 16:42 ET
#   highs/lows Last Updated 10/08/2026 16:54 ET: NYSE 33/107, Nasdaq 23/261
mi["breadth"] = {
    "advanceDeclineRatio": 1.97,
    "adDifference": 598.0,
    "advanceDeclineAsOf": ("Oct 08, 2026 close (barchart $ADRN quote stamp 16:59 ET / "
                           "$ADDN 16:45 ET, live browser; ADRN +535.48% on the day)"),
    "above50": 31.93,
    "above50Prev": 28.34,
    "above50AsOf": "Oct 08, 2026 close (barchart $S5FI/$S5TH, live browser, quote stamp 16:42 ET)",
    "above200": 46.70,
    "above200Prev": 45.10,
    "above200AsOf": "Oct 08, 2026 close (barchart $S5FI/$S5TH, live browser, quote stamp 16:42 ET)",
    "newHighs": 33,
    "newLows": 107,
    "nasdaqHighs": 23,
    "nasdaqLows": 261,
    "spHighs": None,
    "spLows": None,
    "highLowAsOf": ("Oct 08, 2026 (barchart highs-lows summary, live browser, "
                    "Last Updated 10/08/2026 16:54 ET; no S&P 500 columns)"),
    "above50Url": "https://www.barchart.com/stocks/quotes/$S5FI",
    "above200Url": "https://www.barchart.com/stocks/quotes/$S5TH",
    "adRatioUrl": "https://www.barchart.com/stocks/quotes/%24ADRN",
    "adDifferenceUrl": "https://www.barchart.com/stocks/quotes/%24ADDN",
    "highLowUrl": "https://www.barchart.com/stocks/highs-lows/summary",
}

# -------------------------------------------------------------- put/call (BROWSER)
# YCharts, Oct 8 ~5:05 PM ET: equity 0.63 / index 0.93, Latest Period Oct 07
# (Last Updated Oct 7 2026 21:22 EDT; Oct-8 finals post Oct 8 20:00 EDT).
mi["putCall"] = {
    "equity": 0.63,
    "equityAsOf": "Oct 07, 2026 (ycharts, Last Updated Oct 7 2026 21:22 EDT; Oct-8 posts ~8 PM ET)",
    "equityUrl": "https://ycharts.com/indicators/cboe_equity_put_call_ratio",
    "index": 0.93,
    "indexAsOf": "Oct 07, 2026 (ycharts, Last Updated Oct 7 2026 21:22 EDT; Oct-8 posts ~8 PM ET)",
    "indexUrl": "https://ycharts.com/indicators/cboe_index_put_call_ratio",
    "total": 0.74,
    "totalAsOf": "Sep 21, 2026; Oct 8 total unavailable",
    "asof": "Equity Oct 07, 2026 \u00b7 Index Oct 07, 2026 (ycharts)",
}

# -------------------------------------------------------- fear & greed (BROWSER)
# Verified via live browser (cnn.com), Oct 8, 2026: 38 Fear,
# "Last updated Oct 8 at 4:47:14 PM ET". Previous close 44; 1 week ago blank.
mi["fearGreed"] = {
    "value": 38,
    "label": "Fear",
    "previousClose": 44,
    "asof": "Oct 08, 2026 close (cnn.com live page, last updated 4:47:14 PM ET)",
    "note": ("Prev close 44 Neutral (Oct 7); 1 month ago 39. "
             "CNN context: S&P 500 7,765.36 +0.47%; Dow 51,231.64 +0.10%; "
             "Nasdaq 27,193.34 +1.25%."),
    "url": "https://www.cnn.com/markets/fear-and-greed",
    "dataUrl": "https://raw.githubusercontent.com/whit3rabbit/fear-greed-data/main/fear-greed.csv",
}

# ------------------------------------------------------------------ flows
# ETF Action fund_flows page returned 404 at Oct-8 post-close check (verified
# via live browser). Latest verified report is the Oct-7 one (T+1, covers Oct-6
# activity): SPY -$4.18B, QQQ -$2.34B, IWM not individually listed.
# Carried last-good; Oct-7 activity flow data unavailable from any verified
# source this run. etf.com daily flows blocked by Cloudflare bot wall.
mi["flowsAsOf"] = ("ETF Action page 404'd at Oct-8 post-close check; latest verified "
                   "report posted Oct 7, 2026 (T+1 data: covers Oct 6 session activity). "
                   "SPY/QQQ/IWM flows carried last-good. Total net ETF flows +$896.9M "
                   "(Oct-7 report).")

# Carry everything else verbatim: aaii, fedWatch.
for k in ("aaii", "fedWatch"):
    assert k in mi, k

patch = {"MARKET_INTERNALS": mi}
out = Path("/tmp/patch-close-2026-10-08.json")
out.write_text(json.dumps(patch, indent=2))
print("wrote", out, "| SMI latest:", smi["latest"], "| vixTerm spot:", mi["vixTerm"]["spot"])
