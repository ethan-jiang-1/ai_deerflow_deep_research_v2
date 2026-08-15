# Plan: 运行可观测性 - 人类可读日志与实时轨迹

> 类型: 设计 / 复盘（postmortem） | 更新: 2026-08-15

## 背景 / 现状

这次真实研究实际执行了约 35 分钟。保留 Bundle 有 176 条 `diagnostics/events.jsonl` 事件，
足以事后确认 Wave1 的模型调用、submission 与终态；但运行中的控制台只有一次 result-only
等待提示，既看不到进度，也无法用 `tail` 快速判断目前发生了什么。

这不是“JSONL 做得不够好”这么简单。当前三类东西的职责不同：

| 层 | 当前用途 | 缺口 |
| --- | --- | --- |
| Event Journal | Bundle 内、受限、脱敏、可验证的执行事实 | 名称和字段面向机器；只适合事后工具读取 |
| Live Progress Projection | 给 DeerFlow subscriber 的短暂安全事件 | standalone real demo 没有把它变成持续可读输出 |
| Terminal demo | 研究确认、最终结果和诊断引用 | result-only 等待期间没有活动信息或心跳 |

因此 Journal 不能被删除或“改造成普通日志”：它的有界性、脱敏、Bundle 生命周期和非权威地位
是正确的。需要补的是一个由同一安全事实派生、专为操作者阅读的日志投影。

## 决策 / 方案

### 1. 建立两条明确独立的观察路径

```
Graph / provider / validator
          |
          v
  受限安全事件（唯一语义事实）
          |------------------------------|
          v                              v
Event Journal                      Operator Log projection
JSONL、结构化、可验证              文本、可 tail、面向人
Bundle 内、受限                    Bundle 内、受限、仅观察
          |                              |
          |                              v
          |                      demo 实时控制台镜像
          v
  事后 inspector / diagnostic ref
```

第一版把 Operator Log 放在同一 Bundle 的 `diagnostics/operator.log`。它随 Bundle 删除，不建立
跨 Bundle 注册表，也不承诺删除后还能读取。这样它不会绕开现有的 Bundle Loss、隐私和生命周期
边界。未来若需要跨 Bundle 的生产遥测，单独设计 External Run Observation，不能把本计划的
文件拷出去就算完成。

### 2. 日志是投影，不是第二个业务事件源

新增一个无状态格式化器，只接受已经允许写入 Event Journal 的安全字段。每条文本行附带时间、
级别、bundle 短标识、generation、phase、event kind、work/attempt/review 关联和结果。它不得
读取 prompt、模型原文、工具参数、请求头、token、用户原问题、完整 URL 或本地绝对路径。

建议的可读行形状：

```text
2026-08-15T12:32:10Z INFO  run=b_eUD3... gen=0 phase=wave1 work=g0_wave1_w0010 attempt.started
2026-08-15T12:33:20Z WARN  run=b_eUD3... gen=0 phase=wave1 work=g0_wave1_w0011 validation.failed code=source_diagnostic_enum_invalid
2026-08-15T12:40:38Z ERROR run=b_eUD3... gen=0 phase=wave1 terminal.blocked code=research.blocked diag=diag_38b9...
```

日志级别和必须覆盖的语义：

| 级别 | 必须记录 |
| --- | --- |
| `INFO` | Bundle admission、节点开始/完成、受控 work submission、模型/工具尝试开始/结束、gate 路由、最终状态 |
| `WARN` | 可恢复 provider 异常、重试、结构化输出/validation 拒绝、Journal 或 log 的截断/写入失败 |
| `ERROR` | terminal blocked/cancelled/stopped、不可恢复的安全分类、diagnostic reference |

必须先写入或接受 Journal 事实，再异步投影日志。日志队列溢出、格式化失败和文件写失败只产生一个
有界观察健康信号，绝不能改变图路由、重试、gate、Bundle 状态或终端结果。

### 3. 在 real demo 中显示真实的持续活动

`demo_real` 应保留 result-only 生命周期调用，但在它 await 期间启动一个只读、可取消的观察
任务：读取新的 operator-log 行并镜像到 `stderr`，每 15 秒没有新行时输出一次含 elapsed time、
最后确认 phase 和最后事件序号的 heartbeat。它不轮询/修改图 state，不调用 resume/cancel，不把
“没有新日志”解释为失败。

终态屏幕显示固定的只读入口：Bundle 短 id、Event Journal 状态、operator log 位置/检查命令和
terminal diagnostic reference。交互模式与 `--scripted` 模式使用同一投影，以免再次出现两条
运行路径观察能力不一致。

### 4. 先收紧观察契约，再接入所有节点

创建新的 OpenSpec change，primary owner 为 `runtime/run_observation.py` 的观察边界；相邻的
`graph` 只负责提供已经存在的受限事件，`scripts/demo_real.py` 只负责展示。change 需要明确：

- `operator.log` 的路径、最大字节数、单行最大长度、轮换/截断标记与文件权限；
- 固定字段、闭合 event/error code 和 redaction policy；
- Journal 可用而 log 不可用、Journal 不可用而 console 仍需给出何种安全提示的行为；
- 订阅结束、Ctrl-C、Bundle Loss 和进程崩溃时的关闭语义；
- `BUG-029` 的 critic validation 诊断如何先成为安全事件，再出现在日志中；
- 只有调用方明确请求时才可输出更详细的 operator 层级，且仍不能输出原始模型/工具内容。

## 实施顺序与证据

1. 用 OpenSpec 提案固化上述 ownership、字段白名单、隐私边界、容量和失败语义；不要在现有
   `fix-active-demo-bundle-projection` change 中夹带这项工作。
2. 先写确定性红测：安全 event 到单行文本的格式、敏感输入的 redaction、固定排序、容量截断和
   log 写失败不改变 Run outcome。
3. 实现 Bundle-local writer 与 event-to-log projection；读取 API 必须只能读取已选择的 Bundle，
   不得成为 Bundle discovery 或 lifecycle control API。
4. 给 `demo_real` 添加后台 tail 和 15 秒 heartbeat。用可控时钟、慢速 fixture runtime 证明运行
   未返回最终结果前仍能输出真实 event 行和 heartbeat；不使用真实 API 做该测试。
5. 给 Wave1 critic 的非法结构化结果增加安全 validation event，并用 BUG-027 的最小 JSON 做
   从契约失败到 Journal、operator log、终态诊断的回归链。
6. 跑聚焦测试、完整离线验证和 OpenSpec strict validation；最后只做一次有预算的真机 smoke run，
   验证操作者能在 Wave0/Wave1 期间看见持续轨迹，而不是只在终态读取 JSONL。

## 风险 / 取舍

- [把日志当第二状态机] -> writer 和 console 都是 event 的只读投影；类型和测试禁止它们参与 route、state mutation 或 recovery。
- [泄露模型原文、密钥或用户资料] -> 白名单字段而非“写完再清洗”；redaction 测试覆盖常见 token、URL query、本地路径和长文本。
- [日志 I/O 拖慢或阻断真实研究] -> 有界异步队列、固定容量、丢弃/截断健康信号和无副作用失败策略。
- [大量日志淹没操作者] -> 控制台默认只显示 `INFO` 以上的阶段/attempt/validation/gate/terminal 行；细粒度 worker 事件仍可在 Bundle 的 log 中 tail。
- [Journal 与文本日志相互矛盾] -> Journal 是语义真相；文本日志带 event sequence，并在缺失或丢弃时明确显示，不自造“成功”行。
- [继续扩大成跨进程调试平台] -> v1 只服务本地 demo 和已选择 Bundle；跨 Bundle 外部日志需要独立的 authority、保留和隐私设计。

## 落地关联

本计划关联 BUG-029 与 BUG-030，并为新的 OpenSpec change 提供边界。BUG-025 至 BUG-028 的修复
应在各自最小的 owning change 中推进；operator log 只能帮助诊断它们，不能替代其确定性回归测试。
