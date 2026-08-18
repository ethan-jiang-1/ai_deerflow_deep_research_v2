## 1. Parser 归一化（composer.py）

- [x] 1.1 红测：`tests/unit/test_final_delivery_real.py` 新增 fenced 与
  embedded-json 投递的 parse 用例（先失败：当前裸 `json.loads` 拒绝）。
  验证：`cd deep_research_harness && UV_NO_CACHE=1 .venv/bin/python -m pytest
  tests/unit/test_final_delivery_real.py -k layout -x`（红）。
- [x] 1.2 绿：`parse_layout_candidate` 增加投递形状归一化（strip → 裸
  `json.loads` → fenced block 提取 → 首个平衡 JSON 对象 `raw_decode` 扫描），
  归一化产物仍过原样 `FinalDeliveryLayoutCandidate` 校验；内容不宽容（不猜
  id、不修 schema）。同命令转绿；既有裸 JSON 用例不回归。
- [x] 1.3 提取公共构造：plan-order layout 候选构造（现退化分支内联）提为
  `composer.py` 单一函数，退化分支与降级路径共用；退化分支行为不变
  （`test_degenerate_plan_renders_deterministically_without_the_composer` 保持绿）。

## 2. 降级语义 + validation fact（node.py）

- [x] 2.1 红测：非退化 plan + composer 返回垃圾（parse 失败）→ 该 visit 仍
  发布两个 final artifacts、gate view 为 published、不产生 `WORK_FAILED`；
  非退化 plan + composer invocation 失败 → 同样发布。先失败（当前
  `WORK_FAILED`）。
- [x] 2.2 红测：结构级失败仍 repair——plan 读失败 / readback-verify 失败 →
  无发布 + failure view（改写既有
  `test_rejected_layout_and_readback_failure_never_publish_a_pass_view`：
  拆成"layout 拒绝 → 降级发布"与"readback 失败 → repair"两个用例）。
- [x] 2.3 绿：`node.py` 重构——layout 获取（退化构造 / composer 调用 + 归一化
  parse + admit）与结构级操作（evidence 读、render、publish、readback
  verify）分离；layout 级失败（invocation 或 parse/admission）降级为
  plan-order 构造并继续发布；结构级失败保持既有 `except → WORK_FAILED` view。
  2.1/2.2 转绿。
- [x] 2.4 validation fact：layout parse/admission 失败时经
  `dependencies.event_recorder`（None 安全，`try/except: return`）记一条
  journal validation fact——`category=VALIDATION`、phase=final_delivery、
  `validation_stage="initial"`、`validation_codes=(既有 canonical code,)`，
  不带 response_shape（RunEvent 合同对非 wave 阶段要求无 shape）与 raw
  输出；invocation 失败不发（只留既有 invocation fact）。可参照
  topic_planning `_record_validation_observation` 同形加发
  observation_projection live 字段。单测：注入 spy recorder 断言 fact 形状
  与"invocation 失败无 fact"；duplicate-id 候选坍缩为
  `final_layout_shape_invalid`。

## 3. Journal 契约回归

- [x] 3.1 `tests/unit/test_run_observation_store.py` 补一条：phase=
  final_delivery、stage=`initial`、无 response_shape 的 validation fact 被
  RunEvent 合同接受（守护 phase-scoping 不被误扩）；node 侧闭合 code 断言
  已由 2.4 的 spy 覆盖。运行该文件转绿。

## 4. 全量验证

- [x] 4.1 `cd deep_research_harness && UV_OFFLINE=1 make verify`（含
  unit/graph/contract + ruff）全绿。实测口径：变更范围内 2401 passed
  （unit/graph/contract/integration）；仓级既有红点两处均与 HEAD 相同、已登记
  BUG-056（readiness 一致性失败）与 ruff-format 版本性漂移（6 个未触碰文件）。
- [x] 4.2 002 零成本回归：`UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run <root>
  --mode 002"` → `RESULT: PASS`。
- [x] 4.3 真实 003 复跑：`UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run <root>
  --mode 003"` → `RESULT: PASS` + `final/report.md` 真实内容 + 单 work unit
  口径（runbook-003 §5/§6）。模型挂起按 §7 Ctrl-C 重试。

## 5. 收尾

- [x] 5.1 文档口径：`_backlog/_local_demo/runbook-003-medium-real-auto.md`
  §5.1/§8 补一句——final_delivery layout 级失败走 plan-order 降级发布，不再
  可能因排版回显 blocked；观测看 journal validation fact（闭合
  `final_layout_*` code）。同步更新节点包内
  `graph/nodes/final_delivery/workflow.md` 的 Route Facts / From Symptoms
  段（reader projection，加降级路径一句话；`make` 的
  check_node_workflows / check_node_language 需过）。
- [x] 5.2 归档前命令记录（apply agent 执行）：
  `cd deep_research_harness && UV_OFFLINE=1 make verify`、
  `openspec validate fix-final-delivery-layout-fragility --strict`、
  `git diff HEAD --check`；记录 `git status --porcelain=v1
  --untracked-files=all`、`git ls-files --stage deerflow`、
  `git submodule status -- deerflow`、
  `git -C deerflow status --porcelain=v1 --untracked-files=all` 并确认
  submodule 零改动。
- [x] 5.3 归档 change（openspec archive，主 specs 同步）；BUG-055 卡已移至
  `_done/_fixed_bugs/` 并补修复关联；更新 `_backlog/bugs/README.md`、
  `_done/_fixed_bugs/README.md`、`_done/README.md` 计数。
