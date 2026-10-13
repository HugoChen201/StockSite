#!/usr/bin/env python3
"""Close-refresh patch builder for StockSite data.json (Tue 2026-10-13).

VERIFIED VALUES:
- SMI: finalized vs 391 Yahoo SPY 1m bars, full Oct-13 session
  (open 777.34; 10:00 close 777.97 +0.0810%; 15:00 close 777.80;
   daily close 778.01 +0.0270% -> 999.10 -0.0810 +0.0270 = 999.05).
- vixTerm: Yahoo ^VIX / ^VIX3M daily closes, Oct 13, 2026
  (^VIX 15.27 prev 15.21 +0.39%; ^VIX3M 17.96 prev 17.93 +0.17%; ratio 1.18).
- putCall: YCharts text fetch Oct 13 evening — equity Oct 12 = 0.62,
  index Oct 12 = 0.98 (newly posted; was Oct 9 = 1.13 this morning).
  Oct-13 finals post Oct 13 20:00 EDT. Total page fetch failed (405);
  total carried last-good Sep 21 = 0.74.
- breadth / flows / fearGreed: carried last-good (Oct 12 verified)
  pending live-browser verification; as-of labels already say Oct 12.
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
data = json.loads((REPO / "data.json").read_text())
mi = data["MARKET_INTERNALS"]

# --- SMI (FINAL) ---
smi = mi["smi"]
series = [s for s in smi.get("series", []) if s.get("date") != "Oct 13"]
series.append({"date": "Oct 13", "value": 999.05})
smi["series"] = series
smi["status"] = "Finalized"
smi["latest"] = 999.05
smi["change"] = -0.05
smi["asof"] = "Oct 13, 2026 close"
smi["note"] = ("Self-computed Don Hays-style (SPY proxy), never SentimenTrader. "
               "Oct 13: -first-30-min (+0.081%) + last-hour (+0.027%) = -0.054.")
smi["inputs"] = ("SPY open 777.34; 10:00 777.97 (+0.0810%); "
                 "15:00 777.80; close 778.01 (+0.0270%). "
                 "999.10 -0.0810 +0.0270 = 999.05. "
                 "391 verified 1m bars, full 10-13 session")
mi["smi"] = smi

# --- VIX term (FINAL) ---
mi["vixTerm"] = {
    "spot": 15.27,
    "spotPrev": 15.21,
    "spotChange": 0.06,
    "spotChangePct": 0.39,
    "threeMonth": 17.96,
    "threeMonthPrev": 17.93,
    "threeMonthChangePct": 0.17,
    "ratio": 1.18,
    "state": "Contango (calm)",
    "asof": "Oct 13, 2026 close (Yahoo ^VIX / ^VIX3M daily)",
    "note": "^VIX3M 3-month VIX. 17.96/15.27 = 1.18.",
}

# --- put/call: Oct-12 finals (YCharts) ---
pc = mi["putCall"]
pc["equity"] = 0.62
pc["equityAsOf"] = "Oct 12, 2026 (ycharts; Oct-13 finals post Oct 13 20:00 EDT)"
pc["index"] = 0.98
pc["indexAsOf"] = "Oct 12, 2026 (ycharts; Oct-13 finals post Oct 13 20:00 EDT)"
pc["asof"] = "Equity Oct 12, 2026 · Index Oct 12, 2026 (ycharts)"
mi["putCall"] = pc

# breadth, flows, flowsAsOf, fearGreed, aaii, fedWatch carried unchanged
for k in ("breadth", "flows", "flowsAsOf", "fearGreed", "aaii", "fedWatch"):
    assert k in mi, k

patch = {"MARKET_INTERNALS": mi}
out = Path("/tmp/patch.json")
out.write_text(json.dumps(patch, indent=2))
print("wrote", out, "| SMI latest:", smi["latest"], "| vix spot:", mi["vixTerm"]["spot"],
      "| index P/C:", pc["index"])
