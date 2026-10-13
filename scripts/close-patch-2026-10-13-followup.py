#!/usr/bin/env python3
"""Close-refresh FOLLOW-UP patch for StockSite data.json (Tue 2026-10-13).

Live-browser verified Oct 13, 2026 ~5 PM ET (arrived after the main
close patch v1193 was pushed):
- breadth (barchart live): $ADRN 1.20 (16:37 ET), $ADDN 170.00 (16:50 ET),
  $S5FI 38.17 (prev 36.97, 16:47 ET), $S5TH 49.70 (prev 49.50, 16:47 ET),
  highs/lows Last Updated 10/13/2026 16:57 ET: NYSE 48/88, Nasdaq 38/348.
- fearGreed (CNN live): 45 Neutral, last updated Oct 13 4:47:25 PM ET,
  prev close 45; 1wk 46; 1mo 32; 1yr 29.
- flows (ETF Action report posted Oct 13, T+1 = Oct 12 activity):
  total +$10.65B; SPY -$116.8M, QQQ -$1.16B, IWM -$641.5M.
- putCall total: ycharts page not accessible (404) — carried last-good.
SMI / vixTerm / putCall equity+index already finalized in v1193 — carried.
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
data = json.loads((REPO / "data.json").read_text())
mi = data["MARKET_INTERNALS"]

mi["breadth"] = {
    "advanceDeclineRatio": 1.20,
    "adDifference": 170.0,
    "advanceDeclineAsOf": "Oct 13, 2026 close (barchart $ADRN quote stamp 16:37 ET / $ADDN 16:50 ET, live browser)",
    "above50": 38.17,
    "above50Prev": 36.97,
    "above50AsOf": "Oct 13, 2026 close (barchart $S5FI, live browser, quote stamp 16:47 ET)",
    "above200": 49.70,
    "above200Prev": 49.50,
    "above200AsOf": "Oct 13, 2026 close (barchart $S5TH, live browser, quote stamp 16:47 ET)",
    "newHighs": 48,
    "newLows": 88,
    "nasdaqHighs": 38,
    "nasdaqLows": 348,
    "spHighs": None,
    "spLows": None,
    "highLowAsOf": "Oct 13, 2026 (barchart highs-lows summary, live browser, Last Updated 10/13/2026 16:57 ET; 52-week NYSE highs 48 / lows 88, Nasdaq highs 38 / lows 348)",
    "above50Url": "https://www.barchart.com/stocks/quotes/$S5FI",
    "above200Url": "https://www.barchart.com/stocks/quotes/$S5TH",
    "adRatioUrl": "https://www.barchart.com/stocks/quotes/%24ADRN",
    "adDifferenceUrl": "https://www.barchart.com/stocks/quotes/%24ADDN",
    "highLowUrl": "https://www.barchart.com/stocks/highs-lows/summary",
}

mi["fearGreed"] = {
    "value": 45,
    "label": "Neutral",
    "previousClose": 45,
    "asof": "Oct 13, 2026 close (cnn.com live page, last updated 4:47:25 PM ET)",
    "note": "Prev close 45; 1 week ago 46; 1 month ago 32; 1 year ago 29.",
    "url": "https://www.cnn.com/markets/fear-and-greed",
    "dataUrl": "https://raw.githubusercontent.com/whit3rabbit/fear-greed-data/main/fear-greed.csv",
}

mi["flowsAsOf"] = ("ETF Action ETF Flow Report posted Oct 13, 2026 (T+1 data: "
                   "covers Oct 12 session activity). Total net ETF flows +$10.65B. "
                   "SPY -$116.8M, QQQ -$1.16B, IWM -$641.5M.")
mi["flows"] = [
    {"ticker": "SPY", "value": -0.1168, "label": "-$116.8M outflow"},
    {"ticker": "QQQ", "value": -1.16, "label": "-$1.16B outflow"},
    {"ticker": "IWM", "value": -0.6415, "label": "-$641.5M outflow"},
]

pc = mi["putCall"]
pc["totalAsOf"] = "Sep 21, 2026; Oct 13 total unavailable (ycharts total page not accessible)"
mi["putCall"] = pc

# carry-checks: finalized blocks from v1193 must still be present
assert mi["smi"]["latest"] == 999.05 and mi["smi"]["status"] == "Finalized", mi["smi"]
assert mi["vixTerm"]["spot"] == 15.27, mi["vixTerm"]
assert mi["putCall"]["index"] == 0.98, mi["putCall"]
for k in ("aaii", "fedWatch", "flowsUrl", "flowsToolUrl"):
    assert k in mi, k

patch = {"MARKET_INTERNALS": mi}
out = Path("/tmp/patch.json")
out.write_text(json.dumps(patch, indent=2))
print("wrote", out, "| breadth A/D:", mi["breadth"]["advanceDeclineRatio"],
      "| F&G:", mi["fearGreed"]["value"], "| flows total +$10.65B")
