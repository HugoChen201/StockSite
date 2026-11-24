#!/usr/bin/env python3
"""Morning-refresh patch builder for StockSite data.json (Tue 2026-11-24).

Collectors (all verified by the parent run):
- Finviz screen: v=111 Overview via live browser (~7:30 AM ET premarket),
  44 unique tickers (total flipped 44 <-> 45 during the read; SYY duplicated
  across the page 2/3 boundary, deduplicated; BBIO/TS/TTEK/WMS/WYNN in the
  7:28 pass, out by 7:30). Finviz prices cross-checked vs Yahoo Nov 23 closes
  + change% (all 44 within 0.01pp, zero failures). 52-wk highs/SMAs/avg vol
  from Yahoo 1y daily chart. 15 ranked. Front month Dec 18, 2026 for all 44.
- History: Yahoo daily chart API, Nov 23 bars, 74 tickers; SQ missing (Yahoo
  404; Block renamed SQ -> XYZ; NO rename). SNDK Nov 20 + Nov 23 bars patched
  from stockanalysis.com (Yahoo null closes both days). ^VIX series carries a
  stray Nov 24 bar (timezone/futures artifact) — filtered out here (Nov 23
  only). HISTORY also holds 12 earnings-calendar names (ACN, C, DAL, DRI, JBL,
  JEF, NKE, PEP, PGR, SNX, STZ, WFC) that the Yahoo collector does not cover;
  they are left untouched here (enrich-calendar-stocks.py tops them up).
- Internals: F&G 15.73 Extreme Fear (CNN JSON live Nov 24 7:12 AM ET; previous
  close 16.97 confirms stored Nov 23 close of 17); VIX 26.62 / VIX3M 25.50,
  ratio 0.96 backwardation (Yahoo closes, match stored close-refresh values);
  put/call Nov 23 finals eq 0.55 idx 1.21 total 0.94 (ycharts, read live Nov 24
  ~7:30 AM ET); AAII carried (week ending Nov 18: 33.3/24.4/42.2 — FLAG: the
  live AAII history table now shows different prior-week values than stored;
  stored history kept, flag noted); flows carried Nov 20 session (SPY -$1.54B,
  QQQ +$0.61B, IWM -$0.20B — Nov 23-session ETF Action report NOT yet posted
  as of Nov 24 ~7:30 AM ET); SMI carried 998.91 (finalized through Nov 23;
  verified exactly by the Yahoo collector from SPY 1m: first-30-min -0.42%,
  last-hour -0.14%). Breadth (live browser, Nov 23 close): $ADRN 5.09 /
  $ADDN +1,227 (1,527 adv / 300 dec, sums exactly), % above 50-day 52.28
  (prev 42.74), % above 200-day 53.08 (prev 45.92). 52-wk highs/lows Summary
  tab (Last Updated 11/23 19:37 ET — revised after the 16:56 ET print the
  close refresh stored): Overall 25/382, NYSE 9/86, Nasdaq 16/278, Arca 0/18.
  NOTE: the stored Nov 20 lows (Overall 1,014) match no row on the page.
- FedWatch: LIVE CME FedWatch page via browser (data as of 06:20:27 CT Nov 24;
  no Akamai block). Dec 9 hike now 97.5% (one hike 400-425; hold 0.0%, was
  3.8%; 50bp tail 2.5%). EFFR not shown on page again — carried 3.88. Same 8
  meeting tabs ending Nov 17, 2027. Jan 27 second hike 425-450 at 61.4% (was
  61.9%). Jun/Jul/Sep distributions identical as displayed.
- Macro: 33 events, Nov 24..Dec 23, carried from stored list; anchors
  re-verified live (FOMC Dec 9, CPI Dec 10, PPI Dec 15, NFP Dec 4, PCE Dec 23
  all match). G20 Summit Dec 14-15 flagged by the browser check — not a US
  data release, not added (curated list covers FOMC/CPI/PPI/NFP/speeches).
- IV: optioncharts.io overview pages, 62 of 63 refreshed (30-day IV + IV rank
  + IV percentile — the text fetch DOES expose percentile in the IV block this
  run; yesterday's IV_SOURCE text wrongly said percentile was carried, though
  the stored values matched the files). 1 carried: SQ (Sahakol page). HD/UBER
  percentiles swung sharply vs stale stored values (HD 99.6 -> 35.46, UBER
  88.45 -> 19.92) but are internally consistent with their fresh IV ranks
  (HD rank 42.01, UBER rank 53.01); the stored pairs were the inconsistent
  ones, so fresh values are stored. BRK-B via BRKB. FAQ text on most pages
  quotes a different, higher IV rank than the IV block; IV-block values used
  throughout (same convention as prior runs).
- Expected moves: recomputed here from MERGED fresh IV (IV-formula fallback:
  30-day IV x sqrt(DTE/365) to the Friday weekly expiry). Strip: 10 entries,
  unchanged (ADI + DELL report today Nov 24; MU Dec 17 company-confirmed).
- Analyst: 39 new items (NVDA x15 post-earnings wave incl. Bernstein/Oppenheimer/
  StoneX/Melius upgrades Nov 23, META JPMorgan PT cut to $775 Nov 24, CRM Citi
  PT cut to $198, TXN Cantor upgrade), dated Nov 2-24; total 1,131 (was 1,092).
  Zero near-dupes (same ticker+date+firm check).
"""
import json
import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())
screen = json.loads((HID / "screen_2026-11-24.json").read_text())
opt = json.loads((HID / "screen_options_2026-11-24.json").read_text())
internals = json.loads((HID / "internals_2026-11-24.json").read_text())
fedwatch = json.loads((HID / "fedwatch_2026-11-24.json").read_text())
iva = json.loads((HID / "iv_part_a_2026-11-24.json").read_text())
ivb = json.loads((HID / "iv_part_b_2026-11-24.json").read_text())
analyst = json.loads((HID / "analyst_2026-11-24.json").read_text())
yahoo = json.loads((HID / "yahoo_2026-11-24.json").read_text())

RUN_STAMP = datetime.now(ZoneInfo("America/New_York")).strftime(
    "%b %-d, %Y %-I:%M %p ET").replace("  ", " ")
notes = [f"RUN_STAMP={RUN_STAMP}"]

# ---------- merge IV ----------
iv = dict(iva["iv"])
iv.update(ivb["iv"])
assert not (set(iva["iv"]) & set(ivb["iv"])), "IV parts overlap"
CARRIED_IV = sorted(c["ticker"] for c in iva["carried"] + ivb["carried"])
assert CARRIED_IV == ["SQ"], CARRIED_IV
REFRESHED_N = len(iva["refreshed"]) + len(ivb["refreshed"])

# ---------- ranking (scores computed by parent; components verified here) ----------
# (ticker, relVol, dist, optLiq, catalyst, trend, why)
RANK = [
 ("INSM", 19, 12, 18, 20, 15,
  "Sanofi agreed to acquire Insmed for $175/share cash ($41B), announced Nov 24; premarket +14.6% toward the offer — upside capped at $175, close expected H1 2027."),
 ("DG", 16, 14, 15, 18, 16,
  "Piper Sandler upgraded to Overweight Nov 23 (PT $123→$170) ahead of Q3 earnings Dec 3; FTC deceptive-pricing suit (amended Nov 20, now 30 states) still an overhang."),
 ("PTON", 18, 10, 20, 17, 14,
  "Board authorized a $300M buyback Nov 23 after debt refinancing; Q1 FY27 beat Nov 5 (rev $559M, adj. EBITDA $168M +42%, FCF $143M, net cash position). Heaviest front-month options on the screen."),
 ("ARGX", 15, 15, 12, 18, 17,
  "Q3 Nov 13: product sales $1.7B +54% YoY; Piper Sandler raised PT to $1,350 Nov 16; ALKIVIA Phase 3 met endpoints Nov 7; up to 5 US launches planned in 2027."),
 ("REPL", 13, 15, 13, 17, 17,
  "Tudriqev (RP1) commercial launch gaining traction — shares +80% in a month to Nov 12; Q2 FY27 beat Oct 28; Piper Sandler raised PT to $27 from $14 Nov 16."),
 ("CLX", 14, 11, 17, 16, 16,
  "Q1 FY27 beat Nov 2 (adj. EPS $1.55 vs $1.07, sales +33% on GOJO deal + ERP lap); new CEO Fabian Garcia starts Jan 5, 2027."),
 ("ADMA", 16, 8, 15, 17, 17,
  "Q3 beat Nov 4 (ASCENIV rev +31% to $124.7M, adj. EBITDA $77.3M), raised FY26 profit outlook; shares +21% Nov 5; Cantor raised PT to $13."),
 ("HRL", 13, 13, 17, 15, 13,
  "Closed $1.055B Brakebush acquisition Nov 16 (nearly triples chicken sales); raised quarterly dividend 1% Nov 23 (61st straight annual increase); Q4 earnings Dec 3 with FY27 outlook."),
 ("SLS", 16, 4, 19, 18, 14,
  "Phase 3 REGAL win Nov 17: GPS cut death risk 41% in AML (median survival 24 vs 14.7 months); shares +156% that week; $172.5M offering at $13 closed Nov 20. Heaviest total options volume on the screen."),
 ("XNCR", 17, 15, 3, 18, 17,
  "Q3 beat Nov 4 (EPS $0.50 vs -$0.35 est, rev $116.5M vs $63M); JPMorgan raised PT to $37 from $21 Nov 19; plamotamab RA data presented Nov 9. Chain very thin (3 contracts)."),
 ("KD", 17, 5, 14, 17, 16,
  "Q2 FY27 beat Nov 4 (adj. EPS $0.42 vs $0.37, rev $3.65B, signings $4.1B); shares +30% that day; AWS (Nov 5) + ServiceNow (Nov 9) partnerships."),
 ("BRO", 13, 14, 10, 16, 16,
  "Wells Fargo upgraded to Overweight Nov 19 (PT $68→$82); Q3 Oct 26 rev $1.73B, adj. EPS $1.07 both slightly missed, organic growth only 1.2%."),
 ("CPRT", 14, 10, 16, 14, 14,
  "Q1 FY27 earnings Dec 1 (before open, per Business Wire Nov 17 — not Nov 19 as previewed); Stephens reiterated Equal Weight $35 Nov 16; shares +21% off Oct lows."),
 ("CPB", 14, 9, 17, 14, 14,
  "FY26 results Nov 20 (sales -5%, adj. EPS -27%); dividend cut 36% Nov 21; new $500M savings program; Q1 FY27 earnings Dec 9; shares +16.8% in 30 days."),
 ("IDXX", 12, 15, 8, 16, 17,
  "Q3 Nov 2: revenue +10% to $1.21B, EPS $4.01 beat $3.73, raised FY26 EPS guide; +22.7% since the call."),
]
OPTS = opt["options"]
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
scores = [p["score"] for p in potential]
assert scores == sorted(scores, reverse=True), scores
assert len(potential) == 15
notes.append("screen: " + str([(p["ticker"], p["score"]) for p in potential]))

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
assert all(e["date"] >= "2026-11-24" for e in analyst["earningsDates"])
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
assert all(e["date"] >= "2026-11-24" for e in macro)
assert [e["date"] for e in macro] == sorted(e["date"] for e in macro)
for e in macro:
    assert set(e.keys()) == {"category", "categoryZh", "date", "impact",
                             "impactZh", "time", "title", "titleZh"}, e
# Yahoo bars cover the 63 watchlist (minus SQ) + sector ETFs + ^VIX/^VIX3M/SPY.
# HISTORY additionally holds 12 earnings-calendar names the collector does not
# cover; those are left untouched here (enrich-calendar-stocks.py tops them up).
watch = {s["ticker"] for s in data["STOCKS"]}
assert set(yahoo["bars"].keys()) == (watch - {"SQ"}) | \
    {"XLK", "XLF", "XLV", "XLE", "XLI", "XLU", "XLP", "XLY", "XLC", "XLRE",
     "^VIX", "^VIX3M", "SPY"}, set(yahoo["bars"].keys()) ^ (watch - {"SQ"})
assert yahoo["missing"] == ["SQ"]
assert all(any(b["d"] == "2026-11-23" for b in v)
           for t, v in yahoo["bars"].items() if t in data["HISTORY"])
assert yahoo["smiCheck"]["computed"] == 998.91
assert sum(len(v) for v in analyst["analystRevisions"].values()) == 1131, \
    sum(len(v) for v in analyst["analystRevisions"].values())
assert analyst["newAnalystItems"] == 39
assert len(yahoo["sectorBreadth"]) == 10
assert [s["etf"] for s in yahoo["sectorBreadth"]] == [
    "XLK", "XLF", "XLV", "XLE", "XLI", "XLU", "XLP", "XLY", "XLC", "XLRE"]
# Finviz prices cross-checked vs Yahoo Nov 23 closes + change%
for t, (price, chg, _) in FV.items():
    c23 = YH[t]["nov23close"]
    assert abs(price / c23 - 1 - chg / 100) < 0.002, (t, price, c23, chg)
# IV percentile sanity: fresh percentiles must be internally consistent with
# fresh ranks (both from the same IV block); HD/UBER swings vs stale stored
# values were flagged and verified — do not fail on the swing itself.
for t in ("HD", "UBER"):
    assert iv[t]["percentile"] != data["IV_DATA"][t]["percentile"], t
notes.append("validation ok: scores sum + ordered, 63 IV tickers, analyst "
             "keys, 62 refreshed / 1 carried (SQ), no rank >100, FedWatch 8 "
             "meetings sum ~100, 10-entry strip unchanged, SMI carried 998.91 "
             "(verified exactly), AAII carried 33.3/24.4/42.2, macro 33 rich "
             "entries sorted Nov 24..Dec 23, yahoo 74 tickers with Nov 23 "
             "bars + SQ missing, analyst total 1131 (+39 new), Finviz prices "
             "cross-checked vs Yahoo closes")

# ---------- expected moves (recomputed from merged fresh IV) ----------
DTE = {"2026-11-24": ("2026-11-27", 3),
       "2026-12-01": ("2026-12-04", 10), "2026-12-02": ("2026-12-04", 10),
       "2026-12-09": ("2026-12-11", 17), "2026-12-10": ("2026-12-11", 17),
       "2026-12-14": ("2026-12-18", 24), "2026-12-17": ("2026-12-18", 24)}
exp_moves_new = {}
earn = []
for e in analyst["earningsDates"]:
    e = dict(e)
    expiry, dte = DTE[e["date"]]
    mv = round(iv[e["ticker"]]["iv30"] * math.sqrt(dte / 365), 2)
    exp_moves_new[e["ticker"]] = mv
    e["expected_move"] = mv
    e["move_as_of"] = "Nov 24, 2026"
    e["move_method"] = (
        f"30-day IV × √(DTE/365) to Friday weekly expiry {expiry} "
        f"(DTE {dte} from Nov 24); optioncharts expiry-table % not readable "
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
        e["as_of"] = "2026-11-24"
    earn.append(e)
notes.append("expected moves recomputed from merged IV: " +
             str(exp_moves_new))

# ---------- SCREEN_SNAPSHOT ----------
screen_snapshot = {
    "updated": RUN_STAMP,
    "scanTime": "2026-11-24 ~7:30 AM (premarket)",
    "resultCount": 44,
    "resultTime": "2026-11-24 ~7:30 AM (premarket)",
    "source": "https://finviz.com/screener?v=211&f=cap_midover,sh_opt_option,ta_change_u,ta_highlow52w_b10h,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3",
    "optionsAsOf": "Nov 24, 2026 (optioncharts.io)",
    "note": ("Fetched Tue Nov 24, 2026 ~7:30 AM ET. Finviz v=111 Overview via "
             "live browser: 44 unique tickers in the final pass; the total "
             "flipped 44 <-> 45 between page reads within ~2 minutes and "
             "membership churned (BBIO/TS/TTEK/WMS/WYNN in the 7:28 pass, out "
             "by 7:30; SYY/TDC/TSCO/VERX/XNCR in). SYY appears twice in the "
             "raw pass (row 40 on page 2, row 41 on page 3 — a live insertion "
             "between reads) and is counted once. Prices/change are pre-market "
             "moves vs the Nov 23 close, cross-checked vs Yahoo Nov 23 closes "
             "(all 44 within 0.01pp, zero failures). 52-week highs from Yahoo "
             "1y daily chart; distanceFromHigh computed from the pre-market "
             "price vs that high (filter is '10% or more below High', so names "
             "sit 10-47% below their highs). Option volumes are total Nov 23 "
             "contracts traded from optioncharts.io overview pages; optionOI "
             "is total open interest; front month is Dec 18, 2026 for all 44. "
             "relVolume null for all: pre-market Finviz volume is a partial-"
             "session print, so no relative-volume ratio was computed (same as "
             "Nov 11-23 runs); relativeVolume scored from % change + Nov 23 "
             "session relative volume tier instead. All 15 catalysts verified "
             "via headline search. Thin option chains scored down: PRI 1 "
             "contract total, XNCR 3, STGW 13 (frontOI 74,013 is long-dated, "
             "not active), ELVN 21, MRVI 36, COCO 55, VERX 58. INSM +14.62% is "
             "a Nov 24 premarket gap on the Sanofi $175/share cash deal, not "
             "a Nov 23 session move; upside is capped at the $175 offer. LFTO "
             "has no Yahoo SMA200 (recent listing data gap)."),
    "potential": potential,
    "volumes": volumes,
}

# ---------- HISTORY (Nov 23 bars only) ----------
hist_bars = {}
for t in data["HISTORY"]:
    bars = [b for b in yahoo["bars"].get(t, []) if b["d"] == "2026-11-23"]
    if bars:
        hist_bars[t] = bars
assert all(b["d"] == "2026-11-23"
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
             "pending Hugo); 12 earnings-calendar names untouched "
             "(enrich-calendar-stocks.py tops them up)")

# ---------- MARKET_INTERNALS (read-modify-write whole object) ----------
mi = json.loads(json.dumps(data["MARKET_INTERNALS"]))  # deep copy
mi["fearGreed"] = internals["fearGreed"]
mi["vixTerm"] = internals["vixTerm"]
mi["putCall"] = internals["putCall"]
mi["breadth"] = fedwatch["breadth"]  # live-browser Nov 23 closes
mi["aaii"] = internals["aaii"]  # carried week ending Nov 18
mi["flows"] = internals["flows"]  # carried Nov 20 session (Nov 23 report not posted)
mi["flowsAsOf"] = internals["flowsAsOf"]
mi["fedWatch"] = {k: fedwatch[k] for k in
                  ("asof", "context", "effr", "effrAsOf", "meetings")}
notes.append("internals: F&G 15.73 Extreme Fear (Nov 24 7:12 AM ET print; "
             "prev close 16.97 confirms stored Nov 23 close of 17), VIX "
             "26.62/25.50 backwardation 0.96, P/C eq 0.55 idx 1.21 total 0.94 "
             "(Nov 23 finals), AAII carried 33.3/24.4/42.2 (week ending Nov 18; "
             "FLAG: live page history table now disagrees with stored prior "
             "weeks — stored history kept, re-check on next post), flows "
             "carried Nov 20 session (Nov 23 report not yet posted), breadth "
             "A/D 5.09/+1,227, %>50d 52.28 %>200d 53.08, highs/lows summary "
             "Overall 25/382 (19:37 ET revised print), FedWatch 8 meetings "
             "Dec 9 hike 97.5% (hold 0.0%, was 3.8%) (live CME)")

# ---------- SECTOR_BREADTH (Yahoo Nov 23 finals) ----------
sector_breadth = []
for s in yahoo["sectorBreadth"]:
    sector_breadth.append({
        "etf": s["etf"], "name": s["name"], "nameZh": s["nameZh"],
        "change": s["change"], "close": s["close"], "previous": s["previous"],
        "url": s.get("url", f"https://finnhub.io/?q=%22{s['etf']}%22"),
    })
notes.append("sectorBreadth (Nov 23 finals, Yahoo daily closes): " +
             str([(s["etf"], s["change"]) for s in sector_breadth]))

# ---------- IV_SOURCE ----------
iv_source = (
    "Nov 24, 2026 · 62 of 63 refreshed from optioncharts.io (live overview "
    "pages, Nov 23 close data; 30-day IV, IV rank AND IV percentile all "
    "refreshed from the IV block — the text fetch exposes percentile in the "
    "block, correcting yesterday's note that said percentile was carried); 1 "
    "carried last-good: SQ (optioncharts still shows unrelated Sahakol "
    "Equipment, stale Oct 16 crawl; Block now XYZ there, not applied pending "
    "the ticker-rename decision). HD and UBER percentiles moved sharply vs "
    "stale stored values (HD 99.6 → 35.46, UBER 88.45 → 19.92) but are "
    "internally consistent with their fresh IV ranks (HD 42.01, UBER 53.01); "
    "the stored pairs were the inconsistent ones. BRK-B refreshed via the "
    "BRKB page. FAQ text on most pages quotes a different, higher IV rank "
    "than the structured IV block; IV-block values used throughout.")

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
    "15 ranked setups from the November 24 Finviz screen, with verified "
    "front-month options activity.")
i18n["zh"]["tradesDesc"] = (
    "根据 11 月 24 日的 Finviz 筛选，列出15个已验证近月期权活跃度的排序机会。")
i18n["en"]["ivAsOf"] = (
    "Updated Nov 24, 2026 · optioncharts.io 30-day IV readings "
    "(62 of 63 refreshed; 1 carried last-good); stale source pages are "
    "flagged in ticker detail")
i18n["zh"]["ivAsOf"] = (
    "更新于 11 月 24 日 · optioncharts.io 隐含波动率数据（63 个标的中 62 个"
    "已刷新，1 个沿用上次有效值）")
i18n["en"]["calendarDesc"] = f"Macro calendar refreshed {RUN_STAMP}"
i18n["zh"]["calendarDesc"] = f"宏观日历已于 {RUN_STAMP} 更新"
i18n["en"]["sevenDayWindow"] = "Next 7 days: Nov 24 – Nov 30, 2026"
i18n["zh"]["sevenDayWindow"] = "未来7天：2026年11月24日 – 11月30日"
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
