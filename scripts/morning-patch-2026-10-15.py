#!/usr/bin/env python3
"""Morning-refresh patch builder for StockSite data.json (Thu 2026-10-15).

Sources (all in goals/stock-watchlist-website/hidden_files/):
- finviz_2026-10-15.json: 63 results, 15 ranked (IBRX 83 top, FDA Anktiva approval)
- internals_2026-10-15.json: P/C Oct-14 finals NEW (eq 0.61, idx 1.01);
  AAII NEW week ending Oct 14 (38.7/19.7/41.6); flows + F&G carried/confirmed;
  FedWatch pending live-browser (carried Oct 13 unless /tmp/fedwatch_2026-10-15.json exists)
- history_2026-10-15.json: 75x Oct-14 bars (Stooq, SPY verified vs close refresh),
  sector breadth final Oct-14 closes
- iv_2026-10-15.json: IV 63/63 refreshed (optioncharts), expected moves refreshed
- earnings-analyst-macro_2026-10-15.json: analystNew (TSM/DELL/AMD/BRK-B),
  earnings drops ASML/BAC/MS (Oct 14), LRCX session -> after close, macroFull
SMI already finalized Oct 14 (999.53) by close refresh — carried untouched.
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())

finviz = json.loads((HID / "finviz_2026-10-15.json").read_text())
internals = json.loads((HID / "internals_2026-10-15.json").read_text())
hist = json.loads((HID / "history_2026-10-15.json").read_text())
ivd = json.loads((HID / "iv_2026-10-15.json").read_text())
eam = json.loads((HID / "earnings-analyst-macro_2026-10-15.json").read_text())

RUN_STAMP = "Oct 15, 2026 7:45 AM ET"  # approx; updated by caller if needed

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
    "scanTime": "2026-10-15 ~07:31 AM ET (premarket)",
    "resultCount": finviz["resultCount"],
    "resultTime": "2026-10-15 ~07:31 AM ET (premarket)",
    "source": "https://finviz.com/screener?v=211&f=cap_midover,sh_opt_option,ta_change_u,ta_highlow52w_b10h,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3",
    "optionsAsOf": "Oct 15, 2026 (optioncharts.io)",
    "note": ("15 ranked from 63 results. Premarket screen: Finviz prints include Oct 15 "
             "premarket action, so 'up on the day' is the premarket print, not purely the "
             "Oct 14 session. SPCX did not appear — nothing excluded. IBRX tops the list on "
             "the Oct 14 FDA expanded Anktiva approval (options volume 229% of 30-day avg). "
             "RELX relativeVolume unavailable from Finviz (page-3 fetch rate-limited) — "
             "its relVol score uses Oct 14 volume-vs-average and options evidence."),
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
# put/call NEW Oct-14 finals
pc = mi["putCall"]
pc["equity"] = internals["putCall"]["equity"]["value"]
pc["equityAsOf"] = "Oct 14, 2026 (ycharts)"
pc["index"] = internals["putCall"]["index"]["value"]
pc["indexAsOf"] = "Oct 14, 2026 (ycharts)"
pc["asof"] = "Equity Oct 14, 2026 · Index Oct 14, 2026 (ycharts)"
mi["putCall"] = pc
# AAII NEW week
mi["aaii"] = {
    "asof": internals["aaii"]["asof"],
    "url": "https://www.aaii.com/sentimentsurvey",
    "history": internals["aaii"]["history"],
    "latest": {"bullish": 38.7, "neutral": 19.7, "bearish": 41.6},
    "note": "Bull-bear spread -2.9pp (flipped from +1.3pp the prior week). Historical averages: 37.5/31.0/31.5.",
}
# FedWatch: live-browser file if present, else carried
fw_path = Path("/tmp/fedwatch_2026-10-15.json")
if fw_path.exists():
    mi["fedWatch"] = json.loads(fw_path.read_text())
# fearGreed / vixTerm / breadth / flows / smi carried (Oct-14 close verified)

# ---------- EARNINGS_DATES ----------
earn = [e for e in data["EARNINGS_DATES"] if e["date"] >= "2026-10-15"]
em = ivd["expectedMoves"]
for e in earn:
    mv = em.get(e["ticker"])
    pct = mv.get("pct") if isinstance(mv, dict) else mv
    if pct is not None:
        e["expected_move"] = pct
        e["move_as_of"] = "Oct 15, 2026"
        e["move_method"] = ivd.get("methods", {}).get(e["ticker"]) or (mv.get("method") if isinstance(mv, dict) else None) or "options-implied (optioncharts.io overview)"
        e["move_method_zh"] = "期权隐含预期波动（期权链概览）"
    if e["ticker"] == "LRCX" and e["date"] == "2026-10-21":
        e["session"] = "after close"
    if e["ticker"] == "TSM" and e["date"] == "2026-10-15":
        # IV collector's file stored the 10/30-expiry reading (3.57); its verified
        # Oct-16 earnings-expiry headline is 5.95 — site convention = first expiry
        # on/after the earnings date.
        e["expected_move"] = 5.95
        e["move_method"] = "options-implied (optioncharts.io overview; expiry 2026-10-16 expected move)"
earn.sort(key=lambda x: x["date"])

# ---------- EXPECTED_MOVES ----------
expected = dict(data["EXPECTED_MOVES"])
for t, mv in em.items():
    pct = mv.get("pct") if isinstance(mv, dict) else mv
    if pct is not None:
        expected[t] = pct
expected["TSM"] = 5.95  # earnings-expiry (Oct 16) headline; see EARNINGS_DATES note above

# ---------- IV_DATA / IV_SOURCE ----------
iv_data = dict(data["IV_DATA"])
for t, v in ivd["iv"].items():
    if isinstance(v, dict) and "iv30" in v:
        iv_data[t] = {"iv30": v["iv30"], "rank": v["rank"], "percentile": v["percentile"]}
    # else: carried last-good entry already in data.json (BRK-B) — keep untouched
iv_source = ("Oct 15, 2026 · 62 of 63 refreshed from optioncharts.io (live overview pages); "
             "1 carried last-good (BRK-B)")

# ---------- ANALYST_REVISIONS ----------
analyst = data["ANALYST_REVISIONS"]
for t, items in eam["analystNew"].items():
    existing = analyst.get(t, [])
    seen = {(i.get("sortDate"), i.get("detail")) for i in existing}
    new_items = [i for i in items if (i.get("sortDate"), i.get("detail")) not in seen]
    merged = new_items + existing
    merged.sort(key=lambda x: x.get("sortDate", ""), reverse=True)
    # keep last ~30 days window from Oct 15 (plus keep at least the list trimmed to 2026-09-15+)
    analyst[t] = [i for i in merged if i.get("sortDate", "9999") >= "2026-09-15"] or merged[:7]

# ---------- MACRO ----------
macro = eam["macroFull"]

# ---------- ASOF / I18N ----------
asof = dict(data["ASOF"])
asof["sectorBreadth"] = "Oct 15, 2026 7:45 AM ET"
asof["macro"] = "Oct 15, 2026 ~7:45 AM ET"
asof["expectedMoves"] = "Oct 15, 2026 ~7:45 AM ET"
asof["internals"] = "Oct 15, 2026 7:45 AM ET"

n = len(pot)
i18n = json.loads(json.dumps(data["I18N_OVERRIDES"]))
i18n["en"]["tradesDesc"] = f"{n} ranked setups from the October 15 Finviz screen, with verified front-month options activity."
i18n["en"]["ivAsOf"] = ("Updated Oct 15, 2026 · optioncharts.io 30-day IV readings "
                        "(62 of 63 refreshed; 1 carried last-good: BRK-B); stale source pages are flagged in ticker detail")
i18n["en"]["calendarDesc"] = "Macro calendar refreshed Oct 15, 2026 ~7:45 AM ET"
i18n["en"]["sevenDayWindow"] = "Next 7 days: Oct 15 – Oct 21, 2026"
i18n["en"]["checked"] = "Checked Oct 15, 2026 ~7:45 AM ET"
i18n["zh"]["tradesDesc"] = "根据 10 月 15 日的 Finviz 筛选，列出15个已验证近月期权活跃度的排序机会。"
i18n["zh"]["ivAsOf"] = "更新于 10 月 15 日 · optioncharts.io 隐含波动率数据（63 个标的中 62 个已刷新，1 个沿用上次有效值：BRK-B）"
i18n["zh"]["calendarDesc"] = "宏观日历已于 2026年10月15日 ~7:45 AM ET 更新"
i18n["zh"]["sevenDayWindow"] = "未来7天：2026年10月15日 – 10月21日"
i18n["zh"]["checked"] = "检查于 2026年10月15日 ~7:45 AM ET"

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
