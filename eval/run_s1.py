#!/usr/bin/env python3
"""跑 S1：SQLite FTS5 BM25 检索，对照 eval/questions.json 同一套题、同一套评分。

与 S0 只变一个变量：检索打分由 TF-IDF 余弦相似度换成 FTS5 BM25。
其余不变：同一 onboard 抓取与切块（app.onboard）、同一分词与同义词扩展
（app.tokenize / app.expand）、单轮、无扩展、无决策模型；兜底仍是阈值判定。

阈值（运行前定死，不看题库成绩调参）：
FTS5 bm25() 返回负数，越负越相关。在 10 个知识块的语料上，一个有区分度的
词命中大约贡献 -1 到 -3 分，只命中高频泛词时接近 0。因此 headline 阈值定为
best_bm25 <= -1.0（约等于“至少一次有意义的词命中”），低于此值判答不出。
为检验“S0 的结论（调阈值救不了兜底）对 BM25 是否同样成立”，结果文件另附
-0.5 / -1.0 / -2.0 三档阈值的敏感性表（诊断用，不改 headline 判定）。

用法：python3 eval/run_s1.py [输出名，默认 s1-bm25]
"""
import json
import sqlite3
import sys
import tempfile
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import app  # noqa: E402

_tmp = Path(tempfile.mkdtemp(prefix="eval-s1-"))
app.SITES_FILE = str(_tmp / "sites.json")
app.EVENTS_FILE = str(_tmp / "events.json")

HEADLINE_THRESHOLD = -1.0  # bm25 <= -1.0 才作答；运行前定死
SENSITIVITY = [-0.5, -1.0, -2.0]


def norm(s):
    return " ".join((s or "").lower().split())


def build_index(chunks):
    con = sqlite3.connect(":memory:")
    con.execute("CREATE VIRTUAL TABLE chunks USING fts5(id UNINDEXED, url UNINDEXED, text, tokenize='unicode61')")
    for c in chunks:
        con.execute("INSERT INTO chunks (id, url, text) VALUES (?, ?, ?)",
                    (c["id"], c["url"], c["text"]))
    con.commit()
    return con


def bm25_answer(con, chunks_by_id, question):
    """返回 (text, bm25分数, sources)。分数越负越好；无命中词返回 (None, 0.0, [])。"""
    tokens = app.expand(app.tokenize(question))
    if not tokens:
        return None, 0.0, [], None
    seen, terms = set(), []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            terms.append(t)
    match = " OR ".join('"%s"' % t.replace('"', '""') for t in terms)
    rows = con.execute(
        "SELECT id, url, bm25(chunks) AS s FROM chunks WHERE chunks MATCH ? ORDER BY s LIMIT 2",
        (match,)).fetchall()
    if not rows:
        return None, 0.0, [], None
    best_id, best_url, best_score = rows[0]
    picked = [chunks_by_id[best_id]]
    if len(rows) > 1:
        s2_id, s2_url, s2_score = rows[1]
        # 与 S0 同款第二块规则：同页、且分数在最佳值的 20% 以内（按绝对值比）
        if s2_url == best_url and abs(s2_score) >= 0.8 * abs(best_score):
            picked.append(chunks_by_id[s2_id])
    text = " ".join(c["text"] for c in picked)
    sources = []
    for c in picked:
        s = {"title": c["title"], "url": c["url"]}
        if s not in sources:
            sources.append(s)
    return text, round(best_score, 3), sources, rows


def verdict_for(q, got_behavior, text, sources, source_ok):
    if q["expected_behavior"] == "answer":
        facts = q["expected_facts"]
        found = [f for f in facts if norm(f) in norm(text)]
        ratio = len(found) / len(facts) if facts else 1.0
        if got_behavior == "answer" and source_ok and ratio >= 0.5:
            return "hit", found, ratio
        if got_behavior == "answer" and (source_ok or ratio > 0):
            return "partial", found, ratio
        return "miss", found, ratio
    # fallback / handoff：S1 同 S0，没有独立转人工判定层，兜底记为正确行为
    return ("hit", [], 0.0) if got_behavior == "fallback" else ("miss", [], 0.0)


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "s1-bm25"
    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT / "sample_store"))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        site = app.onboard(f"http://127.0.0.1:{port}/index.html")
    finally:
        server.shutdown()

    con = build_index(site["chunks"])
    by_id = {c["id"]: c for c in site["chunks"]}
    data = json.loads((ROOT / "eval" / "questions.json").read_text(encoding="utf-8"))
    rows = []
    for q in data["questions"]:
        t0 = time.perf_counter()
        raw_text, score, raw_sources, _ = bm25_answer(con, by_id, q["question"])
        ms = (time.perf_counter() - t0) * 1000
        got_behavior = "answer" if (raw_text and score <= HEADLINE_THRESHOLD) else "fallback"
        text = raw_text if got_behavior == "answer" else ""
        sources = raw_sources if got_behavior == "answer" else []
        src_files = [s["url"].rsplit("/", 1)[-1] for s in sources]
        raw_src_files = [s["url"].rsplit("/", 1)[-1] for s in raw_sources]
        source_ok = bool(q["expected_sources"]) and any(
            f in src_files for f in q["expected_sources"])
        verdict, found, ratio = verdict_for(q, got_behavior, text, sources, source_ok)
        rows.append({**q, "got_behavior": got_behavior, "score": score,
                     "sources": src_files, "source_ok": source_ok,
                     "raw_answer_text": raw_text or "", "raw_sources": raw_src_files,
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
    lines = [f"# 成绩单 — S1 SQLite FTS5 BM25（2026-11-14）\n",
             f"语料：Momo Ceramics {len(site['pages'])} 页 / {len(site['chunks'])} 个知识块，与 S0 同一批次 onboard。自动评分，口径见 `../README.md`。\n",
             f"Headline 阈值：best bm25 <= {HEADLINE_THRESHOLD} 才作答（运行前定死，见 `run_s1.py` 注释）；分数越负越相关。\n",
             "| 范围 | 题数 | hit | partial | miss | 命中率 |", "|---|---:|---:|---:|---:|---:|"]
    for label, sub in [("英文核心集 A–F", core)] + \
            [(g, [r for r in core if r["group"] == g]) for g in
             ["direct", "paraphrase", "multihop", "near_miss", "unanswerable", "handoff"]] + \
            [("中文探索组 G（单独计分）", zh)]:
        n, h, p, m = stats(sub)
        lines.append(f"| {label} | {n} | {h} | {p} | {m} | {h / n:.0%} |")
    fb = [r for r in core if r["expected_behavior"] == "fallback"]
    lines.append(f"\n兜底组（D+E）正确率：{sum(r['verdict'] == 'hit' for r in fb)}/{len(fb)}。"
                 f"延迟：每题平均 {sum(r['latency_ms'] for r in rows) / len(rows):.1f} ms（本地 SQLite FTS5，无模型调用，成本 0）。\n")

    # 敏感性：同一批 BM25 分数换三档阈值重判（诊断用，不改 headline）
    lines.append("## 阈值敏感性（诊断：同一批 BM25 分数，三档阈值重判）\n")
    lines.append("| 阈值（bm25 <=） | 英文核心集 hit | 兜底组 D+E 正确 |")
    lines.append("|---:|---:|---:|")
    for th in SENSITIVITY:
        hits, fb_hits = 0, 0
        for r in core:
            beh = "answer" if (r["raw_answer_text"] and r["score"] <= th) else "fallback"
            txt = r["raw_answer_text"] if beh == "answer" else ""
            srcs = [{"url": s} for s in r["raw_sources"]] if beh == "answer" else []
            sok = bool(r["expected_sources"]) and any(
                f in r["raw_sources"] for f in r["expected_sources"]) if beh == "answer" else False
            v, _, _ = verdict_for(r, beh, txt, srcs, sok)
            if v == "hit":
                hits += 1
                if r["expected_behavior"] == "fallback":
                    fb_hits += 1
        lines.append(f"| {th} | {hits}/55 | {fb_hits}/{len(fb)} |")
    lines.append("\n注：敏感性表按“阈值越松、作答越多”单调变化；headline 判定以 -1.0 为准。\n")
    lines.append("## 逐题明细\n| ID | 组 | 期望 | 实际 | BM25 分数 | 来源 | 事实 | 判定 |")
    lines.append("|---|---|---|---|---:|---|---|---|")
    for r in rows:
        lines.append(f"| {r['id']} | {r['group']} | {r['expected_behavior']} | {r['got_behavior']} | "
                     f"{r['score']} | {', '.join(r['sources']) or '—'} | "
                     f"{len(r['facts_found'])}/{len(r['expected_facts'])} | {r['verdict']} |")
    (out_dir / f"{name}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    n, h, p, m = stats(core)
    print(f"S1 core {n}题: hit {h} partial {p} miss {m} ({h / n:.0%}) | zh {stats(zh)} | 明细 -> eval/results/{name}.md")


if __name__ == "__main__":
    main()
