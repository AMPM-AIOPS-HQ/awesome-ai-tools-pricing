#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checks for datasets/pending-tools/ (counts only). Run from the repository root:

    python3 scripts/check_pending_tools.py
    python3 scripts/check_pending_tools.py --root <dir>

One PASS/FAIL line per check; exit code 0 only when every check passes. Standard library only.
"""
import argparse
import io
import json
import os
import re
import sys

P = "datasets/pending-tools/"
STATUSES = ["pending-search", "pending-verification", "incomplete-data", "duplicate", "inactive", "renamed-or-merged"]
KEYS = ["dataset", "title", "license", "rule", "published_dataset", "published_rows", "seed_list_size", "already_published",
        "merged_same_id_or_name", "pending_total", "latest_check_on_record", "status_counts", "gap_category_counts", "reason_counts",
        "with_confirmed_homepage", "open_source_review", "files"]
SIGNALS = ["repository-open-source-license", "repository-license-conditional-or-unmarked", "no-matching-repository-link",
           "homepage-unreadable", "no-homepage-on-record"]
ROLES = ["product-itself", "companion-only", "hosted-service-of-open-core", "undetermined"]
# words that would turn a neutral count into a claim, a comparison or an advertisement
CLAIMS = re.compile(r"推薦|熱門|最佳|最好|贊助|排名|業配|可能免費|應該免費|NT\$|US\$|\$\s?\d|€\s?\d|不適合|官方認證"
                    r"|recommend|popular|sponsor|\bbest\b|\brank|top[- ]rated|probably|cheap|\bstars?\b", re.I)
PERSONAL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\b09\d{8}\b|\+\d{8,}")
INTERNAL = re.compile(r"/root/|/opt/|/home/|gh_stars|hn_points|tranco|appstore")
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
        idx, schema = load(P + "index.json"), load(P + "schema.json")
        doc = io.open("docs/pending-tools.md", encoding="utf-8").read()
    except Exception as e:
        check("index.json, schema.json and the doc can be read", ["%s: %s" % (type(e).__name__, e)])
        return finish()

    def shape():
        if list(idx) != KEYS:
            yield "index.json keys differ from the fixed list: %s" % sorted(set(idx) ^ set(KEYS))
        for k in schema.get("required", []):
            if k not in idx:
                yield "required %s missing" % k
        for k in ("published_rows", "seed_list_size", "already_published", "merged_same_id_or_name", "pending_total", "with_confirmed_homepage"):
            if not isinstance(idx.get(k), int) or isinstance(idx.get(k), bool) or idx.get(k) < 0:
                yield "%s must be a non-negative integer" % k
        for k in ("status_counts", "gap_category_counts", "reason_counts"):
            c = idx.get(k)
            if not isinstance(c, dict) or any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in c.values()):
                yield "%s must map text to non-negative integers" % k
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(idx.get("latest_check_on_record"))):
            yield "latest_check_on_record is not a date"
    check("index.json has exactly the expected fields, all counts are integers", shape())
    if results[-1]:
        return finish()

    def sums():
        t = idx["pending_total"]
        if idx["seed_list_size"] - idx["already_published"] - idx["merged_same_id_or_name"] != t:
            yield "seed_list_size - already_published - merged != pending_total"
        for k in ("status_counts", "gap_category_counts", "reason_counts"):
            if sum(idx[k].values()) != t:
                yield "%s adds up to %d, not %d" % (k, sum(idx[k].values()), t)
        if list(idx["status_counts"]) != STATUSES:
            yield "status_counts keys differ from the six defined statuses"
        if idx["with_confirmed_homepage"] > t:
            yield "with_confirmed_homepage exceeds pending_total"
    check("the counts add up", sums())

    def oss():
        o = idx["open_source_review"]
        if o is None:
            return
        if not isinstance(o, dict) or list(o) != ["checked_on", "tools_checked", "signal_counts", "repository_role_counts", "product_itself_by_license"]:
            yield "open_source_review has unexpected fields"
            return
        for k, keys in (("signal_counts", SIGNALS), ("repository_role_counts", ROLES),
                        ("product_itself_by_license", ["open-source-license", "conditional-or-unmarked"])):
            c = o[k]
            if not isinstance(c, dict) or list(c) != keys or any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in c.values()):
                yield "open_source_review.%s must hold exactly the defined keys with non-negative integers" % k
                return
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(o["checked_on"])):
            yield "open_source_review.checked_on is not a date"
        s, r = o["signal_counts"], o["repository_role_counts"]
        if o["tools_checked"] != idx["pending_total"] or sum(s.values()) != o["tools_checked"]:
            yield "open-source signals do not cover every pending tool exactly once"
        if sum(r.values()) != s[SIGNALS[0]] + s[SIGNALS[1]]:
            yield "repository roles do not add up to the tools with a linked repository"
        if sum(o["product_itself_by_license"].values()) != r["product-itself"]:
            yield "product_itself_by_license does not add up to product-itself"
        if o["product_itself_by_license"]["open-source-license"] > s[SIGNALS[0]]:
            yield "more product-itself tools under an open-source license than tools with that signal"
        for k in SIGNALS:
            if not re.search(r"`%s`.*\|\s*%d\s*\|" % (re.escape(k), s[k]), doc):
                yield "doc count for %s differs from index.json" % k
        for k in ROLES:
            if not re.search(r"`%s`.*\|\s*%d\s*\|" % (re.escape(k), r[k]), doc):
                yield "doc count for %s differs from index.json" % k
    check("open-source signal counts add up and match the doc", oss())

    def no_items():
        allowed_files = {"schema": P + "schema.json", "doc": "docs/pending-tools.md"}
        if idx["files"] != allowed_files:
            yield "files must point to the schema and the doc only"
        for k, v in idx.items():
            if isinstance(v, list):
                yield "%s is a list — this dataset holds counts, not items" % k
        blob = json.dumps(idx, ensure_ascii=False)
        if re.search(r"https?://", blob):
            yield "index.json contains a URL"
        if len(idx["reason_counts"]) > 30 or len(idx["gap_category_counts"]) > 9:
            yield "too many distinct keys — looks like per-tool data"
        for extra in ("pending-tools.json", "pending-tools.csv"):
            if os.path.exists(P + extra):
                yield "%s exists — item-level files are not published" % extra
    check("counts only: no item list, no URLs, no per-tool file", no_items())

    def neutral():
        for path, txt in ((P + "index.json", json.dumps(idx, ensure_ascii=False)), ("docs/pending-tools.md", doc)):
            for rx, label in ((CLAIMS, "claim wording"), (PERSONAL, "personal data"), (INTERNAL, "internal detail")):
                m = rx.search(txt)
                if m:
                    yield "%s: %s: %r" % (path, label, m.group(0))
    check("no claims, comparisons, prices, personal data or internal details in public text", neutral())

    def doc_agrees():
        for label, n in (("pending", idx["pending_total"]), ("seed", idx["seed_list_size"]), ("published", idx["already_published"])):
            if not re.search(r"\|\s*\**%d\**\s*\|" % n, doc):
                yield "doc does not show the %s count %d" % (label, n)
        for s in STATUSES:
            if not re.search(r"`%s`.*\|\s*%d\s*\|" % (re.escape(s), idx["status_counts"][s]), doc):
                yield "doc count for %s differs from index.json" % s
    check("the doc shows the same numbers as index.json", doc_agrees())
    return finish()


def finish():
    bad = sum(1 for p in results if p)
    print("\n%d checks, %d passed, %d failed" % (len(results), len(results) - bad, bad))
    print("RESULT=%s" % ("PASS" if not bad else "FAIL"))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
