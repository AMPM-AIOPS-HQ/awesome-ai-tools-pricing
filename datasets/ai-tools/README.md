# AI tools — plan-level pricing

Plan-by-plan prices for the tools in [`data/ai_tools_2026.json`](../../data/ai_tools_2026.json). The tool-level file is unchanged; these files add detail next to it.

| File | What it is |
| :--- | :--- |
| [`plans_2026.json`](./plans_2026.json) · [`plans_2026.csv`](./plans_2026.csv) | One row per plan (paid plans, plus one free-tier row per tool that has a free tier) |
| [`schema.json`](./schema.json) | Field definitions for a plan row and for a change entry |
| [`snapshots/plans_<date>.json`](./snapshots/) | The plan file as it stood on that day. Written once, never rewritten |
| [`../../changes/latest.json`](../../changes/latest.json) | Price changes of published plans in the last 30 days, with the previous value |

## What gets published

- A paid plan is published only when its **latest check against the official pricing page matched** (plan name and price were both read on the page). Plans that could not be found or did not match are held back; the count is in `held_back` at the top of `plans_2026.json`.
- A price field is filled only when that exact figure was read on the official page. Otherwise it is `null`.
- Every row has `source_url` (the official page) and `last_verified` (the day of that check).
- Unknown is always `null` — never `0`, never an empty string. Tax treatment, reset periods, eligibility and promotion end dates are `null` wherever we have not recorded them.
- No paid listings, no sponsored ranking, no affiliate links. Rows are sorted by `plan_id`.

## Monthly and annual prices are kept apart

- `monthly_list_price` — price per month when billed monthly. Never derived from an annual price.
- `annual_billing_price_as_listed` — the figure the official page shows when annual billing is selected, in the page's own unit. `annual_billing_price_unit` says which unit when we recorded it; `null` means we did not.
- `annual_list_price_total` — filled only when the yearly total itself was recorded. Nothing here is multiplied or divided by 12.

## Estimating a bill

```python
cost_per_month = row["monthly_list_price"] * (seats if row["price_unit"] == "per_user" else 1)
```

Only do this when `monthly_list_price` is not `null`. A runnable example that downloads and parses everything: [`examples/fetch_plans.py`](../../examples/fetch_plans.py).

## Checking the data

```bash
python3 scripts/check_ai_tools_data.py
```

Prints one PASS/FAIL line per check and exits non-zero on any failure.

## Stable identifiers

`plan_id` is `<tool_slug>/<plan-slug>` and does not change when a price changes. `tool_slug` joins to `slug` in the tool-level file.
