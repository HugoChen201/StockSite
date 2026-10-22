#!/usr/bin/env python3
"""Close-refresh patch builder for StockSite data.json (Thu 2026-10-22).

VERIFIED VALUES:
- SMI: finalized vs 391 Yahoo SPY 1m bars, full Oct-22 session
  (open 766.37; 10:00 close 767.22 +0.1109%; 15:00 close 761.67;
   close 763.96 +0.3007% -> 1000.09 -0.1109 +0.3007 = 1000.28).
- vixTerm: Yahoo ^VIX / ^VIX3M daily closes, Oct 22, 2026
  (^VIX 19.03 prev 16.68 +14.09%; ^VIX3M 20.12 prev 18.72 +7.48%; ratio 1.06).
  Corrects intraday-mixed 3:55 PM block (spot 19.74 / spotPrev 17.31 stale).
- putCall: YCharts text fetch Oct 22 evening still shows Oct-20 finals
  as latest (equity 0.56, index 1.01); Oct-21 finals post ~8 PM ET Oct 22.
  Total carried last-good Sep 21 = 0.74.
- breadth / flows / fearGreed: carried last-good (Oct 21 verified)
  pending live-browser verification (browser task 01bfecea dispatched);
  follow-up patch if verified Oct-22 numbers arrive.
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
data = json.loads((REPO / "data.json").read_text())
mi = data["MARKET_INTERNALS"]

# --- SMI (FINAL) ---
smi = mi["smi"]
series = [s for s in smi.get("series", []) if s.get("date") != "Oct 22"]
series.append({"date": "Oct 22", "value": 1000.28})
smi["series"] = series
smi["status"] = "Finalized"
smi["latest"] = 1000.28
smi["change"] = 0.19
smi["asof"] = "Oct 22, 2026 close"
smi["note"] = ("Self-computed Don Hays-style (SPY proxy), never SentimenTrader. "
               "Oct 22: -first-30-min (+0.111%) + last-hour (+0.301%) = +0.190.")
smi["inputs"] = ("SPY open 766.37; 10:00 767.22 (+0.1109%); "
                 "15:00 761.67; close 763.96 (+0.3007%). "
                 "1000.09 -0.1109 +0.3007 = 1000.28. "
                 "391 verified 1m bars, full 10-22 session")
smi.pop("intraday", None)
smi.pop("intradayAsOf", None)
smi.pop("intradayInputs", None)
mi["smi"] = smi

# --- VIX term (FINAL) ---
mi["vixTerm"] = {
    "spot": 19.03,
    "spotPrev": 16.68,
    "spotChange": 2.35,
    "spotChangePct": 14.09,
    "threeMonth": 20.12,
    "threeMonthPrev": 18.72,
    "threeMonthChangePct": 7.48,
    "ratio": 1.06,
    "state": "Contango (calm)",
    "asof": "Oct 22, 2026 close (Yahoo ^VIX / ^VIX3M daily)",
    "note": "^VIX3M 3-month VIX. 20.12/19.03 = 1.06.",
}

# --- put/call: Oct-20 finals still latest in YCharts text fetch ---
pc = mi["putCall"]
pc["equity"] = 0.56
pc["equityAsOf"] = "Oct 20, 2026 (ycharts; Oct-21 finals not yet visible, post ~Oct 22 20:00 EDT)"
pc["index"] = 1.01
pc["indexAsOf"] = "Oct 20, 2026 (ycharts; Oct-21 finals not yet visible, post ~Oct 22 20:00 EDT)"
pc["totalAsOf"] = "Sep 21, 2026; Oct 22 total unavailable"
pc["asof"] = "Equity Oct 20, 2026 · Index Oct 20, 2026 (ycharts)"
mi["putCall"] = pc

for k in ("breadth", "flows", "flowsAsOf", "fearGreed", "aaii", "fedWatch"):
    assert k in mi, k

patch = {"MARKET_INTERNALS": mi}
out = Path("/tmp/patch.json")
out.write_text(json.dumps(patch, indent=2))
print("wrote", out, "| SMI latest:", smi["latest"], "| vix spot:", mi["vixTerm"]["spot"],
      "| P/C eq/idx:", pc["equity"], pc["index"])
