# Suspended Plans — 暂停的计划与延期跟进

> 更新: 2026-08-08 | 这里记录已明确不排期、但不应伪装成“完成”的计划或延期跟进。

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

重新开启时，先把文件用 `git mv` 移回相应的活跃目录，再更新活跃索引并建立/更新拥有该工作的
OpenSpec change；不要直接把 suspended 记录当作实现授权。
