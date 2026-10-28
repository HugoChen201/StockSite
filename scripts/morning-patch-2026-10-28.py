#!/usr/bin/env python3
"""Morning-refresh patch builder for StockSite data.json (Wed 2026-10-28).

Sources (hidden_files/):
- finviz_2026-10-28.json: 70 results first pull (v=111 premarket ~7:30 AM ET;
  refresh showed 69 as RBLX fell out; rows 61-70 unrenderable in any view),
  14 ranked. Collector scored share relativeVolume component 10 despite a
  0.0 field value; NORMALIZED here to 0 per precedent (premarket
  unmeasurable -> 0), subtracting 10 from every score (ranking unchanged):
  AXGN 69 top. AXGN catalyst re-verified by parent (MarketBeat extended
  +17.8% at 7:23 AM ET on the Oct 28 Q3 report); BSP identity re-verified
  (Bending Spoons NASDAQ:BSP, Miro closed Oct 26, Berkshire $330M placement).
  Distance-from-high uses Finviz premarket prices vs optioncharts 52w highs,
  so several names compute below the 10% band; reported as computed.
- history_2026-10-28.json: Oct-27 bars (SQ missing: Yahoo "No data found,
  symbol may be delisted" as before; SQ keeps its Oct-23 last bar).
  Sector breadth = Oct-27 daily-bar finals (small diffs vs the Oct-27
  close-refresh intraday snapshot are final-vs-intraday, e.g. XLK 189.49).
- iv_earnings_2026-10-28.json: 37/63 IV refreshed from optioncharts.io;
  26 carried last-good (values verified identical to current IV_DATA).
  Expected moves are Oct-27 straddle values carried forward (Oct-28
  optioncharts fetches hit 429s / no earnings fields). MRVL DROPPED: new
  entry dated Nov 26, which is Thanksgiving (market closed), with sources
  conflicting Nov 26 vs Dec 1; held for verification, not published as fact.
  Earnings otherwise = prior entries with date >= Oct 28, expected_move
  refreshed from the collector (BRK-B stays null); HOOD/SKHY/STX Oct-27
  entries dropped as past. Analyst = current map + analyst_new_2026-10-28
  (42 entries, 18 tickers), deduped, newest first, no losses.
  Macro 17 events Oct 28-Nov 26, incl. Thanksgiving closure note.
- internals_2026-10-28.json + parent live read: Fear/Greed Oct 28 = 34
  Fear (official CNN JSON, 7:11 AM ET; prev close 33) — overrides the
  collector's fallback CSV (Oct 27, 33.6). VIX term Oct-27 closes
  re-verified (17.52/19.57 = 1.12 contango). Put/call Oct-27 finals from
  ycharts: equity 0.59, index 1.06. Barchart unreachable Oct 28 morning
  (empty/403), so breadth + % above MA carry the Oct-27 close values
  (Reuters/Koyfin crosschecks NOT substituted — different methodology).
  ETF flows carried: ETF Action report still shows Oct-26-session data.
  FedWatch carried (Oct-27 live read; Oct-28 page JS-blocked; secondary
  ~90% hold for Oct 28 consistent with carried 91.7%). AAII rechecked:
  still week ending 10/21 (next Thu Oct 29). SMI: Oct-27 final already in
  series (finalized by Oct-27 close refresh) — carried untouched.
"""
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())

finviz = json.loads((HID / "finviz_2026-10-28.json").read_text())
hist = json.loads((HID / "history_2026-10-28.json").read_text())
coll = json.loads((HID / "iv_earnings_2026-10-28.json").read_text())
anew = json.loads((HID / "analyst_new_2026-10-28.json").read_text())

RUN_STAMP = datetime.now(ZoneInfo("America/New_York")).strftime(
    "%b %-d, %Y %-I:%M %p ET").replace("  ", " ")
RUN_TIME = datetime.now(ZoneInfo("America/New_York")).strftime(
    "%-I:%M %p").replace("  ", " ")

# ---------- SCREEN_SNAPSHOT (normalize relativeVolume component to 0) ----------
pot = []
for p in finviz["potential"]:
    p = dict(p)
    comps = dict(p["components"])
    if comps.get("relativeVolume"):
        p["score"] = p["score"] - comps["relativeVolume"]
        comps["relativeVolume"] = 0
        p["components"] = comps
    pot.append(p)
pot.sort(key=lambda x: -x["score"])
volumes = {p["ticker"]: p.get("optionVolume") for p in pot}
excl = "; ".join(f"{e['ticker']} ({e['reason']})"
                 for e in finviz.get("excluded", []))
screen = {
    "updated": RUN_STAMP,
    "scanTime": f"2026-10-28 ~{RUN_TIME} (premarket)",
    "resultCount": finviz["resultCount"],
    "resultTime": f"2026-10-28 ~{RUN_TIME} (premarket)",
    "source": "https://finviz.com/screener?v=211&f=cap_midover,sh_opt_option,ta_change_u,ta_highlow52w_b10h,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3",
    "optionsAsOf": "Oct 28, 2026 (optioncharts.io)",
    "note": ("14 ranked from 70 results (Finviz v=111 premarket snapshot "
             "~7:30 AM ET Oct 28; a refresh minutes later showed 69 as RBLX "
             "fell out; rows 61-70 would not render in any view). AXGN tops "
             "on its Q3 report before the open (+~18% premarket). HRI is 2nd "
             "on its Oct 27 Q3 beat (EPS $3.91 vs $2.92). GEHC is 3rd on this "
             "morning's Q3 beat and raised 2026 guidance. Share relative "
             "volume is unmeasurable premarket and scored 0, per precedent. "
             "Distance-from-high uses Finviz premarket prices vs "
             "optioncharts.io 52-week highs, so several screened names "
             "compute below the 10% band — reported as computed. "
             f"Excluded: {excl}."),
    "potential": pot,
    "volumes": volumes,
}

# ---------- HISTORY ----------
# XYZ excluded deliberately: its Oct-27 bar was observed (close $74.87),
# but STOCKS still lists SQ and Hugo has not approved the SQ->XYZ rename;
# an orphan XYZ series is not appended here.
history = data["HISTORY"]
appended = 0
for t, bar in hist["bars"].items():
    if t == "XYZ":
        continue
    arr = history.setdefault(t, [])
    if arr and arr[-1]["d"] == bar["d"]:
        continue
    arr.append({"c": bar["c"], "d": bar["d"], "h": bar["h"],
                "l": bar["l"], "o": bar["o"]})
    appended += 1

# ---------- SECTOR BREADTH (final Oct-27 closes) ----------
sb_old = {s["etf"]: s for s in data["SECTOR_BREADTH"]}
sector = []
for row in hist["sectorBreadth"]:
    base = dict(sb_old[row["etf"]])
    base["close"] = row["close"]
    base["previous"] = row["previous"]
    base["change"] = row["change"]
    sector.append(base)

# ---------- MARKET_INTERNALS (carried + verified overlays) ----------
mi = data["MARKET_INTERNALS"]
fg = mi["fearGreed"]
fg["value"] = 34
fg["label"] = "Fear"
fg["previousClose"] = 33
fg["asof"] = "Oct 28, 2026 7:11 AM ET (cnn.com official JSON)"
fg["note"] = "Prev close 33."
vt = mi["vixTerm"]
vt["note"] = vt.get("note", "") + " Re-verified Oct 28 morning run."
pc = mi["putCall"]
pc["equity"] = 0.59
pc["equityAsOf"] = "Oct 27, 2026 (ycharts)"
pc["index"] = 1.06
pc["indexAsOf"] = "Oct 27, 2026 (ycharts)"
pc["asof"] = "Equity Oct 27, 2026 · Index Oct 27, 2026 (ycharts)"
br = mi["breadth"]
for k in ("advanceDeclineAsOf", "above50AsOf", "above200AsOf",
          "highLowAsOf"):
    br[k] = br[k] + " (carried — Barchart unreachable Oct 28 morning run)"
mi["flowsAsOf"] = (mi["flowsAsOf"] +
    " Rechecked Oct 28 morning: ETF Action report still shows the "
    "Oct 26-session data; Oct 27-session report not yet posted.")
fw = mi["fedWatch"]
fw["asof"] = (fw["asof"] + " Carried — Oct 28 live page not re-verified "
              "(JS tool; feed blocked); secondary reports ~90% hold for "
              "Oct 28, consistent with carried 91.7%.")
mi["aaii"]["note"] = (mi["aaii"]["note"] +
    " Rechecked Oct 28: latest week still ending 10/21 (next week "
    "publishes Thu Oct 29).")
# smi: carried untouched (Oct-27 final already in series).

# ---------- EARNINGS_DATES (prior entries >= Oct 28, moves refreshed) ----------
prior_by_key = {(e["ticker"], e["date"]): e for e in data["EARNINGS_DATES"]}
earn = []
for e in coll["earnings"]:
    if e["date"] < "2026-10-28" or e["ticker"] == "MRVL":
        continue
    prev = prior_by_key.get((e["ticker"], e["date"]))
    if prev is not None:
        entry = dict(prev)
        if e.get("expectedMove") is not None:
            entry["expected_move"] = e["expectedMove"]
    else:
        entry = {"date": e["date"], "name": e["name"],
                 "session": e["session"], "ticker": e["ticker"],
                 "watchlist": e.get("watchlist", True), "sources": [],
                 "as_of": "2026-10-28",
                 "expected_move": e.get("expectedMove"),
                 "move_as_of": "Oct 27, 2026",
                 "move_method": "options-implied (optioncharts.io overview)",
                 "move_method_zh": "期权隐含预期波动（期权链概览）"}
    earn.append(entry)
earn.sort(key=lambda x: (x["date"], x["ticker"]))

# ---------- EXPECTED_MOVES (carry full map; overwrite non-null, ex MRVL) ----------
expected = dict(data["EXPECTED_MOVES"])
for t, pctv in coll["expectedMoves"].items():
    if t != "MRVL" and pctv is not None:
        expected[t] = pctv

# ---------- IV_DATA / IV_SOURCE ----------
iv_data = dict(data["IV_DATA"])
refreshed = 0
for t, v in coll["iv"].items():
    if isinstance(v, dict) and "iv30" in v:
        if v.get("refreshed"):
            iv_data[t] = {"iv30": v["iv30"], "rank": v["rank"],
                          "percentile": v["percentile"]}
            refreshed += 1
carried_list = coll["ivCarried"]
iv_source = (f"Oct 28, 2026 · {refreshed} of 63 refreshed from optioncharts.io "
             f"(live overview pages); {len(carried_list)} carried last-good "
             f"({', '.join(carried_list)})")

# ---------- ANALYST_REVISIONS (current map + new, deduped, newest first) ----------
analyst = {k: list(v) for k, v in data["ANALYST_REVISIONS"].items()}
for t, entries in anew["analystNew"].items():
    cur = analyst.setdefault(t, [])
    seen = {(e["sortDate"], e["detail"]) for e in cur}
    for e in entries:
        if (e["sortDate"], e["detail"]) not in seen:
            cur.append(dict(e))
            seen.add((e["sortDate"], e["detail"]))
    cur.sort(key=lambda e: (e["sortDate"], e["detail"]), reverse=True)

# ---------- MACRO ----------
macro = coll["macro"]
macro.sort(key=lambda x: x["date"])

# ---------- ASOF / I18N ----------
asof = dict(data["ASOF"])
asof["sectorBreadth"] = RUN_STAMP
asof["macro"] = RUN_STAMP
asof["expectedMoves"] = RUN_STAMP
asof["internals"] = RUN_STAMP

n = len(pot)
i18n = json.loads(json.dumps(data["I18N_OVERRIDES"]))
i18n["en"]["tradesDesc"] = (f"{n} ranked setups from the October 28 Finviz "
                            "screen, with verified front-month options activity.")
i18n["en"]["ivAsOf"] = (f"Updated Oct 28, 2026 · optioncharts.io 30-day IV readings "
                        f"({refreshed} of 63 refreshed; {len(carried_list)} carried "
                        "last-good); stale source pages are flagged in ticker detail")
i18n["en"]["calendarDesc"] = f"Macro calendar refreshed {RUN_STAMP}"
i18n["en"]["sevenDayWindow"] = "Next 7 days: Oct 28 – Nov 3, 2026"
i18n["en"]["checked"] = f"Checked {RUN_STAMP}"
i18n["zh"]["tradesDesc"] = (f"根据 10 月 28 日的 Finviz 筛选，列出{n}个已验证近月期权活跃度的排序机会。")
i18n["zh"]["ivAsOf"] = (f"更新于 10 月 28 日 · optioncharts.io 隐含波动率数据（63 个标的中 "
                        f"{refreshed} 个已刷新，{len(carried_list)} 个沿用上次有效值）")
i18n["zh"]["calendarDesc"] = f"宏观日历已于 {RUN_STAMP} 更新"
i18n["zh"]["sevenDayWindow"] = "未来7天：2026年10月28日 – 11月3日"
i18n["zh"]["checked"] = f"检查于 {RUN_STAMP}"

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
print("RUN_STAMP:", RUN_STAMP)
print("patch keys:", list(patch.keys()))
print("HISTORY appended:", appended, "| earnings:", len(earn), "| macro:", len(macro),
      "| screen:", len(pot), "from", screen["resultCount"],
      "| IV refreshed:", refreshed, "carried:", len(carried_list),
      "| screen scores:", [(p["ticker"], p["score"]) for p in pot])
