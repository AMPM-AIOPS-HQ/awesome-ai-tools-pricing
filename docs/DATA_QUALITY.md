# Data quality review

This document records repository-level checks and items that should be reviewed in the upstream fact-checking database before the next generated export.

## Checks completed on 2026-09-27

- The repository is public and uses CC BY-SA 4.0.
- `datasets/index.json` totals are internally consistent: 109 + 179 + 35 + 7 + 16 + 25 = 371 rows.
- The index reports 13 excluded rows, matching the cards dataset entry.
- Each inspected dataset has JSON, CSV, and a schema where applicable.
- Dataset metadata includes a source, methodology URL, license, generated timestamp, row count, source URL, and `last_verified`.
- The repository contains a disclaimer, contribution guide, and issue workflow.

These checks verify structure and consistency only. They do not prove that every price, fee, eligibility rule, or regulatory statement is currently correct.

## Items requiring upstream review

The following are review flags, not final claims that the values are wrong:

### High priority: source-to-record alignment

Several card records use a generic or apparently different product URL as `source_url`. Examples visible in the current snapshot include:

- `ctbc-7eleven`, `ctbc-amazon`, `ctbc-debit`, `ctbc-asiamiles`, `ctbc-chinaair`, `ctbc-disney`, `ctbc-infinite`, `ctbc-student`, and `ctbc-starbucks` pointing to a LINE Pay or generic card page.
- Multiple records marked as unavailable or legacy pointing only to a card index rather than an archival product page.

Action: use the exact official product or terms page where available. If only a generic index can verify that a product is unavailable, say so explicitly in a separate evidence/status field rather than presenting the index as the product page.

### High priority: mixed-source statements

Some rows state that values came from blogs, public reports, market sources, or a third-party page while the row's `source_url` points to an official page. Examples include entries in the broker and crypto datasets.

Action: split evidence into `official_source_url` and `secondary_source_url`, or remove the secondary-source claim. Do not label a value as officially verified when the cited page does not contain it.

### High priority: classification and naming

The current cards snapshot includes at least one apparent naming/slug mismatch: `feib-friday` is named as a Taishin/FarEasTone product while the slug begins with `feib`. Several records are legacy, stopped, or generic bank-card entries.

Action: confirm issuer, product name, slug, status, and whether the item belongs in the dataset. Add a field such as `status` with controlled values such as `active`, `legacy`, `stopped`, and `unverified`.

### Medium priority: crypto source quality

Some crypto rows cite regulator announcements, company homepages, or broad review pages instead of the exact current fee page. The Pionex row, for example, should be checked against the exchange's current official fee schedule. BitoPro and MAX should cite their current fee pages or API documentation for fee claims.

Action: prefer exact official fee, pricing, product, or terms pages; record the page type and verification method.

### Medium priority: incomplete required values

Some records have empty strings or null values in important fields. This can be valid when the provider does not disclose the value, but it should not be confused with zero, free, or no fee.

Action: use explicit status values such as `not_disclosed`, `not_applicable`, `not_found_on_official_site`, or `not_verified`, and document them in each schema.

### Medium priority: schema strictness

The current schemas allow almost every field to be a string, number, boolean, array, or null. That makes malformed values difficult for downstream users to detect.

Action: tighten schemas gradually: use strings for names, URLs, and dates; use `format: uri` for URLs; use a `YYYY-MM-DD` pattern for `last_verified`; and use explicit nullable types only where null is meaningful. Validate generated JSON and CSV in CI.

## Recommended release gate

Before publishing a daily snapshot:

1. Validate JSON syntax.
2. Validate every row against its schema.
3. Require non-empty `slug`, `name`, `source_url`, and `last_verified`.
4. Check that every `source_url` is HTTPS and has no tracking parameters.
5. Check that every `page_url` matches the row slug.
6. Detect duplicate slugs and duplicate product names.
7. Check `row_count` against the actual number of rows.
8. Check that JSON and CSV contain the same row set.
9. Flag source URLs reused across unrelated products.
10. Fail or quarantine rows with unsupported claims, stale status, or mixed secondary evidence.

The source databases should be corrected first. Generated JSON, CSV, badges, and `datasets/index.json` may be overwritten by the next exporter run.
