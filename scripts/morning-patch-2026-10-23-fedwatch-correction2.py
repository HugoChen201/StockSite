#!/usr/bin/env python3
"""Correction 2: FedWatch FORMAL completion record (data as of 23 Oct 2026
06:20:47 CT, all 10 meetings, receipt-backed) supersedes the interim
06:22:50 CT snapshot applied in v1788 (Oct 28 85.1/14.9).
Formal: Oct 28 91.7% hold / 8.3% hike; Dec 9 16.9/76.3/6.8.
June meeting label is Jun 9, 2027 per the formal record (reverts the
interim-based Jun 16 relabel in v1788). EFFR not shown -> carried 3.88."""
import json
from pathlib import Path
REPO = Path.home() / "workspace" / "StockSite"
data = json.loads((REPO / "data.json").read_text())
mi = data["MARKET_INTERNALS"]
fresh = {
 "Oct 28, 2026": [["375-400", 91.7], ["400-425", 8.3]],
 "Dec 9, 2026": [["375-400", 16.9], ["400-425", 76.3], ["425-450", 6.8]],
 "Jan 27, 2027": [["375-400", 11.1], ["400-425", 55.9], ["425-450", 30.7], ["450-475", 2.3]],
 "Mar 17, 2027": [["375-400", 4.9], ["400-425", 30.8], ["425-450", 44.8], ["450-475", 18.2], ["475-500", 1.3]],
 "Apr 28, 2027": [["375-400", 3.3], ["400-425", 22.5], ["425-450", 40.3], ["450-475", 26.7], ["475-500", 6.7], ["500-525", 0.4]],
 "Jun 9, 2027": [["375-400", 2.1], ["400-425", 15.4], ["425-450", 33.7], ["450-475", 31.8], ["475-500", 14.1], ["500-525", 2.8], ["525-550", 0.2]],
 "Jul 28, 2027": [["375-400", 1.9], ["400-425", 14.1], ["425-450", 31.9], ["450-475", 31.9], ["475-500", 15.9], ["500-525", 3.9], ["525-550", 0.4]],
 "Sep 15, 2027": [["375-400", 1.7], ["400-425", 12.6], ["425-450", 29.8], ["450-475", 31.9], ["475-500", 17.8], ["500-525", 5.3], ["525-550", 0.8], ["550-575", 0.1]],
 "Oct 27, 2027": [["375-400", 1.6], ["400-425", 12.5], ["425-450", 29.6], ["450-475", 31.9], ["475-500", 18.0], ["500-525", 5.5], ["525-550", 0.9], ["550-575", 0.1]],
 "Dec 8, 2027": [["350-375", 0.1], ["375-400", 2.2], ["400-425", 13.4], ["425-450", 29.7], ["450-475", 31.2], ["475-500", 17.3], ["500-525", 5.2], ["525-550", 0.8], ["550-575", 0.1]],
}
fw = mi["fedWatch"]
seen = set()
for m in fw["meetings"]:
    if m["decision"] == "Jun 16, 2027":
        m["decision"] = "Jun 9, 2027"  # formal record tab label; interim-based relabel reverted
    if m["decision"] in fresh:
        m["outcomes"] = [{"label": lbl, "pct": pct} for lbl, pct in fresh[m["decision"]] if pct > 0]
        seen.add(m["decision"])
assert seen == set(fresh), set(fresh) - seen
fw["asof"] = "Oct 23, 2026 (CME FedWatch live page; data as of 23 Oct 2026 06:20:47 CT; all 10 meetings read via meeting tabs, NOW row; formal completion record — supersedes the interim 06:22:50 CT snapshot applied in v1788)"
fw["context"] = "Market-implied probabilities from 30-day fed funds futures (CME FedWatch, verified live this morning), not forecasts. Oct 28: 91.7% hold / 8.3% hike. Dec 9: 16.9% at 375-400 / 76.3% at 400-425 / 6.8% at 425-450."
mi["fedWatch"] = fw
macro = data["MACRO_EVENTS"]
for ev in macro:
    if ev["date"] == "2026-10-28" and "FOMC rate decision" in ev["title"]:
        ev["impact"] = "Markets price ~91.7% hold at 375-400 bps and ~8.3% hike; a surprise would move stocks and bonds sharply."
        ev["impactZh"] = "市场定价约91.7%维持375-400 基点、约8.3%加息；若有意外，股债将剧烈波动。"
Path("/tmp/patch.json").write_text(json.dumps({"MARKET_INTERNALS": mi, "MACRO_EVENTS": macro}))
print("correction2 patch | Oct28:", fw["meetings"][0]["outcomes"], "| Dec9:", fw["meetings"][1]["outcomes"], "| Jun:", fw["meetings"][5]["decision"])
