## 1. Red-First Operation-Guidance Contracts

- [x] 1.1 Owner: current apply agent. Before the first target edit, complete this change's plan-review obligation: re-read its Focus Card, selected review, policy, tasks, and one relevant historical counterexample; record an actionable finding as an ordinary unchecked task, or record a bounded no-finding result with its evidence source. (`DRC-010`)
- [x] 1.2 Extend the isolated charter-governance fixture with a minimal `operations` configuration and add failing focused assertions for the `control-placement`-only `rules.tasks` obligation, distinct apply/archive guidance, general delivery with a selection-limited instruction, and their advisory no-command/no-task-write/no-archive-authority boundary. (`DRC-010`)
- [x] 1.3 Add failing deterministic config-contract tests for the stable task-rule and guidance anchors, including the rule that a shared guidance string alone does not create an obligation; keep installed-CLI delivery, absence, and malformed-input behavior in the local probes rather than making the global CLI version a CI acceptance dependency. (`DRC-010`)
- [x] 1.4 Add failing focused tests for the six probe-record fields: OpenSpec version, SHA-256 digest of the exact fixture configuration, selected change, command and exit status, stdout/stderr summary, observed side effect, and explicit unknowns. (`DRC-010`)

### Plan Review Record

- **Owner:** current apply agent
- **Reviewed:** this change's Focus Card and Control Placement Review; `openspec/policies/control-placement.md`; all pending tasks; and BUG-011 in `_backlog/plans/policy-gate-injection-layer/01-bug-boundary-evidence.md`.
- **Bounded conclusion:** BUG-011's broad terminal guard bypassed an existing final-delivery gate. This change preserves the corresponding invariant by using only general advisory strings plus ordinary tasks; it neither conditionally executes review nor gains apply/archive authority.
- **Disposition:** no actionable implementation finding before the first target edit. The evidence sources above, the installed OpenSpec 1.7 operation-input contract, and the focused red tests in tasks 1.2-1.4 remain the bounded proof path; a later finding must be added as an unchecked task.

## 2. Advisory Authoring Route

- [x] 2.1 Add concise `rules.tasks` wording in `openspec/config.yaml` that requires plan-review and archive-closeout-review task records only for a proposal selecting `control-placement`; name the owner, minimal action, and deterministic or bounded-evidence done condition without creating a task writer or a new blocking checker. (`DRC-010`)
- [x] 2.2 Add separate `operations.apply.guidance` and `operations.archive.guidance` entries that are delivered generally but explicitly apply the control-placement review only when the selected proposal declares it; route an agent respectively to selected review context/actionable findings and actual boundary/unresolved closeout work, while stating that native OpenSpec operation ownership remains authoritative. (`DRC-010`)
- [x] 2.3 Extend the Agent Charter route and its focused checker only for stable config/authoring anchors; do not inspect task completion, execute commands, infer semantic quality, or accept/reject archive readiness. (`DRC-010`)

## 3. Reproducible Local Integration Probes

- [x] 3.1 Create the durable per-probe record template, then run documented, disposable isolated-root fixtures for valid, missing, and malformed operation guidance plus a second lookup after a fixture-config change; record fixture setup, commands, OpenSpec version, SHA-256 fixture-config digest, guidance presence/absence, fresh-read result, parser or consumer limitation, and fixture cleanup in `_backlog/plans/policy-gate-injection-layer/05-operation-guidance-probe-evidence.md`. (`DRC-010`)
- [x] 3.2 Exercise the supported native archive command/skill path only in a disposable isolated OpenSpec root; record selected path, inputs, warnings, unsupported alternatives, and cleanup without introducing an archive adapter or wrapper. (`DRC-010`)
- [x] 3.3 Exercise archive side-effect cases for sync, incomplete-task warning, collision, move, and failure in disposable isolated roots as supported locally; record the observed filesystem, specification, task, worktree result, and cleanup for every attempted case. (`DRC-010`)
- [x] 3.4 Construct a disposable isolated Git/OpenSpec root with a selected change and an unrelated worktree edit; record a reliable selected-change boundary or the explicit `missing-boundary` limitation without a broad worktree scanner. (`DRC-010`)
- [x] 3.5 Use a historical archive only as read-only input and replay one boundary case through an isolated active fixture's ordinary finding-to-task and resumed-apply flow; record delivered guidance, task-ledger state, cleanup, and an honest closed or unclosed result without claiming semantic-review success. (`DRC-010`)
- [x] 3.6 Record only the observed delivery, archive, boundary, replay, deterministic-verdict, and unknown facts that Change 3 may consume; do not create `openspec/guardrails/`, a coordinator interface, dossier, runner, or fresh-session claim. (`DRC-010`)

## 4. Synchronized Governance Records

- [x] 4.1 Register `DRC-010` in `openspec/governance/req-registry.yaml`, synchronize this delta into the main `deep-research-agent-charter` specification, and annotate the changed authoring route, focused contract tests, and probe evidence with the requirement. (`DRC-010`)
- [x] 4.2 Register only the durable Change 2 evidence/document locations and focused test selectors in `openspec/governance/project-structure.toml` and requirement-evidence metadata; render or check generated structure through the existing governance route. (`DRC-010`)
- [x] 4.3 Inspect every proposal active when implementation runs; add the two ordinary review obligations only to proposals that explicitly select `control-placement`, leave other policies and all archives untouched, and record the migration set. (`DRC-010`)

### Active Proposal Migration Record

- **Inspected at implementation:** `openspec list --json` returned only `add-openspec-operation-guidance`.
- **Migration set:** that selected proposal declares `control-placement` and already retains both its plan-review obligation (1.1) and archive-closeout-review obligation (5.3).
- **Excluded:** no other active proposal selected a policy; all archives remain historical and unmodified.

- [x] 4.4 Update `_backlog/plans/policy-gate-injection-layer.md` with Change 2 implementation/probe status and retain Change 3 as deferred until this change is archived with sufficient delivery, archive-side-effect, boundary, and replay evidence. (`DRC-010`)

## 5. Verification And Archive Evidence

- [x] 5.1 Run the focused charter/config and operation-guidance contract tests, `python3 openspec/governance/check_agent_charter.py .`, relevant project requirement/structure/evidence checks, and resolve only failures within Change 2's approved boundary. (`DRC-010`)
- [x] 5.2 Run `cd deerflow_research && UV_OFFLINE=1 make verify`, then `openspec validate add-openspec-operation-guidance --strict` and `git diff HEAD --check`; record exact commands/results and `git status --porcelain=v1 --untracked-files=all` before archive, confirming `backend/` and `frontend/` remain clean. (`DRC-010`)
- [x] 5.3 Owner: current archive agent. Before requesting archive, complete this change's archive-closeout-review obligation against its actual selected-change boundary, unresolved tasks, and deterministic evidence; record an actionable finding as an ordinary unchecked task, or record a bounded no-finding result with its evidence source, without describing guidance as archive authority. (`DRC-010`)

### Archive-Closeout Review Record

- **Owner:** current archive agent
- **Actual selected-change boundary:** `git diff --name-only HEAD` contains only the operation-guidance configuration, charter/spec/governance registration, requirement-evidence metadata, contract tests, probe evidence, and the long-term plan. It contains no `backend/`, `frontend/`, `deerflow_research/src/`, or `deerflow_research/tests/integration/` path.
- **Unresolved selected tasks:** none after this closeout record; all `20/20` planned tasks are complete.
- **Deterministic evidence:** focused contracts and all relevant governance/evidence checks pass; strict OpenSpec validation and diff whitespace checks pass. The complete gate's three integration failures are retained in the Verification Record as an external runtime/test baseline issue, not treated as a passing result or corrected under this change.
- **Disposition:** bounded no finding within the selected change boundary. The observed integration failure is not converted into an unrelated task here because this change neither modifies its runtime owner nor can establish a reliable selected-change code boundary; it requires separately scoped follow-up if it is to be corrected. This review record does not grant archive authority.

### Verification Record

- **Focused route:** `cd deerflow_research && uv run --extra operations python -m pytest tests/contract/test_agent_charter_governance.py tests/contract/test_operation_guidance_probe_evidence.py -q` exited `0` with `88 passed`; charter, requirement, main-spec, architecture, and test-asset checks also exited `0`.
- **Full deterministic route:** `cd deerflow_research && UV_OFFLINE=1 make verify` first returned `No rule to make target 'verify'`; `make -n verify` immediately showed the target, and the rerun reached integration after governance, lock, lint, format, asset, requirement-coverage, and fast checks passed. The rerun exited `2`: fast passed `2274` tests, while three existing integration tests expected a mapping but received a LangGraph `Command` (`test_mixed_real_prefixes.py::test_handlers_run_real_prefix_through_wave2_and_keep_later_nodes_fake`, `test_wave0_lifecycle.py::test_mixed_wave0_complete_lifecycle`, and `test_wave0_lifecycle.py::test_wave0_blocked_when_worker_fails_every_topic`). Workflow selection did not run after that integration failure.
- **Strict and boundary checks:** `openspec validate add-openspec-operation-guidance --strict` exited `0`; `git diff HEAD --check` exited `0`; `git diff --name-only HEAD -- deerflow_research/src deerflow_research/tests/integration backend frontend` was empty.
- **Status before archive:** `git status --porcelain=v1 --untracked-files=all` listed only this change's governance, backlog, evidence, and contract-test files. `git status --porcelain=v1 --untracked-files=all -- backend frontend` was empty.
