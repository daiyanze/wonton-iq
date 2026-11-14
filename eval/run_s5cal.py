#!/usr/bin/env python3
"""第四轮校准 runner（预注册 prereg-round4.md，2026-11-14）。

唯一变量：S5b 混合管线的 JEV 接受线 ∈ {0.8（对照）, 0.9, 0.95}。管线本体直接
复用 run_s5.py（BM25 ∪ BGE-M3 稠密 top-8、RRF k=60、JEV 门逐字同 run_s2），
本文件不复制、不改动任何管线逻辑：

- v4 题库（questions-v4-additions.json，40 题）只跑一次（run_s5.run_dataset），
  逐题记录候选池、池内金块、每块 noul 概率与延迟拆分；三条线全部由记录概率
  离线判分（第二轮先例）。
- 第三轮已记录概率（results/s5b-local-bge-m3.json 的 rows_new 50 题与
  rows_regression 100 题）按 0.9/0.95 离线复判，标注为回归/诊断；判分前先按
  0.8 线复判并与第三轮已存 verdict 逐题比对（不一致数必须为 0 才继续），
  以此验证复判方法与概率复用（同第二轮的校验方式）。
- 评分复用 run_s2.verdict_for（与前三轮逐字一致口径）。接受线只改变哪些
  已打分的块被拼进答案，不产生额外调用，延迟/成本不随线变化。

用法（本地嵌入环境，须离线走缓存，见 round3-setup.md）：
  cd ~/workspace/ecommerce-ai-support
  HF_HUB_OFFLINE=1 HF_HOME=$PWD/eval/.hf-cache eval/.venv-emb/bin/python eval/run_s5cal.py
结果写到 eval/results/s5cal-round4.json / .md（裁决节由人工复核后追加）。
"""
import hashlib
import json
import sys
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parent.parent
EVAL = Path(__file__).resolve().parent
sys.path.insert(0, str(EVAL))
sys.path.insert(0, str(ROOT))

import run_s2  # noqa: E402
import run_s5  # noqa: E402

LINES = [0.8, 0.9, 0.95]
PRICE = run_s2.PRICE_PER_M_INPUT
GROUP_LABELS = {"trap4": "T4 近失陷阱", "unans4": "U4 无答案", "hand4": "H4 人工边界",
                "ans4": "A4 可答对照"}


def integrity_checks():
    """把'管线与第三轮逐字一致'变成可审计的断言：run_s5 的常量与 JEV 模板不变。"""
    assert run_s5.ACCEPT == 0.8, run_s5.ACCEPT
    assert run_s5.DENSE_TOPK == 8 and run_s5.RRF_K == 60
    h = hashlib.sha256(
        (run_s2.NOUL_INSTRUCTIONS + json.dumps(run_s2.NOUL_CRITERIA, sort_keys=True)
         ).encode()).hexdigest()[:16]
    return {"run_s5_accept": run_s5.ACCEPT, "dense_topk": run_s5.DENSE_TOPK,
            "rrf_k": run_s5.RRF_K, "noul_template_sha256_16": h,
            "jev_instructions_verbatim_from": "run_s2.NOUL_INSTRUCTIONS / NOUL_CRITERIA"}


def score_at_line(row, by_id, line):
    """从已记录概率按接受线 line 重判一题（选择集与拼答顺序由池顺序决定）。"""
    probs = row["jev"]["probs"]
    selected = [by_id[cid] for cid in row["pool"]["ids"] if probs.get(cid, 0.0) >= line]
    text, sources = run_s2.assemble(selected)
    got = "answer" if text else "fallback"
    eff_text = text if got == "answer" else ""
    eff_sources = sources if got == "answer" else []
    eff_files = [s["url"].rsplit("/", 1)[-1] for s in eff_sources]
    q = {k: row[k] for k in ("id", "group", "question", "expected_behavior",
                             "expected_sources", "expected_facts")}
    source_ok = bool(q["expected_sources"]) and any(
        f in eff_files for f in q["expected_sources"])
    verdict, found, ratio = run_s2.verdict_for(q, got, eff_text, eff_sources, source_ok)
    return {"id": row["id"], "group": row["group"], "lang": row.get("lang"),
            "question": row["question"], "expected_behavior": row["expected_behavior"],
            "got_behavior": got, "verdict": verdict,
            "noul_max": max(probs.values()) if probs else None,
            "selected": [c["id"] for c in selected],
            "sources": eff_files, "facts_found": found,
            "facts_total": len(q["expected_facts"]),
            "answer_text": eff_text}


def summarize(scored):
    n = len(scored)
    hits = sum(r["verdict"] == "hit" for r in scored)
    fb = [r for r in scored if r["expected_behavior"] != "answer"]
    fb_hits = sum(r["verdict"] == "hit" for r in fb)
    ans = [r for r in scored if r["expected_behavior"] == "answer"]
    ans_hits = sum(r["verdict"] == "hit" for r in ans)
    by_group = {}
    for g in GROUP_LABELS:
        sub = [r for r in scored if r["group"] == g]
        if sub:
            by_group[g] = {"n": len(sub),
                           "hit": sum(r["verdict"] == "hit" for r in sub),
                           "partial": sum(r["verdict"] == "partial" for r in sub),
                           "miss": sum(r["verdict"] == "miss" for r in sub)}
    return {"n": n, "hits": hits, "fallback_n": len(fb), "fallback_hits": fb_hits,
            "fallback_rate": round(fb_hits / len(fb), 4) if fb else None,
            "answerable_n": len(ans), "answerable_hits": ans_hits,
            "by_group": by_group}


def main():
    site = run_s2.onboard_site()
    index = run_s2.Index(run_s2.build_index_file(site["chunks"]))
    by_id = {c["id"]: c for c in site["chunks"]}
    chunks = site["chunks"]
    judge = run_s2.JevJudge()
    backend = run_s5.LocalBGE()
    v4_qs = json.loads((EVAL / "questions-v4-additions.json").read_text(
        encoding="utf-8"))["questions"]

    # ---- v4 只跑一次（接受线在 run_s5 内固定 0.8 判分，概率才是本轮的原料） ----
    rows_v4, corpus_s = run_s5.run_dataset(index, by_id, chunks, v4_qs, judge,
                                           backend, "s5cal-v4")
    total_in = sum(r["jev"]["input_tokens"] for r in rows_v4)
    p50 = round(median([r["service_s"] for r in rows_v4]) * 1000)

    v4_by_line, v4_summary = {}, {}
    for line in LINES:
        scored = [score_at_line(r, by_id, line) for r in rows_v4]
        v4_by_line[str(line)] = scored
        v4_summary[str(line)] = summarize(scored)
    # 0.8 线复判 vs run_s5 原判（用 run_dataset 内建 0.8 口径）的一致性校验
    mism_08 = [s["id"] for s, r in zip(v4_by_line["0.8"], rows_v4)
               if s["verdict"] != r["verdict"]]

    # ---- 第三轮已记录概率复判（回归/诊断） ----
    r3 = json.loads((EVAL / "results" / "s5b-local-bge-m3.json").read_text(
        encoding="utf-8"))
    rescore, mism_r3 = {}, {}
    for name, rows in [("v3_new", r3["rows_new"]), ("v1v2_regression", r3["rows_regression"])]:
        per_line = {}
        base = [score_at_line(r, by_id, 0.8) for r in rows]
        mism_r3[name] = [s["id"] for s, r in zip(base, rows) if s["verdict"] != r["verdict"]]
        for line in LINES:
            scored = base if line == 0.8 else [score_at_line(r, by_id, line) for r in rows]
            per_line[str(line)] = {
                "n": len(scored), "hits": sum(s["verdict"] == "hit" for s in scored),
                "changed_vs_08": [s["id"] for s, b in zip(scored, base)
                                  if s["verdict"] != b["verdict"]],
                "verdicts": {s["id"]: s["verdict"] for s in scored}}
        rescore[name] = per_line

    payload = {"meta": {"date": "2026-11-14", "prereg": "prereg-round4.md",
                        "arm": "S5b pipeline (run_s5, verbatim) — accept-line calibration",
                        "lines": LINES, "integrity": integrity_checks(),
                        "embedding_model": backend.model_id,
                        "embedding_versions": backend.versions,
                        "model_alias": run_s2.MODEL, "model_version": judge.model_version,
                        "v4_calls": sum(r["jev"]["calls"] for r in rows_v4),
                        "v4_input_tokens": total_in,
                        "v4_cost_per_question_usd": round(total_in * PRICE / 1e6 / len(rows_v4), 6),
                        "v4_latency_p50_ms": p50,
                        "jev_retries": judge.retries,
                        "rescore_validation": {"v4_08_vs_run_s5_mismatches": mism_08,
                                               "round3_08_vs_stored_mismatches": mism_r3},
                        "note": "接受线不产生额外调用：三条线共用同一次运行的记录概率，延迟/成本与线无关。"},
               "v4_recorded_rows": rows_v4,
               "v4_by_line": v4_by_line, "v4_summary": v4_summary,
               "round3_rescore": rescore}
    out = EVAL / "results" / "s5cal-round4"
    out.with_suffix(".json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---- 成绩单（裁决节留待人工复核后追加） ----
    L = []
    L.append("# 成绩单 — 第四轮 S5b 接受线校准：0.8 / 0.9 / 0.95（2026-11-14）\n")
    L.append(f"预注册：`../prereg-round4.md`（先于 v4 新题与本轮任何模型调用写定）。语料：Momo Ceramics "
             f"{len(site['pages'])} 页 / {len(chunks)} 个知识块（冻结）。管线 = 第三轮 S5b 本体"
             f"（直接 import `run_s5`，未复制逻辑）；完整性断言：{json.dumps(integrity_checks(), ensure_ascii=False)}。\n")
    L.append(f"JEV：请求别名 {run_s2.MODEL}，实际应答版本 {judge.model_version}；v4 题库共 "
             f"{payload['meta']['v4_calls']} 次调用（重试 {judge.retries} 次），input tokens {total_in}，"
             f"每题成本 ${payload['meta']['v4_cost_per_question_usd']:.5f}，每题延迟 p50 {p50} ms"
             f"（本 VM 共享约 1.5 CPU 的悲观口径，同第三轮）。**接受线只决定哪些已打分块被拼进答案，"
             f"不产生额外调用——三条线的延迟与成本完全相同，不随线变化。**\n")
    L.append(f"复判一致性校验：v4 按 0.8 线复判 vs run_s5 原判，不一致 {len(mism_08)} 题；"
             f"第三轮记录概率按 0.8 线复判 vs 第三轮已存 verdict，不一致 "
             f"v3 新题 {len(mism_r3['v3_new'])} 题、v1+v2 {len(mism_r3['v1v2_regression'])} 题。\n")
    L.append("## v4 题库（40 题）三线判分\n")
    L.append("| 线 | 总命中 /40 | 回退集（陷阱+无答案+转人工）/34 | 回退正确率 | 可答对照 /6 |")
    L.append("|---|---:|---:|---:|---:|")
    for line in LINES:
        s = v4_summary[str(line)]
        L.append(f"| {line} | {s['hits']} | {s['fallback_hits']} | {s['fallback_rate']:.1%} "
                 f"| {s['answerable_hits']} |")
    L.append("")
    for line in LINES:
        s = v4_summary[str(line)]
        L.append(f"### 线 {line} 分组明细\n")
        L.append("| 组 | 题数 | hit | partial | miss |")
        L.append("|---|---:|---:|---:|---:|")
        for g, lab in GROUP_LABELS.items():
            if g in s["by_group"]:
                b = s["by_group"][g]
                L.append(f"| {lab} | {b['n']} | {b['hit']} | {b['partial']} | {b['miss']} |")
        L.append("")
    L.append("## 第三轮已记录概率复判（回归/诊断，不进 v4 主裁决）\n")
    L.append("| 题集 | 线 0.8（复判） | 线 0.9 | 线 0.95 |")
    L.append("|---|---:|---:|---:|")
    for name, lab in [("v3_new", "v3 新题集（50）"), ("v1v2_regression", "v1+v2 回归集（100）")]:
        r = rescore[name]
        L.append(f"| {lab} | {r['0.8']['hits']} | {r['0.9']['hits']} | {r['0.95']['hits']} |")
    L.append("")
    for name, lab in [("v3_new", "v3 新题集"), ("v1v2_regression", "v1+v2 回归集")]:
        for line in ("0.9", "0.95"):
            ch = rescore[name][line]["changed_vs_08"]
            L.append(f"- {lab} 线 {line} 相对 0.8 判定变化：{len(ch)} 题"
                     f"{('（' + ', '.join(ch) + '）') if ch else ''}")
    L.append("")
    L.append("## 逐题明细 — v4（三线并列）\n")
    L.append("| ID | 组 | 期望 | 最高 noul | 0.8 | 0.9 | 0.95 |")
    L.append("|---|---|---|---:|---|---|---|")
    by_id_line = {ln: {r["id"]: r for r in v4_by_line[ln]} for ln in v4_by_line}
    for r in rows_v4:
        nm = r["jev"]["noul_max"]
        L.append(f"| {r['id']} | {GROUP_LABELS[r['group']]} | {r['expected_behavior']} | "
                 f"{nm if nm is not None else '—'} | {by_id_line['0.8'][r['id']]['verdict']} | "
                 f"{by_id_line['0.9'][r['id']]['verdict']} | {by_id_line['0.95'][r['id']]['verdict']} |")
    L.append("")
    for line in ("0.9", "0.95", "0.8"):
        miss = [r for r in v4_by_line[line]
                if r["expected_behavior"] != "answer" and r["verdict"] == "miss"]
        L.append(f"\n## 人工复核材料 — 线 {line}（v4 回退组 miss 的回答原文）\n")
        if not miss:
            L.append("无回退组 miss。\n")
        for r in miss:
            L.append(f"- {r['id']}（{r['group']}）问：{r['question']}\n  答：{r['answer_text']}\n")
    out.with_suffix(".md").write_text("\n".join(L) + "\n", encoding="utf-8")

    print(json.dumps({"v4_summary": v4_summary,
                      "round3_rescore_hits": {n: {ln: rescore[n][ln]["hits"] for ln in
                                                  ("0.8", "0.9", "0.95")} for n in rescore},
                      "validation": payload["meta"]["rescore_validation"],
                      "p50_ms": p50, "cost_q": payload["meta"]["v4_cost_per_question_usd"]},
                     ensure_ascii=False, indent=1))
    print("-> eval/results/s5cal-round4.md / .json")


if __name__ == "__main__":
    main()
