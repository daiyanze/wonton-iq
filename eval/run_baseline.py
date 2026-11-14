#!/usr/bin/env python3
"""跑题库基线：用现版 app.py（S0 / TF-IDF）答 eval/questions.json 全部题并自动评分。

用法：python3 eval/run_baseline.py [输出名，默认 baseline-s0]
评分口径见 eval/README.md：hit / partial / miss 三档，自动评分后 D/F 组需人工复核。
"""
import json
import sys
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import app  # noqa: E402

# 把基线运行的数据写到临时目录，不污染 app 的真实 data/
import tempfile  # noqa: E402

_tmp = Path(tempfile.mkdtemp(prefix="eval-baseline-"))
app.SITES_FILE = str(_tmp / "sites.json")
app.EVENTS_FILE = str(_tmp / "events.json")


def norm(s):
    return " ".join((s or "").lower().split())


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "baseline-s0"
    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT / "sample_store"))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        site = app.onboard(f"http://127.0.0.1:{port}/index.html")
    finally:
        server.shutdown()

    data = json.loads((ROOT / "eval" / "questions.json").read_text(encoding="utf-8"))
    rows = []
    for q in data["questions"]:
        t0 = time.perf_counter()
        text, score, sources = app.answer_question(site, q["question"])
        ms = (time.perf_counter() - t0) * 1000
        got_behavior = "answer" if text else "fallback"
        src_files = [s["url"].rsplit("/", 1)[-1] for s in sources]
        source_ok = bool(q["expected_sources"]) and any(
            f in src_files for f in q["expected_sources"])
        if q["expected_behavior"] == "answer":
            facts = q["expected_facts"]
            found = [f for f in facts if norm(f) in norm(text)]
            ratio = len(found) / len(facts) if facts else 1.0
            if got_behavior == "answer" and source_ok and ratio >= 0.5:
                verdict = "hit"
            elif got_behavior == "answer" and (source_ok or ratio > 0):
                verdict = "partial"
            else:
                verdict = "miss"
        elif q["expected_behavior"] == "fallback":
            facts, found, ratio = [], [], 0.0
            verdict = "hit" if got_behavior == "fallback" else "miss"
        else:  # handoff: 现版没有独立转人工判定，兜底（引导留邮箱转人工）记为正确行为
            facts, found, ratio = [], [], 0.0
            verdict = "hit" if got_behavior == "fallback" else "miss"
        rows.append({**q, "got_behavior": got_behavior, "score": score,
                     "sources": src_files, "source_ok": source_ok,
                     "facts_found": found, "facts_ratio": round(ratio, 2),
                     "answer_text": text or "", "latency_ms": round(ms, 1),
                     "verdict": verdict})

    out_dir = ROOT / "eval" / "results"
    out_dir.mkdir(exist_ok=True)
    (out_dir / f"{name}.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

    def stats(sub):
        n = len(sub)
        h = sum(r["verdict"] == "hit" for r in sub)
        p = sum(r["verdict"] == "partial" for r in sub)
        return n, h, p, n - h - p

    core = [r for r in rows if r["group"] != "zh_exploratory"]
    zh = [r for r in rows if r["group"] == "zh_exploratory"]
    lines = [f"# 成绩单 — S0 现版 TF-IDF 基线（2026-11-14）\n",
             f"语料：Momo Ceramics {len(site['pages'])} 页 / {len(site['chunks'])} 个知识块。自动评分，口径见 `../README.md`。\n",
             "| 范围 | 题数 | hit | partial | miss | 命中率 |", "|---|---:|---:|---:|---:|---:|"]
    for label, sub in [("英文核心集 A–F", core)] + \
            [(g, [r for r in core if r["group"] == g]) for g in
             ["direct", "paraphrase", "multihop", "near_miss", "unanswerable", "handoff"]] + \
            [("中文探索组 G（单独计分）", zh)]:
        n, h, p, m = stats(sub)
        lines.append(f"| {label} | {n} | {h} | {p} | {m} | {h / n:.0%} |")
    fb = [r for r in core if r["expected_behavior"] == "fallback"]
    lines.append(f"\n兜底组（D+E）正确率：{sum(r['verdict'] == 'hit' for r in fb)}/{len(fb)}。"
                 f"延迟：每题平均 {sum(r['latency_ms'] for r in rows) / len(rows):.1f} ms（本地 TF-IDF，无模型调用，成本 0）。\n")
    lines.append("## 逐题明细\n| ID | 组 | 期望 | 实际 | 分数 | 来源 | 事实 | 判定 |")
    lines.append("|---|---|---|---|---:|---|---|---|")
    for r in rows:
        lines.append(f"| {r['id']} | {r['group']} | {r['expected_behavior']} | {r['got_behavior']} | "
                     f"{r['score']} | {', '.join(r['sources']) or '—'} | "
                     f"{len(r['facts_found'])}/{len(r['expected_facts'])} | {r['verdict']} |")
    (out_dir / f"{name}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    n, h, p, m = stats(core)
    print(f"core {n}题: hit {h} partial {p} miss {m} ({h / n:.0%}) | zh {stats(zh)} | 明细 -> eval/results/{name}.md")


if __name__ == "__main__":
    main()
