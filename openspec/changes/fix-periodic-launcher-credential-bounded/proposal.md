# Proposal

## Why

BUG-074: the periodic scenario
`test_prepared_entries_preserve_dependency_state_and_keep_launcher_credential_bounded`
has never passed on any credential-free machine — the entry-environment CI
workflow is red across its entire history, and the 2026-09-28 local run fails
the same way. The test scrubs every credential variable from its children
(`CHILD_SECRET_KEYS`) and writes an empty test-owned `.env`, then asserts the
launcher prints `本地前提检查已就绪` — but the real-mode readiness gate
(`_demo_core.resolve_real_demo_model_profile`) requires a non-blank model
credential in the environment. The two are unsatisfiable together; the
assertion stage can never run green.

The author's intent is reconstructable from the launcher itself:
`run/real-research.sh` exports the model selector and runs the scripted
real-mode entry with a deliberately engineered default question ("list
separators make the extractor withhold subjects, and HITL1 then blocks the
auto-policy run **before the first model call**"). The intended journey is
readiness → scripted run → HITL blocks → `结果类别: research.blocked` →
non-zero exit → no credential names in output — a credential-bounded launcher
verification. What the scenario never supplied was the bounded fake
credential the readiness gate needs.

## What Changes

- The scenario's launcher stage asserts the journey the product actually
  offers a credential-free machine: with every real secret scrubbed and an
  empty test-owned `.env`, the real-mode readiness report honestly says the
  model configuration is not ready, prints its remediation guidance, exits
  non-zero, and never echoes credential variable names. The previously
  asserted ready-then-blocked journey (`本地前提检查已就绪` +
  `结果类别: research.blocked`) is removed as unsatisfiable: an injection
  experiment measured that fake credentials letting readiness pass drive
  `topic_planning` into a REAL model call against the live endpoint (HTTP
  401, `provider.authentication_failed`) — that journey belongs to
  credentialed manual lanes, not the credential-free periodic lane.
- BUG-074 closes with the fix; the credentialed-journey boundary is recorded
  in the change's design as an honest gap, not a silent one.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- None. `skip_specs: true` — a test-asset repair that restores the scenario's
  declared evidence (DPL-005, DPL-006, LCP-002 claims in the asset registry
  are unchanged); no product, runtime, or launcher behavior changes.

## Impact

- Touched: `deep_research_harness/tests/scenarios_periodic/test_local_entry_environment.py`
  (the launcher stage of one scenario) and `_backlog/bugs/BUG-074…` (closure).
- No application source, launcher script, Makefile, or spec changes.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/`
  gitlink; this change owns no such boundary.

## Change Focus

- **Primary module / causal owner:** the periodic entry-environment scenario
  itself (`tests/scenarios_periodic/test_local_entry_environment.py`) — it
  answers "does the credential-bounded launcher journey behave as documented
  on a machine with no real credentials".
- **Seam classification:** wiring — the fix supplies the missing bounded fake
  credential the scenario's own design requires; no admission, control, or
  cognitive surface changes.
- **Question:** Can the launcher stage assert the honest credential-free
  journey (readiness not ready → remediation guidance → bounded output →
  non-zero exit) that the real-mode entry actually offers such a machine?
- **Necessary adjacent/external contracts:** the launcher's documented
  operator-entry policy (`run/real-research.sh`, its engineered default
  question); the real-mode readiness gate (`scripts/_demo_core.py`); EVH-005's
  credential-free periodic lane requirement (fakes are not credentials — the
  lane stays credential-free).
- **Evidence seam:** the scenario is its own evidence — red on every
  credential-free machine (CI run 36354099368 logs; 2026-09-28 local run)
  before the fix, green after; the fake-credential rejection is itself
  measured evidence (HTTP 401 run, 2026-09-28) for why the ready-journey
  assertions had to go.
- **Not in scope:** changing the launcher, the readiness gate, or any product
  semantics; re-architecting the scenario; the periodic lane's other scenario.
- **Triggered review policies:** none: test-asset repair with no candidate, no human-judgment surface change, no control fact, no admission or recovery boundary, and no node-agent role.
