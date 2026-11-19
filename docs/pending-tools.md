# Pending tools — summary / 待補工具統計

How many tools we know about are **not** in the published dataset ([`data/ai_tools_2026.json`](../data/ai_tools_2026.json)) yet, and why.
Only counts are published here. Tool names, identifiers and URLs of pending tools are not part of this repository.

這裡只公開統計數字：各狀態幾筆、各缺口幾筆、原因幾筆。待補工具的名稱、代號與網址都不在這個倉庫裡，也不發布價格、免費額度或商用授權結論。

**We keep a neutral position: these counts are a record of what we could verify so far. No tool is judged or compared here, and a tool being counted says nothing about its quality.**
**我們站在中立的立場，只做紀錄：這些數字是「目前查得到什麼」，不評價、不比較任何工具；被算在裡面不代表那個工具好或不好。**

## Why this exists / 為什麼做這件事

- We are not saying these tools are bad. For products that charge, we think facts such as public pricing, free-tier limits and commercial-use terms should be there for consumers to look at — that is fairer to consumers.
- Open-source and other free-by-nature tools are a different case: there is no price to list, and having no pricing page is normal. For those, what a consumer needs is the license and the official repository, not a price.
- We have started marking which pending tools show open-source signals (see "Open-source signals" below). That check is incomplete, so the count "no public pricing page found" may still include open-source tools. That count describes a page we did not find; it is not a shortcoming of the tool.
- Our rule for open-source tools: being open source waives only the public-pricing-page requirement. Every other check still applies, and an official hosted version that charges is checked like any other paid product. This rule is not applied in our listing process yet.
- Open source does not mean safe. We do not rate safety; please evaluate it yourself.
- This is a check done on the consumer's side: before a tool's price or free tier appears in our data, we want it confirmed on the tool's own official pages.
- It is not a blacklist and not pressure on anyone. "Pending" only means we have not yet found enough official information; it is not a verdict.
- Any vendor or reader can send an official source through an Issue, and we will check again.
- We do not charge tools for being reviewed or listed.

- 我們不是說這些工具不好。對於要收費的產品，我們認為公開定價、免費額度、商用條款這些資料，本來就應該讓消費者查得到、看得到，這樣對消費者比較公平。
- 開源工具與其他本來就免費的工具是另一回事：它沒有價格可列，沒有定價頁是正常的。對這類工具，消費者需要看的是授權條款與官方原始碼倉庫，不是價格。
- 我們已經開始標出哪些待補工具有開源跡象（見下方「開源跡象」）。這次盤點並不完整，所以「官方定價頁未找到」這個數字裡仍可能包含開源工具。這個數字講的是「我們沒找到那個頁面」，不是那個工具有什麼不足。
- 我們對開源工具的規則：開源只免「要有公開定價頁」這一關，其他審核照舊；官方另有收費的代管版時，代管版照一般收費產品審。這條規則目前還沒有套用到收錄流程。
- 開源不代表安全。我們不評安全性，請自行評估。
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

## Open-source signals / 開源跡象

Checked on / 盤點日: 2026-11-19. Tools checked / 盤點筆數: **1064**.

| signal | Meaning | 說明 | Count |
| :--- | :--- | :--- | ---: |
| `repository-open-source-license` | The official homepage links to a repository whose name matches the tool, under a common open-source license | 官網首頁連到名稱對得上的原始碼倉庫，而且是常見的開源授權 | 51 |
| `repository-license-conditional-or-unmarked` | Such a repository is linked, but its license is conditional, unmarked or could not be read | 有連到這樣的倉庫，但授權附條件、沒有標示或讀不到 | 45 |
| `no-matching-repository-link` | No repository with a matching name is linked from the homepage | 首頁沒有名稱對得上的倉庫連結 | 819 |
| `homepage-unreadable` | The homepage on record could not be read at check time | 登記的官網在檢查時讀不到 | 149 |
| `no-homepage-on-record` | No homepage on record | 沒有登記官網 | 0 |

For the tools with a linked repository (the first two rows), we read the repository's own description:
有連到倉庫的（前兩列），我們再讀倉庫的自述，看它是不是工具本身：

| repository role | Meaning | 說明 | Count |
| :--- | :--- | :--- | ---: |
| `product-itself` | The repository describes itself as the tool itself | 倉庫自述就是這個工具本身 | 43 |
| `companion-only` | The repository is only a companion: an SDK, plug-in, docs, examples or an issue tracker | 倉庫只是周邊：開發套件、外掛、文件、範例或問題回報區 | 38 |
| `hosted-service-of-open-core` | The repository is an open-source core; the pending entry is its official hosted service | 倉庫是開源核心，待補的是它的官方代管服務 | 5 |
| `undetermined` | Cannot be told from the repository's own description | 依倉庫自述無法判定 | 10 |

Of the `product-itself` tools: 26 under a common open-source license, 17 with a conditional or unmarked license.
`product-itself` 當中：26 筆是常見開源授權，17 筆授權附條件或沒有標示。

Limits of this check / 這次盤點的限制：

- A linked open-source repository is a signal, not proof that the tool itself is open source.
- `no-matching-repository-link` does not mean "not open source": the homepage may simply not link its repository, or the names may differ.
- The repository role was read from the repository's own description; the source code was not reviewed.
- The homepage read is the one on our records; for most pending tools it is not yet confirmed as the official one.
- 連到一個開源倉庫只是跡象，不能證明工具本身就是開源。
- `no-matching-repository-link` 不代表「不是開源」：可能只是首頁沒放倉庫連結，或名稱對不上。
- 倉庫的角色是依倉庫自述判讀，沒有逐一讀原始碼。
- 讀的是我們紀錄裡登記的官網；多數待補工具的官網還沒有確認是不是官方的。

## How the counts are produced / 怎麼算的

1. Start from the maintainers' seed list.
2. Remove every tool already in the published dataset.
3. Keep one entry per identifier and per name.
4. Give each remaining tool a status from our own check records. Nothing is looked up or inferred at export time.
5. Count. Re-running `python3 scripts/export_pending_tools.py` on the same input gives byte-identical files.

Checks: `python3 scripts/check_pending_tools.py`.

Know an official pricing page we may have missed? Please open an Issue with the official URL.

License: CC BY-SA 4.0 — attribution required: AMPM-AIOPS 問問貓 (ampm-aiops.com)
