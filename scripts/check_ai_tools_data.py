#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data checks for the AI tools dataset (tool-level legacy file + plan-level files).

    python3 scripts/check_ai_tools_data.py            # run from the repository root
    python3 scripts/check_ai_tools_data.py --root <dir>

Prints one PASS/FAIL line per check; exit code 0 only when every check passes.
Standard library only.
"""
import argparse
import csv
import glob
import io
import json
import os
import re
import sys
from urllib.parse import urlsplit, parse_qsl

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TRACKING = re.compile(r"^(aff|aff_id|affid|ref|referral|sdid|utm_\w+|tag|irclickid|clickid|subid|sub_id|campaign|via|fpr)$", re.I)
INTERNAL = re.compile(r"/root/|/opt/|/home/|affiliate_url|utm_medium=affiliate")
SPEC_FIELDS = ["plan_id", "plan_name", "currency", "tax_treatment", "monthly_list_price", "annual_billing_price_as_listed",
               "annual_list_price_total", "billing_period", "free_quota_summary", "free_quota_reset_period", "region",
               "eligibility", "promo_ends", "api_price_unit", "api_unit_price", "source_url", "last_verified"]
TYPES = {"string": str, "number": (int, float), "boolean": bool, "null": type(None)}
results = []


def check(name, problems):
    problems = list(problems)
    results.append((name, problems))
    print("%s  %s%s" % ("PASS" if not problems else "FAIL", name, "" if not problems else "  (%d)" % len(problems)))
    for p in problems[:5]:
        print("        - %s" % p)


def load(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def url_problem(u):
    if not isinstance(u, str) or not u.startswith("https://"):
        return "not an https URL"
    bad = [k for k, _ in parse_qsl(urlsplit(u).query) if TRACKING.match(k)]
    return "tracking parameter %s" % bad if bad else None


def type_ok(v, t):
    ts = t if isinstance(t, list) else [t]
    for x in ts:
        py = TYPES[x]
        if x == "number" and isinstance(v, bool):
            continue
        if isinstance(v, py):
            return True
    return False


def row_problems(rows, schema):
    props, req = schema["properties"], schema["required"]
    for r in rows:
        pid = r.get("plan_id")
        if set(r) != set(props):
            yield "%s: keys differ from schema %s" % (pid, sorted(set(r) ^ set(props)))
            continue
        for k, v in r.items():
            if v == "":
                yield "%s: %s is an empty string (unknown must be null)" % (pid, k)
            elif not type_ok(v, props[k]["type"]):
                yield "%s: %s has wrong type %r" % (pid, k, v)
        for k in req:
            if r.get(k) is None:
                yield "%s: required %s is null" % (pid, k)
        if r.get("plan_type") not in ("free", "paid"):
            yield "%s: plan_type %r" % (pid, r.get("plan_type"))


def source_problems(rows, key="plan_id"):
    for r in rows:
        p = url_problem(r.get("source_url"))
        if p:
            yield "%s: source_url %s" % (r.get(key), p)
        if not DATE.match(str(r.get("last_verified") or "")):
            yield "%s: last_verified %r is not a date" % (r.get(key), r.get("last_verified"))


def annual_problems(rows):
    for r in rows:
        pid, m = r.get("plan_id"), r.get("monthly_list_price")
        a, tot = r.get("annual_billing_price_as_listed"), r.get("annual_list_price_total")
        if r.get("plan_type") == "paid" and m is not None and r.get("billing_period") != "monthly":
            yield "%s: monthly_list_price filled on a plan that is not billed monthly" % pid
        if r.get("plan_type") == "paid" and m is not None and m <= 0:
            yield "%s: paid plan with monthly_list_price %r (unknown must be null)" % (pid, m)
        for label, y in (("annual_billing_price_as_listed", a), ("annual_list_price_total", tot)):
            if m and y and abs(m * 12 - y) < 0.011 and r.get("annual_billing_price_unit") != "per_year":
                yield "%s: %s equals monthly x 12 (looks computed)" % (pid, label)
        if tot and a and abs(a * 12 - tot) < 0.011:
            yield "%s: annual_list_price_total equals annual figure x 12 (looks computed)" % pid
        if r.get("annual_billing_price_unit") is not None and a is None:
            yield "%s: annual unit without an annual figure" % pid
        if (r.get("api_unit_price") is None) != (r.get("api_price_unit") is None):
            yield "%s: api_price_unit and api_unit_price must be filled together" % pid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    a = ap.parse_args()
    os.chdir(a.root)
    P = "datasets/ai-tools/"

    try:
        schema = load(P + "schema.json")
        check("schema.json is valid and lists every specified field",
              ["missing field %s" % f for f in SPEC_FIELDS if f not in schema.get("properties", {})]
              + ["required lacks %s" % f for f in ("plan_id", "source_url", "last_verified") if f not in schema.get("required", [])]
              + ([] if "change" in schema.get("$defs", {}) else ["$defs.change missing"]))
        doc = load(P + "plans_2026.json")
        rows = doc.get("rows") or []
    except Exception as e:
        check("schema.json and plans_2026.json can be read", ["%s: %s" % (type(e).__name__, e)])
        return finish()

    check("plans: at least one row and row_count matches", [] if rows and doc.get("row_count") == len(rows) else ["rows=%d row_count=%r" % (len(rows), doc.get("row_count"))])
    check("plans: every row matches the schema, unknown values are null", row_problems(rows, schema))
    check("plans: every row has an official source_url and a last_verified date", source_problems(rows))
    ids = [r.get("plan_id") for r in rows]
    check("plans: plan_id is unique and shaped <tool_slug>/<plan-slug>",
          ["duplicate %s" % i for i in sorted({i for i in ids if ids.count(i) > 1})]
          + ["bad id %r" % r.get("plan_id") for r in rows if not str(r.get("plan_id")).startswith(str(r.get("tool_slug")) + "/")])
    check("plans: annual prices are not converted into monthly list prices", annual_problems(rows))
    full = [r for r in rows if r.get("plan_type") == "paid" and all(r.get(k) is not None for k in
            ("plan_name", "currency", "billing_period", "monthly_list_price", "source_url", "last_verified"))]
    check("plans: at least one complete paid plan example", [] if full else ["no row has name, currency, billing period, monthly price, source and date all filled"])

    with io.open(P + "plans_2026.csv", encoding="utf-8", newline="") as f:
        crow = list(csv.DictReader(f))
    check("plans: CSV twin has the same columns and plan_ids as the JSON",
          ([] if crow and list(crow[0].keys()) == list(schema["properties"].keys()) else ["CSV header differs from schema order"])
          + ([] if [r["plan_id"] for r in crow] == ids else ["plan_id list differs (csv %d rows, json %d)" % (len(crow), len(rows))])
          + ["%s: CSV source_url/last_verified empty" % r["plan_id"] for r in crow if not r.get("source_url") or not r.get("last_verified")])

    snaps = sorted(glob.glob(P + "snapshots/plans_*.json"))
    sp = []
    if not snaps:
        sp.append("no snapshot file")
    for s in snaps:
        if not re.search(r"plans_\d{4}-\d{2}-\d{2}\.json$", s):
            sp.append("%s: bad file name" % s)
            continue
        d = load(s)
        srows = d.get("rows") or []
        if d.get("snapshot_day") != s[-15:-5]:
            sp.append("%s: snapshot_day does not match file name" % s)
        sp += ["%s: %s" % (s, x) for x in list(row_problems(srows, schema))[:3] + list(source_problems(srows))[:3] + list(annual_problems(srows))[:3]]
    check("snapshots: at least one daily file, each valid against the schema", sp)

    ch = load("changes/latest.json")
    cdef = schema["$defs"]["change"]
    cp = []
    if not isinstance(ch.get("changes"), list) or ch.get("change_count") != len(ch.get("changes") or []):
        cp.append("changes must be a list and change_count must match")
    if not (DATE.match(str((ch.get("window") or {}).get("from"))) and DATE.match(str((ch.get("window") or {}).get("to")))):
        cp.append("window.from / window.to missing")
    for c in ch.get("changes") or []:
        cid = c.get("plan_id")
        cp += ["%s: missing %s" % (cid, k) for k in cdef["required"] if c.get(k) is None]
        if c.get("change_type") not in cdef["properties"]["change_type"]["enum"]:
            cp.append("%s: change_type %r" % (cid, c.get("change_type")))
        if c.get("previous_value") == c.get("new_value"):
            cp.append("%s: previous_value equals new_value" % cid)
        if cid not in ids:
            cp.append("%s: not a published plan" % cid)
        cp += list(source_problems([c]))
    check("changes/latest.json: every entry has change type, previous value, new value, date and source", cp)

    idx = load("datasets/index.json")
    ai = [d for d in idx.get("datasets") or [] if d.get("dataset") == "ai-tools"]
    ip = []
    if len(ai) != 1:
        ip.append("ai-tools entry missing")
    else:
        d = ai[0]
        for k, tail in (("schema", P + "schema.json"), ("changes", "changes/latest.json")):
            if not str(d.get(k) or "").endswith(tail):
                ip.append("ai-tools.%s does not point to %s" % (k, tail))
        pl = d.get("plans") or {}
        if not str(pl.get("json") or "").endswith(P + "plans_2026.json") or not str(pl.get("csv") or "").endswith(P + "plans_2026.csv"):
            ip.append("ai-tools.plans.json/csv pointers wrong")
        if pl.get("rows") != len(rows):
            ip.append("ai-tools.plans.rows %r != %d" % (pl.get("rows"), len(rows)))
        if not d.get("plan_snapshots"):
            ip.append("ai-tools.plan_snapshots missing")
        for k in ("json", "csv"):
            if not str(d.get(k) or "").endswith("data/ai_tools_2026." + k):
                ip.append("legacy pointer ai-tools.%s changed" % k)
    check("index.json: ai-tools entry points to schema, plans, snapshots and changes", ip)

    lp = []
    try:
        old = load("data/ai_tools_2026.json")
        tools = old.get("tools")
        if not isinstance(tools, list) or not tools or old.get("tool_count") != len(tools):
            lp.append("tools list / tool_count broken")
        else:
            lp += ["%s: legacy row lacks %s" % (t.get("slug"), k) for t in tools for k in ("slug", "name", "source_url", "last_verified") if not t.get(k)]
            lp += list(source_problems(tools, key="slug"))
            known = {t["slug"] for t in tools if t.get("slug")}
            lp += ["%s: tool_slug not in the tool-level file" % r["plan_id"] for r in rows if r.get("tool_slug") not in known]
        with io.open("data/ai_tools_2026.csv", encoding="utf-8", newline="") as f:
            head = next(csv.reader(f))
        lp += ["legacy CSV lacks column %s" % k for k in ("slug", "name", "source_url", "last_verified") if k not in head]
    except Exception as e:
        lp.append("%s: %s" % (type(e).__name__, e))
    check("legacy tool-level files are still readable and every plan joins to them", lp)

    fp = []
    for path in [P + "schema.json", P + "plans_2026.json", P + "plans_2026.csv", "changes/latest.json"] + snaps:
        with io.open(path, encoding="utf-8") as f:
            m = INTERNAL.search(f.read())
        if m:
            fp.append("%s contains %r" % (path, m.group(0)))
    check("no server paths or affiliate parameters in the published files", fp)
    return finish()


def finish():
    bad = sum(1 for _, p in results if p)
    print("\n%d checks, %d passed, %d failed" % (len(results), len(results) - bad, bad))
    print("RESULT=%s" % ("PASS" if not bad else "FAIL"))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
