#!/usr/bin/env python3
"""小电商 AI 客服 MVP（试水版）— 仅用 Python 标准库。

链路：商家贴网址 -> 抓取站内页面 -> 切块建知识库 -> 顾客提问抽取式回答（带出处）
答不出 -> 记录未答问题 + 转人工。本版不接订单、不接平台、不编造政策。
"""
import json
import os
import re
import sqlite3
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SITES_FILE = os.path.join(DATA_DIR, "sites.json")
EVENTS_FILE = os.path.join(DATA_DIR, "events.json")
os.makedirs(DATA_DIR, exist_ok=True)

STOPWORDS = set("the a an and or of to in for on with is are do does can i you we it this that my your our".split())
SYNONYMS = {
    "return": "returns refund exchange", "returns": "return refund exchange",
    "refund": "return returns exchange", "exchange": "return returns refund",
    "ship": "shipping delivery", "shipping": "ship delivery", "delivery": "shipping ship",
    "track": "tracking shipment order", "tracking": "track shipment order",
    "order": "orders tracking", "wash": "care dishwasher clean", "clean": "care wash",
    "broken": "damaged damage replacement", "damaged": "damage broken replacement",
}
LINK_KEYWORDS = ["product", "shop", "faq", "help", "support", "shipping", "delivery",
                 "return", "refund", "policy", "policies", "contact", "about", "size", "guide", "care"]
# 检索与决策（2026-11-14 三次切换，成绩与预注册判定见 eval/README.md）：
# 1) 候选池：混合检索——SQLite FTS5 BM25 全部命中块 ∪ BGE-M3 稠密腿 top-8，
#    拼答顺序由 RRF（k=60）融合两张排名表决定（第三轮 S5b 与对照同题库实测）。
# 2) 决策：JEV（TypeSafe System One）单轮逐块打 Noul 概率，noul >= 接受线 的块拼答。
#    接受线按池分档：混合池 JEV_ACCEPT_HYBRID=0.9（第四轮预注册校准：v4 新题库
#    39/40、兜底 97.1%、编造 0；第三轮题集复判 49/50 与 96/100）；BM25-only 池
#    JEV_ACCEPT=0.8（第二轮校准定死，稠密腿不可用时的降级口径 = 原 S2-cal）。
# 降级梯（每一档都是曾经实测验证过的配置，见 answer_question）：
#   稠密腿不可用 -> BM25 池 + JEV @0.8；JEV 不可用 -> BM25 阈值决策
#   （best bm25 <= -1.0 才作答，S1 运行前定死，含同页第二块规则；FTS5 bm25()
#   返回负数，越负越相关）。
BM25_THRESHOLD = -1.0
JEV_ACCEPT = 0.8          # BM25-only 池的 JEV 接受线（eval/prereg-round2.md 定死）
JEV_ACCEPT_HYBRID = 0.9   # 混合池的 JEV 接受线（eval/prereg-round4.md 定死）
JEV_MODEL = "jev-latest"
JEV_TIMEOUT_S = 5    # 请求路径内单次尝试、短超时：JEV 慢/挂时尽快降级，不让顾客请求挂住
DENSE_TOPK = 8       # 稠密腿截断（第三轮预注册，与 eval/run_s5.py 一致）
RRF_K = 60           # RRF 融合常数（同上）
EMBED_MODEL = "BAAI/bge-m3"  # 稠密腿模型（同 eval/run_s5.py 的 LocalBGE）

# JEV 只走 custom.typesafe 连接器 helper（凭证在注册连接里，本文件不接触密钥）。
# 防御式导入：连接器缺失时 _jev 为 None，app 照常启动并走 BM25 降级决策。
_JEV_BIN = os.path.join(os.path.expanduser("~"),
                        "workspace/custom-connectors/custom.typesafe/bin")
if _JEV_BIN not in sys.path:
    sys.path.insert(0, _JEV_BIN)
try:
    import jev as _jev
except Exception:
    _jev = None

# Noul 问题文本与 eval/run_s2.py 逐字一致，保证线上行为与题库实测同款。
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

# ---- 稠密腿：本地 BGE-M3（sentence-transformers），与 eval/run_s5.py 的 LocalBGE 同款 ----
# 必须用 eval/.venv-emb 的解释器启动 app 才能加载（torch 只装在那个 venv 里）。
# 防御式懒加载：导入/加载失败只记为“稠密腿不可用”，app 照常启动，
# 问答整梯降级到 BM25 池 + JEV @0.8（原 S2-cal，见 answer_question 的降级梯）。
# 离线走 HF 缓存：在线模式在本机出口会挂死（eval/round3-setup.md 的坑），
# 所以在导入 sentence-transformers 之前先定好这两个环境变量（不覆盖外部已设的值）。
os.environ.setdefault("HF_HUB_OFFLINE", "1")
_HF_CACHE_DIR = os.path.join(BASE_DIR, "eval", ".hf-cache")
if os.path.isdir(_HF_CACHE_DIR):
    os.environ.setdefault("HF_HOME", _HF_CACHE_DIR)

_embedder = None
_embedder_unavailable = False
_embedder_lock = threading.Lock()
_encode_lock = threading.Lock()


def _get_embedder():
    """进程内单例懒加载 BGE-M3；不可用时返回 None（只试一次，失败不重试）。"""
    global _embedder, _embedder_unavailable
    if _embedder is not None:
        return _embedder
    if _embedder_unavailable:
        return None
    with _embedder_lock:
        if _embedder is not None:
            return _embedder
        if _embedder_unavailable:
            return None
        try:
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer(EMBED_MODEL)
        except Exception:
            _embedder_unavailable = True
            return None
    return _embedder


def _encode(texts):
    """批量编码，返回 L2 归一化向量（list[float]）列表；稠密腿不可用返回 None。

    编码参数与 eval/run_s5.py 的 LocalBGE.embed 逐项一致
    （normalize_embeddings=True、show_progress_bar=False）。编码串行化：
    本机 CPU 弱，多线程并发编码只会互相拖慢，不改结果。
    """
    model = _get_embedder()
    if model is None:
        return None
    try:
        with _encode_lock:
            vecs = model.encode(texts, normalize_embeddings=True,
                                show_progress_bar=False)
    except Exception:
        return None
    return [list(map(float, v)) for v in vecs]


def _persist_embeddings(site):
    """把回填好的块向量写回 sites.json 里该站点的记录（仅当该站点确实在库里）。"""
    try:
        sites = load_json(SITES_FILE, {})
        stored = sites.get(site.get("id"))
        if stored is not None and site.get("embeddings"):
            stored["embeddings"] = site["embeddings"]
            save_json(SITES_FILE, sites)
    except Exception:
        pass


def _site_embeddings(site):
    """返回 {chunk_id: 向量}：站点已存向量直接用；缺失则现算并回存
    （旧版本建的站点第一次被问到时惰性回填，无需数据迁移）。失败返回 None。"""
    chunks = site["chunks"]
    emb = site.get("embeddings") or {}
    if chunks and all(c["id"] in emb for c in chunks):
        return emb
    vecs = _encode([c["text"] for c in chunks])
    if vecs is None:
        return None
    emb = {c["id"]: v for c, v in zip(chunks, vecs)}
    site["embeddings"] = emb
    _persist_embeddings(site)
    return emb


def _dense_top_ids(site, question):
    """稠密腿排名：问题向量对全部块算余弦，取 top-DENSE_TOPK 的块 id
    （排序口径与 eval/run_s5.py 一致：余弦降序、同分按块 id）。
    返回 None 表示稠密腿不可用（与“可用”明确区分，供降级梯判定）。"""
    emb = _site_embeddings(site)
    if emb is None:
        return None
    qv = _encode([question])
    if qv is None:
        return None
    qv = qv[0]
    scored = sorted(((sum(x * y for x, y in zip(qv, emb[c["id"]])), c["id"])
                     for c in site["chunks"]),
                    key=lambda x: (-x[0], x[1]))
    return [cid for _, cid in scored[:DENSE_TOPK]]


def _rrf_order(bm25_ids, dense_ids, pool_ids):
    """RRF 融合定拼答顺序，与 eval/run_s5.py 的 rrf_order 逐字同款：
    每张表按名次贡献 1/(k+rank)，不在表中的块不从该表得分；
    同分先比最佳名次、再比块 id。"""
    score, best = {}, {}
    for rank, cid in enumerate(bm25_ids, 1):
        score[cid] = score.get(cid, 0.0) + 1.0 / (RRF_K + rank)
        best[cid] = min(best.get(cid, 10 ** 9), rank)
    for rank, cid in enumerate(dense_ids, 1):
        score[cid] = score.get(cid, 0.0) + 1.0 / (RRF_K + rank)
        best[cid] = min(best.get(cid, 10 ** 9), rank)
    return sorted(pool_ids, key=lambda cid: (-score.get(cid, 0.0), best.get(cid, 10 ** 9), cid))


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.text_parts = []
        self.links = []
        self._skip = 0
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip += 1
        if tag == "title":
            self._in_title = True
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self._skip:
            self._skip -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._skip:
            return
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title = text
        self.text_parts.append(text)


def fetch_page(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; SupportMVP/0.1)"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        ctype = resp.headers.get("Content-Type", "")
        if "html" not in ctype and ctype:
            return None
        raw = resp.read(800_000)
    parser = PageParser()
    parser.feed(raw.decode("utf-8", errors="ignore"))
    text = re.sub(r"\s+", " ", " ".join(parser.text_parts)).strip()
    links = []
    for href in parser.links:
        full = urllib.parse.urljoin(url, href)
        if urllib.parse.urlparse(full).scheme in ("http", "https"):
            links.append(full.split("#")[0])
    return {"url": url, "title": parser.title or urllib.parse.urlparse(url).path or url,
            "text": text, "links": links}


def chunk_text(text, size=420):
    sentences = re.split(r"(?<=[.!?。！？])\s+", text)
    chunks, cur = [], ""
    for s in sentences:
        if len(cur) + len(s) + 1 <= size:
            cur = (cur + " " + s).strip()
        else:
            if len(cur) >= 60:
                chunks.append(cur)
            cur = s
    if len(cur) >= 60:
        chunks.append(cur)
    return chunks


def link_score(url, host):
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc != host:
        return -1
    low = url.lower()
    return sum(1 for kw in LINK_KEYWORDS if kw in low)


def onboard(start_url, max_pages=12):
    if not re.match(r"^https?://", start_url):
        start_url = "https://" + start_url
    host = urllib.parse.urlparse(start_url).netloc
    visited, queue, pages = set(), [(start_url, 0)], []
    while queue and len(pages) < max_pages:
        url, depth = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        try:
            page = fetch_page(url)
        except Exception:
            page = None
        if not page or len(page["text"]) < 40:
            continue
        pages.append(page)
        if depth < 2:
            scored = sorted(((link_score(u, host), u) for u in set(page["links"])), reverse=True)
            for score, link in scored:
                if score >= 0 and link not in visited:
                    queue.append((link, depth + 1))
    chunks = []
    for page in pages:
        for i, chunk in enumerate(chunk_text(page["text"])):
            chunks.append({"id": f"{len(chunks)}", "url": page["url"], "title": page["title"], "text": chunk})
    suggested = []
    haystack = " ".join(p["url"].lower() + " " + p["title"].lower() for p in pages)
    if "return" in haystack or "refund" in haystack:
        suggested.append("What is your return policy?")
    if "shipping" in haystack or "delivery" in haystack:
        suggested.append("How long does shipping take?")
    if "faq" in haystack:
        suggested.append("Do you offer gift wrapping?")
    site = {
        "id": uuid.uuid4().hex[:8],
        "base_url": start_url,
        "name": pages[0]["title"] if pages else host,
        "created_at": int(time.time()),
        "pages": [{"url": p["url"], "title": p["title"]} for p in pages],
        "chunks": chunks,
        "suggested_questions": suggested,
    }
    # 建库时就算好块向量存入站点记录，问答时直接用；稠密腿不可用（普通
    # python3 启动）时跳过，之后用 venv 解释器提问时再惰性回填（_site_embeddings）。
    if chunks:
        vecs = _encode([c["text"] for c in chunks])
        if vecs is not None:
            site["embeddings"] = {c["id"]: v for c, v in zip(chunks, vecs)}
    sites = load_json(SITES_FILE, {})
    sites[site["id"]] = site
    save_json(SITES_FILE, sites)
    return site


def tokenize(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS and len(t) > 1]


def expand(tokens):
    out = list(tokens)
    for t in tokens:
        if t in SYNONYMS:
            out += SYNONYMS[t].split()
    return out


def build_bm25_index(chunks):
    """从站点已存的 JSON 知识块现建内存 FTS5 索引（与 eval/run_s1.py 同款）。"""
    con = sqlite3.connect(":memory:")
    con.execute("CREATE VIRTUAL TABLE chunks USING fts5(id UNINDEXED, url UNINDEXED, text, tokenize='unicode61')")
    for c in chunks:
        con.execute("INSERT INTO chunks (id, url, text) VALUES (?, ?, ?)",
                    (c["id"], c["url"], c["text"]))
    con.commit()
    return con


# 最近一次 answer_question 的决策信息（线程内），供 /api/chat 写事件日志用：
# {"decision": "hybrid-jev" | "bm25-jev" | "bm25-threshold" | "none", "degraded": bool}
# hybrid-jev = 主档（混合池 + JEV @0.9，degraded=False）；bm25-jev = 稠密腿不可用，
# 退回 BM25 池 + JEV @0.8；bm25-threshold = JEV 不可用，退回 BM25 阈值决策；
# 后两档 degraded=True。none = 无候选可判（无知识块 / 两腿皆空）。
_decision_local = threading.local()


def last_decision():
    return dict(getattr(_decision_local, "info", None) or
                {"decision": "none", "degraded": False})


def _set_decision(decision, degraded):
    _decision_local.info = {"decision": decision, "degraded": degraded}


def jev_probs(question, cand_chunks):
    """一次请求打包全部候选，逐块返回 Noul 概率 {chunk_id: noul}（与 eval/run_s2.py 同款）。

    单次尝试、短超时；任何失败（连接器缺失、HTTP 错误、超时、响应结构异常）
    都抛异常，由调用方降级——这里不吞异常、不编造概率。
    """
    if _jev is None:
        raise RuntimeError("jev connector helper unavailable")
    questions = {}
    for c in cand_chunks:
        questions["chunk_" + c["id"]] = {
            "type": "noul",
            "instructions": NOUL_INSTRUCTIONS.format(text=c["text"]),
            "criteria": NOUL_CRITERIA,
        }
    payload = {"model": JEV_MODEL, "state": "Customer question: " + question,
               "questions": questions}
    data, _latency = _jev.post_systemone(payload, timeout=JEV_TIMEOUT_S)
    answers = data.get("answers")
    if not isinstance(answers, dict) or not answers:
        raise ValueError("malformed JEV response: missing answers")
    probs = {}
    for c in cand_chunks:
        ans = answers.get("chunk_" + c["id"]) or {}
        probs[c["id"]] = float(ans.get("noul", 0.0))
    return probs


def _compose(picked):
    """抽取式拼答：选中块原文按给定顺序拼接 + 出处去重（与 eval 的 assemble 同款）。"""
    text = " ".join(c["text"] for c in picked)
    sources = []
    for c in picked:
        s = {"title": c["title"], "url": c["url"]}
        if s not in sources:
            sources.append(s)
    return text, sources


def _bm25_decide(rows, chunks_by_id):
    """原 BM25 阈值决策（S1 同款，含同页第二块规则）。只作 JEV 失败时的降级路径。"""
    best_id, best_url, best_score = rows[0]
    if best_score > BM25_THRESHOLD:
        return None, round(best_score, 3), []
    picked = [chunks_by_id[best_id]]
    if len(rows) > 1:
        s2_id, s2_url, s2_score = rows[1]
        # 与 S1 同款第二块规则：同页、且分数在最佳值的 20% 以内（按绝对值比）
        if s2_url == best_url and abs(s2_score) >= 0.8 * abs(best_score):
            picked.append(chunks_by_id[s2_id])
    text, sources = _compose(picked)
    return text, round(best_score, 3), sources


def answer_question(site, question):
    chunks = site["chunks"]
    if not chunks:
        _set_decision("none", False)
        return None, 0.0, []
    chunks_by_id = {c["id"]: c for c in chunks}
    seen, terms = set(), []
    for t in expand(tokenize(question)):
        if t not in seen:
            seen.add(t)
            terms.append(t)
    # BM25 腿：分词+同义词扩展后取全部命中块（中日问题分词为空，此腿自然为空，
    # 靠稠密腿出池——这正是第三轮要解决的问题）。
    rows = []
    if terms:
        match = " OR ".join('"%s"' % t.replace('"', '""') for t in terms)
        con = build_bm25_index(chunks)
        try:
            rows = con.execute(
                "SELECT id, url, bm25(chunks) AS s FROM chunks WHERE chunks MATCH ? ORDER BY s",
                (match,)).fetchall()
        finally:
            con.close()
    bm25_ids = [r[0] for r in rows]
    best_score = rows[0][2] if rows else 0.0
    # 稠密腿：可用则与 BM25 并池（去重）、RRF 定顺序、接受线 0.9；
    # 不可用（普通解释器/模型加载失败）则整腿关闭，走 S2-cal 档。
    dense_ids = _dense_top_ids(site, question)
    hybrid = dense_ids is not None
    if not bm25_ids and not dense_ids:
        _set_decision("none", not hybrid)
        return None, 0.0, []
    if hybrid:
        pool_ids = list(dict.fromkeys(bm25_ids + dense_ids))
        order = _rrf_order(bm25_ids, dense_ids, pool_ids)
        accept, tier = JEV_ACCEPT_HYBRID, "hybrid-jev"
    else:
        order = list(bm25_ids)
        accept, tier = JEV_ACCEPT, "bm25-jev"
    # 主决策：池内全部块打包成一次 JEV 请求逐块打 Noul 概率，
    # noul >= accept 的块按 order（混合池为 RRF 序、BM25 池为 BM25 序）拼答；
    # 一块都没过线则兜底（转人工路径不变）。
    try:
        probs = jev_probs(question, [chunks_by_id[cid] for cid in order])
    except Exception:
        probs = None
    if probs is not None:
        _set_decision(tier, not hybrid)
        picked = [chunks_by_id[cid] for cid in order if probs.get(cid, 0.0) >= accept]
        if not picked:
            return None, round(best_score, 3), []
        text, sources = _compose(picked)
        return text, round(best_score, 3), sources
    # 降级路径：JEV 任何失败（连接器缺失 / HTTP 错误 / 超时 / 响应异常）都不编造、
    # 不挂请求——与池的档位无关，一律退回 BM25 阈值决策（无 BM25 命中则兜底），
    # 并在事件日志里标记 degraded，顾客看到的回答格式与正常路径完全一致。
    _set_decision("bm25-threshold", True)
    if not rows:
        return None, 0.0, []
    return _bm25_decide(rows, chunks_by_id)


def log_event(event):
    events = load_json(EVENTS_FILE, [])
    event["ts"] = int(time.time())
    events.append(event)
    save_json(EVENTS_FILE, events)


def get_site(site_id):
    return load_json(SITES_FILE, {}).get(site_id)


LANDING = """<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>小电商 AI 客服 — MVP</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{font-family:system-ui;max-width:760px;margin:40px auto;padding:0 16px;line-height:1.6}
input,button,textarea{font-size:16px;padding:10px} input{width:70%} button{cursor:pointer}
.card{border:1px solid #ddd;border-radius:10px;padding:16px;margin:16px 0} code{background:#f4f4f4;padding:2px 6px}</style></head>
<body><h1>小电商 AI 客服 · 试水版</h1>
<p>商家贴上自己网站地址，系统自动抓取产品、FAQ、物流与退换政策，生成一个能回答顾客问题、答不出会转人工的客服助手。</p>
<div class="card"><h3>开通一个站点</h3>
<input id="url" placeholder="https://your-store.com 或示例 http://127.0.0.1:8077/">
<button onclick="onboard()">生成客服助手</button><div id="out"></div></div>
<div class="card"><h3>已开通</h3><div id="sites">加载中…</div></div>
<script>
async function onboard(){const u=document.getElementById('url').value.trim();if(!u)return;
document.getElementById('out').textContent='抓取中…';
const r=await fetch('/api/onboard',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:u})});
const d=await r.json();if(!r.ok){document.getElementById('out').textContent='失败：'+(d.error||r.status);return;}
document.getElementById('out').innerHTML='完成：抓到 '+d.pages+' 页、'+d.chunks+' 个知识块。<br>'+
'帮助中心：<a href="/help/'+d.id+'">/help/'+d.id+'</a> · 商家视图：<a href="/admin/'+d.id+'">/admin/'+d.id+'</a><br>'+
'嵌入代码：<code>&lt;script src="'+location.origin+'/widget.js?site='+d.id+'" async&gt;&lt;/script&gt;</code>';loadSites();}
async function loadSites(){const r=await fetch('/api/sites');const d=await r.json();
document.getElementById('sites').innerHTML=d.sites.length?d.sites.map(s=>'<div>• <b>'+s.name+'</b>（'+s.pages+' 页）— <a href="/help/'+s.id+'">帮助中心</a> · <a href="/admin/'+s.id+'">商家视图</a></div>').join(''):'暂无';}
loadSites();
</script></body></html>"""

HELP = """<!doctype html><html lang="zh"><head><meta charset="utf-8"><title>__NAME__ — 帮助中心</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{font-family:system-ui;max-width:720px;margin:32px auto;padding:0 16px;line-height:1.6}
#log div{margin:10px 0} .q{font-weight:600} .src{color:#666;font-size:13px} input,textarea{font-size:16px;padding:9px}
input[type=text]{width:75%} button{padding:9px 14px;cursor:pointer} .card{border:1px solid #ddd;border-radius:10px;padding:14px;margin-top:18px}</style></head>
<body><h1>__NAME__ · 帮助中心</h1>
<p>问我产品、物流、退换货的问题。我的回答只引用本店网站已公布的信息，并附出处；查不到的会帮你转人工。</p>
<div><input type="text" id="q" placeholder="例如：What is your return policy?"> <button onclick="ask()">提问</button></div>
<p style="color:#666;font-size:14px">试试：__SUGGESTED__</p>
<div id="log"></div>
<div class="card"><h3>还是需要人工？</h3>
<input type="text" id="email" placeholder="你的邮箱" style="width:45%">
<input type="text" id="msg" placeholder="简单描述问题" style="width:45%">
<button onclick="handoff()">提交转人工</button><div id="hok"></div></div>
<script>
const SITE='__SITE_ID__';
async function ask(){const q=document.getElementById('q').value.trim();if(!q)return;
const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({site_id:SITE,question:q})});
const d=await r.json();const log=document.getElementById('log');
const src=d.sources&&d.sources.length?'<div class="src">出处：'+d.sources.map(s=>'<a href="'+s.url+'">'+s.title+'</a>').join(' · ')+'</div>':'';
log.innerHTML='<div><div class="q">问：'+q+'</div><div>'+d.answer+'</div>'+src+'</div>'+log.innerHTML;}
async function handoff(){const email=document.getElementById('email').value.trim(),message=document.getElementById('msg').value.trim();
if(!email||!message)return;const r=await fetch('/api/handoff',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({site_id:SITE,email:email,message:message})});
document.getElementById('hok').textContent=r.ok?'已提交，商家会通过邮箱回复你。':'提交失败，请重试。';}
</script></body></html>"""

WIDGET_JS = """(function(){var s=document.currentScript;var base=new URL(s.src).origin;
var site=new URL(s.src).searchParams.get('site');if(!site)return;
var btn=document.createElement('button');btn.textContent='💬 客服帮助';
btn.style.cssText='position:fixed;right:18px;bottom:18px;z-index:99999;padding:10px 16px;border-radius:999px;border:1px solid #ccc;background:#111;color:#fff;cursor:pointer';
var panel=document.createElement('div');
panel.style.cssText='position:fixed;right:18px;bottom:70px;z-index:99999;width:320px;max-height:60vh;overflow:auto;background:#fff;border:1px solid #ddd;border-radius:12px;padding:12px;display:none;font-family:system-ui;font-size:14px;line-height:1.5';
panel.innerHTML='<b>帮助中心</b><div class="log"></div><div style="margin-top:8px"><input placeholder="输入问题…" style="width:68%;padding:7px"><button style="padding:7px 10px">发送</button></div>';
btn.onclick=function(){panel.style.display=panel.style.display==='none'?'block':'none';};
document.body.appendChild(btn);document.body.appendChild(panel);
var input=panel.querySelector('input'),log=panel.querySelector('.log');
async function send(){var q=input.value.trim();if(!q)return;input.value='';
var r=await fetch(base+'/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({site_id:site,question:q})});
var d=await r.json();log.innerHTML='<div style="margin:8px 0"><b>问：</b>'+q+'<br>'+d.answer+'</div>'+log.innerHTML;}
panel.querySelector('button').onclick=send;
input.addEventListener('keydown',function(e){if(e.key==='Enter')send();});
})();"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path, qs = parsed.path, urllib.parse.parse_qs(parsed.query)
        if path == "/":
            return self._send(200, LANDING, "text/html; charset=utf-8")
        if path == "/api/sites":
            sites = load_json(SITES_FILE, {})
            return self._json(200, {"sites": [{"id": s["id"], "name": s["name"], "pages": len(s["pages"])}
                                              for s in sites.values()]})
        if path == "/widget.js":
            return self._send(200, WIDGET_JS, "application/javascript; charset=utf-8")
        if path.startswith("/help/"):
            site = get_site(path.split("/")[2])
            if not site:
                return self._json(404, {"error": "site not found"})
            html = (HELP.replace("__NAME__", site["name"]).replace("__SITE_ID__", site["id"])
                    .replace("__SUGGESTED__", " / ".join(site["suggested_questions"]) or "（暂无示例问题）"))
            return self._send(200, html, "text/html; charset=utf-8")
        if path.startswith("/admin/"):
            site = get_site(path.split("/")[2])
            if not site:
                return self._json(404, {"error": "site not found"})
            events = [e for e in load_json(EVENTS_FILE, []) if e.get("site_id") == site["id"]]
            unanswered = [e for e in events if e["type"] == "unanswered"]
            handoffs = [e for e in events if e["type"] == "handoff"]
            rows_u = "".join(f"<li>{e['question']}（{time.strftime('%m-%d %H:%M', time.localtime(e['ts']))}）</li>" for e in unanswered) or "<li>暂无</li>"
            rows_h = "".join(f"<li>{e['email']}：{e['message']}</li>" for e in handoffs) or "<li>暂无</li>"
            srcs = "".join(f"<li><a href='{p['url']}'>{p['title']}</a></li>" for p in site["pages"])
            html = f"""<!doctype html><html lang="zh"><head><meta charset="utf-8"><title>商家视图 — {site['name']}</title>
<style>body{{font-family:system-ui;max-width:760px;margin:32px auto;padding:0 16px;line-height:1.6}}</style></head>
<body><h1>商家视图 · {site['name']}</h1>
<p>已抓取 {len(site['pages'])} 页 · {len(site['chunks'])} 个知识块 · 累计提问 {len([e for e in events if e['type']=='chat'])} 次 · 未答 {len(unanswered)} 条 · 转人工 {len(handoffs)} 条</p>
<h3>未答问题（产品要补的信息）</h3><ul>{rows_u}</ul>
<h3>转人工</h3><ul>{rows_h}</ul>
<h3>知识来源页</h3><ul>{srcs}</ul></body></html>"""
            return self._send(200, html, "text/html; charset=utf-8")
        return self._json(404, {"error": "not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return self._json(400, {"error": "invalid json"})
        if parsed.path == "/api/onboard":
            url = (body.get("url") or "").strip()
            if not url:
                return self._json(400, {"error": "url required"})
            try:
                site = onboard(url)
            except Exception as e:
                return self._json(502, {"error": f"onboard failed: {e}"})
            if not site["chunks"]:
                return self._json(422, {"error": "no readable pages found"})
            return self._json(200, {"id": site["id"], "name": site["name"],
                                    "pages": len(site["pages"]), "chunks": len(site["chunks"]),
                                    "suggested_questions": site["suggested_questions"]})
        if parsed.path == "/api/chat":
            site = get_site(body.get("site_id", ""))
            question = (body.get("question") or "").strip()
            if not site or not question:
                return self._json(400, {"error": "site_id and question required"})
            text, score, sources = answer_question(site, question)
            decision = last_decision()
            log_event({"type": "chat", "site_id": site["id"], "question": question, "score": score,
                       "decision": decision["decision"], "degraded": decision["degraded"]})
            if text is None:
                log_event({"type": "unanswered", "site_id": site["id"], "question": question, "score": score,
                           "decision": decision["decision"], "degraded": decision["degraded"]})
                return self._json(200, {"answer": "这个问题在本店已公布的信息里没有找到答案。可以在下方留下邮箱转人工，商家会回复你。",
                                        "sources": [], "needs_human": True, "score": score})
            return self._json(200, {"answer": text, "sources": sources, "needs_human": False, "score": score})
        if parsed.path == "/api/handoff":
            site = get_site(body.get("site_id", ""))
            email, message = (body.get("email") or "").strip(), (body.get("message") or "").strip()
            if not site or not email or not message:
                return self._json(400, {"error": "site_id, email and message required"})
            log_event({"type": "handoff", "site_id": site["id"], "email": email, "message": message})
            return self._json(200, {"ok": True})
        return self._json(404, {"error": "not found"})


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8078
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
