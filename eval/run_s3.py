#!/usr/bin/env python3
"""跑 S3：完整 SAG2 = BM25 + JEV + 第二轮关键词扩展。同一套题、同一套评分。

与 S2 只变一个变量：多一轮检索。第一轮与 run_s2.answer_s2 完全相同（同一候选
池、同一 Noul 提问、同一 0.5 判定线）。第一轮选中的块给出扩展词（对选中块用
app.tokenize 分词、去掉原查询已有的词、按词频取前 12 个），原查询词 + 扩展词
组成第二轮 BM25 查询；第二轮命中的、尚未选中的块（包括第一轮被 JEV 否掉的
块）带着“已找到的事实”作共享上下文再判一次（问的是“还缺不缺这一块”），
仍是 noul >= 0.5 选中。第一轮一块都没选中时没有扩展来源，直接兜底。

这对应 SAG2（arXiv:2610.22588）的两轮流程：BM25 给候选，决策模型在“问题 +
已选证据”的上下文里逐块判断该块是否补上答案链缺失的一环，选中块的词再驱动
下一轮检索。其余口径（延迟、成本、评分、成绩单结构）与 run_s2.py 完全一致。

用法：python3 eval/run_s3.py [输出名，默认 s3-sag2]
"""
import json
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_s2 as s2  # noqa: E402  复用候选/JEV/评分/成绩单，保证只变一个变量

ACCEPT = s2.ACCEPT
MAX_EXPANSION_TERMS = 12  # 运行前定死


def expansion_terms(selected_chunks, base_terms):
    cnt = Counter()
    for c in selected_chunks:
        cnt.update(s2.app.tokenize(c["text"]))
    base = set(base_terms)
    out = []
    for t, _ in cnt.most_common():
        if t not in base:
            out.append(t)
        if len(out) >= MAX_EXPANSION_TERMS:
            break
    return out


def answer_s3(index, by_id, qtext, judge):
    t0 = time.perf_counter()
    terms = s2.query_terms(qtext)
    cands = s2.get_candidates(index, by_id, terms)
    local_s = time.perf_counter() - t0
    if not cands:
        return {"text": "", "sources": [], "best_bm25": 0.0, "noul_max": None,
                "probs": {}, "selected": [], "n_candidates": 0,
                "calls": 0, "input_tokens": 0, "output_tokens": 0,
                "service_s": local_s, "rounds": [], "expansion_terms": []}
    probs, u_in, u_out, api_s = judge.judge(qtext, [c for c, _ in cands])
    selected = [c for c, _ in cands if probs[c["id"]] >= ACCEPT]
    calls, service_s = 1, local_s + api_s
    rounds = [{"round": 1, "candidates": len(cands),
               "selected": [c["id"] for c in selected]}]
    exp_terms = []
    if selected:
        exp_terms = expansion_terms(selected, terms)
        cands2 = s2.get_candidates(index, by_id, terms + exp_terms)
        sel_ids = {c["id"] for c in selected}
        pool2 = [c for c, _ in cands2 if c["id"] not in sel_ids]
        if pool2:
            probs2, u2_in, u2_out, api2_s = judge.judge(
                qtext, pool2, context_chunks=selected)
            probs = {**probs, **probs2}
            selected2 = [c for c in pool2 if probs2[c["id"]] >= ACCEPT]
            selected = selected + selected2
            calls += 1
            u_in += u2_in
            u_out += u2_out
            service_s += api2_s
            rounds.append({"round": 2, "candidates": len(pool2),
                           "selected": [c["id"] for c in selected2],
                           "expansion_terms": exp_terms})
    text, sources = s2.assemble(selected)
    return {"text": text, "sources": sources,
            "best_bm25": round(cands[0][1], 3),
            "noul_max": max(probs.values()) if probs else None,
            "probs": probs, "selected": [c["id"] for c in selected],
            "n_candidates": len(cands),
            "calls": calls, "input_tokens": u_in, "output_tokens": u_out,
            "service_s": service_s, "rounds": rounds,
            "expansion_terms": exp_terms}


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "s3-sag2"
    site = s2.onboard_site()
    index = s2.Index(s2.build_index_file(site["chunks"]))
    by_id = {c["id"]: c for c in site["chunks"]}
    judge = s2.JevJudge()
    data = json.loads((s2.ROOT / "eval" / "questions.json").read_text(encoding="utf-8"))
    counter = Counter()

    def answer_fn(q):
        res = answer_s3(index, by_id, q["question"], judge)
        counter["done"] += 1
        print(f"[{counter['done']}/60] {q['id']} -> "
              f"{'answer' if res['text'] else 'fallback'}", flush=True)
        return s2.build_row(q, res)

    with ThreadPoolExecutor(max_workers=4) as ex:
        rows = list(ex.map(answer_fn, data["questions"]))
    method = [
        f"判定方式：第一轮同 S2（BM25 全部命中块逐块 JEV 打 Noul，>= {ACCEPT} 选中）；"
        f"第二轮用选中块的高频词（前 {MAX_EXPANSION_TERMS} 个）扩查询，未选中块带已选证据上下文再判，"
        f"同一判定线。两轮设计运行前定死（见 `run_s3.py`）。\n",
        f"JEV 模型：请求别名 {s2.MODEL}，实际应答版本 {judge.model_version}。\n",
    ]
    core, zh = s2.write_report(name, "S3 完整 SAG2（BM25 + JEV + 两轮扩展）",
                               method, rows, site, judge)
    n, h, p, m = s2.stats(core)
    print(f"S3 core {n}题: hit {h} partial {p} miss {m} ({h / n:.0%}) | zh {s2.stats(zh)} | 明细 -> eval/results/{name}.md")


if __name__ == "__main__":
    main()
