#!/usr/bin/env python3
"""CORRECTION patch for StockSite morning refresh 2026-10-20.

Two formal completion records superseded interim data used in v1529:
1. Finviz collector's formal record: the screen actually returned 77 results
   (Overview v=111), ranking was never completed, SPCX never appeared, and
   the interim summary/paste used for v1529's SCREEN_SNAPSHOT (102 results,
   DHT-led ranking) was NOT the collector's data. This patch rebuilds
   SCREEN_SNAPSHOT from the formal record: 77 results, options liquidity
   checks for 22 tickers (optioncharts, Oct 20), catalysts verified by the
   parent via headline search Oct 20 (RIG, UNH, ACN, NOW, PBF, CRGY) or
   explicitly marked flow-only / unverified.
2. FedWatch browser task's formal record (data as of 20 Oct 2026 06:25:49 CT):
   all 10 meetings read; Oct28 82.8/17.2, Dec9 8.3/76.2/15.4, etc. EFFR was
   NOT shown in that view -> effr restored to carried 3.88 (Oct 9).
Macro FOMC impact updated to 82.8% hold.
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())

RUN_STAMP = "Oct 20, 2026 8:45 AM ET"

# Real screen results (formal record): ticker -> (price, changePct, relVol, distanceHigh, company)
RES = {
    "UNH": (409.3, 0.59, 0.09, -11.33, "UnitedHealth Group Inc"),
    "PBF": (83.17, 2.35, 0.01, -10.11, "PBF Energy Inc"),
    "RIG": (5.99, 1.7, 0.05, -21.8, "Transocean Ltd"),
    "CRGY": (13.9, 1.46, 0.04, -10.47, "Crescent Energy Co"),
    "NVS": (152.23, 1.35, 0.07, -10.69, "Novartis AG ADR"),
    "EL": (107.09, 1.24, 0.0, -11.96, "Estee Lauder Cos. Inc"),
    "ACN": (238.1, 0.49, 0.06, -17.55, "Accenture plc"),
    "NOW": (147.44, 1.43, 0.13, -23.55, "ServiceNow Inc"),
    "TENB": (39.06, 0.33, 0.01, -10.56, "Tenable Holdings Inc"),
    "AR": (38.85, 0.06, 0.01, -15.07, "Antero Resources Corp"),
    "MTDR": (58.4, 1.78, 0.03, -12.63, "Matador Resources Co"),
    "DG": (135.88, 1.96, 0.0, -14.13, "Dollar General Corp"),
    "ALL": (248.18, 0.54, 0.0, -10.48, "Allstate Corp"),
}
# ticker -> (score, components, catalyst, catalystSource, liquidity, expiry, optVol, optOI)
DET = {
    "UNH": (78, {"relativeVolume": 9, "distanceHigh": 13, "optionLiquidity": 20, "catalyst": 19, "trend": 17},
            "Oct 13 Q3 beat (adj EPS $4.69 vs $4.14 est.) and FY26 guidance raised to at least $20.50 adj EPS; follow-through buying since",
            "zacks.com Oct 19 (search-verified)", "Thick", "2026-10-23", 23596, 31419),
    "PBF": (72, {"relativeVolume": 8, "distanceHigh": 14, "optionLiquidity": 17, "catalyst": 15, "trend": 18},
            "Q3 earnings Oct 29; refining margins surged on global capacity outages, stock up ~230% YTD with target hikes; front chain call-tilted (P/C ~0.17)",
            "prnewswire Sep 28 / marketbeat (search-verified)", "Thick", "2026-11-20", 3251, 10657),
    "RIG": (71, {"relativeVolume": 16, "distanceHigh": 4, "optionLiquidity": 19, "catalyst": 20, "trend": 12},
            "Oct 19: $550M in new ultra-deepwater drillship contracts (GlobeNewswire); Valaris merger cleared Brazil antitrust; options volume 242% of average, call-heavy (P/C 0.06)",
            "globenewswire Oct 19 (search-verified)", "Thick", "2026-10-23", 13175, 8562),
    "CRGY": (69, {"relativeVolume": 9, "distanceHigh": 14, "optionLiquidity": 17, "catalyst": 13, "trend": 16},
            "Q3 results scheduled Nov 2 AMC (announced Oct 15); heavy call buying — options volume 191% of average, P/C 0.07",
            "businesswire Oct 15 (search-verified)", "Thick", "2026-11-20", 1474, 14773),
    "NVS": (66, {"relativeVolume": 9, "distanceHigh": 14, "optionLiquidity": 17, "catalyst": 10, "trend": 16},
            "No fresh headline verified this morning; front chain call-tilted (P/C 0.21) with options volume 137% of average",
            "optioncharts.io flow, Oct 20 (no headline verified)", "Thick", "2026-11-20", 1758, 18105),
    "EL": (64, {"relativeVolume": 12, "distanceHigh": 12, "optionLiquidity": 12, "catalyst": 14, "trend": 14},
            "Large Apr 2027 call sweep (32,522 calls) drove total options volume to 975% of average; front Oct 23 chain is put-heavy (P/C 5.22) — mixed signal, sized accordingly",
            "optioncharts.io flow, Oct 20 (search-verified via collector check)", "Medium", "2026-10-23", 1263, 2413),
    "ACN": (62, {"relativeVolume": 8, "distanceHigh": 7, "optionLiquidity": 18, "catalyst": 16, "trend": 13},
            "Oct 19: Gemini launchpads with Google Public Sector for federal AI agents; FT reported a review of selling the Greater China business (~$1.5B); closed +3.16% Monday",
            "stocktwits/thestreet Oct 19 (search-verified)", "Thick", "2026-10-23", 5332, 10961),
    "NOW": (61, {"relativeVolume": 10, "distanceHigh": 3, "optionLiquidity": 20, "catalyst": 16, "trend": 12},
            "Piper Sandler raised PT to $175 on Oct 19; Q3 results due Oct 28 AMC; deepest front-month options liquidity in the screen",
            "ad-hoc-news Oct 19 (search-verified)", "Thick", "2026-10-23", 29974, 57747),
    "TENB": (59, {"relativeVolume": 7, "distanceHigh": 14, "optionLiquidity": 11, "catalyst": 13, "trend": 14},
            "Q3 earnings due ~Oct 28 with IV elevated at 86.8% (rank 32) into the print; call-tilted OI",
            "optioncharts.io, Oct 20 (collector check)", "Medium", "2026-11-20", 520, 1756),
    "AR": (55, {"relativeVolume": 10, "distanceHigh": 9, "optionLiquidity": 11, "catalyst": 11, "trend": 14},
            "Options volume 154% of average, call-tilted (P/C 0.40); gas-levered E&P with Q3 due early November",
            "optioncharts.io flow, Oct 20 (collector check)", "Medium", "2026-10-23", 310, 1868),
    "MTDR": (54, {"relativeVolume": 7, "distanceHigh": 11, "optionLiquidity": 11, "catalyst": 10, "trend": 15},
            "Heavily call-tilted open interest (OI P/C 0.13); energy momentum with the sector bid; no fresh headline verified this morning",
            "optioncharts.io flow, Oct 20 (no headline verified)", "Medium", "2026-11-20", 329, 10778),
    "DG": (52, {"relativeVolume": 6, "distanceHigh": 10, "optionLiquidity": 12, "catalyst": 9, "trend": 15},
            "No fresh headline verified this morning; +1.96% premarket momentum in a defensive name above all SMAs",
            "no headline verified (Oct 20 check)", "Medium", "2026-10-23", 610, 3375),
    "ALL": (52, {"relativeVolume": 5, "distanceHigh": 14, "optionLiquidity": 11, "catalyst": 8, "trend": 14},
            "No fresh headline verified this morning; trend + front-month OI base setup only — lowest catalyst conviction in the list",
            "no headline verified (Oct 20 check)", "Medium", "2026-11-20", 587, 7310),
}
pot = []
for t, (score, comp, cat, catsrc, liq, exp, ov, oi) in DET.items():
    price, chg, rv, dh, comp_name = RES[t]
    pot.append({
        "ticker": t, "company": comp_name, "price": price,
        "day": f"{chg:+.2f}%", "relativeVolume": rv, "distanceHigh": dh,
        "score": score, "components": comp, "catalyst": cat, "catalystSource": catsrc,
        "liquidity": liq, "optionExpiry": exp, "optionVolume": ov, "optionOI": oi,
        "volOi": round(ov / oi, 2) if oi else None,
        "optionsSource": "optioncharts.io live 2026-10-20",
    })
pot.sort(key=lambda x: -x["score"])
volumes = {p["ticker"]: p.get("optionVolume") for p in pot}
screen = {
    "updated": RUN_STAMP,
    "scanTime": "2026-10-20 ~07:33 AM ET (premarket)",
    "resultCount": 77,
    "resultTime": "2026-10-20 ~07:33 AM ET (premarket)",
    "source": "https://finviz.com/screener?v=211&f=cap_midover,sh_opt_option,ta_change_u,ta_highlow52w_b10h,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3",
    "optionsAsOf": "Oct 20, 2026 (optioncharts.io)",
    "note": ("CORRECTED Oct 20 (supersedes the v1529 screen section, which was built on an "
             "unverified collector summary that the collector's formal record disowned): the "
             "verified screen returned 77 results (Overview view; the count churned 56-78 "
             "across views as premarket prints flickered). SPCX did NOT appear — nothing "
             "excluded on that ground. 13 ranked from the 22 names with verified front-month "
             "option checks. Thin chains excluded: APPF (57 total contracts), HCM (185 total "
             "OI), OTEX (79 total contracts); MCO ranked out on thin front volume (169) despite "
             "+2.23% day. Thin-print artifacts excluded: CTOS (+4.28% on 5 shares), MQ (2), "
             "KALU (33), ICLR (5). M carries a caution: total volume 622% of average was driven "
             "by a large Jan-27 put print (bearish/hedge) — not ranked. Catalysts for RIG, UNH, "
             "ACN, NOW, PBF, CRGY were headline-verified Oct 20; NVS/MTDR/DG/ALL are flow/trend "
             "setups and say so in their notes."),
    "potential": pot,
    "volumes": volumes,
}

# ---------- FedWatch formal record ----------
mi = data["MARKET_INTERNALS"]
fw = json.loads(json.dumps(mi["fedWatch"]))
formal = [
    ("Oct 28, 2026", [("375-400", 82.8), ("400-425", 17.2)]),
    ("Dec 9, 2026", [("375-400", 8.3), ("400-425", 76.2), ("425-450", 15.4)]),
    ("Jan 27, 2027", [("375-400", 4.4), ("400-425", 44.3), ("425-450", 44.0), ("450-475", 7.3)]),
    ("Mar 17, 2027", [("375-400", 1.3), ("400-425", 16.1), ("425-450", 44.2), ("450-475", 33.2), ("475-500", 5.1)]),
    ("Apr 28, 2027", [("375-400", 0.8), ("400-425", 10.7), ("425-450", 34.0), ("450-475", 37.2), ("475-500", 15.4), ("500-525", 1.9)]),
    ("Jun 9, 2027", [("375-400", 0.5), ("400-425", 7.1), ("425-450", 25.4), ("450-475", 36.0), ("475-500", 23.4), ("500-525", 6.9), ("525-550", 0.7)]),
    ("Jul 28, 2027", [("375-400", 0.5), ("400-425", 6.4), ("425-450", 23.4), ("450-475", 34.9), ("475-500", 24.8), ("500-525", 8.7), ("525-550", 1.4), ("550-575", 0.1)]),
    ("Sep 15, 2027", [("375-400", 0.4), ("400-425", 5.8), ("425-450", 21.6), ("450-475", 33.7), ("475-500", 25.8), ("500-525", 10.3), ("525-550", 2.1), ("550-575", 0.2)]),
    ("Oct 27, 2027", [("375-400", 0.5), ("400-425", 5.9), ("425-450", 21.8), ("450-475", 33.6), ("475-500", 25.7), ("500-525", 10.2), ("525-550", 2.1), ("550-575", 0.2)]),
    ("Dec 8, 2027", [("375-400", 0.9), ("400-425", 7.2), ("425-450", 22.7), ("450-475", 33.0), ("475-500", 24.4), ("500-525", 9.6), ("525-550", 1.9), ("550-575", 0.2)]),
]
fw["meetings"] = [{"decision": d, "outcomes": [{"label": l, "pct": p} for l, p in outs]} for d, outs in formal]
fw["asof"] = "Oct 20, 2026 (CME FedWatch live page; data as of 20 Oct 2026 06:25:49 CT)"
fw["context"] = ("Market-implied probabilities from 30-day fed funds futures (CME FedWatch, "
                 "verified live this morning), not forecasts. Oct 28: 82.8% hold / 17.2% hike. "
                 "Dec 9: 8.3% at 375-400 / 76.2% at 400-425 / 15.4% at 425-450.")
fw["effr"] = 3.88
fw["effrAsOf"] = "Oct 9, 2026 (carried last-good; EFFR not shown on the FedWatch page today)"
mi["fedWatch"] = fw

# ---------- Macro FOMC impact ----------
macro = data["MACRO_EVENTS"]
for m in macro:
    if m["date"] == "2026-10-28" and "FOMC rate decision" in m["title"]:
        m["impact"] = ("Markets price ~82.8% hold at 375-400 bps and ~17.2% hike; "
                       "a surprise would move stocks and bonds sharply.")
        m["impactZh"] = "市场定价约82.8%维持375-400 基点、约17.2%加息；若有意外，股债将剧烈波动。"

# ---------- ASOF / I18N ----------
asof = dict(data["ASOF"])
asof["internals"] = "Oct 20, 2026 8:45 AM ET"
asof["macro"] = "Oct 20, 2026 ~8:45 AM ET"
n = len(pot)
i18n = json.loads(json.dumps(data["I18N_OVERRIDES"]))
i18n["en"]["tradesDesc"] = f"{n} ranked setups from the October 20 Finviz screen, with verified front-month options activity."
i18n["zh"]["tradesDesc"] = "根据 10 月 20 日的 Finviz 筛选，列出13个已验证近月期权活跃度的排序机会。"
i18n["en"]["calendarDesc"] = "Macro calendar refreshed Oct 20, 2026 ~8:45 AM ET"
i18n["en"]["checked"] = "Checked Oct 20, 2026 ~8:45 AM ET"
i18n["zh"]["calendarDesc"] = "宏观日历已于 2026年10月20日 ~8:45 AM ET 更新"
i18n["zh"]["checked"] = "检查于 2026年10月20日 ~8:45 AM ET"

patch = {
    "SCREEN_SNAPSHOT": screen,
    "MARKET_INTERNALS": mi,
    "MACRO_EVENTS": macro,
    "ASOF": asof,
    "I18N_OVERRIDES": i18n,
}
Path("/tmp/patch2.json").write_text(json.dumps(patch))
print("correction patch:", len(pot), "ranked from 77 | fedWatch Oct28:", fw["meetings"][0]["outcomes"],
      "| Dec9:", fw["meetings"][1]["outcomes"])
