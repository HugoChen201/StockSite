#!/usr/bin/env python3
"""Close refresh 2026-11-10: finalize MARKET_INTERNALS with Nov 10 closes.

Verified sources:
- VIX / VIX3M / SPY 1m bars: Yahoo chart API (daily closes + 391 verified 1m bars)
- Breadth ($ADRN/$ADDN/$S5FI/$S5TH/highs-lows): Barchart live browser, 16:53-16:59 ET
- P/C: ycharts (Nov 9 finals re-verified; Nov 10 finals due 20:00 EST)
- Flows: ETF Action flow report posted Nov 10 (Nov 9 session, T+1)
- F&G: whit3rabbit CSV mirror — Nov 10 row not posted yet; Nov 9 carried
"""
import copy
import json

DATA = "/home/hatch/workspace/StockSite/data.json"
PATCH = "/tmp/patch.json"

data = json.load(open(DATA))
mi = copy.deepcopy(data["MARKET_INTERNALS"])

# ---------- vixTerm: Nov 10 closes (Yahoo daily) ----------
mi["vixTerm"] = {
    "spot": 19.46,
    "spotPrev": 19.92,
    "spotChange": -0.46,
    "spotChangePct": -2.31,
    "threeMonth": 20.64,
    "threeMonthPrev": 20.85,
    "threeMonthChangePct": -1.01,
    "ratio": 1.06,
    "state": "Contango (calm)",
    "asof": "Nov 10, 2026 close",
    "note": ("^VIX3M 3-month VIX. 20.64/19.46 = 1.06. Contango (calm): 3M above spot. "
             "VIX fell 2.31% on Nov 10 as SPY fell 0.37% (752.69 -> 749.92). Yahoo daily closes."),
}

# ---------- putCall: Nov 9 finals carried; Nov 10 due 8 PM ET ----------
mi["putCall"]["asof"] = ("Nov 9, 2026 finals (ycharts, re-verified Nov 10 ~5:10 PM ET; "
                         "Nov 10 finals due Nov 10 20:00 EST)")

# ---------- breadth: Nov 10 closes (Barchart, live browser) ----------
b = mi["breadth"]
b.update({
    "advanceDeclineRatio": 0.69,
    "adDifference": -334.0,
    "advanceDeclineAsOf": ("Nov 10, 2026 close (barchart $ADRN / $ADDN, live browser; 16:56 ET; "
        "Price History table confirms 0.69 / -334.00. A stale 16:43 header load showed prev 1.00 / "
        "open 0.34 — conflicts with Price History, discarded. Barchart prev values 4.52 / 1,168.00 "
        "vs stored Nov 9 closes 4.50 / 1,167.00 — small end-of-day restatement.)"),
    "above50": 68.98,
    "above50Prev": 69.18,
    "above50AsOf": ("Nov 10, 2026 close (barchart $S5FI, live browser; 16:53 ET; Price History "
        "confirms 68.98. Barchart now shows Nov 9 latest as 69.18 vs stored 69.52 — restated.)"),
    "above200": 62.82,
    "above200Prev": 63.02,
    "above200AsOf": ("Nov 10, 2026 close (barchart $S5TH, live browser; 16:53 ET; Price History "
        "confirms 62.82. Barchart now shows Nov 9 latest as 63.02 vs stored 63.14 — restated.)"),
    "newHighs": 36,
    "newLows": 57,
    "nasdaqHighs": 52,
    "nasdaqLows": 197,
    "spHighs": None,
    "spLows": None,
    "highLowAsOf": ("Nov 10, 2026 (barchart highs-lows summary, live browser, Last Updated "
        "11/10/2026 16:59 ET; Overall 91/264, NYSE 36/57, Nasdaq 52/197)"),
})

# ---------- flows: Nov 9 session (ETF Action, posted Nov 10, T+1) ----------
mi["flows"] = [
    {"ticker": "SPY", "value": -4.19, "label": "$4.19B outflow (Nov 9 session)"},
    {"ticker": "QQQ", "value": 2.36, "label": "$2.36B inflow (Nov 9 session)"},
    {"ticker": "IWM", "value": -1.10, "label": "$1.10B outflow (Nov 9 session)"},
]
mi["flowsAsOf"] = ("ETF Action ETF Flow Report posted Nov 10, 2026 (data as of Nov 9, 2026 session, "
    "T+1; total net flows -$2.15B). SPY -$4.19B; QQQ +$2.36B; IWM -$1.10B.")

# ---------- fearGreed: Nov 10 not yet posted in mirror; carry Nov 9 ----------
fg = mi["fearGreed"]
fg["note"] = (fg.get("note", "") +
    " Nov 10 value NOT yet posted in the mirror as of ~5:10 PM ET check "
    "(last CSV row still Nov 9 = 31.71) — carried; will refresh on the Nov 11 morning run.")

# ---------- smi: FINALIZED Nov 10 ----------
smi = mi["smi"]
smi.update({
    "status": "Finalized",
    "latest": 998.32,
    "change": -0.33,
    "asof": "Nov 10, 2026 close",
    "note": ("Self-computed Don Hays-style (SPY proxy), never SentimenTrader. "
             "Nov 10: -first-30-min (+0.5134%) + last-hour (+0.1870%) = -0.33."),
    "inputs": ("SPY open 747.90 (Yahoo 1m); 10:00 bar close 751.74 (+0.5134%); "
               "15:00 bar close 748.52; final close 749.92 (+0.1870%). "
               "998.65 - 0.5134 + 0.1870 = 998.32. Final close 749.92 is the 4:00 PM "
               "regular-market price (16:00 bar closed 749.92; after-hours NOT used). "
               "391 verified 1m bars."),
})
smi["series"].append({"date": "Nov 10", "value": 998.32})

# aaii / fedWatch carried verbatim.
json.dump({"MARKET_INTERNALS": mi}, open(PATCH, "w"))
print("patch written to", PATCH)
print("SMI finalized 998.32 (-0.33); VIX 19.46 (-2.31%) / VIX3M 20.64, ratio 1.06 contango")
print("Breadth A/D 0.69 / -334; >50d 68.98 / >200d 62.82; NH/NL Overall 91/264")
print("Flows Nov 9 sess: SPY -4.19 / QQQ +2.36 / IWM -1.10, total -2.15")
