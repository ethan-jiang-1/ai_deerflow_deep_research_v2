# BUG-045: targeted_evidence worker 未排序 source_refs，候选校验必败（`source_refs_not_canonical`）→ wave2 补证循环 9/9 零产出

> 严重级别: P1 | 发现: 2026-08-18 | 状态: 已修复（fix-targeted-evidence-worker）

## 症状

真实 003 run（BUG-044 同一 run）中，wave2 targeted_evidence 补证循环
**9/9 attempts 全部 `work.failed`（WORKER_FAILED），零提交、零产出**——
三个补证轮次（w0000/w0001/w0002 × a00/a01/a02）无一例外。模型的 web
搜索全部成功（17/17 model_tool completed，0 failed），result.json 与
source 缓存都写出来了，但候选在提交前校验失败。结果：gap 永远补不上，
wave2 gate 必然耗尽 →（叠加 BUG-044 的路由问题）run blocked。

这解释了 BUG-044 run 中"honest gap 不收敛"的**真实原因不是模型波动，而是
补证循环结构性瘫痪**：模型甚至诚实报告"assigned gap 只有裸 id、无描述"、
搜到的全是方法论文章（arxiv/PMC/harnex.ai）。

## 根因

`CandidateResult.source_refs` 校验器（`src/deerflow_deep_research/domain/
work_units.py` `validate_source_refs`）要求 source_refs 按
`(source_id, canonical_url)` 字典序排序且唯一，否则抛
`source_refs_not_canonical`（ValueError）。

而 `targeted_evidence/subgraph.py` `run_gap_workers.worker`（行 187）按
**模型输出顺序**遍历 `output.sources` 构建 source_refs，没有排序。模型的
source_id 形如 `source:te_<host>_<path>`（由 URL 派生），搜索返回的顺序
（相关度序）几乎必然不是字典序 → 校验必败 → run_worker 捕获异常 →
WORKER_FAILED（plain exception，无 category 字段，detail hash 匹配
`terminal_code=worker_failed`）→ attempt 失败 → 重试同样失败 → 3 次后
exhaustion。

**同类缺陷**：`wave0/subgraph.py:273` 同样未排序——本次 run wave0 侥幸
（模型恰好输出 src_1..src_7 有序）；若模型返回 2+ 无序 source 同样会炸。
`wave1/subgraph.py:278` 显式排序（`sorted(output.sources, key=...)`），是
正确范式。

## 复现

1. 代码级复现（本 run 真实数据，见
   `_backlog/_done/_evidence/003-blocked-20260818-b_8iYx4hy/bundle/`）：
   用 `work/g0_targeted_evidence_w0000/..._a00/result.json` 的 sources 按
   模型顺序构建 SourceRefs → `CandidateResult.model_validate` 抛
   `source_refs_not_canonical`；排序后通过。
2. 运行级复现：`UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run <root> --mode
   003"`，events.jsonl 中 targeted_evidence 全部 attempt 终态
   `failure_category=work.failed`、无 validation/submit 事件。

## 修复关联

✅ 已修复（2026-08-18，代码已落地）：OpenSpec change
`openspec/changes/archive/2026-08-18-fix-targeted-evidence-worker/`（`targeted-evidence-loop`
TEL-002 delta）。

1. **排序修复**：`targeted_evidence/subgraph.py` worker 构建 source_refs 前按
   `(source_id, canonical_url)` 排序（对齐 wave1 范式）；`wave0/subgraph.py`
   同类缺陷一并防御性修复。
2. **gap 描述上下文**：`run_gap_workers` 经 `store.read_synthesis_gaps()`
   有界读取 canonical artifact 的 gap 描述（try/except fail-soft，读失败退
   化为 id-only），`build_targeted_worker_prompt(gap_id, gap_description=...)`
   以 `MAX_TARGETED_GAP_DESCRIPTION_CHARS=512` 截断带入 objective；路由权威
   仍 id-only（TEL-001 不变），描述只作 worker 检索上下文。

验证：`tests/graph/test_targeted_evidence_real.py` 新增 5 用例（逆序 source
→ ledger 接纳且有序；prompt 带/不带描述；描述截断；node 级描述传递；
gap 读失败 fail-soft）；`tests/integration/test_wave0_work_units.py` 新增
wave0 防御用例；全量 `make verify` 通过、ruff 干净、`openspec validate
--strict` 通过。真实 003 验证 run 待跑（与 BUG-044 修复一并验证）。
