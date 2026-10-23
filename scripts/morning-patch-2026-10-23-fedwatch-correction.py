#!/usr/bin/env python3
"""Correction: FedWatch FORMAL browser record (data as of 23 Oct 2026 06:22:50 CT)
supersedes the carried Oct-22 values used in v1786. All 10 meetings read.
Oct 28: 85.1% hold / 14.9% hike (was 87.3/12.7). Dec 9: 12.2/75.0/12.9.
EFFR not displayed on page -> carried 3.88 stands."""
import json
from pathlib import Path
REPO = Path.home() / "workspace" / "StockSite"
data = json.loads((REPO / "data.json").read_text())
mi = data["MARKET_INTERNALS"]
fresh = {
 "Oct 28, 2026": [["375-400", 85.1], ["400-425", 14.9]],
 "Dec 9, 2026": [["350-375", 0.0], ["375-400", 12.2], ["400-425", 75.0], ["425-450", 12.9]],
 "Jan 27, 2027": [["350-375", 0.0], ["375-400", 6.2], ["400-425", 47.5], ["425-450", 40.4], ["450-475", 6.0]],
 "Mar 17, 2027": [["350-375", 0.2], ["375-400", 2.4], ["400-425", 24.7], ["425-450", 45.0], ["450-475", 24.6], ["475-500", 3.1]],
 "Apr 28, 2027": [["350-375", 0.1], ["375-400", 1.7], ["400-425", 18.1], ["425-450", 39.5], ["450-475", 31.8], ["475-500", 8.2], ["500-525", 0.6]],
 "Jun 16, 2027": [["350-375", 0.2], ["375-400", 2.0], ["400-425", 16.6], ["425-450", 36.6], ["450-475", 31.7], ["475-500", 11.5], ["500-525", 1.4]],
 "Jul 28, 2027": [["350-375", 0.2], ["375-400", 2.0], ["400-425", 16.0], ["425-450", 35.5], ["450-475", 31.8], ["475-500", 12.7], ["500-525", 1.8]],
 "Sep 15, 2027": [["350-375", 0.4], ["375-400", 3.2], ["400-425", 19.3], ["425-450", 35.9], ["450-475", 28.6], ["475-500", 11.0], ["500-525", 1.6]],
 "Oct 27, 2027": [["350-375", 0.5], ["375-400", 3.9], ["400-425", 20.6], ["425-450", 35.4], ["450-475", 27.1], ["475-500", 10.7], ["500-525", 1.8]],
 "Dec 8, 2027": [["325-350", 0.1], ["350-375", 1.2], ["375-400", 7.8], ["400-425", 25.8], ["425-450", 33.4], ["450-475", 22.4], ["475-500", 8.1], ["500-525", 1.2]],
}
fw = mi["fedWatch"]
seen = set()
for m in fw["meetings"]:
    if m["decision"] == "Jun 9, 2027":
        m["decision"] = "Jun 16, 2027"  # live CME tab label; stale label carried in data.json
    if m["decision"] in fresh:
        m["outcomes"] = [{"label": lbl, "pct": pct} for lbl, pct in fresh[m["decision"]] if pct > 0]
        seen.add(m["decision"])
missing = set(fresh) - seen
assert not missing, f"meetings in fresh but not in data.json: {missing}"
fw["asof"] = "Oct 23, 2026 (CME FedWatch live page; data as of 23 Oct 2026 06:22:50 CT, refreshed to 06:24:47 CT on recheck, Oct probabilities unchanged; all 10 meetings read via meeting tabs, NOW row)"
fw["context"] = "Market-implied probabilities from 30-day fed funds futures (CME FedWatch, verified live this morning), not forecasts. Oct 28: 85.1% hold / 14.9% hike. Dec 9: 12.2% at 375-400 / 75.0% at 400-425 / 12.9% at 425-450."
mi["fedWatch"] = fw
macro = data["MACRO_EVENTS"]
for ev in macro:
    if ev["date"] == "2026-10-28" and "FOMC rate decision" in ev["title"]:
        ev["impact"] = "Markets price ~85.1% hold at 375-400 bps and ~14.9% hike; a surprise would move stocks and bonds sharply."
        ev["impactZh"] = "市场定价约85.1%维持375-400 基点、约14.9%加息；若有意外，股债将剧烈波动。"
patch = {"MARKET_INTERNALS": mi, "MACRO_EVENTS": macro}
Path("/tmp/patch.json").write_text(json.dumps(patch))
print("fedwatch correction patch written | Oct28:", fw["meetings"][0]["outcomes"], "| Dec9:", fw["meetings"][1]["outcomes"])
