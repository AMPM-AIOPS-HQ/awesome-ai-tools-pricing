# Pending tools / 待補工具清單

Tools we know about that are **not** in the published dataset ([`data/ai_tools_2026.json`](../data/ai_tools_2026.json)) yet.
The list says only what is known, what is unknown, what is missing and where a fact came from.

本清單只描述「已知、未知、缺口與來源」：不發布價格、免費額度、商用授權結論，也不做任何比較。未知的欄位一律是 `null`。

| File | |
| :--- | :--- |
| [`pending-tools.json`](../datasets/pending-tools/pending-tools.json) · [`pending-tools.csv`](../datasets/pending-tools/pending-tools.csv) | 1064 rows |
| [`schema.json`](../datasets/pending-tools/schema.json) | field definitions |
| [`index.json`](../datasets/pending-tools/index.json) | counts per status and per gap |

## How the list is built / 怎麼產生

1. Start from the maintainers' seed list (1212 identifiers).
2. Remove every tool already in the published dataset (148 removed).
3. Keep one row per identifier and per name (0 merged).
4. Give each remaining tool a status from our own check records. Nothing is looked up or inferred at export time.
5. Sort by name, then identifier. Order carries no meaning.

Re-running `python3 scripts/export_pending_tools.py` on the same input gives byte-identical files.
Checks: `python3 scripts/check_pending_tools.py`.

## Status values / 狀態

| status | Meaning | 說明 | Rows |
| :--- | :--- | :--- | ---: |
| `pending-search` | The official website has not been found yet | 官方網站尚未找到 | 6 |
| `pending-verification` | A candidate source exists; facts are not verified against official pages yet | 已有候選來源，尚未對官方頁面核實 | 572 |
| `incomplete-data` | Checked, but required facts are missing (for example no public pricing page) | 查過，但必要事實不齊（例如沒有公開定價頁） | 486 |
| `duplicate` | Same tool as another row | 與另一筆是同一個工具 | 0 |
| `inactive` | The product is confirmed discontinued | 已確認停止服務 | 0 |
| `renamed-or-merged` | Confirmed renamed or merged into another product | 已確認更名或併入其他產品 | 0 |

The last three values are defined for later use; a value with 0 rows means our records do not confirm any such case today.

## Gap categories / 缺口分類

`gap_category` is one of: 官方網站未找到 · 官方定價頁未找到 · 官方免費額度未找到 · 商用授權未找到 · 幣別、週期或稅別不明 · 地區／帳戶資格不明 · 僅有第三方來源 · 重複、停用、合併或更名. It is `null` when our records do not say which one applies (531 rows) — we do not pick one by guess.

## What is never in this list / 這份清單不會有的東西

- Prices, free-tier amounts, commercial-use conclusions, scores or any comparison between tools.
- A homepage that was not confirmed: `official_homepage` is filled only for a confirmed official domain (1 rows), otherwise `null`.
- Personal data, internal review notes, or any commercial arrangement.

## Wording used / 用語

A row reads like: “工具名稱：X。官方定價頁未找到。暫不發布價格、免費額度或商用授權；最後檢查：2026-11-18。”

Found an error, or have an official source for one of these tools? Please open an Issue with the official URL.

License: CC BY-SA 4.0 — attribution required: AMPM-AIOPS 問問貓 (ampm-aiops.com)
