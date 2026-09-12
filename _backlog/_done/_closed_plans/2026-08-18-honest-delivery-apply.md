# honest-delivery-and-real-run-diagnostics Apply Retro

Date: 2026-08-18

一次 OpenSpec change apply 修复三个真实 run 暴露的 bug（BUG-035/036/037），过程中
在 HEAD 上发现并修复了上一个归档 change 遗留的两个"红门"流程 bug（BUG-038/039），
也暴露了本次 apply 自身的若干安排问题。

## What Went Well

- **先彻底诊断再动手**：三个 bug 都先读 gate kernel、域契约、主 spec 和 langgraph
  实际行为，把根因定位到契约层（gate 无降级出口、投影分支不完整、serde 未注册 +
  saver 未接线），才写一个 change 覆盖全部。
- **stash-基线对比法**：fast/workflow 车道出现 35+1 个失败时，`git stash -u` 后在
  干净 HEAD 上跑同一测试再 pop，把三个"疑似回归"全部正确判为**预存在**（1 个沙箱
  环境性 + 2 个 13249bb 遗留），避免误修、也避免误背锅。
- **确定性证据优先**：降级语义（opt-in 策略 + 一次性 marker + rerun 重置）、披露链
  （gate → readiness → 报告 `## Uncertainties`）、serde 边界全部用离线单测/组合测
  试证明，零 `requires_llm` 新增——真实 003 run（6.1）只留给操作员确认。
- **组合式披露链测试**：在单测层把"降级 pass → unresolved_gaps 进 state →
  readiness 披露 → 报告文本含 gap 描述"串成一条断言链，不需要跑全图就锁住了
  端到端语义。

## Repeatable Practices

- **归因前先对比基线**：`git stash -u` → 跑同一测试 → `git stash pop`，预存在
  失败立刻现形；确认 `git status` 计数恢复再继续。
- **校验器 spy 一次性列出全部漂移**：digest 类失败不要逐个猜——monkeypatch 校验
  函数收集所有 mismatch（文件、声明值、实际值），一轮修完（本次一次列出
  synthesis.py + tool.py 两处）。
- **先读域契约再写失败路径测试**：`TerminalIncidentProjection` 的
  `model_validator` 已经 fail-closed 拒绝 provider-无-ref，运行层的
  `provider_diagnostic_reference_missing` 是纵深防御——测试要断言在不变量真正
  执行的那一层。
- **用维护惯例修维护遗漏**：digest 刷新按 `d09bad1` 确立的 bump 模式机械执行，
  不发明新机制。

## Why This Found More Issues

上一个归档 change 用**部分车道绿**（"2069 unit/graph/contract tests"）当作完成凭
证，跳过了含 eval 的 fast 车道和 workflow 车道；本次因为坚持跑全量
`make verify` 等价物才暴露两处遗留红门。若本次也只跑窄套件，红门会继续传给下一
个 change——"门是红的"本身比"两处具体漂移"更是需要记录的缺陷。

## Next-Time Standard

下次同类 apply，"做完"需要满足：

- [ ] 归档前 `make verify`（或 venv 等价物）**全绿**：fast（含 eval）、
  integration、workflow、strict-msgpack 车道逐个确认；部分车道绿不算完成，
  tasks.md 的验证条目要写明跑了哪些车道。
- [ ] 触碰被 eval digest 钉住的文件（`evals/control/cases/*.json` 的
  `source_path` 引用，如 `domain/synthesis.py`、`tool.py`）时，同一 commit 机械
  刷新对应 digest。
- [ ] spec 行为语义变更时，grep 全部标记（含 `workflow`/`periodic`）的相关测试
  同步更新期望，不留给别的车道。
- [ ] 测试文件修改一律用精确 `edit`（old_string 唯一匹配）；**禁用宽匹配 sed**
  （本次 sed 按"整行 result = 模式"批量替换 F841，误伤了既有测试的赋值行，靠
  ruff F821 才抓回）。
- [ ] `edit` 前在会话内先 `read` 目标文件，即使已通过 grep/sed 掌握结构（本次两
  次被工具拒绝后才补）。
- [ ] 写失败路径测试前先回答：这个不变量在**哪一层**执行（契约校验器 / 运行层
  纵深防御）？断言写在执行层，不写在不可达层。
- [ ] 后台测试命令**不用管道吞退出码**：`... | tail -3` 让 35 failed 报 exit 0；
  必须 `job_output` 读全文、以 pytest 汇总行为准。
- [ ] 起草投影/诊断逻辑前先写下"哪个 ref/字段是权威发布值"（本次曾误用
  `incident.diagnostic_ref` 而非实际发布的 `terminal_diagnostic_ref`，中途修正）。
