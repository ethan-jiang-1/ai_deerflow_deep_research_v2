# Candidate Register

> 角色: 本计划的可更新审计快照，不是 current behavior authority
> 初始快照: 2026-08-13 @ `a733d329902e779a108401f1305c937174f6e492`
> 状态说明: `candidate` 只表示值得调查，不授权删除或 rename

## 使用规则

- 每项必须最终落入 `retired / migrated / renamed / guard-retained / historical / rejected`；
- `decision-required` 必须写明 decision authority 和缺失证据；
- 实施任务只进入 owning OpenSpec change 的 `tasks.md`，本表不复制逐文件 checklist；
- 行为事实变化时引用 main spec/change/test，不在本表重新定义行为；
- 新 candidate 必须说明它属于哪个 authority cluster，不能只贴一个搜索命中。

## 初始候选

| ID | Cluster / surface | 当前证据 | Grade | 初始 disposition | 进入 change 前必须证明 |
| --- | --- | --- | --- | --- | --- |
| PC-001 | `phase agent` identity | `agents/phase_prompt.py`、factory/policies/structured_output、runtime bridge docstring、`resources/node_agent/runtime_policy.md` 与 `test_phase_prompt.py` 仍使用；glossary 当前采用 LLM-Bearing Node / Node Cognitive Control Program | AI-facing + cross-layer | `decision-required`，高优先级 rename candidate | canonical distinctions；model-facing behavior impact；所有 loaders/tests/evals；是否有 external prompt consumers |
| PC-002 | legacy capability binding | `NodeExecutionRequest` 默认 `legacy`；扫描到的 17 个 production builders 均显式 `required` | cross-boundary internal request | `candidate: retire` | reflection/fixture/eval/external constructors；serialization；missing-capability target behavior；negative test |
| PC-003 | `FULL_FAKE` enum/value | current recipe 只产生 fixture/mixed/all_real；enum 与 old-input rejection仍存在；Bundle State 可持久化 mode | persisted/public projection | `migrate-then-retire` candidate | retained data/support window；old value mapping vs rejection；all readers/writers；rollback compatibility |
| PC-004 | demo `bind_full_fake` naming | demo/fixture route 调用该 method，但 current result 是 fixture | assembly + operator code | `rename` candidate | 是否只 private method；docs/tests/current command consumers；与 PC-003 同批还是独立 |
| PC-005 | `MIXED` implementation mode | explicit test composition仍生成 mixed；public production fixed all-real | test composition + persisted projection | `rejected-or-migrate` | mixed 是否仍为必要测试证据；是否会进入 retained public Bundle；明确非生产边界 |
| PC-006 | `research-run-session` capability name | main spec 当前约束 RunObservation；production run_session modules 已删除；test name仍是 session contract | spec/cross-boundary observation | `decision-required: rename/merge` | target capability owner；RUS ID semantic continuity；all spec/test/docs consumers；archive strategy |
| PC-007 | `research-session-lifecycle-binding` capability | current spec主要规定 legacy binding 无权控制；production scan未发现对应 session binding controller | persisted compatibility + spec | `decision-required: retire/merge` | actual legacy records/readers；long-term rejection invariant owner；RES ID disposition；old-data failure behavior |
| PC-008 | retired run-session import guard | `test_retired_run_session_store_has_no_compatibility_module` 明确阻止旧 modules复活 | negative guard | `guard-retained` hypothesis | planted module/path violation仍能 fail；guard scope cannot escape；归属迁到 current structure/observation owner是否更清楚 |
| PC-009 | session-named current tests | `test_run_session_contract.py` 实际测试 `RunObservation*` | test naming | `rename` candidate | selector/registry/docs consumers；不改变 RUS evidence semantics；是否随 PC-006处理 |
| PC-010 | dormant Primary User TUI/local-first concepts | glossary/ADRs标为 dormant；standalone demo TUI仍是 active operator visualizer | product/entry distinction | `decision-required` | current code/config/tests中哪些属于 dormant product route、哪些属于 current operator tool；owner与consumer |
| PC-011 | standalone demos/workbench overlap | README/Make支持 demo CLI、fixture graph、TUI、sessions/workbench；角色不同但可能复制 presentation/control | operator entry | `decision-required` | 每个入口用户、unique outcome、CI/Make consumer、authority duplication、删除后证据去向 |
| PC-012 | config/path compatibility branches | configure/deployment specs/tests包含 legacy path、checkpointer和fallback rejection | public config/deployment | `decision-required` | observed installed baselines；read/write/reject classification；support window；backup/rollback |
| PC-013 | CONTEXT non-glossary tail | glossary后有六段 evaluation/cognitive-control design statements；旧 C-006 曾拒绝仅为缩短而整体搬迁 | current documentation | `decision-required` | 每段是否重复 ADR/spec；current reader route；新 canonical-language目标是否提供具体错误而非偏好 |
| PC-014 | superseded/dormant ADR routing | ADR 0007被 0028 supersede；0002/0008等历史方向已标 dormant | historical architecture record | `historical` hypothesis | current docs不把旧 ADR当authority；status和superseding links足够；不批量重写历史词 |
| PC-015 | dated release/baseline docs | docs index链接 2026-07-17 baseline、attestation、regression materials | historical evidence/current navigation | `historical-or-reroute` | 是否仍是current reader必需；freshness说明；是否应从主 reading path降级到 evidence index |
| PC-016 | suspended scenario asset | `tests/scenarios_suspended/evh_024_release_acceptance.py` 不由默认 pytest/Make执行 | test support | `decision-required: move/delete` | owner、restart trigger、current inbound refs、是否仍有独特诊断价值 |
| PC-017 | empty test scaffolding | tracked `.gitkeep` 存在于 e2e/fixtures/graph/integration/unit 等目录 | private test structure | `candidate: retire` | directories是否仍需 packaging/tooling；tracked consumers；删除不会影响 collection/import |
| PC-018 | oversized evidence registries | assets/scenarios/eval registries有 executable joins，不能按体量删除 | test governance | `rejected wholesale; per-owner subtraction` | 每个 retired selector/requirement同步移除；known-violation smoke防止空扫描 |
| PC-019 | current old-root rejection strings | `deerflow_research` / prior path matches存在于 contract guards和release scope | structural negative guard | `guard-retained-or-stale` | 每个 match是 current rejection、历史 fixture还是无效 residue；guard sensitivity和scope |
| PC-020 | legacy terminal reason | `TerminalReason.REPAIR_EXHAUSTED` 标注 retained for compat, no longer produced by gate | persisted lifecycle enum | `migrate-then-retire` candidate | retained Bundle reader/data；public projection；old input handling；current replacement reason；rollback |

## 明确保留的非候选边界

除非新证据推翻，以下不是“一看见就删”的对象：

- `src_fake` fixture package：当前 deterministic graph composition evidence，且与 production wheel 隔离；
- `mixed` worker-failure aggregate：与 implementation mode 的 `mixed` 不是同一概念；
- OpenSpec archive 和 `_backlog/_done` 中的历史旧词/路径；
- anti-resurrection tests、old-input rejection fixtures；
- current Run Event Journal、Run Observation 和 diagnostic projections，只因名称含 observation/session
  不能推断重复 authority；
- superseded ADR 本体；历史决策应保留，current routes 只需正确指向现行 owner。

## 下一次更新

P0 inventory 完成后：

1. 给每个 candidate 补 owning main spec/requirement IDs；
2. 补 static/dynamic consumer 和 persisted-data evidence；
3. 确定首个最小 OpenSpec change；
4. 新发现只追加真正的 authority cluster，不追加每个文件命中；
5. 每次 change archive 后更新 disposition 和证据链接。
