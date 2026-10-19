#!/usr/bin/env python3
"""Morning-refresh patch builder for StockSite data.json (Mon 2026-10-19).

Sources (goals/stock-watchlist-website/hidden_files/):
- finviz_2026-10-19.json: 89 results, 15 ranked (CLF 88 top, Oct 19 premarket Q3 beat)
- internals_2026-10-19.json: F&G 18 confirmed via fallback CSV; VIX verified;
  P/C NEW Oct-16 finals eq 0.65 / idx 1.05; flows NEW Oct-18 report (Oct-16 session:
  SPY -$4.40B QQQ -$3.42B IWM -$2.47B); breadth/AAII carried Oct-16 verified
- history_2026-10-19.json: 75x Oct-16 bars (Yahoo chart JSON, no 429; SPY verified
  o773.24/c763.25), sector breadth Oct-16 final closes
- iv_2026-10-19.json: IV 61/63 refreshed (optioncharts), BRK-B + SNOW carried;
  expected moves 39 tickers
- earnings-analyst-macro_2026-10-19.json: earnings 40 (META corrected to Oct 21 AMC,
  BE to Oct 22 AMC), analystNew (NFLX x2, STX, GS — all Oct 16), macro 9
- /tmp/fedwatch_2026-10-19.json: LIVE CME read Oct 19 06:19 CT (Oct28 85.1% hold /
  14.9% hike, up from 82.8/17.2)
SMI finalized Oct 16 (1000.14) by close refresh — carried untouched.
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())

finviz = json.loads((HID / "finviz_2026-10-19.json").read_text())
hist = json.loads((HID / "history_2026-10-19.json").read_text())
ivd = json.loads((HID / "iv_2026-10-19.json").read_text())
eam = json.loads((HID / "earnings-analyst-macro_2026-10-19.json").read_text())
inv = json.loads((HID / "internals_2026-10-19.json").read_text())

RUN_STAMP = "Oct 19, 2026 7:45 AM ET"

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
    "scanTime": "2026-10-19 ~07:31 AM ET (premarket)",
    "resultCount": finviz["resultCount"],
    "resultTime": "2026-10-19 ~07:31 AM ET (premarket)",
    "source": "https://finviz.com/screener?v=211&f=cap_midover,sh_opt_option,ta_change_u,ta_highlow52w_b10h,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3",
    "optionsAsOf": "Oct 19, 2026 (optioncharts.io)",
    "note": ("15 ranked from 89 results. Premarket screen: Finviz prints include Oct 19 "
             "premarket action, so 'up on the day' is the premarket print, not purely the "
             "Oct 16 session. CLF tops the list on its Oct 19 premarket Q3 beat "
             "(EPS $0.28 vs $0.24 cons., rev $5.61B, Q4 EBITDA guided ~$715M). "
             "Thin-print artifacts deliberately NOT ranked: LPX (+13.49% on 3 shares), "
             "WDFC (+11.39% on 5), VMI (+8.49% on 1), IR (+8.01% on 17). Thin-options "
             "names excluded: AGYS (front-month 0 contracts / 41 OI), RELX (19 / 106). "
             "SPCX did not appear — nothing excluded."),
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
# FedWatch LIVE Oct 19 (schema contract: decision + outcomes[].label/.pct)
mi["fedWatch"] = json.loads(Path("/tmp/fedwatch_2026-10-19.json").read_text())
# Put/call NEW Oct-16 finals (YCharts)
pc = mi["putCall"]
pc["equity"] = inv["putCall"]["equity"]["value"]
pc["equityAsOf"] = "Oct 16, 2026 (ycharts; next release Oct 19 2026 20:00 EDT)"
pc["index"] = inv["putCall"]["index"]["value"]
pc["indexAsOf"] = "Oct 16, 2026 (ycharts; next release Oct 19 2026 20:00 EDT)"
pc["totalAsOf"] = "Sep 21, 2026; Oct 16 total unavailable"
pc["asof"] = "Equity Oct 16, 2026 · Index Oct 16, 2026 (ycharts)"
mi["putCall"] = pc
# ETF flows NEW (Oct-18 report, Oct-16 session)
mi["flows"] = inv["flows"]["flows"]
mi["flowsAsOf"] = inv["flowsAsOf"]
# fearGreed (18 confirmed via fallback CSV), vixTerm (verified identical),
# breadth (Oct-16 verified), aaii (verified unchanged), smi (final) all carried.

# ---------- EARNINGS_DATES ----------
earn = [e for e in eam["earningsFull"] if e["date"] >= "2026-10-19"]
em = ivd["expectedMoves"]
for e in earn:
    pct = em.get(e["ticker"])
    if pct is not None:
        e["expected_move"] = pct
        e["move_as_of"] = "Oct 19, 2026"
        e["move_method"] = ivd.get("methods", {}).get(e["ticker"]) or "options-implied (optioncharts.io overview)"
        e["move_method_zh"] = "期权隐含预期波动（期权链概览）"
earn.sort(key=lambda x: x["date"])

# ---------- EXPECTED_MOVES ----------
expected = dict(data["EXPECTED_MOVES"])
for t, pct in em.items():
    if pct is not None:
        expected[t] = pct

# ---------- IV_DATA / IV_SOURCE ----------
iv_data = dict(data["IV_DATA"])
for t, v in ivd["iv"].items():
    if isinstance(v, dict) and "iv30" in v:
        iv_data[t] = {"iv30": v["iv30"], "rank": v["rank"], "percentile": v["percentile"]}
    # else carried last-good — keep data.json entry
iv_source = ("Oct 19, 2026 · 61 of 63 refreshed from optioncharts.io (live overview pages); "
             "2 carried last-good (BRK-B, SNOW)")

# ---------- ANALYST_REVISIONS ----------
analyst = data["ANALYST_REVISIONS"]
for t, items in eam["analystNew"].items():
    existing = analyst.get(t, [])
    seen = {(i.get("sortDate"), i.get("detail")) for i in existing}
    new_items = [i for i in items if (i.get("sortDate"), i.get("detail")) not in seen]
    merged = new_items + existing
    merged.sort(key=lambda x: x.get("sortDate", ""), reverse=True)
    analyst[t] = [i for i in merged if i.get("sortDate", "9999") >= "2026-09-19"] or merged[:7]

# ---------- MACRO ----------
macro = eam["macroFull"]
for m in macro:
    if m["date"] == "2026-10-28" and "FOMC rate decision" in m["title"]:
        m["impact"] = ("Markets price ~85.1% hold at 375-400 bps and ~14.9% hike; "
                       "a surprise would move stocks and bonds sharply.")
        m["impactZh"] = "市场定价约85.1%维持375-400 基点、约14.9%加息；若有意外，股债将剧烈波动。"

# ---------- ASOF / I18N ----------
asof = dict(data["ASOF"])
asof["sectorBreadth"] = "Oct 19, 2026 7:45 AM ET"
asof["macro"] = "Oct 19, 2026 ~7:45 AM ET"
asof["expectedMoves"] = "Oct 19, 2026 ~7:45 AM ET"
asof["internals"] = "Oct 19, 2026 7:45 AM ET"

n = len(pot)
i18n = json.loads(json.dumps(data["I18N_OVERRIDES"]))
i18n["en"]["tradesDesc"] = f"{n} ranked setups from the October 19 Finviz screen, with verified front-month options activity."
i18n["en"]["ivAsOf"] = ("Updated Oct 19, 2026 · optioncharts.io 30-day IV readings "
                        "(61 of 63 refreshed; 2 carried last-good: BRK-B, SNOW); stale source pages are flagged in ticker detail")
i18n["en"]["calendarDesc"] = "Macro calendar refreshed Oct 19, 2026 ~7:45 AM ET"
i18n["en"]["sevenDayWindow"] = "Next 7 days: Oct 19 – Oct 25, 2026"
i18n["en"]["checked"] = "Checked Oct 19, 2026 ~7:45 AM ET"
i18n["zh"]["tradesDesc"] = "根据 10 月 19 日的 Finviz 筛选，列出15个已验证近月期权活跃度的排序机会。"
i18n["zh"]["ivAsOf"] = "更新于 10 月 19 日 · optioncharts.io 隐含波动率数据（63 个标的中 61 个已刷新，2 个沿用上次有效值：BRK-B、SNOW）"
i18n["zh"]["calendarDesc"] = "宏观日历已于 2026年10月19日 ~7:45 AM ET 更新"
i18n["zh"]["sevenDayWindow"] = "未来7天：2026年10月19日 – 10月25日"
i18n["zh"]["checked"] = "检查于 2026年10月19日 ~7:45 AM ET"

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
