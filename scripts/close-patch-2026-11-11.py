#!/usr/bin/env python3
"""Close refresh 2026-11-11: finalize MARKET_INTERNALS with Nov 11 closes.

Verified sources:
- VIX / VIX3M / SPY 1m bars: Yahoo chart API (daily closes + 391 verified 1m bars)
- Breadth ($ADRN/$ADDN/$S5FI/$S5TH/highs-lows): Barchart live browser, ~17:03 ET
- P/C: ycharts Nov 10 finals carried (Nov 11 finals due 20:00 EST)
- Flows: ETF Action flow report posted Nov 11 (Nov 10 session, T+1); IWM Nov 10
  flow not in ETF Action top-5 lists and ETFIQ still at Nov 9 -> Nov 9 carried
- F&G: whit3rabbit CSV mirror - Nov 11 row not posted yet; Nov 10 carried
"""
import copy
import json

DATA = "/home/hatch/workspace/StockSite/data.json"
PATCH = "/tmp/patch.json"

data = json.load(open(DATA))
mi = copy.deepcopy(data["MARKET_INTERNALS"])

# ---------- vixTerm: Nov 11 closes (Yahoo daily) ----------
mi["vixTerm"] = {
    "spot": 17.49,
    "spotPrev": 19.46,
    "spotChange": -1.97,
    "spotChangePct": -10.12,
    "threeMonth": 19.24,
    "threeMonthPrev": 20.64,
    "threeMonthChangePct": -6.78,
    "ratio": 1.10,
    "state": "Contango (calm)",
    "asof": "Nov 11, 2026 close",
    "note": ("^VIX3M 3-month VIX. 19.24/17.49 = 1.10. Contango (calm): 3M above spot. "
             "VIX fell 10.12% on Nov 11 as SPY rose 1.32% (749.92 -> 759.81). Yahoo daily closes."),
}

# ---------- putCall: Nov 10 finals carried; Nov 11 due 8 PM ET ----------
mi["putCall"]["asof"] = ("Nov 10, 2026 finals (ycharts, crawled Nov 11 ~7:30 AM ET; "
                         "Nov 11 finals due Nov 11 20:00 EST)")

# ---------- breadth: Nov 11 closes (Barchart, live browser) ----------
b = mi["breadth"]
b.update({
    "advanceDeclineRatio": 1.33,
    "adDifference": 263.0,
    "advanceDeclineAsOf": ("Nov 11, 2026 close (barchart $ADRN / $ADDN, live browser; 16:57 ET; "
        "Price History table confirms 1.33 / +263.00. Barchart Nov 10 $ADDN now shows -333.00 "
        "vs stored -334.00 - small end-of-day restatement.)"),
    "above50": 71.76,
    "above50Prev": 68.98,
    "above50AsOf": ("Nov 11, 2026 close (barchart $S5FI, live browser; 16:57 ET; Price History "
        "confirms 71.76, +2.78 pts vs Nov 10 68.98.)"),
    "above200": 63.81,
    "above200Prev": 62.82,
    "above200AsOf": ("Nov 11, 2026 close (barchart $S5TH, live browser; 16:57 ET; Price History "
        "confirms 63.81, +0.99 pts vs Nov 10 62.82.)"),
    "newHighs": 41,
    "newLows": 42,
    "nasdaqHighs": 64,
    "nasdaqLows": 142,
    "spHighs": None,
    "spLows": None,
    "highLowAsOf": ("Nov 11, 2026 (barchart highs-lows summary, live browser, Last Updated "
        "11/11/2026 16:57 ET; Overall 107/195, NYSE 41/42, Nasdaq 64/142)"),
})

# ---------- flows: Nov 10 session (ETF Action, posted Nov 11, T+1) ----------
mi["flows"] = [
    {"ticker": "SPY", "value": 4.33, "label": "$4.33B inflow (Nov 10 session)"},
    {"ticker": "QQQ", "value": 3.05, "label": "$3.05B inflow (Nov 10 session)"},
    {"ticker": "IWM", "value": -1.10, "label": "$1.10B outflow (Nov 9 session, carried)"},
]
mi["flowsAsOf"] = ("ETF Action ETF Flow Report posted Nov 11, 2026 (data as of Nov 10, 2026 session, "
    "T+1; total net flows +$26.52B). SPY +$4.33B; QQQ +$3.05B. IWM Nov 10 flow not in ETF "
    "Action top-5 lists and ETFIQ still at Nov 9 - Nov 9 value -$1.10B carried.")

# ---------- fearGreed: Nov 11 not yet posted in mirror; carry Nov 10 ----------
fg = mi["fearGreed"]
fg["note"] = (fg.get("note", "") +
    " Nov 11 value NOT yet posted in the mirror as of ~5:05 PM ET check "
    "(last CSV row still Nov 10 = 33.46) - carried; will refresh on the Nov 12 morning run.")

# ---------- smi: FINALIZED Nov 11 ----------
smi = mi["smi"]
smi.update({
    "status": "Finalized",
    "latest": 998.31,
    "change": -0.01,
    "asof": "Nov 11, 2026 close",
    "note": ("Self-computed Don Hays-style (SPY proxy), never SentimenTrader. "
             "Nov 11: -first-30-min (-0.0674%) + last-hour (-0.0802%) = -0.01."),
    "inputs": ("SPY open 756.80 (Yahoo 1m); 10:00 bar close 756.29 (-0.0674%); "
               "15:00 bar close 760.42; final close 759.81 (-0.0802%). "
               "998.32 + 0.0674 - 0.0802 = 998.31. Final close 759.81 is the 4:00 PM "
               "regular-market price (16:00 bar closed 759.81; after-hours NOT used). "
               "391 verified 1m bars."),
})
smi["series"].append({"date": "Nov 11", "value": 998.31})

# aaii / fedWatch carried verbatim.
json.dump({"MARKET_INTERNALS": mi}, open(PATCH, "w"))
print("patch written to", PATCH)
print("SMI finalized 998.31 (-0.01); VIX 17.49 (-10.12%) / VIX3M 19.24, ratio 1.10 contango")
print("Breadth A/D 1.33 / +263; >50d 71.76 / >200d 63.81; NH/NL Overall 107/195")
print("Flows Nov 10 sess: SPY +4.33 / QQQ +3.05, IWM Nov 9 carried -1.10; total +26.52")
