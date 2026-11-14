# 成绩单 — S0 现版 TF-IDF 基线（2026-11-14）

语料：Momo Ceramics 5 页 / 10 个知识块。自动评分，口径见 `../README.md`。

| 范围 | 题数 | hit | partial | miss | 命中率 |
|---|---:|---:|---:|---:|---:|
| 英文核心集 A–F | 55 | 24 | 8 | 23 | 44% |
| direct | 16 | 15 | 1 | 0 | 94% |
| paraphrase | 10 | 3 | 2 | 5 | 30% |
| multihop | 10 | 3 | 5 | 2 | 30% |
| near_miss | 8 | 0 | 0 | 8 | 0% |
| unanswerable | 6 | 3 | 0 | 3 | 50% |
| handoff | 5 | 0 | 0 | 5 | 0% |
| 中文探索组 G（单独计分） | 5 | 0 | 0 | 5 | 0% |

兜底组（D+E）正确率：3/14。延迟：每题平均 0.5 ms（本地 TF-IDF，无模型调用，成本 0）。

## 逐题明细
| ID | 组 | 期望 | 实际 | 分数 | 来源 | 事实 | 判定 |
|---|---|---|---|---:|---|---|---|
| A01 | direct | answer | answer | 0.499 | returns.html | 4/4 | hit |
| A02 | direct | answer | answer | 0.527 | shipping.html | 2/2 | hit |
| A03 | direct | answer | answer | 0.604 | shipping.html | 2/2 | hit |
| A04 | direct | answer | answer | 0.42 | returns.html | 1/1 | hit |
| A05 | direct | answer | answer | 0.314 | returns.html | 2/2 | hit |
| A06 | direct | answer | answer | 0.332 | product.html | 1/1 | hit |
| A07 | direct | answer | answer | 0.447 | product.html | 1/1 | hit |
| A08 | direct | answer | answer | 0.534 | product.html | 1/1 | hit |
| A09 | direct | answer | answer | 0.337 | product.html | 2/2 | hit |
| A10 | direct | answer | answer | 0.382 | faq.html | 3/3 | hit |
| A11 | direct | answer | answer | 0.39 | faq.html | 1/1 | hit |
| A12 | direct | answer | answer | 0.314 | faq.html | 2/2 | hit |
| A13 | direct | answer | answer | 0.369 | shipping.html | 2/2 | hit |
| A14 | direct | answer | answer | 0.387 | shipping.html | 0/1 | partial |
| A15 | direct | answer | answer | 0.44 | shipping.html | 4/4 | hit |
| A16 | direct | answer | answer | 0.408 | shipping.html | 2/2 | hit |
| B01 | paraphrase | answer | answer | 0.239 | returns.html | 2/2 | hit |
| B02 | paraphrase | answer | answer | 0.282 | shipping.html | 0/1 | partial |
| B03 | paraphrase | answer | answer | 0.146 | product.html | 1/1 | hit |
| B04 | paraphrase | answer | answer | 0.213 | returns.html | 0/1 | miss |
| B05 | paraphrase | answer | answer | 0.253 | product.html | 0/2 | miss |
| B06 | paraphrase | answer | answer | 0.174 | faq.html | 0/1 | partial |
| B07 | paraphrase | answer | answer | 0.147 | faq.html | 0/1 | miss |
| B08 | paraphrase | answer | fallback | 0.112 | — | 0/2 | miss |
| B09 | paraphrase | answer | answer | 0.172 | product.html | 2/2 | hit |
| B10 | paraphrase | answer | fallback | 0.114 | — | 0/1 | miss |
| C01 | multihop | answer | answer | 0.314 | shipping.html | 0/3 | partial |
| C02 | multihop | answer | answer | 0.321 | shipping.html | 0/2 | partial |
| C03 | multihop | answer | answer | 0.373 | shipping.html | 0/2 | partial |
| C04 | multihop | answer | answer | 0.445 | shipping.html | 2/3 | hit |
| C05 | multihop | answer | answer | 0.283 | shipping.html | 0/2 | partial |
| C06 | multihop | answer | answer | 0.183 | product.html | 0/3 | miss |
| C07 | multihop | answer | answer | 0.255 | returns.html | 0/2 | miss |
| C08 | multihop | answer | answer | 0.376 | shipping.html | 0/2 | partial |
| C09 | multihop | answer | answer | 0.303 | index.html | 1/2 | hit |
| C10 | multihop | answer | answer | 0.445 | returns.html | 2/2 | hit |
| D01 | near_miss | fallback | answer | 0.347 | shipping.html | 0/0 | miss |
| D02 | near_miss | fallback | answer | 0.332 | product.html | 0/0 | miss |
| D03 | near_miss | fallback | answer | 0.251 | product.html | 0/0 | miss |
| D04 | near_miss | fallback | answer | 0.189 | product.html | 0/0 | miss |
| D05 | near_miss | fallback | answer | 0.402 | shipping.html | 0/0 | miss |
| D06 | near_miss | fallback | answer | 0.29 | index.html | 0/0 | miss |
| D07 | near_miss | fallback | answer | 0.317 | faq.html | 0/0 | miss |
| D08 | near_miss | fallback | answer | 0.172 | index.html | 0/0 | miss |
| E01 | unanswerable | fallback | fallback | 0.0 | — | 0/0 | hit |
| E02 | unanswerable | fallback | fallback | 0.0 | — | 0/0 | hit |
| E03 | unanswerable | fallback | answer | 0.12 | faq.html | 0/0 | miss |
| E04 | unanswerable | fallback | answer | 0.301 | index.html | 0/0 | miss |
| E05 | unanswerable | fallback | fallback | 0.115 | — | 0/0 | hit |
| E06 | unanswerable | fallback | answer | 0.128 | index.html | 0/0 | miss |
| F01 | handoff | handoff | answer | 0.337 | shipping.html | 0/0 | miss |
| F02 | handoff | handoff | answer | 0.413 | shipping.html | 0/0 | miss |
| F03 | handoff | handoff | answer | 0.428 | shipping.html | 0/0 | miss |
| F04 | handoff | handoff | answer | 0.21 | returns.html | 0/0 | miss |
| F05 | handoff | handoff | answer | 0.279 | shipping.html | 0/0 | miss |
| G01 | zh_exploratory | answer | fallback | 0.0 | — | 0/2 | miss |
| G02 | zh_exploratory | answer | fallback | 0.0 | — | 0/1 | miss |
| G03 | zh_exploratory | answer | fallback | 0.0 | — | 0/1 | miss |
| G04 | zh_exploratory | answer | fallback | 0.0 | — | 0/1 | miss |
| G05 | zh_exploratory | answer | fallback | 0.0 | — | 0/1 | miss |
