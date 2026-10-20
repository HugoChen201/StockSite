#!/usr/bin/env python3
"""Morning-refresh patch builder for StockSite data.json (Tue 2026-10-20).

Sources (hidden_files/):
- finviz_2026-10-20.json: 102 results, 14 ranked (DHT 85 top, tanker rates)
- internals_2026-10-20.json: all carried/confirmed from Oct-19 close verification
  (F&G 23 confirmed via fallback CSV Oct-19 row 23.11; VIX 18.44/19.60 confirmed;
  P/C Oct-19 finals not yet visible on YCharts text fetch; no new ETF Action
  report; AAII unchanged) + LIVE FedWatch Oct 20 via browser task (below)
- history_2026-10-20.json: 75x Oct-19 bars (Yahoo, SPY verified), sector breadth
  corrected to Oct-19 FINAL closes
- iv_2026-10-20.json: IV 61/63 refreshed (optioncharts), BRK-B + UBER carried;
  expected moves 38 (+ WMT 6.77 parent-verified Nov-20 expiry)
- earnings-analyst-macro_2026-10-20.json: earnings 41 (+WMT Nov 19), analystNew
  (META Morgan Stanley, WDC Wells Fargo), macro 11 (+JOLTS Nov 3, +PPI Nov 13)
FedWatch LIVE Oct 20 (browser task, CME page, current target 375-400, EFFR 3.87):
  Oct28 82.0 hold / 18.0 hike (was 85.1/14.9); Dec9 11.9/71.4/16.7;
  Jan27 7.7/44.5/38.3/9.5; Mar17 3.4/24.1/40.9/25.8/5.8;
  Apr28 2.3/17.4/33.5/31.0/13.8/2.0. Meetings Jun 2027+ not opened -> carried
  from Oct 19 read, noted in fedWatch context/asof.
SMI finalized Oct 19 (1000.06) by close refresh — carried untouched.
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())

finviz = json.loads((HID / "finviz_2026-10-20.json").read_text())
hist = json.loads((HID / "history_2026-10-20.json").read_text())
ivd = json.loads((HID / "iv_2026-10-20.json").read_text())
eam = json.loads((HID / "earnings-analyst-macro_2026-10-20.json").read_text())

RUN_STAMP = "Oct 20, 2026 8:15 AM ET"

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
    "scanTime": "2026-10-20 ~07:31 AM ET (premarket)",
    "resultCount": finviz["resultCount"],
    "resultTime": "2026-10-20 ~07:31 AM ET (premarket)",
    "source": "https://finviz.com/screener?v=211&f=cap_midover,sh_opt_option,ta_change_u,ta_highlow52w_b10h,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3",
    "optionsAsOf": "Oct 20, 2026 (optioncharts.io)",
    "note": ("14 ranked from 102 results. Premarket screen: Finviz prints are "
             "premarket ticks, so 'up on the day' mixes the Oct 19 close with thin "
             "premarket prints (DHT +5.05% on ~193K premarket shares, relVol 3.70). "
             "DHT tops the list on crude-tanker VLCC rates at/near 2026 highs "
             "(Iran-war disruption). Thin-print artifacts NOT ranked: SGML "
             "(+22.22% on 0 shares), LAC (12 shares), WOLF (13), GSBD (21; also an "
             "Oct 19 merger-arb print). SPCX appeared at #38 and was EXCLUDED per "
             "standing rule (Securitize tokenized-SpaceX symbol, not a public "
             "operating company). Thin-options names excluded: AGYS (19 contracts / "
             "106 OI), RELX (0 / 106). RYTM ranked last (45) — extremely thin "
             "options (14 vol / 84 OI), lowest conviction."),
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
# FedWatch LIVE Oct 20 (schema contract: decision + outcomes[].label/.pct)
fw = json.loads(json.dumps(mi["fedWatch"]))
fresh = {
    "Oct 28, 2026": [("375-400", 82.0), ("400-425", 18.0)],
    "Dec 9, 2026": [("375-400", 11.9), ("400-425", 71.4), ("425-450", 16.7)],
    "Jan 27, 2027": [("375-400", 7.7), ("400-425", 44.5), ("425-450", 38.3), ("450-475", 9.5)],
    "Mar 17, 2027": [("375-400", 3.4), ("400-425", 24.1), ("425-450", 40.9), ("450-475", 25.8), ("475-500", 5.8)],
    "Apr 28, 2027": [("375-400", 2.3), ("400-425", 17.4), ("425-450", 33.5), ("450-475", 31.0), ("475-500", 13.8), ("500-525", 2.0)],
}
for m in fw["meetings"]:
    if m["decision"] in fresh:
        m["outcomes"] = [{"label": lbl, "pct": pct} for lbl, pct in fresh[m["decision"]]]
fw["asof"] = ("Oct 20, 2026 (CME FedWatch live page; data as of 20 Oct 2026 06:21 CT for "
              "Oct 2026–Apr 2027 meetings; Jun 2027+ meetings carried from Oct 19 read)")
fw["context"] = ("Market-implied probabilities from 30-day fed funds futures (CME FedWatch, "
                 "verified live this morning), not forecasts. Oct 28: 82.0% hold / 18.0% hike. "
                 "Dec 9: 11.9% at 375-400 / 71.4% at 400-425 / 16.7% at 425-450.")
fw["effr"] = 3.87
fw["effrAsOf"] = "Oct 20, 2026 (shown on the CME FedWatch page, EFFR 3.87%)"
mi["fedWatch"] = fw
# fearGreed / vixTerm / breadth / flows / aaii / smi / putCall: all confirmed or
# carried from the Oct 19 close verification — no fresher data exists premarket
# Oct 20 (see internals_2026-10-20.json). MARKET_INTERNALS carried wholesale.

# ---------- EARNINGS_DATES ----------
earn = [e for e in eam["earningsFull"] if e["date"] >= "2026-10-20"]
em = dict(ivd["expectedMoves"])
em["WMT"] = 6.77
methods = dict(ivd.get("methods", {}))
methods["WMT"] = "options-implied (optioncharts.io overview; expiry 2026-11-20 expected move)"
for e in earn:
    pct = em.get(e["ticker"])
    if pct is not None:
        e["expected_move"] = pct
        e["move_as_of"] = "Oct 20, 2026"
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
    # else carried last-good — keep data.json entry (BRK-B marker dict has no iv30)
iv_source = ("Oct 20, 2026 · 61 of 63 refreshed from optioncharts.io (live overview pages); "
             "2 carried last-good (BRK-B, UBER)")

# ---------- ANALYST_REVISIONS ----------
analyst = data["ANALYST_REVISIONS"]
for t, items in eam["analystNew"].items():
    existing = analyst.get(t, [])
    seen = {(i.get("sortDate"), i.get("detail")) for i in existing}
    new_items = [i for i in items if (i.get("sortDate"), i.get("detail")) not in seen]
    merged = new_items + existing
    merged.sort(key=lambda x: x.get("sortDate", ""), reverse=True)
    analyst[t] = [i for i in merged if i.get("sortDate", "9999") >= "2026-09-20"] or merged[:7]

# ---------- MACRO ----------
macro = eam["macroFull"]
for m in macro:
    if m["date"] == "2026-10-28" and "FOMC rate decision" in m["title"]:
        m["impact"] = ("Markets price ~82.0% hold at 375-400 bps and ~18.0% hike; "
                       "a surprise would move stocks and bonds sharply.")
        m["impactZh"] = "市场定价约82.0%维持375-400 基点、约18.0%加息；若有意外，股债将剧烈波动。"

# ---------- ASOF / I18N ----------
asof = dict(data["ASOF"])
asof["sectorBreadth"] = "Oct 20, 2026 8:15 AM ET"
asof["macro"] = "Oct 20, 2026 ~8:15 AM ET"
asof["expectedMoves"] = "Oct 20, 2026 ~8:15 AM ET"
asof["internals"] = "Oct 20, 2026 8:15 AM ET"

n = len(pot)
i18n = json.loads(json.dumps(data["I18N_OVERRIDES"]))
i18n["en"]["tradesDesc"] = f"{n} ranked setups from the October 20 Finviz screen, with verified front-month options activity."
i18n["en"]["ivAsOf"] = ("Updated Oct 20, 2026 · optioncharts.io 30-day IV readings "
                        "(61 of 63 refreshed; 2 carried last-good: BRK-B, UBER); stale source pages are flagged in ticker detail")
i18n["en"]["calendarDesc"] = "Macro calendar refreshed Oct 20, 2026 ~8:15 AM ET"
i18n["en"]["sevenDayWindow"] = "Next 7 days: Oct 20 – Oct 26, 2026"
i18n["en"]["checked"] = "Checked Oct 20, 2026 ~8:15 AM ET"
i18n["zh"]["tradesDesc"] = "根据 10 月 20 日的 Finviz 筛选，列出14个已验证近月期权活跃度的排序机会。"
i18n["zh"]["ivAsOf"] = "更新于 10 月 20 日 · optioncharts.io 隐含波动率数据（63 个标的中 61 个已刷新，2 个沿用上次有效值：BRK-B、UBER）"
i18n["zh"]["calendarDesc"] = "宏观日历已于 2026年10月20日 ~8:15 AM ET 更新"
i18n["zh"]["sevenDayWindow"] = "未来7天：2026年10月20日 – 10月26日"
i18n["zh"]["checked"] = "检查于 2026年10月20日 ~8:15 AM ET"

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
