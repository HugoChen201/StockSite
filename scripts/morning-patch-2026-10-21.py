#!/usr/bin/env python3
"""Morning-refresh patch builder for StockSite data.json (Wed 2026-10-21).

Sources (hidden_files/):
- finviz_2026-10-21.json: 77 results, 13 ranked (UNH 78 top) — collector's file
  write failed; parent reconstructed the file verbatim from the collector's
  FORMAL completion record (interim Oct-20 DHT ranking was disowned the same
  way; formal records only).
- history_2026-10-21.json: 75x Oct-20 bars (Yahoo chart JSON; SPY verified
  o765.86/c769.05 vs SMI inputs); sector breadth = Oct-20 FINAL closes.
- iv_2026-10-21.json: IV 45/63 refreshed (optioncharts), 18 carried flagged
  stale (pages stale at Oct-19 copy, values re-verified exact matches);
  expected moves 39 earnings-expiry.
- earnings-analyst-macro_2026-10-21.json: earnings 41 (NFLX dropped post-
  earnings, NVDA Nov 17 added; COST Dec 17 claimed in collector summary but
  NOT in its file — file trusted, COST not added); analystNew NFLX x3
  (Bernstein PT $95->$80 post-earnings 10/21, KeyBanc Buy $85 10/21, Seaport
  $102->$90 10/19), MSFT x2 (BMO $515->$600 10/20, Bernstein $660->$662 10/19);
  macro 11 unchanged.
- internals_2026-10-21.json: everything carried/confirmed — P/C Oct-20 finals
  not visible on YCharts text fetch (lags to Oct 16), no new ETF Action
  report, AAII unchanged wk-end Oct 14, F&G 27 confirmed via fallback CSV
  Oct-20 row 27.2. MARKET_INTERNALS carried wholesale except fedWatch.
FedWatch: filled in below from the live browser task's formal record.
SMI finalized Oct 20 (999.80) by close refresh — carried untouched.
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())

finviz = json.loads((HID / "finviz_2026-10-21.json").read_text())
hist = json.loads((HID / "history_2026-10-21.json").read_text())
ivd = json.loads((HID / "iv_2026-10-21.json").read_text())
eam = json.loads((HID / "earnings-analyst-macro_2026-10-21.json").read_text())
fedwatch_fresh = json.loads((HID / "fedwatch_2026-10-21.json").read_text())

RUN_STAMP = "Oct 21, 2026 8:30 AM ET"

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
    "scanTime": "2026-10-21 ~07:31 AM ET (premarket)",
    "resultCount": finviz["resultCount"],
    "resultTime": "2026-10-21 ~07:31 AM ET (premarket)",
    "source": "https://finviz.com/screener?v=211&f=cap_midover,sh_opt_option,ta_change_u,ta_highlow52w_b10h,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3",
    "optionsAsOf": "Oct 21, 2026 (optioncharts.io)",
    "note": ("13 ranked from 77 results (Overview v=111 count converged at 77; "
             "22 tickers options-checked, front expiry Oct 23). Premarket "
             "screen: Finviz prints mix the Oct 20 close with thin premarket "
             "ticks. UNH tops the list on its Oct-13 Q3 beat + FY26 guidance "
             "raise. Thin-options names excluded: APPF (50 vol / 370 OI), HCM "
             "(134 / 269), OTEX (100 / 838), MCO (169 front vol). M excluded "
             "over a bearish Jan-27 put print (35,269 puts vs 150 calls). "
             "SPCX never appeared — no exclusion needed. Several ranked names "
             "(CB, CRGY, EL, SEIC, DG, ALL, CRWV) are flow/technical only with "
             "no fresh headline catalyst — flagged in their notes and scored "
             "down on catalyst."),
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
fw = json.loads(json.dumps(mi["fedWatch"]))
for m in fw["meetings"]:
    if m["decision"] in fedwatch_fresh["meetings"]:
        m["outcomes"] = [{"label": lbl, "pct": pct}
                          for lbl, pct in fedwatch_fresh["meetings"][m["decision"]]]
fw["asof"] = fedwatch_fresh["asof"]
fw["context"] = fedwatch_fresh["context"]
if fedwatch_fresh.get("effr") is not None:
    fw["effr"] = fedwatch_fresh["effr"]
    fw["effrAsOf"] = fedwatch_fresh["effrAsOf"]
mi["fedWatch"] = fw
# fearGreed / vixTerm / breadth / flows / aaii / smi / putCall: confirmed or
# carried from Oct-20 close verification (internals_2026-10-21.json).

# ---------- EARNINGS_DATES ----------
earn = [e for e in eam["earningsFull"] if e["date"] >= "2026-10-21"]
em = dict(ivd["expectedMoves"])
methods = dict(ivd.get("methods", {}))
for e in earn:
    pct = em.get(e["ticker"])
    if pct is not None:
        e["expected_move"] = pct
        e["move_as_of"] = "Oct 21, 2026"
        e["move_method"] = methods.get(e["ticker"]) or "options-implied (optioncharts.io overview)"
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
carried_list = ivd["carriedList"]
iv_source = ("Oct 21, 2026 · 45 of 63 refreshed from optioncharts.io (live overview pages); "
             f"18 carried last-good ({', '.join(carried_list)})")

# ---------- ANALYST_REVISIONS ----------
analyst = data["ANALYST_REVISIONS"]
for t, items in eam["analystNew"].items():
    existing = analyst.get(t, [])
    seen = {(i.get("sortDate"), i.get("detail")) for i in existing}
    new_items = [i for i in items if (i.get("sortDate"), i.get("detail")) not in seen]
    merged = new_items + existing
    merged.sort(key=lambda x: x.get("sortDate", ""), reverse=True)
    analyst[t] = [i for i in merged if i.get("sortDate", "9999") >= "2026-09-21"] or merged[:7]

# ---------- MACRO ----------
macro = eam["macroFull"]
oct28 = fedwatch_fresh["meetings"].get("Oct 28, 2026", [])
hold = next((p for lbl, p in oct28 if lbl == "375-400"), None)
hike = next((p for lbl, p in oct28 if lbl == "400-425"), None)
if hold is not None and hike is not None:
    for m in macro:
        if m["date"] == "2026-10-28" and "FOMC rate decision" in m["title"]:
            m["impact"] = (f"Markets price ~{hold}% hold at 375-400 bps and ~{hike}% hike; "
                           "a surprise would move stocks and bonds sharply.")
            m["impactZh"] = f"市场定价约{hold}%维持375-400 基点、约{hike}%加息；若有意外，股债将剧烈波动。"

# ---------- ASOF / I18N ----------
asof = dict(data["ASOF"])
asof["sectorBreadth"] = "Oct 21, 2026 8:30 AM ET"
asof["macro"] = "Oct 21, 2026 ~8:30 AM ET"
asof["expectedMoves"] = "Oct 21, 2026 ~8:30 AM ET"
asof["internals"] = "Oct 21, 2026 8:30 AM ET"

n = len(pot)
i18n = json.loads(json.dumps(data["I18N_OVERRIDES"]))
i18n["en"]["tradesDesc"] = f"{n} ranked setups from the October 21 Finviz screen, with verified front-month options activity."
i18n["en"]["ivAsOf"] = ("Updated Oct 21, 2026 · optioncharts.io 30-day IV readings "
                        "(45 of 63 refreshed; 18 carried last-good); stale source pages are flagged in ticker detail")
i18n["en"]["calendarDesc"] = "Macro calendar refreshed Oct 21, 2026 ~8:30 AM ET"
i18n["en"]["sevenDayWindow"] = "Next 7 days: Oct 21 – Oct 27, 2026"
i18n["en"]["checked"] = "Checked Oct 21, 2026 ~8:30 AM ET"
i18n["zh"]["tradesDesc"] = "根据 10 月 21 日的 Finviz 筛选，列出13个已验证近月期权活跃度的排序机会。"
i18n["zh"]["ivAsOf"] = "更新于 10 月 21 日 · optioncharts.io 隐含波动率数据（63 个标的中 45 个已刷新，18 个沿用上次有效值）"
i18n["zh"]["calendarDesc"] = "宏观日历已于 2026年10月21日 ~8:30 AM ET 更新"
i18n["zh"]["sevenDayWindow"] = "未来7天：2026年10月21日 – 10月27日"
i18n["zh"]["checked"] = "检查于 2026年10月21日 ~8:30 AM ET"

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
      "| fedWatch Oct28:", fw["meetings"][0]["outcomes"])
