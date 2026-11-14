#!/usr/bin/env python3
"""第二轮校准实验 runner：S2-cal（BM25 + JEV 单轮，接受线 noul >= 0.8）。

预注册在 prereg-round2.md（2026-11-14，本文件与新题都写于其后）。本 runner 做三件事：

1. 新题集（questions-v2-additions.json 的 45 题，held-out）：BM25 候选与 run_s1/run_s2
   完全同款，JEV 逐块打 Noul 概率并逐题记录；同一批概率按 0.8（S2-cal，headline）
   与 0.5（S2@0.5 对照）两条线各判一次——对照不产生额外调用。
2. S1 对照：run_s1.py 同款 BM25 + (-1.0) 阈值，在新题集上新鲜跑，无 API。
3. v1 回归集：用第一轮已记录的逐块概率（results/s2-jev-single.json）按 0.8 线
   离线重判，复用数据、不做新调用；重判前先校验 0.5 线能逐字复现第一轮判定，
   校验不过则在成绩单里明示（候选顺序取 probs 字典序 = 第一轮记录的 BM25 顺序）。

评分口径复用 run_s2.verdict_for（与 run_baseline/run_s1 逐字一致）。
用法：python3 eval/run_s2cal.py [输出名，默认 s2cal-round2]
结果写到 eval/results/<输出名>.md / .json；D/F 组 miss 的回答原文列在成绩单里
供人工复核（复核结论由人工追加到成绩单末尾）。
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

import run_s1  # noqa: E402  (build_index / bm25_answer / verdict_for)
import run_s2  # noqa: E402  (Index / JevJudge / get_candidates / query_terms / verdict_for / assemble / onboard_site)

ACCEPT_CAL = 0.8    # 预注册接受线，运行前定死（prereg-round2.md）
ACCEPT_CTRL = 0.5   # 第一轮接受线，同批概率对照重判
PRICE = run_s2.PRICE_PER_M_INPUT
GROUPS = ["direct", "paraphrase", "multihop", "near_miss", "unanswerable", "handoff"]
LABELS = {"direct": "A 直问", "paraphrase": "B 改写", "multihop": "C 多跳",
          "near_miss": "D 近似陷阱", "unanswerable": "E 无答案", "handoff": "F 人工边界"}


def stats(sub):
    n = len(sub)
    h = sum(r["verdict"] == "hit" for r in sub)
    p = sum(r["verdict"] == "partial" for r in sub)
    return n, h, p, n - h - p


def judge_and_score(index, by_id, q, judge):
    """一次 JEV 判定，返回原始概率包 + 两条线各自的 row。"""
    t0 = time.perf_counter()
    cands = run_s2.get_candidates(index, by_id, run_s2.query_terms(q["question"]))
    local_s = time.perf_counter() - t0
    if not cands:
        probs, u_in, u_out, api_s, calls = {}, 0, 0, 0.0, 0
    else:
        probs, u_in, u_out, api_s = judge.judge(q["question"], [c for c, _ in cands])
        calls = 1
    rows = {}
    for line, tag in ((ACCEPT_CAL, "cal"), (ACCEPT_CTRL, "ctrl")):
        selected = [c for c, _ in cands if probs.get(c["id"], 0.0) >= line]
        text, sources = run_s2.assemble(selected)
        res = {"text": text, "sources": sources,
               "best_bm25": round(cands[0][1], 3) if cands else 0.0,
               "noul_max": max(probs.values()) if probs else None,
               "probs": probs, "selected": [c["id"] for c in selected],
               "n_candidates": len(cands), "calls": calls,
               "input_tokens": u_in, "output_tokens": u_out,
               "service_s": local_s + api_s,
               "rounds": [{"round": 1, "candidates": len(cands),
                           "selected": [c["id"] for c in selected]}]}
        rows[tag] = run_s2.build_row(q, res)
    return rows


def s1_row(con, by_id, q):
    t0 = time.perf_counter()
    raw_text, score, raw_sources, _ = run_s1.bm25_answer(con, by_id, q["question"])
    ms = (time.perf_counter() - t0) * 1000
    got = "answer" if (raw_text and score <= run_s1.HEADLINE_THRESHOLD) else "fallback"
    text = raw_text if got == "answer" else ""
    sources = raw_sources if got == "answer" else []
    src_files = [s["url"].rsplit("/", 1)[-1] for s in sources]
    source_ok = bool(q["expected_sources"]) and any(f in src_files for f in q["expected_sources"])
    verdict, found, ratio = run_s1.verdict_for(q, got, text, sources, source_ok)
    return {**q, "got_behavior": got, "score": score, "sources": src_files,
            "source_ok": source_ok, "facts_found": found, "facts_ratio": round(ratio, 2),
            "answer_text": text or "", "latency_ms": round(ms, 1), "verdict": verdict}


def rescore_v1(by_id, line):
    """用第一轮记录的概率离线重判 v1 核心 55 题。返回 (rows, 与第一轮判定不一致的题数@0.5)。"""
    old = json.loads((EVAL / "results" / "s2-jev-single.json").read_text(encoding="utf-8"))
    rows, mismatch = [], 0
    for r in old:
        if r["group"] == "zh_exploratory":
            continue
        probs = r["jev"]["probs"]
        cand_ids = list(probs.keys())  # 记录时的 BM25 候选顺序
        selected = [by_id[cid] for cid in cand_ids if probs[cid] >= line]
        text, sources = run_s2.assemble(selected)
        res = {"text": text, "sources": sources, "best_bm25": r["score"],
               "noul_max": r["jev"]["noul_max"], "probs": probs,
               "selected": [c["id"] for c in selected],
               "n_candidates": r["jev"]["n_candidates"], "calls": 0,
               "input_tokens": 0, "output_tokens": 0,
               "service_s": r["service_s"], "rounds": r["jev"]["rounds"]}
        q = {k: r[k] for k in ("id", "group", "lang", "question", "expected_behavior",
                               "expected_sources", "expected_facts", "note")}
        row = run_s2.build_row(q, res)
        if line == ACCEPT_CTRL and row["verdict"] != r["verdict"]:
            mismatch += 1
        rows.append(row)
    return rows, mismatch


def group_table(lines, title, rows):
    lines.append(f"### {title}\n")
    lines.append("| 范围 | 题数 | hit | partial | miss | 命中率 |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for label, sub in [("新题集 A2–F2", rows)] + [(LABELS[g], [r for r in rows if r["group"] == g]) for g in GROUPS]:
        n, h, p, m = stats(sub)
        lines.append(f"| {label} | {n} | {h} | {p} | {m} | {h / n:.0%} |")
    fb = [r for r in rows if r["group"] in ("near_miss", "unanswerable")]
    lines.append(f"\n兜底组（D+E）正确率：{sum(r['verdict'] == 'hit' for r in fb)}/{len(fb)}"
                 f"（{sum(r['verdict'] == 'hit' for r in fb) / len(fb):.0%}）。"
                 f"人工边界组（F）：{sum(r['verdict'] == 'hit' for r in rows if r['group'] == 'handoff')}/5。\n")


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "s2cal-round2"
    site = run_s2.onboard_site()
    index = run_s2.Index(run_s2.build_index_file(site["chunks"]))
    by_id = {c["id"]: c for c in site["chunks"]}
    s1_con = run_s1.build_index(site["chunks"])
    judge = run_s2.JevJudge()

    new_qs = json.loads((EVAL / "questions-v2-additions.json").read_text(encoding="utf-8"))["questions"]
    counter = Counter()

    def work(q):
        rows = judge_and_score(index, by_id, q, judge)
        counter["done"] += 1
        print(f"[{counter['done']}/{len(new_qs)}] {q['id']} cal="
              f"{rows['cal']['verdict']} ctrl={rows['ctrl']['verdict']}", flush=True)
        return q, rows

    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(work, new_qs))
    cal_rows = [r["cal"] for _, r in results]
    ctrl_rows = [r["ctrl"] for _, r in results]
    s1_rows = [s1_row(s1_con, by_id, q) for q in new_qs]

    v1_cal, _ = rescore_v1(by_id, ACCEPT_CAL)
    v1_ctrl, mismatch = rescore_v1(by_id, ACCEPT_CTRL)

    total_in = sum(r["jev"]["input_tokens"] for r in cal_rows)
    cost_per_q = total_in * PRICE / 1e6 / len(cal_rows)
    p50_ms = round(median([r["service_s"] for r in cal_rows]) * 1000)
    call_p50 = round(median(judge.call_latency_s) * 1000) if judge.call_latency_s else 0

    payload = {
        "meta": {"date": "2026-11-14", "prereg": "prereg-round2.md",
                 "accept_cal": ACCEPT_CAL, "accept_ctrl": ACCEPT_CTRL,
                 "model_alias": run_s2.MODEL, "model_version": judge.model_version,
                 "new_set_calls": sum(r["jev"]["calls"] for r in cal_rows),
                 "new_set_input_tokens": total_in,
                 "new_set_cost_per_question_usd": round(cost_per_q, 6),
                 "new_set_latency_p50_ms": p50_ms,
                 "jev_call_p50_ms": call_p50, "jev_retries": judge.retries,
                 "v1_rescore_0.5_verdict_mismatches": mismatch},
        "s2cal_0.8_new": cal_rows, "s2_0.5_new_control": ctrl_rows,
        "s1_new_control": s1_rows,
        "v1_regression_0.8": v1_cal, "v1_regression_0.5_check": v1_ctrl,
    }
    out_dir = EVAL / "results"
    out_dir.mkdir(exist_ok=True)
    (out_dir / f"{name}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    n_cal, h_cal, _, _ = stats(cal_rows)
    n_ctr, h_ctr, _, _ = stats(ctrl_rows)
    n_s1, h_s1, _, _ = stats(s1_rows)
    n_v1, h_v1, _, _ = stats(v1_cal)
    lines = [f"# 成绩单 — 第二轮校准 S2-cal（BM25 + JEV 单轮，接受线 noul >= {ACCEPT_CAL}）（2026-11-14）\n",
             f"预注册：`../prereg-round2.md`（先于新题与本轮任何 JEV 调用写定）。语料：Momo Ceramics "
             f"{len(site['pages'])} 页 / {len(site['chunks'])} 个知识块，与第一轮同一 onboard。\n",
             f"JEV：请求别名 {run_s2.MODEL}，实际应答版本 {judge.model_version}；新题集共 "
             f"{payload['meta']['new_set_calls']} 次调用（重试 {judge.retries} 次），input tokens "
             f"{total_in}，单次调用 p50 {call_p50} ms。\n",
             f"Headline 对比（新题集 45 题）：S2-cal@0.8 **{h_cal}/{n_cal}（{h_cal / n_cal:.0%}）**；"
             f"S2@0.5 对照 {h_ctr}/{n_ctr}（{h_ctr / n_ctr:.0%}）；S1 对照 {h_s1}/{n_s1}（{h_s1 / n_s1:.0%}）。"
             f"每题延迟 p50 {p50_ms} ms、每题成本 ${cost_per_q:.5f}。\n"]
    group_table(lines, "S2-cal（noul >= 0.8）— 新题集", cal_rows)
    group_table(lines, "S2@0.5 对照（同一批概率重判）— 新题集", ctrl_rows)
    group_table(lines, "S1 BM25 对照（阈值 -1.0，新鲜跑）— 新题集", s1_rows)
    lines.append(f"### v1 回归集（复用第一轮记录概率离线重判，不合并进 headline）\n")
    lines.append(f"0.8 线：总命中 {h_v1}/{n_v1}（第一轮 0.5 线实测 46/55）。"
                 f"重判前校验：0.5 线重判与第一轮逐题判定不一致 {mismatch} 题"
                 f"（应为 0；不为 0 说明候选顺序重建有偏差，回归数字需谨慎）。\n")
    v1_fb = [r for r in v1_cal if r["group"] in ("near_miss", "unanswerable")]
    lines.append(f"v1 回归 D+E @0.8：{sum(r['verdict'] == 'hit' for r in v1_fb)}/{len(v1_fb)}。\n")

    lines.append("## 逐题明细 — S2-cal@0.8（新题集）\n| ID | 组 | 期望 | 实际 | 最高 noul | 来源 | 事实 | 判定 |")
    lines.append("|---|---|---|---|---:|---|---|---|")
    for r in cal_rows:
        nm = r["jev"]["noul_max"]
        lines.append(f"| {r['id']} | {r['group']} | {r['expected_behavior']} | {r['got_behavior']} | "
                     f"{nm if nm is not None else '—'} | {', '.join(r['sources']) or '—'} | "
                     f"{len(r['facts_found'])}/{len(r['expected_facts'])} | {r['verdict']} |")

    lines.append("\n## 人工复核材料（D/F 组 miss 的回答原文，判断是无害引用还是编造）\n")
    review = [r for r in cal_rows if r["group"] in ("near_miss", "handoff") and r["verdict"] == "miss"]
    review += [r for r in ctrl_rows if r["group"] in ("near_miss", "handoff") and r["verdict"] == "miss"
               and r["id"] not in {x["id"] for x in review}]
    if not review:
        lines.append("S2-cal@0.8 与 S2@0.5 对照均无 D/F 组 miss。\n")
    seen = set()
    for r in cal_rows + ctrl_rows:
        if r["group"] in ("near_miss", "handoff") and r["verdict"] == "miss" and r["id"] not in seen:
            seen.add(r["id"])
            tag = "0.8" if r in cal_rows else "0.5对照"
            lines.append(f"- {r['id']}（{r['group']}，{tag} 线 miss）问：{r['question']}\n  答：{r['answer_text']}\n")
    (out_dir / f"{name}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"NEW cal@0.8: {h_cal}/{n_cal} | ctrl@0.5: {h_ctr}/{n_ctr} | S1: {h_s1}/{n_s1} | "
          f"v1 regression@0.8: {h_v1}/{n_v1} (0.5-check mismatches: {mismatch}) | "
          f"p50 {p50_ms} ms | cost/q ${cost_per_q:.5f} -> eval/results/{name}.md")


if __name__ == "__main__":
    main()
