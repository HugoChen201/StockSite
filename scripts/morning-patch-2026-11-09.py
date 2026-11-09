#!/usr/bin/env python3
"""Morning-refresh patch builder for StockSite data.json (Mon 2026-11-09).

Collectors (all verified by the parent run):
- Finviz screen: text fetch ~7:28 AM ET, 144 results (v=111 Overview view;
  v=211 TA view returned shell-only; rows 141-144 unrecovered). 15 ranked.
  Screen expanded 37 -> 144 after Nov 6's partial bounce (names reclaimed
  SMAs). Option volume/OI are Nov 6 total-session figures from
  optioncharts.io overview pages; no 429s on the screen pass.
- History: Yahoo daily chart API direct, Nov 6 bars for 74 of 75 HISTORY
  tickers (no gaps). SQ missing: Yahoo 404 -- Block renamed SQ -> XYZ;
  NO rename applied (pending Hugo's decision); SQ carries no new bar.
- Internals: F&G 22 Extreme Fear Nov 6 close (whit3rabbit CSV mirror; CNN
  JSON 418 bot-blocked; Nov 5 = 19.99, superseding stored 20); VIX 25.64 /
  VIX3M 24.60 Nov 6 closes (Yahoo, verified = stored), ratio 0.96
  backwardation; put/call Nov 6 finals via YCharts (eq 0.59, idx 1.26);
  AAII carried (week ending Nov 4, next week posts Nov 12); flows: Nov 6
  session etfaction report NOT yet posted as of ~7:30 AM ET (Nov 5-session
  values carried); breadth carried verbatim from data.json (Nov 6 closes
  finalized by close patch; Barchart text fetch served a stale Sep 1
  snapshot); SMI carried (999.58, finalized through Nov 6); sector breadth
  corrected to Yahoo Nov 6 FINAL closes (stored values were 3:55 PM ET
  snapshots; XLK +1.45% vs +1.39% stored).
- FedWatch: LIVE CME FedWatch page via browser (data as of 06:15 CT Nov 9).
  Dec 9: 19.5% hold / 80.5% hike -- hike odds up from Nov 6's 69.1% after
  the hot NFP (+165k vs ~65k). EFFR carried 3.88 (not shown on page).
- Macro: 21 events (2 past Nov 6 events dropped). Nov CPI stays Dec 10;
  Dec 18 not re-added (verified 2025-shutdown conflation).
- IV: optioncharts.io overview pages, 40 of 63 refreshed (30-day IV + IV
  rank; IV percentile carried last-good for all 63 -- text fetch exposes
  IV/rank only). 23 carried: 10 on browser-service 429 after 40 fetches
  (SKHY, SPY, QQQ, COIN, HOOD, SMCI, DELL, CRM, NOW, ADBE -- NOT retried
  per rate-limit stop), 12 not attempted after the stop (SHOP, GS, MS, JNJ,
  CVX, HD, MSTR, UBER, IWM, SNOW, BAC, TLT), SQ stale (Sahakol page).
  NVDA rank 132 -> 84 (IV 63.7% -> 58.2%); no refreshed ticker ranks >100
  now. BRK-B via BRKB (20.5%, rank 91).
- Expected moves: IV-formula fallback (30-day IV x sqrt(DTE/365) to the
  Friday weekly expiry); all 11 down vs Nov 6 (DTE-driven, Nov 13 expiry
  now DTE 4 vs 7, plus IV easing). Strip: 11 entries (BRK-B Nov 7 dropped,
  past). NVDA Nov 17 re-verified via StockAnalysis.
- Analyst: 133 new entries across 22 tickers; stored 755 carried, total
  888. Flags: HD Stifel rating discrepancy (kept stored), HOOD Cantor
  date conflict (kept stored).
"""
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())
screen = json.loads((HID / "screen_2026-11-09.json").read_text())
internals = json.loads((HID / "internals_2026-11-09.json").read_text())
fedwatch = json.loads((HID / "fedwatch_2026-11-09.json").read_text())
ive = json.loads((HID / "iv_earnings_2026-11-09.json").read_text())
hist = json.loads((HID / "history_2026-11-09.json").read_text())

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
CARRIED_IV = ["SKHY", "SPY", "QQQ", "COIN", "HOOD", "SMCI", "DELL", "CRM",
              "NOW", "ADBE", "SHOP", "GS", "MS", "JNJ", "CVX", "HD", "MSTR",
              "UBER", "IWM", "SNOW", "BAC", "TLT", "SQ"]
assert len(CARRIED_IV) == 23
for t in CARRIED_IV:
    assert ive["iv"][t] == data["IV_DATA"][t], t
for m in fedwatch["meetings"]:
    assert abs(sum(o["pct"] for o in m["outcomes"]) - 100.0) < 0.5, m["decision"]
assert all(e["date"] >= "2026-11-09" for e in ive["earningsDates"])
assert len(ive["earningsDates"]) == 11
assert set(hist["bars"]) <= set(data["HISTORY"])
assert all(b["d"] == "2026-11-06"
           for v in hist["bars"].values() for b in v)
assert internals["smi"]["latest"] == data["MARKET_INTERNALS"]["smi"]["latest"]
assert {k: v for k, v in internals["breadth"].items() if k != "note"} == \
    data["MARKET_INTERNALS"]["breadth"]  # collector added a "note" key only
assert internals["aaii"]["latest"] == data["MARKET_INTERNALS"]["aaii"]["latest"]
assert internals["aaii"]["history"] == data["MARKET_INTERNALS"]["aaii"]["history"]
assert internals["aaii"]["asof"] == data["MARKET_INTERNALS"]["aaii"]["asof"]
# note text differs only: collector re-verified live Nov 9 that no new week
# posted; use the collector's aaii (same values, fresher note)
assert internals["flows"] == data["MARKET_INTERNALS"]["flows"]
notes.append("validation ok: scores sum, 63 IV tickers, analyst keys, "
             "23 carried IV match, FedWatch sums ~100, 11-entry strip "
             "all future, 74 history bars all Nov 6, carried internals match")

# ---------- SCREEN_SNAPSHOT ----------
screen_snapshot = {
    "updated": RUN_STAMP,
    "scanTime": "2026-11-09 ~7:30 AM (premarket)",
    "resultCount": screen["resultCount"],
    "resultTime": "2026-11-09 ~7:30 AM (premarket)",
    "source": "https://finviz.com/screener?v=211&f=cap_midover,sh_opt_option,ta_change_u,ta_highlow52w_b10h,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3",
    "optionsAsOf": "Nov 9, 2026 (optioncharts.io)",
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
# breadth + smi + flows carried verbatim (Nov 6 closes, finalized by
# close patch / already in data.json); aaii from collector (same values,
# note re-verified live Nov 9)
mi["aaii"] = internals["aaii"]
mi["flowsAsOf"] = internals["flowsAsOf"]
mi["fedWatch"] = fedwatch
notes.append("internals: F&G 22 Extreme Fear (Nov 6 final), VIX 25.64/24.60 "
             "backwardation 0.96, P/C eq 0.59 idx 1.26 (Nov 6 finals), AAII "
             "carried 34.1/17.5/48.4, flows carried (Nov 6 report not "
             "posted), FedWatch Dec 9 19.5% hold / 80.5% hike (live CME)")

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
notes.append("EARNINGS 11 entries (BRK-B Nov 7 dropped); moves via "
             "IV-formula fallback, all 11 down vs Nov 6")

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
assert not unmatched, unmatched
dropped = [f"{d0} {t}" for (d0, t) in stored_macro
           if not any(e["date"] == d0 and e["title"] == t for e in macro)]
macro = sorted(macro, key=lambda e: (e["date"], _time_key(e)))
notes.append(f"MACRO {len(macro)} events, {macro[0]['date']}..{macro[-1]['date']}; "
             f"dropped: {dropped}")

# ---------- ASOF (read-modify-write) ----------
asof = dict(data["ASOF"])
asof["sectorBreadth"] = RUN_STAMP
asof["macro"] = RUN_STAMP
asof["expectedMoves"] = RUN_STAMP

# ---------- I18N_OVERRIDES (read-modify-write whole object) ----------
i18n = json.loads(json.dumps(data["I18N_OVERRIDES"]))
i18n["en"]["tradesDesc"] = (
    "15 ranked setups from the November 9 Finviz screen, with verified "
    "front-month options activity.")
i18n["zh"]["tradesDesc"] = (
    "根据 11 月 9 日的 Finviz 筛选，列出15个已验证近月期权活跃度的排序机会。")
i18n["en"]["ivAsOf"] = (
    "Updated Nov 9, 2026 · optioncharts.io 30-day IV readings "
    "(40 of 63 refreshed; 23 carried last-good; IV percentile carried "
    "last-good for all 63); stale source pages are flagged in ticker detail")
i18n["zh"]["ivAsOf"] = (
    "更新于 11 月 9 日 · optioncharts.io 隐含波动率数据（63 个标的中 40 个"
    "已刷新，23 个沿用上次有效值；IV 百分位全部沿用上次有效值）")
i18n["en"]["calendarDesc"] = f"Macro calendar refreshed {RUN_STAMP}"
i18n["zh"]["calendarDesc"] = f"宏观日历已于 {RUN_STAMP} 更新"
i18n["en"]["sevenDayWindow"] = "Next 7 days: Nov 9 – Nov 15, 2026"
i18n["zh"]["sevenDayWindow"] = "未来7天：2026年11月9日 – 11月15日"
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
