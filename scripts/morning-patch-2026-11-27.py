#!/usr/bin/env python3
"""Morning-refresh patch builder for StockSite data.json (Fri 2026-11-27).

Collectors (all verified by the parent run):
- Finviz screen: LIVE browser fetch 7:29-7:30 AM ET, 102 results (premarket
  snapshot; membership churned during capture: BNY dropped, EPAM entered,
  PBLS dropped on re-check). Ranked 14 setups, scored on the last completed
  regular session (Wed Nov 25; Thu Nov 26 Thanksgiving, market closed).
  Prices/change are Nov 25 regular-session closes (Yahoo chart JSON), NOT
  premarket prints. relVolume = Nov 25 vol / mean of prior 4 sessions
  (quoteSummary 401-blocked, 4-session mean is the proxy). Distance from
  52w high from the Nov 25 CLOSE vs Yahoo 52w high. Option volumes are
  total Nov 25 contracts from optioncharts.io; front month Dec 18, 2026.
  Thin-print artifacts excluded: SPHR (+5.88% premarket on 138 shares),
  DOV (+2.68% on 7 shares). All 14 catalysts headline-verified.
  RENDERER SCHEMA NOTE (found this run): app.js normalizePotentialRow /
  renderPotentialTrades reads fields the old morning-patch entries never
  set (company, day, marketCap, relativeVolume, distanceHigh, optionExpiry,
  liquidity, catalyst, setup, optionsSource; scoreParts from components
  short keys relVol/distHigh/optLiq/catalyst/trend). Stored entries lacked
  them, so live cards rendered rel volume 0.00x, below-high 0.0%, expiry
  "Oct 16, 2026", liquidity Thin, empty catalyst/setup, score bars 0
  except catalyst. This patch populates the full renderer schema; the
  hardcoded "Oct. 16" in the score-note copy inside app.js is still stale
  (renderer text, not data — flagged, not edited here).
- History: Yahoo daily chart, Nov 25 bars, 62 watchlist tickers (SQ missing:
  Yahoo 404, Block renamed SQ -> XYZ; NO rename). SNDK patched from
  stockanalysis.com (Yahoo null close; O 71.32 H 73.77 L 67.02 C 73.61
  V 124,408,329). ^VIX/^VIX3M + 10 sector ETFs fetched for internals.
  SMI: series already ends at Nov 25 (998.84, +0.17, set by the Nov 25
  close refresh with documented inputs: 10:00 bar close 702.39, 15:00 bar
  close 715.72). The history collector's independent SPY 1m read gives
  998.71 (first30 +0.1288% using 10:00 price 703.53; lastHour +0.1705%
  using 15:00 price 715.48) — a bar-alignment difference (open vs close
  of the 10:00/15:00 1m bars), 0.13 apart. Stored 998.84 KEPT: it carries
  a verified, documented derivation (391 bars); the alternative is noted
  here, not substituted.
- Internals: F&G 15 Extreme Fear (Nov 25 close, CNN live Nov 25; mirror
  CSV 15.60 corroborates; CNN JSON 418-blocked Nov 27). VIX 28.29 / VIX3M
  26.29, ratio 0.93 backwardation (Yahoo closes, match stored). Put/call
  Nov 25 finals eq 0.64 idx 1.04 total 0.98 (YCharts live). AAII NEW week
  ending 11/25: 37.1/17.5/45.4 (posted despite Thanksgiving). Flows Nov 25
  session: SPY -$4.81B, QQQ +$2.90B, IWM -$0.57B (ETF Action, posted
  Nov 26). Breadth carried Nov 24 closes (Barchart text fetch serves Sep 2
  cached snapshots, 85-86 days stale): %>50d 55.06 %>200d 53.47, A/D
  1.49/+359; Nov 25 highs/lows held from Nov 25 live-browser read (NYSE
  28/144, Nasdaq 27/417). FedWatch FRESH live CME read Nov 27 7:36 AM ET
  (see fedwatch_2026-11-27.json): Dec 9 hike 99.2% (hold 0.8%), Jan 27
  second hike 63.8%; 8 meetings through Nov 17, 2027; EFFR carried 3.88
  (not shown on page). Sector breadth Nov 25 Yahoo finals.
  Macro: 29 events, Nov 27..Dec 23; dropped 7 past; REMOVED Dec 9 JOLTS
  (Sep+Oct) — BLS schedule refutes it (Sep JOLTS released Nov 3, Oct on
  Dec 1, Nov on Jan 5, 2027); added 6 (Advance Econ Indicators Nov 27,
  Construction Spending Dec 1, claims Dec 3/10/17, Flash PMI Dec 16).
- IV: optioncharts.io, 62 of 63 refreshed (30-day IV + rank + percentile
  from the IV block; FAQ text ignored). 1 carried: SQ (optioncharts now
  404s on SQ entirely; was the stale Sahakol page). Broad IV easing on
  Nov 25 (DELL IV crush post-earnings 102.38 -> 87.85, rank 90.03 -> 69.46;
  NVDA rank 79.64 -> 77.74; ADI rank 86.67 -> 72.53; VRT rank 92.92 ->
  78.44). UBER percentile unstable again (43.25 -> 48.02); stored as read.
- Expected moves recomputed from merged fresh IV (IV-formula fallback:
  30-day IV x sqrt(DTE/365) to the first Friday weekly expiry ON/AFTER
  the earnings date, DTE counted from Nov 27 — the expiry that captures
  the event; the literal on/before expiry falls before Dec 9/10 reports
  and cannot price the move).
- Analyst: 24 new items, all Nov 25 (DELL x7, ADI x7, MU/AVGO/AMD/AMAT
  UBS cuts, AMZN/META maintains, SNOW Citi cut, Wedbush initiations
  COIN/HOOD/SQ). Zero dupes vs the 9 stored Nov 25 items. Total 1182.
"""
import json
import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())
internals = json.loads((HID / "internals_2026-11-27.json").read_text())
fedwatch = json.loads((HID / "fedwatch_2026-11-27.json").read_text())
iva = json.loads((HID / "iv_part_a_2026-11-27.json").read_text())
ivb = json.loads((HID / "iv_part_b_2026-11-27.json").read_text())
analyst = json.loads((HID / "analyst_2026-11-27.json").read_text())
yahoo = json.loads((HID / "history_2026-11-27.json").read_text())
screen = json.loads((HID / "screen_2026-11-27.json").read_text())

RUN_STAMP = datetime.now(ZoneInfo("America/New_York")).strftime(
    "%b %-d, %Y %-I:%M %p ET").replace("  ", " ")
notes = [f"RUN_STAMP {RUN_STAMP}"]

# ---------- validation ----------
assert yahoo["date"] == "2026-11-25"
assert len(yahoo["bars"]) == 62, len(yahoo["bars"])
assert yahoo["missing"] == ["SQ"]
assert set(yahoo["bars"]) == {s["ticker"] for s in data["STOCKS"]} - {"SQ"}
iv_merged_raw = {}
for part in (iva["iv"], ivb["iv"]):
    for t, v in part.items():
        assert t not in iv_merged_raw, f"dup IV {t}"
        iv_merged_raw[t] = v
assert set(iv_merged_raw) == {s["ticker"] for s in data["STOCKS"]}
fresh = [t for t, v in iv_merged_raw.items() if v["status"] == "fresh"]
assert len(fresh) == 62, len(fresh)
assert iv_merged_raw["SQ"]["status"] == "carried"
assert (iv_merged_raw["SQ"]["iv"], iv_merged_raw["SQ"]["rank"],
        iv_merged_raw["SQ"]["percentile"]) == (
    data["IV_DATA"]["SQ"]["iv30"], data["IV_DATA"]["SQ"]["rank"],
    data["IV_DATA"]["SQ"]["percentile"])
for t, v in iv_merged_raw.items():
    if v["status"] == "fresh":
        assert 0 < v["iv"] < 300 and 0 <= v["rank"] <= 100, (t, v)
assert len(fedwatch["meetings"]) == 8
for m in fedwatch["meetings"]:
    assert abs(sum(o["pct"] for o in m["outcomes"]) - 100.0) < 0.5, m["decision"]
assert [m["decision"] for m in fedwatch["meetings"]] == \
    [m["decision"] for m in data["MARKET_INTERNALS"]["fedWatch"]["meetings"]]
assert set(fedwatch.keys()) == {"asof", "context", "effr", "effrAsOf", "meetings"}
assert fedwatch["effr"] == 3.88
macro = internals["macroEvents"]
assert len(macro) == 29, len(macro)
assert all(e["date"] >= "2026-11-27" for e in macro)
assert [e["date"] for e in macro] == sorted(e["date"] for e in macro)
for e in macro:
    assert set(e.keys()) == {"category", "categoryZh", "date", "impact",
                             "impactZh", "time", "title", "titleZh"}, e
assert analyst["totalNew"] == 24 and len(analyst["newItems"]) == 24
stored_keys = {(t, it["date"], it["firm"])
               for t, items in data["ANALYST_REVISIONS"].items()
               for it in items}
for it in analyst["newItems"]:
    assert it["date"] == "2026-11-25", it
    assert (it["ticker"], it["date"], it["firm"]) not in stored_keys, it
assert sum(len(v) for v in data["ANALYST_REVISIONS"].values()) == 1158
assert screen["resultCount"] == 102
assert len(screen["potential"]) == 14
for p in screen["potential"]:
    c = p["components"]
    assert c["relativeVolume"] + c["distanceFromHigh"] + c["optionLiquidity"] \
        + c["catalyst"] + c["trendStructure"] == p["score"], p["ticker"]
    assert p["catalyst"] and p["name"] and p["relVolume"] is not None
    assert p["frontMonthVol"] is not None and p["frontMonthOI"] is not None
notes.append("validation ok: IV 62 fresh / SQ carried, FedWatch 8 meetings "
             "fresh (Dec 9 hike 99.2%), macro 29 sorted Nov 27..Dec 23, "
             "analyst +24 (total 1182), screen 102 results / 14 ranked, "
             "history 62 Nov 25 bars + SQ missing, SMI kept 998.84 (see header)")

# ---------- IV_DATA (normalized to stored {iv30, rank, percentile}) ----------
iv = {}
for t, v in iv_merged_raw.items():
    if v["status"] == "fresh":
        iv[t] = {"iv30": v["iv"], "rank": v["rank"],
                 "percentile": v["percentile"]}
    else:
        iv[t] = dict(data["IV_DATA"][t])  # SQ carried last-good
assert len(iv) == 63

iv_source = (
    "Nov 27, 2026 · 62 of 63 refreshed from optioncharts.io (live overview "
    "pages, Nov 25 close data; 30-day IV, IV rank AND IV percentile all "
    "refreshed from the IV block); 1 carried last-good: SQ (optioncharts "
    "now returns 404 on SQ; Block now XYZ there, not applied pending the "
    "ticker-rename decision). Broad IV easing across most names on Nov 25 "
    "(DELL IV crush post-earnings 102.38 → 87.85, rank 90.03 → 69.46; NVDA "
    "rank 79.64 → 77.74; ADI rank 86.67 → 72.53; VRT rank 92.92 → 78.44). "
    "UBER percentile unstable again (43.25 → 48.02) — optioncharts "
    "percentiles look unstable for this name; stored as read. FAQ text on "
    "most pages quotes a different, higher IV rank than the structured IV "
    "block; IV-block values used throughout.")

# ---------- expected moves (recomputed from merged fresh IV) ----------
DTE = {"2026-12-01": ("2026-12-04", 7), "2026-12-02": ("2026-12-04", 7),
       "2026-12-09": ("2026-12-11", 14), "2026-12-10": ("2026-12-11", 14),
       "2026-12-14": ("2026-12-18", 21), "2026-12-17": ("2026-12-18", 21)}
exp_moves_new = {}
earn = []
for e in data["EARNINGS_DATES"]:
    e = dict(e)
    expiry, dte = DTE[e["date"]]
    mv = round(iv[e["ticker"]]["iv30"] * math.sqrt(dte / 365), 2)
    exp_moves_new[e["ticker"]] = mv
    e["expected_move"] = mv
    e["move_as_of"] = "Nov 27, 2026"
    e["move_method"] = (
        f"30-day IV × √(DTE/365) to Friday weekly expiry {expiry} "
        f"(DTE {dte} from Nov 27); optioncharts expiry-table % not readable "
        "in text fetch — IV-formula fallback per refresh rules")
    e["move_method_zh"] = "期权隐含预期波动（30日隐含波动率×√(DTE/365)）"
    earn.append(e)
assert [(e["date"], e["ticker"]) for e in earn] == [
    ("2026-12-01", "MRVL"), ("2026-12-02", "CRM"),
    ("2026-12-02", "SNOW"), ("2026-12-09", "ADBE"),
    ("2026-12-09", "AVGO"), ("2026-12-10", "COST"),
    ("2026-12-14", "ORCL"), ("2026-12-17", "MU")]
# cross-check against the collectors' independently computed moves
for t, mv in exp_moves_new.items():
    coll = (iva["expectedMoves"].get(t) or ivb["expectedMoves"].get(t))
    assert coll is not None, t
    coll_mv = coll.get("expectedMove", coll.get("expectedMovePct"))
    assert coll_mv == mv, (t, coll_mv, mv)
notes.append("expected moves recomputed from merged IV: " +
             str(exp_moves_new))

# ---------- SCREEN_SNAPSHOT (fresh live-browser screen, renderer schema) ----------
# Market caps from the Finviz live-browser table (7:29-7:30 AM ET).
MARKET_CAP = {"AMC": "2.94B", "ZS": "38.41B", "OKTA": "36.31B",
              "IBM": "232.78B", "AZO": "56.69B", "APO": "72.57B",
              "FNV": "49.19B", "APA": "15.56B", "TNGX": "4.35B",
              "RBLX": "40.61B", "RGLD": "21.24B", "TEL": "62.07B",
              "BB": "5.14B", "ARES": "45.06B"}


def liquidity_label(opt_vol, opt_oi):
    # Badge rule as stated on the site: High OI >= 50K and V/OI >= 15%;
    # Medium OI >= 10K and V/OI >= 8%; else Thin. Applied to TOTAL
    # option volume / total OI (the V/OI the card displays).
    if opt_oi is None or opt_vol is None or opt_oi == 0:
        return "Thin"
    ratio = opt_vol / opt_oi
    if opt_oi >= 50000 and ratio >= 0.15:
        return "High"
    if opt_oi >= 10000 and ratio >= 0.08:
        return "Medium"
    return "Thin"


potential = []
volumes = {}
for p in screen["potential"]:
    c = p["components"]
    comps = {"relativeVolume": c["relativeVolume"],
             "distanceFromHigh": c["distanceFromHigh"],
             "optionLiquidity": c["optionLiquidity"],
             "catalyst": c["catalyst"],
             "trendStructure": c["trendStructure"],
             # short keys actually read by app.js normalizePotentialRow
             "relVol": c["relativeVolume"],
             "distHigh": c["distanceFromHigh"],
             "optLiq": c["optionLiquidity"],
             "trend": c["trendStructure"]}
    entry = {
        "ticker": p["ticker"],
        "company": p["name"],
        "industry": "",
        "score": p["score"],
        "components": comps,
        "price": p["price"],
        "change": p["change"],
        "changePct": p["changePct"],
        "day": p["changePct"],
        "volume": p["volume"],
        "relVolume": p["relVolume"],
        "relativeVolume": p["relVolume"],
        "distanceFromHigh": p["distanceFromHigh"],
        "distanceHigh": abs(p["distanceFromHigh"]),
        "nearHighPct": p["nearHighPct"],
        "optionVolume": p["optionVolume"],
        "optionOI": p["optionOI"],
        "frontMonthVol": p["frontMonthVol"],
        "frontMonthOI": p["frontMonthOI"],
        "marketCap": "$" + MARKET_CAP[p["ticker"]],
        "trendLabel": "Above all SMAs",
        "optionExpiry": "Dec 18, 2026",
        "liquidity": liquidity_label(p["optionVolume"], p["optionOI"]),
        "catalyst": p["catalyst"],
        "why": p["why"],
        "note": p["note"],
        "setup": p["catalyst"],
        "optionsSource": "https://optioncharts.io/options/" + p["ticker"],
    }
    potential.append(entry)
    volumes[p["ticker"]] = p["optionVolume"]

screen_snapshot = {
    "updated": "Nov 27, 2026 7:30 AM ET",
    "scanTime": "2026-11-27 ~7:30 AM (premarket)",
    "resultCount": 102,
    "resultTime": "2026-11-27 ~7:30 AM (premarket)",
    "source": "https://finviz.com/screener?v=211&f=cap_midover,sh_opt_option,"
              "ta_change_u,ta_highlow52w_b10h,ta_sma20_pa,ta_sma200_pa,"
              "ta_sma50_pa&ft=3",
    "optionsAsOf": "Nov 25, 2026 (optioncharts.io)",
    "note": ("Fetched Fri Nov 27, 2026 7:29-7:30 AM ET. Finviz v=111 Overview "
             "via live browser: 102 results (membership churned during "
             "capture — BNY dropped, EPAM entered, PBLS dropped on re-check — "
             "a premarket snapshot, not a settled close-based screen). "
             "Prices/change are Nov 25 regular-session closes (Yahoo chart "
             "JSON), NOT premarket prints; premarket volumes are tiny (SPHR "
             "138 shares, DOV 7 shares), so relVolume is scored from Nov 25 "
             "regular-session volume / mean of prior 4 sessions. Distance "
             "from 52-week high is computed from the Nov 25 CLOSE vs the "
             "Yahoo 52w high. Option volumes are total Nov 25 contracts "
             "traded from optioncharts.io overview pages; front month "
             "Dec 18, 2026. Thin-print artifacts excluded: SPHR (+5.88% "
             "premarket on 138 shares), DOV (+2.68% on 7 shares). All 14 "
             "catalysts verified via headline search. AMC tops (79): Hunger "
             "Games opening weekend; ZS upside capped by the CrowdStrike "
             "all-stock deal terms."),
    "potential": potential,
    "volumes": volumes,
}
notes.append("SCREEN_SNAPSHOT fresh: 102 results, 14 ranked (AMC 79 top, "
             "ZS/OKTA 74, IBM 73); entries now populate the full renderer "
             "schema (company/day/marketCap/relativeVolume/distanceHigh/"
             "optionExpiry/liquidity/catalyst/setup/optionsSource + "
             "components short keys)")

# ---------- HISTORY (Nov 25 bars for HISTORY tickers only) ----------
history = {t: list(bars) for t, bars in data["HISTORY"].items()}
appended = 0
for t, bar in yahoo["bars"].items():
    if t not in history:
        continue
    nb = {"d": "2026-11-25", "o": bar["o"], "h": bar["h"], "l": bar["l"],
          "c": bar["c"], "v": bar["v"]}
    existing = {b["d"] for b in history[t]}
    if nb["d"] not in existing:
        history[t] = sorted(history[t] + [nb], key=lambda b: b["d"])
        appended += 1
notes.append(f"HISTORY appended {appended} Nov 25 bars (62 watchlist ex SQ; "
             "sector-ETF / ^VIX / ^VIX3M bars are not HISTORY keys — they "
             "feed sectorBreadth / vixTerm only); missing: SQ (Yahoo 404, "
             "no rename); 12 earnings-calendar names untouched "
             "(enrich-calendar-stocks.py tops them up); SNDK bar patched "
             "from stockanalysis.com")

# ---------- MARKET_INTERNALS (read-modify-write whole object) ----------
mi = json.loads(json.dumps(data["MARKET_INTERNALS"]))  # deep copy
mi["fearGreed"] = internals["fearGreed"]
mi["vixTerm"] = internals["vixTerm"]
mi["putCall"] = internals["putCall"]
mi["breadth"] = internals["breadth"]  # carried Nov 24 closes, as-of unavailable
mi["aaii"] = internals["aaii"]  # NEW week ending Nov 25
mi["flows"] = internals["flows"]  # Nov 25 session
mi["flowsAsOf"] = internals["flowsAsOf"]
mi["fedWatch"] = {k: fedwatch[k] for k in
                  ("asof", "context", "effr", "effrAsOf", "meetings")}
# SMI: series already ends at Nov 25 (998.84, kept — see header). Unchanged.
assert mi["smi"]["latest"] == 998.84
notes.append("internals: F&G 15 Extreme Fear (Nov 25 close), VIX 28.29/26.29 "
             "backwardation 0.93, P/C eq 0.64 idx 1.04 total 0.98 (Nov 25 "
             "finals), AAII NEW 37.1/17.5/45.4 (week ending Nov 25), flows "
             "Nov 25 SPY -$4.81B / QQQ +$2.90B / IWM -$0.57B, breadth "
             "carried (Barchart stale), SMI kept 998.84, FedWatch FRESH "
             "live CME Dec 9 hike 99.2% / Jan 27 2nd hike 63.8%")

# ---------- SECTOR_BREADTH (Yahoo Nov 25 finals) ----------
sector_breadth = []
for s in internals["sectorBreadth"]:
    sector_breadth.append({
        "etf": s["etf"], "name": s["name"], "nameZh": s["nameZh"],
        "change": s["change"], "close": s["close"], "previous": s["previous"],
        "url": s.get("url", f"https://finnhub.io/?q=%22{s['etf']}%22"),
    })
notes.append("sectorBreadth (Nov 25 finals, Yahoo daily closes): " +
             str([(s["etf"], s["change"]) for s in sector_breadth]))

# ---------- EXPECTED_MOVES ----------
exp_moves = dict(data["EXPECTED_MOVES"])
for t, mv in exp_moves_new.items():
    exp_moves[t] = mv

# ---------- ANALYST_REVISIONS (prepend new, newest-first) ----------
analyst_revs = json.loads(json.dumps(data["ANALYST_REVISIONS"]))
for it in analyst["newItems"]:
    item = {"date": it["date"], "firm": it["firm"], "action": it["action"],
            "note": it.get("note", ""), "source": it["source"]}
    analyst_revs.setdefault(it["ticker"], []).insert(0, item)
total_analyst = sum(len(v) for v in analyst_revs.values())
assert total_analyst == 1182, total_analyst
notes.append("analyst +24 (DELL x7, ADI x7, UBS cuts MU/AVGO/AMD/AMAT, "
             "AMZN/META maintains, SNOW Citi, Wedbush COIN/HOOD/SQ); "
             f"total {total_analyst}")

# ---------- ASOF (read-modify-write) ----------
asof = dict(data["ASOF"])
asof["sectorBreadth"] = RUN_STAMP
asof["macro"] = RUN_STAMP
asof["expectedMoves"] = RUN_STAMP

# ---------- I18N_OVERRIDES (read-modify-write whole object) ----------
i18n = json.loads(json.dumps(data["I18N_OVERRIDES"]))
i18n["en"]["tradesDesc"] = (
    "14 ranked setups from the November 27 Finviz screen, with verified "
    "front-month options activity.")
i18n["zh"]["tradesDesc"] = (
    "根据 11 月 27 日的 Finviz 筛选，列出14个已验证近月期权活跃度的排序机会。")
i18n["en"]["ivAsOf"] = (
    "Updated Nov 27, 2026 · optioncharts.io 30-day IV readings "
    "(62 of 63 refreshed; 1 carried last-good); stale source pages are "
    "flagged in ticker detail")
i18n["zh"]["ivAsOf"] = (
    "更新于 11 月 27 日 · optioncharts.io 隐含波动率数据（63 个标的中 62 个"
    "已刷新，1 个沿用上次有效值）")
i18n["en"]["calendarDesc"] = f"Macro calendar refreshed {RUN_STAMP}"
i18n["zh"]["calendarDesc"] = f"宏观日历已于 {RUN_STAMP} 更新"
i18n["en"]["sevenDayWindow"] = "Next 7 days: Nov 27 – Dec 3, 2026"
i18n["zh"]["sevenDayWindow"] = "未来7天：2026年11月27日 – 12月3日"
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
    "ANALYST_REVISIONS": analyst_revs,
    "ASOF": asof,
    "I18N_OVERRIDES": i18n,
}
json.dump(patch, open("/tmp/patch.json", "w"))
print("\n".join(notes))
print("patch keys:", sorted(patch.keys()))
print("analyst total entries:", total_analyst)
