#!/usr/bin/env python3
"""Morning-refresh patch builder for StockSite data.json (Fri 2026-10-23).

Sources (hidden_files/):
- finviz_2026-10-23.json: FILE authoritative; parent live-screen verification
  matched exactly (Overview '#1 / 54 Total'; CLF 13.14, CCI 86.43 +9.64%,
  BHVN 14.88, CLOV 4.74, BAH 81.00 on page 1). 54 results, 14 ranked, CLF 74 top.
  SPCX not in screen (standing exclusion noted by collector anyway).
- history_2026-10-23.json: 75x Oct-22 bars (Yahoo chart JSON, no 429);
  SPY verified o766.37/c763.96 vs SMI inputs. Sector breadth = Oct-22 FINAL
  closes (replaces the 3:55 PM intraday snapshot in data.json).
- iv_2026-10-23.json: FILE authoritative (61/63 refreshed, carried BRK-B + SQ).
  The collector's chat summary contradicted its file (claimed 40 refreshed,
  GOOGL/META/TSLA stale) — parent arbitration via live optioncharts.io pages
  proved the FILE correct: GOOGL page reads 'As of October 22, 2026, IV 36.96,
  rank 62.83, percentile 71.43' = file values exactly, EM 6.12 = Oct-30 expiry
  row; SQ page is a Thai namesake with no data (carried correct). Same
  file-over-summary precedent as Oct 15/20/21/22.
- earnings-analyst-macro_2026-10-23.json: earnings 34 (BE/WDC dropped
  post-Oct-22 reports; both beat, shares fell); analystNew 21 items
  (BE x5 post-Q3, WDC x2, GOOGL x1, AVGO x1, META x6 + TSLA x6 Oct-22
  follow-ons not in data.json); macro 11 carried.
- internals_2026-10-23.json: matches parent verification exactly —
  P/C equity NEW Oct-21 final 0.52 (YCharts), index carried Oct-20 1.01;
  F&G 20 confirmed via fallback CSV Oct-22 row 19.81 (CNN teapot);
  VIX 19.03 / VIX3M 20.12 confirmed via Yahoo chart JSON;
  flows carried (no Oct-23 ETF Action report posted; Oct-22 report covers
  Oct-21 session); AAII unchanged wk-end Oct 21: 36.9/17.3/45.8.
- FedWatch: CARRIED Oct-22 formal record (Oct 28: 87.3% hold / 12.7% hike)
  at patch time — live browser task still running; if its formal record
  lands later, apply as a correction patch (Oct 13/20/22 precedent).
SMI finalized Oct 22 (1000.28) by close refresh — carried untouched.
Breadth (A/D 1.55/+398, >50d 60.63, >200d 57.25, hi 94/lo 64) = Oct-22 close
verified by close-refresh follow-up — carried untouched.
"""
import json
from pathlib import Path

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())

finviz = json.loads((HID / "finviz_2026-10-23.json").read_text())
hist = json.loads((HID / "history_2026-10-23.json").read_text())
ivd = json.loads((HID / "iv_2026-10-23.json").read_text())
eam = json.loads((HID / "earnings-analyst-macro_2026-10-23.json").read_text())
internals = json.loads((HID / "internals_2026-10-23.json").read_text())

RUN_STAMP = "Oct 23, 2026 7:45 AM ET"

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
    "scanTime": "2026-10-23 ~07:35 AM ET (premarket)",
    "resultCount": finviz["resultCount"],
    "resultTime": "2026-10-23 ~07:35 AM ET (premarket)",
    "source": "https://finviz.com/screener?v=211&f=cap_midover,sh_opt_option,ta_change_u,ta_highlow52w_b10h,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3",
    "optionsAsOf": "Oct 23, 2026 (optioncharts.io)",
    "note": (f"14 ranked from {finviz['resultCount']} results (parent live-screen recheck "
             "showed '#1 / 54 Total' and the file's page-1 prices matched exactly). "
             "CLF tops the list on its Oct-19 Q3 beat (adj EPS $0.28, EBITDA more than "
             "doubled sequentially, 2027 EBITDA seen >$4B on contract resets) with thick "
             "front-month options (15,450 vol / 116,613 OI). Premarket screen: Finviz "
             "prints mix the Oct 22 close with thin premarket ticks, so relative volume "
             f"is near zero and was scored down. Excluded: {excl}. Several ranked names "
             "(PTON, CLOV, SPG, BEKE) are flow/technical only with no fresh headline "
             "catalyst — flagged in their notes and scored down on catalyst."),
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

# ---------- SECTOR BREADTH (final Oct-22 closes) ----------
sb_old = {s["etf"]: s for s in data["SECTOR_BREADTH"]}
sector = []
for row in hist["sectorBreadth"]:
    base = dict(sb_old[row["etf"]])
    base["close"] = row["close"]
    base["previous"] = row["previous"]
    base["change"] = row["change"]
    sector.append(base)

# ---------- MARKET_INTERNALS ----------
mi = data["MARKET_INTERNALS"]
pc = mi["putCall"]
pc["equity"] = internals["putCall"]["equity"]["value"]
pc["equityAsOf"] = "Oct 21, 2026 (ycharts)"
pc["index"] = internals["putCall"]["index"]["value"]
pc["indexAsOf"] = "Oct 20, 2026 (ycharts; Oct-21 index finals not yet visible)"
pc["asof"] = "Equity Oct 21, 2026 · Index Oct 20, 2026 (ycharts)"
mi["putCall"] = pc
# fearGreed confirmed 20 (CSV Oct-22 19.81); vixTerm confirmed 19.03/20.12;
# breadth, flows, aaii, smi, fedWatch: Oct-22 close values carried untouched.

# ---------- EARNINGS_DATES ----------
earn = [e for e in eam["earningsFull"] if e["date"] >= "2026-10-23"]
em = dict(ivd["expectedMoves"])
methods = dict(ivd.get("methods", {}))
for e in earn:
    pct = em.get(e["ticker"])
    if pct is not None:
        e["expected_move"] = pct
        e["move_as_of"] = "Oct 23, 2026"
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
iv_source = (f"Oct 23, 2026 · {refreshed} of 63 refreshed from optioncharts.io (live overview pages); "
             f"{len(carried_list)} carried last-good ({', '.join(carried_list)})")

# ---------- ANALYST_REVISIONS ----------
analyst = data["ANALYST_REVISIONS"]
added = 0
for t, items in eam["analystNew"].items():
    existing = analyst.get(t, [])
    seen = {(i.get("sortDate"), i.get("detail")) for i in existing}
    new_items = [i for i in items if (i.get("sortDate"), i.get("detail")) not in seen]
    added += len(new_items)
    merged = new_items + existing
    merged.sort(key=lambda x: x.get("sortDate", ""), reverse=True)
    analyst[t] = [i for i in merged if i.get("sortDate", "9999") >= "2026-09-23"] or merged[:7]

# ---------- MACRO ----------
macro = eam["macroFull"]

# ---------- ASOF / I18N ----------
asof = dict(data["ASOF"])
asof["sectorBreadth"] = RUN_STAMP
asof["macro"] = "Oct 23, 2026 ~7:45 AM ET"
asof["expectedMoves"] = "Oct 23, 2026 ~7:45 AM ET"
asof["internals"] = RUN_STAMP

n = len(pot)
i18n = json.loads(json.dumps(data["I18N_OVERRIDES"]))
i18n["en"]["tradesDesc"] = f"{n} ranked setups from the October 23 Finviz screen, with verified front-month options activity."
i18n["en"]["ivAsOf"] = (f"Updated Oct 23, 2026 · optioncharts.io 30-day IV readings "
                        f"({refreshed} of 63 refreshed; {len(carried_list)} carried last-good); stale source pages are flagged in ticker detail")
i18n["en"]["calendarDesc"] = "Macro calendar refreshed Oct 23, 2026 ~7:45 AM ET"
i18n["en"]["sevenDayWindow"] = "Next 7 days: Oct 23 – Oct 29, 2026"
i18n["en"]["checked"] = "Checked Oct 23, 2026 ~7:45 AM ET"
i18n["zh"]["tradesDesc"] = f"根据 10 月 23 日的 Finviz 筛选，列出{n}个已验证近月期权活跃度的排序机会。"
i18n["zh"]["ivAsOf"] = f"更新于 10 月 23 日 · optioncharts.io 隐含波动率数据（63 个标的中 {refreshed} 个已刷新，{len(carried_list)} 个沿用上次有效值）"
i18n["zh"]["calendarDesc"] = "宏观日历已于 2026年10月23日 ~7:45 AM ET 更新"
i18n["zh"]["sevenDayWindow"] = "未来7天：2026年10月23日 – 10月29日"
i18n["zh"]["checked"] = "检查于 2026年10月23日 ~7:45 AM ET"

patch = {
    "SCREEN_SNAPSHOT": screen,
    "HISTORY": history,
    "MARKET_INTERNALS": mi,
    "SECTOR_BREADTH": sector,
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
      "| IV refreshed:", refreshed, "carried:", carried_list,
      "| analyst new merged:", added,
      "| P/C eq/idx:", pc["equity"], pc["index"],
      "| sector XLK:", sector[0]["change"])
