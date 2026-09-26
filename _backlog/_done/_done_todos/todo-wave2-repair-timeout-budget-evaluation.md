# TODO: wave2-repair-timeout-budget-evaluation

> 状态: **已完成（DONE-006，2026-09-27）**——由 change
> `align-wave2-calibration-case-budget`（archive `2026-09-27-…`）解决。
> 优先级: 中 | 更新: 2026-09-27
> 上游: plan demo-real-gateway-closeout.md（G3 验收遗留项，plan 已归档 CLS-060） | 下游: 无

## 终局处置

设计问题于 2026-09-26 深夜静态裁决（owning 层 = evaluation-hardening spec 上限
精神 + fixture 等值契约；生产层已为同类问题付学费 300s/64k）。2026-09-27 用户
拍板"对齐当前 codebase，openspec 一口气收掉"后走 change 落地：

- 四个 `wave2-synthesis` 分支 case（synthesis + repair × normal + highest-risk）
  从 `_ZERO` 档（60s/16k）迁入 `_WAVE2` 档（180s/32k，单调用/零工具/单尝试
  不变）——值取自 corpus 既有 worker 档（`_WORKER` 180s/32k），严格低于生产
  分支策略上限（300s/64k/4 calls）。
- validator 改为 `_branch_tier` 分支键控三档映射，fail-closed 等值契约原样保留；
  漂移测试新增"把 wave2 case 改回 60s 必须仍报
  `evidence_judgment_calibration_bounds_invalid`"；另有 ordering-only 断言
  记录档位对生产天花板的距离。
- 门禁全绿（六 checker 治理门 / `UV_OFFLINE=1 make verify` / strict validate /
  diff check / 版本对齐 1.13.1 / gitlink 证据，退出码全部直测）。

**遗留（非阻塞，补充性证据）**：下一个显式选择的 live 窗口跑一次这四个 case
记录 typed rubric disposition；若健康链路上 180s 仍超时，那是更深问题的证据，
不是继续调档的理由（已写入 change tasks.md 的 Deferred evidence 节）。

以下为历史判断记录，供追溯。

## Why

`make test-live` 分诊（2026-09-26）后 live lane 为 49/50 等效。唯一剩余失败
`wave2-synthesis-repair-normal`：两次复现均为 **TimeoutError**——真实模型延迟超出
case 预算。该 case 的校准测试直接传死 `validation_category="parser_invalid"`，
与 G1/G2 改动零交集。问题不在代码路径，在 case 的 timeout 预算与真实模型延迟的匹配。

## 现状对齐（2026-09-26 深夜静态复审补全）

- 其余 49 个 live case 全部通过（含修复后的 `gateway_forwarding_proof`）。
- **预算定位**：case 预算 = `tests/scenarios/evidence_judgment_calibration.py` 的
  `_ZERO` 档（60s / 1 model call / 16k tokens），被 validator **等值强制**——
  12 个非 worker case 共享同一档，改一个即改全部（corpus 级决策，非单点调参）。
- **Spec 上限**：evaluation-hardening spec 要求 case bounds "no wider than its
  existing zero-tool branch policy"。生产 wave2-synthesis 策略 = **300s / 4 calls /
  64k tokens**——合法上调空间一直存在，但 `_ZERO` 的等值契约使松动成为治理决策。
- **生产侧已付过学费**：wave2 生产策略 docstring 明记 "real runs exhaust the
  scripted-calibrated values on real output (observed `budget.exhausted`)"，
  生产层已为此加余量（300s + 64k）；case 层未跟进。
- **健康基线**：同晚 live canary `live-wave2-synthesis`（真实全量综合调用）
  wall_time = **24.7s** —— 60s 预算对健康链路本应有 ~2.4× 余量。
- **混杂因素**：两次 TimeoutError 与当晚 Gateway 路线记录的 provider 断流
  （`stream_chunk_timeout` 240s×4-8，VPN 链路抖动）同窗口共存；坏链路窗口里
  任何合理预算都会超时（当晚 Gateway 主线也在断流中挣扎）。
- **冻结条款不适用**：spec "LIVE_CANARIES deadline budget SHALL remain unchanged"
  只冻结 6 个 canary；本 case 不在其中。

## 设计问题（已裁决）

- **预算 owning 层** → 上限由 evaluation-hardening spec（branch policy 天花板）
  拥有；具体数值由测试 fixture 的 `_ZERO` 等值契约拥有；调预算 = corpus 治理
  决策（改共享档或引入分支档位 + validator 重构），非一行改动。
- **调预算 vs 记录已知方差** → 现有证据（24.7s 健康基线 × 60s 预算；失败与
  断流窗口共存）使"环境方差"成为领先假设；**首选结论是不改预算**，除非干净
  窗口的耗时分布证明 P95 逼近 60s。

## Current Direction

首个干净链路窗口跑一次该 case（或等价取 wave2 修复轮真实耗时分布），按分布裁决：

- P95 明显 < 60s → 判为已知环境方差，关本 todo，零代码改动（诚实记录优于调参凑绿）。
- P95 逼近/超 60s → 走 corpus 治理调 `_ZERO`（或为 wave2 分支引入独立档位），
  一次提交 + validator 决策 + 本 todo 记录取舍。

## Non-Goals

- 不动 wave2 解析/校验代码路径（G1 已修且真机验证过）。
- 不为 50/50 的账面数字调参凑绿。
- 不在无干净窗口数据的情况下预调预算（那只是把方差换成猜数）。

## Next Step

下次干净 live 窗口跑该 case 并留存耗时证据，按 Current Direction 的分布判据裁决。
