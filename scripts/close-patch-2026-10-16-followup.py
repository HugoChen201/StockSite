#!/usr/bin/env python3
"""Follow-up patch: verified live-browser Oct-16 close numbers.

Source: live browser task checked ~17:02-17:10 ET Oct 16, 2026.
- Barchart: $ADRN 0.77 (stamp Oct 16 16:40 ET), $ADDN -237 header
  (page Key Turning Points showed -239; header value used),
  $S5FI 45.12 (16:37 ET, prev close 44.13), $S5TH 51.88 unchanged
  (16:50 ET), highs/lows Last Updated 10/16/2026 16:58 ET:
  NYSE 61/51, Nasdaq 37/284.
- CNN Fear & Greed: 18 Extreme Fear, prev close 31, last updated
  Oct 16 4:47:26 PM ET; 1 week ago 46, 1 month ago 27.
- ETF Action Oct-16 report (T+1, Oct-15 activity): total +$19.12B,
  SPY +$7.65B, QQQ +$1.13B, IWM +$2.22B.
- YCharts live: Oct-15 finals now posted — equity 0.62, index 0.99
  (last updated Oct 15 21:53/21:54 EDT).
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
data = json.loads((REPO / "data.json").read_text())
mi = data["MARKET_INTERNALS"]

# --- breadth (Oct 16 finals, barchart live) ---
b = mi["breadth"]
b["advanceDeclineRatio"] = 0.77
b["adDifference"] = -237.0
b["advanceDeclineAsOf"] = "Oct 16, 2026 close (barchart $ADRN quote stamp 16:40 ET / $ADDN 16:40 ET, live browser)"
b["above50"] = 45.12
b["above50Prev"] = 44.13
b["above50AsOf"] = "Oct 16, 2026 close (barchart $S5FI, live browser, quote stamp 16:37 ET)"
b["above200"] = 51.88
b["above200Prev"] = 51.88
b["above200AsOf"] = "Oct 16, 2026 close (barchart $S5TH, live browser, quote stamp 16:50 ET; unchanged on day)"
b["newHighs"] = 61
b["newLows"] = 51
b["nasdaqHighs"] = 37
b["nasdaqLows"] = 284
b["highLowAsOf"] = "Oct 16, 2026 (barchart highs-lows summary, live browser, Last Updated 10/16/2026 16:58 ET; 52-week NYSE highs 61 / lows 51, Nasdaq highs 37 / lows 284)"
mi["breadth"] = b

# --- fear & greed (Oct 16, CNN live) ---
mi["fearGreed"] = {
    "value": 18,
    "label": "Extreme Fear",
    "previousClose": 31,
    "asof": "Oct 16, 2026 close (cnn.com live page, last updated 4:47:26 PM ET)",
    "note": "Prev close 31; 1 week ago 46; 1 month ago 27.",
    "url": "https://www.cnn.com/markets/fear-and-greed",
    "dataUrl": "https://raw.githubusercontent.com/whit3rabbit/fear-greed-data/main/fear-greed.csv",
}

# --- flows (ETF Action Oct-16 report, Oct-15 activity) ---
mi["flows"] = [
    {"ticker": "SPY", "value": 7.65, "label": "+$7.65B inflow"},
    {"ticker": "QQQ", "value": 1.13, "label": "+$1.13B inflow"},
    {"ticker": "IWM", "value": 2.22, "label": "+$2.22B inflow"},
]
mi["flowsAsOf"] = "ETF Action ETF Flow Report posted Oct 16, 2026 (T+1 data: covers Oct 15 session activity). Total net ETF flows +$19.12B. SPY +$7.65B, QQQ +$1.13B, IWM +$2.22B."

# --- put/call: Oct-15 finals (YCharts live) ---
pc = mi["putCall"]
pc["equity"] = 0.62
pc["equityAsOf"] = "Oct 15, 2026 (ycharts live; Oct-16 finals post Oct 16 20:00 EDT)"
pc["index"] = 0.99
pc["indexAsOf"] = "Oct 15, 2026 (ycharts live; Oct-16 finals post Oct 16 20:00 EDT)"
pc["totalAsOf"] = "Sep 21, 2026; Oct 16 total unavailable"
pc["asof"] = "Equity Oct 15, 2026 · Index Oct 15, 2026 (ycharts)"
mi["putCall"] = pc

patch = {"MARKET_INTERNALS": mi}
out = Path("/tmp/patch.json")
out.write_text(json.dumps(patch, indent=2))
print("wrote", out, "| A/D:", b["advanceDeclineRatio"], "| >50d:", b["above50"],
      "| F&G:", mi["fearGreed"]["value"], "| P/C eq/idx:", pc["equity"], pc["index"])
