#!/usr/bin/env python3
"""Morning-refresh patch builder for StockSite data.json (Wed 2026-11-25).

Collectors (all verified by the parent run):
- Finviz screen: BLOCKED. browser.open on the screener URL returned 403
  (upstream access rejected); do not retry per the fetch denial. No live
  browser available to this subagent run. SCREEN_SNAPSHOT is CARRIED verbatim
  from Nov 24 (44 results, 15 ranked, INSM 84 top). The Potential Trades pane
  keeps its Nov 24 stamp — honest, not restamped. Parent: a live-browser
  Finviz fetch is still needed for a fresh screen; apply as a follow-up patch.
- History: Yahoo daily chart API, Nov 24 bars, 74 tickers (62 watchlist ex SQ
  + 10 sector ETFs + ^VIX + ^VIX3M; SPY inside the 63). SQ missing (Yahoo
  404; Block renamed SQ -> XYZ; NO rename). SNDK Nov 24 bar patched from
  stockanalysis.com (Yahoo null close again; C 77.95, -11.13%). ^VIX/^VIX3M
  and the 10 sector ETFs are NOT keys in data.json HISTORY (75 keys = 63
  watchlist + 12 calendar names); their bars feed vixTerm / sectorBreadth
  only. The stray Nov 24 ^VIX bar (close 28.84) lived only in yesterday's
  collector file, not in data.json; the fresh Yahoo bar (C 26.36) is used for
  vixTerm. Stray Nov 25 ^VIX bar excluded.
  HISTORY also holds 12 earnings-calendar names the collector does not cover;
  left untouched (enrich-calendar-stocks.py tops them up).
- Internals: F&G 17.42 Extreme Fear (CNN official JSON served a 19-day-stale
  Nov 5 cached copy; value from the whit3rabbit GitHub mirror of CNN data,
  crawled <1 min before read; CNN rounds to 17, matching the stored Nov 24
  close print; mirror's Nov 23 value 14.88 differs from CNN's live Nov 24
  morning read of 16.97 — CNN revises prints, flagged). VIX 26.36 / VIX3M
  25.47, ratio 0.97 backwardation (Yahoo closes, match stored close-refresh
  values). Put/call Nov 24 finals eq 0.57 idx 1.12 total 0.95 (ycharts, read
  live Nov 25 ~7:32 AM ET). AAII carried (week ending Nov 18: 33.3/24.4/42.2;
  FLAG RESOLVED: the live AAII history table now matches stored history
  exactly — the Nov 24 discrepancy is gone; no new week posted, next release
  Thu Nov 26 is Thanksgiving, likely delayed). Flows carried Nov 20 session
  (SPY -$1.54B, QQQ +$0.61B, IWM -$0.20B — no Nov 23/24-session ETF Action
  report posted as of Nov 25 ~7:35 AM ET). SMI carried 998.67 (verified
  exactly by the Yahoo collector from SPY 1m: first-30-min +0.62%,
  last-hour +0.38%). Breadth carried Nov 24 closes (Barchart unreadable:
  browser.open served an 84-day-stale Sep 2 snapshot for $S5FI; $S5TH /
  highs-lows crawls failed page_too_old): %>50d 55.06 %>200d 53.47, A/D 1.49 /
  +359, highs/lows NYSE 23/85 Nasdaq 39/272 — as-of marked unavailable.
  FedWatch carried verbatim (CME page shell-only via browser.open; CME API
  curl IP-blocked; third-party mirrors suggest Dec 9 ~99% 25bp hike vs stored
  97.5% — one day stale, re-read when CME is readable).
- Macro: 31 events, Nov 25..Dec 23; dropped the 3 Nov 24 events, added U.S.
  International Trade in Goods and Services (Oct) Dec 8 8:30 AM ET (BEA
  schedule, two independent reads). Anchors re-verified (FOMC Dec 8-9,
  decision Dec 9 2 PM; CPI Dec 10; PPI Dec 15; NFP Dec 4; PCE Dec 23).
- IV: optioncharts.io overview pages, 62 of 63 refreshed (30-day IV + IV rank
  + IV percentile from the IV block; FAQ text ignored per convention). 1
  carried: SQ (Sahakol page). Broad IV rise across semis/AI on Nov 24
  (NVDA rank 71.41->79.64, AMD 76.0->88.75, DELL 81.58->90.03, VRT
  67.68->92.92). UBER percentile swung again (19.92->43.25) — optioncharts
  percentiles look unstable for this name; stored as read.
- Expected moves: recomputed from merged fresh IV (IV-formula fallback:
  30-day IV x sqrt(DTE/365) to the Friday weekly expiry, DTE counted from
  Nov 25). Strip: 8 entries (ADI + DELL dropped — reported Nov 24).
- Analyst: 27 new items (DELL/ADI post-earnings PT cuts, MU downgraded to
  Neutral by BNP Paribas Exane, Evercore sweeping PT cuts across
  memory/storage/AI infra, TSLA Seaport Buy initiation $475), dated Nov 24-25;
  total 1,158 (was 1,131). Zero near-dupes (same ticker+date+firm check).
- Sector breadth (Nov 24 finals, Yahoo): 8 of 10 green; XLK -3.26% worst,
  XLV +2.95% best.
"""
import json
import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())
internals = json.loads((HID / "internals_2026-11-25.json").read_text())
fedwatch = json.loads((HID / "fedwatch_2026-11-25.json").read_text())
iva = json.loads((HID / "iv_part_a_2026-11-25.json").read_text())
ivb = json.loads((HID / "iv_part_b_2026-11-25.json").read_text())
analyst = json.loads((HID / "analyst_2026-11-25.json").read_text())
yahoo = json.loads((HID / "yahoo_2026-11-25.json").read_text())

RUN_STAMP = datetime.now(ZoneInfo("America/New_York")).strftime(
    "%b %-d, %Y %-I:%M %p ET").replace("  ", " ")
(Path("/tmp/run_stamp.txt")).write_text(RUN_STAMP)
notes = [f"RUN_STAMP={RUN_STAMP}"]

# ---------- merge IV ----------
iv = dict(iva["iv"])
iv.update(ivb["iv"])
assert not (set(iva["iv"]) & set(ivb["iv"])), "IV parts overlap"
CARRIED_IV = sorted(c["ticker"] for c in iva["carried"] + ivb["carried"])
assert CARRIED_IV == ["SQ"], CARRIED_IV
REFRESHED_N = len(iva["refreshed"]) + len(ivb["refreshed"])

# ---------- validation ----------
assert set(iv) == {s["ticker"] for s in data["STOCKS"]}, \
    set(iv) ^ {s["ticker"] for s in data["STOCKS"]}
assert set(analyst["analystRevisions"]) == {s["ticker"] for s in data["STOCKS"]}
assert REFRESHED_N == 62, REFRESHED_N
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
assert [m["decision"] for m in fedwatch["meetings"]] == \
    [m["decision"] for m in data["MARKET_INTERNALS"]["fedWatch"]["meetings"]]
assert all(e["date"] >= "2026-11-25" for e in analyst["earningsDates"])
assert len(analyst["earningsDates"]) == 8
assert [(e["date"], e["ticker"]) for e in analyst["earningsDates"]] == [
    ("2026-12-01", "MRVL"), ("2026-12-02", "CRM"),
    ("2026-12-02", "SNOW"), ("2026-12-09", "ADBE"),
    ("2026-12-09", "AVGO"), ("2026-12-10", "COST"),
    ("2026-12-14", "ORCL"), ("2026-12-17", "MU")]
assert internals["smi"] == data["MARKET_INTERNALS"]["smi"]
assert internals["smi"]["latest"] == 998.67
assert yahoo["smiCheck"]["match"] is True
assert yahoo["smiCheck"]["computed"] == 998.67
assert internals["aaii"]["latest"] == {"bullish": 33.3, "neutral": 24.4,
                                       "bearish": 42.2}
assert len(internals["aaii"]["history"]) == 4
macro = internals["macroEvents"]
assert len(macro) == 31, len(macro)
assert all(e["date"] >= "2026-11-25" for e in macro)
assert [e["date"] for e in macro] == sorted(e["date"] for e in macro)
for e in macro:
    assert set(e.keys()) == {"category", "categoryZh", "date", "impact",
                             "impactZh", "time", "title", "titleZh"}, e
watch = {s["ticker"] for s in data["STOCKS"]}
assert set(yahoo["bars"].keys()) == (watch - {"SQ"}) | \
    {"XLK", "XLF", "XLV", "XLE", "XLI", "XLU", "XLP", "XLY", "XLC", "XLRE",
     "^VIX", "^VIX3M"}, set(yahoo["bars"].keys()) ^ (watch - {"SQ"})
assert yahoo["missing"] == ["SQ"]
assert all(any(b["d"] == "2026-11-24" for b in v)
           for v in yahoo["bars"].values())
assert sum(len(v) for v in analyst["analystRevisions"].values()) == 1158, \
    sum(len(v) for v in analyst["analystRevisions"].values())
assert analyst["newAnalystItems"] == 27
assert len(yahoo["sectorBreadth"]) == 10
assert [s["etf"] for s in yahoo["sectorBreadth"]] == [
    "XLK", "XLF", "XLV", "XLE", "XLI", "XLU", "XLP", "XLY", "XLC", "XLRE"]
# breadth values carried (only as-of strings changed)
sb = data["MARKET_INTERNALS"]["breadth"]
nb = fedwatch["breadth"]
for k in ("above50", "above50Prev", "above200", "above200Prev",
          "advanceDeclineRatio", "adDifference", "newHighs", "newLows",
          "nasdaqHighs", "nasdaqLows"):
    assert sb[k] == nb[k], (k, sb[k], nb[k])
# vixTerm values match stored Nov 24 closes
assert internals["vixTerm"]["spot"] == 26.36
assert internals["vixTerm"]["threeMonth"] == 25.47
notes.append("validation ok: 62 IV refreshed / 1 carried (SQ), analyst 1158 "
             "(+27), FedWatch 8 meetings carried, SMI verified 998.67, AAII "
             "carried 33.3/24.4/42.2, macro 31 sorted Nov 25..Dec 23, yahoo "
             "74 tickers with Nov 24 bars + SQ missing, breadth values "
             "carried, F&G 17.42 mirror, P/C fresh 0.57/1.12/0.95")

# ---------- expected moves (recomputed from merged fresh IV) ----------
DTE = {"2026-12-01": ("2026-12-04", 9), "2026-12-02": ("2026-12-04", 9),
       "2026-12-09": ("2026-12-11", 16), "2026-12-10": ("2026-12-11", 16),
       "2026-12-14": ("2026-12-18", 23), "2026-12-17": ("2026-12-18", 23)}
exp_moves_new = {}
earn = []
for e in analyst["earningsDates"]:
    e = dict(e)
    expiry, dte = DTE[e["date"]]
    mv = round(iv[e["ticker"]]["iv30"] * math.sqrt(dte / 365), 2)
    exp_moves_new[e["ticker"]] = mv
    e["expected_move"] = mv
    e["move_as_of"] = "Nov 25, 2026"
    e["move_method"] = (
        f"30-day IV × √(DTE/365) to Friday weekly expiry {expiry} "
        f"(DTE {dte} from Nov 25); optioncharts expiry-table % not readable "
        "in text fetch — IV-formula fallback per refresh rules")
    e["move_method_zh"] = "期权隐含预期波动（30日隐含波动率×√(DTE/365)）"
    st = next((x for x in data["EARNINGS_DATES"]
               if x["ticker"] == e["ticker"]), None)
    if st and len(st.get("sources", [])) > len(e.get("sources", [])):
        e["sources"] = st["sources"]  # keep fuller stored source list
    earn.append(e)
notes.append("expected moves recomputed from merged IV: " +
             str(exp_moves_new))

# ---------- SCREEN_SNAPSHOT (CARRIED — Finviz 403-blocked this run) ----------
screen_snapshot = data["SCREEN_SNAPSHOT"]
notes.append("SCREEN_SNAPSHOT CARRIED from Nov 24 (Finviz screener 403 on "
             "browser.open text fetch; no live browser in this run). Trades "
             "pane keeps its Nov 24 7:44 AM ET stamp; follow-up patch needed "
             "once a live-browser Finviz fetch lands.")

# ---------- HISTORY (Nov 24 bars for HISTORY tickers only) ----------
hist_bars = {}
for t in data["HISTORY"]:
    bars = [b for b in yahoo["bars"].get(t, []) if b["d"] == "2026-11-24"]
    if bars:
        hist_bars[t] = bars
assert all(b["d"] == "2026-11-24"
           for v in hist_bars.values() for b in v)
history = {t: list(bars) for t, bars in data["HISTORY"].items()}
appended = 0
for t, bars in hist_bars.items():
    existing = {b["d"] for b in history[t]}
    new = [b for b in bars if b["d"] not in existing]
    if new:
        history[t] = sorted(history[t] + new, key=lambda b: b["d"])
        appended += len(new)
notes.append(f"HISTORY appended {appended} Nov 24 bars across "
             f"{len(hist_bars)} tickers (62 watchlist ex SQ; sector-ETF / "
             "^VIX / ^VIX3M bars are not HISTORY keys — they feed "
             "sectorBreadth / vixTerm only); missing: SQ (Yahoo 404, no "
             "rename); 12 earnings-calendar names untouched "
             "(enrich-calendar-stocks.py tops them up)")

# ---------- MARKET_INTERNALS (read-modify-write whole object) ----------
mi = json.loads(json.dumps(data["MARKET_INTERNALS"]))  # deep copy
mi["fearGreed"] = internals["fearGreed"]
mi["vixTerm"] = internals["vixTerm"]
mi["putCall"] = internals["putCall"]
mi["breadth"] = fedwatch["breadth"]  # carried Nov 24 closes, as-of unavailable
mi["aaii"] = internals["aaii"]  # carried week ending Nov 18
mi["flows"] = internals["flows"]  # carried Nov 20 session
mi["flowsAsOf"] = internals["flowsAsOf"]
mi["fedWatch"] = {k: fedwatch[k] for k in
                  ("asof", "context", "effr", "effrAsOf", "meetings")}
notes.append("internals: F&G 17.42 Extreme Fear (GitHub mirror of CNN data; "
             "CNN JSON served stale Nov 5 copy; prev close 14.88 per mirror "
             "vs 16.97 CNN live Nov 24 — CNN revises prints), VIX 26.36/25.47 "
             "backwardation 0.97, P/C eq 0.57 idx 1.12 total 0.95 (Nov 24 "
             "finals), AAII carried 33.3/24.4/42.2 (week ending Nov 18; live "
             "history now matches stored — Nov 24 flag resolved), flows "
             "carried Nov 20 session (no Nov 23/24 report posted), breadth "
             "carried (Barchart stale/unreadable), SMI carried 998.67 "
             "(verified exactly), FedWatch carried (CME IP-blocked; mirrors "
             "suggest Dec 9 ~99% vs stored 97.5%)")

# ---------- SECTOR_BREADTH (Yahoo Nov 24 finals) ----------
sector_breadth = []
for s in yahoo["sectorBreadth"]:
    sector_breadth.append({
        "etf": s["etf"], "name": s["name"], "nameZh": s["nameZh"],
        "change": s["change"], "close": s["close"], "previous": s["previous"],
        "url": s.get("url", f"https://finnhub.io/?q=%22{s['etf']}%22"),
    })
notes.append("sectorBreadth (Nov 24 finals, Yahoo daily closes): " +
             str([(s["etf"], s["change"]) for s in sector_breadth]))

# ---------- IV_SOURCE ----------
iv_source = (
    "Nov 25, 2026 · 62 of 63 refreshed from optioncharts.io (live overview "
    "pages, Nov 24 close data; 30-day IV, IV rank AND IV percentile all "
    "refreshed from the IV block); 1 carried last-good: SQ (optioncharts "
    "still shows unrelated Sahakol Equipment, stale Oct 16 crawl; Block now "
    "XYZ there, not applied pending the ticker-rename decision). Broad IV "
    "rise across semis/AI on Nov 24 (NVDA rank 71.41 → 79.64, AMD 76.0 → "
    "88.75, DELL 81.58 → 90.03, VRT 67.68 → 92.92). UBER percentile swung "
    "again (19.92 → 43.25) — optioncharts percentiles look unstable for this "
    "name; stored as read. BRK-B refreshed via the BRKB page. FAQ text on "
    "most pages quotes a different, higher IV rank than the structured IV "
    "block; IV-block values used throughout.")

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
# tradesDesc UNCHANGED — screen carried from Nov 24 (Finviz blocked).
i18n["en"]["ivAsOf"] = (
    "Updated Nov 25, 2026 · optioncharts.io 30-day IV readings "
    "(62 of 63 refreshed; 1 carried last-good); stale source pages are "
    "flagged in ticker detail")
i18n["zh"]["ivAsOf"] = (
    "更新于 11 月 25 日 · optioncharts.io 隐含波动率数据（63 个标的中 62 个"
    "已刷新，1 个沿用上次有效值）")
i18n["en"]["calendarDesc"] = f"Macro calendar refreshed {RUN_STAMP}"
i18n["zh"]["calendarDesc"] = f"宏观日历已于 {RUN_STAMP} 更新"
i18n["en"]["sevenDayWindow"] = "Next 7 days: Nov 25 – Dec 1, 2026"
i18n["zh"]["sevenDayWindow"] = "未来7天：2026年11月25日 – 12月1日"
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
