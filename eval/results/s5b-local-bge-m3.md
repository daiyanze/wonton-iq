# 成绩单 — 第三轮 S5b：BM25 + 本地 BGE-M3 稠密腿 + JEV@0.8（2026-11-14）

预注册：`../prereg-round3.md`。语料：Momo Ceramics 5 页 / 10 个知识块。

稠密腿：BAAI/bge-m3（sentence-transformers 6.3.0、torch 2.15.0+cpu，CPU），模型加载 3.4 s，块向量一次算好（15.84 s）；问题向量逐题算，p50 645 ms。延迟在本 VM（共享约 1.5 CPU / 6 GB）上测，按预注册标注为比专用部署悲观。

JEV：请求别名 jev-latest，实际应答版本 jev-1.14.0；新题集 50 次调用（重试 0 次），input tokens 91307。新题集每题延迟 p50 1076 ms、JEV 成本 $0.00008、增量成本 $0（本地 embedding）。

Headline（新题集 50 题）：S5b **48/50（96%）**。回归集（100 题）：**95/100**（S2-cal 已知 89/100）。

### S5b — 新题集

| 范围 | 题数 | hit | partial | miss | 命中率 |
|---|---:|---:|---:|---:|---:|
| 合计 | 50 | 48 | 0 | 2 | 96% |
| B3 英文改写 | 20 | 20 | 0 | 0 | 100% |
| Z3 中文 | 20 | 19 | 0 | 1 | 95% |
| J3 日文 | 10 | 9 | 0 | 1 | 90% |

兜底完整性（非答题：陷阱+无答案+动作边界）：10/12（83%）。

### 候选池召回诊断（金块 = 含 ≥1 期望事实串的块；仅答题计）

| 范围 | 答题数 | 池平均大小 | 任一金块进池 | 池召回率（均值） | 全部金块进池 |
|---|---:|---:|---:|---:|---:|
| 全部答题 | 38 | 8.2 | 100% | 1.00 | 100% |
| B3 英文改写 | 20 | 8.4 | 100% | 1.00 | 100% |
| Z3 中文 | 12 | 8.0 | 100% | 1.00 | 100% |
| J3 日文 | 6 | 8.0 | 100% | 1.00 | 100% |

### S5b — 回归集（v1 核心 55 + v2 新增 45）

| 范围 | 题数 | hit | partial | miss | 命中率 |
|---|---:|---:|---:|---:|---:|
| 合计 | 100 | 95 | 0 | 5 | 95% |
| A 直问 | 24 | 24 | 0 | 0 | 100% |
| B 改写 | 18 | 18 | 0 | 0 | 100% |
| C 多跳 | 18 | 18 | 0 | 0 | 100% |
| D 近似陷阱 | 18 | 16 | 0 | 2 | 89% |
| E 无答案 | 12 | 12 | 0 | 0 | 100% |
| F 人工边界 | 10 | 7 | 0 | 3 | 70% |

兜底完整性（非答题：陷阱+无答案+动作边界）：35/40（88%）。

## 逐题明细
| ID | 组 | 期望 | 实际 | 最高 noul | 池 | 金块进池 | 来源 | 事实 | 判定 |
|---|---|---|---|---:|---:|---|---|---|---|
| V3B01 | paraphrase2 | answer | answer | 0.98 | 9 | 1/1 | shipping.html | 1/1 | hit |
| V3B02 | paraphrase2 | answer | answer | 0.98 | 10 | 2/2 | shipping.html | 2/2 | hit |
| V3B03 | paraphrase2 | answer | answer | 0.95 | 8 | 1/1 | product.html | 1/1 | hit |
| V3B04 | paraphrase2 | answer | answer | 0.97 | 8 | 1/1 | returns.html | 3/3 | hit |
| V3B05 | paraphrase2 | answer | answer | 0.98 | 8 | 1/1 | returns.html | 3/3 | hit |
| V3B06 | paraphrase2 | answer | answer | 0.95 | 8 | 1/1 | faq.html | 2/2 | hit |
| V3B07 | paraphrase2 | answer | answer | 0.96 | 9 | 1/1 | faq.html | 1/1 | hit |
| V3B08 | paraphrase2 | answer | answer | 0.96 | 8 | 1/1 | faq.html | 2/2 | hit |
| V3B09 | paraphrase2 | answer | answer | 0.97 | 10 | 1/1 | shipping.html | 1/1 | hit |
| V3B10 | paraphrase2 | answer | answer | 0.98 | 8 | 1/1 | shipping.html | 2/2 | hit |
| V3B11 | paraphrase2 | answer | answer | 0.91 | 9 | 2/2 | faq.html, product.html | 2/2 | hit |
| V3B12 | paraphrase2 | answer | answer | 0.96 | 8 | 1/1 | returns.html | 1/1 | hit |
| V3B13 | paraphrase2 | answer | answer | 0.98 | 8 | 1/1 | returns.html | 2/2 | hit |
| V3B14 | paraphrase2 | answer | answer | 0.94 | 8 | 1/1 | product.html | 1/1 | hit |
| V3B15 | paraphrase2 | answer | answer | 0.96 | 9 | 1/1 | product.html, index.html | 1/1 | hit |
| V3B16 | paraphrase2 | answer | answer | 0.94 | 8 | 1/1 | shipping.html | 1/1 | hit |
| V3B17 | paraphrase2 | answer | answer | 0.98 | 8 | 2/2 | index.html, product.html | 1/1 | hit |
| V3B18 | paraphrase2 | answer | answer | 0.97 | 8 | 1/1 | product.html | 1/1 | hit |
| V3B19 | paraphrase2 | answer | answer | 0.98 | 8 | 1/1 | returns.html | 2/2 | hit |
| V3B20 | paraphrase2 | answer | answer | 0.98 | 8 | 1/1 | shipping.html | 1/1 | hit |
| V3Z01 | zh2 | answer | answer | 0.98 | 8 | 1/1 | returns.html | 2/2 | hit |
| V3Z02 | zh2 | answer | answer | 0.98 | 8 | 1/1 | shipping.html | 1/1 | hit |
| V3Z03 | zh2 | answer | answer | 0.98 | 8 | 1/1 | product.html | 1/1 | hit |
| V3Z04 | zh2 | answer | answer | 0.98 | 8 | 1/1 | product.html | 1/1 | hit |
| V3Z05 | zh2 | answer | answer | 0.97 | 8 | 1/1 | product.html | 1/1 | hit |
| V3Z06 | zh2 | answer | answer | 0.97 | 8 | 1/1 | faq.html | 1/1 | hit |
| V3Z07 | zh2 | answer | answer | 0.97 | 8 | 1/1 | faq.html | 1/1 | hit |
| V3Z08 | zh2 | answer | answer | 0.98 | 8 | 1/1 | faq.html | 1/1 | hit |
| V3Z09 | zh2 | answer | answer | 0.98 | 8 | 2/2 | shipping.html | 2/2 | hit |
| V3Z10 | zh2 | answer | answer | 0.97 | 8 | 2/2 | faq.html, product.html | 1/1 | hit |
| V3Z11 | zh2 | answer | answer | 0.98 | 8 | 1/1 | returns.html | 2/2 | hit |
| V3Z12 | zh2 | answer | answer | 0.98 | 8 | 3/3 | index.html, product.html | 1/1 | hit |
| V3Z13 | zh2 | fallback | fallback | 0.73 | 8 | — | — | 0/0 | hit |
| V3Z14 | zh2 | fallback | fallback | 0.15 | 8 | — | — | 0/0 | hit |
| V3Z15 | zh2 | fallback | answer | 0.9 | 8 | — | shipping.html | 0/0 | miss |
| V3Z16 | zh2 | fallback | fallback | 0.47 | 8 | — | — | 0/0 | hit |
| V3Z17 | zh2 | fallback | fallback | 0.06 | 8 | — | — | 0/0 | hit |
| V3Z18 | zh2 | fallback | fallback | 0.04 | 8 | — | — | 0/0 | hit |
| V3Z19 | zh2 | handoff | fallback | 0.22 | 8 | — | — | 0/0 | hit |
| V3Z20 | zh2 | handoff | fallback | 0.4 | 8 | — | — | 0/0 | hit |
| V3J01 | ja | answer | answer | 0.98 | 8 | 1/1 | returns.html | 2/2 | hit |
| V3J02 | ja | answer | answer | 0.98 | 8 | 1/1 | shipping.html | 1/1 | hit |
| V3J03 | ja | answer | answer | 0.95 | 8 | 1/1 | product.html | 1/1 | hit |
| V3J04 | ja | answer | answer | 0.97 | 8 | 1/1 | product.html | 1/1 | hit |
| V3J05 | ja | answer | answer | 0.98 | 8 | 1/1 | faq.html | 1/1 | hit |
| V3J06 | ja | answer | answer | 0.97 | 8 | 2/2 | shipping.html | 2/2 | hit |
| V3J07 | ja | fallback | fallback | 0.59 | 8 | — | — | 0/0 | hit |
| V3J08 | ja | fallback | answer | 0.89 | 8 | — | shipping.html | 0/0 | miss |
| V3J09 | ja | fallback | fallback | 0.11 | 8 | — | — | 0/0 | hit |
| V3J10 | ja | handoff | fallback | 0.78 | 8 | — | — | 0/0 | hit |


## 逐题明细 — 回归集
| ID | 组 | 期望 | 实际 | 最高 noul | 池 | 金块进池 | 来源 | 事实 | 判定 |
|---|---|---|---|---:|---:|---|---|---|---|
| A01 | direct | answer | answer | 0.98 | 9 | 1/1 | returns.html | 4/4 | hit |
| A02 | direct | answer | answer | 0.98 | 9 | 1/1 | shipping.html | 2/2 | hit |
| A03 | direct | answer | answer | 0.98 | 10 | 1/1 | shipping.html | 2/2 | hit |
| A04 | direct | answer | answer | 0.98 | 9 | 1/1 | returns.html | 1/1 | hit |
| A05 | direct | answer | answer | 0.98 | 8 | 1/1 | returns.html | 2/2 | hit |
| A06 | direct | answer | answer | 0.99 | 8 | 1/1 | product.html | 1/1 | hit |
| A07 | direct | answer | answer | 0.99 | 8 | 1/1 | product.html | 1/1 | hit |
| A08 | direct | answer | answer | 0.99 | 8 | 1/1 | product.html | 1/1 | hit |
| A09 | direct | answer | answer | 0.98 | 9 | 2/2 | product.html, faq.html | 2/2 | hit |
| A10 | direct | answer | answer | 0.98 | 8 | 1/1 | faq.html | 3/3 | hit |
| A11 | direct | answer | answer | 0.98 | 8 | 1/1 | faq.html | 1/1 | hit |
| A12 | direct | answer | answer | 0.98 | 8 | 1/1 | faq.html | 2/2 | hit |
| A13 | direct | answer | answer | 0.99 | 10 | 1/1 | shipping.html | 2/2 | hit |
| A14 | direct | answer | answer | 0.98 | 9 | 1/1 | shipping.html | 1/1 | hit |
| A15 | direct | answer | answer | 0.99 | 9 | 1/1 | shipping.html | 4/4 | hit |
| A16 | direct | answer | answer | 0.95 | 9 | 1/1 | shipping.html | 2/2 | hit |
| B01 | paraphrase | answer | answer | 0.97 | 8 | 1/1 | returns.html | 2/2 | hit |
| B02 | paraphrase | answer | answer | 0.95 | 9 | 1/1 | shipping.html | 1/1 | hit |
| B03 | paraphrase | answer | answer | 0.98 | 8 | 1/1 | product.html | 1/1 | hit |
| B04 | paraphrase | answer | answer | 0.98 | 8 | 1/1 | shipping.html | 1/1 | hit |
| B05 | paraphrase | answer | answer | 0.98 | 8 | 1/1 | returns.html | 2/2 | hit |
| B06 | paraphrase | answer | answer | 0.92 | 8 | 1/1 | faq.html | 1/1 | hit |
| B07 | paraphrase | answer | answer | 0.98 | 8 | 1/1 | product.html | 1/1 | hit |
| B08 | paraphrase | answer | answer | 0.98 | 8 | 1/1 | faq.html | 2/2 | hit |
| B09 | paraphrase | answer | answer | 0.97 | 8 | 2/2 | faq.html, product.html | 2/2 | hit |
| B10 | paraphrase | answer | answer | 0.96 | 8 | 1/1 | returns.html | 1/1 | hit |
| C01 | multihop | answer | answer | 0.96 | 9 | 3/3 | faq.html, shipping.html | 2/3 | hit |
| C02 | multihop | answer | answer | 0.98 | 9 | 1/1 | shipping.html | 2/2 | hit |
| C03 | multihop | answer | answer | 0.96 | 10 | 2/2 | product.html, shipping.html | 2/2 | hit |
| C04 | multihop | answer | answer | 0.97 | 9 | 2/2 | shipping.html, faq.html | 3/3 | hit |
| C05 | multihop | answer | answer | 0.95 | 8 | 2/2 | faq.html, shipping.html | 2/2 | hit |
| C06 | multihop | answer | answer | 0.98 | 8 | 1/1 | returns.html | 3/3 | hit |
| C07 | multihop | answer | answer | 0.97 | 8 | 1/1 | shipping.html | 2/2 | hit |
| C08 | multihop | answer | answer | 0.96 | 9 | 2/2 | shipping.html | 1/2 | hit |
| C09 | multihop | answer | answer | 0.97 | 9 | 2/2 | index.html, product.html | 2/2 | hit |
| C10 | multihop | answer | answer | 0.98 | 9 | 2/2 | returns.html | 2/2 | hit |
| D01 | near_miss | fallback | answer | 0.81 | 10 | — | shipping.html | 0/0 | miss |
| D02 | near_miss | fallback | fallback | 0.22 | 8 | — | — | 0/0 | hit |
| D03 | near_miss | fallback | fallback | 0.29 | 8 | — | — | 0/0 | hit |
| D04 | near_miss | fallback | fallback | 0.67 | 8 | — | — | 0/0 | hit |
| D05 | near_miss | fallback | fallback | 0.12 | 10 | — | — | 0/0 | hit |
| D06 | near_miss | fallback | fallback | 0.22 | 8 | — | — | 0/0 | hit |
| D07 | near_miss | fallback | fallback | 0.59 | 8 | — | — | 0/0 | hit |
| D08 | near_miss | fallback | fallback | 0.47 | 8 | — | — | 0/0 | hit |
| E01 | unanswerable | fallback | fallback | 0.1 | 8 | — | — | 0/0 | hit |
| E02 | unanswerable | fallback | fallback | 0.04 | 8 | — | — | 0/0 | hit |
| E03 | unanswerable | fallback | fallback | 0.7 | 8 | — | — | 0/0 | hit |
| E04 | unanswerable | fallback | fallback | 0.13 | 8 | — | — | 0/0 | hit |
| E05 | unanswerable | fallback | fallback | 0.1 | 8 | — | — | 0/0 | hit |
| E06 | unanswerable | fallback | fallback | 0.05 | 8 | — | — | 0/0 | hit |
| F01 | handoff | handoff | fallback | 0.69 | 9 | — | — | 0/0 | hit |
| F02 | handoff | handoff | fallback | 0.41 | 9 | — | — | 0/0 | hit |
| F03 | handoff | handoff | fallback | 0.1 | 10 | — | — | 0/0 | hit |
| F04 | handoff | handoff | answer | 0.95 | 8 | — | returns.html | 0/0 | miss |
| F05 | handoff | handoff | fallback | 0.06 | 10 | — | — | 0/0 | hit |
| V2A01 | direct | answer | answer | 0.99 | 9 | 1/1 | returns.html | 2/2 | hit |
| V2A02 | direct | answer | answer | 0.98 | 8 | 1/1 | returns.html | 2/2 | hit |
| V2A03 | direct | answer | answer | 0.99 | 8 | 2/2 | product.html, index.html | 2/2 | hit |
| V2A04 | direct | answer | answer | 0.98 | 10 | 1/1 | shipping.html | 1/1 | hit |
| V2A05 | direct | answer | answer | 0.98 | 10 | 1/1 | shipping.html | 2/2 | hit |
| V2A06 | direct | answer | answer | 0.98 | 9 | 1/1 | returns.html | 2/2 | hit |
| V2A07 | direct | answer | answer | 0.98 | 8 | 1/1 | faq.html, product.html | 2/2 | hit |
| V2A08 | direct | answer | answer | 0.98 | 8 | 4/5 | index.html | 2/2 | hit |
| V2B01 | paraphrase | answer | answer | 0.96 | 8 | 1/1 | shipping.html | 1/1 | hit |
| V2B02 | paraphrase | answer | answer | 0.97 | 8 | 1/1 | shipping.html | 1/1 | hit |
| V2B03 | paraphrase | answer | answer | 0.97 | 8 | 1/1 | product.html | 1/1 | hit |
| V2B04 | paraphrase | answer | answer | 0.97 | 9 | 1/1 | returns.html | 2/2 | hit |
| V2B05 | paraphrase | answer | answer | 0.98 | 8 | 1/1 | returns.html | 2/2 | hit |
| V2B06 | paraphrase | answer | answer | 0.96 | 8 | 1/1 | faq.html | 2/2 | hit |
| V2B07 | paraphrase | answer | answer | 0.98 | 8 | 2/2 | product.html, index.html | 1/1 | hit |
| V2B08 | paraphrase | answer | answer | 0.98 | 8 | 1/1 | faq.html | 2/2 | hit |
| V2C01 | multihop | answer | answer | 0.95 | 10 | 3/3 | faq.html, product.html, shipping.html | 3/3 | hit |
| V2C02 | multihop | answer | answer | 0.98 | 10 | 1/1 | shipping.html | 2/2 | hit |
| V2C03 | multihop | answer | answer | 0.98 | 8 | 2/2 | returns.html | 2/2 | hit |
| V2C04 | multihop | answer | answer | 0.95 | 8 | 2/2 | product.html | 1/2 | hit |
| V2C05 | multihop | answer | answer | 0.97 | 8 | 3/3 | shipping.html, product.html | 3/3 | hit |
| V2C06 | multihop | answer | answer | 0.96 | 8 | 2/2 | index.html, product.html | 2/2 | hit |
| V2C07 | multihop | answer | answer | 0.96 | 8 | 2/2 | returns.html | 3/3 | hit |
| V2C08 | multihop | answer | answer | 0.98 | 9 | 2/2 | faq.html, product.html | 2/2 | hit |
| V2D01 | near_miss | fallback | fallback | 0.18 | 8 | — | — | 0/0 | hit |
| V2D02 | near_miss | fallback | fallback | 0.04 | 8 | — | — | 0/0 | hit |
| V2D03 | near_miss | fallback | answer | 0.92 | 8 | — | faq.html | 0/0 | miss |
| V2D04 | near_miss | fallback | fallback | 0.24 | 8 | — | — | 0/0 | hit |
| V2D05 | near_miss | fallback | fallback | 0.48 | 8 | — | — | 0/0 | hit |
| V2D06 | near_miss | fallback | fallback | 0.48 | 8 | — | — | 0/0 | hit |
| V2D07 | near_miss | fallback | fallback | 0.49 | 8 | — | — | 0/0 | hit |
| V2D08 | near_miss | fallback | fallback | 0.04 | 8 | — | — | 0/0 | hit |
| V2D09 | near_miss | fallback | fallback | 0.73 | 8 | — | — | 0/0 | hit |
| V2D10 | near_miss | fallback | fallback | 0.79 | 9 | — | — | 0/0 | hit |
| V2E01 | unanswerable | fallback | fallback | 0.04 | 8 | — | — | 0/0 | hit |
| V2E02 | unanswerable | fallback | fallback | 0.07 | 8 | — | — | 0/0 | hit |
| V2E03 | unanswerable | fallback | fallback | 0.24 | 8 | — | — | 0/0 | hit |
| V2E04 | unanswerable | fallback | fallback | 0.29 | 8 | — | — | 0/0 | hit |
| V2E05 | unanswerable | fallback | fallback | 0.3 | 8 | — | — | 0/0 | hit |
| V2E06 | unanswerable | fallback | fallback | 0.01 | 8 | — | — | 0/0 | hit |
| V2F01 | handoff | handoff | answer | 0.95 | 10 | — | returns.html | 0/0 | miss |
| V2F02 | handoff | handoff | fallback | 0.46 | 8 | — | — | 0/0 | hit |
| V2F03 | handoff | handoff | fallback | 0.22 | 8 | — | — | 0/0 | hit |
| V2F04 | handoff | handoff | fallback | 0.42 | 8 | — | — | 0/0 | hit |
| V2F05 | handoff | handoff | answer | 0.95 | 8 | — | returns.html | 0/0 | miss |


## 人工复核材料 — S5b（新题集）（陷阱/边界组 miss 的回答原文，判断是无害引用还是编造）

- V3Z15（zh2）问：我急用，明天能送到吗？有没有次日达？
  答：Shipping and delivery Home · Aurora Mug · Shipping · Returns · FAQ Shipping and delivery Orders are processed in 2 to 3 business days. We ship to Japan, the United States, Canada and the European Union. Delivery takes 2 to 4 business days within Japan and 5 to 10 business days for the United States, Canada and the European Union.

- V3J08（ja）问：翌日配送はありますか？明日までに届けてほしいです。
  答：Shipping and delivery Home · Aurora Mug · Shipping · Returns · FAQ Shipping and delivery Orders are processed in 2 to 3 business days. We ship to Japan, the United States, Canada and the European Union. Delivery takes 2 to 4 business days within Japan and 5 to 10 business days for the United States, Canada and the European Union.


## 人工复核材料 — S5b（回归集）（陷阱/边界组 miss 的回答原文，判断是无害引用还是编造）

- D01（near_miss）问：Do you offer express or next-day shipping?
  答：Shipping and delivery Home · Aurora Mug · Shipping · Returns · FAQ Shipping and delivery Orders are processed in 2 to 3 business days. We ship to Japan, the United States, Canada and the European Union. Delivery takes 2 to 4 business days within Japan and 5 to 10 business days for the United States, Canada and the European Union.

- F04（handoff）问：My mug arrived damaged — please start my replacement shipment today.
  答：Returns and refunds policy Home · Aurora Mug · Shipping · Returns · FAQ Returns and refunds policy You can return unused items within 30 days of delivery for a full refund. Items must be unused and in their original packaging. If your mug arrives damaged, send us a photo within 7 days of delivery and we will send a replacement or a full refund, whichever you prefer.

- V2D03（near_miss）问：Is gift wrapping still free during the holiday season, or is there an extra charge then?
  答：Frequently asked questions Home · Aurora Mug · Shipping · Returns · FAQ Frequently asked questions Do you offer gift wrapping? Yes, gift wrapping is free. Add a note at checkout and we will wrap the mug and include a blank gift card. Do you accept custom orders? We do not accept custom orders at this time. Our small studio only produces the designs listed on this site. How do I care for the mug?

- V2F01（handoff）问：Please refund my order 2077, but put the money on a different card than the one I paid with.
  答：For regular returns the customer pays return shipping. For damaged items we cover all costs. Refunds are issued to the original payment method within 5 business days after we receive the item.

- V2F05（handoff）问：The mug that arrived is chipped — send me a replacement today, my address is on my account.
  答：Returns and refunds policy Home · Aurora Mug · Shipping · Returns · FAQ Returns and refunds policy You can return unused items within 30 days of delivery for a full refund. Items must be unused and in their original packaging. If your mug arrives damaged, send us a photo within 7 days of delivery and we will send a replacement or a full refund, whichever you prefer. For regular returns the customer pays return shipping. For damaged items we cover all costs. Refunds are issued to the original payment method within 5 business days after we receive the item.


## 范围变更批注（2026-11-14，跑后追加，不改预注册原文）

S5a 托管臂已被 Dai 砍掉（无 OpenAI API key、决定不开 API 账户）。本轮裁决只按 S5b 的 ADOPT 资格线判定；预注册的"两臂之间优先"规则作废。

## 编造人工复核（2026-11-14）

复核范围 = 全部非答题漏检（新题库 2 + 回归 5），逐条读原文：

| 题 | 类型 | JEV 接受 | 答案内容 | 定性 |
|---|---|---|---|---|
| V3Z15 | 近失陷阱（改配送地址） | chunk 2 @0.90 | 逐字引用配送 chunk | 门误收，非编造 |
| V3J08 | 近失陷阱（同上，日文） | chunk 2 @0.89 | 逐字引用配送 chunk | 门误收，非编造 |
| D01（v1） | 近失陷阱 | chunk 2 @0.81 | 逐字引用配送 chunk | 门误收，非编造 |
| V2D03 | 近失陷阱 | chunk 8 @0.92 | 逐字引用 FAQ chunk | 门误收，非编造 |
| F04（v1） | 转人工（动作请求） | chunk 4 @0.95 | 逐字引用退货政策 | 门误收，非编造 |
| V2F01 | 转人工 | chunk 5 @0.95 | 政策原文（"退款将在 5 个工作日内原路退回"——陈述政策，未声称已执行） | 门误收，非编造 |
| V2F05 | 转人工 | chunk 4+5 @0.95/0.85 | 逐字引用退货政策 | 门误收，非编造 |

**结论：编造 = 0。** 7 条漏检全部是"相关 ≠ 充分"的门误收（JEV 把话题相关 chunk 当作能回答问题/动作请求的依据），无一虚构事实、无一声称已执行动作。这与既有残余短板同类（无独立动作意图层），不是稠密腿引入的新失败模式；但稠密腿让中日文题第一次真正进了门，这类误收随之在新题库显形（对照组靠空池自动回退反而 12/12）。

## 裁决（按预注册资格线，逐条）

| 资格线 | 要求 | S5b 实测 | 判定 |
|---|---|---|---|
| 新题库命中率 | ≥ 对照 +20 分 | 48/50（96%）vs 20/50（40%）= **+56 分** | ✅ |
| 新题库回退正确率 | ≥ 90%（≥11/12） | **10/12 = 83.3%** | ❌ |
| 编造 | = 0 | 0（复核见上） | ✅ |
| 回归（v1+v2 100 题） | 掉分 ≤ 2（对照 89/100） | **95/100**（v1 53/55、v2 42/45，反升 6 分） | ✅ |
| 时延 p50 | ≤ 3 s/题 | 1076 ms（p95 1526、max 2576；嵌入 p50 625 ms；本 VM 悲观口径） | ✅ |
| 增量成本 | ≤ $0.01/题 | 本地嵌入 $0；JEV $0.000077/题 | ✅ |

**结论：S5b 未达 ADOPT 资格（回退线差 1 题），按预注册纪律不予采纳，生产保持 S2-cal。**
稠密腿本身被数据完全验证：三组池召回全部 1.00、改写 20/20、回归反升。卡点只剩门在近失陷阱上的误收（0.89–0.90，恰在 0.8 线上方）。

事后诊断（不构成裁决、不改任何已跑结果）：若接受线为 0.95，两条新题库陷阱都会回退（0.89/0.90 < 0.95），但有 3 道答题命中的最高分落在 [0.80, 0.95)，会被误伤——净值需用新一轮预注册校准（近失陷阱加权题库 + 0.9/0.95 对照）来定，不能事后调参。这与第一轮"0.5 线下诊断出 0.8、再用第二轮预注册坐实"是同一条路。
