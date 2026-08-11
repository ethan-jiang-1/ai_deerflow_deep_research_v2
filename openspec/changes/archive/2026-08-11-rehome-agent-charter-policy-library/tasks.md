## 1. Lock the migration contract

- [x] 1.1 Extend `deep_research_harness/tests/contract/test_agent_charter_governance.py` with a focused red fixture/case that accepts `openspec/agent-charter/` plus one ten-document `openspec/policies/` library, and rejects a legacy-only or duplicate policy topology; demonstrate the red state with `cd deep_research_harness && .venv/bin/python -m pytest tests/contract/test_agent_charter_governance.py` before changing the checker.
- [x] 1.2 Update `openspec/governance/check_agent_charter.py` so `CHARTER_ROOT`, the single `POLICY_REGISTRY`, expected Charter links, and authoring-pointer checks resolve only the new canonical topology without adding policy-applicability inference or semantic review; make the focused contract test green with `cd deep_research_harness && .venv/bin/python -m pytest tests/contract/test_agent_charter_governance.py`.

## 2. Rehome Charter and policy prose

- [x] 2.1 Use `git mv` to move `README.md` and `charter.md` from `openspec/governance/agent-charter/` to `openspec/agent-charter/`, and move its nine policy documents into `openspec/policies/`; remove the now-empty legacy directories and leave no redirect, symlink, or duplicate canonical copy.
- [x] 2.2 Rebuild `openspec/agent-charter/README.md` as the sole routing index and `openspec/policies/README.md` as the single categorized policy-library index, with every policy linked from the new relative paths and no second Charter or applicability-inference role.
- [x] 2.3 Update only the affected active Charter and policy prose to use the cross-cutting control-placement terminology and delivered closeout-evidence boundary; preserve every policy name, trigger, authority boundary, posture, review-table schema, and conditional task/guidance obligation.
- [x] 2.4 Keep `openspec/guardrails/README.md` and `openspec/guardrails/selected_change_closeout.py` out of this migration; confirm the scoped diff neither changes their command behavior nor claims to repair their separate output-containment or task-parser contracts.

## 3. Synchronize active routes and structural authority

- [x] 3.1 Replace the legacy Charter and nested-policy required-path inventory in `openspec/governance/project-structure.toml` with the exact new Charter, unified policy-library, and guardrail paths; update the DRC registry wording that still describes control-placement as external or deferred.
- [x] 3.2 Update every active authoring and reader pointer to the canonical paths, including `openspec/config.yaml`, `openspec/CONTEXT.md`, the minimal Charter link in `openspec/governance/README.md`, and the affected `deep_research_harness/` guides and context documents; preserve each document's existing reader role and do not modernize archives or closed plans.
- [x] 3.3 Search active, non-archive material for `openspec/governance/agent-charter` and `agent-charter/policies`, correct any remaining canonical reference, and verify that the old tree is absent rather than retained as a compatibility route.

## 4. Verify the scoped migration

- [x] 4.1 Run the focused topology evidence: `python3 openspec/governance/check_agent_charter.py` and `cd deep_research_harness && .venv/bin/python -m pytest tests/contract/test_agent_charter_governance.py`.
- [x] 4.2 Run the governance checks: `python3 openspec/governance/check_project_architecture.py`, `python3 openspec/governance/check_project_specs.py`, `python3 openspec/governance/check_project_reqs.py`, `python3 openspec/governance/check_project_req_coverage.py`, and `cd deep_research_harness && make governance`.
- [x] 4.3 Before archive, run `cd deep_research_harness && UV_OFFLINE=1 make verify`, `openspec validate rehome-agent-charter-policy-library --strict`, and `git diff HEAD --check`; record `git status --porcelain=v1 --untracked-files=all`, verify `deerflow/` remains untouched, and review the rename-aware scoped diff.
