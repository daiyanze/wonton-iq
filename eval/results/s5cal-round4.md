# 成绩单 — 第四轮 S5b 接受线校准：0.8 / 0.9 / 0.95（2026-11-14）

预注册：`../prereg-round4.md`（先于 v4 新题与本轮任何模型调用写定）。语料：Momo Ceramics 5 页 / 10 个知识块（冻结）。管线 = 第三轮 S5b 本体（直接 import `run_s5`，未复制逻辑）；完整性断言：{"run_s5_accept": 0.8, "dense_topk": 8, "rrf_k": 60, "noul_template_sha256_16": "38a54efd70a934a9", "jev_instructions_verbatim_from": "run_s2.NOUL_INSTRUCTIONS / NOUL_CRITERIA"}。

JEV：请求别名 jev-latest，实际应答版本 jev-1.14.0；v4 题库共 40 次调用（重试 0 次），input tokens 74348，每题成本 $0.00008，每题延迟 p50 1128 ms（本 VM 共享约 1.5 CPU 的悲观口径，同第三轮）。**接受线只决定哪些已打分块被拼进答案，不产生额外调用——三条线的延迟与成本完全相同，不随线变化。**

复判一致性校验：v4 按 0.8 线复判 vs run_s5 原判，不一致 0 题；第三轮记录概率按 0.8 线复判 vs 第三轮已存 verdict，不一致 v3 新题 0 题、v1+v2 0 题。

## v4 题库（40 题）三线判分

| 线 | 总命中 /40 | 回退集（陷阱+无答案+转人工）/34 | 回退正确率 | 可答对照 /6 |
|---|---:|---:|---:|---:|
| 0.8 | 36 | 30 | 88.2% | 6 |
| 0.9 | 39 | 33 | 97.1% | 6 |
| 0.95 | 39 | 33 | 97.1% | 6 |

### 线 0.8 分组明细

| 组 | 题数 | hit | partial | miss |
|---|---:|---:|---:|---:|
| T4 近失陷阱 | 20 | 17 | 0 | 3 |
| U4 无答案 | 8 | 8 | 0 | 0 |
| H4 人工边界 | 6 | 5 | 0 | 1 |
| A4 可答对照 | 6 | 6 | 0 | 0 |

### 线 0.9 分组明细

| 组 | 题数 | hit | partial | miss |
|---|---:|---:|---:|---:|
| T4 近失陷阱 | 20 | 19 | 0 | 1 |
| U4 无答案 | 8 | 8 | 0 | 0 |
| H4 人工边界 | 6 | 6 | 0 | 0 |
| A4 可答对照 | 6 | 6 | 0 | 0 |

### 线 0.95 分组明细

| 组 | 题数 | hit | partial | miss |
|---|---:|---:|---:|---:|
| T4 近失陷阱 | 20 | 19 | 0 | 1 |
| U4 无答案 | 8 | 8 | 0 | 0 |
| H4 人工边界 | 6 | 6 | 0 | 0 |
| A4 可答对照 | 6 | 6 | 0 | 0 |

## 第三轮已记录概率复判（回归/诊断，不进 v4 主裁决）

| 题集 | 线 0.8（复判） | 线 0.9 | 线 0.95 |
|---|---:|---:|---:|
| v3 新题集（50） | 48 | 49 | 47 |
| v1+v2 回归集（100） | 95 | 96 | 93 |

- v3 新题集 线 0.9 相对 0.8 判定变化：1 题（V3J08）
- v3 新题集 线 0.95 相对 0.8 判定变化：5 题（V3B11, V3B14, V3B16, V3Z15, V3J08）
- v1+v2 回归集 线 0.9 相对 0.8 判定变化：1 题（D01）
- v1+v2 回归集 线 0.95 相对 0.8 判定变化：6 题（B06, C01, D01, V2C01, V2C05, V2D03）

## 逐题明细 — v4（三线并列）

| ID | 组 | 期望 | 最高 noul | 0.8 | 0.9 | 0.95 |
|---|---|---|---:|---|---|---|
| V4T01 | T4 近失陷阱 | fallback | 0.7 | hit | hit | hit |
| V4T02 | T4 近失陷阱 | fallback | 0.13 | hit | hit | hit |
| V4T03 | T4 近失陷阱 | fallback | 0.08 | hit | hit | hit |
| V4T04 | T4 近失陷阱 | fallback | 0.87 | miss | hit | hit |
| V4T05 | T4 近失陷阱 | fallback | 0.82 | miss | hit | hit |
| V4T06 | T4 近失陷阱 | fallback | 0.26 | hit | hit | hit |
| V4T07 | T4 近失陷阱 | fallback | 0.59 | hit | hit | hit |
| V4T08 | T4 近失陷阱 | fallback | 0.96 | miss | miss | miss |
| V4T09 | T4 近失陷阱 | fallback | 0.72 | hit | hit | hit |
| V4T10 | T4 近失陷阱 | fallback | 0.77 | hit | hit | hit |
| V4T11 | T4 近失陷阱 | fallback | 0.15 | hit | hit | hit |
| V4T12 | T4 近失陷阱 | fallback | 0.08 | hit | hit | hit |
| V4T13 | T4 近失陷阱 | fallback | 0.4 | hit | hit | hit |
| V4T14 | T4 近失陷阱 | fallback | 0.79 | hit | hit | hit |
| V4T15 | T4 近失陷阱 | fallback | 0.15 | hit | hit | hit |
| V4T16 | T4 近失陷阱 | fallback | 0.6 | hit | hit | hit |
| V4T17 | T4 近失陷阱 | fallback | 0.17 | hit | hit | hit |
| V4T18 | T4 近失陷阱 | fallback | 0.42 | hit | hit | hit |
| V4T19 | T4 近失陷阱 | fallback | 0.19 | hit | hit | hit |
| V4T20 | T4 近失陷阱 | fallback | 0.32 | hit | hit | hit |
| V4U01 | U4 无答案 | fallback | 0.06 | hit | hit | hit |
| V4U02 | U4 无答案 | fallback | 0.79 | hit | hit | hit |
| V4U03 | U4 无答案 | fallback | 0.32 | hit | hit | hit |
| V4U04 | U4 无答案 | fallback | 0.06 | hit | hit | hit |
| V4U05 | U4 无答案 | fallback | 0.05 | hit | hit | hit |
| V4U06 | U4 无答案 | fallback | 0.07 | hit | hit | hit |
| V4U07 | U4 无答案 | fallback | 0.06 | hit | hit | hit |
| V4U08 | U4 无答案 | fallback | 0.04 | hit | hit | hit |
| V4H01 | H4 人工边界 | handoff | 0.3 | hit | hit | hit |
| V4H02 | H4 人工边界 | handoff | 0.57 | hit | hit | hit |
| V4H03 | H4 人工边界 | handoff | 0.05 | hit | hit | hit |
| V4H04 | H4 人工边界 | handoff | 0.88 | miss | hit | hit |
| V4H05 | H4 人工边界 | handoff | 0.08 | hit | hit | hit |
| V4H06 | H4 人工边界 | handoff | 0.05 | hit | hit | hit |
| V4A01 | A4 可答对照 | answer | 0.99 | hit | hit | hit |
| V4A02 | A4 可答对照 | answer | 0.98 | hit | hit | hit |
| V4A03 | A4 可答对照 | answer | 0.97 | hit | hit | hit |
| V4A04 | A4 可答对照 | answer | 0.98 | hit | hit | hit |
| V4A05 | A4 可答对照 | answer | 0.97 | hit | hit | hit |
| V4A06 | A4 可答对照 | answer | 0.98 | hit | hit | hit |


## 人工复核材料 — 线 0.9（v4 回退组 miss 的回答原文）

- V4T08（trap4）问：Do you provide a prepaid return label, or do I have to arrange the return postage myself?
  答：For regular returns the customer pays return shipping. For damaged items we cover all costs. Refunds are issued to the original payment method within 5 business days after we receive the item.


## 人工复核材料 — 线 0.95（v4 回退组 miss 的回答原文）

- V4T08（trap4）问：Do you provide a prepaid return label, or do I have to arrange the return postage myself?
  答：For regular returns the customer pays return shipping. For damaged items we cover all costs. Refunds are issued to the original payment method within 5 business days after we receive the item.


## 人工复核材料 — 线 0.8（v4 回退组 miss 的回答原文）

- V4T04（trap4）问：Can you print a personal message on the gift card instead of leaving it blank?
  答：Frequently asked questions Home · Aurora Mug · Shipping · Returns · FAQ Frequently asked questions Do you offer gift wrapping? Yes, gift wrapping is free. Add a note at checkout and we will wrap the mug and include a blank gift card. Do you accept custom orders? We do not accept custom orders at this time. Our small studio only produces the designs listed on this site. How do I care for the mug?

- V4T05（trap4）问：Is the Aurora Mug available in any other colours besides the midnight blue one?
  答：Aurora Mug — product details Home · Aurora Mug · Shipping · Returns · FAQ Aurora Mug — product details The Aurora Mug is a handmade stoneware mug with a matte midnight-blue glaze. Capacity is 350 ml. Price is 38 US dollars. The mug is microwave safe and dishwasher safe, though hand washing is recommended to keep the glaze finish. Each piece is made to order in small batches.

- V4T08（trap4）问：Do you provide a prepaid return label, or do I have to arrange the return postage myself?
  答：For regular returns the customer pays return shipping. For damaged items we cover all costs. Refunds are issued to the original payment method within 5 business days after we receive the item.

- V4H04（hand4）问：帮我催一下我的订单，让仓库今天就把它发出来。
  答：Shipping and delivery Home · Aurora Mug · Shipping · Returns · FAQ Shipping and delivery Orders are processed in 2 to 3 business days. We ship to Japan, the United States, Canada and the European Union. Delivery takes 2 to 4 business days within Japan and 5 to 10 business days for the United States, Canada and the European Union.


## 编造人工复核（2026-11-14）

复核范围 = v4 回退集在候选线 0.9 / 0.95 下的全部 miss（两条线相同，仅 V4T08 一题），以及对照线 0.8 下的全部 miss（V4T04、V4T05、V4T08、V4H04，第三轮未复核过的新题），逐条读原文：

| 题 | 线 | JEV 接受 | 答案内容 | 定性 |
|---|---|---|---|---|
| V4T08（预付退货面单） | 0.8 / 0.9 / 0.95 均 miss | chunk 5 @0.96 | 逐字引用退货块（"常规退货运费顾客付、破损我们全包、退款 5 个工作日原路退回"） | 门误收，非编造：未声称提供预付面单，未虚构事实 |
| V4T04（礼品卡代印寄语） | 仅 0.8 miss | chunk 8 @0.87 | 逐字引用 FAQ 块（原文写的正是"空白礼品卡"） | 门误收，非编造 |
| V4T05（其他配色） | 仅 0.8 miss | chunk 6 @0.82 | 逐字引用产品块（只写午夜蓝） | 门误收，非编造 |
| V4H04（催发货） | 仅 0.8 miss | chunk 2 @0.88 | 逐字引用配送块 | 门误收，非编造：未声称已催/已发货 |

**结论：三条线编造均 = 0。** 全部 miss 是同一类"相关 ≠ 充分"的门误收（逐字引用话题相邻块），无一虚构事实、无一声称已执行动作。V4T08 是三条线都漏的唯一陷阱：它问的"预付面单"与 chunk 5 的"谁付退货运费"确实高度相邻（某种意义上答了后半句），被以 0.96 接受——抬线解决不了这一题，属残余问题记录在案。

## 裁决（按预注册 ADOPT 规则逐条）

| 规则 | 要求 | 线 0.9 | 线 0.95 |
|---|---|---|---|
| (a) v4 回退正确率 | ≥ 90%（34 题至少 31） | **33/34 = 97.1%** ✅ | **33/34 = 97.1%** ✅ |
| (b) v4 答题不误伤 | 对照 6 题命中下降 ≤ 1（vs 0.8 线 6/6） | 6/6，下降 0 ✅ | 6/6，下降 0 ✅ |
| (c) 编造 | = 0（人工复核） | 0 ✅ | 0 ✅ |
| (d) 第三轮复判不塌 | v3 新题 ≥ 47/50 且 v1+v2 ≥ 93/100 | **49/50、96/100** ✅ | 47/50、93/100 ✅（两项都贴线） |

对照线 0.8 在 v4 上的成绩（同批概率）：总命中 36/40、回退 30/34 = 88.2%——在全新的陷阱加权题库上复现了第三轮的失败模式，说明本轮题库的鉴别力与校准对象都对。

两条候选线都达标，按预注册"两线都达标取较低线（少牺牲召回）"：**ADOPT 线 0.9——即"混合管线（BM25 + BGE-M3 稠密腿）+ JEV 接受线 0.9"通过本轮校准。** 0.95 的额外代价在复判里看得很清楚：v3 答题组丢 V3B11（0.91）、V3B14（0.94）、V3B16（0.94）三题、回归再丢 B06/C01/V2C01/V2C05 等答题题，换来的只是多拦下 V3Z15 一道陷阱（0.90，恰好压在 0.9 线上仍被接受——这是 0.9 线已知的残余漏检）与 V2D03；净值不如 0.9。线 0.9 在复判中的变化只有两处且都是修好陷阱：V3J08（0.89 → 拒）、回归 D01（0.81 → 拒），答题组零损失。

**按预注册，ADOPT 不等于动生产：app.py 保持 S2-cal 不变，是否切换到"混合 + 0.9"仍需 Dai 另行点头。**
