# BUG-015: provider 终态给出的检查命令在模块改名后失效

> 严重级别: P1 | 发现: 2026-07-31 | 状态: 已修复（2026-07-31）

## 症状

真实 provider timeout 终态告诉用户“只读诊断”，并输出：

```bash
make -C agent demo-sessions DEMO_ARGS="inspect <run-reference>"
```

该命令现在确定失败：`make: *** agent: No such file or directory. Stop.`。模块已由提交
`12b94a7` 从 `agent/` 改名为 `deerflow_research/`。用户按终端给出的唯一诊断动作操作后
被直接中断，只能自行猜测目录改名和替代命令。

实际可用的等价命令是：

```bash
make -C deerflow_research demo-sessions DEMO_ARGS="inspect <run-reference>"
```

这只是只读检查，不会继续执行；因此失效命令并非安全限制，而是错误的 UX 行动入口。

## 根因

CLI/TUI 仍把旧模块根硬编码为 `agent`。例如
[`demo_real.py`](../../../deerflow_research/scripts/demo_real.py#L190) 和
[`demo_real.py`](../../../deerflow_research/scripts/demo_real.py#L222)。

更严重的是测试只比较硬编码字符串。现有
[`test_demo_run_update_adapters.py`](../../../deerflow_research/tests/integration/test_demo_run_update_adapters.py#L70)
期待完全相同的旧命令，因此重命名后仍然通过，未验证命令可从文档承诺的上下文运行。

## 影响

- 用户在 provider 故障后无法执行产品明确提供的排障动作，形成额外的 UX 故障。
- `REC-005`/`REC-006` 所要求的“exact inspection command”失去真实性。
- 隐藏了 `BUG-014` 和 `BUG-016`：即使保留资料足够，用户也到不了检查入口。

## 复现

```bash
cd /Users/bowhead/ai_deerflow_deep_research
make -C agent demo-sessions DEMO_ARGS="inspect r_O9XU_UbsEE1LIm6utC4kmXF4gcxVG94bVd8QYFuyaSs"
```

预期：打印的命令应运行并保持只读。实际：目录不存在。将 `agent` 改为
`deerflow_research` 后，命令成功列出该 run 的 retained bundle 和事件。

## 修复与验证

由 `harden-research-run-diagnostics-and-hitl-intake` 修复。CLI、TUI 和 standalone demo 共用
`inspection_command()`，只在已验证 retained-session correlation 存在时从
`deerflow_research/` 渲染：

```bash
make demo-sessions DEMO_ARGS="inspect <run-reference>"
```

README 与本地操作手册同时声明该命令为只读；它不重试、不恢复 `same_process` 执行，也不创建
新运行。

- `tests/integration/test_demo_run_update_adapters.py::test_standalone_adapters_render_the_same_retained_session_view`
  证明 CLI/TUI 共享同一命令形状。
- `tests/integration/test_demo_sessions.py::test_rendered_module_local_inspection_command_executes_against_a_fixture_bundle`
  从实际 `deerflow_research/` 模块目录执行渲染命令，断言不会调用 graph 或 provider。
- 2026-07-31 的本 change focused suite 通过 228 项测试。
