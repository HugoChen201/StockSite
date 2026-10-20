#!/usr/bin/env python3
"""Follow-up patch: verified live-browser Oct-20 close numbers.

Source: live browser task completed 2026-10-20 ~21:11 UTC (17:11 ET).
- Barchart: $S5FI 52.08 (quote 16:33 ET, prev close 43.93),
  $S5TH 53.28 (16:50 ET, prev close 50.69),
  $ADRN 2.84 (16:54 ET) / $ADDN +879.00 (16:36 ET),
  highs/lows Last Updated 10/20/2026 16:59 ET: NYSE 57/53, Nasdaq 39/238.
- CNN Fear & Greed: 27 Fear, prev close 23, 1 week ago 44,
  1 month ago 30, last updated Oct 20 at 4:48:29 PM ET.
- ETF Action report posted Oct 20, 2026 (T+1, data as of Oct 19):
  total +$10.26B, SPY +$3.47B, QQQ +$4.90B, IWM -$513.8M.
- YCharts live: Oct-19 finals now visible (equity 0.55, index 0.99;
  last updated Oct 19 2026 22:02 EDT); no Oct-20 final yet.
SMI / vixTerm from the main close patch are carried unchanged.
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
data = json.loads((REPO / "data.json").read_text())
mi = data["MARKET_INTERNALS"]

# --- breadth (Oct 20 finals, barchart live) ---
b = mi["breadth"]
b["advanceDeclineRatio"] = 2.84
b["adDifference"] = 879.0
b["advanceDeclineAsOf"] = "Oct 20, 2026 close (barchart $ADRN quote stamp 16:54 ET / $ADDN 16:36 ET, live browser)"
b["above50"] = 52.08
b["above50Prev"] = 43.93
b["above50AsOf"] = "Oct 20, 2026 close (barchart $S5FI, live browser, quote stamp 16:33 ET)"
b["above200"] = 53.28
b["above200Prev"] = 50.69
b["above200AsOf"] = "Oct 20, 2026 close (barchart $S5TH, live browser, quote stamp 16:50 ET)"
b["newHighs"] = 57
b["newLows"] = 53
b["nasdaqHighs"] = 39
b["nasdaqLows"] = 238
b["highLowAsOf"] = "Oct 20, 2026 (barchart highs-lows summary, live browser, Last Updated 10/20/2026 16:59 ET; 52-week NYSE highs 57 / lows 53, Nasdaq highs 39 / lows 238)"
mi["breadth"] = b

# --- fear & greed (Oct 20, CNN live) ---
mi["fearGreed"] = {
    "value": 27,
    "label": "Fear",
    "previousClose": 23,
    "asof": "Oct 20, 2026 close (cnn.com live page, last updated 4:48:29 PM ET)",
    "note": "Prev close 23; 1 week ago 44; 1 month ago 30.",
    "url": "https://www.cnn.com/markets/fear-and-greed",
    "dataUrl": "https://raw.githubusercontent.com/whit3rabbit/fear-greed-data/main/fear-greed.csv",
}

# --- flows (ETF Action Oct-20 report, Oct-19 activity) ---
mi["flows"] = [
    {"ticker": "SPY", "value": 3.47, "label": "+$3.47B inflow"},
    {"ticker": "QQQ", "value": 4.9, "label": "+$4.90B inflow"},
    {"ticker": "IWM", "value": -0.51, "label": "-$513.8M outflow"},
]
mi["flowsAsOf"] = "ETF Action ETF Flow Report posted Oct 20, 2026 (covers Oct 19 session activity). Total net ETF flows +$10.26B. SPY +$3.47B, QQQ +$4.90B, IWM -$513.8M."

# --- put/call: Oct-19 finals now visible on YCharts live ---
pc = mi["putCall"]
pc["equity"] = 0.55
pc["equityAsOf"] = "Oct 19, 2026 (ycharts; next release Oct 20 2026 20:00 EDT)"
pc["index"] = 0.99
pc["indexAsOf"] = "Oct 19, 2026 (ycharts; next release Oct 20 2026 20:00 EDT)"
pc["totalAsOf"] = "Sep 21, 2026; Oct 20 total unavailable"
pc["asof"] = "Equity Oct 19, 2026 \u00b7 Index Oct 19, 2026 (ycharts)"
mi["putCall"] = pc

patch = {"MARKET_INTERNALS": mi}
out = Path("/tmp/patch.json")
out.write_text(json.dumps(patch, indent=2))
print("wrote", out, "| A/D:", b["advanceDeclineRatio"], "| >50d:", b["above50"],
      "| F&G:", mi["fearGreed"]["value"], "| P/C eq/idx:", pc["equity"], pc["index"])
