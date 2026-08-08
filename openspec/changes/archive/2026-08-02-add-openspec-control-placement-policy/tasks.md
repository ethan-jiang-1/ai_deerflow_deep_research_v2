## 1. Red-First Contract Coverage

- [x] 1.1 Extend the isolated charter-governance fixture project to materialize both charter-local and external policy roots, the renamed `Triggered review policies` Focus Card field, and a reusable exact seven-column Control Placement Review fixture. (`DRC-009`)
- [x] 1.2 Add failing focused tests for legacy Focus Card field rejection, continuation-line rejection, unknown or unavailable declared policy documents, and the conditional external-policy route. (`DRC-009`)
- [x] 1.3 Add failing focused tests for zero or duplicate Control Placement Review headings or tables, header/separator drift, no rows, empty cells, and every invalid design posture. (`DRC-009`)
- [x] 1.4 Add failing focused tests that require `human-interaction-integrity` for every `human-decision` row and preserve independent Node Agent and Workflow Outcome Review validation when those policies are also selected. (`DRC-009`)

## 2. Policy Route And Authoring Guidance

- [x] 2.1 Add `openspec/policies/README.md` and `openspec/policies/control-placement.md` with the closed postures, trigger, review questions, composition rules, handoff/write-reload evidence guidance, and explicit non-runtime, non-V2 authority boundary. (`DRC-009`)
- [x] 2.2 Route the external policy from the Agent Charter index, add the narrow cognition-to-deterministic-owner principle to `charter.md`, and retain existing focused-policy ownership rather than creating a second charter family. (`DRC-009`)
- [x] 2.3 Update `openspec/config.yaml` so authoring uses `Triggered review policies`, describes the conditional Control Placement Review record, and preserves the existing Node Agent and Workflow Outcome Review instructions. (`DRC-009`)

## 3. Deterministic Admission Checker

- [x] 3.1 Replace the checker’s fixed charter-local policy tuple with a canonical registry of charter and external policy documents, retaining existing policy paths and adding `control-placement`. (`DRC-009`)
- [x] 3.2 Migrate active proposal validation to the sole `Triggered review policies` field, reject the legacy spelling, validate canonical names and declared policy-document availability, and continue to exclude archived changes from admission checks. (`DRC-009`)
- [x] 3.3 Implement the selected `control-placement` validator: exactly one review heading and table, exact seven-column header and separator, at least one complete row, closed posture values, and the required human-interaction policy combination. (`DRC-009`)
- [x] 3.4 Keep the checker deliberately structural: do not infer policy applicability, scan implementation source, evaluate review prose, or grant runtime authority; make all new focused tests pass. (`DRC-009`)

## 4. Synchronized Governance Records

- [x] 4.1 After the route and checker are implemented, atomically migrate this proposal and every other proposal active at implementation time to `Triggered review policies`; add this proposal's selected `control-placement` record, then run the checker without rewriting either archived 2026-08-02 repair or any other archive. (`DRC-009`)
- [x] 4.2 Register `DRC-009` in `openspec/governance/req-registry.yaml`, synchronize it into the main `deep-research-agent-charter` specification, and mark the policy, checker, and focused contract test with the requirement. (`DRC-009`)
- [x] 4.3 Register `openspec/policies/` and both new external policy files in `openspec/governance/project-structure.toml`; update the requirement-evidence metadata with the smallest sufficient focused checker selector. (`DRC-009`)
- [x] 4.4 Update `_backlog/plans/policy-gate-injection-layer.md` to record V1 implementation and the bounded two-archive replay evidence while keeping V2 `add-cross-session-cognitive-guardrails` explicitly deferred with no guardrail directory, runner, dossier, hook, or semantic evaluator. (`DRC-009`)

## 5. Verification And Archive Evidence

- [x] 5.1 Run `cd deerflow_research && uv run --extra operations python -m pytest tests/contract/test_agent_charter_governance.py -q` and `python3 openspec/governance/check_agent_charter.py .`, including all active proposals. (`DRC-009`)
- [x] 5.2 Run the governance and evidence checks touched by the registration work, then `cd deerflow_research && UV_OFFLINE=1 make verify`; resolve any active-proposal or generated-structure conformance failure. (`DRC-009`)
- [x] 5.3 Run `openspec validate add-openspec-control-placement-policy --strict` and `git diff HEAD --check`; record the exact commands/results and `git status --porcelain=v1 --untracked-files=all` in this task file before archive, confirming `backend/` and `frontend/` remain clean. (`DRC-009`)

## Verification Evidence

- `cd deerflow_research && uv run --extra operations python -m pytest tests/contract/test_agent_charter_governance.py -q` -> `82 passed in 5.61s`.
- `python3 openspec/governance/check_agent_charter.py .` -> `Agent charter governance passed.`
- `python3 openspec/governance/check_project_reqs.py .` -> `307 registered (4 retired, 0 orphan)`; `python3 openspec/governance/check_project_specs.py .` -> `44 main spec files, 0 violations`; `python3 openspec/governance/check_project_architecture.py .` -> passed.
- `cd deerflow_research && make test-assets` -> passed with `348` central claims; `make test-req-coverage` -> passed.
- `cd deerflow_research && UV_OFFLINE=1 make verify` -> passed after formatting the new focused test; includes `2268` selected fast-lane tests, Ruff, governance, asset, and requirement coverage checks.
- `openspec validate add-openspec-control-placement-policy --strict` -> `Change 'add-openspec-control-placement-policy' is valid`.
- `git diff HEAD --check` -> exit 0 with no output.
- `git status --porcelain=v1 --untracked-files=all` before archive:

```text
 M _backlog/plans/policy-gate-injection-layer.md
 M deerflow_research/AGENTS.md
 M deerflow_research/tests/assets/evidence.py
 M deerflow_research/tests/assets/requirement_evidence.py
 M deerflow_research/tests/contract/test_agent_charter_governance.py
 M openspec/changes/add-openspec-control-placement-policy/proposal.md
 M openspec/changes/add-openspec-control-placement-policy/tasks.md
 M openspec/config.yaml
 M openspec/governance/agent-charter/README.md
 M openspec/governance/agent-charter/charter.md
 M openspec/governance/check_agent_charter.py
 M openspec/governance/project-structure.toml
 M openspec/governance/req-registry.yaml
 M openspec/specs/deep-research-agent-charter/spec.md
?? openspec/policies/README.md
?? openspec/policies/control-placement.md
```

`backend/` and `frontend/` have no modified or untracked paths.
