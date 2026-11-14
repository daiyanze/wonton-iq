# 第三轮 · 本地嵌入（S5b）环境记录

日期：2026-11-14。对应预注册 `prereg-round3.md`。托管臂 S5a 已于同日被 Dai 砍掉（无 OpenAI API key），本文件只涉及本地臂。

## 环境

- venv：`eval/.venv-emb`（Python 3.12，工作区内持久化）。
- 安装（精确版本，`pip list` 实测）：
  - `torch 2.15.0+cpu`（`pip install --index-url https://download.pytorch.org/whl/cpu torch`）
  - `sentence-transformers 6.3.0`（连带 `transformers 5.23.0`、`numpy 2.5.4`、`huggingface-hub 2.4.0`）
- 模型：`BAAI/bge-m3`，HF 修订 `5617a9f61b028005a4858fdac845db406aefb181`（refs/main 实测），缓存于 `eval/.hf-cache`（约 2.7 GB），稠密维度 1024，L2 归一化后余弦 = 点积；按 BGE-M3 官方用法，短查询不加指令前缀。
- 复现命令：

  ```bash
  cd ~/workspace/ecommerce-ai-support/eval
  HF_HUB_OFFLINE=1 HF_HOME=$PWD/.hf-cache .venv-emb/bin/python eval/run_s5.py s5b
  ```

## 过程中的两个坑（都已绕过，不影响实验变量）

1. 首次 `pip install torch` 的大文件下载在约 223/539 MB 处断流失败；加 `--retries 10 --timeout 120` 重跑成功。HF 模型下载同样多次断线靠客户端重试完成（约 2.3 GB，耗时约 10 分钟）。
2. 在线模式下 sentence-transformers 会尝试补下载 `model.safetensors`，在本机不稳定的出口上挂死（连接建立但零吞吐 ≥4 分钟）；缓存里的 `pytorch_model.bin` 本已完整（首轮下载时权重加载 100%）。**所有正式运行一律 `HF_HUB_OFFLINE=1` 走缓存**，加载行为与在线一致（同一修订、同一权重文件格式差异仅为序列化格式）。

## Sanity check（2026-11-14，正式跑之前）

- 模型加载（缓存命中）：4.4 s；10 个 chunk 批量编码：17.7 s。
- 单题查询编码时延（热身后）：2.3–3.8 s/题 —— 本 VM 为共享约 1.5 CPU，明显偏慢，属预注册声明的悲观口径。
- 三道探针（金块须进余弦 top-3）：**全部通过**，其中两道金块排第 1：

| 探针 | 问题 | 金块 | top-3（余弦） | 结果 |
|---|---|---|---|---|
| V3B17 | What's it crafted from — porcelain or something else?（BM25 零候选） | 0、6 | 7 (0.536)、**0 (0.501)**、**6 (0.478)** | ✅ |
| V3Z01 | 我想把没用过的杯子退回去，能在收到货之后多少天内退？ | 4 | **4 (0.712)**、5 (0.637)、2 (0.564) | ✅ |
| V3J02 | 日本国内だと、届くまで何日くらいかかりますか？ | 2 | **2 (0.714)**、5 (0.579)、3 (0.559) | ✅ |
