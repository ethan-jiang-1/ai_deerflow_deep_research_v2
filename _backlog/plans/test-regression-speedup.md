# 回归提速 · 第三轮（test-regression-speedup）

> 生成: 2026-08-22 | 状态: **进行中（L1 ✅ / L2 翻默认 ✅ 落地 / L-A 跨进程缓存 ✅ 落地 / L-C 实测否决）**
> 用途: 回归（`UV_OFFLINE=1 make verify`）提速的**持续运营文档**。第一、二轮见
> [`../_done/_closed_plans/CLS-052-test-suite-cleanup-and-speed.md`](../_done/_closed_plans/CLS-052-test-suite-cleanup-and-speed.md)
> （去重 / 修红 / xdist opt-in / CI uv 缓存 / 时长政策 / 串行默认拍板）。本文件承接第三轮：
> **换思路——不是删用例，而是砍单用例的驱动开销 + 复查并行决策**。
> 数据来源: 本机 `.venv` 实测（warm venv）+ `.reports/*.xml`。

---

## Tracking（进展跟踪总账）

> 维护规则: 完成一项 → 在对应表填 ✅ + 日期 + 验证证据；新决策 → 追加"历史决策记录"；
> 新待办 → 追加文末"待办"；被撤回/否决的项保留记录（原因即价值）。

### 第三轮 · 已完成（R3-1 ~ R3-8）

| # | 事项 | 完成 | 验证证据（实测） |
| --- | --- | --- | --- |
| R3-1 | 系统测量：确认 integration lane 是最大黑洞，`test_demo_tui` 一模块占 28s/55.6s（50%） | ✅ 2026-08-22 | `.reports/test-integration.xml` 模块耗时分解 |
| R3-2 | **L1 落地：TUI 逐键输入 → composer 直赋**（23 处 + `_type_composer` 助手） | ✅ 2026-08-22 | `test_demo_tui` 51 passed：**30.93s → 10.83s（-20.1s，-65%）**；integration lane 全绿：**57.2s → 36.65s（-36%）**；`git diff` 仅触 1 文件（+36/-23） |
| R3-3 | **L2 并行安全 review**（静态扫描 + 实证复核） | ✅ 2026-08-22 | 无共享写/固定端口/未恢复 cwd/会话级 fixture；两次 `-n 4` 全绿（CLS-052 T10/T12）；发现 3 条护栏见 §L2 |
| R3-4 | **L2 翻默认并行**：`PYTEST_XDIST ?= -n 4`（用户拍板"也需要"） | ✅ 2026-08-22 | 三 lane `-n 4` 全绿：fast 43→**29.7s**、integration 37→**27.9s**、workflow 9.5→**8.7s**；`-n auto`(8核) workflow 20.1s 过订阅否决；CI yaml 显式 `-n 4`；时长政策/契约/文档同步 |
| R3-5 | **护栏①：并行时长阈值** `check_test_durations.py --parallel`（8s） | ✅ 2026-08-22 | 并行报告最慢单用例 5.39s（串行 3.46s 的整树收集测试被放大）；8s 阈值正确放行、5s 会误杀；Makefile `test-duration-policy` 按 `$(PYTEST_XDIST)` 自动传 `--parallel` |
| R3-6 | **护栏②：TUI `_wait_for` 上限 4.0 → 8.0s** | ✅ 2026-08-22 | 并行争用下慢 worker 不会偶发 flake |
| R3-7 | **L-A 落地：跨进程 catalog 磁盘缓存**（用户拍板"转做 L-A"） | ✅ 2026-08-22 | 整树 `--collect-only` 子进程 **4.4s → 1.4s**（warm 命中）；`verify` 4 进程收集税 ~15s → ~5s；指纹失效自验证通过；63 个收集契约测试全绿；`make test-assets` 绿 |
| R3-8 | **L-C 实测否决**：数据矩阵"1 case per table"合并 | ✅ 2026-08-22 | 9 候选文件 538 用例仅占 fast lane 4.42s；大头被 425 claims 证据契约逐 row 绑定（合并即红）；安全合并面仅 43 行、极限省 ~0.2s，代价丢失败定位粒度。**用户拍板砍掉** |

### 第三轮 · 待办

| # | 事项 | 状态 | 触发条件 / 说明 |
| --- | --- | --- | --- |
| R3-9 | L3：CI checkout 加 `submodules: recursive` | ⏸️ 搁置 | 存量 CI 问题（CLS-052 T20）：当前 CI `make install` 必挂；用户此前"CI 以后再说"，本轮痛点=本地，仍搁置 |
| R3-10 | L4：entry-env 工作流触发收窄（去 `src/**`/`src_fake/**` 或改 cron+dispatch） | ⏸️ 搁置 | 需改契约 `test_entry_environment_regression_workflow.py::EXPECTED_PATHS`；CI 相关，非本轮痛点 |
| R3-11 | L5 套件级时长预算（growth gate） | ❌ 不折腾 | 本轮用户未选；若用例数/时长再次失控，作为治理手段重估 |
| R3-12 | 治理层 claim 合并（425 claims 逐 row 绑定是用例数天花板） | 📋 远期 | L-C 实测证明用例数大头被证据契约钉死；只有合并 claims 才能实质减数，需单独立项（动 traceability） |

---

## 1. 现状基线（第三轮测量）

| lane | 用例数 | 串行 | `-n 4` |
| --- | --- | --- | --- |
| fast | 2648 | 42.9s | 23.9s |
| integration | 304 | **57.2s** | 20.9s |
| workflow | ~35 | ~8-12s | ~10s |
| **verify 合计** | ~3040 | **~120s** | **52.4s**（CLS-052 T12，`-n auto` 全绿） |

帕累托：
- **fast lane**：2363/2648（89%）用例 <10ms；最慢 30 个 ≈ 24s/40s（60%），全是子进程/真活契约测试。
- **integration lane**：`test_demo_tui` 单模块 28s/55.6s（50%）；次之 refinement_round（4.2+3.7s）、demo_cli（3.6s）、provider_durability（3.2s 真子进程重启）。

## 2. 前两轮账目（CLS-052，不重复劳动）

- ✅ 已做：删 2 真重复；xdist 进 dev 组（opt-in）；CI uv 缓存（R1）；5s/用例时长政策；`-n auto` 全绿验证（52.4s）。
- 🧭 已拍板：**默认串行**（测试未经精心并行 review）；**CI 单 job + `make verify`**（治理契约钉死）；旧概念测试全保留（守卫）。
- ❌ 已否决（有实测）：make -j verify（过订阅更慢）；合并 pytest 调用（不省时）；拆 4 CI job（违反契约）；demo_tui 用例合并（省不了时间，因为慢在驱动开销不是用例数——本轮 L1 才是正解）。

## 3. 第三轮系统分析（换思路：砍单用例成本，不是删用例）

### 3.1 决定性实验

| 实验 | 结果 | 结论 |
| --- | --- | --- |
| 38 次逐键输入（`pilot.press(*"start deep research")`×2） | **3.02s call** | textual 8.2.8 pilot 每键 ≈ **80ms**（2×idle wait + animator wait） |
| 同样语义：`composer.value = "..."` + 回车 | **0.18s call** | 应用分发只读 `Input.Submitted.value`，直赋语义等价 |
| `configure.py` 子进程启动 | **0.12s** | 子进程不是 fast lane 的敌人；慢用例大头是 in-process 真活 |
| TUI 文件 23 处 `press(*"…")` 键数合计 | **316 键 ≈ 25.3s** | 即整个模块 28s 的来源 |

### 3.2 杠杆总账（全部量化后）

| # | 杠杆 | 收益 | 判定 |
| --- | --- | --- | --- |
| **L1** | TUI 逐键 → composer 直赋（20+ 处；测回显语义的同样适用，因回显来自提交值） | integration 57→37s（**-20s，已落地**） | ✅ 做完了 |
| **L2** | xdist 默认并行（-n 4，翻默认已拍板） | fast 43→**29.7s**、integration 37→**27.9s**、workflow 9.5→**8.7s** | ✅ 落地（R3-4/R3-5/R3-6） |
| **L-A** | 跨进程 catalog 磁盘缓存（指纹失效 + 原子写） | 整树收集子进程 4.4s→**1.4s**；verify 4 进程收集税 ~15s→~5s；fast lane `-n 4` 叠加后 43→**17.2s** | ✅ 落地（R3-7，用户拍板转做） |
| **L-C** | 数据矩阵"1 case per table"合并 | 安全面仅 43 行、省 ~0.2s；大头被 425 claims 逐 row 绑定 | ❌ 实测否决（R3-8，用户拍板砍掉） |
| L3 | CI checkout `submodules: recursive` | CI 正确性（现在必挂） | ⏸️ CI 以后再说 |
| L4 | entry-env 触发收窄 | 多数 PR 省 2-3min 第二 job | ⏸️ CI 相关 + 需契约变更 |
| L5 | 套件级时长预算 | 防膨胀（0 即时收益） | ❌ 不折腾（本轮） |
| L6 | asset_checker 进程内收集 | -1~2s（L-A 已覆盖主路径，L6 剩余价值 ~0） | ❌ 不折腾 |
| L7 | workflow lane 收集收窄 | -3s（L-A 后 workflow 收集税已近零） | ❌ 不折腾 |
| L8 | 本地增量模式（diff→目录 + `--lf`） | 本地迭代 5-10x | ❌ 不折腾（本轮） |

**结论（修订）**：L1（驱动开销）+ L2（并行默认）+ L-A（跨进程收集缓存）三件套落地后，
本地 `make verify` pytest 部分 **~90s → ~56s**（fast 17.2 + integration 24.9 + workflow 8.7，
实测值；`make verify` 另加 lint/assets/lock ≈ 15s）。L-C 实测证明**用例数大头被 425-claims
证据契约钉死**（合并即红 `make test-assets`），安全合并面只有 43 行、收益 ~0.2s——减用例
不是提速路径，治理层 claim 合并才是（见 R3-12 远期待办）。

---

## L2 · 并行安全 review（R3-3 交付物）

### 静态扫描结果（无风险项）

| 扫描面 | 结果 |
| --- | --- |
| 仓库树内写文件 | 无——测试写路径全部经 `tmp_path`；`.reports`/`.gitignore` 仅被读取断言 |
| 固定端口 / socket | 仅 `("127.0.0.1", 0)` 临时端口（`test_test_lane_selection`），无碰撞 |
| cwd 变更 | `test_prepare` 的 `os.chdir` 包在 `try/finally` 恢复；xdist 下每 worker 独立进程，进程内 chdir 不跨 worker |
| env 变更 | 全部 `monkeypatch` 或带 teardown 恢复的 fixture（如 `test_diagnostics._env`）；xdist 下 env 天然进程隔离 |
| 会话/模块级 fixture | conftest 无 session/module 级 fixture（仅 function 级 autouse 网络守卫） |
| 固定 /tmp 路径 | 仅作为 host_path **字符串值**传入构造器（序列化/校验单测），无真实写 |
| sys.modules / sys.path | 进程内生效，xdist 下不跨 worker；`test_node_registry` 的 pop 已有 serial 同险，非新增 |
| multiprocessing / subprocess 测试 | worker 间隔离；`uv run` 子进程在 `UV_NO_SYNC=1`（verify 导出）下不抢 sync 锁 |
| 实证 | CLS-052 T10（`-n 4` verify 全绿）+ T12（`-n auto` 52.4s 全绿） |

### 护栏（已全部落地，R3-5/R3-6）

1. **时长政策通胀**：✅ `check_test_durations.py` 新增 `--parallel` 阈值（8s），Makefile
   `test-duration-policy` 按 `$(PYTEST_XDIST)` 非空自动传 `--parallel`。并行报告最慢单用例
   5.39s（串行 3.46s 放大），8s 正确放行、5s 会误杀。
2. **TUI `_wait_for(max_wait=4.0)`**：✅ 上限提到 8.0s（R3-6），并行争用下慢 worker 不 flake。
3. **CI runner 核数**：✅ CI yaml 显式 `UV_OFFLINE=1 make verify PYTEST_XDIST="-n 4"`
   （ubuntu-latest 4 vCPU，比 `-n auto` 可预期）；本地默认 `-n 4`（实测 8 核机上 `-n auto`
   对 workflow lane 过订阅更慢：20.1s vs 8.7s）。

### 判定

并行执行**实证全绿 + 静态无共享状态风险 + 护栏落地**；用户 2026-08-22 拍板翻默认
（R3-4），`PYTEST_XDIST ?= -n 4`，串行为 opt-out（`PYTEST_XDIST=` 空）。

---

## 4. 历史决策记录

| 决策 | 结论 | 日期 | 原因 / 证据 |
| --- | --- | --- | --- |
| L1：TUI 逐键 → 直赋 | ✅ 采纳并落地 | 2026-08-22 | 实测 80ms/键 × 316 键 = 25.3s；直赋 0.18s 同语义（R3-2） |
| L2：翻默认并行 | ✅ 拍板落地（`-n 4`） | 2026-08-22 | 用户拍板"也需要"（R3-4）；三 lane 全绿；`-n auto` workflow 过订阅否决（R3-4 实测） |
| L-A：跨进程 catalog 磁盘缓存 | ✅ 采纳并落地 | 2026-08-22 | 用户拍板"转做 L-A"（R3-7）；收集 4.4s→1.4s；契约测试 63 全绿 |
| L-C：数据矩阵 1 case per table | ❌ 实测否决 | 2026-08-22 | 用户拍板砍掉（R3-8）；安全面 43 行省 ~0.2s，大头被 425 claims 钉死 |
| L3-L8 | ⏸️/❌ 暂不动 | 2026-08-22 | CI 相关或收益 1-3s，见 §3.2 |

---

## 5. Check items（可验证清单）

- [x] `test_demo_tui`：51 passed，**10.83s**（基线 30.93s）
- [x] integration lane：**300 passed，36.65s**（基线 57.2s，4 skipped 为 gateway 环境跳过，非改动引起）
- [x] 改动范围（L1）：仅 `deep_research_harness/tests/integration/test_demo_tui.py`（+36/-23）
- [x] 助手 `_type_composer` 的语义注释说明"分发读 `Input.Submitted.value`，直赋等价"
- [x] L2 review 结论已读（§L2）：无共享状态风险，护栏 1 是翻默认硬前提 → **已落地**
- [x] **拍板翻默认**：`PYTEST_XDIST ?= -n 4` + 契约 `test_verification_gate_contract.py` 同步 + 护栏 1-3 落地
- [x] 翻默认后实测：fast **17.2s**（-n 4 + L-A 缓存；单 -n 4 为 29.7s）、integration **24.9s**（-n auto）、workflow **8.7s**（-n 4）；`test-duration-policy --parallel` 通过；lint 全绿；`make test-assets` 绿
- [x] 已知环境失败（非仓库缺陷）：`test_production_wheel_excludes_fixture_package` 沙箱 uv cache EPERM（BUG-032，CLS-052 已记录）

---

## 6. 待办（parked）

| 项 | 触发条件 |
| --- | --- |
| L3 CI submodules 修复 | 用户重启 CI 话题（CLS-052 T20 已定位：checkout 加 `submodules: recursive`） |
| L4 entry-env 触发收窄 | 同上 + 契约变更 |
| L5 套件级时长预算（growth gate） | 用例数/总时长再次失控时启用（治理手段） |
| R3-12 治理层 claim 合并 | 单独立项（动 425-claims traceability）；L-C 实测证明这是唯一实质减数路径 |
