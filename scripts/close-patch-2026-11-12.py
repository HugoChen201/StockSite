#!/usr/bin/env python3
"""Close refresh 2026-11-12: finalize MARKET_INTERNALS with Nov 12 closes.

Verified sources:
- VIX / VIX3M / SPY 1m bars: Yahoo chart API (daily closes + 391 verified 1m bars)
- Breadth ($ADRN/$ADDN/$S5FI/$S5TH/highs-lows): Barchart live browser, ~17:01-17:02 ET
- P/C: ycharts Nov 11 finals carried (Nov 12 finals due 20:00 EST)
- Flows: ETF Action flow report posted Nov 12 (Nov 11 session, T+1); total +$1.54B
- F&G: whit3rabbit CSV mirror - Nov 12 row not posted yet; Nov 11 carried
"""
import copy
import json

DATA = "/home/hatch/workspace/StockSite/data.json"
PATCH = "/tmp/patch.json"

data = json.load(open(DATA))
mi = copy.deepcopy(data["MARKET_INTERNALS"])

# ---------- vixTerm: Nov 12 closes (Yahoo daily) ----------
mi["vixTerm"] = {
    "spot": 18.70,
    "spotPrev": 17.49,
    "spotChange": 1.21,
    "spotChangePct": 6.92,
    "threeMonth": 20.06,
    "threeMonthPrev": 19.24,
    "threeMonthChangePct": 4.26,
    "ratio": 1.07,
    "state": "Contango (calm)",
    "asof": "Nov 12, 2026 close",
    "note": ("^VIX3M 3-month VIX. 20.06/18.70 = 1.07. Contango (calm): 3M above spot. "
             "VIX rose 6.92% on Nov 12 as SPY fell 0.35% (759.81 -> 757.12). Yahoo daily closes."),
}

# ---------- putCall: Nov 11 finals carried; Nov 12 due 8 PM ET ----------
mi["putCall"]["asof"] = ("Nov 11, 2026 finals (ycharts, crawled Nov 12 ~5:05 PM ET; "
                         "Nov 12 finals due Nov 12 20:00 EST)")

# ---------- breadth: Nov 12 closes (Barchart, live browser) ----------
b = mi["breadth"]
b.update({
    "advanceDeclineRatio": 0.32,
    "adDifference": -943.0,
    "advanceDeclineAsOf": ("Nov 12, 2026 close (barchart $ADRN / $ADDN, live browser; 17:01 ET; "
        "Price History table confirms 0.32 / -943.00. Note: $ADDN live header showed -944.00 on "
        "one re-check; Price History table and 52-Week Key Points both showed -943.00 across "
        "three observations, so -943.00 used. Prior close 1.33 / +262.00.)"),
    "above50": 69.78,
    "above50Prev": 71.76,
    "above50AsOf": ("Nov 12, 2026 close (barchart $S5FI, live browser; 17:01 ET; Price History "
        "confirms 69.78, -1.98 pts vs Nov 11 71.76.)"),
    "above200": 61.82,
    "above200Prev": 63.81,
    "above200AsOf": ("Nov 12, 2026 close (barchart $S5TH, live browser; 17:01 ET; Price History "
        "confirms 61.82, -1.99 pts vs Nov 11 63.81.)"),
    "newHighs": 29,
    "newLows": 81,
    "nasdaqHighs": 36,
    "nasdaqLows": 223,
    "spHighs": None,
    "spLows": None,
    "highLowAsOf": ("Nov 12, 2026 (barchart highs-lows summary, live browser, Last Updated "
        "11/12/2026 16:51 ET; Overall 67/325, NYSE 29/81, Nasdaq 36/223, NYSE Arca 2/21; "
        "5,087 stocks considered. Note: this Summary tab has no daily row - 52-week counts "
        "used; prior days used the newhilo.php daily table, so counts are not strictly "
        "comparable day-over-day.)"),
})

# ---------- flows: Nov 11 session (ETF Action, posted Nov 12, T+1) ----------
mi["flows"] = [
    {"ticker": "SPY", "value": 2.06, "label": "$2.06B inflow (Nov 11 session)"},
    {"ticker": "QQQ", "value": -0.74, "label": "$0.74B outflow (Nov 11 session)"},
    {"ticker": "IWM", "value": -0.39, "label": "$0.39B outflow (Nov 11 session)"},
]
mi["flowsAsOf"] = ("ETF Action ETF Flow Report posted Nov 12, 2026 (data as of Nov 11, 2026 session, "
    "T+1; total net flows +$1.54B). SPY +$2.06B; QQQ -$0.74B; IWM -$0.39B.")

# ---------- fearGreed: Nov 12 not yet posted in mirror; carry Nov 11 ----------
fg = mi["fearGreed"]
fg["note"] = (fg.get("note", "") +
    " Nov 12 value NOT yet posted in the mirror as of ~5:05 PM ET check "
    "(last CSV row still Nov 11 = 36.97) - carried; will refresh on the Nov 13 morning run.")

# ---------- smi: FINALIZED Nov 12 ----------
smi = mi["smi"]
smi.update({
    "status": "Finalized",
    "latest": 997.91,
    "change": -0.40,
    "asof": "Nov 12, 2026 close",
    "note": ("Self-computed Don Hays-style (SPY proxy), never SentimenTrader. "
             "Nov 12: -first-30-min (-0.3714%) + last-hour (-0.0317%) = -0.40."),
    "inputs": ("SPY open 753.98 (Yahoo 1m); 10:00 bar close 756.78 (+0.3714%); "
               "15:00 bar close 757.36; final close 757.12 (-0.0317%). "
               "998.31 - 0.3714 - 0.0317 = 997.91. Final close 757.12 is the 4:00 PM "
               "regular-market price (16:00 bar closed 757.12; after-hours NOT used). "
               "391 verified 1m bars."),
})
smi["series"].append({"date": "Nov 12", "value": 997.91})

# aaii / fedWatch carried verbatim.
json.dump({"MARKET_INTERNALS": mi}, open(PATCH, "w"))
print("patch written to", PATCH)
print("SMI finalized 997.91 (-0.40); VIX 18.70 (+6.92%) / VIX3M 20.06, ratio 1.07 contango")
print("Breadth A/D 0.32 / -943; >50d 69.78 / >200d 61.82; NH/NL Overall 67/325")
print("Flows Nov 11 sess: SPY +2.06 / QQQ -0.74 / IWM -0.39; total +1.54")
