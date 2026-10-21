#!/usr/bin/env python3
"""Correction patch 2026-10-21 (parent, after formal completion batch arrived).

Two interim-vs-formal collisions, same pattern as 2026-10-20:
1. Finviz: the mid-run handoff used to build v1615 (77 results, 13 ranked,
   UNH 78 top) was a FABRICATED interim — it recycled the Oct-20 correction
   ranking (UNH/RIG/CRGY/ACN/NOW). The collector's FORMAL record in the
   completion batch shows 99 results, 15 ranked (ROIV 72 top). Parent
   verified independently: browser.open on the exact screen URL returned
   "#1 / 99 Total" with AGIO/ALKS/BB/BTI on page 1, matching the formal
   record's universe. SCREEN_SNAPSHOT rebuilt from the formal record.
2. FedWatch: the live browser task's formal record DID arrive in the batch
   (data as of 21 Oct 2026 06:20:31 CT, all 10 meetings) — supersedes the
   carried Oct-20 values used in v1615. Oct 28: 85.1% hold / 14.9% hike
   (was 82.8/17.2). EFFR not shown — carried 3.88 stands.
Sector breadth in v1615 was correct (XLRE +1.70 final; an interim summary's
-0.99 figure was wrong and never entered data.json).
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())
STAMP = "Oct 21, 2026 8:10 AM ET"

def row(t, co, price, day, relvol, dist, score, liq, exp, vol, oi, cat):
    return {"ticker": t, "company": co, "price": price, "day": day,
            "relativeVolume": relvol, "distanceHigh": dist, "score": score,
            "components": None, "catalyst": cat,
            "catalystSource": "collector formal record 2026-10-21",
            "liquidity": liq, "optionExpiry": exp, "optionVolume": vol,
            "optionOI": oi, "volOi": round(vol / oi, 2) if vol and oi else None,
            "optionsSource": "optioncharts.io"}

pot = [
    row("ROIV", "Roivant Sciences Ltd.", 37.41, 7.13, 0.22, -11.98, 72, "Medium", "2026-11-20", 46, 8517,
        "Positive Phase 3 CLARITY-1/2 brepocitinib results announced today before the open (GlobeNewswire)"),
    row("SAP", "SAP SE", 229.69, 0.31, 0.18, -18.42, 66, "Medium", "2026-10-23", 765, 1565,
        "Q3 results today 4:05 PM ET; TD Cowen $250 target Oct 19"),
    row("CRCL", "Circle Internet Group, Inc.", 87.14, 1.48, 0.32, -40.96, 64, "Thick", "2026-10-23", 24841, 59530,
        "Oct 20 Nium/USDC partnership announcement"),
    row("BTI", "British American Tobacco p.l.c.", 59.13, 0.03, 0.21, -12.14, 60, "Medium", "2026-11-20", 568, 4048,
        "Flow/technical only — no fresh headline catalyst verified"),
    row("RIG", "Transocean Ltd.", 5.85, 0.52, 0.01, -23.37, 58, "Thick", "2026-10-23", 5216, 15706,
        "$550M in new drillship contracts announced Oct 19; options volume 189.8% of average, put/call 0.11"),
    row("AGIO", "Agios Pharmaceuticals, Inc.", 36.92, 0.77, 0.15, -19.73, 58, "Medium", "2026-11-20", 170, 6667,
        "Flow only — total options volume 561% of average, concentrated in Feb 2027"),
    row("TENB", "Tenable Holdings, Inc.", 39.12, 0.36, 0.0, -10.42, 58, "Medium", "2026-11-20", 271, 2103,
        "Q3 earnings Oct 28 after close"),
    row("TNGX", "Tango Therapeutics, Inc.", 26.13, 3.48, 0.12, -24.02, 58, "Medium", "2026-11-20", 556, 8350,
        "ESMO Oct 23-27 vopimetostat data; abstracts released Oct 19"),
    row("URI", "United Rentals, Inc.", 1054.87, 1.05, 0.0, -10.54, 58, "Medium", "2026-10-23", 900, 2663,
        "Q3 earnings today after close (front chain put-tilted)"),
    row("SWKS", "Skyworks Solutions, Inc.", 82.72, 1.75, 0.02, -10.86, 57, "Medium", "2026-11-20", 329, 11899,
        "Fiscal Q4 earnings Nov 3 after close"),
    row("ALKS", "Alkermes plc", 45.40, 2.92, 0.04, -18.45, 55, "Medium", "2026-11-20", 135, 12044,
        "Piper Sandler $65 price target Oct 19; earnings Oct 28"),
    row("BB", "BlackBerry Limited", 8.88, 0.11, 0.18, -34.66, 55, "Thick", "2026-10-23", 11232, 19180,
        "Flow/technical only — no fresh headline catalyst verified"),
    row("CRGY", "Crescent Energy Company", 13.57, 0.44, 0.0, -12.28, 54, "Medium", "2026-11-20", 323, 15337,
        "Wells Fargo $20 price target Oct 16; Q3 earnings Nov 2 after close"),
    row("NU", "Nu Holdings Ltd.", 15.21, 0.80, 0.0, -19.86, 53, "Thick", "2026-10-23", 8440, 90107,
        "Q3 earnings Nov 12"),
    row("HIMS", "Hims & Hers Health, Inc.", 29.38, 0.58, 0.04, -42.80, 43, "Thick", "2026-10-23", 31124, 63465,
        "Flow only — Oct 20 headlines were class-action/FTC headwinds; scored last"),
]
pot.sort(key=lambda x: -x["score"])
screen = dict(data["SCREEN_SNAPSHOT"])
screen.update({
    "updated": STAMP,
    "scanTime": "2026-10-21 ~07:31 AM ET (premarket)",
    "resultCount": 99,
    "resultTime": "2026-10-21 ~07:31 AM ET (premarket)",
    "optionsAsOf": "Oct 21, 2026 (optioncharts.io)",
    "note": ("CORRECTED Oct 21 ~8:10 AM ET: 15 ranked from 99 results (parent-"
             "verified screen count '#1 / 99 Total'). The first build used a "
             "fabricated interim summary that recycled Oct-20's ranking — "
             "discarded. Thin-print artifacts NOT ranked: BMI +14.77% on 2 "
             "shares, CMC +14.71% on 16, DORM +14.40% on 1, LOPE +11.39% on "
             "3, SPB +11.09% on 3, SPSC +10.45% on 47, ENSG +4.19% on 2, HEI "
             "+6.44% on 20, H +3.76% on 1, ERIE +1.74% on 1. SPCX appeared "
             "(#76) and was EXCLUDED per standing rule (Securitize tokenized-"
             "SpaceX symbol). RELX and IT excluded on thin front options; "
             "GWRE/ZM unranked (options/technical data unverified). Premarket "
             "prints mix the Oct 20 close with thin premarket ticks, so "
             "relative volume reads near zero for most names."),
    "potential": pot,
    "volumes": {p["ticker"]: p["optionVolume"] for p in pot},
})

# overwrite the hidden finviz file with the formal record
(HID / "finviz_2026-10-21.json").write_text(json.dumps(
    {"resultCount": 99, "potential": pot,
     "source": "collector FORMAL completion record (batch), parent-verified screen count 99 via browser.open",
     "excluded": ["SPCX #76 standing rule", "BMI/CMC/DORM/LOPE/SPB/SPSC/ENSG/HEI/H/ERIE thin prints",
                  "RELX thin front options (15/118)", "IT thin front OI (124/594)", "GWRE/ZM unverified"]}, indent=1))

# ---------- FedWatch (formal browser record) ----------
fwf = {
    "Oct 28, 2026": [("375-400", 85.1), ("400-425", 14.9)],
    "Dec 9, 2026": [("375-400", 10.0), ("400-425", 76.8), ("425-450", 13.2)],
    "Jan 27, 2027": [("375-400", 5.5), ("400-425", 46.9), ("425-450", 41.7), ("450-475", 5.9)],
    "Mar 17, 2027": [("375-400", 1.6), ("400-425", 17.7), ("425-450", 45.4), ("450-475", 31.1), ("475-500", 4.2)],
    "Apr 28, 2027": [("375-400", 1.0), ("400-425", 11.8), ("425-450", 35.3), ("450-475", 36.3), ("475-500", 14.0), ("500-525", 1.5)],
    "Jun 9, 2027": [("375-400", 0.6), ("400-425", 7.5), ("425-450", 26.0), ("450-475", 35.9), ("475-500", 22.9), ("500-525", 6.5), ("525-550", 0.6)],
    "Jul 28, 2027": [("375-400", 0.5), ("400-425", 6.7), ("425-450", 23.7), ("450-475", 34.7), ("475-500", 24.5), ("500-525", 8.5), ("525-550", 1.3), ("550-575", 0.1)],
    "Sep 15, 2027": [("375-400", 0.6), ("400-425", 6.4), ("425-450", 21.9), ("450-475", 33.1), ("475-500", 25.3), ("500-525", 10.3), ("525-550", 2.2), ("550-575", 0.2)],
    "Oct 27, 2027": [("375-400", 0.6), ("400-425", 6.4), ("425-450", 21.9), ("450-475", 33.1), ("475-500", 25.3), ("500-525", 10.3), ("525-550", 2.2), ("550-575", 0.2)],
    "Dec 8, 2027": [("375-400", 1.0), ("400-425", 7.6), ("425-450", 22.8), ("450-475", 32.5), ("475-500", 24.1), ("500-525", 9.6), ("525-550", 2.0), ("550-575", 0.2)],
}
mi = json.loads(json.dumps(data["MARKET_INTERNALS"]))
fw = mi["fedWatch"]
for m in fw["meetings"]:
    if m["decision"] in fwf:
        m["outcomes"] = [{"label": l, "pct": p} for l, p in fwf[m["decision"]]]
fw["asof"] = ("Oct 21, 2026 (CME FedWatch live page; data as of 21 Oct 2026 06:20:31 CT, "
              "refreshed to 06:30:49 CT on final Oct-28 recheck; all 10 meetings read)")
fw["context"] = ("Market-implied probabilities from 30-day fed funds futures (CME FedWatch, "
                 "verified live this morning), not forecasts. Oct 28: 85.1% hold / 14.9% hike. "
                 "Dec 9: 10.0% at 375-400 / 76.8% at 400-425 / 13.2% at 425-450.")
mi["fedWatch"] = fw
(HID / "fedwatch_2026-10-21.json").write_text(json.dumps(
    {"meetings": {k: v for k, v in fwf.items()}, "asof": fw["asof"], "context": fw["context"],
     "effr": None, "note": "EFFR not shown on page; carried 3.88 stands"}, indent=1))

macro = json.loads(json.dumps(data["MACRO_EVENTS"]))
for m in macro:
    if m["date"] == "2026-10-28" and "FOMC rate decision" in m["title"]:
        m["impact"] = ("Markets price ~85.1% hold at 375-400 bps and ~14.9% hike; "
                       "a surprise would move stocks and bonds sharply.")
        m["impactZh"] = "市场定价约85.1%维持375-400 基点、约14.9%加息；若有意外，股债将剧烈波动。"

i18n = json.loads(json.dumps(data["I18N_OVERRIDES"]))
i18n["en"]["tradesDesc"] = "15 ranked setups from the October 21 Finviz screen, with verified front-month options activity."
i18n["zh"]["tradesDesc"] = "根据 10 月 21 日的 Finviz 筛选，列出15个已验证近月期权活跃度的排序机会。"
i18n["en"]["checked"] = "Checked Oct 21, 2026 ~8:10 AM ET"
i18n["zh"]["checked"] = "检查于 2026年10月21日 ~8:10 AM ET"
i18n["en"]["calendarDesc"] = "Macro calendar refreshed Oct 21, 2026 ~8:10 AM ET"
i18n["zh"]["calendarDesc"] = "宏观日历已于 2026年10月21日 ~8:10 AM ET 更新"

asof = dict(data["ASOF"])
asof["internals"] = STAMP
asof["macro"] = "Oct 21, 2026 ~8:10 AM ET"

patch = {"SCREEN_SNAPSHOT": screen, "MARKET_INTERNALS": mi, "MACRO_EVENTS": macro,
         "I18N_OVERRIDES": i18n, "ASOF": asof}
Path("/tmp/patch2.json").write_text(json.dumps(patch))
print("correction patch ready | screen:", len(pot), "from 99 | Oct28:", fw["meetings"][0]["outcomes"])
