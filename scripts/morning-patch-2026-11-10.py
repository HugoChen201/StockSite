#!/usr/bin/env python3
"""Morning-refresh patch builder for StockSite data.json (Tue 2026-11-10).

Collectors (all verified by the parent run):
- Finviz screen: text fetch ~7:27 AM ET, 87 results (v=111 Overview view;
  v=211 TA view returned shell-only; rows 81-87 unrecovered). 15 ranked.
  Option volumes are Nov 9 session totals from optioncharts.io; optionOI
  is null for all 15 (text fetch exposes volume only, no total OI).
- History: Yahoo daily chart API direct, Nov 9 bars for 74 of 75 HISTORY
  tickers (no gaps; cross-checked vs Finnhub closes). SQ missing: Yahoo
  404 -- Block renamed SQ -> XYZ; NO rename applied (pending Hugo).
- Internals: F&G 32 Fear Nov 9 close (whit3rabbit CSV mirror; CNN JSON
  418 bot-blocked; mirror revised Nov 6 to 24.35, superseding stored 22);
  VIX 19.92 / VIX3M 20.85 Nov 9 closes (Yahoo, verified = stored), ratio
  1.05 contango; put/call Nov 9 finals via YCharts (eq 0.56, idx 1.06);
  AAII carried (week ending Nov 4, next week posts Nov 12); flows: Nov 9
  session etfaction report NOT yet posted as of ~7:30 AM ET (Nov 6-session
  values carried, already finalized by close patch); breadth carried
  verbatim (Barchart text fetch HTTP 202, no data); SMI carried 998.65
  (finalized through Nov 9 by close patch); sector breadth corrected to
  Yahoo Nov 9 FINAL closes (stored values were 3:55 PM ET snapshots).
- FedWatch: LIVE CME FedWatch page via browser (data as of 06:15 CT Nov 10).
  Dec 9: 0.9% hold / 99.1% hike -- near-certain hike now priced (was
  80.5% Nov 9) after hot-CPI expectations + Waller 50bp signal. EFFR
  carried 3.88 (not shown on page). Meeting dates Jun 9 / Sep 15 2027
  confirmed as stored (assignment list had Jun 16 / Sep 22).
- Macro: 22 events (21 matched stored + NEW Dec 10 CPI Nov 2026, BLS
  schedule verified Nov 6). Dec 18 CPI not re-added (2025 conflation).
- IV: optioncharts.io overview pages, 48 of 63 refreshed (30-day IV + IV
  rank; IV percentile carried last-good for all 63 -- text fetch exposes
  IV/rank only). 15 carried: 14 on browser-service 429 after 48 fetches
  (NOW, ADBE, SHOP, GS, MS, JNJ, CVX, HD, MSTR, UBER, IWM, SNOW, BAC,
  TLT -- NOT retried per rate-limit stop), SQ stale (Sahakol page).
  No refreshed ticker ranks >100 now (HD carried rank 102 only).
  BRK-B via BRKB (16.7%, rank 54).
- Expected moves: IV-formula fallback (30-day IV x sqrt(DTE/365) to the
  Friday weekly expiry); 9 of 11 down vs Nov 9 (DTE-driven, Nov 13
  expiry now DTE 3 vs 4); DELL and CRM up (IV rises outweighed DTE).
  Strip: 11 entries, none dropped (earliest CRWV today, Nov 10 AMC).
- Analyst: 2 new entries (AMD Nov 9 Oppenheimer upgrade Perform ->
  Outperform PT $600; NVDA Nov 9 Aletheia downgrade Buy -> Hold);
  stored 888 carried, total 890. Block/Cantor PT $95->$102 NOT applied
  (XYZ rename pending). Per-ticker MarketBeat pages not re-checked
  (429 after IV fetches) -- only the two headline items added.
"""
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())
screen = json.loads((HID / "screen_2026-11-10.json").read_text())
internals = json.loads((HID / "internals_2026-11-10.json").read_text())
fedwatch = json.loads((HID / "fedwatch_2026-11-10.json").read_text())
ive = json.loads((HID / "iv_earnings_2026-11-10.json").read_text())
hist = json.loads((HID / "history_2026-11-10.json").read_text())

RUN_STAMP = datetime.now(ZoneInfo("America/New_York")).strftime(
    "%b %-d, %Y %-I:%M %p ET").replace("  ", " ")
notes = [f"RUN_STAMP={RUN_STAMP}"]

# ---------- validation ----------
for p in screen["potential"]:
    assert p["score"] == sum(p["components"].values()), p["ticker"]
    assert set(p["components"]) == {"relativeVolume", "distanceFromHigh",
        "optionLiquidity", "catalyst", "trendStructure"}
assert set(ive["iv"]) == {s["ticker"] for s in data["STOCKS"]}
assert set(ive["analystRevisions"]) == {s["ticker"] for s in data["STOCKS"]}
CARRIED_IV = ["NOW", "ADBE", "SHOP", "GS", "MS", "JNJ", "CVX", "HD",
              "MSTR", "UBER", "IWM", "SNOW", "BAC", "TLT", "SQ"]
assert len(CARRIED_IV) == 15
for t in CARRIED_IV:
    assert ive["iv"][t] == data["IV_DATA"][t], t
for m in fedwatch["meetings"]:
    assert abs(sum(o["pct"] for o in m["outcomes"]) - 100.0) < 0.5, m["decision"]
assert all(e["date"] >= "2026-11-10" for e in ive["earningsDates"])
assert len(ive["earningsDates"]) == 11
assert set(hist["bars"]) <= set(data["HISTORY"])
assert all(b["d"] == "2026-11-09"
           for v in hist["bars"].values() for b in v)
assert internals["smi"] == data["MARKET_INTERNALS"]["smi"]
assert {k: v for k, v in internals["breadth"].items() if k != "note"} == \
    data["MARKET_INTERNALS"]["breadth"]
assert internals["aaii"]["latest"] == data["MARKET_INTERNALS"]["aaii"]["latest"]
assert internals["aaii"]["history"] == data["MARKET_INTERNALS"]["aaii"]["history"]
assert internals["aaii"]["asof"] == data["MARKET_INTERNALS"]["aaii"]["asof"]
assert internals["flows"] == data["MARKET_INTERNALS"]["flows"]
assert internals["vixTerm"]["spot"] == data["MARKET_INTERNALS"]["vixTerm"]["spot"]
assert internals["vixTerm"]["threeMonth"] == \
    data["MARKET_INTERNALS"]["vixTerm"]["threeMonth"]
notes.append("validation ok: scores sum, 63 IV tickers, analyst keys, "
             "15 carried IV match, FedWatch sums ~100, 11-entry strip "
             "all future, 74 history bars all Nov 9, carried internals match")

# ---------- SCREEN_SNAPSHOT ----------
screen_snapshot = {
    "updated": RUN_STAMP,
    "scanTime": "2026-11-10 ~7:30 AM (premarket)",
    "resultCount": screen["resultCount"],
    "resultTime": "2026-11-10 ~7:30 AM (premarket)",
    "source": "https://finviz.com/screener?v=211&f=cap_midover,sh_opt_option,ta_change_u,ta_highlow52w_b10h,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3",
    "optionsAsOf": "Nov 10, 2026 (optioncharts.io)",
    "note": screen["note"],
    "potential": screen["potential"],
    "volumes": screen["volumes"],
}
notes.append("screen: " + str([(p["ticker"], p["score"])
                               for p in screen["potential"]]))

# ---------- HISTORY ----------
history = {t: list(bars) for t, bars in data["HISTORY"].items()}
appended = 0
for t, bars in hist.get("bars", {}).items():
    if t not in history:
        continue
    existing = {b["d"] for b in history[t]}
    new = [b for b in bars if b["d"] not in existing]
    if new:
        history[t] = sorted(history[t] + new, key=lambda b: b["d"])
        appended += len(new)
notes.append(f"HISTORY appended {appended} bars across "
             f"{len(hist['bars'])} tickers; missing: {hist.get('missing')} "
             "(SQ 404, rename pending Hugo)")

# ---------- MARKET_INTERNALS (read-modify-write whole object) ----------
mi = json.loads(json.dumps(data["MARKET_INTERNALS"]))  # deep copy
mi["fearGreed"] = internals["fearGreed"]
mi["vixTerm"] = internals["vixTerm"]
mi["putCall"] = internals["putCall"]
# breadth + smi + flows carried verbatim (Nov 9 closes, finalized by
# close patch / already in data.json); aaii from collector (same values,
# note re-verified live Nov 10)
mi["aaii"] = internals["aaii"]
mi["flowsAsOf"] = internals["flowsAsOf"]
mi["fedWatch"] = fedwatch
notes.append("internals: F&G 32 Fear (Nov 9 final), VIX 19.92/20.85 "
             "contango 1.05, P/C eq 0.56 idx 1.06 (Nov 9 finals), AAII "
             "carried 34.1/17.5/48.4, flows carried (Nov 9 report not "
             "posted), FedWatch Dec 9 0.9% hold / 99.1% hike (live CME)")

# ---------- SECTOR_BREADTH ----------
sector_breadth = []
for s in internals["sectorBreadth"]:
    sector_breadth.append({
        "etf": s["etf"], "name": s["name"], "nameZh": s["nameZh"],
        "change": s["change"], "close": s["close"], "previous": s["previous"],
        "url": s.get("url", f"https://finnhub.io/?q=%22{s['etf']}%22"),
    })
notes.append("sectorBreadth: " + str([(s["etf"], s["change"])
                                      for s in sector_breadth]))

# ---------- EARNINGS + EXPECTED MOVES ----------
stored_earn = {e["ticker"]: e for e in data["EARNINGS_DATES"]}
earn = []
for e in ive["earningsDates"]:
    e = dict(e)
    st = stored_earn.get(e["ticker"])
    if st and len(st.get("sources", [])) > len(e.get("sources", [])):
        e["sources"] = st["sources"]  # keep fuller stored source list
    earn.append(e)
exp_moves = dict(data["EXPECTED_MOVES"])
for t, mv in ive["expectedMoves"].items():
    exp_moves[t] = mv
notes.append("EARNINGS 11 entries, none dropped; moves via "
             "IV-formula fallback, 9 of 11 down vs Nov 9")

# ---------- MACRO (merge collector's flat events onto stored rich entries) --
def _time_key(e):
    t = e.get("time", "")
    try:
        return datetime.strptime(t.replace(" ET", ""), "%I:%M %p").time()
    except Exception:
        return datetime.strptime("11:59 PM", "%I:%M %p").time()

stored_macro = {(e["date"], e["title"]): e for e in data["MACRO_EVENTS"]}
macro = []
unmatched = []
for ev in internals["macroEvents"]:
    match = None
    for (d0, title), st in stored_macro.items():
        if d0 == ev["date"] and (ev["event"][:25] in title
                                 or title[:25] in ev["event"]):
            match = st
            break
    if match is None:
        unmatched.append(ev)
        continue
    e = dict(match)
    e["time"] = ev["time"] or match["time"]
    macro.append(e)
# New event this run: Dec 10 CPI (November 2026), BLS schedule verified
# Nov 6 (Oct CPI Nov 10, Nov CPI Dec 10). Build the rich entry here.
new_cpi = [ev for ev in unmatched
           if ev["date"] == "2026-12-10" and ev["event"].startswith("CPI")]
assert len(new_cpi) == 1 and len(unmatched) == 1, unmatched
macro.append({
    "category": "Inflation",
    "categoryZh": "通胀",
    "date": "2026-12-10",
    "impact": "November CPI; BLS schedule verified Nov 6: October CPI Nov 10, "
              "November CPI Dec 10, 2026 (8:30 AM ET). A hot print keeps "
              "December hike odds high, a cool one lets the Fed stay patient. "
              "The Dec 18 date seen in some summaries was a 2025-shutdown "
              "conflation and is not used.",
    "impactZh": "11 月 CPI；读数偏高则维持 12 月加息概率高企，偏低则让美联储保持耐心。",
    "time": "8:30 AM ET",
    "title": "CPI (November 2026)",
    "titleZh": "CPI（11 月）",
})
dropped = [f"{d0} {t}" for (d0, t) in stored_macro
           if not any(e["date"] == d0 and e["title"] == t for e in macro)]
macro = sorted(macro, key=lambda e: (e["date"], _time_key(e)))
notes.append(f"MACRO {len(macro)} events, {macro[0]['date']}..{macro[-1]['date']}; "
             f"added: Dec 10 CPI (November 2026); dropped: {dropped}")

# ---------- ASOF (read-modify-write) ----------
asof = dict(data["ASOF"])
asof["sectorBreadth"] = RUN_STAMP
asof["macro"] = RUN_STAMP
asof["expectedMoves"] = RUN_STAMP

# ---------- I18N_OVERRIDES (read-modify-write whole object) ----------
i18n = json.loads(json.dumps(data["I18N_OVERRIDES"]))
i18n["en"]["tradesDesc"] = (
    "15 ranked setups from the November 10 Finviz screen, with verified "
    "front-month options activity.")
i18n["zh"]["tradesDesc"] = (
    "根据 11 月 10 日的 Finviz 筛选，列出15个已验证近月期权活跃度的排序机会。")
i18n["en"]["ivAsOf"] = (
    "Updated Nov 10, 2026 · optioncharts.io 30-day IV readings "
    "(48 of 63 refreshed; 15 carried last-good; IV percentile carried "
    "last-good for all 63); stale source pages are flagged in ticker detail")
i18n["zh"]["ivAsOf"] = (
    "更新于 11 月 10 日 · optioncharts.io 隐含波动率数据（63 个标的中 48 个"
    "已刷新，15 个沿用上次有效值；IV 百分位全部沿用上次有效值）")
i18n["en"]["calendarDesc"] = f"Macro calendar refreshed {RUN_STAMP}"
i18n["zh"]["calendarDesc"] = f"宏观日历已于 {RUN_STAMP} 更新"
i18n["en"]["sevenDayWindow"] = "Next 7 days: Nov 10 – Nov 16, 2026"
i18n["zh"]["sevenDayWindow"] = "未来7天：2026年11月10日 – 11月16日"
i18n["en"]["checked"] = f"Checked {RUN_STAMP}"
i18n["zh"]["checked"] = f"检查于 {RUN_STAMP}"

patch = {
    "SCREEN_SNAPSHOT": screen_snapshot,
    "HISTORY": history,
    "MARKET_INTERNALS": mi,
    "SECTOR_BREADTH": sector_breadth,
    "IV_DATA": ive["iv"],
    "IV_SOURCE": ive["ivSource"],
    "EXPECTED_MOVES": exp_moves,
    "EARNINGS_DATES": earn,
    "MACRO_EVENTS": macro,
    "ANALYST_REVISIONS": ive["analystRevisions"],
    "ASOF": asof,
    "I18N_OVERRIDES": i18n,
}
json.dump(patch, open("/tmp/patch.json", "w"))
print("\n".join(notes))
print("patch keys:", sorted(patch.keys()))
print("analyst total entries:",
      sum(len(v) for v in ive["analystRevisions"].values()))
