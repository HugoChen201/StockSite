#!/usr/bin/env python3
"""Close refresh patch for Thu Nov 19, 2026. Builds /tmp/patch.json from
verified Nov 19 close data; MARKET_INTERNALS replaced wholesale (carried
blocks copied from current data.json)."""
import json, copy

DATA = "/home/hatch/workspace/StockSite/data.json"
data = json.load(open(DATA))
mi = copy.deepcopy(data["MARKET_INTERNALS"])

# --- fearGreed: Nov 19 final, CNN live (official print) ---
# CNN page read live Nov 19 ~5:04 PM ET: 19 Extreme Fear, previous close 24
# Extreme Fear, last updated Nov 19 4:44:44 PM ET. 1 week ago 40 Fear.
# FLAG: CNN's previous-close field prints 24, but the Nov 18 close patch
# stored 25 from its own live CNN read (~5:05 PM ET Nov 18). CNN likely
# revised Nov 18's print down a point; stored previousClose follows the
# current page (24), with the discrepancy noted.
mi["fearGreed"] = {
    "value": 19,
    "label": "Extreme Fear",
    "previousClose": 24,
    "asof": "Nov 19, 2026 close (CNN live, last updated 4:44:44 PM ET)",
    "note": ("CNN official print read live Nov 19 ~5:04 PM ET: 19 Extreme Fear, "
             "previous close 24 Extreme Fear, 1 week ago 40 Fear. SPY fell 1.96% "
             "on the day (730.20 -> 715.87); VIX +15.80%. Note: CNN's previous-close "
             "field now prints 24, but the Nov 18 close patch stored 25 from its own "
             "live CNN read Nov 18 ~5:05 PM ET — CNN appears to have revised the "
             "Nov 18 print down a point."),
    "url": "https://www.cnn.com/markets/fear-and-greed",
}

# --- vixTerm: Yahoo daily closes, Nov 19 ---
# ^VIX 28.44 (prev 24.56, +3.88, +15.80%); ^VIX3M 27.03 (prev 24.29,
# +2.74, +11.28%). Ratio 27.03/28.44 = 0.95 -> still backwardation.
# Nov 16-18 values in the 5-day series match stored closes exactly.
mi["vixTerm"] = {
    "spot": 28.44,
    "spotPrev": 24.56,
    "spotChange": 3.88,
    "spotChangePct": 15.80,
    "threeMonth": 27.03,
    "threeMonthPrev": 24.29,
    "threeMonthChangePct": 11.28,
    "ratio": 0.95,
    "state": "Backwardation (stress)",
    "asof": "Nov 19, 2026 close",
    "note": ("^VIX3M 3-month VIX. 27.03/28.44 = 0.95. Backwardation: 3M still below "
             "spot, and the inversion widened as VIX spiked 15.80% on Nov 19 "
             "(SPY -1.96%, 730.20 -> 715.87). Yahoo daily closes; Nov 16-18 values "
             "in the 5-day series match stored closes exactly."),
}

# --- putCall: Nov 18 finals (ycharts) ---
# Nov 19 finals due Nov 19 20:00 EST — not yet posted at ~5:05 PM ET read.
# Total page verified Nov 19: latest Nov 18 = 1.05 (matches stored).
mi["putCall"] = {
    "equity": 0.72,
    "equityAsOf": "Nov 18, 2026 (ycharts)",
    "equityUrl": "https://ycharts.com/indicators/cboe_equity_put_call_ratio",
    "index": 1.14,
    "indexAsOf": "Nov 18, 2026 (ycharts)",
    "indexUrl": "https://ycharts.com/indicators/cboe_index_put_call_ratio",
    "total": 1.05,
    "totalAsOf": "Nov 18, 2026 (ycharts)",
    "totalUrl": "https://ycharts.com/indicators/total_putcall_ratio",
    "asof": ("Nov 18, 2026 finals (ycharts, total page re-verified Nov 19 ~5:05 PM ET; "
             "latest row Nov 18 = 1.05, matches stored. Nov 19 finals due Nov 19 20:00 EST)"),
}

# --- breadth: Barchart live browser, Nov 19 close ---
# $S5FI 49.10 (-7.16 vs Nov 18 56.26); $S5TH 49.10 (-6.96 vs Nov 18 56.06).
# FLAG: both printed exactly 49.10 despite different prev closes/day ranges.
# $ADVN 210 / $DECN 1,620 -> net -1,410 (matches $ADDN); ratio 210/1,620 =
# 0.13 computed — $ADRN printed 0.12, and its previous-close field flipped
# from 0.88 (5:03 PM read, matching 856/971) to 1.00 (5:06 PM re-reads).
# Per convention, the computed ratio is stored and the print is flagged.
# Highs/lows from the highs-lows Summary tab (Last Updated 11/19 16:53 ET):
# Overall 21/655, NYSE 9/182, Nasdaq 12/434, Arca 0/39 — per spec, the
# summary tab is used, NOT the quote-symbol set.
# CONFLICTS (not used): $MAHN 10 vs summary NYSE 9; $MAHQ 11 vs summary
# Nasdaq 12; $MALN page text 185 vs screenshot 182 (summary NYSE lows 182).
mi["breadth"] = {
    "above200": 49.10,
    "above200AsOf": "Nov 19, 2026 close (barchart $S5TH, live browser; 49.10, -6.96 pts vs Nov 18 56.06. Flag: $S5TH and $S5FI both printed exactly 49.10 despite different previous closes and day ranges.)",
    "above200Prev": 56.06,
    "above200Url": "https://www.barchart.com/stocks/quotes/$S5TH",
    "above50": 49.10,
    "above50AsOf": "Nov 19, 2026 close (barchart $S5FI, live browser; 49.10, -7.16 pts vs Nov 18 56.26. Flag: $S5FI and $S5TH both printed exactly 49.10.)",
    "above50Prev": 56.26,
    "above50Url": "https://www.barchart.com/stocks/quotes/$S5FI",
    "adDifference": -1410.0,
    "adDifferenceUrl": "https://www.barchart.com/stocks/quotes/%24ADDN",
    "adRatioUrl": "https://www.barchart.com/stocks/quotes/%24ADRN",
    "advanceDeclineAsOf": ("Nov 19, 2026 close (barchart $ADVN/$DECN/$ADDN, live browser, "
        "16:43 ET; advancing 210, declining 1,620, net -1,410; ratio 0.13 computed "
        "from counts — Barchart's $ADRN prints 0.12 and its previous-close field "
        "flipped from 0.88 (5:03 PM read, matching 856/971) to 1.00 (5:06 PM "
        "re-reads, twice verified). Previous close: 856 adv / 971 dec, net -115.)"),
    "advanceDeclineRatio": 0.13,
    "highLowAsOf": ("Nov 19, 2026 (barchart highs-lows Summary tab, live browser, "
        "Last Updated 11/19/2026 16:53 ET; Overall 21/655, NYSE 9/182, Nasdaq "
        "12/434, Arca 0/39. Sums check: 9+12+0=21, 182+434+39=655. Conflicting "
        "views NOT used: quote symbols $MAHN 10 / $MAHQ 11 disagree with the "
        "summary page's NYSE 9 / Nasdaq 12; $MALN page text 185 vs screenshot 182.)"),
    "highLowUrl": "https://www.barchart.com/stocks/highs-lows/summary",
    "nasdaqHighs": 12,
    "nasdaqLows": 434,
    "newHighs": 9,
    "newLows": 182,
    "spHighs": None,
    "spLows": None,
}

# --- flows: Nov 18 session (ETF Action report posted Nov 19, T+1) ---
# "ARK and Large-Cap Blend Lead a Strong Equity Day", posted Nov 19, 2026.
# Total +$11.43B. SPY +$1.35B; QQQ -$1.15B.
# IWM exact 1-day flow NOT in the public report (no "IWM" match in the text)
# — carried Nov 16-session -$0.25B and flagged, per standing convention.
mi["flows"] = [
    {"ticker": "SPY", "value": 1.35, "label": "$1.35B inflow (Nov 18 session)"},
    {"ticker": "QQQ", "value": -1.15, "label": "$1.15B outflow (Nov 18 session)"},
    {"ticker": "IWM", "value": -0.25, "label": "$0.25B outflow (Nov 16 session — carried; Nov 18-session value not in public ETF Action report)"},
]
mi["flowsAsOf"] = ("Nov 18, 2026 session (ETF Action flow report posted Nov 19, T+1 basis; "
    "total +$11.43B day). SPY +$1.35B; QQQ -$1.15B. IWM exact Nov 18-session flow "
    "not shown in the public report (no 'IWM' match in the report text) — carried "
    "Nov 16-session -$0.25B and flagged.")
mi["flowsUrl"] = "https://www.etfaction.com/"
mi["flowsToolUrl"] = "https://www.etf.com/etfanalytics/etf-fund-flows-tool"

# --- smi: FINALIZED Nov 19 = 999.90 (+0.09) ---
smi = copy.deepcopy(mi["smi"])
smi["status"] = "Finalized"
smi["latest"] = 999.90
smi["change"] = 0.09
smi["asof"] = "Nov 19, 2026 close"
smi["series"] = smi["series"] + [{"date": "Nov 19", "value": 999.90}]
smi["note"] = ("Self-computed Don Hays-style (SPY proxy), never SentimenTrader. "
               "Nov 19: -first-30-min (-0.2073%) + last-hour (-0.1172%) = +0.09.")
smi["inputs"] = ("SPY open 738.07 (Yahoo 1m, 9:30 bar close); 10:00 bar close 736.54 "
                 "(-0.2073%); 15:00 bar close 716.71; final close 715.87 (-0.1172%). "
                 "999.81 + 0.2073 - 0.1172 = 999.90. Final close 715.87 is the 4:00 PM "
                 "regular-market price (16:00 bar close 715.87; 391 bars verified).")
mi["smi"] = smi

# aaii + fedWatch carried unchanged (already in mi via deepcopy)

patch = {"MARKET_INTERNALS": mi}
json.dump(patch, open("/tmp/patch.json", "w"))
print("patch written; SMI", smi["latest"], "change", smi["change"])
print("fearGreed", mi["fearGreed"]["value"], "| VIX", mi["vixTerm"]["spot"],
      "| above50", mi["breadth"]["above50"], "above200", mi["breadth"]["above200"],
      "| A/D", mi["breadth"]["advanceDeclineRatio"], mi["breadth"]["adDifference"],
      "| NH/NL NYSE", mi["breadth"]["newHighs"], "/", mi["breadth"]["newLows"])
