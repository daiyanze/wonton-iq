# 成绩单 — 第三轮 control：S2-cal（BM25 候选 + JEV 单轮，接受线 noul >= 0.8）（2026-11-14）

预注册：`../prereg-round3.md`（先于新题与本轮任何模型调用写定）。语料：Momo Ceramics 5 页 / 10 个知识块，与前两轮同一 onboard。control 即现行线上系统，在新题集上新鲜跑。

JEV：请求别名 jev-latest，实际应答版本 jev-1.14.0；新题集共 19 次调用（重试 0 次），input tokens 18287。每题延迟 p50 0 ms、每题 JEV 成本 $0.00002。

Headline（新题集 50 题）：S2-cal **20/50（40%）**。

### S2-cal control — 新题集

| 范围 | 题数 | hit | partial | miss | 命中率 |
|---|---:|---:|---:|---:|---:|
| 合计 | 50 | 20 | 0 | 30 | 40% |
| B3 英文改写 | 20 | 7 | 0 | 13 | 35% |
| Z3 中文 | 20 | 9 | 0 | 11 | 45% |
| J3 日文 | 10 | 4 | 0 | 6 | 40% |

兜底完整性（非答题：陷阱+无答案+动作边界）：12/12（100%）。

### 候选池召回诊断（金块 = 含 ≥1 期望事实串的块；仅答题计）

| 范围 | 答题数 | 池平均大小 | 任一金块进池 | 池召回率（均值） | 全部金块进池 |
|---|---:|---:|---:|---:|---:|
| 全部答题 | 38 | 1.7 | 21% | 0.21 | 21% |
| B3 英文改写 | 20 | 3.0 | 35% | 0.35 | 35% |
| Z3 中文 | 12 | 0.4 | 8% | 0.08 | 8% |
| J3 日文 | 6 | 0.0 | 0% | 0.00 | 0% |

## 逐题明细
| ID | 组 | 期望 | 实际 | 最高 noul | 池 | 金块进池 | 来源 | 事实 | 判定 |
|---|---|---|---|---:|---:|---|---|---|---|
| V3B01 | paraphrase2 | answer | fallback | 0.05 | 4 | 0/1 | — | 0/1 | miss |
| V3B02 | paraphrase2 | answer | answer | 0.98 | 9 | 2/2 | shipping.html | 2/2 | hit |
| V3B03 | paraphrase2 | answer | fallback | 0.03 | 2 | 0/1 | — | 0/1 | miss |
| V3B04 | paraphrase2 | answer | fallback | 0.05 | 3 | 0/1 | — | 0/3 | miss |
| V3B05 | paraphrase2 | answer | fallback | 0.03 | 1 | 0/1 | — | 0/3 | miss |
| V3B06 | paraphrase2 | answer | answer | 0.96 | 2 | 1/1 | faq.html | 2/2 | hit |
| V3B07 | paraphrase2 | answer | fallback | 0.27 | 4 | 0/1 | — | 0/1 | miss |
| V3B08 | paraphrase2 | answer | fallback | 0.04 | 2 | 0/1 | — | 0/2 | miss |
| V3B09 | paraphrase2 | answer | answer | 0.97 | 6 | 1/1 | shipping.html | 1/1 | hit |
| V3B10 | paraphrase2 | answer | fallback | 0.04 | 1 | 0/1 | — | 0/2 | miss |
| V3B11 | paraphrase2 | answer | answer | 0.89 | 5 | 2/2 | faq.html, product.html | 2/2 | hit |
| V3B12 | paraphrase2 | answer | fallback | 0.37 | 2 | 0/1 | — | 0/1 | miss |
| V3B13 | paraphrase2 | answer | fallback | 0.03 | 1 | 0/1 | — | 0/2 | miss |
| V3B14 | paraphrase2 | answer | answer | 0.94 | 2 | 1/1 | product.html | 1/1 | hit |
| V3B15 | paraphrase2 | answer | answer | 0.95 | 4 | 0/1 | index.html | 0/1 | miss |
| V3B16 | paraphrase2 | answer | fallback | 0.04 | 3 | 0/1 | — | 0/1 | miss |
| V3B17 | paraphrase2 | answer | fallback | — | 0 | 0/2 | — | 0/1 | miss |
| V3B18 | paraphrase2 | answer | fallback | — | 0 | 0/1 | — | 0/1 | miss |
| V3B19 | paraphrase2 | answer | answer | 0.98 | 4 | 1/1 | returns.html | 2/2 | hit |
| V3B20 | paraphrase2 | answer | answer | 0.98 | 6 | 1/1 | shipping.html | 1/1 | hit |
| V3Z01 | zh2 | answer | fallback | — | 0 | 0/1 | — | 0/2 | miss |
| V3Z02 | zh2 | answer | fallback | — | 0 | 0/1 | — | 0/1 | miss |
| V3Z03 | zh2 | answer | fallback | — | 0 | 0/1 | — | 0/1 | miss |
| V3Z04 | zh2 | answer | answer | 0.98 | 5 | 1/1 | product.html | 1/1 | hit |
| V3Z05 | zh2 | answer | fallback | — | 0 | 0/1 | — | 0/1 | miss |
| V3Z06 | zh2 | answer | fallback | — | 0 | 0/1 | — | 0/1 | miss |
| V3Z07 | zh2 | answer | fallback | — | 0 | 0/1 | — | 0/1 | miss |
| V3Z08 | zh2 | answer | fallback | — | 0 | 0/1 | — | 0/1 | miss |
| V3Z09 | zh2 | answer | fallback | — | 0 | 0/2 | — | 0/2 | miss |
| V3Z10 | zh2 | answer | fallback | — | 0 | 0/2 | — | 0/1 | miss |
| V3Z11 | zh2 | answer | fallback | — | 0 | 0/1 | — | 0/2 | miss |
| V3Z12 | zh2 | answer | fallback | — | 0 | 0/3 | — | 0/1 | miss |
| V3Z13 | zh2 | fallback | fallback | — | 0 | — | — | 0/0 | hit |
| V3Z14 | zh2 | fallback | fallback | — | 0 | — | — | 0/0 | hit |
| V3Z15 | zh2 | fallback | fallback | — | 0 | — | — | 0/0 | hit |
| V3Z16 | zh2 | fallback | fallback | — | 0 | — | — | 0/0 | hit |
| V3Z17 | zh2 | fallback | fallback | — | 0 | — | — | 0/0 | hit |
| V3Z18 | zh2 | fallback | fallback | — | 0 | — | — | 0/0 | hit |
| V3Z19 | zh2 | handoff | fallback | — | 0 | — | — | 0/0 | hit |
| V3Z20 | zh2 | handoff | fallback | — | 0 | — | — | 0/0 | hit |
| V3J01 | ja | answer | fallback | — | 0 | 0/1 | — | 0/2 | miss |
| V3J02 | ja | answer | fallback | — | 0 | 0/1 | — | 0/1 | miss |
| V3J03 | ja | answer | fallback | — | 0 | 0/1 | — | 0/1 | miss |
| V3J04 | ja | answer | fallback | — | 0 | 0/1 | — | 0/1 | miss |
| V3J05 | ja | answer | fallback | — | 0 | 0/1 | — | 0/1 | miss |
| V3J06 | ja | answer | fallback | — | 0 | 0/2 | — | 0/2 | miss |
| V3J07 | ja | fallback | fallback | — | 0 | — | — | 0/0 | hit |
| V3J08 | ja | fallback | fallback | — | 0 | — | — | 0/0 | hit |
| V3J09 | ja | fallback | fallback | — | 0 | — | — | 0/0 | hit |
| V3J10 | ja | handoff | fallback | — | 0 | — | — | 0/0 | hit |


## 人工复核材料 — S2-cal control（陷阱/边界组 miss 的回答原文，判断是无害引用还是编造）

无陷阱/边界组 miss。


## 人工复核（对照组，2026-11-14 跑后追加）

- **陷阱/转人工题：12/12 全部正确回退，零漏检** —— 按预注册口径无漏检样本可复核，**编造 = 0**。
  其中中日文的非答题是靠空候选池"自动回退"拿到的（池召回 0），不是判别能力 — 见 README 第三轮小结。
- 答题组唯一"答了但错"的 V3B15：JEV 以 0.95 接受了 chunk 0（首页"尺寸有小幅差异"），
  但期望事实"vary by up to 5 mm"在 chunk 7、从未进池。答案是逐字引用、无编造，属池召回 + 事实粒度问题，不在编造否决范围内。
- 对照组新题库总分 **20/50**：paraphrase2 7/20、zh2 9/20（12 道答题仅 Z04 靠拉丁词 "Aurora" 命中）、ja 4/10（6 道答题全灭）。
  池召回（答题）：改写 0.35、中 0.08、日 0.00 — 本轮要修的结构性短板在此。
