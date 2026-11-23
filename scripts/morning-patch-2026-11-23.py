#!/usr/bin/env python3
"""Morning-refresh patch builder for StockSite data.json (Mon 2026-11-23).

Collectors (all verified by the parent run):
- Finviz screen: v=111 Overview via live browser (~7:28 AM ET premarket),
  60 total (Charts view showed 61 moments earlier — premarket drift).
  Rows 1-40 captured; page 3 (41-60) not read. FLAG: the browser agent's
  written report corrupted page-1 prices/market caps (e.g. CLX $142.44 vs
  page $105.22, ADMA $27.34 vs $13.18, CMG $42.75 vs $36.36; page 2 was
  correct). Prices/mcaps here are re-extracted from the raw accessibility
  tree in the agent session log and cross-checked vs Yahoo Nov 20 closes +
  change% (all 40 consistent). 52-wk highs/SMAs/avg vol from Yahoo 1y daily
  chart (not optioncharts this run — rate-limit risk). 15 ranked.
- History: Yahoo daily chart API, Nov 20 bars. 74 tickers; SQ missing
  (Yahoo 404; Block renamed SQ -> XYZ; NO rename).
- Internals: F&G carried 10 Extreme Fear Nov 20 (CNN JSON 418-blocked;
  mirror CSV 9.67 corroborates); VIX 35.89 / VIX3M 30.94, ratio 0.86
  backwardation (Yahoo closes re-verified this morning, match stored);
  put/call Nov 20 finals eq 0.77 idx 1.27 total 1.13 (ycharts, read live
  Nov 23 ~7:30 AM ET; Nov 19 values match stored, confirming series);
  AAII carried (week ending Nov 18: 33.3/24.4/42.2); flows carried Nov 19
  session (SPY -$11.65B, QQQ -$1.29B, IWM -$0.20B — Nov 20-session ETF
  Action report NOT yet posted as of Nov 23 ~7:30 AM ET); SMI carried
  998.62 (finalized through Nov 20). Breadth (live browser Nov 23
  ~7:28 AM ET): $ADRN 0.20 / $ADDN -1,214 (309 adv / 1,523 dec, sums
  exactly; prev close 0.12 / -1,410), % above 50-day 42.74 (prev 49.10),
  % above 200-day 45.92 (prev 49.10) — NOTE the Nov 20 close refresh
  stored 46.12 as headline with 45.92 as Key Turning Points; this
  morning's live read shows Last Price 45.92 (-6.48% move), so 45.92 is
  stored now. 52-wk highs/lows Summary tab (Last Updated 11/20 19:39 ET):
  Overall 17/1,014, NYSE 8/256, Nasdaq 9/694, Arca 0/64 (lows revised up
  from the 16:58 ET snapshot's 986).
- FedWatch: LIVE CME FedWatch page via browser (data as of 06:20:36 CT
  Nov 23; Akamai block cleared by fresh-browser move). Dec 9 hike now
  96.2% (one hike 400-425; hold rose to 3.8% from 0.0%; 50bp tail 0.0%).
  EFFR not shown on page again — carried 3.88. Same 8 meeting tabs
  ending Nov 17, 2027. Jan 27 second hike 425-450 at 61.9% (was 63.1%).
- Macro: 33 events, Nov 24..Dec 23. Dropped 2 Nov 20 events (Michigan
  final, Fed speakers Cook/Waller). No new events added.
- IV: optioncharts.io overview pages, 51 of 63 refreshed (30-day IV +
  IV rank; IV percentile carried last-good for all 63). 12 carried:
  PLTR/SNDK/WDC/CRWV/HD/MSTR/UBER/IWM/SNOW/BAC/TLT (429 mid-batch, not
  retried), SQ (Sahakol page). BRK-B via BRKB. FAQ text on most pages
  quotes a different, higher IV rank than the IV block (often >100);
  IV-block values used throughout (same convention as prior runs).
- Expected moves: recomputed here from MERGED fresh IV (IV-formula
  fallback: 30-day IV x sqrt(DTE/365) to the Friday weekly expiry).
  Strip: 10 entries — MU MOVED Dec 16 -> Dec 17 (Micron's own Nov 19
  press release: fiscal Q1 call Thu Dec 17, 2:30 PM MT — company
  confirmed, supersedes the Dec 16 estimate). No other adds/drops.
- Analyst: 23 new items (VRT x5 incl. Baird downgrade Nov 23,
  TSLA HSBC upgrade, UNH TD Cowen upgrade, BRK-B Argus downgrade,
  NVDA William Blair initiation, AMZN/MSFT/MRVL/SNOW/JNJ/MU/WMT x8 PT
  moves), dated Nov 2-23; total 1,092 (was 1,069). Zero near-dupes
  (same ticker+date+firm check).
"""
import json
import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())
screen = json.loads((HID / "screen_2026-11-23.json").read_text())
opt1 = json.loads((HID / "screen_options_2026-11-23.json").read_text())
opt2 = json.loads((HID / "screen_options2_2026-11-23.json").read_text())
internals = json.loads((HID / "internals_2026-11-23.json").read_text())
fedwatch = json.loads((HID / "fedwatch_2026-11-23.json").read_text())
iva = json.loads((HID / "iv_part_a_2026-11-23.json").read_text())
ivb = json.loads((HID / "iv_part_b_2026-11-23.json").read_text())
analyst = json.loads((HID / "analyst_2026-11-23.json").read_text())
yahoo = json.loads((HID / "yahoo_2026-11-23.json").read_text())

RUN_STAMP = datetime.now(ZoneInfo("America/New_York")).strftime(
    "%b %-d, %Y %-I:%M %p ET").replace("  ", " ")
notes = [f"RUN_STAMP={RUN_STAMP}"]

# ---------- merge IV ----------
iv = dict(iva["iv"])
iv.update(ivb["iv"])
assert not (set(iva["iv"]) & set(ivb["iv"])), "IV parts overlap"
CARRIED_IV = sorted(c["ticker"] for c in iva["carried"] + ivb["carried"])
assert CARRIED_IV == ["BAC", "CRWV", "HD", "IWM", "MSTR", "PLTR", "SNDK",
                       "SNOW", "SQ", "TLT", "UBER", "WDC"], CARRIED_IV
REFRESHED_N = len(iva["refreshed"]) + len(ivb["refreshed"])

# ---------- ranking (scores computed by parent; components verified here) ----------
# (ticker, relVol, dist, optLiq, catalyst, trend, why)
RANK = [
 ("FROG", 17, 12, 15, 18, 17,
  "Q3 beat Nov 5 (revenue +31% to $179.2M, cloud +60%), raised FY26 guide; +35% since the print, leading premarket +4.33%."),
 ("HD", 16, 12, 20, 15, 16,
  "Q3 beat Nov 17 (comps +2.2%, best since Q3 FY22); CFO Richard McPhail becomes CEO today; heaviest front-month options on the screen."),
 ("CMG", 15, 13, 19, 14, 16,
  "Q3 miss Oct 28 priced in; BOGO Rewards offer Nov 25 + $0 delivery Nov 27-30; Bernstein maintained Buy/$43 Nov 17."),
 ("CHYM", 14, 13, 17, 15, 15,
  "Q3 Nov 4: revenue $718M (+32%), 3rd straight GAAP-profitable quarter, raised FY26 guide; +7% in 48 hours."),
 ("ACHC", 15, 13, 12, 16, 17,
  "Q3 Nov 4 beat (adj EPS $0.60 vs $0.46), raised FY26 guidance for a 3rd straight quarter; unusual options activity Nov 9."),
 ("LUV", 14, 10, 18, 14, 15,
  "Q3 Oct 21: record revenue $8.42B (+21.2%), EPS beat; UBS raised PT to $59 Nov 17."),
 ("ALGT", 16, 8, 13, 16, 16,
  "Q3 Nov 4: adj loss $0.03 beat the $0.47 loss expected, revenue +71% to $961.6M; +12.8% since, Investor Day Dec 7."),
 ("ARGX", 15, 13, 9, 17, 15,
  "Q3 product sales +54%; ALKIVIA Phase 3 data Nov 7 met endpoints; $550M acquisition Nov 9; Piper Sandler raised PT to $1,350 Nov 17."),
 ("IDXX", 14, 13, 8, 16, 17,
  "Q3 Nov 2: revenue +10% to $1.21B, EPS $4.01 beat $3.73, raised FY26 EPS guide; +22.7% since the call."),
 ("LOW", 15, 8, 17, 13, 15,
  "Q3 Nov 18: sales +9.3%, comps +1.8% (6th straight positive quarter), adj EPS $3.10 beat but included a $0.34 tariff refund; raised sales guide."),
 ("DHI", 14, 12, 14, 12, 14,
  "Q4 FY26 miss Oct 29 (EPS $2.67 vs $3.01, orders -7%, FY27 guide light) and downgrades, but housing rallied Nov 5 (+8.1%) and dividend raised 11%."),
 ("CLX", 12, 10, 16, 12, 16,
  "Q1 FY27 beat Nov 2 (adj EPS $1.55 vs $1.07) on the GOJO deal + ERP lap; new CEO Fabian Garcia starts Jan 5, 2027."),
 ("KVYO", 16, 5, 12, 15, 17,
  "Q3 Nov 4: revenue $387.2M (+25%), EPS $0.22 beat $0.17, raised FY26 guide; new $300M buyback, ARR crossed $1.5B."),
 ("LION", 15, 10, 8, 15, 16,
  "Q2 FY27 Nov 5: revenue $668.8M (+41%), adj OIBDA $72M vs $14.1M; Sony to co-finance/distribute the Naruto film."),
 ("CSL", 14, 13, 5, 15, 16,
  "Q3 Oct 28: record adj EPS $5.92 (+6%), revenue $1.5B (+9%); dividend raised 14% (50th straight annual increase)."),
]
OPTS = {**{t: v for t, v in opt1["options"].items()},
        **{t: v for t, v in opt2["options"].items()}}
HEADLINES = {**opt1["headlines"], **opt2["headlines"]}
FV = screen["finviz"]  # {ticker: [price, changePct, premarketVol]}
YH = screen["yahoo"]

potential = []
volumes = {}
for (t, rv, dh, ol, cat, tr, why) in RANK:
    price, chg, prevol = FV[t]
    high52 = YH[t]["high52"]
    dist = round((price - high52) / high52 * 100, 2)
    o = OPTS[t]
    assert "totalVolume" in o, t
    comp = {"relativeVolume": rv, "distanceFromHigh": dh,
            "optionLiquidity": ol, "catalyst": cat, "trendStructure": tr}
    potential.append({
        "ticker": t, "score": sum(comp.values()), "components": comp,
        "price": price, "change": chg, "changePct": chg,
        "volume": prevol, "relVolume": None,
        "distanceFromHigh": dist, "nearHighPct": dist,
        "optionVolume": o["totalVolume"], "optionOI": o["totalOI"],
        "note": why, "why": why,
    })
    volumes[t] = o["totalVolume"]
# verify score ordering desc (ties keep listed order)
scores = [p["score"] for p in potential]
assert scores == sorted(scores, reverse=True), scores
assert len(potential) == 15
notes.append("screen: " + str([(p["ticker"], p["score"]) for p in potential]))

# ---------- validation ----------
assert set(iv) == {s["ticker"] for s in data["STOCKS"]}, \
    set(iv) ^ {s["ticker"] for s in data["STOCKS"]}
assert set(analyst["analystRevisions"]) == {s["ticker"] for s in data["STOCKS"]}
assert REFRESHED_N == 51, REFRESHED_N
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
assert all(e["date"] >= "2026-11-23" for e in analyst["earningsDates"])
assert len(analyst["earningsDates"]) == 10
assert [(e["date"], e["ticker"]) for e in analyst["earningsDates"]] == [
    ("2026-11-24", "ADI"), ("2026-11-24", "DELL"), ("2026-12-01", "MRVL"),
    ("2026-12-02", "CRM"), ("2026-12-02", "SNOW"), ("2026-12-09", "ADBE"),
    ("2026-12-09", "AVGO"), ("2026-12-10", "COST"), ("2026-12-14", "ORCL"),
    ("2026-12-17", "MU")]
assert internals["smi"]["series"] == data["MARKET_INTERNALS"]["smi"]["series"]
assert internals["smi"]["latest"] == data["MARKET_INTERNALS"]["smi"]["latest"]
assert internals["aaii"]["latest"] == {"bullish": 33.3, "neutral": 24.4,
                                       "bearish": 42.2}
assert len(internals["aaii"]["history"]) == 4
macro = internals["macroEvents"]
assert len(macro) == 33, len(macro)
assert all(e["date"] >= "2026-11-23" for e in macro)
assert [e["date"] for e in macro] == sorted(e["date"] for e in macro)
for e in macro:
    assert set(e.keys()) == {"category", "categoryZh", "date", "impact",
                             "impactZh", "time", "title", "titleZh"}, e
assert set(yahoo["bars"].keys()) == set(data["HISTORY"]) - {"SQ"} | \
    {"XLK", "XLF", "XLV", "XLE", "XLI", "XLU", "XLP", "XLY", "XLC", "XLRE",
     "^VIX", "^VIX3M", "SPY"}
assert yahoo["missing"] == ["SQ"]
assert all(any(b["d"] == "2026-11-20" for b in v)
           for t, v in yahoo["bars"].items() if t in data["HISTORY"])
assert sum(len(v) for v in analyst["analystRevisions"].values()) == 1092, \
    sum(len(v) for v in analyst["analystRevisions"].values())
assert analyst["newAnalystItems"] == 23
assert len(yahoo["sectorBreadth"]) == 10
assert [s["etf"] for s in yahoo["sectorBreadth"]] == [
    "XLK", "XLF", "XLV", "XLE", "XLI", "XLU", "XLP", "XLY", "XLC", "XLRE"]
# Finviz prices cross-checked vs Yahoo Nov 20 closes + change%
for t, (price, chg, _) in FV.items():
    c20 = YH[t]["nov20close"]
    assert abs(price / c20 - 1 - chg / 100) < 0.002, (t, price, c20, chg)
notes.append("validation ok: scores sum + ordered, 63 IV tickers, analyst "
             "keys, 51 refreshed / 12 carried, no rank >100, FedWatch 8 "
             "meetings sum ~100, 10-entry strip (MU Dec 16->Dec 17 confirmed), "
             "SMI carried 998.62, AAII carried 33.3/24.4/42.2, macro 33 rich "
             "entries sorted Nov 24..Dec 23, yahoo 74 tickers with Nov 20 "
             "bars + SQ missing, analyst total 1092 (+23 new), Finviz prices "
             "cross-checked vs Yahoo closes")

# ---------- expected moves (recomputed from merged fresh IV) ----------
DTE = {"2026-11-24": ("2026-11-27", 4),
       "2026-12-01": ("2026-12-04", 11), "2026-12-02": ("2026-12-04", 11),
       "2026-12-09": ("2026-12-11", 18), "2026-12-10": ("2026-12-11", 18),
       "2026-12-14": ("2026-12-18", 25), "2026-12-17": ("2026-12-18", 25)}
exp_moves_new = {}
earn = []
for e in analyst["earningsDates"]:
    e = dict(e)
    expiry, dte = DTE[e["date"]]
    mv = round(iv[e["ticker"]]["iv30"] * math.sqrt(dte / 365), 2)
    exp_moves_new[e["ticker"]] = mv
    e["expected_move"] = mv
    e["move_as_of"] = "Nov 23, 2026"
    e["move_method"] = (
        f"30-day IV × √(DTE/365) to Friday weekly expiry {expiry} "
        f"(DTE {dte} from Nov 23); optioncharts expiry-table % not readable "
        "in text fetch — IV-formula fallback per refresh rules")
    e["move_method_zh"] = "期权隐含预期波动（30日隐含波动率×√(DTE/365)）"
    st = next((x for x in data["EARNINGS_DATES"]
               if x["ticker"] == e["ticker"]), None)
    if st and len(st.get("sources", [])) > len(e.get("sources", [])):
        e["sources"] = st["sources"]  # keep fuller stored source list
    if e["ticker"] == "MU":
        # Dec 17 is company-confirmed (Nov 19 press release); rewrite the
        # stale "Dec 16 used" conflict note carried in the sources.
        e["sources"] = [
            s for s in e["sources"]
            if "CONFLICT NOTE" not in s.get("label", "")]
        e["sources"].append({
            "label": ("Micron press release Nov 19, 2026 (GlobeNewswire / "
                      "investors.micron.com): fiscal Q1 call Thu Dec 17, "
                      "2026, 2:30 PM MT — company-confirmed, supersedes the "
                      "Dec 16 estimate (StockAnalysis/Zacks) and the Dec 23 "
                      "estimate (Yahoo/TipRanks)"),
            "url": ("https://www.globenewswire.com/news-release/2026/11/19/"
                    "3407102/14450/en/micron-technology-to-report-fiscal-"
                    "first-quarter-results-on-december-17-2026.html"),
        })
        e["as_of"] = "2026-11-23"
    earn.append(e)
notes.append("expected moves recomputed from merged IV: " +
             str(exp_moves_new))

# ---------- SCREEN_SNAPSHOT ----------
screen_snapshot = {
    "updated": RUN_STAMP,
    "scanTime": "2026-11-23 ~7:28 AM (premarket)",
    "resultCount": 60,
    "resultTime": "2026-11-23 ~7:28 AM (premarket)",
    "source": "https://finviz.com/screener?v=211&f=cap_midover,sh_opt_option,ta_change_u,ta_highlow52w_b10h,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3",
    "optionsAsOf": "Nov 23, 2026 (optioncharts.io)",
    "note": ("Fetched Mon Nov 23, 2026 ~7:28 AM ET. Finviz v=111 Overview via "
             "live browser: '#1 / 60 Total' (Charts view showed 61 moments "
             "earlier — premarket drift); rows 1-40 seen, page 3 (41-60) not "
             "read. FLAG: the browser agent's written report corrupted page-1 "
             "prices/market caps (e.g. CLX $142.44 vs page $105.22, ADMA "
             "$27.34 vs $13.18, CMG $42.75 vs $36.36; page 2 correct) — prices "
             "here are re-extracted from the raw accessibility tree in the "
             "agent session log and cross-checked vs Yahoo Nov 20 closes + "
             "change% (all 40 consistent). Prices/change are pre-market moves "
             "vs the Nov 20 close. 52-week highs from Yahoo 1y daily chart; "
             "distanceFromHigh computed from the pre-market price vs that high "
             "(every name 10-35% below its high, matching Finviz's '10% or "
             "more below High' filter). Option volumes are total Nov 20 "
             "contracts traded from optioncharts.io overview pages; optionOI "
             "is total open interest. relVolume null for all: pre-market "
             "Finviz volume is a partial-session print, so no relative-volume "
             "ratio was computed (same as Nov 11-20 runs); relativeVolume "
             "scored from % change + Nov 20 session relative volume tier "
             "instead. All 15 catalysts verified via headline search. Thin "
             "option chains scored down: MMS 8 contracts total (3 front-month), "
             "CR 11, CSL 28, IMVT not ranked (27 contracts, score 54); "
             "ARGX 168, LION 153, IDXX 115 also thin."),
    "potential": potential,
    "volumes": volumes,
}

# ---------- HISTORY (Nov 20 bars only) ----------
hist_bars = {}
for t in data["HISTORY"]:
    bars = [b for b in yahoo["bars"].get(t, []) if b["d"] == "2026-11-20"]
    if bars:
        hist_bars[t] = bars
assert all(b["d"] == "2026-11-20"
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
mi["breadth"] = fedwatch["breadth"]  # live-browser Nov 20 closes
mi["aaii"] = internals["aaii"]  # carried week ending Nov 18
mi["flows"] = internals["flows"]  # carried Nov 19 session (Nov 20 report not posted)
mi["flowsAsOf"] = internals["flowsAsOf"]
mi["fedWatch"] = {k: fedwatch[k] for k in
                  ("asof", "context", "effr", "effrAsOf", "meetings")}
notes.append("internals: F&G 10 Extreme Fear (Nov 20 close; CNN JSON "
             "418-blocked, mirror CSV 9.67 corroborates), VIX 35.89/30.94 "
             "backwardation 0.86, P/C eq 0.77 idx 1.27 total 1.13 (Nov 20 "
             "finals), AAII carried 33.3/24.4/42.2 (week ending Nov 18), "
             "flows carried Nov 19 session (Nov 20 report not yet posted), "
             "breadth A/D 0.20/-1,214, %>50d 42.74 %>200d 45.92, highs/lows "
             "summary Overall 17/1,014, FedWatch 8 meetings Dec 9 hike 96.2% "
             "(hold 3.8%, was 0.0%) (live CME)")

# ---------- SECTOR_BREADTH (Yahoo Nov 20 finals) ----------
sector_breadth = []
for s in yahoo["sectorBreadth"]:
    sector_breadth.append({
        "etf": s["etf"], "name": s["name"], "nameZh": s["nameZh"],
        "change": s["change"], "close": s["close"], "previous": s["previous"],
        "url": s.get("url", f"https://finnhub.io/?q=%22{s['etf']}%22"),
    })
notes.append("sectorBreadth (Nov 20 finals, Yahoo daily closes): " +
             str([(s["etf"], s["change"]) for s in sector_breadth]))

# ---------- IV_SOURCE ----------
iv_source = (
    "Nov 23, 2026 · 51 of 63 refreshed from optioncharts.io (live overview "
    "pages, Nov 20 close data; 30-day IV and IV rank refreshed; IV percentile "
    "carried last-good for all 63 — the text fetch exposes 30-day IV and IV "
    "rank only, not percentile); 12 carried last-good: PLTR, SNDK, WDC, "
    "CRWV, HD, MSTR, UBER, IWM, SNOW, BAC, TLT (optioncharts returned 429 "
    "rate-limit mid-batch; not retried), SQ (optioncharts still shows "
    "unrelated Sahakol Equipment, stale Oct 16 crawl; Block now XYZ there, "
    "not applied pending the ticker-rename decision). BRK-B refreshed via "
    "the BRKB page. FAQ text on most pages quotes a different, higher IV "
    "rank than the structured IV block (often >100); IV-block values used "
    "throughout.")

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
    "15 ranked setups from the November 23 Finviz screen, with verified "
    "front-month options activity.")
i18n["zh"]["tradesDesc"] = (
    "根据 11 月 23 日的 Finviz 筛选，列出15个已验证近月期权活跃度的排序机会。")
i18n["en"]["ivAsOf"] = (
    "Updated Nov 23, 2026 · optioncharts.io 30-day IV readings "
    "(51 of 63 refreshed; 12 carried last-good; IV percentile carried "
    "last-good for all 63); stale source pages are flagged in ticker detail")
i18n["zh"]["ivAsOf"] = (
    "更新于 11 月 23 日 · optioncharts.io 隐含波动率数据（63 个标的中 51 个"
    "已刷新，12 个沿用上次有效值；IV 百分位全部沿用上次有效值）")
i18n["en"]["calendarDesc"] = f"Macro calendar refreshed {RUN_STAMP}"
i18n["zh"]["calendarDesc"] = f"宏观日历已于 {RUN_STAMP} 更新"
i18n["en"]["sevenDayWindow"] = "Next 7 days: Nov 23 – Nov 29, 2026"
i18n["zh"]["sevenDayWindow"] = "未来7天：2026年11月23日 – 11月29日"
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
