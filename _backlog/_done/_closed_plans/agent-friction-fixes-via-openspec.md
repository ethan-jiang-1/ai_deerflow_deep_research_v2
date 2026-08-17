# Plan: 用最少 OpenSpec change 修复 agent 摩擦点（gate 红 / 文档悬空 / 代码歧义）

> 类型: 设计 | 更新: 2026-08-17

## 背景 / 现状

2026-08-16 的 coding-agent 友善度审查（读完全部关键代码 + 实际跑 gate）确认了约 20 个问题点，全部有实证，分四类：

1. **Gate 在 HEAD 上是红的（最优先）** —— `UV_OFFLINE=1 make verify` 三处独立失败：
   - `lint`：`tests/contract/test_import_boundaries.py:391-392,404-405` 四处 E501（超长字符串字面量，ruff 自动修不了）；
   - `test-assets`：`missing deterministic @impl: PRS-019,SCR-001`（这两个需求 ID 已登记在 `req-registry.yaml:606-607`，但全仓确定性收集集里没有对应 @impl docstring）；
   - `test-integration`：`test_local_entry_environment.py::test_prepared_entries_...` 非封闭——`_copy_harness`（:42）把本机 **gitignored 的 `profiles/`** 整个拷进临时项目，且流程里从不 `profile-init` 就 `profile-check`（干净 clone 上会以 `profile_pair_missing` 失败，本机以 `profile_sqlite_isolation` 失败）。
   - 连带：`.github/workflows/agent-tests.yml:26` 跑的就是 `make verify` → CI 必红。测试内容本身健康（test-fast 2812 全绿，integration 253 过 1 挂）。
2. **文档悬空引用** —— 根 `AGENTS.md:25` + `README.md:9` 指向不存在的 `deerflow/_digest/`（唯一合法的框架理解通道是死路）；`_backlog/README.md:113-124` 锚旧根路径 `/Users/bowhead/ai_deerflow_deep_research/`、`backend/frontend/_digest/_faq_on_digested/reference` 全不存在、分支说法错误（main vs 实际 ethan）；`deep_research_harness/README.md:126` 的 `DEERFLOW_DEMO_MODEL=<profile> make demo-real` 缺 `PROFILE` make 变量必失败。
3. **代码歧义与堆积** —— 双 `attempt_id` 格式（`lifecycle.py:501` 的 `g0-wave0-a1` vs `work_units/ids.py:24` 的 `g0_wave0_w0001_a01`，只有后者匹配 `ATTEMPT_ID_RE`，两边都有生产消费点）；bundle-id 正则 ×6（`bundle.py:55`/`run_observation.py:33`/`lifecycle.py:28`/`work_units.py:57`/`state.py:97`/`tool.py:33`）、`CONTENT_HASH_RE` ×2+别名 `WORK_UNIT_HASH_RE`、`SANDBOX_PATH_RE==BUNDLE_REF_RE`、11 个 phase 列表 ×5；`project_lifecycle_status`（`state.py:1097`，仅测试使用）与 `result_for_state`（`bundle_lifecycle.py:854`）投影互相矛盾；死代码（`engine/work_units/reducers.py`、`graph/routing.py` 整文件，`GATED_FIELDS`、`MAX_FAKE_*`、`dedupe_source_urls`、`serialize/validate_research_state`、`_request_id/_pending_interrupt` 零调用）；误导注释（`middleware.py:69`「None for non-text」实际 `return -1`、`real_gates.py:139` 魔法字符串 vs `publication.py:17` 常量、`gate.py:142` 注释类型错误、`state.py` 模块 docstring 提已删模块）；`research.py` WAVE0/WAVE1 ~60 行拷贝；`builder.py:359` 静默依赖 registry 包序 == topology 序。
4. **测试选择摩擦** —— `postgres` marker 全仓零使用（`make test-postgres` 实测 exit 5「no tests collected」）；`release_e2e` 唯一真实使用在 `tests/scenarios_suspended/evh_024_release_acceptance.py`（文件名不匹配 `test_*.py`，靠不可收集而"死"，meta 断言是「收集不到所以通过」）；`workflow` marker 的测试躺在 `tests/unit/`（`test_node_agent_bridge.py:1158`），`test-unit` 与 `test-fast` 对它选择不一致；`conftest.py:22-42` autouse 全局禁网无文档；`tests/fixtures/` 名字叫 fixtures 但零个 `@pytest.fixture`；13 个测试子目录无 taxonomy 文档；`scripts/check_test_assets.py` 手写 pytest `-m` 解析器 + 嵌套 pytest（`collect_test_catalog.py`）。

**修复原则**：全部走 OpenSpec change；change 数量最小化（每个 change 一个凝聚力主题）；每个 change 红测先行、验证命令明确、`@impl` 溯源；不碰 `deerflow/`。

## 执行状态（2026-08-17 更新）

| Change | 状态 | 说明 |
|--------|------|------|
| 1 `restore-deterministic-verification-gate` | ✅ 完成 | 由另一 agent 拆为两个 change 实施并归档：`2026-08-17-tier-entry-environment-regression`（marker 退役 + 环境封闭化，把 `test_local_entry_environment.py` 迁到 `tests/scenarios_periodic/`，commit `759a12f`）+ `2026-08-17-restore-deterministic-verification-gate`（E501 修复 + PRS-019/SCR-001 @impl + EVH-031，commit `252a0ad`）；另补格式清扫 chore `08ce2cc`。gate 在 HEAD 全绿 |
| 2 `fix-agent-facing-documentation-integrity` | ✅ 完成 | propose（另一 agent）→ polish（补 openspec/README 措辞、contract 文件落点、反耦合断言）→ apply（AGENTS.md/README/_backlog/openspec/run README 修正 + 新增 `tests/contract/test_documentation_integrity.py`、`test_test_surface_orientation.py` + DPL-012 契约同步）→ 归档 `2026-08-17-fix-agent-facing-documentation-integrity` → commit `e176975` |
| 3 `single-source-runtime-identifiers-and-retire-dead-code` | 🔄 进行中 | propose + polish ready（skip_specs）；apply 主体完成：`domain/identifiers.py` 单源（LogicalPhase 迁入 + 正则 + `LOGICAL_PHASE_NAMES`）、`make_attempt_id`→`make_node_visit_id` 改名、5 处 phase 列表与 6 处正则收敛、删除 `project_lifecycle_status`/`GATED_FIELDS`/`MAX_FAKE_*`/`dedupe_source_urls`/`_request_id`/`_pending_interrupt`/`reducers.py`/`routing.py`（含 toml 注册同步）、WAVE0/1 policy 去重、4 处注释修正；红测 `tests/contract/test_identifier_single_sourcing.py` 4/4 绿；gate 验证进行中（test-assets 已绿）。**apply 决策修正**：`serialize_research_state`/`validate_research_state` 保留（state serde 规范测试缝，支撑 `test_state_bounds` 边界不变量） |
| 4 `split-domain-state-authority`（可选） | ⏸ 未排期 | Change 3 落地后按需续开 |
| 收尾 | ⏸ 待办 | 全部 change 归档后：plan `git mv` 至 `_done/_closed_plans/`（CLS-044，追加到最下面）+ 三处 README 同步 |

## 决策 / 方案

### 3 个核心 change + 1 个可选 follow-up

**Change 1 — `restore-deterministic-verification-gate`（验证门禁恢复为绿且诚实）**

- Scope：
  - `test_import_boundaries.py` 四处 E501：字符串字面量改拼接或加 `noqa: E501`（apply 时选一处，优先改拼接）。
  - 给 PRS-019、SCR-001 补确定性 `@impl` docstring：放在各自归属的确定性测试文件（`tests/contract/test_scripted_real_debug_command.py` 与路径/放置契约测试），跑到 `make test-assets` 绿。
  - 修 `test_local_entry_environment.py` 封闭性：`profile-check` 前先 `profile-init PROFILE=demo`，或 `_copy_harness` 只拷贝 git-tracked 的 profiles 内容——apply 时选一，以「干净 clone 上能绿」为验收。
  - 退役死 marker：`postgres`（删 marker 注册、`test-postgres` target、`test_lane_selection`/`test_test_structure_retirement` 等 meta 字符串断言同步）；`release_e2e`（二选一：把 `evh_024_release_acceptance.py` 改名 `test_evh_024_...py` 使其作为 suspended 材料可收集，或整体退役 marker + conftest 逃生口 + meta 断言同步——倾向改名，保留 suspended 材料的可见性）。
- 决策要点：postgres 是「声明了但从未接线」的假门，Postgres 服务本就被 openspec tech-stack 决策推迟，退役比留一个 exit-5 的门诚实。
- Seam classification：`deterministic-guardrail`（验证系统的行为修正，不碰运行时）。
- Evidence seam：`UV_OFFLINE=1 make verify` 全绿；`make test-postgres` 不再存在或按新语义可跑。
- 为什么并入一个 change：三处失败同属「验证系统」，是 agent 每天第一脚就踩的坑；meta-tests 的字符串断言会被 marker/target 改动波及，放一个 change 一次性同步，避免两次评审同一个文件面。

**Change 2 — `fix-agent-facing-documentation-integrity`（文档引用与命令修正）**

- Scope：
  - 根 `AGENTS.md:25` / `README.md:9`：`deerflow/_digest/` 悬空引用改为指向实际存在的只读参考（`deerflow/AGENTS.md` → `deerflow/backend/AGENTS.md`），并明说「研究笔记不随 submodule 分发」。
  - `_backlog/README.md`：旧根路径改 `..._v2`；`backend/frontend/_digest/_faq_on_digested/reference` 行改为 `deerflow/backend`、`deerflow/frontend`、`deerflow/_digest`（不存在则删除该行并说明）、`_reference/`；分支说法统一 ethan；头部日期更新。
  - `deep_research_harness/README.md:126`（及 135）：`DEERFLOW_DEMO_MODEL=... make demo-real` → `make demo-real PROFILE=demo ...`（与 `local-operations.md:20` 一致）。
  - 根 `README.md:34`：`demo-real-scripted` 措辞从「真实流程」改为 embedded-smoke 校准（与 Makefile 注释一致）。
  - `openspec/README.md:7`：「changes/ holds active proposed deltas」措辞按现状（当前 0 活跃）微调。
  - `docs/testing-and-evaluation.md` 补三节说明，把测试摩擦变成文档事实：测试目录 taxonomy（13 个目录各自语义 + 新增测试放哪）、`conftest.py` autouse 全局禁网及其逃生口（`requires_llm`/`release_e2e` marker）、`tests/fixtures/` 是 helper 模块而非 pytest fixture。
- 决策要点：测试摩擦里「命名误导」类问题（fixtures 无 fixture、禁网无文档、目录无 taxonomy）成本最低的修复是**文档化而非重命名/重构**——重命名 `tests/fixtures` 会波及 70+ import，收益低于成本，不选。
- Seam classification：`wiring`（纯文档 + 一处命令示例修正，无运行时行为变化）。
- Evidence seam：无行为变化；验证 = `make governance` 过 + 附机械核对清单（grep 全部 md 中的相对路径是否存在于磁盘）。

**Change 3 — `single-source-runtime-identifiers-and-retire-dead-code`（标识符单一来源 + 死代码退役）**

- Scope（一个 Focus Card，owner = `domain/`；两组任务）：
  - 标识符权威：统一双 `attempt_id`（apply 时二选一：node-visit id 改名 `visit_id`，或统一格式——**硬约束：不改变任何已持久化/已观察值的格式**，`RunEvent.attempt_id`/`agent_context` 是观察记录，格式若变会破坏既有数据兼容，故倾向改名而非改格式；apply 前先列全消费点兼容矩阵）；bundle-id/content-hash/sandbox-path 正则与 11 个 phase 列表收敛到一个 domain 常量模块，删 5-6 份拷贝；修投影矛盾（`project_lifecycle_status` 仅测试使用且与真实投影冲突 → 删除函数及其测试，或与 `result_for_state` 对齐，倾向删除）；`builder.py:359` 顺序检查改为单一来源 + 可读报错。
  - 清理：删 `engine/work_units/reducers.py`、`graph/routing.py`、`GATED_FIELDS`、`MAX_FAKE_*`、`dedupe_source_urls`、`serialize/validate_research_state`（降为 internal 或删）、`_request_id/_pending_interrupt`；修正 `middleware.py:69`/`gate.py:142`/`state.py` 模块 docstring；`real_gates.py:139` 改用 `FINAL_DELIVERY_GATE_VIEW_KEY`；`research.py` WAVE0/WAVE1 合并为一个参数化 worker policy 工厂。
- 决策要点：这是唯一含语义决策的 change（attempt_id 的命名/格式），其余全是机械收敛；2800+ 确定性测试是安全网。
- Seam classification：`deterministic-guardrail`（标识符/常量/投影，无 LLM 行为）。
- Evidence seam：`make verify` 全绿；每项删除先有 grep 零调用证明（含 `tests/assets`、`scripts/` 与动态引用排查）。
- 为什么并入一个 change：全部是「单一来源 + 删除」的机械收敛，同属 `domain/` 权威面；拆开反而让评审重复看同一批文件。

**Change 4（可选 follow-up）— `split-domain-state-authority`（巨型文件拆分）**

- Scope：`domain/state.py`（1851 行）按责任拆分（BundleLocalState / ResearchGraphState / ResearchState / reducers / 序列化）；`domain/work_units.py`（1416）、`runtime/bundle_lifecycle.py`（1259）、`graph/nodes/hitl1/node.py`（1108）随后同批或后批。
- 为什么单列且排最后：纯机械搬移但触碰全仓 import 面，风险最高、独立评审价值大；与 Change 3 分离可避免一个 change 混入高风险结构变动。Change 3 落地顺利即可续开。

### 备选（考虑过但不选）

- 每个问题单独开 change（~15 个）→ 违反「少量 change」目标，评审与归档成本 ×15。
- Change 3+4 合并 → 一个 change 混「语义收敛」与「结构搬移」，评审面失控。
- 用 Program Focus 形式做多 workstream → 语法/预算成本高于收益；三个 change 各有单一语义核心，不需要。

## 风险 / 取舍

- [attempt_id 统一时改错格式，破坏持久化/观察数据兼容] → 缓解：硬约束「不改变已持久化值格式」，倾向改名而非改格式；apply 前列消费点兼容矩阵；红测先行。
- [meta-tests 精确字符串断言连锁失败] → 缓解：Change 1 内部一次性同步 Makefile/pyproject/conftest 与其 meta 断言；改完先跑 contract 段。
- [删死代码误删仍被动态引用（getattr/importlib/字符串路由）] → 缓解：每项删除前 grep 全仓含 `tests/assets`、`scripts/`；动态引用场景专项排查。
- [文档修复后仍漏新悬空引用] → 缓解：Change 2 验收含「grep 全部 md 相对路径是否存在于磁盘」的机械核对清单。
- [三 change 并行评审导致冲突] → 缓解：串行执行 1 → 2 → 3；1 是地基，3 依赖 verify 绿才有安全网。

## 落地关联

| Change 名称（slug） | 主题 | 打开时机 | 验证命令 | 归档前置（config.yaml tasks 规矩） |
|---|---|---|---|---|
| `restore-deterministic-verification-gate` | gate 绿 + 测试选择诚实 | 立即 | `UV_OFFLINE=1 make verify` 全绿；`make test-assets` 绿 | `openspec validate <name> --strict`；`git diff HEAD --check`；gitlink/submodule 状态证据 |
| `fix-agent-facing-documentation-integrity` | 文档引用/命令修正 + 测试摩擦文档化 | Change 1 归档后 | `make governance` 过；路径核对清单 | 同上 |
| `single-source-runtime-identifiers-and-retire-dead-code` | 标识符单一来源 + 死代码退役 | Change 2 归档后 | `make verify` 全绿；grep 零调用清单 | 同上 |
| `split-domain-state-authority`（可选） | 巨型文件拆分 | 按需 | `make verify` 全绿 | 同上 |

打开每个 change 时：proposal 带 `## Change Focus`（Primary module / Seam classification / Question / Necessary adjacent contracts / Evidence seam / Not in scope / Triggered review policies——Change 3 因投影退役触发 `authority-and-projections`，其余以 `change-admission` 为主）；tasks.md 逐项红测先行 + 每项标 `@impl`；清理项**能复用既有需求 ID 就不新增 ID**，保持 req registry 只增不删的节俭。

## 执行纪律（用户确认，2026-08-17）

1. **每个 change 的固定流水线**：`openspec-propose` 生成提案 → 紧跟 `/polish-openspec-change` 打磨（按 skill 要求多轮风险导向 review，修正所有可由既有事实确定的缺陷，不臆造决策）→ 直到 `ready for apply`（`openspec validate --strict` + `git diff --check` 全过、无未决矛盾）→ 才执行 apply。**没有 polish 到 apply-ready 绝不 apply。**
2. **每个 change 归档后立即主动提交**（`git add` + `git commit`，含 change 目录与实现改动），一个 change 一个 commit，不攒批；提交信息遵循仓库惯例（如 `feat:`/`fix:`/`docs:` 前缀 + 一句话）。
3. **计划完成收尾**：3（+1 可选）个 change 全部落地并归档后，本 plan 文件 `git mv` 到 `_backlog/_done/_closed_plans/agent-friction-fixes-via-openspec.md`（**追加到最下面**），并同步更新 `_done/_closed_plans/README.md`（分配 CLS-044）、本目录 README（删活跃行）、`_done/README.md`（closed 计数 +1）。
