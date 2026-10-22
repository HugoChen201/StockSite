#!/usr/bin/env python3
"""Morning-refresh patch builder for StockSite data.json (Thu 2026-10-22).

Sources (hidden_files/):
- finviz_2026-10-22.json: FILE is authoritative (64 results, 15 ranked, LMT 74
  top). The collector's chat handoff carried a DIFFERENT interim dataset
  (47 results, PATH 88 top) — disowned per the Oct-20/21 precedent after the
  parent verified the live screen via browser.open: 65 total, and the file's
  prices/day% matched the live screen exactly on all 6 overlapping names
  (BTI/CHKP/CLOV/CRGY/DG/DLTR); the handoff dataset matched nothing.
- history_2026-10-22.json: 75x Oct-21 bars (Yahoo chart JSON; SKHY + SQ-via-XYZ
  added on parent recheck). Sector breadth Oct-21 closes verified vs data.json
  (matches within rounding) — data.json SECTOR_BREADTH carried.
- iv_2026-10-22.json: FILE authoritative (chat summary counts/values differed):
  IV 48/63 refreshed, 15 carried (pages stale at Oct-21 copies, 429 batch or
  no-IV tickers); expected moves 35 earnings.
- earnings-analyst-macro_2026-10-22.json: earnings 36 (LRCX/META/PGR/TSLA/TXN
  dropped post-earnings); analystNew 18 items (META x7, TSLA x5, LRCX x3,
  TXN x2, GOOGL x1 — post-earnings actions); macro 11 carried.
- internals_2026-10-22.json: AAII FRESH week ending Oct 21 (file values
  36.9/17.3/45.8 verified by parent directly on aaii.com; the collector's chat
  report numbers 35.2/20.2/44.6 were WRONG and not used). putCall carried
  (YCharts still latest Oct 20: eq 0.56 / idx 1.01), flows carried (no Oct-22
  ETF Action report), F&G 31 confirmed by fallback CSV Oct-21 row 31.37.
- fedwatch_2026-10-22.json: live CME page, data as of Oct 21 14:37 CT:
  Oct 28 94.8% hold / 5.2% hike; Dec 9 49.4/47.7/2.9. Browser EFFR reading
  3.63 NOT written (inconsistent with 375-400 target range) — effr carried.
SMI finalized Oct 21 (1000.09) by close refresh — carried untouched.
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())

finviz = json.loads((HID / "finviz_2026-10-22.json").read_text())
hist = json.loads((HID / "history_2026-10-22.json").read_text())
ivd = json.loads((HID / "iv_2026-10-22.json").read_text())
eam = json.loads((HID / "earnings-analyst-macro_2026-10-22.json").read_text())
internals = json.loads((HID / "internals_2026-10-22.json").read_text())
fedwatch_fresh = json.loads((HID / "fedwatch_2026-10-22.json").read_text())

RUN_STAMP = "Oct 22, 2026 7:45 AM ET"

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
excl = "; ".join(finviz.get("excluded", []))
screen = {
    "updated": RUN_STAMP,
    "scanTime": "2026-10-22 ~07:35 AM ET (premarket)",
    "resultCount": finviz["resultCount"],
    "resultTime": "2026-10-22 ~07:35 AM ET (premarket)",
    "source": "https://finviz.com/screener?v=211&f=cap_midover,sh_opt_option,ta_change_u,ta_highlow52w_b10h,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3",
    "optionsAsOf": "Oct 22, 2026 (optioncharts.io)",
    "note": (f"15 ranked from {finviz['resultCount']} results (parent recheck of the live screen "
             "showed 65 total premarket — count drifts with ticks; the file's prices matched the "
             "live screen exactly). LMT tops the list on this morning's Q3 beat (EPS $7.97 vs "
             "$7.49 est, sales +11%, guidance raised). Premarket screen: Finviz prints mix the "
             "Oct 21 close with thin premarket ticks, so relative volume is near zero and was "
             f"scored down. Excluded: {excl}. Several ranked names (MDT, DG, BTI, LYB) are "
             "flow/technical only with no fresh headline catalyst — flagged in their notes and "
             "scored down on catalyst."),
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
# effr carried last-good (browser's 3.63 reading inconsistent with target range)
mi["fedWatch"] = fw

aaii_fresh = internals["aaii"]
weeks = aaii_fresh["recentWeeks"]
mi["aaii"] = {
    "asof": "Week ending Oct 21, 2026 (published Oct 22)",
    "url": "https://www.aaii.com/sentimentsurvey",
    "history": str([{"date": w["weekEnding"].replace("/2026", ""), "bullish": w["bullish"],
                     "neutral": w["neutral"], "bearish": w["bearish"]} for w in weeks]),
    "latest": str({"bullish": weeks[0]["bullish"], "neutral": weeks[0]["neutral"],
                   "bearish": weeks[0]["bearish"]}),
    "note": ("Bull-bear spread -8.9pp (widened from -2.9pp the prior week). "
             "Historical averages: 37.5/31.0/31.5. Verified on aaii.com this morning."),
}
# fearGreed confirmed (CSV Oct-21 row 31.37 vs 31 in data.json) — carried.
# vixTerm / breadth / flows / putCall / smi: Oct-21 close values carried untouched.

# ---------- EARNINGS_DATES ----------
earn = [e for e in eam["earningsFull"] if e["date"] >= "2026-10-22"]
em = dict(ivd["expectedMoves"])
methods = dict(ivd.get("methods", {}))
for e in earn:
    pct = em.get(e["ticker"])
    if pct is not None:
        e["expected_move"] = pct
        e["move_as_of"] = "Oct 22, 2026"
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
refreshed = 0
for t, v in ivd["iv"].items():
    if isinstance(v, dict) and "iv30" in v:
        iv_data[t] = {"iv30": v["iv30"], "rank": v["rank"], "percentile": v["percentile"]}
        refreshed += 1
carried_list = ivd["carriedList"]
iv_source = (f"Oct 22, 2026 · {refreshed} of 63 refreshed from optioncharts.io (live overview pages); "
             f"{len(carried_list)} carried last-good ({', '.join(carried_list)})")

# ---------- ANALYST_REVISIONS ----------
analyst = data["ANALYST_REVISIONS"]
for t, items in eam["analystNew"].items():
    existing = analyst.get(t, [])
    seen = {(i.get("sortDate"), i.get("detail")) for i in existing}
    new_items = [i for i in items if (i.get("sortDate"), i.get("detail")) not in seen]
    merged = new_items + existing
    merged.sort(key=lambda x: x.get("sortDate", ""), reverse=True)
    analyst[t] = [i for i in merged if i.get("sortDate", "9999") >= "2026-09-22"] or merged[:7]

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
asof["sectorBreadth"] = RUN_STAMP
asof["macro"] = "Oct 22, 2026 ~7:45 AM ET"
asof["expectedMoves"] = "Oct 22, 2026 ~7:45 AM ET"
asof["internals"] = RUN_STAMP

n = len(pot)
i18n = json.loads(json.dumps(data["I18N_OVERRIDES"]))
i18n["en"]["tradesDesc"] = f"{n} ranked setups from the October 22 Finviz screen, with verified front-month options activity."
i18n["en"]["ivAsOf"] = (f"Updated Oct 22, 2026 · optioncharts.io 30-day IV readings "
                        f"({refreshed} of 63 refreshed; {len(carried_list)} carried last-good); stale source pages are flagged in ticker detail")
i18n["en"]["calendarDesc"] = "Macro calendar refreshed Oct 22, 2026 ~7:45 AM ET"
i18n["en"]["sevenDayWindow"] = "Next 7 days: Oct 22 – Oct 28, 2026"
i18n["en"]["checked"] = "Checked Oct 22, 2026 ~7:45 AM ET"
i18n["zh"]["tradesDesc"] = f"根据 10 月 22 日的 Finviz 筛选，列出{n}个已验证近月期权活跃度的排序机会。"
i18n["zh"]["ivAsOf"] = f"更新于 10 月 22 日 · optioncharts.io 隐含波动率数据（63 个标的中 {refreshed} 个已刷新，{len(carried_list)} 个沿用上次有效值）"
i18n["zh"]["calendarDesc"] = "宏观日历已于 2026年10月22日 ~7:45 AM ET 更新"
i18n["zh"]["sevenDayWindow"] = "未来7天：2026年10月22日 – 10月28日"
i18n["zh"]["checked"] = "检查于 2026年10月22日 ~7:45 AM ET"

patch = {
    "SCREEN_SNAPSHOT": screen,
    "HISTORY": history,
    "MARKET_INTERNALS": mi,
    "SECTOR_BREADTH": data["SECTOR_BREADTH"],
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
      "| IV refreshed:", refreshed, "carried:", len(carried_list),
      "| fedWatch Oct28:", fw["meetings"][0]["outcomes"],
      "| AAII:", mi["aaii"]["latest"])
