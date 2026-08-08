## Why

The deterministic Deep Research test lanes are credible but slower than their risks
require: repeated pytest collection, a subprocess-only architecture checker, and a
full-scale ledger round-trip dominate the edit loop. The measured 2026-07-22 baseline
puts `make test-fast` at 65.6 seconds, although the focused observation work itself
finishes in seconds.

This change makes the common deterministic edit loop materially faster without
weakening a requirement, hiding a collector failure, or treating the complete
verification gate as optional.

## What Changes

- Route every deterministic-governance collection consumer through one validated,
  keyed collector while preserving exact lane-selection and command-line collector
  coverage.
- Expose a reusable in-process architecture-checker seam and migrate its live
  repository contract test away from unnecessary process spawning; retain CLI coverage
  where command-line behavior is the subject.
- Split the ledger-boundary evidence into a fast representative round trip and a
  separate exact-limit proof so the 4,096-record production boundary remains tested.
- Add named focused Make targets for intake, retained observation, work-unit, and
  strict-checkpoint slices. Each reports its elapsed time and single stated purpose;
  `make verify` remains the complete deterministic gate.
- Establish a maintained impact/evidence map and enforce an explicit smallest-
  sufficient evidence budget: extra layers must prove a distinct risk and any
  escalation to trace replay, live dependencies, or full-real execution must be
  justified.
- Add a deterministic CI duration policy: report the twenty slowest fast-lane tests
  and reject an individual test over five seconds unless it has a reviewed, bounded
  waiver with a distinct reason.
- Produce one reference-environment fast-lane benchmark with separate collection,
  setup, and call attribution, and require the optimized `make test-fast` result to
  meet the plan’s 35-second aggregate acceptance budget.

## Capabilities

### New Capabilities

- `deep-research-delivery-efficiency`: Measurable, risk-preserving deterministic
  delivery acceleration for Deep Research test governance and focused developer
  verification (`DER-001` through `DER-006`).

### Modified Capabilities

- `evaluation-hardening`: Require smallest-sufficient, distinct-risk evidence-layer
  selection and an explicit justification for escalated evidence (`EVH-011`).

## Impact

- Affected project-owned surfaces: `agent/Makefile`, `agent/tests/`,
  `agent/scripts/check_test_assets.py`, test-evidence metadata, OpenSpec
  governance/specification artifacts, and `.github/workflows/agent-tests.yml`.
- The retained-session, graph, lifecycle, node-agent, checkpoint, sandbox, and
  product presentation contracts are unchanged. No runtime configuration, mount,
  dependency, skill, MCP, ACP, Agent/SOUL, or DeerFlow task-subagent surface is used
  or changed; there is no next-agent-build or Gateway-restart impact.
- No files under `backend/` or `frontend/` are modified.
- Evidence is deterministic unit/contract/integration coverage at the responsible
  collection, checker, ledger, and Make seams. Persisted replay, live dependencies,
  and full-real acceptance are out of scope unless a distinct risk is documented by
  the evidence policy.
