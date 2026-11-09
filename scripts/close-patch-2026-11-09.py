#!/usr/bin/env python3
"""Close refresh patch for Nov 9, 2026. Sources: Yahoo daily (VIX, VIX3M, SPY),
Yahoo SPY 1m bars (391 bars), Barchart breadth (live browser), whit3rabbit
fear-greed-data CSV mirror (old fear-and-greed repo deleted; Nov 9 not yet posted,
due 23:00 UTC), YCharts P/C (Nov 9 finals due 8 PM ET; Nov 6 finals carried),
ETF Action flows (Nov 6 session, posted Nov 9)."""
import json

data = json.load(open("/home/hatch/workspace/StockSite/data.json"))
mi = data["MARKET_INTERNALS"]

mi["fearGreed"] = {
    "value": 22,
    "label": "Extreme Fear",
    "previousClose": 19.99,
    "asof": "Nov 6, 2026 close (whit3rabbit fear-greed-data CSV mirror; Nov 9 value not yet posted as of ~5:10 PM ET, due 23:00 UTC)",
    "note": "CNN Fear & Greed Nov 6 reads 22.08 (Extreme Fear), Nov 5 = 19.99. Old mirror repo whit3rabbit/fear-and-greed is deleted (404); surviving mirror is whit3rabbit/fear-greed-data, fear-greed.csv, values match stored. Nov 9 value not yet in the mirror; carried last-good.",
    "url": "https://www.cnn.com/markets/fear-and-greed",
}

mi["vixTerm"] = {
    "spot": 19.92,
    "spotPrev": 25.64,
    "spotChange": -5.72,
    "spotChangePct": -22.31,
    "threeMonth": 20.85,
    "threeMonthPrev": 24.60,
    "threeMonthChangePct": -15.24,
    "ratio": 1.05,
    "state": "Contango (calm)",
    "asof": "Nov 09, 2026 close",
    "note": "^VIX3M 3-month VIX. 20.85/19.92 = 1.05. Contango (calm): 3M above spot. VIX fell 22.31% on Nov 9 as SPY rose 2.37% (735.29 -> 752.69). Yahoo daily closes.",
}

mi["putCall"] = {
    "equity": 0.59,
    "equityAsOf": "Nov 6, 2026 (ycharts)",
    "equityUrl": "https://ycharts.com/indicators/cboe_equity_put_call_ratio",
    "index": 1.26,
    "indexAsOf": "Nov 6, 2026 (ycharts)",
    "indexUrl": "https://ycharts.com/indicators/cboe_index_put_call_ratio",
    "total": 0.74,
    "totalAsOf": "Sep 21, 2026; Nov 6 total not published on ycharts indicator pages",
    "asof": "Nov 9 finals not yet posted at ~5:10 PM ET (ycharts, due 8:00 PM ET); values shown are Nov 6 finals",
}

# --- BREADTH: Barchart live browser, Nov 9 close ---
mi["breadth"] = {
    "advanceDeclineRatio": 4.50,
    "adDifference": 1167.0,
    "advanceDeclineAsOf": "Nov 9, 2026 close (barchart $ADRN / $ADDN, live browser; 16:40 ET; $ADRN prev shown 1.00 vs stored Nov 6 close 0.84 and $ADDN prev -149.00 vs stored -150 — Barchart glitches, persisted after reload; values 4.50 / 1,167.00 consistent either way: 0.84+3.66 = 1.00+3.50 = 4.50)",
    "above50": 69.52,
    "above50Prev": 61.55,
    "above50AsOf": "Nov 9, 2026 close (barchart $S5FI, live browser; 16:37 ET; prev 61.55 matches stored Nov 6 close)",
    "above200": 63.14,
    "above200Prev": 55.97,
    "above200AsOf": "Nov 9, 2026 close (barchart $S5TH, live browser; 16:37 ET; prev 55.97 matches stored Nov 6 close)",
    "newHighs": 41,
    "newLows": 45,
    "nasdaqHighs": 80,
    "nasdaqLows": 148,
    "spHighs": None,
    "spLows": None,
    "highLowAsOf": "Nov 9, 2026 (barchart highs-lows summary, live browser, Last Updated 11/09/2026 16:59 ET; Overall 124/202, NYSE 41/45, Nasdaq 80/148)",
    "above50Url": "https://www.barchart.com/stocks/quotes/$S5FI",
    "above200Url": "https://www.barchart.com/stocks/quotes/$S5TH",
    "adRatioUrl": "https://www.barchart.com/stocks/quotes/%24ADRN",
    "adDifferenceUrl": "https://www.barchart.com/stocks/quotes/%24ADDN",
    "highLowUrl": "https://www.barchart.com/stocks/highs-lows/summary",
}

mi["flows"] = [
    {"ticker": "SPY", "value": -2.31, "label": "$2.31B outflow (Nov 6 session)"},
    {"ticker": "QQQ", "value": 2.79, "label": "$2.79B inflow (Nov 6 session)"},
    {"ticker": "IWM", "value": 0.54, "label": "$0.54B inflow (Nov 6 session)"},
]
mi["flowsAsOf"] = ("ETF Action ETF Flow Report posted Nov 9, 2026 (data as of Nov 6, 2026 session, T+1; "
                    "Nov 9-session report not yet posted). Total net ETF flows +$8.59B. SPY -$2.31B; "
                    "QQQ +$2.79B; IWM +$0.54B.")

# --- SMI: SPY 1m bars, Yahoo. open 741.95; 10:00 close 747.45; 15:00 close 754.13; final 752.69 ---
open_px, ten_px, three_px, final_px = 741.95, 747.45, 754.13, 752.69
first30 = (ten_px - open_px) / open_px * 100
last_hr = (final_px - three_px) / three_px * 100
prev_smi = mi["smi"]["series"][-1]["value"]  # 999.58 (Nov 06)
smi_val = round(prev_smi - first30 + last_hr, 2)
smi_change = round(smi_val - prev_smi, 2)

smi = mi["smi"]
smi["status"] = "Finalized"
smi["latest"] = smi_val
smi["change"] = smi_change
smi["asof"] = "Nov 9, 2026 close"
smi["inputs"] = (f"SPY open {open_px} (Yahoo 1m); 10:00 bar close {ten_px} ({first30:+.4f}%); "
                 f"15:00 bar close {three_px}; final close {final_px} ({last_hr:+.4f}%). "
                 f"{prev_smi} - {first30:+.4f} + {last_hr:+.4f} = {smi_val}. Final close {final_px} is the 4:00 PM "
                 "regular-market price (16:00 bar closed 752.69; after-hours NOT used).")
smi["note"] = (f"Self-computed Don Hays-style (SPY proxy), never SentimenTrader. Nov 9: "
               f"-first-30-min ({first30:+.4f}%) + last-hour ({last_hr:+.4f}%) = {smi_change:+.2f}.")
smi["intraday"] = smi_val
smi["intradayAsOf"] = "Nov 09, 2026 4:00 PM ET (final)"
smi["intradayInputs"] = smi["inputs"]
series = smi["series"]
if not (series and series[-1]["date"] == "Nov 09"):
    series.append({"date": "Nov 09", "value": smi_val})

asof = dict(data.get("ASOF", {}))
asof["internals"] = "Nov 09, 2026 close"

patch = {"MARKET_INTERNALS": mi, "ASOF": asof}
with open("/tmp/patch.json", "w") as f:
    json.dump(patch, f)
print(f"patch written; SMI Nov 9 = {smi_val} ({smi_change:+.2f}); VIX 19.92 (-22.31%), VIX3M 20.85, ratio 1.05 contango")
