#!/usr/bin/env python3
"""Close-refresh patch builder for StockSite data.json (Tue 2026-10-20).

VERIFIED VALUES:
- SMI: finalized vs 391 Yahoo SPY 1m bars, full Oct-20 session
  (open 765.86; 10:00 close 767.92 +0.2690%; 15:00 close 769.01;
   close 769.05 +0.0052% -> 1000.06 -0.2690 +0.0052 = 999.80).
- vixTerm: Yahoo ^VIX / ^VIX3M daily closes, Oct 20, 2026
  (^VIX 17.31 prev 18.44 -6.13%; ^VIX3M 18.99 prev 19.60 -3.11%; ratio 1.10).
  This corrects the intraday-mixed vixTerm block from the 3:55 PM 5-min run
  (spot 17.59 / threeMonth 19.11 / spotPrev 19.99 were stale/mixed).
- putCall: YCharts text fetch Oct 20 evening still shows Oct-16 finals
  as latest (equity 0.65, index 1.05); Oct-19 finals not yet visible,
  Oct-20 finals post ~8 PM ET. Total carried last-good Sep 21 = 0.74.
- breadth / flows / fearGreed: carried last-good (Oct 19 verified)
  pending live-browser verification (browser task dispatched);
  follow-up patch if verified Oct-20 numbers arrive.
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
data = json.loads((REPO / "data.json").read_text())
mi = data["MARKET_INTERNALS"]

# --- SMI (FINAL) ---
smi = mi["smi"]
series = [s for s in smi.get("series", []) if s.get("date") != "Oct 20"]
series.append({"date": "Oct 20", "value": 999.8})
smi["series"] = series
smi["status"] = "Finalized"
smi["latest"] = 999.8
smi["change"] = -0.26
smi["asof"] = "Oct 20, 2026 close"
smi["note"] = ("Self-computed Don Hays-style (SPY proxy), never SentimenTrader. "
               "Oct 20: -first-30-min (+0.269%) + last-hour (+0.005%) = -0.264.")
smi["inputs"] = ("SPY open 765.86; 10:00 767.92 (+0.2690%); "
                 "15:00 769.01; close 769.05 (+0.0052%). "
                 "1000.06 -0.2690 +0.0052 = 999.80. "
                 "391 verified 1m bars, full 10-20 session")
# clear stale intraday fields so the card shows the final, not the 3:55 PM intraday estimate
smi.pop("intraday", None)
smi.pop("intradayAsOf", None)
smi.pop("intradayInputs", None)
mi["smi"] = smi

# --- VIX term (FINAL) ---
mi["vixTerm"] = {
    "spot": 17.31,
    "spotPrev": 18.44,
    "spotChange": -1.13,
    "spotChangePct": -6.13,
    "threeMonth": 18.99,
    "threeMonthPrev": 19.6,
    "threeMonthChangePct": -3.11,
    "ratio": 1.1,
    "state": "Contango (calm)",
    "asof": "Oct 20, 2026 close (Yahoo ^VIX / ^VIX3M daily)",
    "note": "^VIX3M 3-month VIX. 18.99/17.31 = 1.10.",
}

# --- put/call: Oct-16 finals still latest in YCharts fetch (already correct in data.json; restate explicitly) ---
pc = mi["putCall"]
pc["equity"] = 0.65
pc["equityAsOf"] = "Oct 16, 2026 (ycharts; next release Oct 19 2026 20:00 EDT)"
pc["index"] = 1.05
pc["indexAsOf"] = "Oct 16, 2026 (ycharts; next release Oct 19 2026 20:00 EDT)"
pc["totalAsOf"] = "Sep 21, 2026; Oct 20 total unavailable"
pc["asof"] = "Equity Oct 16, 2026 \u00b7 Index Oct 16, 2026 (ycharts)"
mi["putCall"] = pc

# breadth, flows, flowsAsOf, fearGreed, aaii, fedWatch carried unchanged
for k in ("breadth", "flows", "flowsAsOf", "fearGreed", "aaii", "fedWatch"):
    assert k in mi, k

patch = {"MARKET_INTERNALS": mi}
out = Path("/tmp/patch.json")
out.write_text(json.dumps(patch, indent=2))
print("wrote", out, "| SMI latest:", smi["latest"], "| vix spot:", mi["vixTerm"]["spot"],
      "| index P/C:", pc["index"])
