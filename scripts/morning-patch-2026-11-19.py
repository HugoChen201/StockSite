#!/usr/bin/env python3
"""Morning-refresh patch builder for StockSite data.json (Thu 2026-11-19).

Collectors (all verified by the parent run):
- Finviz screen: v=211 shell-only again, v=111 Overview used, 59 results
  across 3 pages. 15 ranked (PANW 89 top on Q1 FY27 beat + guide raise,
  CRWD 86, OKTA 83). relVolume null for all (premarket volume is
  partial-session); relVol scored from %chg+avg-vol tier. Unranked thin
  chains: FBIN, TDC. No optioncharts 429s on screen checks. No SPCX.
- History: Yahoo daily chart API direct, Nov 18 bars. 74 tickers; SQ
  missing expected (Yahoo 404; Block renamed SQ -> XYZ; NO rename).
- Internals: F&G 25 Extreme Fear Nov 18 close (CNN JSON 418-blocked;
  corroborated by Nov 18 close patch live read + mirror CSV 24.61);
  VIX 24.56 / VIX3M 24.29, ratio 0.99 backwardation (Yahoo closes
  verified); put/call Nov 18 finals eq 0.72 idx 1.14 total 1.05
  (ycharts, read Nov 19 ~7:35 AM ET); AAII NEW week ending Nov 18:
  33.3/24.4/42.2 (was 30.8/17.8/51.4); flows carried Nov 17 session
  (SPY +$6.73B, QQQ -$1.65B, IWM -$0.25B Nov 16) — Nov 18-session ETF
  Action report NOT yet posted; sector breadth Yahoo Nov 18 FINAL closes
  (XLY +1.79% best, XLE -3.27% worst); SMI carried 999.81 (finalized
  through Nov 18).
- Breadth (live browser, fresh read Nov 19 ~7:31 AM ET): $ADRN 0.88,
  $ADDN -115 (close patch stored -117 from a 16:57 ET snapshot; later
  read used), % above 50-day 56.26 (prev 57.85), % above 200-day 56.06
  (prev stored 56.06; page's own prev-close field printed 57.25,
  flagged as inconsistent), all Nov 18 closes. 52-wk highs/lows from
  the highs-lows Summary tab (Last Updated 11/18 19:42 ET): Overall
  43/601, NYSE 19/167, Nasdaq 23/393, Arca 1/41 — quote-symbol set
  ($MALN 166) NOT used, per spec.
- FedWatch: LIVE CME FedWatch page via browser (data as of 06:15-06:20
  CT Nov 19; Akamai block cleared by fresh-browser move). Dec 9 hike
  now 100%: one hike 400-425 at 90.7% (was 96.7%), 50bp tail 9.3%
  (was 3.3%). EFFR not shown on page again — carried 3.88. Same 8
  meeting tabs ending Nov 17, 2027.
- Macro: 35 events, Nov 19..Dec 23. Dropped Nov 18 Housing Starts +
  FOMC Minutes; ADDED Nov 19 Jobless Claims + LEI + Fed speakers
  Jefferson/Barr/Paulson, Nov 20 Cook/Waller, Nov 25 Durable Goods +
  New Home Sales, Dec 16 Retail Sales, Dec 17 Housing Starts.
- IV: optioncharts.io overview pages, 58 of 63 refreshed (30-day IV +
  IV rank; IV percentile carried last-good for all 63). 5 carried:
  LRCX/AMAT/TXN/KLAC (optioncharts 429 rate-limit on parallel batch,
  not retried), SQ (Sahakol page). SPY recovered (refreshed today).
  BRK-B via BRKB.
- Expected moves: recomputed here from MERGED fresh IV (IV-formula
  fallback: 30-day IV x sqrt(DTE/365) to the Friday weekly expiry).
  Strip: 11 entries unchanged — WMT reports today Nov 19 BMO (stays),
  no drops/adds.
- Analyst: 24 new items (NVDA x8 post-earnings, MSFT x7, HD x3, others),
  dated Nov 16-18; total 1,057 (was 1,033).
"""
import json
import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())
screen = json.loads((HID / "screen_2026-11-19.json").read_text())
internals = json.loads((HID / "internals_2026-11-19.json").read_text())
fedwatch = json.loads((HID / "fedwatch_2026-11-19.json").read_text())
iva = json.loads((HID / "iv_part_a_2026-11-19.json").read_text())
ivb = json.loads((HID / "iv_part_b_2026-11-19.json").read_text())
analyst = json.loads((HID / "analyst_2026-11-19.json").read_text())
yahoo = json.loads((HID / "yahoo_2026-11-19.json").read_text())

RUN_STAMP = datetime.now(ZoneInfo("America/New_York")).strftime(
    "%b %-d, %Y %-I:%M %p ET").replace("  ", " ")
notes = [f"RUN_STAMP={RUN_STAMP}"]

# ---------- merge IV ----------
iv = dict(iva["iv"])
iv.update(ivb["iv"])
assert not (set(iva["iv"]) & set(ivb["iv"])), "IV parts overlap"
CARRIED_IV = sorted(c["ticker"] for c in iva["carried"] + ivb["carried"])
assert CARRIED_IV == ["AMAT", "KLAC", "LRCX", "SQ", "TXN"], CARRIED_IV
REFRESHED_N = len(iva["refreshed"]) + len(ivb["refreshed"])

# ---------- validation ----------
for p in screen["potential"]:
    assert p["score"] == sum(p["components"].values()), p["ticker"]
    assert set(p["components"]) == {"relativeVolume", "distanceFromHigh",
        "optionLiquidity", "catalyst", "trendStructure"}
    assert set(p.keys()) == {"change", "changePct", "components",
        "distanceFromHigh", "nearHighPct", "note", "optionOI",
        "optionVolume", "price", "relVolume", "score", "ticker",
        "volume", "why"}, p["ticker"]
assert screen["resultCount"] == 59
assert len(screen["potential"]) == 15
assert set(iv) == {s["ticker"] for s in data["STOCKS"]}, \
    set(iv) ^ {s["ticker"] for s in data["STOCKS"]}
assert set(analyst["analystRevisions"]) == {s["ticker"] for s in data["STOCKS"]}
assert REFRESHED_N == 58, REFRESHED_N
for t in CARRIED_IV:
    assert iv[t] == data["IV_DATA"][t], t
assert all(v["rank"] <= 100 for v in iv.values()), \
    [t for t, v in iv.items() if v["rank"] > 100]
assert all(v["iv30"] > 0 for v in iv.values())
for m in fedwatch["meetings"]:
    assert abs(sum(o["pct"] for o in m["outcomes"]) - 100.0) < 0.5, m["decision"]
assert len(fedwatch["meetings"]) == 8
assert set(fedwatch.keys()) == {"asof", "context", "effr", "effrAsOf",
                                "meetings", "breadth"}
assert fedwatch["effr"] == 3.88
assert all(e["date"] >= "2026-11-19" for e in analyst["earningsDates"])
assert len(analyst["earningsDates"]) == 11
assert analyst["droppedEarnings"] == []
assert analyst["addedEarnings"] == []
assert internals["smi"]["series"] == data["MARKET_INTERNALS"]["smi"]["series"]
assert internals["smi"]["latest"] == data["MARKET_INTERNALS"]["smi"]["latest"]
assert internals["aaii"]["latest"] == {"bullish": 33.3, "neutral": 24.4,
                                       "bearish": 42.2}
assert len(internals["aaii"]["history"]) == 4
macro = internals["macroEvents"]
assert len(macro) == 35, len(macro)
assert all(e["date"] >= "2026-11-19" for e in macro)
assert [e["date"] for e in macro] == sorted(e["date"] for e in macro)
for e in macro:
    assert set(e.keys()) == {"category", "categoryZh", "date", "impact",
                             "impactZh", "time", "title", "titleZh"}, e
assert set(yahoo["bars"].keys()) == set(data["HISTORY"]) - {"SQ"}
assert yahoo["missing"] == ["SQ"]
assert all(any(b["d"] == "2026-11-18" for b in v)
           for v in yahoo["bars"].values())
assert sum(len(v) for v in analyst["analystRevisions"].values()) == 1057, \
    sum(len(v) for v in analyst["analystRevisions"].values())
assert analyst["newAnalystItems"] == 24
# sector breadth from Yahoo collector (Nov 18 finals)
assert len(yahoo["sectorBreadth"]) == 10
assert [s["etf"] for s in yahoo["sectorBreadth"]] == [
    "XLK", "XLF", "XLV", "XLE", "XLI", "XLU", "XLP", "XLY", "XLC", "XLRE"]
notes.append("validation ok: scores sum, 63 IV tickers, analyst keys, "
             "58 refreshed / 5 carried (LRCX, AMAT, TXN, KLAC 429; SQ "
             "Sahakol), no rank >100, FedWatch 8 meetings sum ~100, "
             "11-entry strip all future (no drops/adds), SMI carried, "
             "AAII NEW 33.3/24.4/42.2, macro 35 rich entries sorted "
             "Nov 19..Dec 23, yahoo 74 tickers with Nov 18 bars + SQ "
             "missing, analyst total 1057 (+24 new)")

# ---------- expected moves (recomputed from merged fresh IV) ----------
DTE = {"2026-11-19": ("2026-11-20", 1), "2026-11-24": ("2026-11-27", 8),
       "2026-12-01": ("2026-12-04", 15), "2026-12-02": ("2026-12-04", 15),
       "2026-12-09": ("2026-12-11", 22), "2026-12-10": ("2026-12-11", 22),
       "2026-12-14": ("2026-12-18", 29), "2026-12-16": ("2026-12-18", 29)}
exp_moves_new = {}
earn = []
for e in analyst["earningsDates"]:
    e = dict(e)
    expiry, dte = DTE[e["date"]]
    mv = round(iv[e["ticker"]]["iv30"] * math.sqrt(dte / 365), 2)
    exp_moves_new[e["ticker"]] = mv
    e["expected_move"] = mv
    e["move_as_of"] = "Nov 19, 2026"
    e["move_method"] = (
        f"30-day IV × √(DTE/365) to Friday weekly expiry {expiry} "
        f"(DTE {dte} from Nov 19); optioncharts expiry-table % not readable "
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
    "scanTime": "2026-11-19 ~7:30 AM (premarket)",
    "resultCount": screen["resultCount"],
    "resultTime": "2026-11-19 ~7:30 AM (premarket)",
    "source": "https://finviz.com/screener?v=211&f=cap_midover,sh_opt_option,ta_change_u,ta_highlow52w_b10h,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3",
    "optionsAsOf": "Nov 19, 2026 (optioncharts.io)",
    "note": screen["note"],
    "potential": screen["potential"],
    "volumes": screen["volumes"],
}
notes.append("screen: " + str([(p["ticker"], p["score"])
                               for p in screen["potential"]]))

# ---------- HISTORY (Nov 18 bars only) ----------
hist_bars = {}
for t in data["HISTORY"]:
    bars = [b for b in yahoo["bars"].get(t, []) if b["d"] == "2026-11-18"]
    if bars:
        hist_bars[t] = bars
assert all(b["d"] == "2026-11-18"
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
mi["putCall"] = internals["putCall"]
mi["breadth"] = fedwatch["breadth"]  # live-browser Nov 18 closes
mi["aaii"] = internals["aaii"]  # NEW week ending Nov 18
mi["flows"] = internals["flows"]  # carried Nov 17 session (Nov 18 report not posted)
mi["flowsAsOf"] = internals["flowsAsOf"]
mi["fedWatch"] = {k: fedwatch[k] for k in
                  ("asof", "context", "effr", "effrAsOf", "meetings")}
notes.append("internals: F&G 25 Extreme Fear (Nov 18 close; CNN JSON "
             "418-blocked, mirror CSV 24.61 corroborates), VIX 24.56/24.29 "
             "backwardation 0.99, P/C eq 0.72 idx 1.14 total 1.05 (Nov 18 "
             "finals), AAII NEW 33.3/24.4/42.2 (week ending Nov 18), flows "
             "carried Nov 17 session (Nov 18 report not yet posted), "
             "breadth A/D 0.88/-115, %>50d 56.26 %>200d 56.06, highs/lows "
             "summary Overall 43/601, FedWatch 8 meetings Dec 9 hike 100% "
             "(90.7% one hike / 9.3% 50bp) (live CME)")

# ---------- SECTOR_BREADTH (Yahoo Nov 18 finals) ----------
sector_breadth = []
for s in yahoo["sectorBreadth"]:
    sector_breadth.append({
        "etf": s["etf"], "name": s["name"], "nameZh": s["nameZh"],
        "change": s["change"], "close": s["close"], "previous": s["previous"],
        "url": s.get("url", f"https://finnhub.io/?q=%22{s['etf']}%22"),
    })
notes.append("sectorBreadth (Nov 18 finals, Yahoo daily closes): " +
             str([(s["etf"], s["change"]) for s in sector_breadth]))

# ---------- IV_SOURCE ----------
iv_source = (
    "Nov 19, 2026 · 58 of 63 refreshed from optioncharts.io (live overview "
    "pages, Nov 18 close data; 30-day IV and IV rank refreshed; IV percentile "
    "carried last-good for all 63 — the text fetch exposes 30-day IV and IV "
    "rank only, not percentile); 5 carried last-good: LRCX, AMAT, TXN, KLAC "
    "(optioncharts returned 429 rate-limit on a parallel batch; not retried), "
    "SQ (optioncharts still shows unrelated Sahakol Equipment, stale Oct 16 "
    "crawl; Block now XYZ there, not applied pending the ticker-rename "
    "decision). SPY refreshed today after yesterday's empty page. BRK-B "
    "refreshed via the BRKB page.")

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
    "15 ranked setups from the November 19 Finviz screen, with verified "
    "front-month options activity.")
i18n["zh"]["tradesDesc"] = (
    "根据 11 月 19 日的 Finviz 筛选，列出15个已验证近月期权活跃度的排序机会。")
i18n["en"]["ivAsOf"] = (
    "Updated Nov 19, 2026 · optioncharts.io 30-day IV readings "
    "(58 of 63 refreshed; 5 carried last-good; IV percentile carried "
    "last-good for all 63); stale source pages are flagged in ticker detail")
i18n["zh"]["ivAsOf"] = (
    "更新于 11 月 19 日 · optioncharts.io 隐含波动率数据（63 个标的中 58 个"
    "已刷新，5 个沿用上次有效值；IV 百分位全部沿用上次有效值）")
i18n["en"]["calendarDesc"] = f"Macro calendar refreshed {RUN_STAMP}"
i18n["zh"]["calendarDesc"] = f"宏观日历已于 {RUN_STAMP} 更新"
i18n["en"]["sevenDayWindow"] = "Next 7 days: Nov 19 – Nov 25, 2026"
i18n["zh"]["sevenDayWindow"] = "未来7天：2026年11月19日 – 11月25日"
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
    "ANALYST_REVISIONS": analyst["analystRevisions"],
    "ASOF": asof,
    "I18N_OVERRIDES": i18n,
}
json.dump(patch, open("/tmp/patch.json", "w"))
print("\n".join(notes))
print("patch keys:", sorted(patch.keys()))
print("analyst total entries:",
      sum(len(v) for v in analyst["analystRevisions"].values()))
