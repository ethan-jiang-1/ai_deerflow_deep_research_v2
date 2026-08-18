## 1. 测试先行：targeted worker 排序 + gap 描述

- [x] 1.1 `tests/graph/test_targeted_evidence_real.py` 新增用例：模型输出两个
      source 且为逆 canonical 序（复用 `_targeted_summary` 模式）→ 断言 ledger
      记录存在且 `source_refs` 按 `(source_id, canonical_url)` 排序（修复前红：
      候选被拒、WORKER_FAILED、零记录）
- [x] 1.2 新增 prompt 用例：`build_targeted_worker_prompt` 带描述 → objective
      含 bounded 描述；不带 → 仅 id；超长描述被截断
- [x] 1.3 新增 node 级用例：store 的 gap 记录存在 → worker 请求携带描述；
      store 读失败 → 仍以 id-only 上下文运行（fail-soft，不崩）
- [x] 1.4 wave0 worker 防御用例：逆序 2 source 输出 → 候选被接纳
- [x] 1.5 运行新用例确认红

## 2. 实现修复

- [x] 2.1 `targeted_evidence/subgraph.py`：worker 内
      `ordered = tuple(sorted(output.sources, key=lambda s: (s.source_id, s.canonical_url)))`
      后构建 refs（对齐 wave1 范式）
- [x] 2.2 `targeted_evidence/subgraph.py`：`run_gap_workers` 内 try/except
      `controller.store.read_synthesis_gaps()` 建 `desc_by_id`，closure 捕获；
      `build_targeted_worker_prompt(gap_id, gap_description=...)` 带 bounded 描述
- [x] 2.3 `prompts.py`：签名扩展 + `MAX_TARGETED_GAP_DESCRIPTION_CHARS` 截断
- [x] 2.4 `wave0/subgraph.py`：同款排序（防御）
- [x] 2.5 ruff 通过；新用例转绿；既有 targeted/wave0 测试保持绿

## 3. 回归与验证

- [x] 3.1 全量测试：`UV_NO_CACHE=1 make verify`（本机 uv 全局缓存权限限制，
      `UV_OFFLINE=1` 会在 lock-check 失败；等价窄口径：
      `UV_NO_CACHE=1 .venv/bin/python -m pytest tests/unit tests/graph tests/contract`）
- [x] 3.2 `openspec validate fix-targeted-evidence-worker --strict` 通过
- [x] 3.3 更新 BUG-045（修复关联指向本 change）；BUG-044 关联注明
- [ ] 3.4 真实 003 验证 run（两个 change 都已落地后）：预期 targeted 有
      ledger 提交、wave2 有收敛机会；不收敛时按 BUG-044 降级交付
