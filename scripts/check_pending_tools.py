#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checks for datasets/pending-tools/. Run from the repository root:

    python3 scripts/check_pending_tools.py
    python3 scripts/check_pending_tools.py --root <dir>

One PASS/FAIL line per check; exit code 0 only when every check passes. Standard library only.
"""
import argparse
import csv
import io
import json
import os
import re
import sys

P = "datasets/pending-tools/"
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# words that would turn a neutral status line into a claim, a comparison or an advertisement
CLAIMS = re.compile(r"推薦|熱門|最佳|最好|贊助|排名|業配|可能免費|應該免費|大約|約\s*(NT|US)?\$|NT\$|US\$|\$\s?\d|€\s?\d|不適合|比.{0,6}(差|好)|官方認證"
                    r"|recommend|popular|sponsor|\bbest\b|\brank|top[- ]rated|probably|cheap|\bstars?\b", re.I)
PERSONAL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\b09\d{8}\b|\+\d{8,}")
INTERNAL = re.compile(r"/root/|/opt/|/home/|gh_stars|hn_points|tranco|signals|appstore")
results = []


def check(name, problems):
    problems = list(problems)
    results.append(problems)
    print("%s  %s%s" % ("PASS" if not problems else "FAIL", name, "" if not problems else "  (%d)" % len(problems)))
    for p in problems[:5]:
        print("        - %s" % p)


def load(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    a = ap.parse_args()
    os.chdir(a.root)
    try:
        doc, schema, index = load(P + "pending-tools.json"), load(P + "schema.json"), load(P + "index.json")
        rows, props = doc["rows"], schema["properties"]
        with io.open(P + "pending-tools.csv", encoding="utf-8", newline="") as f:
            crow = list(csv.DictReader(f))
        text_doc = io.open("docs/pending-tools.md", encoding="utf-8").read()
    except Exception as e:
        check("all five files can be read", ["%s: %s" % (type(e).__name__, e)])
        return finish()
    cols = list(props)

    ids = [r.get("tool_id") for r in rows]
    names = [str(r.get("name")).casefold() for r in rows]
    check("no duplicate tool_id or name", ["duplicate id %s" % i for i in sorted({i for i in ids if ids.count(i) > 1})]
          + ["duplicate name %s" % n for n in sorted({n for n in names if names.count(n) > 1})])

    def row_problems():
        for r in rows:
            t = r.get("tool_id")
            if list(r) != cols:
                yield "%s: keys differ from schema" % t
                continue
            if r["status"] not in props["status"]["enum"]:
                yield "%s: status %r" % (t, r["status"])
            if r["gap_category"] not in props["gap_category"]["enum"]:
                yield "%s: gap_category %r" % (t, r["gap_category"])
            if not isinstance(r["exclusion_reason"], str) or not r["exclusion_reason"].strip():
                yield "%s: exclusion_reason missing" % t
            if not DATE.match(str(r["last_checked_at"] or "")):
                yield "%s: last_checked_at %r" % (t, r["last_checked_at"])
            if not isinstance(r["missing_fields"], list) or any(m not in props["missing_fields"]["items"]["enum"] for m in r["missing_fields"]):
                yield "%s: missing_fields %r" % (t, r["missing_fields"])
            if not r["missing_fields"] and r["status"] in ("pending-search", "pending-verification", "incomplete-data"):
                yield "%s: no missing field listed" % t
            for k in ("name", "exclusion_reason"):
                if r[k] == "":
                    yield "%s: %s is empty" % (t, k)
            if r["notes"] == "" or r["recheck_at"] == "":
                yield "%s: unknown must be null, not an empty string" % t
    check("every row has status, reason, missing fields and a check date", row_problems())

    def home_problems():
        for r in rows:
            h, s = r.get("official_homepage"), r.get("source_urls")
            if h is not None and not (isinstance(h, str) and h.startswith("https://") and "?" not in h):
                yield "%s: official_homepage %r" % (r["tool_id"], h)
            if not isinstance(s, list) or any(u != h for u in s):
                yield "%s: source_urls must hold confirmed sources only" % r["tool_id"]
            if h is not None and "official_homepage" in (r.get("missing_fields") or []):
                yield "%s: homepage filled but also listed as missing" % r["tool_id"]
            if h is None and r.get("status") == "pending-search" and "official_homepage" not in (r.get("missing_fields") or []):
                yield "%s: pending-search without official_homepage in missing_fields" % r["tool_id"]
    check("official_homepage is a confirmed https URL or null; no unconfirmed source", home_problems())

    def neutral_problems():
        for r in rows:
            for k in ("exclusion_reason", "notes", "status", "gap_category"):
                v = r.get(k) or ""
                for rx, label in ((CLAIMS, "claim wording"), (PERSONAL, "personal data"), (INTERNAL, "internal detail")):
                    m = rx.search(v)
                    if m:
                        yield "%s: %s in %s: %r" % (r["tool_id"], label, k, m.group(0))
        for path, txt in (("docs/pending-tools.md", text_doc), (P + "index.json", json.dumps(index, ensure_ascii=False))):
            for rx, label in ((CLAIMS, "claim wording"), (PERSONAL, "personal data"), (INTERNAL, "internal detail")):
                m = rx.search(txt)
                if m:
                    yield "%s: %s: %r" % (path, label, m.group(0))
        extra = [k for k in cols if re.search(r"price|cost|free_tier$|commercial|score|rank|star|popular", k)]
        if extra:
            yield "schema has value fields that do not belong here: %s" % extra
    check("no prices, claims, comparisons, personal data or internal details in public text", neutral_problems())

    check("rows are sorted by name then tool_id", [] if rows == sorted(rows, key=lambda r: (r["name"].casefold(), r["tool_id"])) else ["order differs"])

    def consistent():
        if list(crow[0].keys()) != cols if crow else True:
            yield "CSV header differs from schema"
        if [r["tool_id"] for r in crow] != ids:
            yield "CSV rows differ from JSON rows"
        if index.get("columns") != cols:
            yield "index.columns differs from schema"
        if not (doc.get("row_count") == index.get("row_count") == len(rows) == len(crow)):
            yield "row counts differ (json %s, index %s, rows %d, csv %d)" % (doc.get("row_count"), index.get("row_count"), len(rows), len(crow))
        sc = {}
        for r in rows:
            sc[r["status"]] = sc.get(r["status"], 0) + 1
        if {k: v for k, v in (index.get("status_counts") or {}).items() if v} != sc:
            yield "index.status_counts differs from the rows"
        if schema.get("required") != cols:
            yield "schema.required differs from the column list"
        if ("%d rows" % len(rows)) not in text_doc:
            yield "docs/pending-tools.md row count is stale"
    check("JSON, CSV, schema, index and doc agree on columns and counts", consistent())

    def overlap():
        try:
            pub = {t.get("slug") for t in load("data/ai_tools_2026.json").get("tools") or []}
        except Exception as e:
            yield "cannot read data/ai_tools_2026.json: %s" % e
            return
        for i in ids:
            if i in pub:
                yield "%s is already in the published dataset" % i
    check("no row is already in the published dataset", overlap())
    return finish()


def finish():
    bad = sum(1 for p in results if p)
    print("\n%d checks, %d passed, %d failed" % (len(results), len(results) - bad, bad))
    print("RESULT=%s" % ("PASS" if not bad else "FAIL"))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
