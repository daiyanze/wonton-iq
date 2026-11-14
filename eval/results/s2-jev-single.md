# 成绩单 — S2 BM25 + JEV 单轮决策（2026-11-14）

语料：Momo Ceramics 5 页 / 10 个知识块，与 S0/S1 同一批次 onboard。自动评分，口径见 `../README.md`。

判定方式：BM25 候选（全部命中块）逐块由 JEV 打 Noul 概率，>= 0.5 选中拼答，一块没选中则兜底。判定线运行前定死（见 `run_s2.py`）。

JEV 模型：请求别名 jev-latest，实际应答版本 jev-1.14.0。

| 范围 | 题数 | hit | partial | miss | 命中率 |
|---|---:|---:|---:|---:|---:|
| 英文核心集 A–F | 55 | 46 | 1 | 8 | 84% |
| direct | 16 | 16 | 0 | 0 | 100% |
| paraphrase | 10 | 6 | 1 | 3 | 60% |
| multihop | 10 | 10 | 0 | 0 | 100% |
| near_miss | 8 | 5 | 0 | 3 | 62% |
| unanswerable | 6 | 6 | 0 | 0 | 100% |
| handoff | 5 | 3 | 0 | 2 | 60% |
| 中文探索组 G（单独计分） | 5 | 0 | 0 | 5 | 0% |

兜底组（D+E）正确率：11/14。人工边界组（F）正确率：3/5。

延迟与成本：每题服务时间 p50 411 ms、平均 412 ms（核心集，含本地 BM25 与 JEV 调用，不含线程排队）；JEV 单次调用 p50 376 ms，共 52 次调用（另重试 0 次）；input tokens 共 70793，核心集每题成本 $0.00005（$0.042/1M input tokens，output 免费）。

## 逐题明细
| ID | 组 | 期望 | 实际 | 最高 noul | 来源 | 事实 | 判定 |
|---|---|---|---|---:|---|---|---|
| A01 | direct | answer | answer | 0.98 | returns.html | 4/4 | hit |
| A02 | direct | answer | answer | 0.98 | shipping.html | 2/2 | hit |
| A03 | direct | answer | answer | 0.98 | shipping.html | 2/2 | hit |
| A04 | direct | answer | answer | 0.98 | returns.html | 1/1 | hit |
| A05 | direct | answer | answer | 0.98 | returns.html | 2/2 | hit |
| A06 | direct | answer | answer | 0.99 | product.html | 1/1 | hit |
| A07 | direct | answer | answer | 0.99 | product.html | 1/1 | hit |
| A08 | direct | answer | answer | 0.99 | product.html | 1/1 | hit |
| A09 | direct | answer | answer | 0.98 | faq.html, product.html | 2/2 | hit |
| A10 | direct | answer | answer | 0.98 | faq.html | 3/3 | hit |
| A11 | direct | answer | answer | 0.98 | faq.html | 1/1 | hit |
| A12 | direct | answer | answer | 0.98 | faq.html | 2/2 | hit |
| A13 | direct | answer | answer | 0.98 | shipping.html | 2/2 | hit |
| A14 | direct | answer | answer | 0.98 | product.html, shipping.html | 1/1 | hit |
| A15 | direct | answer | answer | 0.99 | shipping.html | 4/4 | hit |
| A16 | direct | answer | answer | 0.96 | shipping.html | 2/2 | hit |
| B01 | paraphrase | answer | answer | 0.97 | returns.html | 2/2 | hit |
| B02 | paraphrase | answer | answer | 0.95 | shipping.html | 1/1 | hit |
| B03 | paraphrase | answer | answer | 0.98 | product.html | 1/1 | hit |
| B04 | paraphrase | answer | answer | 0.98 | shipping.html | 1/1 | hit |
| B05 | paraphrase | answer | fallback | 0.06 | — | 0/2 | miss |
| B06 | paraphrase | answer | fallback | 0.18 | — | 0/1 | miss |
| B07 | paraphrase | answer | fallback | 0.03 | — | 0/1 | miss |
| B08 | paraphrase | answer | answer | 0.98 | faq.html | 2/2 | hit |
| B09 | paraphrase | answer | answer | 0.97 | product.html, faq.html | 2/2 | hit |
| B10 | paraphrase | answer | answer | 0.56 | returns.html | 0/1 | partial |
| C01 | multihop | answer | answer | 0.96 | faq.html, shipping.html | 2/3 | hit |
| C02 | multihop | answer | answer | 0.98 | shipping.html | 2/2 | hit |
| C03 | multihop | answer | answer | 0.96 | product.html, shipping.html | 2/2 | hit |
| C04 | multihop | answer | answer | 0.97 | shipping.html, faq.html | 3/3 | hit |
| C05 | multihop | answer | answer | 0.95 | faq.html, product.html, shipping.html | 2/2 | hit |
| C06 | multihop | answer | answer | 0.98 | returns.html | 3/3 | hit |
| C07 | multihop | answer | answer | 0.97 | shipping.html | 2/2 | hit |
| C08 | multihop | answer | answer | 0.96 | shipping.html | 1/2 | hit |
| C09 | multihop | answer | answer | 0.96 | index.html, product.html | 2/2 | hit |
| C10 | multihop | answer | answer | 0.98 | returns.html | 2/2 | hit |
| D01 | near_miss | fallback | answer | 0.79 | shipping.html | 0/0 | miss |
| D02 | near_miss | fallback | fallback | 0.16 | — | 0/0 | hit |
| D03 | near_miss | fallback | fallback | 0.29 | — | 0/0 | hit |
| D04 | near_miss | fallback | answer | 0.7 | returns.html | 0/0 | miss |
| D05 | near_miss | fallback | fallback | 0.09 | — | 0/0 | hit |
| D06 | near_miss | fallback | fallback | 0.04 | — | 0/0 | hit |
| D07 | near_miss | fallback | answer | 0.56 | faq.html | 0/0 | miss |
| D08 | near_miss | fallback | fallback | 0.48 | — | 0/0 | hit |
| E01 | unanswerable | fallback | fallback | — | — | 0/0 | hit |
| E02 | unanswerable | fallback | fallback | — | — | 0/0 | hit |
| E03 | unanswerable | fallback | fallback | — | — | 0/0 | hit |
| E04 | unanswerable | fallback | fallback | 0.13 | — | 0/0 | hit |
| E05 | unanswerable | fallback | fallback | 0.09 | — | 0/0 | hit |
| E06 | unanswerable | fallback | fallback | 0.05 | — | 0/0 | hit |
| F01 | handoff | handoff | answer | 0.72 | returns.html | 0/0 | miss |
| F02 | handoff | handoff | fallback | 0.43 | — | 0/0 | hit |
| F03 | handoff | handoff | fallback | 0.09 | — | 0/0 | hit |
| F04 | handoff | handoff | answer | 0.95 | returns.html | 0/0 | miss |
| F05 | handoff | handoff | fallback | 0.05 | — | 0/0 | hit |
| G01 | zh_exploratory | answer | fallback | — | — | 0/2 | miss |
| G02 | zh_exploratory | answer | fallback | — | — | 0/1 | miss |
| G03 | zh_exploratory | answer | fallback | — | — | 0/1 | miss |
| G04 | zh_exploratory | answer | fallback | — | — | 0/1 | miss |
| G05 | zh_exploratory | answer | fallback | — | — | 0/1 | miss |

## 人工复核材料（D/F 组 miss 的回答原文，判断是无害引用还是编造）

- D01（near_miss）问：Do you offer express or next-day shipping?
  答：Shipping and delivery Home · Aurora Mug · Shipping · Returns · FAQ Shipping and delivery Orders are processed in 2 to 3 business days. We ship to Japan, the United States, Canada and the European Union. Delivery takes 2 to 4 business days within Japan and 5 to 10 business days for the United States, Canada and the European Union.

- D04（near_miss）问：Do you offer a warranty if the mug cracks after a year?
  答：Returns and refunds policy Home · Aurora Mug · Shipping · Returns · FAQ Returns and refunds policy You can return unused items within 30 days of delivery for a full refund. Items must be unused and in their original packaging. If your mug arrives damaged, send us a photo within 7 days of delivery and we will send a replacement or a full refund, whichever you prefer.

- D07（near_miss）问：Can I buy a gift card to give someone instead of a mug?
  答：Frequently asked questions Home · Aurora Mug · Shipping · Returns · FAQ Frequently asked questions Do you offer gift wrapping? Yes, gift wrapping is free. Add a note at checkout and we will wrap the mug and include a blank gift card. Do you accept custom orders? We do not accept custom orders at this time. Our small studio only produces the designs listed on this site. How do I care for the mug?

- F01（handoff）问：Please cancel my order number 1042 and refund me right now.
  答：Returns and refunds policy Home · Aurora Mug · Shipping · Returns · FAQ Returns and refunds policy You can return unused items within 30 days of delivery for a full refund. Items must be unused and in their original packaging. If your mug arrives damaged, send us a photo within 7 days of delivery and we will send a replacement or a full refund, whichever you prefer. For regular returns the customer pays return shipping. For damaged items we cover all costs. Refunds are issued to the original payment method within 5 business days after we receive the item.

- F04（handoff）问：My mug arrived damaged — please start my replacement shipment today.
  答：Returns and refunds policy Home · Aurora Mug · Shipping · Returns · FAQ Returns and refunds policy You can return unused items within 30 days of delivery for a full refund. Items must be unused and in their original packaging. If your mug arrives damaged, send us a photo within 7 days of delivery and we will send a replacement or a full refund, whichever you prefer. For regular returns the customer pays return shipping. For damaged items we cover all costs. Refunds are issued to the original payment method within 5 business days after we receive the item.


## 人工复核结论（2026-11-14 复核）

D 组 miss 3 题（D01、D04、D07）、F 组 miss 2 题（F01、F04），逐条核对回答原文：全部为站内原文的逐字引用，**编造 = 0，不触发规则 5 一票否决**。D01 引配送政策全文，没有声称提供次日达；D04 引退货政策，没有声称有一年保修；D07 引的 FAQ 块提到礼品包装“附赠空白礼品卡”，没有声称礼品卡可单独购买（五题里最接近误导的一条，仍属无害引用）；F01、F04 引退货与换货政策，没有声称已取消订单或已发出换货。这批 miss 的性质是“该兜底时答了”，不是编造——抽取式拼答在结构上生成不出新事实。

判定线敏感性（诊断，与 S1 的敏感性表同法：用同一批已记录概率换线重判，不改 headline 判定）：0.5 → 46/55、D+E 11/14；0.6 与 0.7 → 47/55、D+E 12/14；0.8 与 0.9 → 50/55、D+E 14/14、C 组仍 10/10。概率在本题库上呈双峰分布：真命中的块几乎都在 0.95 以上，三个陷阱块在 0.56–0.81。但事后改线就是拿题库调参，违反预注册纪律，本成绩单不改判；它只说明差距是决策边界的标定问题，下一步若走这条路要预注册新判定线并扩充题库重跑。
