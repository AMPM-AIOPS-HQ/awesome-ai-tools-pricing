# Pending tools — summary / 待補工具統計

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
| Seed list / 種子名單 | 1212 |
| Already published / 已在正式資料 | 148 |
| **Pending / 待補** | **1064** |
| Newest check on record / 最新檢查日 | 2026-11-18 |
| Official domain confirmed / 官方網域已確認 | 1 |

## By status / 依狀態

| status | Meaning | 說明 | Count |
| :--- | :--- | :--- | ---: |
| `pending-search` | The official website has not been found yet | 官方網站尚未找到 | 6 |
| `pending-verification` | A candidate source exists; facts are not verified against official pages yet | 已有候選來源，尚未對官方頁面核實 | 572 |
| `incomplete-data` | Checked, but required facts are missing (for example no public pricing page) | 查過，但必要事實不齊（例如沒有公開定價頁） | 486 |
| `duplicate` | Same tool as another entry | 與另一筆是同一個工具 | 0 |
| `inactive` | The product is confirmed discontinued | 已確認停止服務 | 0 |
| `renamed-or-merged` | Confirmed renamed or merged into another product | 已確認更名或併入其他產品 | 0 |

A status with 0 means our records do not confirm any such case today.

## By reason / 依原因

| Reason / 原因 | Count |
| :--- | ---: |
| 官方定價頁未找到。暫不發布價格、免費額度或商用授權。 | 359 |
| 已排入查核，價格、免費額度與商用授權尚未對官方頁面核實。 | 299 |
| 查核資料不齊（來源不足或欄位缺漏）。 | 112 |
| 登記的網站在最後檢查時無法連線，官方網站未確認。 | 112 |
| 找到的網站內容與工具名稱對不上，官方網站未確認。 | 56 |
| 官方網站擋自動讀取，待人工重驗；不代表網站不存在。 | 53 |
| 觀察中，尚未開始查核。 | 52 |
| 現有紀錄不足以收錄，原因未細分。 | 15 |
| 僅有名單代號，尚未開始搜尋官方網站。 | 6 |

## By gap category / 依缺口分類

| Gap category / 缺口分類 | Count |
| :--- | ---: |
| `null` | 531 |
| 官方定價頁未找到 | 359 |
| 官方網站未找到 | 174 |

`null` means our records do not say which of the eight categories applies — we do not pick one by guess.

## How the counts are produced / 怎麼算的

1. Start from the maintainers' seed list.
2. Remove every tool already in the published dataset.
3. Keep one entry per identifier and per name.
4. Give each remaining tool a status from our own check records. Nothing is looked up or inferred at export time.
5. Count. Re-running `python3 scripts/export_pending_tools.py` on the same input gives byte-identical files.

Checks: `python3 scripts/check_pending_tools.py`.

Know an official pricing page we may have missed? Please open an Issue with the official URL.

License: CC BY-SA 4.0 — attribution required: AMPM-AIOPS 問問貓 (ampm-aiops.com)
