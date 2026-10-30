#!/usr/bin/env python3
"""Morning-refresh patch builder for StockSite data.json (Fri 2026-10-30).

Reads collector files from hidden_files/ (written by parallel collectors):
- finviz_2026-10-30.json, history_2026-10-30.json,
  iv_earnings_2026-10-30.json, analyst_new_2026-10-30.json,
  internals_2026-10-30.json, internals_parent_2026-10-30.json (live FedWatch).
Missing collector file -> that block is carried unchanged (never invented).
SMI: Oct-29 final (1000.76) already in series -> carried untouched.
VIX term: Oct-29 close values already in data.json, independently
cross-checked by the history collector -> carried, asof reworded to note
the Oct-30 morning re-verification.
MRVL earnings: held out (TipRanks Nov 26 = Thanksgiving, MarketBeat Dec 1
unconfirmed/outside window).
IV: optioncharts rate-limited (429) after ~40 fetches; per hard-stop rule
no retries — 23 tickers carried last-good.
"""
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path.home() / "workspace" / "StockSite"
HID = Path.home() / "workspace/goals/stock-watchlist-website/hidden_files"
data = json.loads((REPO / "data.json").read_text())

def load(name):
    p = HID / name
    return json.loads(p.read_text()) if p.exists() else None

finviz = load("finviz_2026-10-30.json")
hist = load("history_2026-10-30.json")
coll = load("iv_earnings_2026-10-30.json")
anew = load("analyst_new_2026-10-30.json")
intern = load("internals_2026-10-30.json")
parent = load("internals_parent_2026-10-30.json")

RUN_STAMP = datetime.now(ZoneInfo("America/New_York")).strftime(
    "%b %-d, %Y %-I:%M %p ET").replace("  ", " ")
TODAY = "2026-10-30"
notes = []

# ---------- SCREEN_SNAPSHOT ----------
if finviz and finviz.get("potential"):
    pot = sorted(finviz["potential"], key=lambda x: -x["score"])
    volumes = {p["ticker"]: p.get("optionVolume") for p in pot}
    excl = "; ".join(f"{e['ticker']} ({e['reason']})"
                     for e in finviz.get("excluded", []))
    screen = {
        "updated": RUN_STAMP,
        "scanTime": "2026-10-30 ~7:27 AM (premarket)",
        "resultCount": finviz["resultCount"],
        "resultTime": "2026-10-30 ~7:27 AM (premarket)",
        "source": "https://finviz.com/screener?v=211&f=cap_midover,sh_opt_option,ta_change_u,ta_highlow52w_b10h,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3",
        "optionsAsOf": "Oct 30, 2026 (optioncharts.io)",
        "note": (f"{len(pot)} ranked from {finviz['resultCount']} results "
                 "(Finviz premarket snapshot ~7:27 AM ET Oct 30; a re-read "
                 "minutes later showed 112 as the premarket screen drifted, "
                 "and rows 101-110 of the 110-count screen were unreadable, "
                 "so ranked names come from rows 1-100). AZN and RTX tie on "
                 "top: AZN on this morning's Q3 beat + $1.5B savings plan, "
                 "RTX on its Oct 20 Q3 beat plus an $8B Air Force contract. "
                 "Share relative volume is unmeasurable premarket and scored "
                 "0, per precedent. Distance scored relatively: "
                 "Finviz/optioncharts 52-week highs put ranked names 11-21% "
                 "below their highs despite the screen's within-10% filter, "
                 "so the component ranks closeness rather than the 10% claim. "
                 + (f"Excluded: {excl}." if excl else "")),
        "potential": pot,
        "volumes": volumes,
    }
    notes.append(f"screen: {len(pot)}/{finviz['resultCount']} "
                 + str([(p['ticker'], p['score']) for p in pot]))
else:
    screen = data["SCREEN_SNAPSHOT"]
    notes.append("screen: CARRIED (no finviz file)")

# ---------- HISTORY ----------
history = data["HISTORY"]
appended = 0
if hist:
    for t, bar in hist.get("bars", {}).items():
        arr = history.setdefault(t, [])
        if arr and arr[-1]["d"] == bar["d"]:
            continue
        arr.append({"c": bar["c"], "d": bar["d"], "h": bar["h"],
                    "l": bar["l"], "o": bar["o"]})
        appended += 1
    notes.append(f"HISTORY appended: {appended}, missing: {hist.get('missing')}")
else:
    notes.append("HISTORY: CARRIED (no history file)")

# ---------- SECTOR BREADTH ----------
if hist and hist.get("sectorBreadth"):
    sb_old = {s["etf"]: s for s in data["SECTOR_BREADTH"]}
    sector = []
    for row in hist["sectorBreadth"]:
        base = dict(sb_old[row["etf"]])
        base["close"] = row["close"]
        base["previous"] = row["previous"]
        base["change"] = row["change"]
        sector.append(base)
else:
    sector = data["SECTOR_BREADTH"]
    notes.append("SECTOR_BREADTH: CARRIED")

# ---------- MARKET_INTERNALS ----------
mi = json.loads(json.dumps(data["MARKET_INTERNALS"]))
if intern:
    fg = intern.get("fearGreed") or {}
    if fg.get("value") is not None:
        mi["fearGreed"].update({"value": fg["value"], "label": fg["label"],
            "previousClose": fg.get("previousClose"),
            "asof": fg.get("asof", RUN_STAMP),
            "note": ("Fallback CSV series (official CNN JSON unreachable "
                      "Oct 30 morning). Differs slightly from the Oct 29 "
                      "CNN live-page reading of 35; do not treat as a "
                      "live-page quote.")})
    vt = intern.get("vixTerm") or {}
    if hist and hist.get("vix"):
        v = hist["vix"]
        mi["vixTerm"].update({"spot": v["spot"], "spotPrev": v["spotPrev"],
            "threeMonth": v["threeMonth"],
            "threeMonthPrev": v["threeMonthPrev"],
            "ratio": round(v["threeMonth"] / v["spot"], 2)
                if v.get("spot") else mi["vixTerm"].get("ratio"),
            "state": "Contango (calm)",
            "asof": "Oct 29, 2026 close (Yahoo ^VIX / ^VIX3M daily; "
                    "re-verified Oct 30 morning run)",
            "note": "^VIX3M 3-month VIX. 19.37/17.20 = 1.13."})
    pc = intern.get("putCall") or {}
    if pc.get("equity") is not None:
        mi["putCall"].update({"equity": pc["equity"],
            "equityAsOf": "Oct 28, 2026 (ycharts; Oct-29 finals not yet "
                          "reflected in cached YCharts pages Oct 30 morning)",
            "index": pc.get("index"),
            "indexAsOf": "Oct 28, 2026 (ycharts; Oct-29 finals not yet "
                         "reflected in cached YCharts pages Oct 30 morning)",
            "asof": "Equity Oct 28, 2026 · Index Oct 28, 2026 (ycharts; "
                    "Oct-29 finals pending)"})
    br = intern.get("breadth") or {}
    # Barchart text fetches stale -> carry Oct-29 close values, annotate.
    for k in ("advanceDeclineAsOf", "above50AsOf", "above200AsOf",
              "highLowAsOf"):
        mi["breadth"][k] = mi["breadth"][k] + \
            " (carried — Barchart text fetches stale Oct 30 morning run)"
    fl = intern.get("flows") or {}
    # Latest ETF Action report is the Oct-28-session report already in
    # data.json -> carry, with a recheck note.
    mi["flowsAsOf"] = (mi["flowsAsOf"] +
        " Rechecked Oct 30 morning: no newer ETF Action report posted; "
        "Oct 28-session report remains latest (Oct 29 session not yet "
        "posted, T+1).")
    notes.append("internals: refreshed from collector; unreachable: "
                 + str(intern.get("unreachable")))
else:
    notes.append("MARKET_INTERNALS: CARRIED (no internals file)")
if parent:
    pfw = parent.get("fedWatch") or {}
    if pfw:
        mi["fedWatch"] = pfw
        notes.append("fedWatch: parent live-read override applied")
# SMI + AAII carried untouched (Oct-29 SMI finalized; no new AAII week).

# ---------- EARNINGS_DATES / EXPECTED_MOVES ----------
prior_by_key = {(e["ticker"], e["date"]): e for e in data["EARNINGS_DATES"]}
earn = []
if coll:
    for e in coll.get("earnings", []):
        if e["date"] < TODAY or e["ticker"] == "MRVL":
            continue
        prev = prior_by_key.get((e["ticker"], e["date"]))
        if prev is not None:
            entry = dict(prev)
            if e.get("expectedMove") is not None:
                entry["expected_move"] = e["expectedMove"]
                entry["move_as_of"] = "Oct 30, 2026"
            if e.get("session") and e["session"] != "unknown":
                entry["session"] = e["session"]
            if e["ticker"] == "AMD":
                entry["move_method"] = ("options-implied (IV formula "
                    "fallback: 55.04% IV x sqrt(4/365); optioncharts "
                    "near-expiry expected moves blank Oct 30 morning)")
        else:
            entry = {"date": e["date"], "name": e["name"],
                     "session": e["session"], "ticker": e["ticker"],
                     "watchlist": e.get("watchlist", True), "sources": [],
                     "as_of": TODAY,
                     "expected_move": e.get("expectedMove"),
                     "move_as_of": "Oct 30, 2026",
                     "move_method": "options-implied (optioncharts.io overview)",
                     "move_method_zh": "期权隐含预期波动（期权链概览）"}
        earn.append(entry)
    seen = {(e["ticker"], e["date"]) for e in earn}
    for e in data["EARNINGS_DATES"]:
        if e["date"] >= TODAY and (e["ticker"], e["date"]) not in seen \
                and e["ticker"] != "MRVL":
            earn.append(dict(e))
    earn.sort(key=lambda x: (x["date"], x["ticker"]))
    expected = dict(data["EXPECTED_MOVES"])
    for t, pctv in coll.get("expectedMoves", {}).items():
        if t != "MRVL" and pctv is not None:
            expected[t] = pctv
    notes.append(f"earnings: {len(earn)} entries")
else:
    earn = [dict(e) for e in data["EARNINGS_DATES"] if e["date"] >= TODAY]
    expected = data["EXPECTED_MOVES"]
    notes.append("EARNINGS/EXPECTED: past entries dropped, rest carried")

# ---------- IV_DATA / IV_SOURCE ----------
iv_data = dict(data["IV_DATA"])
refreshed = 0
carried_list = []
if coll:
    for t, v in coll.get("iv", {}).items():
        if isinstance(v, dict) and "iv30" in v and v.get("refreshed"):
            iv_data[t] = {"iv30": v["iv30"], "rank": v["rank"],
                          "percentile": v["percentile"]}
            refreshed += 1
    carried_list = coll.get("ivCarried", [])
iv_source = (f"Oct 30, 2026 · {refreshed} of 63 refreshed from optioncharts.io "
             f"(live overview pages); {len(carried_list)} carried last-good"
             + (f" ({', '.join(carried_list)})" if carried_list else "")
             + " — optioncharts rate-limited (429) after ~40 fetches, "
               "no retries")

# ---------- ANALYST_REVISIONS ----------
analyst = {k: list(v) for k, v in data["ANALYST_REVISIONS"].items()}
if anew:
    for t, entries in anew.get("analystNew", {}).items():
        cur = analyst.setdefault(t, [])
        seen = {(e["sortDate"], e["detail"]) for e in cur}
        for e in entries:
            if (e["sortDate"], e["detail"]) not in seen:
                cur.append(dict(e))
                seen.add((e["sortDate"], e["detail"]))
        cur.sort(key=lambda e: (e["sortDate"], e["detail"]), reverse=True)

# ---------- MACRO ----------
macro = [dict(m) for m in data["MACRO_EVENTS"] if m["date"] >= TODAY]
if intern and intern.get("macro"):
    for m in intern["macro"]:
        if m["date"] < TODAY:
            continue
        dup = False
        for mm in macro:
            if mm["date"] != m["date"]:
                continue
            a, b = mm["title"], m["title"]
            if a.split()[0] in b or b.split()[0] in a \
                    or ("PPI" in a and "PPI" in b) \
                    or ("JOLTS" in a and "JOLTS" in b) \
                    or ("CPI" in a and "CPI" in b) \
                    or (a.startswith("FOMC") and b.startswith("FOMC")) \
                    or ("Employment" in a and "Employment" in b):
                dup = True
                break
        if not dup:
            t = m.get("time", "")
            t = {"08:30 ET": "8:30 AM ET", "14:00 ET": "2:00 PM ET"}.get(t, t)
            macro.append({"category": m.get("category", "Central Bank"),
                          "categoryZh": m.get("categoryZh", ""),
                          "date": m["date"],
                          "impact": m.get("impact", ""),
                          "impactZh": m.get("impactZh", ""),
                          "time": t,
                          "title": m["title"],
                          "titleZh": m.get("titleZh", "")})
macro.sort(key=lambda x: (x["date"], x.get("time", "")))

# ---------- ASOF / I18N ----------
asof = dict(data["ASOF"])
asof["sectorBreadth"] = RUN_STAMP
asof["macro"] = RUN_STAMP
asof["expectedMoves"] = RUN_STAMP
asof["internals"] = RUN_STAMP

n = len(screen["potential"]) if finviz and finviz.get("potential") else None
i18n = json.loads(json.dumps(data["I18N_OVERRIDES"]))
if n is not None:
    i18n["en"]["tradesDesc"] = (f"{n} ranked setups from the October 30 Finviz "
                                "screen, with verified front-month options activity.")
    i18n["zh"]["tradesDesc"] = (f"根据 10 月 30 日的 Finviz 筛选，列出{n}个已验证近月期权活跃度的排序机会。")
i18n["en"]["ivAsOf"] = (f"Updated Oct 30, 2026 · optioncharts.io 30-day IV readings "
                        f"({refreshed} of 63 refreshed; {len(carried_list)} carried "
                        "last-good); stale source pages are flagged in ticker detail")
i18n["en"]["calendarDesc"] = f"Macro calendar refreshed {RUN_STAMP}"
i18n["en"]["sevenDayWindow"] = "Next 7 days: Oct 30 – Nov 5, 2026"
i18n["en"]["checked"] = f"Checked {RUN_STAMP}"
i18n["zh"]["ivAsOf"] = (f"更新于 10 月 30 日 · optioncharts.io 隐含波动率数据（63 个标的中 "
                        f"{refreshed} 个已刷新，{len(carried_list)} 个沿用上次有效值）")
i18n["zh"]["calendarDesc"] = f"宏观日历已于 {RUN_STAMP} 更新"
i18n["zh"]["sevenDayWindow"] = "未来7天：2026年10月30日 – 11月5日"
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
for line in notes:
    print("-", line)
print("IV refreshed:", refreshed, "carried:", len(carried_list))
print("earnings:", len(earn), "| macro:", len(macro))
