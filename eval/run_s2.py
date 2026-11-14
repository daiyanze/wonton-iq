#!/usr/bin/env python3
"""跑 S2：BM25 + JEV 单轮决策，对照 eval/questions.json 同一套题、同一套评分。

与 S1 只变一个变量：候选的取舍不再由 BM25 分数阈值决定，改由 JEV（TypeSafe
System One，Noul 问题）逐块判断“这段原文是否给出了回答顾客问题所需的事实”。
其余不变：同一 onboard 抓取与切块（app.onboard）、同一分词与同义词扩展
（app.tokenize / app.expand）、同一 BM25 MATCH 候选池（全部命中块、按 bm25
排序）、同一抽取式拼答与出处、同一评分口径（verdict_for 与 run_s1.py 逐字一致）。

运行前定死的设计（不看题库成绩调参）：
- JEV 判定线 noul >= 0.5。0.5 是概率模型自身的判定边界，不是拟合出来的阈值。
- 每题把全部候选打包成一次请求：state = 顾客问题，每个候选一个 Noul 问题，
  instructions 内嵌该块原文，问题之间隔离评估（TypeSafe 官方 Noul 文档的用法）。
- Noul 的 instructions 与 criteria 文本固定为本文件常量，对所有题、所有块一致。
- 选中的块按 BM25 顺序拼成答案；一块都没选中（或没有候选）则兜底。
- 延迟口径：题目之间 4 线程并行（真实部署不会串行等），每题延迟记“服务时间”
  = 本地 BM25 耗时 + 该题自己的 JEV 调用耗时之和，不含线程排队等待。
- 成本口径：按官方价格 $0.042 / 1M input tokens 计，output tokens 免费；
  token 数取每次响应 usage 字段的实测值。

JEV 调用走 custom.typesafe 连接器 helper（凭证在注册连接里，本文件不接触密钥）：
~/workspace/custom-connectors/custom.typesafe/bin/jev.py

用法：python3 eval/run_s2.py [输出名，默认 s2-jev-single]
"""
import json
import sqlite3
import sys
import tempfile
import threading
import time
import urllib.error
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.typesafe/bin"))
import app  # noqa: E402
import jev  # noqa: E402  (custom.typesafe 连接器 helper)

_tmp = Path(tempfile.mkdtemp(prefix="eval-s2-"))
app.SITES_FILE = str(_tmp / "sites.json")
app.EVENTS_FILE = str(_tmp / "events.json")

ACCEPT = 0.5  # JEV noul 判定线，运行前定死
PRICE_PER_M_INPUT = 0.042  # 官方 models 页：$0.042 / 1M input tokens，output 免费
MODEL = "jev-latest"

NOUL_INSTRUCTIONS = (
    "The passage below is from an online store's website.\n"
    "Passage: {text}\n"
    "Does this passage state a fact that answers part or all of the customer's "
    "question in the state, or a fact that is needed in order to answer it?"
)
NOUL_CRITERIA = {
    "true": "The passage states at least one concrete fact, such as a price, a "
            "time, a condition, a policy term or a product detail, that forms "
            "part of the answer to the customer's question.",
    "false": "The passage is only about the same general topic, or states "
             "nothing that would be quoted in a correct answer to this question.",
}
NOUL2_INSTRUCTIONS = (
    "The passage below is from an online store's website.\n"
    "Passage: {text}\n"
    "Given the facts already found in the state, does this passage state an "
    "additional fact that is needed to complete the answer to the customer's "
    "question?"
)
NOUL2_CRITERIA = {
    "true": "The passage adds a concrete fact required for the complete answer "
            "that the facts already found do not cover.",
    "false": "The passage repeats a fact already found, is only about the same "
             "general topic, or is not needed to answer the question.",
}


def norm(s):
    return " ".join((s or "").lower().split())


def verdict_for(q, got_behavior, text, sources, source_ok):
    # 与 run_s1.py 逐字一致的评分口径，保证 S0/S1/S2/S3 可比
    if q["expected_behavior"] == "answer":
        facts = q["expected_facts"]
        found = [f for f in facts if norm(f) in norm(text)]
        ratio = len(found) / len(facts) if facts else 1.0
        if got_behavior == "answer" and source_ok and ratio >= 0.5:
            return "hit", found, ratio
        if got_behavior == "answer" and (source_ok or ratio > 0):
            return "partial", found, ratio
        return "miss", found, ratio
    # fallback / handoff：与 S0/S1 相同，没有独立转人工判定层，兜底记为正确行为
    return ("hit", [], 0.0) if got_behavior == "fallback" else ("miss", [], 0.0)


# ---------- BM25 候选（与 run_s1.py 同款，只是不再 LIMIT 2） ----------

def build_index_file(chunks):
    path = str(_tmp / "index.db")
    con = sqlite3.connect(path)
    con.execute("CREATE VIRTUAL TABLE chunks USING fts5(id UNINDEXED, url UNINDEXED, text, tokenize='unicode61')")
    for c in chunks:
        con.execute("INSERT INTO chunks (id, url, text) VALUES (?, ?, ?)",
                    (c["id"], c["url"], c["text"]))
    con.commit()
    con.close()
    return path


class Index:
    """文件型 FTS5 索引，每线程一条连接（内存库不能跨连接共享）。"""

    def __init__(self, path):
        self.path = path
        self._local = threading.local()

    def conn(self):
        con = getattr(self._local, "con", None)
        if con is None:
            con = sqlite3.connect(self.path)
            self._local.con = con
        return con


def query_terms(question):
    seen, terms = set(), []
    for t in app.expand(app.tokenize(question)):
        if t not in seen:
            seen.add(t)
            terms.append(t)
    return terms


def get_candidates(index, by_id, terms):
    """返回 [(chunk, bm25分数)]，按分数升序（越负越相关）；无词或无命中返回 []。"""
    if not terms:
        return []
    match = " OR ".join('"%s"' % t.replace('"', '""') for t in terms)
    rows = index.conn().execute(
        "SELECT id, bm25(chunks) AS s FROM chunks WHERE chunks MATCH ? ORDER BY s",
        (match,)).fetchall()
    return [(by_id[r[0]], r[1]) for r in rows]


# ---------- JEV 决策 ----------

class JevJudge:
    """把候选块打包成一次 System One 请求逐块打 Noul 概率。线程安全地累计统计。"""

    def __init__(self):
        self._lock = threading.Lock()
        self.call_latency_s = []      # 每次成功调用的耗时
        self.retries = 0
        self.model_version = None

    def _call(self, payload):
        last_err = None
        for attempt in range(3):
            try:
                data, latency = jev.post_systemone(payload, timeout=60)
                with self._lock:
                    self.call_latency_s.append(latency)
                    if data.get("model"):
                        self.model_version = data["model"]
                return data
            except jev.JevHTTPError as e:
                last_err = e
                if e.status != 429 and e.status < 500:
                    raise
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                last_err = e
            with self._lock:
                self.retries += 1
            time.sleep(1.5 * (attempt + 1))
        raise RuntimeError(f"JEV call failed after 3 attempts: {last_err}")

    def judge(self, question, chunks, context_chunks=None):
        """返回 (probs {chunk_id: noul}, usage_in, usage_out, api_seconds)。

        context_chunks 为 None 时是单轮判定（S2 / S3 第一轮）；
        否则 state 里带上已选中的事实，问的是“还缺不缺这一块”（S3 第二轮）。
        """
        if not chunks:
            return {}, 0, 0, 0.0
        if context_chunks:
            state = ("Customer question: " + question + "\n\nFacts already found:\n" +
                     "\n".join("- " + c["text"] for c in context_chunks))
            tmpl, crit = NOUL2_INSTRUCTIONS, NOUL2_CRITERIA
        else:
            state = "Customer question: " + question
            tmpl, crit = NOUL_INSTRUCTIONS, NOUL_CRITERIA
        questions = {}
        for c in chunks:
            questions["chunk_" + c["id"]] = {
                "type": "noul",
                "instructions": tmpl.format(text=c["text"]),
                "criteria": crit,
            }
        t0 = time.perf_counter()
        data = self._call({"model": MODEL, "state": state, "questions": questions})
        api_s = time.perf_counter() - t0
        probs = {}
        for c in chunks:
            ans = data["answers"]["chunk_" + c["id"]]
            probs[c["id"]] = float(ans["noul"])
        usage = data.get("usage", {})
        return probs, usage.get("input_tokens", 0), usage.get("output_tokens", 0), api_s


def assemble(selected_chunks):
    text = " ".join(c["text"] for c in selected_chunks)
    sources = []
    for c in selected_chunks:
        s = {"title": c["title"], "url": c["url"]}
        if s not in sources:
            sources.append(s)
    return text, sources


def answer_s2(index, by_id, qtext, judge):
    """S2 单轮：BM25 候选 -> JEV 逐块判定 -> >=0.5 的块拼答。"""
    t0 = time.perf_counter()
    cands = get_candidates(index, by_id, query_terms(qtext))
    local_s = time.perf_counter() - t0
    if not cands:
        return {"text": "", "sources": [], "best_bm25": 0.0, "noul_max": None,
                "probs": {}, "selected": [], "n_candidates": 0,
                "calls": 0, "input_tokens": 0, "output_tokens": 0,
                "service_s": local_s, "rounds": []}
    probs, u_in, u_out, api_s = judge.judge(qtext, [c for c, _ in cands])
    selected = [c for c, _ in cands if probs[c["id"]] >= ACCEPT]
    text, sources = assemble(selected)
    return {"text": text, "sources": sources,
            "best_bm25": round(cands[0][1], 3),
            "noul_max": max(probs.values()) if probs else None,
            "probs": probs, "selected": [c["id"] for c in selected],
            "n_candidates": len(cands),
            "calls": 1, "input_tokens": u_in, "output_tokens": u_out,
            "service_s": local_s + api_s,
            "rounds": [{"round": 1, "candidates": len(cands),
                        "selected": [c["id"] for c in selected]}]}


# ---------- 评分与成绩单（结构与 run_s1.py 一致） ----------

def stats(sub):
    n = len(sub)
    h = sum(r["verdict"] == "hit" for r in sub)
    p = sum(r["verdict"] == "partial" for r in sub)
    return n, h, p, n - h - p


def p50_ms(values_s):
    return round(median(values_s) * 1000) if values_s else 0


def write_report(name, heading, method_lines, rows, site, judge):
    out_dir = ROOT / "eval" / "results"
    out_dir.mkdir(exist_ok=True)
    (out_dir / f"{name}.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

    core = [r for r in rows if r["group"] != "zh_exploratory"]
    zh = [r for r in rows if r["group"] == "zh_exploratory"]
    lines = [f"# 成绩单 — {heading}（2026-11-14）\n",
             f"语料：Momo Ceramics {len(site['pages'])} 页 / {len(site['chunks'])} 个知识块，与 S0/S1 同一批次 onboard。自动评分，口径见 `../README.md`。\n"]
    lines += method_lines
    lines += ["| 范围 | 题数 | hit | partial | miss | 命中率 |", "|---|---:|---:|---:|---:|---:|"]
    for label, sub in [("英文核心集 A–F", core)] + \
            [(g, [r for r in core if r["group"] == g]) for g in
             ["direct", "paraphrase", "multihop", "near_miss", "unanswerable", "handoff"]] + \
            [("中文探索组 G（单独计分）", zh)]:
        n, h, p, m = stats(sub)
        lines.append(f"| {label} | {n} | {h} | {p} | {m} | {h / n:.0%} |")
    fb_de = [r for r in core if r["group"] in ("near_miss", "unanswerable")]
    lines.append(f"\n兜底组（D+E）正确率：{sum(r['verdict'] == 'hit' for r in fb_de)}/{len(fb_de)}。"
                 f"人工边界组（F）正确率：{sum(r['verdict'] == 'hit' for r in core if r['group'] == 'handoff')}/5。\n")

    core_tokens = sum(r["jev"]["input_tokens"] for r in core)
    total_calls = sum(r["jev"]["calls"] for r in rows)
    lines.append(
        f"延迟与成本：每题服务时间 p50 {p50_ms([r['service_s'] for r in core])} ms、平均 "
        f"{sum(r['service_s'] for r in core) / len(core) * 1000:.0f} ms（核心集，含本地 BM25 与 JEV 调用，"
        f"不含线程排队）；JEV 单次调用 p50 {p50_ms(judge.call_latency_s)} ms，共 {total_calls} 次调用"
        f"（另重试 {judge.retries} 次）；input tokens 共 {sum(r['jev']['input_tokens'] for r in rows)}，"
        f"核心集每题成本 ${core_tokens * PRICE_PER_M_INPUT / 1e6 / len(core):.5f}"
        f"（${PRICE_PER_M_INPUT}/1M input tokens，output 免费）。\n")

    lines.append("## 逐题明细\n| ID | 组 | 期望 | 实际 | 最高 noul | 来源 | 事实 | 判定 |")
    lines.append("|---|---|---|---|---:|---|---|---|")
    for r in rows:
        nm = r["jev"]["noul_max"]
        lines.append(f"| {r['id']} | {r['group']} | {r['expected_behavior']} | {r['got_behavior']} | "
                     f"{nm if nm is not None else '—'} | {', '.join(r['sources']) or '—'} | "
                     f"{len(r['facts_found'])}/{len(r['expected_facts'])} | {r['verdict']} |")

    review = [r for r in rows if r["group"] in ("near_miss", "handoff") and r["verdict"] == "miss"]
    lines.append("\n## 人工复核材料（D/F 组 miss 的回答原文，判断是无害引用还是编造）\n")
    if not review:
        lines.append("无 D/F 组 miss。\n")
    for r in review:
        lines.append(f"- {r['id']}（{r['group']}）问：{r['question']}\n  答：{r['answer_text']}\n")
    (out_dir / f"{name}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return core, zh


def onboard_site():
    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT / "sample_store"))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        return app.onboard(f"http://127.0.0.1:{port}/index.html")
    finally:
        server.shutdown()


def build_row(q, res):
    got_behavior = "answer" if res["text"] else "fallback"
    text = res["text"] if got_behavior == "answer" else ""
    sources = res["sources"] if got_behavior == "answer" else []
    src_files = [s["url"].rsplit("/", 1)[-1] for s in sources]
    raw_src_files = [s["url"].rsplit("/", 1)[-1] for s in res["sources"]]
    source_ok = bool(q["expected_sources"]) and any(
        f in src_files for f in q["expected_sources"])
    verdict, found, ratio = verdict_for(q, got_behavior, text, sources, source_ok)
    return {**q, "got_behavior": got_behavior, "score": res["best_bm25"],
            "sources": src_files, "source_ok": source_ok,
            "raw_answer_text": res["text"], "raw_sources": raw_src_files,
            "facts_found": found, "facts_ratio": round(ratio, 2),
            "answer_text": text, "latency_ms": round(res["service_s"] * 1000, 1),
            "service_s": round(res["service_s"], 3),
            "verdict": verdict,
            "jev": {"n_candidates": res["n_candidates"], "probs": res["probs"],
                    "selected": res["selected"], "noul_max": res["noul_max"],
                    "calls": res["calls"], "input_tokens": res["input_tokens"],
                    "output_tokens": res["output_tokens"], "rounds": res["rounds"],
                    "expansion_terms": res.get("expansion_terms", [])}}


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "s2-jev-single"
    site = onboard_site()
    index = Index(build_index_file(site["chunks"]))
    by_id = {c["id"]: c for c in site["chunks"]}
    judge = JevJudge()
    data = json.loads((ROOT / "eval" / "questions.json").read_text(encoding="utf-8"))
    counter = Counter()

    def answer_fn(q):
        res = answer_s2(index, by_id, q["question"], judge)
        counter["done"] += 1
        print(f"[{counter['done']}/60] {q['id']} -> "
              f"{'answer' if res['text'] else 'fallback'}", flush=True)
        return build_row(q, res)

    with ThreadPoolExecutor(max_workers=4) as ex:
        rows = list(ex.map(answer_fn, data["questions"]))
    method = [
        f"判定方式：BM25 候选（全部命中块）逐块由 JEV 打 Noul 概率，>= {ACCEPT} 选中拼答，"
        f"一块没选中则兜底。判定线运行前定死（见 `run_s2.py`）。\n",
        f"JEV 模型：请求别名 {MODEL}，实际应答版本 {judge.model_version}。\n",
    ]
    core, zh = write_report(name, "S2 BM25 + JEV 单轮决策", method, rows, site, judge)
    n, h, p, m = stats(core)
    print(f"S2 core {n}题: hit {h} partial {p} miss {m} ({h / n:.0%}) | zh {stats(zh)} | 明细 -> eval/results/{name}.md")


if __name__ == "__main__":
    main()
