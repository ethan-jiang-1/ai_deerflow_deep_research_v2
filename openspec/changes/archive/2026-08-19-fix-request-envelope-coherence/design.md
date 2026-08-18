# Design: fix-request-envelope-coherence

## Context

真实 003 run 暴露的确定性失败（与模型行为无关）：

| Run | 症状 | 算术 |
|-----|------|------|
| 2 | readiness critic 4×`token_admission` → 无界补证循环 → blocked | 请求 9,175B（证据 6,255 + 脚手架）+ 2,048 cap > 8,192 信封 |
| 3 | wave2 a3 pre-model 20ms `candidate_invalid` blocked | 6 条 accepted ref 证据 14,821B 无界序列化 > objective 16,384 字符 |

## Goals / Non-Goals

- **Goal**：任一 prompt builder 在其声明的最大输入下产出的请求，**按构造**满足
  （a）域契约上限（objective ≤ 16,384 字符）与（b）节点 admission 信封
  （请求 UTF-8 上界 + system prompt + output cap ≤ total_token_budget）。
  用确定性回归测试把两类上限互相锁死。
- **Non-Goal**：不改模型行为、不改路由/降级语义（BUG-050/053/054 属
  honest-degraded-delivery change）、不做观测性增强（BUG-048 其余项属
  run-forensics change）。

## Decisions

### D1. 信封对齐选"放宽预算"而非"收紧投影"（readiness / final_delivery）

两个 critic/composer 的**输入**是产品语义需要的信息（证据 + plan 投影），8 KiB
投影上限本身合理；错的是信封没有覆盖它。放宽信封（readiness 16,384、
final_delivery 24,576）不改变任何认知边界——仍是 1 次调用、零工具、2048 输出
cap、60s 墙钟。备选"投影砍半到 4 KiB"被否：readiness judge 证据完整性是
answerability 判定质量的地基，砍投影引入新的误判源。

数字推导（非魔法数）：
- readiness：投影 8,192 + 脚手架/问题 ~1,150 + system prompt 1,268 + cap 2,048
  = 12,658 → 取 16,384（头寸 ~3.7K，28%）
- final_delivery：另含 plan 投影（结论文本 ≤ 每题 ~2K × must_answer 数）→ 取
  24,576

### D2. wave2 选"投影拟合"而非"放宽 objective 域上限"

`NodeExecutionRequest.objective` 16,384 字符是**全域域契约**（bridge、capability
渲染、所有节点共享），为一个节点放宽等于全局放宽。而 wave2 的证据是唯一随 run
**无界增长**的输入（每轮 targeted_evidence 追加 2.5–3.7 KiB），必须投影。采纳与
readiness/final_delivery 同形的确定性截断：共享字节预算起步 32 KiB，objective 超
任一上限则预算 ×¾ 重投，至下限 1 KiB 仍超则 typed 失败
`synthesis_evidence_projection_overflow`。截断条目置 `truncated=true`（诚实性：
模型知道看到的证据不完整）。

第二上限（UTF-8 字节 ≤ 44,800）由 wave2 信封推导：64,000 − 16,384（output cap）
− 1,268（system prompt）≈ 46,348，取整 44,800。字符上限与字节上限并存的原因：
objective 限制是字符数（pydantic），admission 是字节（middleware UTF-8 上界），
CJK 内容两者差异可达 3×，必须同时满足。

### D3. 类别保真：pre-model 构造失败 ≠ 模型候选失败

`candidate_invalid` 语义是"模型产出的候选无效"。pydantic ValidationError（输入
条件）落进同桶会误导排障（run 3 实况）。规则：请求构造期（构造器内部 raise 的
typed ValueError）携带其具体类别；对仍可能漏出的 ValidationError 统一归一为
`synthesis_request_shape_invalid`（pattern-safe），只有模型输出的解析/语义失败才
允许 `candidate_invalid`/`parser_invalid`/`semantic_invalid`。

### D4. 一致性由测试锁死，不由文档约定

两条不变量测试（builder-maximal 输入 → 断言信封不等式 / 双上限不等式）放在
builder 与 policy 的组装层（unit/graph 测试）。任何人单独改任一数字，CI 红。

### D5. 连贯性声明的问题数边界（明确 out of scope）

readiness/final_delivery 的"builder-maximal 可接纳"指**证据投影满额**且
must-answer 问题数使其序列化 assignment 仍在 objective 16,384 字符域上限内
（003 minimal 意图 = 1 个问题；满额 8 KiB 证据下余量 ~6.9K 字符，按问题在请求中
的膨胀差异，readiness 约容纳 ~13 问、final_delivery 约 ~3-4 问——conclusion 条目
含 question 两份 + 16 个 backing ref）。
接近域上限的 16 问题上限：readiness 走既有保守降级（conservative verdicts）、
final_delivery 走既有 typed blocked（WORK_FAILED gate view）——失败有界、可诊断，
但 layout 不会成功。为多问题规模引入拟合投影（D2 模式推广到这两个 builder）是
明确的 follow-up，不在本 change。

## Risks / Trade-offs

- [放宽信封增加单次调用成本上界] → readiness/final_delivery 各 1 次调用/visit，
  上界增幅 ≈ 2×/3×但绝对值仍小（≤24K token cap）；且 admission 是"上界检查"，
  实际用量由 usage 记账。
- [投影截断丢证据尾部] → truncated 标记 + readiness/final_delivery 投影上限本就
  覆盖其语义；wave2 截断只发生在 >32 KiB 累积证据的极端 run（003 正常路径
  ~15 KiB 不触发）。
- [几何收缩循环的最坏迭代数] → 32K→1K 约 8 次迭代，每次仅本地字符串操作，
  微秒级，无风险。

## Migration Plan

纯运行时一致性修复，无持久化格式、无 state 字段、无对外契约变化；旧 run bundle
无迁移需求。工作区已有实现 + run 4 验证（readiness 首次真正运行、wave2 六条证据
通过），apply 阶段收编并补 D3。
