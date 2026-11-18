#!/usr/bin/env python3
"""Close refresh patch for Wed Nov 18, 2026. Builds /tmp/patch.json from
verified Nov 18 close data; MARKET_INTERNALS replaced wholesale (carried
blocks copied from current data.json)."""
import json, copy

DATA = "/home/hatch/workspace/StockSite/data.json"
data = json.load(open(DATA))
mi = copy.deepcopy(data["MARKET_INTERNALS"])

# --- fearGreed: Nov 18 final, CNN live (official print) ---
# CNN page loaded live Nov 18 ~5:05 PM ET, NOT blocked: 25 Extreme Fear,
# previous close 25 Extreme Fear, 1 week ago 35 Fear; last updated 4:51:49 PM ET.
# Value unchanged day-over-day (25 -> 25).
mi["fearGreed"] = {
    "value": 25,
    "label": "Extreme Fear",
    "previousClose": 25,
    "asof": "Nov 18, 2026 close (CNN live, last updated 4:51:49 PM ET)",
    "note": ("CNN official print read live Nov 18 ~5:05 PM ET: 25 Extreme Fear "
             "('Extreme Fear is driving the US market'), previous close 25 Extreme "
             "Fear, 1 week ago 35 Fear. Value unchanged day-over-day. SPY fell "
             "0.31% on the day (732.44 -> 730.20); VIX -3.53%."),
    "url": "https://www.cnn.com/markets/fear-and-greed",
}

# --- vixTerm: Yahoo daily closes, Nov 18 ---
# ^VIX 24.56 (prev 25.46, -0.90, -3.53%); ^VIX3M 24.29 (prev 24.98, -0.69,
# -2.76%). Ratio 24.29/24.56 = 0.99 -> still backwardation. Nov 16-17 values
# in the 5-day series match stored closes exactly.
mi["vixTerm"] = {
    "spot": 24.56,
    "spotPrev": 25.46,
    "spotChange": -0.90,
    "spotChangePct": -3.53,
    "threeMonth": 24.29,
    "threeMonthPrev": 24.98,
    "threeMonthChangePct": -2.76,
    "ratio": 0.99,
    "state": "Backwardation (stress)",
    "asof": "Nov 18, 2026 close",
    "note": ("^VIX3M 3-month VIX. 24.29/24.56 = 0.99. Backwardation: 3M still below "
             "spot, though the inversion narrowed as VIX eased 3.53% on Nov 18 "
             "(SPY -0.31%, 732.44 -> 730.20). Yahoo daily closes; Nov 16-17 values "
             "in the 5-day series match stored closes exactly."),
}

# --- putCall: Nov 17 finals (ycharts, posted Nov 17 22:33 EST) ---
# Equity 0.71, index 0.98, total 0.98 (Nov 16: 0.73/1.01/0.95). Nov 18 finals
# due Nov 18 20:00 EST — not yet posted at ~5:11 PM ET read.
# NOTE: the old total URL (cboe_total_put_call_ratio) 404s; correct page is
# ycharts.com/indicators/total_putcall_ratio (CBOE Total Put/Call Ratio,
# I:CBOETPCR) — stored as totalUrl going forward.
mi["putCall"] = {
    "equity": 0.71,
    "equityAsOf": "Nov 17, 2026 (ycharts)",
    "equityUrl": "https://ycharts.com/indicators/cboe_equity_put_call_ratio",
    "index": 0.98,
    "indexAsOf": "Nov 17, 2026 (ycharts)",
    "indexUrl": "https://ycharts.com/indicators/cboe_index_put_call_ratio",
    "total": 0.98,
    "totalAsOf": "Nov 17, 2026 (ycharts)",
    "totalUrl": "https://ycharts.com/indicators/total_putcall_ratio",
    "asof": ("Nov 17, 2026 finals (ycharts, live browser Nov 18 ~5:11 PM ET; "
             "all three pages Last Updated Nov 17, 2026 22:33 EST; Nov 18 finals "
             "due Nov 18 20:00 EST)"),
}

# --- breadth: Barchart live browser, Nov 18 close ---
# $S5FI 56.26 (-1.59 vs Nov 17 57.85); $S5TH 56.06 (unch vs Nov 17 56.06).
# $ADVN 855 / $DECN 972 -> ratio 0.88 computed; $ADDN -117 (+1,040 vs -1,157).
# Highs/lows from the highs-lows Summary tab (Last Updated 11/18 16:57 ET):
# Overall 40/584, NYSE 18/161, Nasdaq 21/383, Arca 1/40 — per spec, the
# summary tab is used, NOT the quote-symbol set.
# CONFLICTS (not used): $ADRN printed 0.87 (counts imply 0.88) and its
# previous-close field prints 1.00, which is wrong (Nov 17 counts 337/1,494
# = 0.23, as stored). Quote symbols $MAHN 19 / $MALN 166 disagree with the
# summary page's NYSE 18/161 by +1/+5; $MAHQ 21 / $MALQ 383 agree with it.
# $MALQ's own Key Turning Points table shows 382 vs the 383 headline.
mi["breadth"] = {
    "above200": 56.06,
    "above200AsOf": "Nov 18, 2026 close (barchart $S5TH, live browser; 56.06, unchanged vs Nov 17 56.06.)",
    "above200Prev": 56.06,
    "above200Url": "https://www.barchart.com/stocks/quotes/$S5TH",
    "above50": 56.26,
    "above50AsOf": "Nov 18, 2026 close (barchart $S5FI, live browser; 56.26, -1.59 pts vs Nov 17 57.85.)",
    "above50Prev": 57.85,
    "above50Url": "https://www.barchart.com/stocks/quotes/$S5FI",
    "adDifference": -117.0,
    "adDifferenceUrl": "https://www.barchart.com/stocks/quotes/%24ADDN",
    "adRatioUrl": "https://www.barchart.com/stocks/quotes/%24ADRN",
    "advanceDeclineAsOf": ("Nov 18, 2026 close (barchart $ADVN/$DECN/$ADDN, live browser, "
        "16:47 ET; advancing 855, declining 972, net -117; ratio 0.88 computed "
        "from counts — Barchart's $ADRN prints 0.87 and its previous-close field "
        "prints 1.00, which is wrong (Nov 17 counts 337/1,494 = 0.23, as stored). "
        "Previous close: 337 adv / 1,494 dec, net -1,157.)"),
    "advanceDeclineRatio": 0.88,
    "highLowAsOf": ("Nov 18, 2026 (barchart highs-lows Summary tab, live browser, "
        "Last Updated 11/18/2026 16:57 ET; Overall 40/584, NYSE 18/161, Nasdaq "
        "21/383, Arca 1/40. Sums check: 18+21+1=40, 161+383+40=584. Conflicting "
        "views NOT used: quote symbols $MAHN 19 / $MALN 166 disagree with the "
        "summary page's NYSE 18/161; $MAHQ 21 / $MALQ 383 agree.)"),
    "highLowUrl": "https://www.barchart.com/stocks/highs-lows/summary",
    "nasdaqHighs": 21,
    "nasdaqLows": 383,
    "newHighs": 18,
    "newLows": 161,
    "spHighs": None,
    "spLows": None,
}

# --- flows: Nov 17 session (ETF Action report posted Nov 18, T+1) ---
# "ARK Surges as Mega-Cap Blend Dominates Flows", posted Nov 18, 2026.
# Total +$14.89B. SPY +$6.73B (top inflow); QQQ -$1.65B (top outflow).
# IWM exact 1-day flow NOT in the public report (no "IWM" match in the text;
# laggards were QQQ, DIA, IJR, VIG, LST) — carried Nov 16-session -$0.25B
# and flagged, per standing convention.
mi["flows"] = [
    {"ticker": "SPY", "value": 6.73, "label": "$6.73B inflow (Nov 17 session)"},
    {"ticker": "QQQ", "value": -1.65, "label": "$1.65B outflow (Nov 17 session)"},
    {"ticker": "IWM", "value": -0.25, "label": "$0.25B outflow (Nov 16 session — carried; Nov 17-session value not in public ETF Action report)"},
]
mi["flowsAsOf"] = ("Nov 17, 2026 session (ETF Action flow report posted Nov 18, T+1 basis; "
    "total +$14.89B day). SPY +$6.73B (top inflow); QQQ -$1.65B (top outflow). IWM exact "
    "Nov 17-session flow not shown in the public report (no 'IWM' match in the report "
    "text) — carried Nov 16-session -$0.25B and flagged.")
mi["flowsUrl"] = "https://www.etfaction.com/"
mi["flowsToolUrl"] = "https://www.etf.com/etfanalytics/etf-fund-flows-tool"

# --- smi: FINALIZED Nov 18 = 999.81 (+0.09) ---
smi = copy.deepcopy(mi["smi"])
smi["status"] = "Finalized"
smi["latest"] = 999.81
smi["change"] = 0.09
smi["asof"] = "Nov 18, 2026 close"
smi["series"] = smi["series"] + [{"date": "Nov 18", "value": 999.81}]
smi["note"] = ("Self-computed Don Hays-style (SPY proxy), never SentimenTrader. "
               "Nov 18: -first-30-min (-0.0803%) + last-hour (+0.0110%) = +0.09.")
smi["inputs"] = ("SPY open 734.66 (Yahoo 1m, 9:30 bar close); 10:00 bar close 734.07 "
                 "(-0.0803%); 15:00 bar close 730.12; final close 730.20 (+0.0110%). "
                 "999.72 + 0.0803 + 0.0110 = 999.81. Final close 730.20 is the 4:00 PM "
                 "regular-market price (16:00 bar close 730.20; 391 bars verified).")
mi["smi"] = smi

# aaii + fedWatch carried unchanged (already in mi via deepcopy)

patch = {"MARKET_INTERNALS": mi}
json.dump(patch, open("/tmp/patch.json", "w"))
print("patch written; SMI", smi["latest"], "change", smi["change"])
print("fearGreed", mi["fearGreed"]["value"], "| VIX", mi["vixTerm"]["spot"],
      "| above50", mi["breadth"]["above50"], "above200", mi["breadth"]["above200"],
      "| A/D", mi["breadth"]["advanceDeclineRatio"], mi["breadth"]["adDifference"],
      "| NH/NL NYSE", mi["breadth"]["newHighs"], "/", mi["breadth"]["newLows"])
