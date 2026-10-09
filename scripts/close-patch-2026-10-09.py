#!/usr/bin/env python3
"""Close-refresh patch builder for StockSite data.json (Fri 2026-10-09).

Loads data.json, replaces refreshed MARKET_INTERNALS blocks wholesale (every
unrefreshed block is carried verbatim), appends the finalized SMI reading,
dumps the changed top-level keys to /tmp/patch-close-2026-10-09.json.
Apply with: python3 scripts/update-data.py /tmp/patch-close-2026-10-09.json

VERIFIED VALUES:
- SMI: finalized vs 391 Yahoo SPY 1m bars, full Oct-09 session.
- vixTerm: Yahoo ^VIX / ^VIX3M daily closes, Oct 9, 2026.
- breadth, fearGreed, putCall, flows: from live-browser verification (Oct 9
  post-close). put/call Oct-9 finals post ~8 PM ET -> expect Oct-8 finals.
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
data = json.loads((REPO / "data.json").read_text())
mi = data["MARKET_INTERNALS"]

# ---------------------------------------------------------------- SMI (FINAL)
# Verified vs 391 SPY 1m Yahoo bars, full Oct-09-2026 session:
#   9:30 open 776.24; 10:00 close 776.06 (-0.0232%)
#   15:00 close 778.915; 16:00 close 778.57 (-0.0443%)
#   998.99 - (-0.0232) + (-0.0443) = 998.97
smi = mi["smi"]
series = smi.get("series", [])
series.append({"date": "Oct 09", "value": 998.97})
smi["series"] = series
smi["status"] = "Finalized"
smi["latest"] = 998.97
smi["change"] = -0.02
smi["asof"] = "Oct 09, 2026 close"
smi["note"] = ("Self-computed Don Hays-style (SPY proxy), never SentimenTrader. "
               "Oct 9: -first-30-min (+0.023%) + last-hour (-0.044%) = -0.021.")
smi["inputs"] = ("SPY open 776.24; 10:00 776.06 (-0.0232%); "
                 "15:00 778.915; close 778.57 (-0.0443%). "
                 "998.99 +0.0232 -0.0443 = 998.97. "
                 "391 verified 1m bars, full 10-09 session")

# --------------------------------------------------------------- VIX term (FINAL)
# Yahoo ^VIX / ^VIX3M daily closes, Oct 9, 2026:
#   ^VIX 14.84 (prev 15.41, -0.57 / -3.70%); ^VIX3M 17.77 (prev 18.08, -0.31 / -1.71%)
mi["vixTerm"] = {
    "spot": 14.84,
    "spotPrev": 15.41,       # Oct 8 close (verified Oct-8 close refresh)
    "spotChange": -0.57,
    "spotChangePct": -3.70,
    "threeMonth": 17.77,
    "threeMonthPrev": 18.08, # Oct 8 close (verified Oct-8 close refresh)
    "threeMonthChangePct": -1.71,
    "ratio": 1.20,
    "state": "Contango (calm)",
    "asof": "Oct 09, 2026 close (Yahoo ^VIX / ^VIX3M daily)",
    "note": "^VIX3M 3-month VIX. 17.77/14.84 = 1.20.",
}

# ------------------------------------------------------------- breadth (BROWSER)
# Verified via live browser, Oct 9, 2026 post-close:
#   $ADRN 1.03 (-47.72% on the day; prev 1.97), stamp 17:00 ET
#   $ADDN 35.00 (prev 598.00), stamp 17:00 ET
#   $S5FI 34.93 (prev 31.93), $S5TH 47.70 (prev 46.70), stamp 16:57 ET
#   highs/lows Last Updated 10/09/2026 16:56 ET: NYSE 37/66, Nasdaq 34/175
mi["breadth"] = {
    "advanceDeclineRatio": 1.03,
    "adDifference": 35.0,
    "advanceDeclineAsOf": ("Oct 09, 2026 close (barchart $ADRN quote stamp 17:00 ET / "
                           "$ADDN 17:00 ET, live browser; ADRN -47.72% on the day)"),
    "above50": 34.93,
    "above50Prev": 31.93,
    "above50AsOf": "Oct 09, 2026 close (barchart $S5FI/$S5TH, live browser, quote stamp 16:57 ET)",
    "above200": 47.70,
    "above200Prev": 46.70,
    "above200AsOf": "Oct 09, 2026 close (barchart $S5FI/$S5TH, live browser, quote stamp 16:57 ET)",
    "newHighs": 37,
    "newLows": 66,
    "nasdaqHighs": 34,
    "nasdaqLows": 175,
    "spHighs": None,
    "spLows": None,
    "highLowAsOf": ("Oct 09, 2026 (barchart highs-lows summary, live browser, "
                    "Last Updated 10/09/2026 16:56 ET; 52-week rows; no S&P 500 columns)"),
    "above50Url": "https://www.barchart.com/stocks/quotes/$S5FI",
    "above200Url": "https://www.barchart.com/stocks/quotes/$S5TH",
    "adRatioUrl": "https://www.barchart.com/stocks/quotes/%24ADRN",
    "adDifferenceUrl": "https://www.barchart.com/stocks/quotes/%24ADDN",
    "highLowUrl": "https://www.barchart.com/stocks/highs-lows/summary",
}

# -------------------------------------------------------------- put/call (BROWSER)
# YCharts, Oct 9 ~5:03 PM ET: equity 0.62 / index 1.03, Latest Period Oct 08
# (Last Updated Oct 8 2026 21:12 EDT; Oct-9 finals post Oct 9 20:00 EDT).
mi["putCall"] = {
    "equity": 0.62,
    "equityAsOf": "Oct 08, 2026 (ycharts, Last Updated Oct 8 2026 21:12 EDT; Oct-9 posts Oct 9 20:00 EDT)",
    "equityUrl": "https://ycharts.com/indicators/cboe_equity_put_call_ratio",
    "index": 1.03,
    "indexAsOf": "Oct 08, 2026 (ycharts, Last Updated Oct 8 2026 21:12 EDT; Oct-9 posts Oct 9 20:00 EDT)",
    "indexUrl": "https://ycharts.com/indicators/cboe_index_put_call_ratio",
    "total": 0.74,
    "totalAsOf": "Sep 21, 2026; Oct 9 total unavailable",
    "asof": "Equity Oct 08, 2026 \u00b7 Index Oct 08, 2026 (ycharts)",
}

# -------------------------------------------------------- fear & greed (BROWSER)
# Verified via live browser (cnn.com), Oct 9, 2026: 45 Neutral,
# "Last updated October 9 at 4:42:42 PM ET". Previous close 37.
mi["fearGreed"] = {
    "value": 45,
    "label": "Neutral",
    "previousClose": 37,
    "asof": "Oct 09, 2026 close (cnn.com live page, last updated 4:42:42 PM ET)",
    "note": ("Prev close 37 Fear (Oct 8); 1 week ago 39; 1 month ago 38; 1 year ago 48. "
             "CNN context: S&P 500 7,811.54 +0.59%; Dow 51,654.95 +0.83%; "
             "Nasdaq 27,366.17 +0.64%."),
    "url": "https://www.cnn.com/markets/fear-and-greed",
    "dataUrl": "https://raw.githubusercontent.com/whit3rabbit/fear-greed-data/main/fear-greed.csv",
}

# ------------------------------------------------------------------ flows
# ETF Action ETF Flow Report posted Oct 9, 2026 (T+1: covers Oct 8 session
# activity). Total net ETF flows +$6.27B. SPY -$505.3M outflow, QQQ +$833.8M,
# IWM +$457.9M.
mi["flowsAsOf"] = ("ETF Action ETF Flow Report posted Oct 9, 2026 (T+1 data: "
                   "covers Oct 8 session activity). Total net ETF flows +$6.27B. "
                   "SPY -$505.3M, QQQ +$833.8M, IWM +$457.9M.")
mi["flows"] = [
    {"ticker": "SPY", "value": -0.5053, "label": "$505.3M outflow"},
    {"ticker": "QQQ", "value": 0.8338, "label": "$833.8M inflow"},
    {"ticker": "IWM", "value": 0.4579, "label": "$457.9M inflow"},
]

# Carry everything else verbatim: aaii, fedWatch, flowsUrl, flowsToolUrl.
for k in ("aaii", "fedWatch", "flowsUrl", "flowsToolUrl"):
    assert k in mi, k

patch = {"MARKET_INTERNALS": mi}
out = Path("/tmp/patch-close-2026-10-09.json")
out.write_text(json.dumps(patch, indent=2))
print("wrote", out, "| SMI latest:", smi["latest"], "| vixTerm spot:", mi["vixTerm"]["spot"])
