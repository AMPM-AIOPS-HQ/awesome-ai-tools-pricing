# Dataset field guide

This guide explains the common fields used by the public datasets.

## Common fields

| Field | Meaning |
| --- | --- |
| `slug` | Stable identifier used in the public record URL. |
| `name` | Product, provider, card, exchange, wallet, or service name. |
| `source_url` | Official page used during verification. It is evidence for the snapshot, not a permanent guarantee. |
| `last_verified` | Date the row was checked, using `YYYY-MM-DD`. |
| `page_url` | Back-link to the detailed AMPM-AIOPS record. |

## Status and missing values

The current exports may contain empty strings or nulls. Consumers should not interpret them as zero, free, unavailable, or no fee. Until controlled status fields are added, treat them as unknown and consult the source page.

Recommended future values are:

- `not_applicable`
- `not_disclosed`
- `not_found_on_official_site`
- `not_verified`
- `estimated`

## Dataset-specific fields

### AI tools

The AI tools dataset describes free tiers, the cheapest paid monthly price, commercial-use notes, and category. Prices may vary by country, tax, billing cycle, credits, usage limits, or API consumption.

### Credit cards

`annual_fee`, `cashback`, `revolving_rate`, and `cash_advance_fee` are descriptive strings because issuer rules contain conditions and time-limited campaigns. Always read the issuer's fee table and campaign terms.

### eSIM

`price_twd` is a displayed TWD-equivalent range and may include plans with different destinations, validity periods, data limits, or billing currencies. Compare like-for-like plans before using it as a ranking.

### VPN

`min_price_usd_per_month` is the effective long-term price, not necessarily the month-to-month price. `latest_audit_year` identifies the latest independent no-log audit found in the source record; it does not prove current operational privacy.

### Brokers

`tw_eligible` describes apparent availability for Taiwan residents at verification time. Account approval, residency, tax forms, entity, exchange, market, and product eligibility can differ. `trade_fee` does not necessarily include exchange, regulatory, clearing, FX, wire, custody, or data fees.

### Crypto

`kind` distinguishes exchanges and wallets. `fee_or_price` may describe maker/taker fees, retail device pricing, spreads, or other costs depending on `kind`. Read `twd_channel` together with the provider's current terms and local regulatory information.

## Consumer guidance

Use `datasets/index.json` to discover files and schemas. Use the JSON files for structured access and the CSV files for spreadsheet workflows. Always retain `last_verified`, `source_url`, and the AMPM-AIOPS attribution when redistributing data.
