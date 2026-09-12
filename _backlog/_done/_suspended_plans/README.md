# Suspended Plans — 暂停的计划与延期跟进

> 更新: 2026-09-12 | 这里记录已明确不排期、但不应伪装成“完成”的计划或延期跟进。

Suspended 不等于 done，也不是删除：保留原始上下文、风险和重启条件，但它们不再属于活跃
todo/plan，不进入推荐执行顺序。只有新的明确优先级决定或经审查的 OpenSpec change 才能把它们
移回活跃目录。

| 文件 | 暂停理由 | 重新进入条件 |
| --- | --- | --- |
| `deferred_deep-research-00-launcher-and-docker.md` | 当前没有要建设或验证的部署环境。 | 明确要配置本地/生产部署环境或 Docker live smoke。 |
| `deferred_deep-research-00-postgres-profile.md` | 当前以 file-backed SQLite 为已验证 durable store，没有多 worker / Postgres 需求。 | 明确采用 Postgres 或需要其真实 durability 验证。 |
| `deferred_deep-research-six-case-live-closure.md` | 当前不追求完整 credentialed live aggregate。 | 发版、关键 live 依赖变更或明确分配凭证验证窗口。 |
| `evh-024-release-acceptance-diagnosis.md` | 凭据化 selector 已被安全 suspend；快速确定性诊断环尚未建立。 | 新的 approved OpenSpec change 先交付少于十秒的诊断环，再单独授权真实执行。 |
| `2026-08-06-fast-lane-duration-profile.md` | 快速验证时长的历史测量没有获批 owner、预算或改进目标，不应作为活跃优化工作。 | 明确批准一个带性能预算和覆盖保留条件的 test-performance/governance change。 |
| `todo-a004t01-openspec-scenario-rename-validator.md` | 已确认 scenario-title rename 由外部 `@fission-ai/openspec@1.8.0` 共同 validate/archive guard 拥有；本仓没有安全局部变更。 | 用户单独授权 Fission-AI/OpenSpec issue/proposal/PR，或授权调查一个明确支持 scenario identity/rename 的版本升级。 |
| `todo-a009-risk-based-semantic-traceability.md` | 长期候选未排期（2026-08-13 起）：`@impl` 证据体系已满足现行要求，触发条件自创建起从未满足，无任何可执行 action。 | 出现高风险 requirement change、且审查明确需要 scenario 级语义 traceability 时；届时先设计有界 policy 再评估载体。 |
| `deferred-bug-048-state-projection.md` | CLS-047 遗留：`state.json`/checkpoint 自洽投影没有 owning spec，先有合同才能实现。 | 出现该投影合同的 approved OpenSpec change。 |
| `deferred-test-speed-remainders.md` | CLS-052 收尾遗留：CI R1 缓存确认（被 CI submodule 存量问题挡住）+ R4/R5 低优先。 | 用户重开 CI 话题，或 02x 战役收尾触发 R4 重估。 |
| `deferred-ci-and-traceability-remainders.md` | CLS-053 搁置：L3 CI `submodules: recursive`、L4 entry-env 触发收窄、R3-12 治理层 claim 合并（远期，动 traceability）。 | 用户重开 CI 话题（L3/L4），或出现需实质减少用例数的高风险改动（R3-12）。 |
| `deferred-wave0-provider-tool-root-cause.md` | CLS-015 证据边界：Wave0 provider/tool/validator 根因须由一次新的脱敏真实重现确定，不能从 retained trace 反推。 | 授权并排期一次脱敏真实重现。 |
| `deferred-stage-b1-embedded-real-run.md` | Mode 020 战役主体 Stage B1（embedded 真人真跑）未完成；三次尝试因网络不可达 blocked（期间 BUG-062/063/064 已修）。 | 网络恢复且用户授权重跑，见 runbook-020 与 handoff-020。 |

重新开启时，先把文件用 `git mv` 移回相应的活跃目录，再更新活跃索引并建立/更新拥有该工作的
OpenSpec change；不要直接把 suspended 记录当作实现授权。
