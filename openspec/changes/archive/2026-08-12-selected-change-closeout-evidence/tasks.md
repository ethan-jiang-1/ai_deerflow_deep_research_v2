# Tasks — Selected Change Closeout Evidence Repair

## 1. Code: output containment to guardrail-evidence/

- [x] 1.1 In `openspec/guardrails/selected_change_closeout.py`, change
      `_validate_review` to reject any resolved output not
      `is_relative_to(change_root / "guardrail-evidence")`, with condition
      `output-path-outside-evidence`, instead of the current change-root-only check.

## 2. Code: strict Markdown unchecked-task parsing

- [x] 2.1 In `_unchecked_task_labels`, replace the substring `- [ ]` scan with an
      anchored Markdown list-item unchecked-task regex
      (`^\s*(?:[-*+])\s+\[ \]\s+(.+?)\s*$`) so only real task lines yield labels.

## 3. Spec delta

- [x] 3.1 Keep the `selected-change-closeout-evidence` delta spec: SCC-002
      persisted-output containment is now the dedicated `guardrail-evidence/`
      subdirectory, and the "Persistent evidence cannot escape its evidence
      directory" scenario covers change artifacts such as `tasks.md`/`proposal.md`.

## 4. Documentation

- [x] 4.1 Update `openspec/guardrails/README.md`: `record-review` output must resolve
      under `<active change root>/guardrail-evidence/`; examples assume the planning
      home as `cwd`; state that `missing-boundary`/`invalid-review` are stdout JSON
      `result` values with exit code 0 and callers must parse `result`, not the exit
      code.

## 5. Tests

- [x] 5.1 Update `deep_research_harness/tests/contract/test_selected_change_closeout.py`
      so all persisted outputs use `guardrail-evidence/` and add a fixture proving an
      output under the change root but outside `guardrail-evidence/` (e.g. `tasks.md`)
      is rejected with `output-path-outside-evidence`.
- [x] 5.2 Add a fixture proving a prose line containing `- [ ]` is not parsed as an
      unchecked task label (rejected as `unknown-unchecked-task`).

## 6. Verification

- [x] 6.1 Run `openspec validate selected-change-closeout-evidence --strict` and
      `git diff --check`.
- [x] 6.2 Run the focused tests
      `deep_research_harness/.venv/bin/python -m pytest tests/contract/test_selected_change_closeout.py`
      and the governance gates
      `python3 openspec/governance/check_project_reqs.py`,
      `check_project_req_coverage.py`, `check_project_specs.py`,
      `check_project_architecture.py`, `check_agent_charter.py`.
