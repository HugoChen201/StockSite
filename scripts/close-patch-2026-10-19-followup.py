#!/usr/bin/env python3
"""Follow-up patch: verified live-browser Oct-19 close numbers.

Source: live browser task completed 2026-10-19 ~21:06 UTC (17:06 ET).
- Barchart: $S5FI 43.93 (quote 16:52 ET, prev close 45.12),
  $S5TH 50.69 (16:52 ET, prev close 51.88),
  $ADRN 0.49 / $ADDN -618.00 (both 16:55 ET),
  highs/lows Last Updated 10/19/2026 16:59 ET: NYSE 29/97, Nasdaq 16/325.
- CNN Fear & Greed: 23 Extreme Fear, prev close 17, 1 week ago 46,
  1 month ago 30, last updated Oct 19 at 4:49:01 PM ET.
- ETF Action report posted Oct 19, 2026 (T+1, data as of Oct 16):
  total +$3.72B, SPY -$4.40B, QQQ -$3.42B, IWM -$2.47B
  (flow values unchanged from carried block; posting date updated Oct 18 -> Oct 19).
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
data = json.loads((REPO / "data.json").read_text())
mi = data["MARKET_INTERNALS"]

# --- breadth (Oct 19 finals, barchart live) ---
b = mi["breadth"]
b["advanceDeclineRatio"] = 0.49
b["adDifference"] = -618.0
b["advanceDeclineAsOf"] = "Oct 19, 2026 close (barchart $ADRN quote stamp 16:55 ET / $ADDN 16:55 ET, live browser)"
b["above50"] = 43.93
b["above50Prev"] = 45.12
b["above50AsOf"] = "Oct 19, 2026 close (barchart $S5FI, live browser, quote stamp 16:52 ET)"
b["above200"] = 50.69
b["above200Prev"] = 51.88
b["above200AsOf"] = "Oct 19, 2026 close (barchart $S5TH, live browser, quote stamp 16:52 ET)"
b["newHighs"] = 29
b["newLows"] = 97
b["nasdaqHighs"] = 16
b["nasdaqLows"] = 325
b["highLowAsOf"] = "Oct 19, 2026 (barchart highs-lows summary, live browser, Last Updated 10/19/2026 16:59 ET; 52-week NYSE highs 29 / lows 97, Nasdaq highs 16 / lows 325)"
mi["breadth"] = b

# --- fear & greed (Oct 19, CNN live) ---
mi["fearGreed"] = {
    "value": 23,
    "label": "Extreme Fear",
    "previousClose": 17,
    "asof": "Oct 19, 2026 close (cnn.com live page, last updated 4:49:01 PM ET)",
    "note": "Prev close 17; 1 week ago 46; 1 month ago 30.",
    "url": "https://www.cnn.com/markets/fear-and-greed",
    "dataUrl": "https://raw.githubusercontent.com/whit3rabbit/fear-greed-data/main/fear-greed.csv",
}

# --- flows (ETF Action Oct-19 report, Oct-16 activity; values unchanged) ---
mi["flows"] = [
    {"ticker": "SPY", "value": -4.4, "label": "-$4.40B outflow"},
    {"ticker": "QQQ", "value": -3.42, "label": "-$3.42B outflow"},
    {"ticker": "IWM", "value": -2.47, "label": "-$2.47B outflow"},
]
mi["flowsAsOf"] = "ETF Action ETF Flow Report posted Oct 19, 2026 (covers Oct 16 session activity). Total net ETF flows +$3.72B. SPY -$4.40B, QQQ -$3.42B, IWM -$2.47B."

patch = {"MARKET_INTERNALS": mi}
out = Path("/tmp/patch.json")
out.write_text(json.dumps(patch, indent=2))
print("wrote", out, "| A/D:", b["advanceDeclineRatio"], "| >50d:", b["above50"],
      "| F&G:", mi["fearGreed"]["value"])
