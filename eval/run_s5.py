#!/usr/bin/env python3
"""第三轮混合检索实验 runner（预注册 prereg-round3.md，2026-11-14）。

三个臂（一次只变候选生成这一个变量，JEV 门控/拼答/兜底与线上 S2-cal 逐字一致）：
- control：S2-cal 本体——BM25 全部命中块作候选池、BM25 顺序拼答，接受线 noul >= 0.8。
  本轮只在新题集（questions-v3-additions.json 50 题）上新鲜跑。
- s5b：BM25 ∪ 稠密 top-8（本地 BGE-M3，sentence-transformers，L2 归一化余弦），
  接受块按 RRF（k=60）融合 BM25 表与稠密 top-8 表定拼答顺序。新题集 + 回归集
  （v1 英文核心 55 + v2 新增 45 = 100 题）都跑。须用装了 torch 的 venv 解释器运行。
- s5a：托管稠密腿（OpenAI text-embedding-3-small）。本轮只注册不跑：key 要等 Dai
  经安全入口提交、后续任务接线连接器后才能用；现在调用该后端会直接报
  “awaiting connector” 错误，不许绕路取 key。

逐题记录：候选池大小、金块（包含 ≥1 期望事实串的块）进池数与池召回率、JEV 逐块
概率、延迟拆分（embedding / BM25 / JEV）、tokens 与成本（JEV $0.042/1M input 实测
usage；本地 embedding 成本 0）。评分复用 run_s2.verdict_for（逐字一致口径）。
陷阱/人工边界组 miss 的回答原文列进成绩单供人工复核（结论由人工追加）。

用法：
  python3 eval/run_s5.py control   # 系统 python3 即可（无 torch 依赖）
  eval/.venv-emb/bin/python eval/run_s5.py s5b
  python3 eval/run_s5.py s5a       # 只会打印等待连接器的说明并退出
结果写到 eval/results/s2cal-round3-control.* 与 eval/results/s5b-local-bge-m3.*。
"""
import json
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parent.parent
EVAL = Path(__file__).resolve().parent
sys.path.insert(0, str(EVAL))
sys.path.insert(0, str(ROOT))

import run_s2  # noqa: E402  (Index / JevJudge / get_candidates / query_terms / verdict_for / assemble / onboard_site / norm)

ACCEPT = 0.8        # 预注册接受线（与线上 JEV_ACCEPT 一致）
DENSE_TOPK = 8      # 稠密腿截断（预注册）
RRF_K = 60          # RRF 常数（预注册）
PRICE = run_s2.PRICE_PER_M_INPUT
NEW_GROUPS = ["paraphrase2", "zh2", "ja"]
GROUP_LABELS = {"paraphrase2": "B3 英文改写", "zh2": "Z3 中文", "ja": "J3 日文",
                "direct": "A 直问", "paraphrase": "B 改写", "multihop": "C 多跳",
                "near_miss": "D 近似陷阱", "unanswerable": "E 无答案", "handoff": "F 人工边界"}


# ---------------- embedding 后端 ----------------

class LocalBGE:
    """本地 BGE-M3（sentence-transformers）。懒加载，导入失败即如实报错。"""

    name = "local-bge-m3"

    def __init__(self, model_id="BAAI/bge-m3"):
        import torch  # noqa: F401  (只为在缺依赖时尽早报错)
        from sentence_transformers import SentenceTransformer
        t0 = time.perf_counter()
        self.model = SentenceTransformer(model_id)
        self.load_s = time.perf_counter() - t0
        self.model_id = model_id
        import sentence_transformers
        import torch as _t
        self.versions = {"sentence_transformers": sentence_transformers.__version__,
                         "torch": _t.__version__}

    def embed(self, texts):
        """返回 (归一化向量列表, 耗时秒)。逐条调用以便逐题计延迟。"""
        t0 = time.perf_counter()
        vecs = self.model.encode(texts, normalize_embeddings=True,
                                 show_progress_bar=False)
        return [list(map(float, v)) for v in vecs], time.perf_counter() - t0


class HostedOpenAI:
    """托管稠密腿（OpenAI text-embedding-3-small）——本轮只注册不跑。

    后续任务会把这里接到一个 custom connector helper（POST
    https://api.openai.com/v1/embeddings，凭证只走注册连接）。在那之前，
    任何调用都必须明确失败，不许用环境变量/文件/明文 key 等任何方式绕路。
    """

    name = "hosted-openai-text-embedding-3-small"

    def embed(self, texts):
        raise RuntimeError(
            "S5a hosted backend awaiting connector: the OpenAI embedding leg is "
            "registered in prereg-round3.md but not wired up. It runs in a "
            "follow-up task after Dai submits the OpenAI key via secure entry. "
            "Do NOT supply a key any other way.")


# ---------------- 候选池 ----------------

def gold_ids(q, chunks):
    if q["expected_behavior"] != "answer":
        return []
    return [c["id"] for c in chunks
            if any(run_s2.norm(f) in run_s2.norm(c["text"]) for f in q["expected_facts"])]


def cosine(a, b):
    return sum(x * y for x, y in zip(a, b))  # 两边均已 L2 归一化


def rrf_order(bm25_ids, dense_top_ids, pool_ids):
    score, best = {}, {}
    for rank, cid in enumerate(bm25_ids, 1):
        score[cid] = score.get(cid, 0.0) + 1.0 / (RRF_K + rank)
        best[cid] = min(best.get(cid, 10 ** 9), rank)
    for rank, cid in enumerate(dense_top_ids, 1):
        score[cid] = score.get(cid, 0.0) + 1.0 / (RRF_K + rank)
        best[cid] = min(best.get(cid, 10 ** 9), rank)
    return sorted(pool_ids, key=lambda cid: (-score.get(cid, 0.0), best.get(cid, 10 ** 9), cid))


# ---------------- 单题作答 ----------------

def answer_question_arm(index, by_id, chunks, q, judge, backend=None,
                        chunk_vecs=None, query_vec=None, query_emb_s=0.0):
    """返回 row。backend=None 即 control（纯 BM25 池）；否则混合池 + RRF 顺序。"""
    t0 = time.perf_counter()
    cands = run_s2.get_candidates(index, by_id, run_s2.query_terms(q["question"]))
    bm25_s = time.perf_counter() - t0
    bm25_ids = [c["id"] for c, _ in cands]

    dense_top_ids, cosines = [], {}
    if backend is not None:
        scored = sorted(((cosine(query_vec, chunk_vecs[c["id"]]), c["id"]) for c in chunks),
                        key=lambda x: (-x[0], x[1]))
        cosines = {cid: round(s, 4) for s, cid in scored}
        dense_top_ids = [cid for _, cid in scored[:DENSE_TOPK]]
        pool_ids = list(dict.fromkeys(bm25_ids + dense_top_ids))
        order = rrf_order(bm25_ids, dense_top_ids, pool_ids)
    else:
        pool_ids = list(bm25_ids)
        order = list(bm25_ids)
    pool_chunks = [by_id[cid] for cid in order]

    if pool_chunks:
        probs, u_in, u_out, api_s = judge.judge(q["question"], pool_chunks)
        calls = 1
    else:
        probs, u_in, u_out, api_s, calls = {}, 0, 0, 0.0, 0
    selected = [by_id[cid] for cid in order if probs.get(cid, 0.0) >= ACCEPT]
    text, sources = run_s2.assemble(selected)

    gold = gold_ids(q, chunks)
    gold_in = [g for g in gold if g in set(pool_ids)]
    got = "answer" if text else "fallback"
    src_files = [s["url"].rsplit("/", 1)[-1] for s in sources]
    raw_src_files = src_files if got == "answer" else \
        [s["url"].rsplit("/", 1)[-1] for s in sources]
    eff_text = text if got == "answer" else ""
    eff_sources = sources if got == "answer" else []
    eff_src_files = [s["url"].rsplit("/", 1)[-1] for s in eff_sources]
    source_ok = bool(q["expected_sources"]) and any(
        f in eff_src_files for f in q["expected_sources"])
    verdict, found, ratio = run_s2.verdict_for(q, got, eff_text, eff_sources, source_ok)
    service_s = query_emb_s + bm25_s + api_s
    return {**q, "got_behavior": got,
            "score": round(cands[0][1], 3) if cands else 0.0,
            "sources": eff_src_files, "source_ok": source_ok,
            "raw_answer_text": text, "raw_sources": raw_src_files,
            "facts_found": found, "facts_ratio": round(ratio, 2),
            "answer_text": eff_text,
            "latency_ms": round(service_s * 1000, 1), "service_s": round(service_s, 3),
            "verdict": verdict,
            "jev": {"n_candidates": len(pool_ids), "probs": probs,
                    "selected": [c["id"] for c in selected],
                    "noul_max": max(probs.values()) if probs else None,
                    "calls": calls, "input_tokens": u_in, "output_tokens": u_out},
            "pool": {"size": len(pool_ids), "ids": pool_ids,
                     "bm25_ids": bm25_ids, "dense_top_ids": dense_top_ids,
                     "gold_ids": gold, "gold_in_pool": gold_in,
                     "pool_recall": (round(len(gold_in) / len(gold), 3) if gold else None),
                     "any_gold_in_pool": (len(gold_in) > 0 if gold else None),
                     "cosines": cosines},
            "latency_split_ms": {"embedding": round(query_emb_s * 1000, 1),
                                 "bm25": round(bm25_s * 1000, 1),
                                 "jev": round(api_s * 1000, 1)}}


def run_dataset(index, by_id, chunks, questions, judge, backend=None, label=""):
    """跑一个题集。混合臂先逐题（串行）算问题向量并逐题计时，再 4 线程跑 BM25+JEV。"""
    chunk_vecs, query_vecs, query_emb_s = None, {}, {}
    corpus_emb_s = 0.0
    if backend is not None:
        vecs, corpus_emb_s = backend.embed([c["text"] for c in chunks])
        chunk_vecs = {c["id"]: v for c, v in zip(chunks, vecs)}
        for q in questions:
            v, s = backend.embed([q["question"]])
            query_vecs[q["id"]] = v[0]
            query_emb_s[q["id"]] = s
    counter = Counter()

    def work(q):
        row = answer_question_arm(index, by_id, chunks, q, judge, backend,
                                  chunk_vecs, query_vecs.get(q["id"]),
                                  query_emb_s.get(q["id"], 0.0))
        counter["done"] += 1
        print(f"[{label} {counter['done']}/{len(questions)}] {q['id']} -> {row['verdict']}",
              flush=True)
        return row

    with ThreadPoolExecutor(max_workers=4) as ex:
        rows = list(ex.map(work, questions))
    return rows, corpus_emb_s


# ---------------- 成绩单 ----------------

def stats(sub):
    n = len(sub)
    h = sum(r["verdict"] == "hit" for r in sub)
    p = sum(r["verdict"] == "partial" for r in sub)
    return n, h, p, n - h - p


def group_table(lines, title, rows, groups):
    lines.append(f"### {title}\n")
    lines.append("| 范围 | 题数 | hit | partial | miss | 命中率 |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for label, sub in [("合计", rows)] + \
            [(GROUP_LABELS[g], [r for r in rows if r["group"] == g]) for g in groups]:
        if not sub:
            continue
        n, h, p, m = stats(sub)
        lines.append(f"| {label} | {n} | {h} | {p} | {m} | {h / n:.0%} |")
    lines.append("")


def fallback_line(lines, rows):
    fb = [r for r in rows if r["expected_behavior"] != "answer"]
    if fb:
        h = sum(r["verdict"] == "hit" for r in fb)
        lines.append(f"兜底完整性（非答题：陷阱+无答案+动作边界）：{h}/{len(fb)}"
                     f"（{h / len(fb):.0%}）。\n")


def pool_recall_table(lines, rows):
    lines.append("### 候选池召回诊断（金块 = 含 ≥1 期望事实串的块；仅答题计）\n")
    lines.append("| 范围 | 答题数 | 池平均大小 | 任一金块进池 | 池召回率（均值） | 全部金块进池 |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    ans = [r for r in rows if r["expected_behavior"] == "answer"]
    scopes = [("全部答题", ans)] + \
        [(GROUP_LABELS[g], [r for r in ans if r["group"] == g]) for g in
         ["paraphrase2", "zh2", "ja", "direct", "paraphrase", "multihop"] ]
    for label, sub in scopes:
        if not sub:
            continue
        any_rate = sum(1 for r in sub if r["pool"]["any_gold_in_pool"]) / len(sub)
        rec = [r["pool"]["pool_recall"] for r in sub if r["pool"]["pool_recall"] is not None]
        full = sum(1 for r in sub if r["pool"]["pool_recall"] == 1.0) / len(sub)
        avg_pool = sum(r["pool"]["size"] for r in sub) / len(sub)
        lines.append(f"| {label} | {len(sub)} | {avg_pool:.1f} | {any_rate:.0%} | "
                     f"{sum(rec) / len(rec):.2f} | {full:.0%} |")
    lines.append("")


def detail_table(lines, rows):
    lines.append("## 逐题明细\n| ID | 组 | 期望 | 实际 | 最高 noul | 池 | 金块进池 | 来源 | 事实 | 判定 |")
    lines.append("|---|---|---|---|---:|---:|---|---|---|---|")
    for r in rows:
        nm = r["jev"]["noul_max"]
        gold = r["pool"]["gold_ids"]
        gin = f"{len(r['pool']['gold_in_pool'])}/{len(gold)}" if gold else "—"
        lines.append(f"| {r['id']} | {r['group']} | {r['expected_behavior']} | {r['got_behavior']} | "
                     f"{nm if nm is not None else '—'} | {r['pool']['size']} | {gin} | "
                     f"{', '.join(r['sources']) or '—'} | "
                     f"{len(r['facts_found'])}/{len(r['expected_facts'])} | {r['verdict']} |")
    lines.append("")


def review_material(lines, rows, arm_label):
    review = [r for r in rows if r["expected_behavior"] != "answer" and r["verdict"] == "miss"]
    lines.append(f"\n## 人工复核材料 — {arm_label}（陷阱/边界组 miss 的回答原文，判断是无害引用还是编造）\n")
    if not review:
        lines.append("无陷阱/边界组 miss。\n")
    for r in review:
        lines.append(f"- {r['id']}（{r['group']}）问：{r['question']}\n  答：{r['answer_text']}\n")


def load_regression_questions():
    v1 = json.loads((EVAL / "questions.json").read_text(encoding="utf-8"))["questions"]
    v2 = json.loads((EVAL / "questions-v2-additions.json").read_text(encoding="utf-8"))["questions"]
    return [q for q in v1 if q["group"] != "zh_exploratory"] + v2


def p50_ms(rows):
    return round(median([r["service_s"] for r in rows]) * 1000) if rows else 0


def main():
    arm = sys.argv[1] if len(sys.argv) > 1 else ""
    if arm not in ("control", "s5b", "s5a"):
        print(__doc__)
        return
    if arm == "s5a":
        try:
            HostedOpenAI().embed(["probe"])
        except RuntimeError as e:
            print(str(e))
        return

    site = run_s2.onboard_site()
    index = run_s2.Index(run_s2.build_index_file(site["chunks"]))
    by_id = {c["id"]: c for c in site["chunks"]}
    chunks = site["chunks"]
    judge = run_s2.JevJudge()
    new_qs = json.loads((EVAL / "questions-v3-additions.json").read_text(encoding="utf-8"))["questions"]

    if arm == "control":
        rows, _ = run_dataset(index, by_id, chunks, new_qs, judge, None, "control-new")
        total_in = sum(r["jev"]["input_tokens"] for r in rows)
        cost_q = total_in * PRICE / 1e6 / len(rows)
        payload = {"meta": {"date": "2026-11-14", "prereg": "prereg-round3.md",
                            "arm": "S2-cal control (BM25 pool, JEV accept >= 0.8)",
                            "model_alias": run_s2.MODEL, "model_version": judge.model_version,
                            "new_set_calls": sum(r["jev"]["calls"] for r in rows),
                            "new_set_input_tokens": total_in,
                            "new_set_cost_per_question_usd": round(cost_q, 6),
                            "new_set_latency_p50_ms": p50_ms(rows),
                            "jev_call_p50_ms": round(median(judge.call_latency_s) * 1000)
                            if judge.call_latency_s else 0,
                            "jev_retries": judge.retries},
                   "rows_new": rows}
        out = EVAL / "results" / "s2cal-round3-control"
        out.with_suffix(".json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        n, h, p, m = stats(rows)
        lines = [f"# 成绩单 — 第三轮 control：S2-cal（BM25 候选 + JEV 单轮，接受线 noul >= {ACCEPT}）（2026-11-14）\n",
                 f"预注册：`../prereg-round3.md`（先于新题与本轮任何模型调用写定）。语料：Momo Ceramics "
                 f"{len(site['pages'])} 页 / {len(chunks)} 个知识块，与前两轮同一 onboard。control 即现行线上系统，在新题集上新鲜跑。\n",
                 f"JEV：请求别名 {run_s2.MODEL}，实际应答版本 {judge.model_version}；新题集共 "
                 f"{payload['meta']['new_set_calls']} 次调用（重试 {judge.retries} 次），input tokens {total_in}。"
                 f"每题延迟 p50 {p50_ms(rows)} ms、每题 JEV 成本 ${cost_q:.5f}。\n",
                 f"Headline（新题集 50 题）：S2-cal **{h}/{n}（{h / n:.0%}）**。\n"]
        group_table(lines, "S2-cal control — 新题集", rows, NEW_GROUPS)
        fallback_line(lines, rows)
        pool_recall_table(lines, rows)
        detail_table(lines, rows)
        review_material(lines, rows, "S2-cal control")
        out.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"control new: {h}/{n} | p50 {p50_ms(rows)} ms | cost/q ${cost_q:.5f} "
              f"-> eval/results/s2cal-round3-control.md")
        return

    # s5b
    backend = LocalBGE()
    rows_new, corpus_s_new = run_dataset(index, by_id, chunks, new_qs, judge, backend, "s5b-new")
    reg_qs = load_regression_questions()
    rows_reg, corpus_s_reg = run_dataset(index, by_id, chunks, reg_qs, judge, backend, "s5b-reg")
    total_in_new = sum(r["jev"]["input_tokens"] for r in rows_new)
    cost_q_new = total_in_new * PRICE / 1e6 / len(rows_new)
    emb_p50 = round(median([r["latency_split_ms"]["embedding"] for r in rows_new]))
    payload = {"meta": {"date": "2026-11-14", "prereg": "prereg-round3.md",
                        "arm": "S5b (BM25 + local BGE-M3 dense top-8, RRF k=60, JEV accept >= 0.8)",
                        "embedding_model": backend.model_id,
                        "embedding_versions": backend.versions,
                        "embedding_load_s": round(backend.load_s, 2),
                        "corpus_embed_s_new": round(corpus_s_new, 3),
                        "model_alias": run_s2.MODEL, "model_version": judge.model_version,
                        "new_set_calls": sum(r["jev"]["calls"] for r in rows_new),
                        "new_set_input_tokens": total_in_new,
                        "new_set_jev_cost_per_question_usd": round(cost_q_new, 6),
                        "new_set_incremental_cost_per_question_usd": 0.0,
                        "new_set_latency_p50_ms": p50_ms(rows_new),
                        "new_set_embedding_p50_ms": emb_p50,
                        "jev_retries": judge.retries},
               "rows_new": rows_new, "rows_regression": rows_reg}
    out = EVAL / "results" / "s5b-local-bge-m3"
    out.with_suffix(".json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    n, h, p, m = stats(rows_new)
    nr, hr, pr, mr = stats(rows_reg)
    lines = [f"# 成绩单 — 第三轮 S5b：BM25 + 本地 BGE-M3 稠密腿 + JEV@{ACCEPT}（2026-11-14）\n",
             f"预注册：`../prereg-round3.md`。语料：Momo Ceramics {len(site['pages'])} 页 / {len(chunks)} 个知识块。\n",
             f"稠密腿：{backend.model_id}（sentence-transformers {backend.versions['sentence_transformers']}、"
             f"torch {backend.versions['torch']}，CPU），模型加载 {backend.load_s:.1f} s，块向量一次算好"
             f"（{corpus_s_new:.2f} s）；问题向量逐题算，p50 {emb_p50} ms。延迟在本 VM（共享约 1.5 CPU / 6 GB）"
             f"上测，按预注册标注为比专用部署悲观。\n",
             f"JEV：请求别名 {run_s2.MODEL}，实际应答版本 {judge.model_version}；新题集 "
             f"{payload['meta']['new_set_calls']} 次调用（重试 {judge.retries} 次），input tokens {total_in_new}。"
             f"新题集每题延迟 p50 {p50_ms(rows_new)} ms、JEV 成本 ${cost_q_new:.5f}、增量成本 $0（本地 embedding）。\n",
             f"Headline（新题集 50 题）：S5b **{h}/{n}（{h / n:.0%}）**。回归集（100 题）：**{hr}/{nr}**"
             f"（S2-cal 已知 89/100）。\n"]
    group_table(lines, "S5b — 新题集", rows_new, NEW_GROUPS)
    fallback_line(lines, rows_new)
    pool_recall_table(lines, rows_new)
    group_table(lines, "S5b — 回归集（v1 核心 55 + v2 新增 45）", rows_reg,
                ["direct", "paraphrase", "multihop", "near_miss", "unanswerable", "handoff"])
    fallback_line(lines, rows_reg)
    detail_table(lines, rows_new)
    lines.append("\n## 逐题明细 — 回归集\n| ID | 组 | 期望 | 实际 | 最高 noul | 池 | 金块进池 | 来源 | 事实 | 判定 |")
    lines.append("|---|---|---|---|---:|---:|---|---|---|---|")
    for r in rows_reg:
        nm = r["jev"]["noul_max"]
        gold = r["pool"]["gold_ids"]
        gin = f"{len(r['pool']['gold_in_pool'])}/{len(gold)}" if gold else "—"
        lines.append(f"| {r['id']} | {r['group']} | {r['expected_behavior']} | {r['got_behavior']} | "
                     f"{nm if nm is not None else '—'} | {r['pool']['size']} | {gin} | "
                     f"{', '.join(r['sources']) or '—'} | "
                     f"{len(r['facts_found'])}/{len(r['expected_facts'])} | {r['verdict']} |")
    lines.append("")
    review_material(lines, rows_new, "S5b（新题集）")
    review_material(lines, rows_reg, "S5b（回归集）")
    out.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"s5b new: {h}/{n} | regression: {hr}/{nr} | p50 {p50_ms(rows_new)} ms "
          f"| emb p50 {emb_p50} ms -> eval/results/s5b-local-bge-m3.md")


if __name__ == "__main__":
    main()
