# 成绩单 — 第二轮校准 S2-cal（BM25 + JEV 单轮，接受线 noul >= 0.8）（2026-11-14）

预注册：`../prereg-round2.md`（先于新题与本轮任何 JEV 调用写定）。语料：Momo Ceramics 5 页 / 10 个知识块，与第一轮同一 onboard。

JEV：请求别名 jev-latest，实际应答版本 jev-1.14.0；新题集共 39 次调用（重试 0 次），input tokens 51923，单次调用 p50 367 ms。

Headline 对比（新题集 45 题）：S2-cal@0.8 **39/45（87%）**；S2@0.5 对照 37/45（82%）；S1 对照 23/45（51%）。每题延迟 p50 395 ms、每题成本 $0.00005。

### S2-cal（noul >= 0.8）— 新题集

| 范围 | 题数 | hit | partial | miss | 命中率 |
|---|---:|---:|---:|---:|---:|
| 新题集 A2–F2 | 45 | 39 | 0 | 6 | 87% |
| A 直问 | 8 | 8 | 0 | 0 | 100% |
| B 改写 | 8 | 5 | 0 | 3 | 62% |
| C 多跳 | 8 | 8 | 0 | 0 | 100% |
| D 近似陷阱 | 10 | 9 | 0 | 1 | 90% |
| E 无答案 | 6 | 6 | 0 | 0 | 100% |
| F 人工边界 | 5 | 3 | 0 | 2 | 60% |

兜底组（D+E）正确率：15/16（94%）。人工边界组（F）：3/5。

### S2@0.5 对照（同一批概率重判）— 新题集

| 范围 | 题数 | hit | partial | miss | 命中率 |
|---|---:|---:|---:|---:|---:|
| 新题集 A2–F2 | 45 | 37 | 0 | 8 | 82% |
| A 直问 | 8 | 8 | 0 | 0 | 100% |
| B 改写 | 8 | 5 | 0 | 3 | 62% |
| C 多跳 | 8 | 8 | 0 | 0 | 100% |
| D 近似陷阱 | 10 | 7 | 0 | 3 | 70% |
| E 无答案 | 6 | 6 | 0 | 0 | 100% |
| F 人工边界 | 5 | 3 | 0 | 2 | 60% |

兜底组（D+E）正确率：13/16（81%）。人工边界组（F）：3/5。

### S1 BM25 对照（阈值 -1.0，新鲜跑）— 新题集

| 范围 | 题数 | hit | partial | miss | 命中率 |
|---|---:|---:|---:|---:|---:|
| 新题集 A2–F2 | 45 | 23 | 2 | 20 | 51% |
| A 直问 | 8 | 7 | 1 | 0 | 88% |
| B 改写 | 8 | 4 | 0 | 4 | 50% |
| C 多跳 | 8 | 5 | 1 | 2 | 62% |
| D 近似陷阱 | 10 | 3 | 0 | 7 | 30% |
| E 无答案 | 6 | 3 | 0 | 3 | 50% |
| F 人工边界 | 5 | 1 | 0 | 4 | 20% |

兜底组（D+E）正确率：6/16（38%）。人工边界组（F）：1/5。

### v1 回归集（复用第一轮记录概率离线重判，不合并进 headline）

0.8 线：总命中 50/55（第一轮 0.5 线实测 46/55）。重判前校验：0.5 线重判与第一轮逐题判定不一致 0 题（应为 0；不为 0 说明候选顺序重建有偏差，回归数字需谨慎）。

v1 回归 D+E @0.8：14/14。

## 逐题明细 — S2-cal@0.8（新题集）
| ID | 组 | 期望 | 实际 | 最高 noul | 来源 | 事实 | 判定 |
|---|---|---|---|---:|---|---|---|
| V2A01 | direct | answer | answer | 0.98 | returns.html | 2/2 | hit |
| V2A02 | direct | answer | answer | 0.98 | returns.html | 2/2 | hit |
| V2A03 | direct | answer | answer | 0.99 | product.html, index.html | 2/2 | hit |
| V2A04 | direct | answer | answer | 0.98 | shipping.html | 1/1 | hit |
| V2A05 | direct | answer | answer | 0.98 | shipping.html | 2/2 | hit |
| V2A06 | direct | answer | answer | 0.98 | returns.html | 2/2 | hit |
| V2A07 | direct | answer | answer | 0.98 | faq.html, product.html | 2/2 | hit |
| V2A08 | direct | answer | answer | 0.98 | index.html | 2/2 | hit |
| V2B01 | paraphrase | answer | fallback | — | — | 0/1 | miss |
| V2B02 | paraphrase | answer | answer | 0.98 | shipping.html | 1/1 | hit |
| V2B03 | paraphrase | answer | answer | 0.97 | product.html | 1/1 | hit |
| V2B04 | paraphrase | answer | answer | 0.97 | returns.html | 2/2 | hit |
| V2B05 | paraphrase | answer | fallback | 0.35 | — | 0/2 | miss |
| V2B06 | paraphrase | answer | fallback | 0.04 | — | 0/2 | miss |
| V2B07 | paraphrase | answer | answer | 0.98 | product.html, index.html | 1/1 | hit |
| V2B08 | paraphrase | answer | answer | 0.98 | faq.html | 2/2 | hit |
| V2C01 | multihop | answer | answer | 0.96 | shipping.html, product.html, faq.html | 3/3 | hit |
| V2C02 | multihop | answer | answer | 0.98 | shipping.html | 2/2 | hit |
| V2C03 | multihop | answer | answer | 0.97 | returns.html | 2/2 | hit |
| V2C04 | multihop | answer | answer | 0.94 | product.html | 1/2 | hit |
| V2C05 | multihop | answer | answer | 0.97 | shipping.html, product.html | 2/3 | hit |
| V2C06 | multihop | answer | answer | 0.96 | index.html | 1/2 | hit |
| V2C07 | multihop | answer | answer | 0.96 | returns.html | 2/3 | hit |
| V2C08 | multihop | answer | answer | 0.98 | faq.html, product.html | 2/2 | hit |
| V2D01 | near_miss | fallback | fallback | 0.15 | — | 0/0 | hit |
| V2D02 | near_miss | fallback | fallback | — | — | 0/0 | hit |
| V2D03 | near_miss | fallback | answer | 0.92 | faq.html | 0/0 | miss |
| V2D04 | near_miss | fallback | fallback | 0.21 | — | 0/0 | hit |
| V2D05 | near_miss | fallback | fallback | 0.04 | — | 0/0 | hit |
| V2D06 | near_miss | fallback | fallback | 0.46 | — | 0/0 | hit |
| V2D07 | near_miss | fallback | fallback | 0.03 | — | 0/0 | hit |
| V2D08 | near_miss | fallback | fallback | 0.04 | — | 0/0 | hit |
| V2D09 | near_miss | fallback | fallback | 0.74 | — | 0/0 | hit |
| V2D10 | near_miss | fallback | fallback | 0.79 | — | 0/0 | hit |
| V2E01 | unanswerable | fallback | fallback | — | — | 0/0 | hit |
| V2E02 | unanswerable | fallback | fallback | 0.05 | — | 0/0 | hit |
| V2E03 | unanswerable | fallback | fallback | — | — | 0/0 | hit |
| V2E04 | unanswerable | fallback | fallback | 0.26 | — | 0/0 | hit |
| V2E05 | unanswerable | fallback | fallback | 0.29 | — | 0/0 | hit |
| V2E06 | unanswerable | fallback | fallback | — | — | 0/0 | hit |
| V2F01 | handoff | handoff | answer | 0.95 | returns.html | 0/0 | miss |
| V2F02 | handoff | handoff | fallback | — | — | 0/0 | hit |
| V2F03 | handoff | handoff | fallback | 0.22 | — | 0/0 | hit |
| V2F04 | handoff | handoff | fallback | 0.4 | — | 0/0 | hit |
| V2F05 | handoff | handoff | answer | 0.96 | returns.html | 0/0 | miss |

## 人工复核材料（D/F 组 miss 的回答原文，判断是无害引用还是编造）

- V2D03（near_miss，0.8 线 miss）问：Is gift wrapping still free during the holiday season, or is there an extra charge then?
  答：Frequently asked questions Home · Aurora Mug · Shipping · Returns · FAQ Frequently asked questions Do you offer gift wrapping? Yes, gift wrapping is free. Add a note at checkout and we will wrap the mug and include a blank gift card. Do you accept custom orders? We do not accept custom orders at this time. Our small studio only produces the designs listed on this site. How do I care for the mug?

- V2F01（handoff，0.8 线 miss）问：Please refund my order 2077, but put the money on a different card than the one I paid with.
  答：For regular returns the customer pays return shipping. For damaged items we cover all costs. Refunds are issued to the original payment method within 5 business days after we receive the item.

- V2F05（handoff，0.8 线 miss）问：The mug that arrived is chipped — send me a replacement today, my address is on my account.
  答：Returns and refunds policy Home · Aurora Mug · Shipping · Returns · FAQ Returns and refunds policy You can return unused items within 30 days of delivery for a full refund. Items must be unused and in their original packaging. If your mug arrives damaged, send us a photo within 7 days of delivery and we will send a replacement or a full refund, whichever you prefer.

- V2D09（near_miss，0.5对照 线 miss）问：Can the Aurora Mug go in the oven for reheating food?
  答：Aurora Mug — product details Home · Aurora Mug · Shipping · Returns · FAQ Aurora Mug — product details The Aurora Mug is a handmade stoneware mug with a matte midnight-blue glaze. Capacity is 350 ml. Price is 38 US dollars. The mug is microwave safe and dishwasher safe, though hand washing is recommended to keep the glaze finish. Each piece is made to order in small batches.

- V2D10（near_miss，0.5对照 线 miss）问：Can I exchange my mug for a different design instead of getting a refund?
  答：Returns and refunds policy Home · Aurora Mug · Shipping · Returns · FAQ Returns and refunds policy You can return unused items within 30 days of delivery for a full refund. Items must be unused and in their original packaging. If your mug arrives damaged, send us a photo within 7 days of delivery and we will send a replacement or a full refund, whichever you prefer.


## 人工复核结论（D/F 组 miss 逐条看过回答原文）

S2-cal@0.8 的 D/F miss 共 3 题，S2@0.5 对照共 5 题（多出 V2D09、V2D10），全部核对为**所选块的逐字原文拼接**（用 onboard 块文本逐字比对，全部一致）：

- **V2D03**（两线皆 miss）：答的是 FAQ 块原文（“gift wrapping is free…”）。原文只讲平时免费，全文没有任何“假日季/额外收费”的说法——错在不该答，不在编造。与第一轮 D07 同类（无害引用）。
- **V2F01**（两线皆 miss）：答的是退货块原文，其中“refunds are issued to the original payment method”恰好与顾客“退到另一张卡”的要求相反。没有承诺换卡退款，更没有声称已执行——行为 miss（应转人工），不是编造。
- **V2F05**（两线皆 miss）：答的是退货块原文，“we will send a replacement or a full refund, whichever you prefer”是店铺政策原文，不是“已为你寄出补发”的执行声称。行为 miss，不是编造。
- **V2D09**（仅 0.5 线 miss，最高 noul 0.74）：产品块原文只说微波炉/洗碗机安全，**没有**把安全性升级到烤箱。无害引用；0.8 线下正确兜底。
- **V2D10**（仅 0.5 线 miss，最高 noul 0.79）：退货块原文，没有声称可以换货。无害引用；0.8 线下正确兜底。

**编造 = 0，规则 5（一票否决）不触发。** F 组两题在两条线上都 miss，原因是 JEV 把“陈述相关政策事实”的块判为可答（0.95 / 0.96），与接受线无关——这是系统没有独立转人工判定层的老问题（第一轮 S0/S1 同样没有该层），属行为层缺口，不属编造。

## 按预注册规则逐条判定（prereg-round2.md）

| 条 | 要求 | 实测 | 过线 |
|---|---|---|---|
| 1 | 新题集 D+E ≥ 90% | 15/16 = 93.8% | ✅ |
| 2 | 新题集总命中率 ≥ S1 + 15 个百分点 | 86.7% vs S1 51.1%（+35.6 点） | ✅ |
| 3 | 编造 = 0 | 0（人工复核，见上） | ✅ |
| 4 | 新题集延迟 p50 ≤ 3 秒 | 395 ms | ✅ |
| 5 | 每题成本 ≤ $0.01 | $0.000048 | ✅ |
| 6 | v1 回归集 @0.8 ≥ 44/55 | 50/55（D+E 亦 14/14） | ✅ |

**判定：ADOPT 规则触发。** 建议把 app.py 的决策层换成 JEV 单轮、接受线 noul ≥ 0.8（S2 架构）；按预注册，本轮不动 app.py，等 Dai 最终点头。

对照读数：同一批概率按 0.5 线在新题上是 37/45、D+E 13/16（81%）——和第一轮一样过不了 90% 线；0.8 线把总分反而抬高到 39/45（修好 V2D09/V2D10 两道陷阱，答题组零损失）。新题集 B 组 3 题 miss（V2B01 无 BM25 候选、V2B05/V2B06 最高 noul 0.35/0.04）在两条线上完全一致，与接受线无关，是召回/判定问题，不在本轮标定范围内。
