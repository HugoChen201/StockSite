#!/usr/bin/env python3
"""Morning-refresh patch builder for StockSite data.json (Fri 2026-11-20).

Collectors (all verified by the parent run):
- Finviz screen: v=111 Overview via browser.open, page 1 (r=1-20) clean,
  page 2 (r=21-34) 403 to the text fetch — recovered via live browser
  (~7:31 AM ET; live page showed 36 total vs 34 at the collector's fetch,
  screen drifting in premarket). 14 ranked (HD 78 top, CLX 76, KHC 76
  added from page 2, CMG 75, CPA 73). KHC option-checked by parent
  (20,134 contracts Nov 19, OI 416,980, front-month 7,596; 52-wk high
  $28.09); TSCO 62 added the same way (5,046 / OI 152,435, front-month
  1,397; 52-wk high $56.28). KRC +2.73% / PRAX +2.61% seen on page 2
  but NOT ranked (16 / 280 premarket shares, not option-checked).
  relVolume null for all (premarket partial session); relVol scored
  from %chg + avg-vol tier. Thin chains scored down: AWI 12, BRO 15,
  IMVT 32, EPAM 231, HDB 328 contracts.
- History: Yahoo daily chart API (curl concurrent), Nov 19 bars.
  74 tickers; SQ missing expected (Yahoo 404; Block renamed SQ -> XYZ;
  NO rename).
- Internals: F&G 19 Extreme Fear Nov 19 close (CNN JSON 418-blocked;
  mirror CSV 18.68 corroborates; prev close 24); VIX 28.44 / VIX3M
  27.03, ratio 0.95 backwardation (Yahoo closes verified, match stored);
  put/call Nov 19 finals eq 0.62 idx 1.20 total 1.01 (ycharts, read
  Nov 20 ~7:35 AM ET; Nov 18 values match stored, confirming series);
  AAII carried (week ending Nov 18: 33.3/24.4/42.2); flows carried
  Nov 18 session (SPY +$1.35B, QQQ -$1.15B, IWM -$0.25B Nov 16) —
  Nov 19-session ETF Action report NOT yet posted; SMI carried 999.9
  (finalized through Nov 19).
- Breadth (live browser, fresh read Nov 20 ~7:30 AM ET): $ADRN 0.12
  printed / 0.13 computed from counts (210 adv / 1,620 dec, net
  -1,410, matching $ADDN exactly; prev close 0.88 / -115), % above
  50-day 49.10 (prev 56.26), % above 200-day 49.10 (prev 56.06) —
  flag: $S5FI and $S5TH again printed exactly 49.10. 52-wk highs/lows
  from the highs-lows Summary tab (Last Updated 11/19 19:45 ET):
  Overall 23/677, NYSE 11/185, Nasdaq 12/452, Arca 0/40.
- FedWatch: LIVE CME FedWatch page via browser (data as of 06:15-06:20
  CT Nov 20; Akamai block cleared by fresh-browser move). Dec 9 hike
  now 100%: one hike 400-425 at 99.6% (was 90.7%), 50bp tail 0.4%
  (was 9.3%). EFFR not shown on page again — carried 3.88. Same 8
  meeting tabs ending Nov 17, 2027 (Jun 9 / Sep 15 labels as stored).
- Macro: 35 events, Nov 20..Dec 23. Dropped 4 Nov 19 events + the
  Dec 16 "combined employment report" entry as superseded (BLS
  schedule lists Dec 4 for the November jobs report; October report
  already released Nov 6). ADDED Nov 24 S&P/Case-Shiller + Richmond
  Fed Mfg + Consumer Confidence, Nov 25 Jobless Claims (moved up for
  Thanksgiving), Dec 15 Empire State Mfg.
- IV: optioncharts.io overview pages, 58 of 63 refreshed (30-day IV +
  IV rank; IV percentile carried last-good for all 63). 5 carried:
  ASML/MU/INTC (optioncharts 429 mid-batch, not retried), SNDK
  (overview page internally inconsistent — 30-day IV 200.1% above its
  own 1-yr high 163.4%, rank 137; carried pending glitch clearing),
  SQ (Sahakol page). BRK-B via BRKB. CRM flag: IV-block rank 97.86
  used; FAQ text says 107.
- Expected moves: recomputed here from MERGED fresh IV (IV-formula
  fallback: 30-day IV x sqrt(DTE/365) to the Friday weekly expiry).
  Strip: 10 entries — WMT DROPPED (reported Nov 19 BMO), no adds.
- Analyst: 12 new items (WMT x5 post-earnings PT raises, NVDA x2
  post-earnings cuts, MSFT x1 upgrade, AAPL x1, BE x1 upgrade,
  MSTR x1 downgrade, AMD x1), dated Nov 13-19; total 1,069 (was 1,057).
"""
import json
import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())
screen = json.loads((HID / "screen_2026-11-20.json").read_text())
internals = json.loads((HID / "internals_2026-11-20.json").read_text())
fedwatch = json.loads((HID / "fedwatch_2026-11-20.json").read_text())
iva = json.loads((HID / "iv_part_a_2026-11-20.json").read_text())
ivb = json.loads((HID / "iv_part_b_2026-11-20.json").read_text())
analyst = json.loads((HID / "analyst_2026-11-20.json").read_text())
yahoo = json.loads((HID / "yahoo_2026-11-20.json").read_text())

RUN_STAMP = datetime.now(ZoneInfo("America/New_York")).strftime(
    "%b %-d, %Y %-I:%M %p ET").replace("  ", " ")
notes = [f"RUN_STAMP={RUN_STAMP}"]

# ---------- merge IV ----------
iv = dict(iva["iv"])
iv.update(ivb["iv"])
assert not (set(iva["iv"]) & set(ivb["iv"])), "IV parts overlap"
CARRIED_IV = sorted(c["ticker"] for c in iva["carried"] + ivb["carried"])
assert CARRIED_IV == ["ASML", "INTC", "MU", "SNDK", "SQ"], CARRIED_IV
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
assert screen["resultCount"] == 34
assert len(screen["potential"]) == 14
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
assert all(e["date"] >= "2026-11-20" for e in analyst["earningsDates"])
assert len(analyst["earningsDates"]) == 10
assert analyst["droppedEarnings"] == ["WMT"]
assert analyst["addedEarnings"] == []
assert internals["smi"]["series"] == data["MARKET_INTERNALS"]["smi"]["series"]
assert internals["smi"]["latest"] == data["MARKET_INTERNALS"]["smi"]["latest"]
assert internals["aaii"]["latest"] == {"bullish": 33.3, "neutral": 24.4,
                                       "bearish": 42.2}
assert len(internals["aaii"]["history"]) == 4
macro = internals["macroEvents"]
assert len(macro) == 35, len(macro)
assert all(e["date"] >= "2026-11-20" for e in macro)
assert [e["date"] for e in macro] == sorted(e["date"] for e in macro)
for e in macro:
    assert set(e.keys()) == {"category", "categoryZh", "date", "impact",
                             "impactZh", "time", "title", "titleZh"}, e
assert set(yahoo["bars"].keys()) == set(data["HISTORY"]) - {"SQ"}
assert yahoo["missing"] == ["SQ"]
assert all(any(b["d"] == "2026-11-19" for b in v)
           for v in yahoo["bars"].values())
assert sum(len(v) for v in analyst["analystRevisions"].values()) == 1069, \
    sum(len(v) for v in analyst["analystRevisions"].values())
assert analyst["newAnalystItems"] == 12
# sector breadth from Yahoo collector (Nov 19 finals)
assert len(yahoo["sectorBreadth"]) == 10
assert [s["etf"] for s in yahoo["sectorBreadth"]] == [
    "XLK", "XLF", "XLV", "XLE", "XLI", "XLU", "XLP", "XLY", "XLC", "XLRE"]
notes.append("validation ok: scores sum, 63 IV tickers, analyst keys, "
             "58 refreshed / 5 carried (ASML, MU, INTC 429; SNDK page "
             "glitch; SQ Sahakol), no rank >100, FedWatch 8 meetings sum "
             "~100, 10-entry strip (WMT dropped, no adds), SMI carried, "
             "AAII carried 33.3/24.4/42.2, macro 35 rich entries sorted "
             "Nov 20..Dec 23, yahoo 74 tickers with Nov 19 bars + SQ "
             "missing, analyst total 1069 (+12 new)")

# ---------- expected moves (recomputed from merged fresh IV) ----------
DTE = {"2026-11-24": ("2026-11-27", 7),
       "2026-12-01": ("2026-12-04", 14), "2026-12-02": ("2026-12-04", 14),
       "2026-12-09": ("2026-12-11", 21), "2026-12-10": ("2026-12-11", 21),
       "2026-12-14": ("2026-12-18", 28), "2026-12-16": ("2026-12-18", 28)}
exp_moves_new = {}
earn = []
for e in analyst["earningsDates"]:
    e = dict(e)
    expiry, dte = DTE[e["date"]]
    mv = round(iv[e["ticker"]]["iv30"] * math.sqrt(dte / 365), 2)
    exp_moves_new[e["ticker"]] = mv
    e["expected_move"] = mv
    e["move_as_of"] = "Nov 20, 2026"
    e["move_method"] = (
        f"30-day IV × √(DTE/365) to Friday weekly expiry {expiry} "
        f"(DTE {dte} from Nov 20); optioncharts expiry-table % not readable "
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
    "scanTime": "2026-11-20 ~7:30 AM (premarket)",
    "resultCount": screen["resultCount"],
    "resultTime": "2026-11-20 ~7:30 AM (premarket)",
    "source": "https://finviz.com/screener?v=211&f=cap_midover,sh_opt_option,ta_change_u,ta_highlow52w_b10h,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3",
    "optionsAsOf": "Nov 20, 2026 (optioncharts.io)",
    "note": screen["note"],
    "potential": screen["potential"],
    "volumes": screen["volumes"],
}
notes.append("screen: " + str([(p["ticker"], p["score"])
                               for p in screen["potential"]]))

# ---------- HISTORY (Nov 19 bars only) ----------
hist_bars = {}
for t in data["HISTORY"]:
    bars = [b for b in yahoo["bars"].get(t, []) if b["d"] == "2026-11-19"]
    if bars:
        hist_bars[t] = bars
assert all(b["d"] == "2026-11-19"
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
mi["breadth"] = fedwatch["breadth"]  # live-browser Nov 19 closes
mi["aaii"] = internals["aaii"]  # carried week ending Nov 18
mi["flows"] = internals["flows"]  # carried Nov 18 session (Nov 19 report not posted)
mi["flowsAsOf"] = internals["flowsAsOf"]
mi["fedWatch"] = {k: fedwatch[k] for k in
                  ("asof", "context", "effr", "effrAsOf", "meetings")}
notes.append("internals: F&G 19 Extreme Fear (Nov 19 close; CNN JSON "
             "418-blocked, mirror CSV 18.68 corroborates), VIX 28.44/27.03 "
             "backwardation 0.95, P/C eq 0.62 idx 1.20 total 1.01 (Nov 19 "
             "finals), AAII carried 33.3/24.4/42.2 (week ending Nov 18), "
             "flows carried Nov 18 session (Nov 19 report not yet posted), "
             "breadth A/D 0.13/-1,410, %>50d 49.10 %>200d 49.10, highs/lows "
             "summary Overall 23/677, FedWatch 8 meetings Dec 9 hike 100% "
             "(99.6% one hike / 0.4% 50bp) (live CME)")

# ---------- SECTOR_BREADTH (Yahoo Nov 19 finals) ----------
sector_breadth = []
for s in yahoo["sectorBreadth"]:
    sector_breadth.append({
        "etf": s["etf"], "name": s["name"], "nameZh": s["nameZh"],
        "change": s["change"], "close": s["close"], "previous": s["previous"],
        "url": s.get("url", f"https://finnhub.io/?q=%22{s['etf']}%22"),
    })
notes.append("sectorBreadth (Nov 19 finals, Yahoo daily closes): " +
             str([(s["etf"], s["change"]) for s in sector_breadth]))

# ---------- IV_SOURCE ----------
iv_source = (
    "Nov 20, 2026 · 58 of 63 refreshed from optioncharts.io (live overview "
    "pages, Nov 19 close data; 30-day IV and IV rank refreshed; IV percentile "
    "carried last-good for all 63 — the text fetch exposes 30-day IV and IV "
    "rank only, not percentile); 5 carried last-good: ASML, MU, INTC "
    "(optioncharts returned 429 rate-limit mid-batch; not retried), SNDK "
    "(overview page internally inconsistent — 30-day IV 200.1% above its own "
    "1-yr high 163.4%, IV rank 137; carried pending glitch clearing), SQ "
    "(optioncharts still shows unrelated Sahakol Equipment, stale Oct 16 "
    "crawl; Block now XYZ there, not applied pending the ticker-rename "
    "decision). BRK-B refreshed via the BRKB page. CRM page flag: IV-block "
    "rank 97.86 used; FAQ text says 107.")

# ---------- EXPECTED_MOVES ----------
exp_moves = dict(data["EXPECTED_MOVES"])
for t, mv in exp_moves_new.items():
    exp_moves[t] = mv
if "WMT" in exp_moves:
    del exp_moves["WMT"]  # reported Nov 19; no longer an upcoming earnings move

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
    "14 ranked setups from the November 20 Finviz screen, with verified "
    "front-month options activity.")
i18n["zh"]["tradesDesc"] = (
    "根据 11 月 20 日的 Finviz 筛选，列出14个已验证近月期权活跃度的排序机会。")
i18n["en"]["ivAsOf"] = (
    "Updated Nov 20, 2026 · optioncharts.io 30-day IV readings "
    "(58 of 63 refreshed; 5 carried last-good; IV percentile carried "
    "last-good for all 63); stale source pages are flagged in ticker detail")
i18n["zh"]["ivAsOf"] = (
    "更新于 11 月 20 日 · optioncharts.io 隐含波动率数据（63 个标的中 58 个"
    "已刷新，5 个沿用上次有效值；IV 百分位全部沿用上次有效值）")
i18n["en"]["calendarDesc"] = f"Macro calendar refreshed {RUN_STAMP}"
i18n["zh"]["calendarDesc"] = f"宏观日历已于 {RUN_STAMP} 更新"
i18n["en"]["sevenDayWindow"] = "Next 7 days: Nov 20 – Nov 26, 2026"
i18n["zh"]["sevenDayWindow"] = "未来7天：2026年11月20日 – 11月26日"
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
