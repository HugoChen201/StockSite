#!/usr/bin/env python3
"""Morning-refresh patch builder for StockSite data.json (Tue 2026-11-17).

Collectors (all verified by the parent run):
- Finviz screen: v=211 shell-only again, v=111 Overview used, 37 results
  (down from 86 Nov 16). 12 ranked. relVolume null for all (premarket
  volume is partial-session). Six names unranked (RGLD, CEG, CVNA, AON,
  ARGX, MMS): optioncharts 429, recorded as unknown in the screen note.
- History: Yahoo daily chart API direct, Nov 16 bars for 74 of 75 HISTORY
  tickers. SQ missing: Yahoo 404 -- Block renamed SQ -> XYZ; NO rename
  applied (pending Hugo).
- Internals: F&G 31 Fear Nov 16 (mirror CSV 31.02; CNN JSON 418
  bot-blocked; mirror runs below CNN officials, Nov 13 mirror 37.37 vs
  CNN 39, so 31 is mirror-derived/approximate); VIX 22.91 / VIX3M 23.02
  Nov 16 closes verified vs stored (Yahoo), ratio 1.00 contango (flat);
  put/call Nov 16 finals eq 0.73 idx 1.01 total 0.95 (equity + index
  verified by direct ycharts page fetch Nov 17 ~7:45 AM ET; total via
  ycharts search index, total page fetch failed); AAII carried (week
  ending Nov 11: 30.8/17.8/51.4; next week ends Nov 18); flows: NEW
  Nov 13 session (ETF Action posted Nov 16, T+1) SPY -$6.13B / QQQ
  +$5.16B / IWM not reported today; sector breadth Yahoo Nov 16 FINAL
  closes (XLK -3.24% worst, XLP +0.27% top, SPY -1.91%) — parent verified
  vs Yahoo chart API: stored close-patch values were a 3:55 PM pre-close
  snapshot, Yahoo daily closes used instead; SMI carried 999.19
  (finalized through Nov 16 by close patch).
- Breadth (live browser, fresh read Nov 17 ~7:30 AM ET): A/D ratio 0.32,
  A/D diff -929.00, % above 50-day 65.00 (prev 71.37), % above 200-day
  59.84 (prev 63.81), all Nov 16 closes confirmed via Price History.
  52-wk highs/lows from the highs-lows Summary tab: NYSE 31/129, Nasdaq
  29/427, Overall 62/605 — NOT strictly comparable to prior days'
  newhilo.php daily-table counts.
- FedWatch: LIVE CME FedWatch page via browser (data as of 06:20 CT
  Nov 17). Dec 9: hold 0.0%, one hike 95.4% (was 93.4%), 50bp tail 4.6%
  (was 6.6%). EFFR carried 3.88 (not shown on page). Same 8 meeting tabs
  ending Nov 17, 2027 as Nov 16.
- Macro: 29 events, rich format straight from the collector. Nov 16
  events dropped; ADDED Michigan final Nov 20, ISM Manufacturing Dec 1,
  ADP Dec 2, ISM Services Dec 3, Michigan prelim Dec 4, Productivity &
  Costs Dec 8, Existing-Home Sales Dec 9, Michigan final Dec 18.
- IV: optioncharts.io overview pages, 62 of 63 refreshed (30-day IV + IV
  rank; IV percentile carried last-good for all 63 -- text fetch exposes
  IV/rank only). 1 carried: SQ (Sahakol page). 10 tickers recovered by a
  parent curl retry pass after the collectors hit upstream 429s (CRM,
  CRWV, CVX, DELL, UBER, UNH, VRT, WDC, WMT, XOM) — parsed from the
  IV Rank stat box (first loose-regex pass wrongly matched the IV(30d)
  gauge value and was discarded). NOTE: optioncharts pages DO display an
  IV Percentile figure (e.g. WMT 96.81% vs stored 98.01%); percentile was
  still carried last-good for all 63 per the standing method — flag for a
  future method check. BRK-B via BRKB.
- Expected moves: recomputed here from MERGED fresh IV (IV-formula
  fallback: 30-day IV x sqrt(DTE/365) to the Friday weekly expiry).
  Strip: 12 entries, no drops, no adds. HD + NVDA report TODAY (Nov 17).
- Analyst: 45 new items (NVDA x10, WMT x8, NBIS x4, HD x3, AMD x3,
  AMAT x2, TSLA x2, DELL x2, CRM x2, XOM x2, AVGO/LLY/COST/ADBE/AAPL/
  PLTR/CRWV x1), dated Nov 2-17; stored rest carried. Total 1,010 items
  (was 965). CORRECTION applied here: stored HD Stifel Oct 26 item said
  "maintained Buy rating — PT $346 → $322"; MarketBeat + FundSpec both
  list it as Hold, PT $346 → $322 — fixed to "(Hold maintained)" with a
  MarketBeat source.
"""
import json
import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())
screen = json.loads((HID / "screen_2026-11-17.json").read_text())
internals = json.loads((HID / "internals_2026-11-17.json").read_text())
fedwatch = json.loads((HID / "fedwatch_2026-11-17.json").read_text())
ivb = json.loads((HID / "iv_part_b_2026-11-17.json").read_text())
ivc = json.loads((HID / "iv_part_c_ivonly_2026-11-17.json").read_text())
ivc2 = json.loads((HID / "iv_part_c_2026-11-17.json").read_text())
yahoo = json.loads((HID / "yahoo_2026-11-17.json").read_text())
retry = json.loads(Path("/tmp/iv_retry_2026-11-17.json").read_text())

RUN_STAMP = datetime.now(ZoneInfo("America/New_York")).strftime(
    "%b %-d, %Y %-I:%M %p ET").replace("  ", " ")
notes = [f"RUN_STAMP={RUN_STAMP}"]

# ---------- merge IV (retry pass recovers the 429-carried tickers) ----------
iv = dict(ivb["iv"])
iv.update(ivc["iv"])
assert set(retry) == {"CRM", "CRWV", "CVX", "DELL", "UBER", "UNH",
                      "VRT", "WDC", "WMT", "XOM"}, set(retry)
for t, v in retry.items():
    iv[t] = {"iv30": v["iv30"],
             "percentile": data["IV_DATA"][t]["percentile"],
             "rank": v["rank"]}
ivb_carried = [c["ticker"] for c in ivb["carried"]]
ivc_carried = [c["ticker"] if isinstance(c, dict) else c
               for c in ivc["carried"]]
CARRIED_IV = sorted((set(ivb_carried) | set(ivc_carried)) - set(retry))
REFRESHED_N = len(ivb["refreshed"]) + len(ivc["refreshed"]) + len(retry)

# ---------- validation ----------
for p in screen["potential"]:
    assert p["score"] == sum(p["components"].values()), p["ticker"]
    assert set(p["components"]) == {"relativeVolume", "distanceFromHigh",
        "optionLiquidity", "catalyst", "trendStructure"}
    assert set(p.keys()) == {"change", "changePct", "components",
        "distanceFromHigh", "nearHighPct", "note", "optionOI",
        "optionVolume", "price", "relVolume", "score", "ticker",
        "volume", "why"}, p["ticker"]
assert screen["resultCount"] == 37
assert len(screen["potential"]) == 12
assert set(iv) == {s["ticker"] for s in data["STOCKS"]}, \
    set(iv) ^ {s["ticker"] for s in data["STOCKS"]}
assert set(ivc2["analystRevisions"]) == {s["ticker"] for s in data["STOCKS"]}
assert REFRESHED_N == 62, REFRESHED_N
assert CARRIED_IV == ["SQ"], CARRIED_IV
assert iv["SQ"] == data["IV_DATA"]["SQ"]
assert all(v["rank"] <= 100 for v in iv.values()), \
    [t for t, v in iv.items() if v["rank"] > 100]
assert all(v["iv30"] > 0 for v in iv.values())
for m in fedwatch["meetings"]:
    assert abs(sum(o["pct"] for o in m["outcomes"]) - 100.0) < 0.5, m["decision"]
assert len(fedwatch["meetings"]) == 8
assert set(fedwatch.keys()) == {"asof", "context", "effr", "effrAsOf",
                                "meetings", "breadth"}
assert all(e["date"] >= "2026-11-17" for e in ivc2["earningsDates"])
assert len(ivc2["earningsDates"]) == 12
assert internals["smi"]["series"] == data["MARKET_INTERNALS"]["smi"]["series"]
assert internals["smi"]["latest"] == data["MARKET_INTERNALS"]["smi"]["latest"]
assert internals["aaii"]["latest"] == {"bullish": 30.8, "neutral": 17.8,
                                       "bearish": 51.4}
assert len(internals["aaii"]["history"]) == 4
macro = internals["macroEvents"]
assert len(macro) == 29, len(macro)
assert all(e["date"] >= "2026-11-17" for e in macro)
assert [e["date"] for e in macro] == sorted(e["date"] for e in macro)
for e in macro:
    assert set(e.keys()) == {"category", "categoryZh", "date", "impact",
                             "impactZh", "time", "title", "titleZh"}, e
assert set(yahoo["bars"].keys()) == set(data["HISTORY"]) - {"SQ"}
assert yahoo["missing"] == ["SQ"]
assert all(any(b["d"] == "2026-11-16" for b in v)
           for v in yahoo["bars"].values())
assert sum(len(v) for v in ivc2["analystRevisions"].values()) == 1010, \
    sum(len(v) for v in ivc2["analystRevisions"].values())
assert len(ivc2["newAnalystItems"]) == 45
# HD Stifel correction: stored item mis-rates it as Buy; MarketBeat +
# FundSpec both list Hold, PT $346 -> $322, Oct 26.
stifel = [i for i in ivc2["analystRevisions"]["HD"]
          if i["firm"] == "Stifel" and i["date"] == "2026-10-26"]
assert len(stifel) == 1 and stifel[0]["action"] == \
    "maintained Buy rating — PT $346 → $322", stifel
notes.append("validation ok: scores sum, 63 IV tickers, analyst keys, "
             "62 refreshed / 1 carried (SQ), no rank >100, FedWatch "
             "8 meetings sum ~100, 12-entry strip all future, SMI carried, "
             "AAII carried 30.8/17.8/51.4, macro 29 rich entries sorted "
             "Nov 17..Dec 23, yahoo 74 tickers with Nov 16 bars + SQ missing, "
             "analyst total 1010 (+45 new), HD Stifel mis-rate confirmed")

# ---------- HD Stifel correction ----------
ar = ivc2["analystRevisions"]
for i in ar["HD"]:
    if i["firm"] == "Stifel" and i["date"] == "2026-10-26":
        i["action"] = "lowered price target — PT $346 → $322 (Hold maintained)"
        i["source"] = ("MarketBeat HD forecast (Stifel Nicolaus, Oct 26, "
                       "2026: Lower Target, Hold, $346 → $322) — "
                       "https://www.marketbeat.com/stocks/NYSE/HD/forecast/ ; "
                       "FundSpec HD ratings table, same action")
        i["note"] = ("CORRECTED Nov 17, 2026: stored item mis-rated this as "
                     "'maintained Buy'; MarketBeat + FundSpec both list Hold")
notes.append("HD Stifel Oct 26 corrected Buy -> Hold, PT $346 -> $322")

# ---------- expected moves (recomputed from merged fresh IV) ----------
DTE = {"2026-11-17": ("2026-11-20", 3), "2026-11-19": ("2026-11-20", 3),
       "2026-11-24": ("2026-11-27", 10), "2026-12-01": ("2026-12-04", 17),
       "2026-12-02": ("2026-12-04", 17), "2026-12-09": ("2026-12-11", 24),
       "2026-12-10": ("2026-12-11", 24), "2026-12-14": ("2026-12-18", 31)}
exp_moves_new = {}
earn = []
for e in ivc2["earningsDates"]:
    e = dict(e)
    expiry, dte = DTE[e["date"]]
    mv = round(iv[e["ticker"]]["iv30"] * math.sqrt(dte / 365), 2)
    exp_moves_new[e["ticker"]] = mv
    e["expected_move"] = mv
    e["move_as_of"] = "Nov 17, 2026"
    e["move_method"] = (
        f"30-day IV × √(DTE/365) to Friday weekly expiry {expiry} "
        f"(DTE {dte} from Nov 17); optioncharts expiry-table % not readable "
        "in text fetch — IV-formula fallback per refresh rules")
    e["move_method_zh"] = "期权隐含预期波动（30日隐含波动率×√(DTE/365)）"
    st = next((x for x in data["EARNINGS_DATES"]
               if x["ticker"] == e["ticker"]), None)
    if st and len(st.get("sources", [])) > len(e.get("sources", [])):
        e["sources"] = st["sources"]  # keep fuller stored source list
    earn.append(e)
notes.append("expected moves recomputed from merged IV: " +
             str(exp_moves_new))

# ---------- SCREEN_SNAPSHOT ----------
screen_snapshot = {
    "updated": RUN_STAMP,
    "scanTime": "2026-11-17 ~7:30 AM (premarket)",
    "resultCount": screen["resultCount"],
    "resultTime": "2026-11-17 ~7:30 AM (premarket)",
    "source": "https://finviz.com/screener?v=211&f=cap_midover,sh_opt_option,ta_change_u,ta_highlow52w_b10h,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3",
    "optionsAsOf": "Nov 17, 2026 (optioncharts.io)",
    "note": screen["note"],
    "potential": screen["potential"],
    "volumes": screen["volumes"],
}
notes.append("screen: " + str([(p["ticker"], p["score"])
                               for p in screen["potential"]]))

# ---------- HISTORY (Nov 16 bars only) ----------
hist_bars = {}
for t in data["HISTORY"]:
    bars = [b for b in yahoo["bars"].get(t, []) if b["d"] == "2026-11-16"]
    if bars:
        hist_bars[t] = bars
assert all(b["d"] == "2026-11-16"
           for v in hist_bars.values() for b in v)
history = {t: list(bars) for t, bars in data["HISTORY"].items()}
appended = 0
for t, bars in hist_bars.items():
    existing = {b["d"] for b in history[t]}
    new = [b for b in bars if b["d"] not in existing]
    if new:
        history[t] = sorted(history[t] + new, key=lambda b: b["d"])
        appended += len(new)
notes.append(f"HISTORY appended {appended} bars across "
             f"{len(hist_bars)} tickers; missing: SQ (Yahoo 404, rename "
             "pending Hugo)")

# ---------- MARKET_INTERNALS (read-modify-write whole object) ----------
mi = json.loads(json.dumps(data["MARKET_INTERNALS"]))  # deep copy
mi["fearGreed"] = internals["fearGreed"]
mi["vixTerm"] = internals["vixTerm"]
pc = internals["putCall"]
# Equity + index verified by direct ycharts page fetch this morning
# (Nov 16: eq 0.73, idx 1.01, both match the collector's values).
pc["asof"] = ("Nov 16, 2026 finals (ycharts; equity + index verified by "
              "direct page fetch Nov 17 ~7:45 AM ET — Nov 16 eq 0.73, idx "
              "1.01; total 0.95 corroborated by the ycharts search index of "
              "the I:CBOETPCR page (ycharts.com/indicators/"
              "total_putcall_ratio); the guessed total-page slug 404s)")
mi["putCall"] = pc
mi["breadth"] = fedwatch["breadth"]  # live-browser Nov 16 closes
mi["aaii"] = internals["aaii"]  # carried, week ending Nov 11
mi["flows"] = internals["flows"]  # NEW Nov 13 session
mi["flowsAsOf"] = internals["flowsAsOf"]
mi["fedWatch"] = {k: fedwatch[k] for k in
                  ("asof", "context", "effr", "effrAsOf", "meetings")}
notes.append("internals: F&G 31 Fear (Nov 16, mirror CSV 31.02 — "
             "mirror-derived, CNN official still 418-blocked), VIX 22.91/"
             "23.02 contango (flat) 1.00, P/C eq 0.73 idx 1.01 total 0.95 "
             "(Nov 16 finals), AAII carried 30.8/17.8/51.4, flows NEW Nov 13 "
             "session SPY -6.13/QQQ +5.16/IWM not reported, breadth A/D "
             "0.32/-929, %>50d 65.00 %>200d 59.84, FedWatch 8 meetings Dec 9 "
             "hike 95.4% / 50bp 4.6% (live CME)")

# ---------- SECTOR_BREADTH ----------
sector_breadth = []
for s in internals["sectorBreadth"]:
    sector_breadth.append({
        "etf": s["etf"], "name": s["name"], "nameZh": s["nameZh"],
        "change": s["change"], "close": s["close"], "previous": s["previous"],
        "url": s.get("url", f"https://finnhub.io/?q=%22{s['etf']}%22"),
    })
notes.append("sectorBreadth (Nov 16 finals, Yahoo daily closes): " +
             str([(s["etf"], s["change"]) for s in sector_breadth]))

# ---------- IV_SOURCE ----------
iv_source = (
    "Nov 17, 2026 · 62 of 63 refreshed from optioncharts.io (live overview "
    "pages, Nov 16 close data; 30-day IV and IV rank refreshed; IV percentile "
    "carried last-good for all 63 — the text fetch exposes 30-day IV and IV "
    "rank only, not percentile); 1 carried last-good: SQ (optioncharts still "
    "shows unrelated Sahakol Equipment, stale Oct 16 crawl; Block now XYZ "
    "there, not applied pending the ticker-rename decision). 10 tickers "
    "recovered by a parent retry pass after the collectors hit upstream 429 "
    "rate limits (CRM, CRWV, CVX, DELL, UBER, UNH, VRT, WDC, WMT, XOM). "
    "BRK-B refreshed via the BRKB page. NOTE: the optioncharts pages also "
    "display an IV Percentile figure (e.g. WMT 96.81% vs stored 98.01%); "
    "percentile was still carried last-good for all 63 per the standing "
    "method — flag for a future method check.")

# ---------- EXPECTED_MOVES ----------
exp_moves = dict(data["EXPECTED_MOVES"])
for t, mv in exp_moves_new.items():
    exp_moves[t] = mv

# ---------- MACRO (rich entries straight from collector) ----------
stored_macro = {(e["date"], e["title"]) for e in data["MACRO_EVENTS"]}
new_macro = {(e["date"], e["title"]) for e in macro}
added = sorted(new_macro - stored_macro)
dropped = sorted(stored_macro - new_macro)
notes.append(f"MACRO {len(macro)} events, {macro[0]['date']}..{macro[-1]['date']}; "
             f"added: {added}; dropped: {dropped}")

# ---------- ASOF (read-modify-write) ----------
asof = dict(data["ASOF"])
asof["sectorBreadth"] = RUN_STAMP
asof["macro"] = RUN_STAMP
asof["expectedMoves"] = RUN_STAMP

# ---------- I18N_OVERRIDES (read-modify-write whole object) ----------
i18n = json.loads(json.dumps(data["I18N_OVERRIDES"]))
i18n["en"]["tradesDesc"] = (
    "12 ranked setups from the November 17 Finviz screen, with verified "
    "front-month options activity.")
i18n["zh"]["tradesDesc"] = (
    "根据 11 月 17 日的 Finviz 筛选，列出12个已验证近月期权活跃度的排序机会。")
i18n["en"]["ivAsOf"] = (
    "Updated Nov 17, 2026 · optioncharts.io 30-day IV readings "
    "(62 of 63 refreshed; 1 carried last-good; IV percentile carried "
    "last-good for all 63); stale source pages are flagged in ticker detail")
i18n["zh"]["ivAsOf"] = (
    "更新于 11 月 17 日 · optioncharts.io 隐含波动率数据（63 个标的中 62 个"
    "已刷新，1 个沿用上次有效值；IV 百分位全部沿用上次有效值）")
i18n["en"]["calendarDesc"] = f"Macro calendar refreshed {RUN_STAMP}"
i18n["zh"]["calendarDesc"] = f"宏观日历已于 {RUN_STAMP} 更新"
i18n["en"]["sevenDayWindow"] = "Next 7 days: Nov 17 – Nov 23, 2026"
i18n["zh"]["sevenDayWindow"] = "未来7天：2026年11月17日 – 11月23日"
i18n["en"]["checked"] = f"Checked {RUN_STAMP}"
i18n["zh"]["checked"] = f"检查于 {RUN_STAMP}"

patch = {
    "SCREEN_SNAPSHOT": screen_snapshot,
    "HISTORY": history,
    "MARKET_INTERNALS": mi,
    "SECTOR_BREADTH": sector_breadth,
    "IV_DATA": iv,
    "IV_SOURCE": iv_source,
    "EXPECTED_MOVES": exp_moves,
    "EARNINGS_DATES": earn,
    "MACRO_EVENTS": macro,
    "ANALYST_REVISIONS": ar,
    "ASOF": asof,
    "I18N_OVERRIDES": i18n,
}
json.dump(patch, open("/tmp/patch.json", "w"))
print("\n".join(notes))
print("patch keys:", sorted(patch.keys()))
print("analyst total entries:",
      sum(len(v) for v in ar.values()))
