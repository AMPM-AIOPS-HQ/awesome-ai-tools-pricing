#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export the public "pending tools" summary: how many tools we know about that are not in the
published dataset yet, counted by status, by gap and by reason. Only counts are written:
no tool names, no identifiers, no URLs, no prices, no free-tier figures, no conclusions.

    python3 scripts/export_pending_tools.py --pool <candidate pool json> --verified <verified-source json>

  --pool      maintainers' candidate pool (private file; only names, states and check dates are read)
  --verified  list of candidate URLs with an "official domain verified" flag
  --official  published tool-level dataset (default: data/ai_tools_2026.json)
  --root      repository root to write into (default: .)

Same input -> byte-identical output (no generation timestamp is written). Standard library only.
"""
import argparse
import csv
import io
import json
import os
import re
from urllib.parse import urlsplit

LICENSE_TXT = "CC BY-SA 4.0 — attribution required: AMPM-AIOPS 問問貓 (ampm-aiops.com)"
OUT = "datasets/pending-tools"
COLS = ["tool_id", "name", "official_homepage", "status", "gap_category", "missing_fields", "exclusion_reason",
        "last_checked_at", "recheck_at", "source_urls", "notes"]
STATUSES = ["pending-search", "pending-verification", "incomplete-data", "duplicate", "inactive", "renamed-or-merged"]
GAPS = ["官方網站未找到", "官方定價頁未找到", "官方免費額度未找到", "商用授權未找到", "幣別、週期或稅別不明",
        "地區／帳戶資格不明", "僅有第三方來源", "重複、停用、合併或更名"]
ALL_MISSING = ["official_homepage", "official_pricing_page", "free_tier", "commercial_use"]
PRICE_MISSING = ["official_pricing_page", "free_tier", "commercial_use"]
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}")

# pool "dropped" rule text -> (status, gap_category, missing_fields, exclusion_reason)
DROP_RULES = {
    "沒取得官網網址（來源頁被擋或未提供）": ("pending-search", "官方網站未找到", ALL_MISSING, "官方網站未找到。暫不發布價格、免費額度或商用授權。"),
    "入榜須有公開定價頁": ("incomplete-data", "官方定價頁未找到", PRICE_MISSING, "官方定價頁未找到。暫不發布價格、免費額度或商用授權。"),
    "入榜須有可連線的官方網站": ("pending-verification", "官方網站未找到", ALL_MISSING, "登記的網站在最後檢查時無法連線，官方網站未確認。"),
    "官網內容須對得上工具名稱": ("pending-verification", "官方網站未找到", ALL_MISSING, "找到的網站內容與工具名稱對不上，官方網站未確認。"),
    "官網擋自動查核，待重驗（不是官網不存在）": ("pending-verification", None, PRICE_MISSING, "官方網站擋自動讀取，待人工重驗；不代表網站不存在。"),
    "寫稿查核階段不符收錄標準（定價不公開、非終端產品等，見逐筆說明）": ("incomplete-data", None, PRICE_MISSING, "查核時必要事實不齊（例如定價未公開）。"),
    "未達入榜門檻": ("incomplete-data", None, PRICE_MISSING, "現有紀錄不足以收錄，原因未細分。"),
}
DROP_DEFAULT = ("incomplete-data", None, PRICE_MISSING, "現有紀錄不足以收錄，原因未細分。")
STATE_RULES = {   # other pool sections
    "strong_queue": ("pending-verification", None, PRICE_MISSING, "已排入查核，價格、免費額度與商用授權尚未對官方頁面核實。"),
    "pending": ("incomplete-data", None, PRICE_MISSING, "查核資料不齊（來源不足或欄位缺漏）。"),
    "observe": ("pending-verification", None, PRICE_MISSING, "觀察中，尚未開始查核。"),
    "ingested": ("pending-verification", None, PRICE_MISSING, "已進入查核流程，尚未達公開門檻。"),
}
NOWHERE = ("pending-search", "官方網站未找到", ALL_MISSING, "僅有名單代號，尚未開始搜尋官方網站。")
ORDER = ["dropped", "pending", "strong_queue", "observe", "ingested"]   # tie-break when check dates are equal


def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")


def day(x):
    return x[:10] if isinstance(x, str) and DATE.match(x) else None


def clean_home(u):
    if not isinstance(u, str) or not u.startswith("https://"):
        return None
    s = urlsplit(u.strip())
    return "https://%s%s" % (s.netloc.lower(), s.path if s.path else "/")


def section_view(name, e):
    """(display name, check date, channel) from one pool entry; nothing else is read"""
    if not isinstance(e, dict):
        return None, None, None
    if name == "pending":
        t = e.get("tool") or {}
        return t.get("name"), day(e.get("last_try")), None
    if name == "dropped":
        return e.get("name"), day(e.get("checked_at")) or day(e.get("date")), e.get("source")
    if name == "strong_queue":
        return e.get("name"), day(e.get("scouted")), e.get("source")
    if name == "observe":
        return e.get("name"), day(e.get("last_check")), e.get("source")
    return None, day(e.get("date")), None


def build(pool, verified, official_slugs):
    seeded = pool.get("seeded") or {}
    homes = {}
    for e in (verified.get("entries") or []):
        if e.get("official_domain_verified") is True and e.get("tool_id") and clean_home(e.get("url")):
            homes.setdefault(e["tool_id"], clean_home(e["url"]))
    rows, already_public = [], 0
    for k in sorted(seeded):
        tid = re.sub(r"[^a-z0-9-]+", "-", str(k).strip().lower()).strip("-")
        if not tid:
            continue
        if k in official_slugs or tid in official_slugs:
            already_public += 1
            continue
        views = []
        for i, sec in enumerate(ORDER):
            e = (pool.get(sec) or {}).get(k)
            if e is not None:
                nm, d, ch = section_view(sec, e)
                views.append((d or "", -i, sec, nm, ch, e))
        name = next((v[3] for v in sorted(views, reverse=True) if v[3]), None)
        notes = []
        if views:
            d, _, sec, _, ch, e = max(views)
            if sec == "dropped":
                status, gap, missing, reason = DROP_RULES.get(e.get("rule"), DROP_DEFAULT)
            else:
                status, gap, missing, reason = STATE_RULES[sec]
            checked = d or day(seeded.get(k))
            # the pool's discovery-channel label is internal and can hint at popularity: it is not exported
        else:
            status, gap, missing, reason = NOWHERE
            checked = day(seeded.get(k))
        home = homes.get(k) or homes.get(tid)
        missing = [m for m in missing if not (m == "official_homepage" and home)]
        if not name:
            name = tid
            notes.append("名稱未登記，暫以代號顯示。")
        rows.append({"tool_id": tid, "name": str(name).strip(), "official_homepage": home, "status": status, "gap_category": gap,
                     "missing_fields": list(missing), "exclusion_reason": reason, "last_checked_at": checked, "recheck_at": None,
                     "source_urls": [home] if home else [], "notes": " ".join(notes) or None})
    # one row per tool_id and per name (case-insensitive); the smallest tool_id is kept
    rows.sort(key=lambda r: r["tool_id"])
    seen_id, seen_name, kept, merged = set(), set(), [], 0
    for r in rows:
        nk = r["name"].casefold()
        if r["tool_id"] in seen_id or nk in seen_name:
            merged += 1
            continue
        seen_id.add(r["tool_id"])
        seen_name.add(nk)
        kept.append(r)
    kept.sort(key=lambda r: (r["name"].casefold(), r["tool_id"]))
    return kept, {"seed_list_size": len(seeded), "already_published": already_public, "merged_same_id_or_name": merged}


def count(rows, key):
    c = {}
    for r in rows:
        v = r[key] if r[key] is not None else "null"
        c[v] = c.get(v, 0) + 1
    return dict(sorted(c.items()))


def schema():
    cnt = {"type": "object", "additionalProperties": {"type": "integer", "minimum": 0}}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Pending tools — summary",
        "description": "Schema of datasets/pending-tools/index.json. Counts only: this dataset never contains tool names, identifiers, URLs, "
                       "prices, free-tier figures or commercial-use conclusions. License: " + LICENSE_TXT,
        "type": "object",
        "required": ["dataset", "published_rows", "seed_list_size", "already_published", "pending_total", "latest_check_on_record",
                     "status_counts", "gap_category_counts", "reason_counts", "with_confirmed_homepage"],
        "properties": {
            "dataset": {"type": "string"},
            "published_rows": {"type": "integer", "description": "Rows in data/ai_tools_2026.json when the summary was built."},
            "seed_list_size": {"type": "integer", "description": "Identifiers on the maintainers' seed list."},
            "already_published": {"type": "integer", "description": "Seed-list tools already in the published dataset."},
            "pending_total": {"type": "integer", "description": "seed_list_size minus already_published (after merging same identifier or name)."},
            "latest_check_on_record": {"type": ["string", "null"], "description": "Newest check date among the pending tools (YYYY-MM-DD)."},
            "status_counts": dict(cnt, description="Pending tools per status: " + ", ".join(STATUSES) + "."),
            "gap_category_counts": dict(cnt, description="Pending tools per gap category; `null` = our records do not say which category applies."),
            "reason_counts": dict(cnt, description="Pending tools per neutral reason sentence (zh-Hant)."),
            "with_confirmed_homepage": {"type": "integer", "description": "Pending tools whose official domain is confirmed."},
        },
    }


DOC = """# Pending tools — summary / 待補工具統計

How many tools we know about are **not** in the published dataset ([`data/ai_tools_2026.json`](../data/ai_tools_2026.json)) yet, and why.
Only counts are published here. Tool names, identifiers and URLs of pending tools are not part of this repository.

這裡只公開統計數字：各狀態幾筆、各缺口幾筆、原因幾筆。待補工具的名稱、代號與網址都不在這個倉庫裡，也不發布價格、免費額度或商用授權結論。

**We keep a neutral position: these counts are a record of what we could verify so far. No tool is judged or compared here, and a tool being counted says nothing about its quality.**
**我們站在中立的立場，只做紀錄：這些數字是「目前查得到什麼」，不評價、不比較任何工具；被算在裡面不代表那個工具好或不好。**

## Why this exists / 為什麼做這件事

- This is a check done on the consumer's side: before a tool's price or free tier appears in our data, we want it confirmed on the tool's own official pages.
- It is not a blacklist and not pressure on anyone. "Pending" only means we have not yet found enough official information; it is not a verdict.
- Any vendor or reader can send an official source through an Issue, and we will check again.
- We do not charge tools for being reviewed or listed.

- 這是站在消費者這一邊多做的一層把關：工具的價格或免費額度要先在它自己的官方頁面查證過，才會出現在我們的資料裡。
- 這不是黑名單，也不是對任何人施壓。「待補」只代表我們還沒找到足夠的官方資料，不是結論。
- 任何工具方或讀者都可以開 Issue 提供官方來源，我們會重新查核。
- 我們不向工具方收取審核或收錄的費用。

| File | |
| :--- | :--- |
| [`index.json`](../datasets/pending-tools/index.json) | the counts |
| [`schema.json`](../datasets/pending-tools/schema.json) | field definitions |

## The numbers / 數字

| | |
| :--- | ---: |
| Seed list / 種子名單 | {seed} |
| Already published / 已在正式資料 | {published} |
| **Pending / 待補** | **{rows}** |
| Newest check on record / 最新檢查日 | {day} |
| Official domain confirmed / 官方網域已確認 | {homes} |

## By status / 依狀態

| status | Meaning | 說明 | Count |
| :--- | :--- | :--- | ---: |
| `pending-search` | The official website has not been found yet | 官方網站尚未找到 | {n_pending-search} |
| `pending-verification` | A candidate source exists; facts are not verified against official pages yet | 已有候選來源，尚未對官方頁面核實 | {n_pending-verification} |
| `incomplete-data` | Checked, but required facts are missing (for example no public pricing page) | 查過，但必要事實不齊（例如沒有公開定價頁） | {n_incomplete-data} |
| `duplicate` | Same tool as another entry | 與另一筆是同一個工具 | {n_duplicate} |
| `inactive` | The product is confirmed discontinued | 已確認停止服務 | {n_inactive} |
| `renamed-or-merged` | Confirmed renamed or merged into another product | 已確認更名或併入其他產品 | {n_renamed-or-merged} |

A status with 0 means our records do not confirm any such case today.

## By reason / 依原因

{reason_table}

## By gap category / 依缺口分類

{gap_table}

`null` means our records do not say which of the eight categories applies — we do not pick one by guess.

## How the counts are produced / 怎麼算的

1. Start from the maintainers' seed list.
2. Remove every tool already in the published dataset.
3. Keep one entry per identifier and per name.
4. Give each remaining tool a status from our own check records. Nothing is looked up or inferred at export time.
5. Count. Re-running `python3 scripts/export_pending_tools.py` on the same input gives byte-identical files.

Checks: `python3 scripts/check_pending_tools.py`.

Know an official pricing page we may have missed? Please open an Issue with the official URL.

License: {license}
"""


def table(counts, head):
    return "| %s | Count |\n| :--- | ---: |\n" % head + "\n".join("| %s | %d |" % (("`null`" if k == "null" else k), v) for k, v in counts.items())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True)
    ap.add_argument("--verified", required=True)
    ap.add_argument("--official", default=None)
    ap.add_argument("--root", default=".")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    official = load(a.official or os.path.join(root, "data/ai_tools_2026.json"))
    slugs = {t.get("slug") for t in official.get("tools") or [] if t.get("slug")}
    rows, st = build(load(a.pool), load(a.verified), slugs)   # rows stay in memory; only counts are written
    by_status = {s: 0 for s in STATUSES}
    by_status.update(count(rows, "status"))
    by_gap = count(rows, "gap_category")
    by_reason = dict(sorted(count(rows, "exclusion_reason").items(), key=lambda kv: (-kv[1], kv[0])))
    homes = sum(1 for r in rows if r["official_homepage"])
    data_day = max((r["last_checked_at"] or "" for r in rows), default="") or None
    dump(os.path.join(root, OUT, "index.json"), {
        "dataset": "pending-tools-summary", "title": "AI tools not yet in the published dataset — counts only", "license": LICENSE_TXT,
        "rule": "counts only — no tool names, identifiers, URLs, prices, free-tier figures or commercial-use conclusions",
        "published_dataset": "data/ai_tools_2026.json", "published_rows": len(slugs),
        "seed_list_size": st["seed_list_size"], "already_published": st["already_published"], "merged_same_id_or_name": st["merged_same_id_or_name"],
        "pending_total": len(rows), "latest_check_on_record": data_day,
        "status_counts": by_status, "gap_category_counts": by_gap, "reason_counts": by_reason, "with_confirmed_homepage": homes,
        "files": {"schema": OUT + "/schema.json", "doc": "docs/pending-tools.md"}})
    dump(os.path.join(root, OUT, "schema.json"), schema())
    doc = DOC
    for s in STATUSES:
        doc = doc.replace("{n_%s}" % s, str(by_status[s]))
    fmt = {"rows": len(rows), "seed": st["seed_list_size"], "published": st["already_published"], "day": data_day, "homes": homes,
           "reason_table": table(by_reason, "Reason / 原因"), "gap_table": table(by_gap, "Gap category / 缺口分類"), "license": LICENSE_TXT}
    for k, v in fmt.items():
        doc = doc.replace("{%s}" % k, str(v))
    os.makedirs(os.path.join(root, "docs"), exist_ok=True)
    with io.open(os.path.join(root, "docs/pending-tools.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)
    print("PENDING_SUMMARY_OK pending=%d %s status=%s" % (len(rows), json.dumps(st), json.dumps(by_status)))


if __name__ == "__main__":
    main()
