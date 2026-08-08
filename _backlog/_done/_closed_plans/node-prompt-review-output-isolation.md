# Plan: Hidden Local Node-Prompt Review Output

> 类型: 架构分析 / 迁移计划 | 状态: Closed — implemented by `isolate-fixture-implementations` | 归档: 2026-08-01 | 更新: 2026-08-01

## Closure

This plan was implemented by the completed OpenSpec change
`isolate-fixture-implementations` (archived 2026-08-01). The committed prompt
catalog was removed, the on-demand review projection now lives only in ignored
`.node-prompt-review/`, and the clean-checkout and explicit-review workflows are
covered by the change's completed verification tasks.

## 背景 / 已核实事实

`deerflow_research/node_prompts/` 不是运行时读取的 prompt 源码，也不是人工维护的第二份实现。
它是 `deerflow_research/scripts/prompt_dump.py` 将 `graph.prompt_catalog` 提供的代码拥有的合成
case，经 `agents.phase_prompt.render_phase_agent_prompt()` 渲染后的确定性 Markdown 审阅投影。

当前目录由 2026-07-27 的 node-prompt catalog change 引入，并在 2026-07-31 从 `agent/` 随模块
根目录迁移到 `deerflow_research/`。运行时 prompt authority 仍是 graph prompt builder、共享 renderer
与 runtime bridge；生成的 Markdown 不选择 prompt、工具、路由、checkpoint 或 agent action。

问题不在于生成器不可靠，而在于已提交的 `node_prompts/` 看起来像普通源码，容易让 coding agent
或 reviewer 把它当成可编辑的行为 authority。

## 决策 / 方案

将已提交的 `deerflow_research/node_prompts/` 删除，并将按需生成的审阅输出改为：

```text
deerflow_research/.node-prompt-review/
```

选择这个名字是为了同时表达：

- `node-prompt`：内容是节点 prompt 的最终渲染投影；
- `review`：它只服务人工审阅，不是编辑面、配置或运行时输入；
- 前导 `.`：默认文件浏览和常规源码检索不把它当作日常实现面；
- `deerflow_research/.gitignore`：该目录是可删除、可再生的本地产物，而非版本控制基线。

隐藏目录是可读性和工作流约定，不是安全边界；使用 `--hidden` 的工具仍可读取它。真正的 authority
边界由运行时不读取该目录、生成器只写固定路径、以及结构/测试约束共同保证。

## 目标行为

| 场景 | 预期行为 |
| --- | --- |
| Reviewer 需要查看最终 prompt | 显式运行 `make prompt-dump`，只写 `.node-prompt-review/`。 |
| Reviewer 需要验证本地产物 | `make prompt-dump-check` 只读检查已生成的树，报告缺失、陈旧、危险或意外路径。 |
| 干净 checkout / CI | `UV_OFFLINE=1 make verify` 不创建、不要求该目录；保留 source-level catalog inventory、renderer 和临时树测试。 |
| Prompt 语义或 runtime 行为 | 继续只改 graph builder、共享 renderer 或 runtime bridge；不得手改生成的 Markdown。 |

因为 Git 忽略的本地树不能再充当已提交的 freshness baseline，标准验证不再宣称自动产生 Markdown
diff。它保留确定性源码级证据；需要文本审阅时由 reviewer 明确生成本地投影。

## 实施顺序

1. 先增加失败测试：验证干净 checkout 的 `make verify` 不依赖该目录，且显式 dump/check 仍保持
   固定路径、只读检查和安全路径拒绝。
2. 将 `prompt_dump.py` 的固定 root 改为 `.node-prompt-review/`；保留 case registry 与共享 renderer，
   不增加新的 runtime reader。
3. 删除已跟踪的 `node_prompts/`，在 `deerflow_research/.gitignore` 忽略新目录，并更新 Makefile、
   文档、catalog/evidence 测试与 requirement evidence。
4. 从 `openspec/governance/project-structure.toml` 删除已提交 root 的 required-path 注册；结构检查仍
   注册 renderer、case registry、dump 脚本及测试，但不要求本地产物存在。
5. 先验证 clean checkout 行为，再显式生成、检查并确认 `git check-ignore` 命中新目录。

## 风险 / 取舍

- [Prompt 改动不再自动带出提交的 Markdown diff] → 明确以 `make prompt-dump` 作为审阅步骤，保留
  source-level inventory、rendering 和 bridge 一致性测试。
- [本地目录陈旧或被手改] → `make prompt-dump-check` 保持只读失败；重新运行 dump 是唯一恢复方式。
- [隐藏目录被误认为安全措施] → 文档明确它不隔离 `--hidden` 扫描，也不拥有任何执行 authority。
- [结构检查要求不存在的本地产物] → 删除 required-path 注册，改为验证忽略规则与可再生产物的边界。

## 落地关联

本计划的可执行 authority 已由归档的 OpenSpec change
[`isolate-fixture-implementations`](../../../openspec/changes/archive/2026-08-01-isolate-fixture-implementations/) 实现：

- proposal 说明范围和 source-of-truth 迁移；
- design 的「Keep the node-prompt review projection hidden, local, and untracked」记录决策与取舍；
- `node-prompt-catalog` 与 `project-structure` delta specs 定义可观察行为；
- tasks `6.3` 与 `7.4` 定义测试、迁移和最终验证。

本文件只保留分析与设计理由；不得作为第二份 implementation spec 或 runtime authority。该 change
已完成并归档，本计划据此关闭。
