#!/usr/bin/env python3
"""Morning-refresh patch builder for StockSite data.json (Fri 2026-10-16).

Sources (goals/stock-watchlist-website/hidden_files/):
- finviz_2026-10-16.json: 122 results, 15 ranked (UNH 84 top, Q3 beat + guidance raise)
- internals_2026-10-16.json: everything carried/confirmed from Oct-15 close baseline
- history_2026-10-16.json: 75x Oct-15 bars (Yahoo chart JSON; Stooq JS-blocked), sector breadth Oct-15 closes
- iv_2026-10-16.json: IV 62/63 refreshed (optioncharts), BRK-B carried; expected moves plain numbers, 40 tickers
- earnings-analyst-macro_2026-10-16.json: earningsFull 40 (TSM dropped; STX/VRT session fixes),
  analystNew (BAC x7, ASML x2, NFLX, VRT), macroFull 9 (+midterms Nov 3)
- /tmp/fedwatch_2026-10-16.json: LIVE CME read Oct 16 06:20 CT (Oct28 82.8% hold / 17.2% hike)
SMI finalized Oct 15 (999.71) by close refresh — carried untouched.
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())

finviz = json.loads((HID / "finviz_2026-10-16.json").read_text())
hist = json.loads((HID / "history_2026-10-16.json").read_text())
ivd = json.loads((HID / "iv_2026-10-16.json").read_text())
eam = json.loads((HID / "earnings-analyst-macro_2026-10-16.json").read_text())

RUN_STAMP = "Oct 16, 2026 7:45 AM ET"

# ---------- SCREEN_SNAPSHOT ----------
pot = []
STD_KEYS = ["ticker", "company", "price", "day", "relativeVolume", "distanceHigh",
            "score", "components", "catalyst", "catalystSource", "liquidity",
            "optionExpiry", "optionVolume", "optionOI", "volOi", "optionsSource"]
for row in finviz["potential"]:
    r = {k: row.get(k) for k in STD_KEYS}
    for k, v in row.items():
        if k not in r:
            r[k] = v
    pot.append(r)
pot.sort(key=lambda x: -x["score"])
volumes = {p["ticker"]: p.get("optionVolume") for p in pot}
screen = {
    "updated": RUN_STAMP,
    "scanTime": "2026-10-16 ~07:31 AM ET (premarket)",
    "resultCount": finviz["resultCount"],
    "resultTime": "2026-10-16 ~07:31 AM ET (premarket)",
    "source": "https://finviz.com/screener?v=211&f=cap_midover,sh_opt_option,ta_change_u,ta_highlow52w_b10h,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3",
    "optionsAsOf": "Oct 16, 2026 (optioncharts.io)",
    "note": ("15 ranked from 122 results. Premarket screen: Finviz prints include Oct 16 "
             "premarket action, so 'up on the day' is the premarket print, not purely the "
             "Oct 15 session. SPCX did not appear — nothing excluded. RDNT (screen's top "
             "gainer, +7.50%) deliberately NOT ranked: the move rests on a 1-share premarket "
             "print vs an Oct 15 close near $70.41, and its front options are thin. UNH tops "
             "the list on its Oct 13 Q3 beat + FY26 guidance raise. Some optioncharts pages "
             "(UNH/GOOGL/NOW/COST/WMT) were dated Oct 15 — flagged in those entries' notes."),
    "potential": pot,
    "volumes": volumes,
}

# ---------- HISTORY ----------
history = data["HISTORY"]
appended = 0
for t, bar in hist["bars"].items():
    arr = history.setdefault(t, [])
    if arr and arr[-1]["d"] == bar["d"]:
        continue
    arr.append({"c": bar["c"], "d": bar["d"], "h": bar["h"], "l": bar["l"], "o": bar["o"]})
    appended += 1

# ---------- MARKET_INTERNALS ----------
mi = data["MARKET_INTERNALS"]
# FedWatch LIVE Oct 16 (schema contract: decision + outcomes[].label/.pct)
mi["fedWatch"] = json.loads(Path("/tmp/fedwatch_2026-10-16.json").read_text())
# fearGreed / vixTerm / breadth / flows / putCall / aaii / smi all carried:
# internals collector verified no newer values had posted by ~7:30 AM ET
# (CNN teapot, Yahoo 429, YCharts still at Oct-14 finals, ETF Action Oct-16
# report not yet posted, AAII confirmed still week-ending Oct 14).

# ---------- EARNINGS_DATES ----------
earn = [e for e in eam["earningsFull"] if e["date"] >= "2026-10-16"]
em = ivd["expectedMoves"]
for e in earn:
    pct = em.get(e["ticker"])
    if pct is not None:
        e["expected_move"] = pct
        e["move_as_of"] = "Oct 16, 2026"
        e["move_method"] = ivd.get("methods", {}).get(e["ticker"]) or "options-implied (optioncharts.io overview)"
        e["move_method_zh"] = "期权隐含预期波动（期权链概览）"
earn.sort(key=lambda x: x["date"])

# ---------- EXPECTED_MOVES ----------
expected = dict(data["EXPECTED_MOVES"])
for t, pct in em.items():
    if pct is not None:
        expected[t] = pct
expected.pop("TSM", None)  # reported Oct 15 BMO — no upcoming earnings

# ---------- IV_DATA / IV_SOURCE ----------
iv_data = dict(data["IV_DATA"])
for t, v in ivd["iv"].items():
    if isinstance(v, dict) and "iv30" in v:
        iv_data[t] = {"iv30": v["iv30"], "rank": v["rank"], "percentile": v["percentile"]}
    # else carried last-good (BRK-B object without iv30 key) — keep data.json entry
iv_source = ("Oct 16, 2026 · 62 of 63 refreshed from optioncharts.io (live overview pages); "
             "1 carried last-good (BRK-B)")

# ---------- ANALYST_REVISIONS ----------
analyst = data["ANALYST_REVISIONS"]
for t, items in eam["analystNew"].items():
    existing = analyst.get(t, [])
    seen = {(i.get("sortDate"), i.get("detail")) for i in existing}
    new_items = [i for i in items if (i.get("sortDate"), i.get("detail")) not in seen]
    merged = new_items + existing
    merged.sort(key=lambda x: x.get("sortDate", ""), reverse=True)
    analyst[t] = [i for i in merged if i.get("sortDate", "9999") >= "2026-09-16"] or merged[:7]

# ---------- MACRO ----------
macro = eam["macroFull"]

# ---------- ASOF / I18N ----------
asof = dict(data["ASOF"])
asof["sectorBreadth"] = "Oct 16, 2026 7:45 AM ET"
asof["macro"] = "Oct 16, 2026 ~7:45 AM ET"
asof["expectedMoves"] = "Oct 16, 2026 ~7:45 AM ET"
asof["internals"] = "Oct 16, 2026 7:45 AM ET"

n = len(pot)
i18n = json.loads(json.dumps(data["I18N_OVERRIDES"]))
i18n["en"]["tradesDesc"] = f"{n} ranked setups from the October 16 Finviz screen, with verified front-month options activity."
i18n["en"]["ivAsOf"] = ("Updated Oct 16, 2026 · optioncharts.io 30-day IV readings "
                        "(62 of 63 refreshed; 1 carried last-good: BRK-B); stale source pages are flagged in ticker detail")
i18n["en"]["calendarDesc"] = "Macro calendar refreshed Oct 16, 2026 ~7:45 AM ET"
i18n["en"]["sevenDayWindow"] = "Next 7 days: Oct 16 – Oct 22, 2026"
i18n["en"]["checked"] = "Checked Oct 16, 2026 ~7:45 AM ET"
i18n["zh"]["tradesDesc"] = "根据 10 月 16 日的 Finviz 筛选，列出15个已验证近月期权活跃度的排序机会。"
i18n["zh"]["ivAsOf"] = "更新于 10 月 16 日 · optioncharts.io 隐含波动率数据（63 个标的中 62 个已刷新，1 个沿用上次有效值：BRK-B）"
i18n["zh"]["calendarDesc"] = "宏观日历已于 2026年10月16日 ~7:45 AM ET 更新"
i18n["zh"]["sevenDayWindow"] = "未来7天：2026年10月16日 – 10月22日"
i18n["zh"]["checked"] = "检查于 2026年10月16日 ~7:45 AM ET"

patch = {
    "SCREEN_SNAPSHOT": screen,
    "HISTORY": history,
    "MARKET_INTERNALS": mi,
    "SECTOR_BREADTH": hist["sectorBreadth"],
    "EARNINGS_DATES": earn,
    "EXPECTED_MOVES": expected,
    "IV_DATA": iv_data,
    "IV_SOURCE": iv_source,
    "ANALYST_REVISIONS": analyst,
    "MACRO_EVENTS": macro,
    "ASOF": asof,
    "I18N_OVERRIDES": i18n,
}
out = Path("/tmp/patch.json")
out.write_text(json.dumps(patch))
print("patch keys:", list(patch.keys()))
print("HISTORY appended:", appended, "| earnings:", len(earn), "| macro:", len(macro),
      "| screen:", len(pot), "from", screen["resultCount"],
      "| fedWatch asof:", mi["fedWatch"].get("asof"))
