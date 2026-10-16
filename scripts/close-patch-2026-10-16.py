#!/usr/bin/env python3
"""Close-refresh patch builder for StockSite data.json (Fri 2026-10-16).

VERIFIED VALUES:
- SMI: finalized vs 391 Yahoo SPY 1m bars, full Oct-16 session
  (open 773.24; 10:00 close 771.42 -0.2347%; 15:00 close 761.74;
   close 763.25 +0.1982% -> 999.71 +0.2347 +0.1982 = 1000.14).
- vixTerm: Yahoo ^VIX / ^VIX3M daily closes, Oct 16, 2026
  (^VIX 19.99 prev 16.46 +21.45%; ^VIX3M 20.50 prev 18.49 +10.87%; ratio 1.03).
- putCall: YCharts text fetch Oct 16 evening still shows Oct-14 finals
  as latest (equity 0.61, index 1.01); Oct-15 finals not yet visible in
  the fetch. Total carried last-good Sep 21 = 0.74.
- breadth / flows / fearGreed: carried last-good (Oct 15 verified)
  pending live-browser verification (browser task dispatched);
  follow-up patch if verified Oct-16 numbers arrive.
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
data = json.loads((REPO / "data.json").read_text())
mi = data["MARKET_INTERNALS"]

# --- SMI (FINAL) ---
smi = mi["smi"]
series = [s for s in smi.get("series", []) if s.get("date") != "Oct 16"]
series.append({"date": "Oct 16", "value": 1000.14})
smi["series"] = series
smi["status"] = "Finalized"
smi["latest"] = 1000.14
smi["change"] = 0.43
smi["asof"] = "Oct 16, 2026 close"
smi["note"] = ("Self-computed Don Hays-style (SPY proxy), never SentimenTrader. "
               "Oct 16: -first-30-min (-0.235%) + last-hour (+0.198%) = +0.433.")
smi["inputs"] = ("SPY open 773.24; 10:00 771.42 (-0.2347%); "
                 "15:00 761.74; close 763.25 (+0.1982%). "
                 "999.71 +0.2347 +0.1982 = 1000.14. "
                 "391 verified 1m bars, full 10-16 session")
mi["smi"] = smi

# --- VIX term (FINAL) ---
mi["vixTerm"] = {
    "spot": 19.99,
    "spotPrev": 16.46,
    "spotChange": 3.53,
    "spotChangePct": 21.45,
    "threeMonth": 20.50,
    "threeMonthPrev": 18.49,
    "threeMonthChangePct": 10.87,
    "ratio": 1.03,
    "state": "Contango (calm)",
    "asof": "Oct 16, 2026 close (Yahoo ^VIX / ^VIX3M daily)",
    "note": "^VIX3M 3-month VIX. 20.50/19.99 = 1.03.",
}

# --- put/call: Oct-14 finals still latest in YCharts fetch ---
pc = mi["putCall"]
pc["equity"] = 0.61
pc["equityAsOf"] = "Oct 14, 2026 (ycharts; Oct-15 finals post Oct 15 20:00 EDT, not yet visible in fetch)"
pc["index"] = 1.01
pc["indexAsOf"] = "Oct 14, 2026 (ycharts; Oct-15 finals post Oct 15 20:00 EDT, not yet visible in fetch)"
pc["totalAsOf"] = "Sep 21, 2026; Oct 16 total unavailable"
pc["asof"] = "Equity Oct 14, 2026 · Index Oct 14, 2026 (ycharts)"
mi["putCall"] = pc

# breadth, flows, flowsAsOf, fearGreed, aaii, fedWatch carried unchanged
for k in ("breadth", "flows", "flowsAsOf", "fearGreed", "aaii", "fedWatch"):
    assert k in mi, k

patch = {"MARKET_INTERNALS": mi}
out = Path("/tmp/patch.json")
out.write_text(json.dumps(patch, indent=2))
print("wrote", out, "| SMI latest:", smi["latest"], "| vix spot:", mi["vixTerm"]["spot"],
      "| index P/C:", pc["index"])
