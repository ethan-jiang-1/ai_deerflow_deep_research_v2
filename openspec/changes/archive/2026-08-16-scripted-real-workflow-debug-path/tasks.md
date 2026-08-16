# Tasks: scripted-real-workflow-debug-path

## 1. 治理登记

- [x] 1.1 在 `openspec/governance/req-registry.yaml` 登记 `SCR: scripted-real-workflow-debug` 前缀与 SCR-001..SCR-005 五个 pending ID，并登记 PRS-019
- [x] 1.2 在 `openspec/governance/project-structure.toml` 注册新增的脚本、`src_fake` 模块与测试文件路径，跑 `python3 openspec/governance/check_project_architecture.py` 与 `check_project_reqs.py` 通过

## 2. 红测（先红，@impl SCR-002/SCR-003）

- [x] 2.1 新建 `tests/integration/test_scripted_real_workflow_debug.py`：import 未来 composition 模块（`deerflow_deep_research_fixtures.scripted_real`），运行固定 Bundle；先确认因 entrypoint 缺失而红
- [x] 2.2 断言三波 action proof：11 次模型调用、2 次 web_search、0 次 web_fetch、≥1 Wave0 accepted record、两条 Wave1 review artifact、Wave2 finding backing ref ∈ accepted refs、trace 含 hitl1_auto_profile/hitl2/readiness/final_delivery、终态 completed

## 3. Scenario catalog 与 composition（@impl SCR-001/SCR-002）

- [x] 3.1 新建 `src_fake/deerflow_deep_research_fixtures/scripted_real/`：`baseline.py` 持有固定问题、HITL1 确认文本、11 条带占位符的模型剧本、web_search 脚本响应与每波预算声明
- [x] 3.2 新建 `src_fake/deerflow_deep_research_fixtures/scripted_real/composition.py`：占位符模板模型（usage_metadata、严格耗尽）、scripted bridge factory（narrow 预算 + model/tools resolver）、本地 envelope/AppConfig/沙箱 provider、`run()` 驱动 start → HITL1 确认 → resume 的公共控制入口
- [x] 3.3 红测转绿：wave1 提取含 ≥2 新来源、critic 对齐、wave2 back 在 wave0 accepted ref、readiness backing 用 submission ref、composer 数组只含 prompt 条目 id

## 4. Operator 命令与 CLI contract（@impl SCR-004/SCR-005）

- [x] 4.1 新建 `scripts/debug_scripted_real_workflow.py`：零 `.env`、输出 `composition=all_real_adapters` / `authenticity=scripted_real_workflow` / 零网络零凭据断言 / 每波 counter / Bundle id / Journal 入口 / 总耗时 / 证明与不证明边界
- [x] 4.2 Makefile 新增独立 target `debug-scripted-real-workflow`，不动既有 target；同步 README 的 operator-only 文档
- [x] 4.3 新建 `tests/contract/test_scripted_real_debug_command.py`：零 `.env`/零网络屏蔽、严格耗尽失败用例（缺响应、多一次工具调用、非法脚本输出、意外进入 targeted/rerun）、<10s 断言（超时即失败）

## 5. 收尾

- [x] 5.1 删除 spike 文件 `tests/integration/spike_scripted_real_workflow.py`
- [x] 5.2 `make governance`、`make test-fast`、`make test-integration` 全绿；`openspec validate --strict scripted-real-workflow-debug-path` 通过（验证记录：governance 全绿；test-fast 2802 通过，2 个 make/uv 子进程测试在 DSH 沙箱下因缓存访问被阻、完整访问下通过；test-integration 246 通过，`test_wave1_work_units` 的 question-floor 断言失败是 BUG-028 缓解状态的既有失败，`test_local_entry_environment::test_prepared_entries` 的 profile-check 失败是拷贝树缺 `profiles/` 的既有环境问题——两者与本 change 均无共享代码路径）
- [x] 5.3 更新 `_backlog/bugs/BUG-031`（关联本 change），`_backlog/plans/` 记下一步（BUG-028 修复后的 repair/targeted named case）
