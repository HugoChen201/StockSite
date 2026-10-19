#!/usr/bin/env python3
"""Close-refresh patch builder for StockSite data.json (Mon 2026-10-19).

VERIFIED VALUES:
- SMI: finalized vs 391 Yahoo SPY 1m bars, full Oct-19 session
  (open 767.23; 10:00 close 766.50 -0.0951%; 15:00 close 767.83;
   close 766.48 -0.1758% -> 1000.14 +0.0951 -0.1758 = 1000.06).
- vixTerm: Yahoo ^VIX / ^VIX3M daily closes, Oct 19, 2026
  (^VIX 18.44 prev 19.99 -7.75%; ^VIX3M 19.60 prev 20.50 -4.39%; ratio 1.06).
  This corrects the intraday-mixed vixTerm block from the 3:59 PM 5-min run.
- putCall: YCharts text fetch Oct 19 evening still shows Oct-16 finals
  as latest (equity 0.65, index 1.05); Oct-19 finals post Oct 19 20:00 EDT.
  Total carried last-good Sep 21 = 0.74.
- breadth / flows / fearGreed: carried last-good (Oct 16 verified)
  pending live-browser verification (browser task dispatched);
  follow-up patch if verified Oct-19 numbers arrive.
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
data = json.loads((REPO / "data.json").read_text())
mi = data["MARKET_INTERNALS"]

# --- SMI (FINAL) ---
smi = mi["smi"]
series = [s for s in smi.get("series", []) if s.get("date") != "Oct 19"]
series.append({"date": "Oct 19", "value": 1000.06})
smi["series"] = series
smi["status"] = "Finalized"
smi["latest"] = 1000.06
smi["change"] = -0.08
smi["asof"] = "Oct 19, 2026 close"
smi["note"] = ("Self-computed Don Hays-style (SPY proxy), never SentimenTrader. "
               "Oct 19: -first-30-min (-0.095%) + last-hour (-0.176%) = -0.081.")
smi["inputs"] = ("SPY open 767.23; 10:00 766.50 (-0.0951%); "
                 "15:00 767.83; close 766.48 (-0.1758%). "
                 "1000.14 +0.0951 -0.1758 = 1000.06. "
                 "391 verified 1m bars, full 10-19 session")
# clear stale intraday fields so the card shows the final, not the 3:59 PM intraday estimate
smi.pop("intraday", None)
smi.pop("intradayAsOf", None)
smi.pop("intradayInputs", None)
mi["smi"] = smi

# --- VIX term (FINAL) ---
mi["vixTerm"] = {
    "spot": 18.44,
    "spotPrev": 19.99,
    "spotChange": -1.55,
    "spotChangePct": -7.75,
    "threeMonth": 19.60,
    "threeMonthPrev": 20.50,
    "threeMonthChangePct": -4.39,
    "ratio": 1.06,
    "state": "Contango (calm)",
    "asof": "Oct 19, 2026 close (Yahoo ^VIX / ^VIX3M daily)",
    "note": "^VIX3M 3-month VIX. 19.60/18.44 = 1.06.",
}

# --- put/call: Oct-16 finals still latest in YCharts fetch (already correct in data.json; restate explicitly) ---
pc = mi["putCall"]
pc["equity"] = 0.65
pc["equityAsOf"] = "Oct 16, 2026 (ycharts; next release Oct 19 2026 20:00 EDT)"
pc["index"] = 1.05
pc["indexAsOf"] = "Oct 16, 2026 (ycharts; next release Oct 19 2026 20:00 EDT)"
pc["totalAsOf"] = "Sep 21, 2026; Oct 19 total unavailable"
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
