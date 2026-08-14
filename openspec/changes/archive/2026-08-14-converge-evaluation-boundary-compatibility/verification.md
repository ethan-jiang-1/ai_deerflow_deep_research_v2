# Apply Verification Evidence

> Status: evidence-limited. This record does not authorize archive while tasks 4.2-4.4 remain open.

## Control Placement Review

The completed diff matches the proposal's Control Placement and Workflow Outcome Review tables.
`EvaluationBundleManifest` remains the single fact authority for `evidence_layer`, and
`verify_bundle()` parses and validates the retained manifest before any digest calculation or
Review Record write. Missing and unknown layers therefore become the bounded
`bundle_manifest_invalid` diagnostic, with no Review Record, operation result reference/status,
or Bundle-byte mutation. The supported `runtime.evaluation` facade projects the domain contracts
by identity; `runtime.evaluation.contracts` is absent and no runtime evaluation module imports it.
No additional recovery, default, backfill, writer, or provenance-upgrade route was introduced.

## Passing Evidence

- The four focused provenance/facade tests pass.
- Requirement, spec, architecture/render-guide, Agent Charter, requirement-coverage, and test-asset
  checks pass.
- Ruff check/format, strict OpenSpec validation, and `git diff HEAD --check` pass.
- `UV_OFFLINE=1 make verify` passes governance, lock, Ruff, asset, and requirement-coverage gates
  before reaching the unrelated `test-fast` baseline failure below.

## Baseline Blocker

`PYTHONDONTWRITEBYTECODE=1 UV_OFFLINE=1 uv run --extra operations python -m pytest tests/eval`
returns `105 passed, 2 failed`. The only failures are outside this change's evaluation-boundary
scope:

- `tests/eval/test_fault_injection.py::test_wall_time_timeout_returns_typed_budget_exhausted_outcome`
  expects `wall_time` but receives `policy`.
- `tests/eval/test_fault_injection.py::test_tool_unavailable_timeout_bridge_fails_closed[tool-unavailable-timeout]`
  expects `tools_unavailable` but receives `capability_admission_failed`.

The same interpreter reproduced both failures in an isolated detached worktree at baseline
`c304f453b90e63dc66c878f9bd4073d9797dd1b3`. `UV_OFFLINE=1 make verify` likewise reaches
`test-fast` after its preceding gates and fails only the first assertion above. Repairing the
node-agent fault outcomes requires separate scope and authorization.

## Unrun Evidence

Credentialed/live evaluation, release, Postgres, external-consumer, and retained-data lanes remain
intentionally unrun and evidence-limited. This change makes no claim about those compatibility or
retention surfaces.
