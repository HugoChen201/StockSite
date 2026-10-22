#!/usr/bin/env python3
"""Follow-up patch: verified live-browser Oct-22 close numbers.

Source: live browser task completed 2026-10-22 ~21:04 UTC (17:04 ET), FORMAL record.
- Barchart: $ADRN 1.55 / $ADDN +398.00 (both 16:33 ET),
  $S5FI 60.63 (16:43 ET, prev 55.26), $S5TH 57.25 (16:43 ET, prev 54.67),
  highs/lows Last Updated 10/22/2026 16:56 ET: NYSE 94/64, Nasdaq 67/280.
- CNN Fear & Greed: 20 Extreme Fear, prev close 31, last updated Oct 22 at 4:44:06 PM ET.
- ETF Action report posted Oct 22, 2026 (T+1, data as of Oct 21):
  total +$11.23B, SPY -$2.42B, QQQ -$573.9M, IWM not listed in report.
SMI / vixTerm / putCall from the main close patch are carried unchanged.
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
data = json.loads((REPO / "data.json").read_text())
mi = data["MARKET_INTERNALS"]

b = mi["breadth"]
b["advanceDeclineRatio"] = 1.55
b["adDifference"] = 398.0
b["advanceDeclineAsOf"] = "Oct 22, 2026 close (barchart $ADRN / $ADDN quote stamps 16:33 ET, live browser)"
b["above50"] = 60.63
b["above50Prev"] = 55.26
b["above50AsOf"] = "Oct 22, 2026 close (barchart $S5FI, live browser, quote stamp 16:43 ET)"
b["above200"] = 57.25
b["above200Prev"] = 54.67
b["above200AsOf"] = "Oct 22, 2026 close (barchart $S5TH, live browser, quote stamp 16:43 ET)"
b["newHighs"] = 94
b["newLows"] = 64
b["nasdaqHighs"] = 67
b["nasdaqLows"] = 280
b["highLowAsOf"] = "Oct 22, 2026 (barchart highs-lows summary, live browser, Last Updated 10/22/2026 16:56 ET; 52-week NYSE highs 94 / lows 64, Nasdaq highs 67 / lows 280)"
mi["breadth"] = b

mi["fearGreed"] = {
    "value": 20,
    "label": "Extreme Fear",
    "previousClose": 31,
    "asof": "Oct 22, 2026 close (cnn.com live page, last updated 4:44:06 PM ET)",
    "note": "Prev close 31.",
    "url": "https://www.cnn.com/markets/fear-and-greed",
    "dataUrl": "https://raw.githubusercontent.com/whit3rabbit/fear-greed-data/main/fear-greed.csv",
}

mi["flows"] = [
    {"ticker": "SPY", "value": -2.42, "label": "-$2.42B outflow"},
    {"ticker": "QQQ", "value": -0.5739, "label": "-$573.9M outflow"},
    {"ticker": "IWM", "value": None, "label": "not reported today"},
]
mi["flowsAsOf"] = "ETF Action ETF Flow Report posted Oct 22, 2026 (covers Oct 21 session activity). Total net ETF flows +$11.23B. SPY -$2.42B, QQQ -$573.9M, IWM not listed in report."

patch = {"MARKET_INTERNALS": mi}
out = Path("/tmp/patch.json")
out.write_text(json.dumps(patch, indent=2))
print("wrote", out, "| A/D:", b["advanceDeclineRatio"], "| >50d:", b["above50"], "| F&G:", mi["fearGreed"]["value"])
