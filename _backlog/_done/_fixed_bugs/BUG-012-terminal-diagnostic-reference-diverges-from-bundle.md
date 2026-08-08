# BUG-012: Terminal CLI diagnostic reference disagrees with its retained run bundle

> Severity: P1 | Discovered: 2026-07-26 | Status: fixed (2026-07-26)

## Symptom

One bounded real demo reached a blocked `topic_planning` terminal and displayed a safe
diagnostic reference in the CLI, but read-only inspection of the exact retained run
reported a different reference. An operator cannot reliably correlate the terminal
message with the retained diagnostic artifact.

Observed run: `r_sGWsYW3NXmXoT0NdnMdAB-1ApofWZibdUXmLbcyOQO8`

- CLI terminal reference: `diag_N1m8kjPjiqXbdHEgWfboW_Ve`
- Retained bundle summary reference: `diag_9a8155c2ab7cfa2b189cc47c`
- Both describe `blocked@topic_planning` and the bundle remains `retained` with
  `same_process` durability.

## Root Cause

`ResearchRunExperience._project_result()` published the retained session before it
constructed the terminal `RunFailure`. When a blocked terminal had no checkpointed
`diagnostic_ref` (either no incident, or a non-provider incident without one), the
two projections allocated independently:

- `RunSessionStore` derived and persisted a deterministic bundle reference from the
  trusted lifecycle fact.
- `_failure_for_terminal()` then called `_failure()` without a reference, causing
  `DemoDiagnosticJournal` to allocate a different random support-journal reference
  for the CLI.

This was a shared run-experience ordering defect, not a topic-planning-only defect.
The same split could affect any record-bearing blocked terminal without a prior
checkpointed diagnostic reference.

## Reproduction

The deterministic regression is the lowest responsible seam and covers both affected
shapes:

```bash
cd agent
env -u VIRTUAL_ENV uv run --extra operations pytest \
  tests/contract/test_run_experience_failures.py::test_blocked_terminal_without_checkpointed_reference_uses_the_retained_bundle_reference -q
```

Before the fix it failed twice: once for an unclassified blocked terminal and once
for a non-provider terminal incident without a reference. After the fix it passes
both cases and asserts that the terminal update, retained summary, and support
journal hold the same reference.

## Fix Relationship

Resolved in `harden-deep-research-workflow-outcomes` task 5.3. The run-experience
boundary now allocates one safe terminal reference before session publication: it
reuses a checkpointed incident reference when present, otherwise writes the support
journal once and passes that result to both `RecordBearingLifecycleFact` and
`RunFailure`.

The verified supplemental real run was
`r_TslYsahrz0UPeenXC-O1DtYNKJnRr4AH71XUow20nmo`. It terminally blocked at `wave0`
with `structured_output`; CLI, retained bundle, terminal trace, and support journal
all reported `diag_53pN1ZHqaGjPq04E00IFZ1YY`.
