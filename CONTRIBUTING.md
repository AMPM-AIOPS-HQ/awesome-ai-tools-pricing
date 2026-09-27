# Contributing

Thank you for helping keep this open-data repository accurate and useful.

## What to contribute

The most valuable contributions are:

- Corrections to prices, fees, quotas, eligibility, availability, or limits
- Updates when an official provider page has changed
- Missing official source URLs
- Improvements to schemas, documentation, validation, and data quality
- Reports of duplicate, outdated, misleading, or incorrectly categorized rows

## How to report a correction

Please [open an Issue](https://github.com/AMPM-AIOPS-HQ/awesome-ai-tools-pricing/issues) and include:

1. The dataset and record name
2. The field or value that is incorrect
3. The current value shown in the repository
4. The corrected value, if known
5. A link to the provider's current official page
6. The date you checked the source
7. Any relevant regional, plan, eligibility, or currency conditions

Please do not submit affiliate links, referral links, scraped copies of provider pages, personal data, passwords, API keys, or confidential information.

## Pull requests

This repository is generated from the fact-checked source databases behind AMPM-AIOPS. Direct edits to generated JSON, CSV, badges, or `datasets/index.json` may be overwritten by the next export.

Before opening a pull request:

- Explain the reason for the change and identify the affected dataset or files.
- Use an official source whenever possible.
- Preserve the existing schema and field naming conventions.
- Keep `source_url` free of tracking or referral parameters.
- Do not copy substantial text, images, logos, or tables from third-party websites.
- Update documentation or schemas when the data structure changes.
- Check that JSON remains valid and CSV formatting is preserved.
- Clearly describe any fields that could not be verified.

For factual corrections, an Issue is usually preferred first. The project maintainers will re-check the source and include confirmed changes in the next export.

## Verification standard

A published row should have:

- A current `last_verified` date
- An official `source_url`
- A clear distinction between confirmed facts, unavailable information, estimates, and notes
- Enough context to avoid confusing one plan, region, currency, or eligibility rule with another

Prices, fees, quotas, and eligibility can change at any time. A source link is evidence of where a value was checked, not a guarantee that the value remains current.

## License and attribution

By submitting original content to this repository, you agree that your contribution may be distributed under [CC BY-SA 4.0](./LICENSE). Please do not submit material that you do not have permission to license or that contains confidential or personal information.

Contributions should preserve attribution to [AMPM-AIOPS 問問貓](https://ampm-aiops.com) and the applicable official source links.

## Code of conduct

Please be respectful, factual, and constructive. Do not harass maintainers, providers, or other contributors. Issues and pull requests may be closed if they contain spam, unsupported allegations, personal data, malicious content, or material unrelated to this repository.
