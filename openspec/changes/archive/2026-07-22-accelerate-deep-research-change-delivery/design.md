## Context

The 2026-07-22 baseline measured `make test-fast` at 65.6 seconds. Most of the
cost is not model, network, or lifecycle behavior: repeated `pytest --collect-only`
processes consume roughly 20--25 seconds, the live architecture contract launches a
separate Python process, and one hash-chained ledger test constructs and parses all
4,096 records. The same contract suite already has clear lane, ledger, and
architecture authorities; this change must make their evidence cheaper to run, not
less meaningful.

The work is wholly project-owned under `agent/`, OpenSpec governance, and test
metadata. It has no graph-node, typed `ResearchState`, checkpoint, node-agent,
sandbox-artifact, configuration, skill, MCP, ACP, Agent/SOUL, or Gateway surface.
`backend/` and `frontend/` remain untouched.

## Goals / Non-Goals

**Goals:**

- Make normal deterministic edit-loop selections substantially faster and measure the
  resulting timing honestly.
- On the recorded reference environment, reduce `make test-fast` to at most 35
  seconds and attribute the result across collection, setup, and call work.
- Preserve exact lane selection, architecture checking, and ledger-limit semantics.
- Make the smallest relevant test command and its purpose discoverable.
- Keep active-change `tasks.md` as a compact, checkable progress record.

**Non-Goals:**

- Do not parallelize pytest, skip deterministic gates, lower production constants, or
  optimize model/provider/network latency.
- Do not claim a universal wall-clock guarantee across machines; the 35-second target
  is a measured local acceptance budget with recorded environment and timing output.
- Do not alter `make verify`'s membership, lifecycle behavior, or any production
  authority.

## Decisions

### Cache collector results only at an explicit, resettable test seam

Introduce a small collector service around a single complete project test catalog. A
short current-Python child process uses pytest collection hooks to emit node ids plus
inherited marker names once; callers filter that validated catalog in memory by their
existing paths and marker expression. Its cache key includes the agent root and command
shape, not the query expression, so lane selection, replay registry, regression
descent, workflow inventory, and asset governance share one successful collection.
Tests that use a temporary root or injected command retain the direct collector path
and reset the cache explicitly.

The service's production default is `sys.executable` running the small catalog helper:
the asset checker is already launched through `uv run`, so nesting `uv run` produces
needless setup work. Tests may inject a direct pytest command for failure fixtures,
but the injected tuple remains part of the cache key. This is preferred over caching
raw subprocess output because callers need one validated selector-set contract.

This is preferred over an unkeyed module-global set because collection configuration
and temporary-fixture roots are semantically meaningful. It is preferred over only
pytest fixtures because the production asset checker is also a command-line program
and must use the same collector semantics. Failure results are not cached, and a
known bad collector response remains a direct fail-closed smoke test.

### Separate checker logic from its CLI adapter

Extract or formalize a public Python-level repository-check function in
`check_project_architecture.py`; `main()` stays the thin argparse/exit-code adapter.
The live contract invokes the Python seam, while existing command-line tests retain a
subprocess assertion for argument parsing, exit behavior, and stderr. This removes
spawn cost only where the CLI protocol is not the subject of the test.

The agent test imports the governance module through the repository-root namespace
after explicitly adding that root to its test-only import path. No production package
or `backend/`/`frontend/` import direction changes.

### Preserve the ledger boundary by testing distinct invariants at their lowest seams

Keep the production constant assertion (`4,096`) and the early `MAX+1` rejection.
Replace the all-4,096 successful hash-chain round trip with a bounded representative
chain (for example 256 records) that proves canonical encode/parse and hash linkage.
The old test made the same construction/serialization assertion 4,096 times without
adding a distinct transition risk. If implementation shows an exact-success case has
a separate parser risk, add a named slow proof with a documented reason rather than
quietly returning it to every fast invocation.

### Name focused targets without creating a second release gate

Add focused targets for intake, retained observation, work units, and strict
checkpoint compatibility. Each invokes its exact, reviewed selector through one
timing wrapper that prints elapsed time and a stable purpose label. These are edit-
loop aids only: `make verify` remains the canonical full deterministic gate and
continues to invoke the established lanes and governance checks.

### Make evidence escalation reviewable in existing test-owned metadata

Add a typed `RequirementImpact` record and validator beside the existing
`RequirementEvidenceRule` metadata in `agent/tests/assets/requirement_evidence.py`.
The additive map binds each requirement changed by a test-evidence change to its
owning contract, lowest production seam, normal exact selector, distinct risk, and
optional bounded escalation rationale. Its selector must resolve through the existing
claim catalog and collected selection. The default is at most one pure contract/unit
proof, one wiring integration proof, and one user-path/workflow proof, each with a
distinct risk. This is a budget for duplicated proof, not a ceiling on all test cases
within one risk family. Trace replay, live, or full-real evidence is permitted only
when it adds a named risk unavailable below that seam.

### Enforce CI duration evidence from the existing fast lane

Extend the existing fast-lane invocation to write a deterministic JUnit report and
still print `--durations=20`. A project-owned duration checker reads that report and
rejects an individual test over five seconds unless a typed waiver names its exact
selector, distinct reason, owner, and expiry/review point. The existing
`agent-tests.yml` deterministic job invokes this policy after the canonical verifier;
the target does not run a second broad test suite. This chooses a bounded failure with
explicit waivers over a warning that would silently normalize regressions.

### Keep aggregate performance acceptance measurable but reference-scoped

Add a project-owned benchmark report that records the exact command, timestamp,
Python/platform identity, selected-test count, and total wall time. It records
collection separately through the collector seam and setup/call phase durations through
a narrowly enabled pytest timing hook or report; its schema is validated with
deterministic fixture data. The final change evidence repeats the recorded baseline
conditions and must show `make test-fast` at or below 35 seconds. This is a change
acceptance result on the named reference environment, not a flaky universal CI
wall-clock assertion; CI instead enforces the portable five-second per-test policy.

## Risks / Trade-offs

- [Cache hides a changed collector input] -> Key every semantically relevant input,
  do not cache failures, and test reset/temporary-root behavior plus a malformed
  collection response.
- [In-process checker diverges from CLI] -> Keep `main()` as an adapter over the same
  function and retain at least one CLI-level contract test.
- [Smaller ledger sample misses the exact limit] -> Assert the production maximum,
  retain `MAX+1` early rejection, and justify the representative round trip as the
  separate serialization/linkage proof.
- [Target proliferation creates competing verification] -> Document each focused
  target as non-release and retain the existing `verify` composition unchanged.
- [Timing threshold flakes across machines] -> Enforce the five-second per-test CI
  budget only through the committed JUnit checker; every exception has an expiring,
  reviewed waiver and local timing remains visible rather than being treated as a
  portable pass/fail claim.
- [Aggregate target is confused with CI portability] -> Require the 35-second result
  only in the final benchmark evidence recorded under the same reference conditions;
  CI retains the selector-level duration policy.

## Migration Plan

1. Add red tests and an impact-map format before caching or changing targets.
2. Implement and measure one optimization at a time: collection, checker seam,
   ledger boundary, then focused targets/duration policy and reference benchmark.
3. Update evidence metadata and active `tasks.md` after each group with the exact
   selector, elapsed time, and next smallest proof.
4. Run focused targets during implementation, then the unchanged offline `make
   verify`, CI duration-policy target, strict OpenSpec validation, and
   diff/protected-path checks before archive.

Rollback is a source-only revert of the cache, helper, targets, and test refactor;
there is no deployed state, migration, restart, or compatibility data to unwind.

## Open Questions

None. The five-second limit is a CI per-test budget with explicit typed waivers, not a
claim about every local machine; `requirement_evidence.py` is the sole impact-map
authority.
