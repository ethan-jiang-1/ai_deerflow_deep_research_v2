## Context

See proposal.md — Why. 现状事实（2026-08-17 实测）：`make verify` 在 HEAD 上失败于 lint（`test_import_boundaries.py` 4 处 E501）、test-assets（PRS-019/SCR-001 无确定性 `@impl`）、test-integration（`test_local_entry_environment.py` 拷贝本机 gitignored `profiles/` 后 `profile-check` 失败）。`postgres` marker 全仓零使用（`make test-postgres` exit 5）；`release_e2e` 的唯一真实使用文件 `scenarios_suspended/evh_024_release_acceptance.py` 因文件名不匹配 `test_*.py` 而不可收集。测试内容本身健康：test-fast 2812 全绿、integration 253 过 1 挂。

## Goals / Non-Goals

**Goals:**
- `UV_OFFLINE=1 make verify` 在干净 checkout 上全绿（lint / test-assets / test-integration / test-workflow 全过）。
- 测试选择语义单一来源：`tests/assets/selection.py` 三常量 ↔ Makefile `-m` 表达式 ↔ contract 断言三者一致，且不再引用已退役 marker。
- suspended release 材料对收集工具可见（可收集、被 marker 排除），不再靠文件名隐身。
- integration 环境测试不再依赖任何本机 gitignored 状态。

**Non-Goals:**
- 不接 Postgres 测试服务、不移除 `postgres-test` extra（tech-stack 决策仍推迟）。
- 不改 `release_e2e` marker 本身、conftest 逃生口、`requires_llm` marker。
- 不清理其他 lint 债务、不重构测试目录、不碰 `tests/fixtures/` 命名、不动 `src/` 与 `deerflow/`。
- 不新增「clean-checkout gate 绿」之外的运行时行为要求。

## Decisions

**D1. E501 修复用字符串相邻拼接，不用 `noqa`。**
- 为什么不是 noqa：`test_import_boundaries.py` 是「manifest 精确字符串」契约测试，其长字符串必须保持字面值；noqa 会把 4 行例外永久留在 lint 里，而拼接零成本且保持 line-length 政策完整。备选「提升 line-length」被否（会放宽全仓标准）。

**D2. `postgres` marker 退役（删）而不是接线。**
- 为什么退役：Postgres 服务被 tech-stack 决策推迟，marker 声明三年无人用，`make test-postgres` 稳定 exit 5「no tests collected」——这是假门。接线需要引入 Compose 服务与测试基建，远超本 change 主题。备选「保留并文档化」被否：一个必然失败的 target 对 agent 是持续摩擦。
- 引用面（已枚举，全部在本 change 内同步）：pyproject marker 注册（:52）；Makefile `test`（:114）、test-fast（:120）、test-integration（:152）、test-workflow（:157）四处 `-m` + `test-postgres` target（:192-196）；`scripts/benchmark_fast.py:19`；`tests/assets/selection.py:6,16,20`（单一来源常量）；`tests/contract/test_test_lane_selection.py:33-36`（常量断言）；`tests/contract/test_verification_gate_contract.py:55`（Makefile 原文断言）；`tests/assets/inventory.py:45,49`（VerifiedLane 数据行）。

**D3. `release_e2e` 改文件名使其可收集，而不是退役 marker。**
- 为什么改名：suspended 材料是「保留的 suspended 诊断材料」，marker 语义（requires_llm + release_e2e）仍然正确且被 conftest 逃生口使用；问题只是文件名意外不匹配收集规则，导致 `test_test_structure_retirement.py:63` 的「收集为空」断言是「收集不到所以通过」的假绿。改名后断言改为「suspended 材料被收集、被 lane 排除」——真绿。备选「退役 marker」被否：会删掉 conftest 逃生口的一个分支并扩大 diff 面。
- 连带（已枚举，全部在本 change 内同步）：`test_release_suspension.py:18,32-33`（SUSPENDED_SELECTOR 常量含旧文件名、is_file 断言、收集为空断言）、`test_test_structure_retirement.py:63`、`test_test_lane_selection.py:112-113` 的「release_e2e 收集为空」断言改为「收集到 suspended 选择器」；`scenarios_suspended/README.md` 如提及文件名则校对。

**D4. 非封闭 integration 测试改为「测试内构造 profile」，而不是删步骤或只拷 tracked 文件。**
- 为什么构造：该测试断言「prepared entries 保持依赖状态」（含 `profile-check` 作为 prepared entry），删步骤会丢覆盖；「只拷 git-tracked profiles」在干净 checkout 上没有 profile 可拷，`profile-check` 仍会以 `profile_pair_missing` 失败。构造方案：在拷贝项目里写 `profiles/demo/config.yaml`（`database.backend: sqlite` + 指向该 profile 隔离目录的绝对 `sqlite_dir`、无 checkpointer 段）与 `extensions_config.json`，复用 `tests/contract/test_local_profiles.py` 已验证的 profile 形状——确定性、与机器无关。备选「先 profile-init」被否：profile-init 依赖根 config.yaml（gitignored，CI 上不存在）。
- 注意：`_copy_harness` 仍会拷贝本地 `profiles/`（copytree 无 ignore）——测试改为**不依赖其内容**（构造自己的），可顺手把 `profiles` 加入 ignore_patterns 使拷贝面更干净（低风险，列为任务可选）。

**D5. `@impl` 补位遵循「归属 + checker 即 oracle」。**
- SCR-001（operator-only composition root 标签）→ `tests/contract/test_scripted_real_debug_command.py` 模块 docstring（已有 SCR-003/004/005，同族补位）。
- PRS-019（canonical harness 路径、无生产包发现）→ `tests/contract/test_import_boundaries.py`（manifest/路径契约测试，已有 PRS-001..018 族）或 `tests/integration/test_scripted_real_workflow_debug.py`——apply 时以哪个文件的断言真正覆盖该声明为准，`make test-assets` 是验收 oracle；若两者都不覆盖，则在该契约测试里补一条断言再标记。
- 不新增需求 ID：PRS-019/SCR-001 已 alive，只补实现标记。

## Risks / Trade-offs

- [D2 改动面大：Makefile 表达式 ↔ selection.py 常量 ↔ contract 断言三处不同步导致 test-fast 红] → 缓解：同一次编辑内完成全部引用面（引用清单已在 D2 枚举）；改完先跑 contract 段再跑 test-fast。
- [D3 改名后 suspended 文件被 `pytest tests`（test-workflow 用 `-m workflow...`）以外的方式收集，影响其他收集面] → 缓解：文件带 `requires_llm`+`release_e2e` 双 marker，所有确定性 lane 都排除它；改名前后跑 `pytest tests/scenarios_suspended --collect-only` 对比验证。
- [D4 构造的 profile 与真实 profile-init 产物形状漂移] → 缓解：复用 `test_local_profiles.py` 已验证的配置形状；隔离检查（absolute sqlite_dir == profile 目录）是本机无关的纯函数。
- [D5 选错 @impl 归属文件，checker 仍红] → 缓解：checker 是 oracle，迭代到绿；归属规则「哪个确定性测试真正断言该声明」优先于就近补位。
- [E501 拼接改写引入转义错误，字面值变化导致契约测试行为漂移] → 缓解：拼接必须保持字符串最终值逐字节不变；改后跑 `test_import_boundaries.py` 单文件。

## Migration Plan

无运行时迁移：本 change 只动测试/验证/文档接线面。回滚 = revert 对应提交（无数据迁移、无 schema 变化）。部署顺序：apply 顺序即任务顺序（红测 → 修复 → 同步 → 全量 verify）。

## Open Questions

无——所有决策在 D1-D5 中已定，均可安全执行；apply 中如发现新引用面（如 inventory.py 的其他数据行依赖旧表达式），按 D2 的「同一 change 内全量同步」原则处理。
