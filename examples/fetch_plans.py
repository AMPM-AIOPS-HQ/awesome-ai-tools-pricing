#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download and parse the plan-level AI tools pricing data. Standard library only.

    python3 examples/fetch_plans.py                       # list the plans of one tool
    python3 examples/fetch_plans.py --tool cursor --seats 5
    python3 examples/fetch_plans.py --ref <branch-or-tag>  # read another git ref

What it shows:
  1. find the files through datasets/index.json
  2. read plans (JSON) and the CSV twin
  3. estimate a monthly bill for N seats - only from prices billed monthly;
     annual-billing figures are printed as listed and never converted
  4. read changes/latest.json to follow price changes
"""
import argparse
import csv
import io
import json
import sys
import urllib.request

REPO_RAW = "https://raw.githubusercontent.com/AMPM-AIOPS-HQ/awesome-ai-tools-pricing"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ai-tools-pricing-example"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="main")
    ap.add_argument("--tool", default="chatgpt")
    ap.add_argument("--seats", type=int, default=1)
    a = ap.parse_args()
    at_ref = lambda u: u.replace(REPO_RAW + "/main/", "%s/%s/" % (REPO_RAW, a.ref))

    index = json.loads(get("%s/%s/datasets/index.json" % (REPO_RAW, a.ref)))
    ai = next(d for d in index["datasets"] if d["dataset"] == "ai-tools")
    plans = json.loads(get(at_ref(ai["plans"]["json"])))
    rows = plans["rows"]
    csv_rows = list(csv.DictReader(io.StringIO(get(at_ref(ai["plans"]["csv"])))))
    changes = json.loads(get(at_ref(ai["changes"])))
    legacy = json.loads(get(at_ref(ai["json"])))

    print("plans: %d rows (csv: %d) | tools covered: %d | newest check: %s" % (
        len(rows), len(csv_rows), plans["tools_covered"], plans["last_verified_max"]))
    print("tool-level file (unchanged format): %d tools" % len(legacy["tools"]))

    mine = [r for r in rows if r["tool_slug"] == a.tool]
    if not mine:
        print("no published plan for tool %r" % a.tool)
    for r in mine:
        price = r["monthly_list_price"]
        if r["plan_type"] == "free":
            line = "free tier"
        elif price is None:
            line = "no monthly list price on record (null)"
        else:
            seats = a.seats if r["price_unit"] == "per_user" else 1
            line = "%s %s/month x %d = %s %.2f per month" % (r["currency"], price, seats, r["currency"], price * seats)
        if r["annual_billing_price_as_listed"] is not None:
            line += " | annual billing shows %s %s (unit: %s)" % (r["currency"], r["annual_billing_price_as_listed"], r["annual_billing_price_unit"])
        print("  %-28s %s  [checked %s, %s]" % (r["plan_name"] or "(free tier)", line, r["last_verified"], r["source_url"]))

    print("price changes %s .. %s: %d" % (changes["window"]["from"], changes["window"]["to"], changes["change_count"]))
    for c in changes["changes"][:5]:
        print("  %s %s: %s -> %s (%s, %s)" % (c["plan_id"], c["field"], c["previous_value"], c["new_value"], c["change_type"], c["detected_on"]))

    ok = bool(rows) and len(rows) == len(csv_rows) and all(r["source_url"] and r["last_verified"] for r in rows)
    print("FETCH_OK" if ok else "FETCH_FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
