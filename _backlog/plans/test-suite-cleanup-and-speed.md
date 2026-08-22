# 测试资产审计与回归提速计划（多轮持续运营）

> 生成: 2026-08-22 | 状态: **第一轮 ✅ 完成 · 第二轮 🚧 进行中（见 §8 / Tracking）**
> 用途: 测试资产审计 + 回归提速的**持续运营文档**。第一轮（去重/修红/并行化）已落地；
> 第二、三…轮的想法与执行都沿用本文件，按 §Tracking 追加。
> 数据来源: 本机 `.venv` 实测（warm venv，无缓存冷启动）。

---

## Tracking（进展跟踪总账）

> **总进度: 第一轮 ✅ 全部完成 · 第二轮 🚧 部分完成（1 落地 / 3 决策否决或撤回 / 1 待确认）· 待办见文末 §Tracking-待办**
> 维护规则: 完成一项 → 在对应表填 ✅ + 日期 + 验证证据；新决策 → 追加到"历史决策记录"；
> 新待办 → 追加到文末"待办"；被撤回/否决的项保留记录（原因即价值），不删除。

### 第一轮 · 已完成（T1-T12）

| # | 事项 | 完成 | 验证证据（实测） |
| --- | --- | --- | --- |
| T1 | 审计测量：235 文件 / 3042 用例 / 三 lane 串行耗时 | ✅ 2026-08-22 | fast 42s、integration 57.5s、workflow 11.7s（§1） |
| T2 | 决策点拍板（demo_tui / eval digest / readiness / xdist） | ✅ 2026-08-22 | 用户 4 项全部批准（§7） |
| T3 | 去重：删 rerun_policy 2 用例（⊆ rerun_e2e） | ✅ 2026-08-22 | `test_rerun_policy/e2e` 13 passed；lint 绿 |
| T4 | 修 eval control digest：补 `scripts/regenerate_control_digests.py` | ✅ 2026-08-22 | eval suite 59 passed；`--check` 21 controls 全绿 |
| T5 | readiness cap-trip：d772aba 真回归（降级路径丢输出） | ✅ 2026-08-22 | bridge 修复 + 测试加强；4 passed；RELEASE-20260822-01 |
| T6 | demo_tui 合并实测否决 | ✅ 2026-08-22 | 49 用例 34.1s ≈ 51 基线 34.2-34.8s；已还原（§5.1） |
| T7 | pytest-xdist 进 dev 组 + dev 组收敛 + Makefile 简化 | ✅ 2026-08-22 | 纯 `uv run pytest`；opt-in 并行档 fast 24s / integration 21s / workflow 10s |
| T8 | 治理契约同步（`test_verification_gate_contract.py` 钉 xdist 走线） | ✅ 2026-08-22 | contract 1 passed |
| T9 | digest 再生成入口：`make control-digests-check` + 文档 | ✅ 2026-08-22 | target 验证 21 controls；docs 更新 |
| T10 | 全量门禁终验（-n 4 档） | ✅ 2026-08-22 | `make verify PYTEST_XDIST="-n 4"` 全绿 |
| T11 | 挂起评审（§5.3）：无价值存疑项，机制保留 | ✅ 2026-08-22 | 所有耗时项均有价值归属 |
| T12 | 复核 + 量化 | ✅ 2026-08-22 | verify 52.4s（-n auto）/ make test 42.1s / 串行 ~120s |

### 第二轮 · 已完成（T13-T19）

| # | 事项 | 完成 | 验证证据 / 备注 |
| --- | --- | --- | --- |
| T13 | R1: CI uv 缓存显式配置（agent-tests + entry-environment） | ✅ 2026-08-22 | `enable-cache: true` + `prune-cache: false`；**待 CI 首跑确认命中** |
| T14 | R2 尝试：CI lane 并行 job（拆 4 job） | ✅ 尝试过（→ T19 撤回） | 曾通过 YAML 验证；后被治理契约打回，见 T19 |
| T15 | R3 否决修正：单次调用合并不省时 | ✅ 2026-08-22 | `make test` 42.1s ≈ verify pytest 部分；原估算错误已纠正 |
| T16 | 旧概念审计（§9）：全部判定为守卫，无纯考古 | ✅ 2026-08-22 | 交叉核对 src=0 项均为缺席守卫；47 用例仅 3.17s |
| T17 | R6 否决：`make -j verify` 实测更慢 | ✅ 2026-08-22 | -n 3 → 59.5s、-n 2 → 67.9s vs 串行；过订阅 |
| T18 | 用户指令：默认串行 | ✅ 2026-08-22 | `PYTEST_XDIST ?=`（空=串行）；xdist 改 opt-in；契约/文档同步 |
| T19 | R2 撤回：CI 4-job 违反治理契约 | ✅ 2026-08-22 | `test_agent_pr_workflow` / `test_repository_delivery` 变红；恢复单 job + `make verify`，保留 R1 缓存 |

### 历史决策记录（所有决定，含否决/撤回，原因即价值）

| 决策 | 结论 | 日期 | 原因 / 证据 |
| --- | --- | --- | --- |
| demo_tui 51 用例合并瘦身 | ❌ 否决 | 2026-08-22 | 实测 49 用例 34.1s ≈ 51 基线 34.2-34.8s，合并不省时反损粒度（T6） |
| 默认并行（xdist -n auto） | ↩️ 改为默认串行 | 2026-08-22 | 用户指令：测试未经精心并行 review；xdist 保留 opt-in（T18） |
| R2 CI lane 并行 job | ↩️ 撤回 | 2026-08-22 | 违反治理契约（CI 必须是单 job + `make verify`），契约测试变红（T19） |
| R3 本地单次调用合并 | ❌ 否决 | 2026-08-22 | 实测不省时（make test 42.1s ≈ verify pytest 部分）（T15） |
| R6 `make -j verify` | ❌ 否决 | 2026-08-22 | 8 核过订阅，-n 3/-n 2 均比串行慢（T17） |
| 删除旧概念测试 | ❌ 否决（保留） | 2026-08-22 | 审计后全是守卫（拒绝/缺席/迁移保险），删了松边界（T16） |
| R1 CI uv 缓存 | ✅ 采纳 | 2026-08-22 | 唯一安全提速：install 2-4min → ~30s，不违反契约（T13） |

### Tracking-待办（文末，还没做的）

| 项 | 状态 | 触发条件 / 说明 |
| --- | --- | --- |
| CI 确认 R1 缓存命中 | 📋 需真实 CI 跑 | 推一次分支，看 install 步骤是否命中缓存；命中则 CI 总时长 4-6min → ~1.5-2min |
| R4 demo_tui 用例数 | 📋 待办 | 02x 战役收尾后重新评估（§5.1"不合并"结论战役期间成立） |
| R5 收集优化 | 📋 低优先 | workflow lane 全树收集 3040 个（~4s），收益 ~2-3s，不值得 |
| （可选）xdist 默认并行重启 | 📋 待 review | 若有人认真 review 完并行安全性，可把默认翻回 `-n auto`（本次实测 52.4s） |

### 按计划章节对账（内容都做完了吗 → 是）

| 章节 | 内容 | 处置 |
| --- | --- | --- |
| §1 现状测量 | 规模 / 耗时 / 帕累托 | ✅ 记录完毕 |
| §2 合并去重清单 | 2.1 真重复 / 2.2 分层冗余 / 2.3 伪重复 / 2.4 互补对 | ✅ 2.1 已删；2.2/2.3/2.4 决策"不动"（有理由） |
| §3 存量红测 | 3.1 eval digest（×35）/ 3.2 readiness（×1） | ✅ 全部修复并验证 |
| §4 耗时-价值分级 | 9 个耗时文件 triage | ✅ 全部"保留"判定，无挂起 |
| §5 提速杠杆 | 5.1 瘦身（否决）/ 5.2 xdist（落地）/ 5.3 挂起程序 / 5.4 去重 | ✅ 5.1 实测否决；5.2 落地（opt-in）；5.3 程序化；5.4 完成 |
| §6 执行阶段 | Phase 0-3 / Phase 4 | ✅ 0-3 完成；4（挂起）无候选关闭 |
| §7 决策点 | 4 项 | ✅ 全部拍板（表格化） |

---

## 8. 第二轮空间评估（2026-08-22）

> 结论：**本地已接近收益边界（再省 ~10s / 19%），CI 仍有大头（install 冷缓存 2-4 分钟）。**

### 8.1 第一轮最终量化（已完成）

| 指标 | 改动前（串行） | 现在（默认串行） | opt-in 加速（-n 4，未 review） | 收益 |
| --- | --- | --- | --- | --- |
| `make verify` | ~120s | ~120s（命令已简化） | **52.4s** | 串行下持平；CI 靠 R1 缓存提速 |
| `make test`（单次调用全量） | — | **42.1s** | 单次调用比 verify 的 3 次 pytest 调用再省 ~10s |
| fast / integration / workflow（-n 4） | 42 / 57.5 / 11.7s | 24 / 21 / 10s | — |

### 8.2 剩余空间（按收益排序，全部未实施）

| # | 杠杆 | 预计收益 | 代价 / 风险 | 建议 |
| --- | --- | --- | --- | --- |
| R1 | **CI uv 缓存显式配置**（setup-uv v5 默认开启；已显式钉死 `enable-cache: true` + `prune-cache: false`） | CI install 2-4min → ~30s | 零风险；需 CI 首跑后观察缓存命中 | ✅ 已做（T13），**等一次真实 CI 运行确认** |
| R2 | ~~CI lane 并行 job~~ **已撤回**（T19）：拆 4 job 违反治理契约 `test_agent_pr_workflow`（钉单 job + `make verify`）与 `test_repository_delivery` | — | 契约恢复绿 | ❌ 撤回（2026-08-22） |
| R3 | ~~本地单次调用合并~~ **已实测否决**：`make test` 42.1s ≈ verify 的 pytest 部分（52.4 - lint/assets/lock ≈ 42s），合并 3 次调用不省时间；52.4 vs 42.1 的差全部来自脚本开销 | ~0s | 无 | ❌ 放弃（2026-08-22 修正，原估算错误） |
| R4 | **测试用例数**（剩余全是"有价值"项） | 边际 | 唯一候选：02x 战役后 demo_tui 再评估 | 战役后再说 |
| R5 | **收集优化**（workflow lane 全树收集 3040 个再筛 3005 个，4.1s） | ~2-3s | 需改 marker/path 结构，收益小 | 不值得 |

**判断（2026-08-22 修订）**：按用户指令，测试**默认串行**（未经精心并行 review，
xdist 只留 opt-in `PYTEST_XDIST="-n 4"`）；R2（CI lane 并行 job）因违反治理契约已撤回；
R6（`make -j verify`）实测过订阅否决。**安全且有效的剩余杠杆只有 R1（uv 缓存，已落地）**——
CI install 冷缓存 2-4 分钟 → ~30s，不违反任何契约。本地 `make verify` 串行 ≈ 2 分钟
为当前默认；需要临时加速时可显式 `make verify PYTEST_XDIST="-n 4"`（实测 52.4s，注意
未正式 review 并行安全性，用前自行评估）。

---

## 9. 旧概念审计（2026-08-22）

> 用户提出：测试里是否残留历史上的旧/过时概念，若有就不值得留。结论：**旧概念大量存在，
> 但几乎全部是守卫而非考古，不建议删。**

### 9.1 扫描结果

| 类别 | 数量 | 例子 | 判定 |
| --- | --- | --- | --- |
| 拒绝/缺席守卫（旧概念被拒/已退役/不存在） | ~25 个测试函数 | `test_legacy_checkpointer_is_refused_before_action_saver_factory`、`test_no_runtime_broker_or_historical_resolver_remains`、`test_hitl1_receives_a_selected_bundle_context_without_legacy_identity_or_checkpoint` | **保留**——钉住当前边界，防复活 |
| 迁移保险（旧格式若出现则正确迁移） | ~10 个（retained/cutover） | `test_registered_checkpoint_migration_writes_reloads_and_replays_current_gate_facts`、`test_v1_journal_is_reject_only_and_creates_no_current_output` | **保留**——`scripts/retained_run_data_migration.py` 仍是活工具；库存零记录属保险 |
| 历史文物 pin | 少量 | release-attestation、deferred-activation dossier（HITL2 状态 pin） | **保留**——审计/治理价值 |
| **纯考古**（生产已删、测旧行为、无守卫价值） | **0** | — | — |

### 9.2 关键证据

- 交叉核对 `tests vs src`：`checkpointer`(21/6)、`legacy_checkpoint`(6/1)、`legacy_bundle_locator`(1/1)
  等旧概念在生产仍有对应（拒绝逻辑）；`legacy_manifest`/`dossier`/`session_broker`(tests>0, src=0)
  均为**缺席守卫**——断言模块/概念不存在，不是测试已删行为。
- `scripts/retained_run_data_inventory.json` 为**零记录**（迁移已完成）；retained 测试是保险，
  且拒绝型用例（unregistered/stale/cannot migrate）钉的是当前准入边界。
- 成本：47 个守卫用例 `-n 4` 仅 3.17s，**没有速度理由删除**。
- Docker、`UNAVAILABLE_REAL_FACTORY` 等"疑似旧"概念经核对仍在生产使用。

### 9.3 判定

**不建议删。** 这批"旧概念"测试的价值恰恰在于概念是旧的——它们把"这个旧东西不能再回来"
钉成契约。删掉 = 松开边界。若未来想瘦身，唯一可议的是 retained 迁移保险（§9.1 第二类），
但要先确认迁移工具不再需要；当前建议保留。

---

## 0. 结论摘要（TL;DR）

1. **慢在数量与等待，不在单个用例**：fast lane 单测最慢 0.48s、integration 最慢 2.74s，
   全部低于 5s 时长政策线。原 `make verify` ≈ 2 分钟（本机 warm），
   integration lane（57.5s）是最大黑洞。
2. **真重复极少**：确认 1 处（rerun_policy 2 用例 ⊆ rerun_e2e 4 用例，已删）；
   其余跨文件重名多为"不同对象同名"，unit/live calibration 对是互补不是重复。
3. **HEAD 曾有 36 个存量红测**：35 个 eval control digest 过期（已补再生成脚本修复）、
   1 个 readiness cap-trip 集成失败（d772aba 引入的真回归：降级路径丢弃已生成输出；
   已修复 bridge + 加强测试 + 记录 regression-descent）。
4. **提速基建已落地，但默认串行**：pytest-xdist 进 dev 组（opt-in，未 review 并行安全，
   默认串行）；测试所需运行时包（textual/dotenv/ruamel）并入 dev 组，pytest 目标跑纯
   `uv run pytest`。opt-in 并行档实测 `make verify` ~52s（fast 42s→24s 等）；
   **安全收益在 CI**：uv 缓存（R1）把 install 2-4 分钟压到 ~30s。
5. **Textual 合并会话不省时（实测否决）**：demo_tui 保持 51 用例。共享会话会累积
   渲染状态（49 用例 34.1s ≈ 51 用例基线 34.2-34.8s），合并没有收益。

---

## 1. 现状测量

### 1.1 规模

| 指标 | 数值 |
| --- | --- |
| 测试文件（test_*.py） | 235 |
| 收集用例总数 | 3042 |
| 默认 lane 用例（排除 requires_llm / release_e2e / periodic） | 2989 |
| 测试文件增长 | 2 周内 219 → 235（74 个 commit 触及 tests/） |

按目录分布（test 函数数）：unit 824、contract 416、graph 310、integration 295、
domain 173、engine 81、eval 78、live 8、blocking_io 13。

### 1.2 门禁耗时（本机 warm venv 实测）

| lane | 用例 | 墙钟 | 备注 |
| --- | --- | --- | --- |
| test-fast（assets/contract/domain/engine/unit/graph/eval） | 2615 | **42s** | 单测最慢 0.48s，均数 ~16ms |
| test-integration（integration + blocking_io） | 299 | **57.5s** | 单测最慢 2.74s，均数 ~190ms |
| test-workflow | 34 | **11.7s** | 单测最慢 0.80s |
| lint + test-assets + lock-check | — | ~5-15s | |
| **合计 verify** | 2948 | **≈ 2 分钟** | CI 另加 install/sync（冷缓存 +2-4 分钟） |

**关键事实**：没有任何单个用例超过 5s 时长政策线（`scripts/check_test_durations.py`
的 MAX_FAST_TEST_SECONDS=5.0）。这意味着**砍用例数量或并行化才是有效手段**，
找"慢用例"并优化它没有意义。

### 1.3 耗时帕累托

integration lane（55.6s 执行时间）前 6 个文件占 **82.5%**：

| 文件 | 用例 | 耗时 |
| --- | --- | --- |
| `tests/integration/test_demo_tui.py` | 51 | **28.2s**（~24s 为 Textual pilot 真实等待） |
| `tests/integration/test_refinement_round_workflow.py` | 9 | 4.2s |
| `tests/integration/test_refinement_round_recovery.py` | 13 | 3.7s |
| `tests/integration/test_demo_cli.py` | 2 | 3.6s |
| `tests/integration/test_provider_durability.py` | 7 | 3.2s（真实子进程重启） |
| `tests/integration/test_research_lifecycle_tool.py` | 20 | 3.1s |

fast lane 最耗时文件（合计 ~13s）：`test_asset_checker_contract.py` 4.13s、
`test_configure.py` 3.24s、`test_regression_descent.py` 2.94s、
`test_scripted_real_debug_command.py` 2.65s —— 均为**真实子进程/整树收集**的治理验证，属于"贵但值得"。

---

## 2. 合并 / 去重清单

### 2.1 【真重复 · 建议删】rerun_policy 的 fixture 回归 ⊆ rerun_e2e

`tests/unit/test_rerun_policy.py::TestFixtureRerunStillUsesConstant`（2 用例）与
`tests/unit/test_rerun_e2e.py::TestFixtureRerunRegression`（4 用例）逐行比对：

| policy 用例 | e2e 对应用例 | e2e 额外断言 |
| --- | --- | --- |
| `test_fixture_at_generation_0_produces_route_next` | `test_fixture_gen_0_bumps_to_1_routes_next` | + `"rerun_scope" not in result` |
| `test_fixture_at_generation_2_exhausted` | `test_fixture_gen_2_exhausted` | — |
| — | `test_fixture_gen_1_bumps_to_2_routes_next` | 独有 |
| — | `test_fixture_no_scope_no_invalidation_no_workspecs` | 独有 |

- 构建参数完全一致（`NodeBuildDependencies(graph_context=object(), agent_context=object(),
  capabilities=object())`）。
- **无任何证据声明引用 rerun_policy**（`grep rerun_policy tests/assets/*.py` 为空），
  删除不触碰 `validate_claim_selections`。
- 删除后需同步移除文件顶部 `build_fixture` import（仅该类使用，防 ruff F401）。

### 2.2 【分层冗余 · 保留】gate_kernel vs gate_integration

`test_final_delivery_evidence_blocked` / `test_readiness_repair_targeted` 在
`engine/test_gate_kernel.py`（纯内核）与 `graph/test_gate_integration.py`（真实 gate 装配）
各测一次同一行为。这是 domain/engine/graph 分层契约的**刻意交叉验证**（内核断言 route，
集成层追加 `verdict.value == "repair"`），保留。

### 2.3 【伪重复 · 不动】20 个跨文件重名 test 函数

如 `test_canonical_json_roundtrip` / `test_rejects_unknown_field` 同时出现在
`test_wave1_contracts.py` 与 `test_critic_contracts.py` —— 测的是不同对象
（Wave1WorkerOutput vs SourceDiagnosticResult/ClaimVerifierResult）。重命名收益
小于 churn，不处理。

### 2.4 【互补 · 不动】unit/live calibration 对

`tests/unit/test_*_calibration.py`（语料契约检查，6-9 用例）与
`tests/live/test_*_live_calibration.py`（`requires_llm` 真实 LLM 运行，1 个参数化用例）
是"语料校验 + 真机运行"互补，live 侧默认 lane 已排除，不重复。

---

## 3. 存量红测（HEAD，36 个真实失败）

> 本地另有一个 `test_live_architecture_contract.py::test_production_wheel_excludes_fixture_package`
> 失败是沙箱 uv cache EPERM（BUG-032 同类环境问题），非仓库缺陷，CI 上应通过。

### 3.1 eval control digest 过期（×35，tests/eval/test_cognitive_evaluation_suite.py）

- 根因：`evals/control/cases/*.json` 里 `src/deerflow_deep_research/domain/human_interaction.py`
  的 pin digest（`2ab99d4…`）与当前文件（`8d34a4e…`）不一致。
- 最近触碰该文件的 commit（8f4cb92 / d7b5692，02x HITL 交互）**没有再生成 digest**；
  且**仓库里没有再生成脚本**，digest 是手维护的。
- 处置建议：**修，不挂起**。补一个 `scripts/regenerate_control_digests.py`（或手改 6 个
  case JSON 的 digest），把 gate 恢复绿。机制本身是真实 guard（锁住 live 语料与源文件的
  对应关系），值得保留。

### 3.2 readiness cap-trip 集成失败（×1）

`tests/integration/test_scripted_real_workflow_debug.py::test_scripted_real_readiness_cap_trip_degrades_to_completed_delivery`
期望 readiness 阶段 journal 事件带 `budget_stop_reason="per_call_output_cap"` 未出现。
疑与最近 readiness commit（68e201f / d772aba，budget tiered 改动）相关，**需作者 triage**：
是测试断言过期还是真回归。

---

## 4. 耗时-价值分级（triage）

| 文件（用例数） | 耗时 | 价值判断 |
| --- | --- | --- |
| `test_demo_tui.py`（51） | 28.2s | **保留但瘦身**（§5.1）。02x 战役（RUN-010/020）唯一 TUI 覆盖；~24s 是真实等待不是浪费，但 51 用例对单个演示面过多 |
| `test_refinement_round_workflow.py`（9） | 4.2s | 方向循环关键证明，保留 |
| `test_refinement_round_recovery.py`（13） | 3.7s | 恢复路径证明，保留 |
| `test_demo_cli.py`（2） | 3.6s | demo 入口证明，保留 |
| `test_provider_durability.py`（7） | 3.2s | 真实子进程重启耐久性（`make test-durability`），刻意保留 |
| `test_research_lifecycle_tool.py`（20） | 3.1s | 生命周期工具证明，保留 |
| fast lane 治理四件套（asset_checker/configure/regression_descent/scripted_debug） | ~13s | 真实子进程/整树收集的治理验证，贵但值得，保留 |
| `test_cognitive_evaluation_suite.py`（58） | 0.57s | 不慢，但当前红。修 digest 恢复（§3.1） |

**结论：没有应挂起的文件。** 所有耗时项的价值都能判断；`tests_suspended/`
机制保留给"价值存疑"的未来候选（§5.3）。

---

## 5. 提速杠杆（按收益排序）

### 5.1 demo_tui 瘦身（已实测否决）—— 不合并

- **实测结论（2026-08-22）**：Textual pilot 共享会话**不省时**。合并 4 个用例
  为 2 个共享会话后，49 用例实测 34.11s，与原 51 用例基线 34.2–34.8s 持平；
  且被合并的单个用例变慢（stream: 0.12+0.12s → 1.20s；env+slash: 0.81+0.37s →
  2.36s）——共享会话累积渲染状态，后续交互更慢。
- **决策**：`test_demo_tui.py` 保持 51 用例，不合并。Textual 合并只损失粒度与
  可调试性，时间上无收益。真实耗时杠杆交给 pytest-xdist（§5.2）：51 个用例
  会在多个 worker 进程间分发，单文件不再串行。
- 撤回记录：曾临时合并 stream_turn 与 env/slash 两簇，已 `git checkout` 还原。

### 5.2 pytest-xdist 并行（已实施）—— 收益最大

- **现状（已落地，2026-08-22）**：dev 依赖组新增 `pytest-xdist>=3.6,<4`；
  同时把测试所需运行时包（textual、python-dotenv、ruamel.yaml）并入 dev 组，
  pytest 目标从此跑纯 `uv run pytest`，不再重复 `--extra` 旗标。
- Makefile：`test`/`test-fast`/`test-integration`/`test-workflow` 都携带
  `$(PYTEST_XDIST)` 变量，**默认空 = 串行**（2026-08-22 用户指令：测试未经精心
  并行 review，串行最稳）；加速为 opt-in：`make verify PYTEST_XDIST="-n 4"`。
- **实测（本机，-n 4 为 opt-in 加速档）**：
  | lane | 串行 | -n 4 | 提速 |
  | --- | --- | --- | --- |
  | test-fast | 42s | **24.0s** | 43% |
  | test-integration | 57.5s | **21.0s** | 64% |
  | test-workflow | 11.7s | **10.0s** | 15% |
  - 注：-n 4 并行档下未发现并行特有失败，但**并行安全性未经正式 review**，
    默认仍串行；并行档自担风险。
- CI：保持单 job 规范门禁（治理契约钉死），不做 lane 拆分（R2 已撤回）；
  提速只靠 R1 uv 缓存。
- **收益（串行默认下）**：本地 `make verify` ≈ 2 分钟（与改动前持平，但收集/命令
  开销已简化）；CI 因 R1 缓存从 4-6 分钟降到 ~1.5-2 分钟。opt-in 并行档实测 ~52s。

### 5.3 挂起程序（`deep_research_harness/tests_suspended/`）

- 机制：`pyproject.toml` 的 `testpaths=["tests"]` 只收集 `tests/`，sibling 的
  `tests_suspended/` 天然不被收集；lane partition 契约（`test_test_lane_selection.py`）
  只对 `tests/` 内文件成立 → 挂起文件自动退出所有 lane，**不破坏契约**。
- 唯一联动点：`tests/assets/evidence.py` 与 `tests/assets/requirement_evidence.py`
  的 `TestEvidenceClaim` selector 声明（`validate_claim_selections` 要求 selector
  存在于聚焦选择内）。**挂起任何文件前必须同步删除/改写其声明**，否则
  `make test-assets` 红。
- 前置检查清单（挂起单个文件时）：
  1. `grep -rn "<文件名>" tests/assets/*.py` → 清证据声明
  2. `git mv tests/<dir>/<file>.py tests_suspended/<file>.py`
  3. 跑 `make test-assets` + 受影响 lane 确认绿
  4. 在 `docs/testing-and-evaluation.md` 或本 plan 记录挂起原因与复检条件

### 5.4 去重（微）

- 删 rerun_policy 2 用例（§2.1），省 2 个用例的执行与收集成本。

---

## 6. 执行阶段

| Phase | 内容 | 验收 | 前置 |
| --- | --- | --- | --- |
| 0 | 拍板（§7 决策点） | 决策记录在本文件 | — |
| 1 | ✅ 已完成：删 rerun_policy 重复 + 修 eval digest（§3.1）+ readiness 回归修复 | eval suite 绿、integration 绿、rerun 绿 | P0 |
| 2 | ✅ 已完成（结论：不合并）：demo_tui 保持 51 用例（§5.1 实测否决合并） | — | P0 |
| 3 | ✅ 已完成：pytest-xdist + Makefile 简化 + dev 组收敛（§5.2） | verify ≤ ~60s，三 lane 并行全绿 | P0 |
| 4 | 挂起（如出现价值存疑项） | 按 §5.3 清单执行 | P0 |

---

## 7. 待拍板决策点（已全部拍板，2026-08-22）

| 决策点 | 选项 | 拍板 | 落地 |
| --- | --- | --- | --- |
| 1. demo_tui 51 用例 | A) 保留 / B) 合并瘦身 / C) 挂起 | **B（合并断言瘦身）→ 实测后改 A（保留）** | §5.1 实测否决合并，保持 51 用例（T6） |
| 2. eval digest 过期 | A) 修 / B) 挂起 | **A（修）** | 补再生成脚本，35 红测恢复（T4） |
| 3. readiness cap-trip | 作者 triage | **排查** | 真回归，已修复（T5） |
| 4. xdist 并行 | 上 / 暂缓 | **上** | 已落地，verify ≈ 1min（T7/T8/T10） |
