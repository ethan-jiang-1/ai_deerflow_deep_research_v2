# Tasks: close-provider-timeout-budget-handback

## 1. TDD 红：注入式 provider 超时的确定性用例（零凭证零网络）

- [x] 1.1 在 wave2 node 的最低测试缝（`tests/graph/test_wave2_synthesis_real.py`
  既有文件或同层新增）注入失败 `run_agent`：首次返回
  `InvocationFailure`，其 `problem.provider_observation` 的 timeout origin =
  `bridge_wall_time_budget`，第二次成功——断言 node 不写终态、不产生
  budget-exhaustion handback、走正常 validation 路径（WSN-012 场景 1+2）
  → `test_provider_transient_timeout_retries_and_succeeds`（红→绿）
- [x] 1.2 同缝注入 `provider_sdk_timeout` origin 变体：同样触发重试
  （两 origin 等价，WSN-012 场景 1 的参数化）
  → `test_provider_sdk_timeout_origin_retries_equally` +
  `test_provider_transient_classification_requires_timeout_origin`（谓词
  单测：两 origin 判真；无 observation / budget-class 判假——apply 中发现
  domain 契约 `provider_timeout_observation_invalid` 已禁止"PROVIDER_TIMEOUT
  观察无 origin"形态，边界比原设想更干净，测试按可代表形态收敛）
- [x] 1.3 注入连续 provider-transient 失败直到预算耗尽：断言最终进入现行
  budget-class handback（`wave2_budget_exhausted` 路径不变），gate 处置
  语义与既有回放一致（WSN-012 场景 3）
  → `test_provider_transient_retries_end_in_budget_handback`
- [x] 1.4 非瞬态失败回归锁：token 耗尽（`NodeFinishReason.BUDGET_EXHAUSTED`
  且无 timeout origin）与结构非法失败 → 分类与处置与改动前逐字一致
  （WSN-012 场景 4；对照既有 budget/exhausted 回放用例保持绿）
  → 既有 `test_non_budget_failures_keep_their_terminal_disposition` +
  `test_budget_exhausted_invocation_hands_route_authority_to_the_gate`
  （BUG-050 用例零漂移，全文件 49 passed）
- [x] 1.5 journal 序列断言：重试序列中每次 attempt 独立记账、ordinal 续进、
  同 phase 同 node attempt identity（WSN-012 场景 5）
  → 测试缝级断言（`requests == 2`、`contexts[0] == contexts[1]` 同 attempt
  identity、各自独立 invocation）；ordinal 续进由 middleware/bridge 既有
  记账保证（`test_budget_middleware.py` 覆盖计数路径），journal 层不改动
- [x] 1.6 取消不吞：注入 `CancelledError` 透传，不进入重试（design D2）
  → `test_provider_transient_retry_does_not_swallow_cancellation`
- [x] 1.7（apply 中补齐 repair 调用点场景）：主调用成功但候选非法 →
  repair 首次 transient 失败 → repair 重试成功 → 正常收尾
  → `test_repair_invocation_retries_provider_transient_timeout`

## 2. 实现（最小 owner：wave2 包内）

- [x] 2.1 `domain/workflow_outcomes.py`：把 `_timeout_origin` 提升为公开导出
  `timeout_origin_of`（公开名 + `__all__`，不复制实现不改语义；内部调用点
  同步换名）；wave2 包内新增 `_is_provider_transient(outcome)` 消费该公开
  映射（design D1；实现在 node.py，与 `_is_budget_class` 同处）
- [x] 2.2 `node.py`：合成主调用与 repair 调用点包
  `_invoke_with_provider_retry`（transient → 重试；非 transient 透传；
  `CancelledError` 透传；无自造预算计数，design D2/D3）
- [x] 2.3 任务 1 全部用例转绿；既有 wave2 budget-handback / exhausted /
  degradation 回放零漂移（全文件 49 passed，其中既有 43 全绿）

## 3. 预算执法证据锁定（design R1/R3 已在 polish 取证，apply 固化）

- [x] 3.1 以测试锁定执法契约：`agents/middleware.py::awrap_model_call` 在
  `model_calls >= max_model_calls` 时抛 `AgentBudgetError(BUDGET_EXHAUSTED,
  MODEL_CALL_LIMIT)`（无 timeout origin）——既有覆盖确认：
  `tests/unit/test_budget_middleware.py:115-127`（断言 MODEL_CALL_LIMIT +
  handler 不被调用），无需新增
- [x] 3.2 确认重试循环终止性用例：注入连续 transient 失败时，最后一次
  invocation 由预算执法失败收口进入 handback（任务 1.3 即此形态；
  实现未偏离 D2 主路径，无偏离记录）

## 4. 契约与门

- [x] 4.1 在 `openspec/governance/req-registry.yaml` 登记新 requirement ID
  `WSN-012`（wave2-synthesis-node — provider 瞬态超时在模型调用预算内
  重试），描述与 delta spec 一致；确认无 already-assigned 冲突
  （registry 中 WSN 段原止于 WSN-011，无冲突）
- [x] 4.2 对照 delta spec 五个 scenario 逐条核对测试覆盖：
  场景 1（首次超时重试不降级）→ 1.1；场景 2（重试成功无痕）→ 1.1 +
  1.7；场景 3（重试耗尽回落既有 budget 处置）→ 1.3；场景 4（非瞬态
  不受影响）→ 1.4 + 谓词单测负例；场景 5（attempt 独立可观察）→ 1.5
- [x] 4.3 `UV_OFFLINE=1 make verify` 全绿（fast + integration + workflow；
  strict validate 通过）——**2026-08-30 实跑**：lock-check/lint/format/assets ✅ +
  fast **2656 passed**（含本 change 6 个新用例）+ integration **301 passed,
  4 skipped** + workflow **35 passed**，exit 0
