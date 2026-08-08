## Progress

- Current group: implementation complete; ready for archive.
- Completed evidence: 2026-07-22 baseline recorded `make test-fast` at 65.6s;
  repeated collection, architecture-checker spawn, and full-scale ledger round trip
  are the measured targets. First review normalized every collection consumer, CI
  duration enforcement, and impact-map ownership; strict OpenSpec and requirement-ID
  checks passed. Second review added reference-scoped aggregate acceptance: no more
  than 35 seconds with collection/setup/call attribution. Apply baseline recorded
  before implementation: only this change's planning artifacts and requirement registry
  were dirty; `backend/` and `frontend/` were clean. `RequirementImpact` red-green
  contract passed (`8 passed`). Unified catalog collection regression suite passed
  (`26 passed` in `5.68s`); its prior equivalent took `21.59s`, and the partition
  check fell from `9.20s` to `0.06s`. Architecture seam and CLI contracts passed
  (`19 passed` in `5.79s`); ledger boundary contracts passed (`9 passed` in `0.33s`),
  with the representative chain itself at `0.22s`.
- Next smallest selector: full deterministic verification.
- Elapsed time: focused collection suite `5.68s`; reference benchmark: collection
  `2.212s`, setup `1.135s`, call `25.668s`, total `30.175s` across 1652 tests.
- Blocker: none. Final evidence: `UV_OFFLINE=1 make verify`, duration policy,
  benchmark, strict OpenSpec validation, requirement registry validation, and
  `git diff HEAD --check` passed; protected `backend/` and `frontend/` paths remain
  clean. Review decisions: one collector interface, typed impact metadata in
  `requirement_evidence.py`, and five-second CI duration policy with bounded waivers.

## 1. Baseline And Evidence Map

- [x] 1.1 Record the implementation worktree/protected-path baseline and add typed
  `RequirementImpact` metadata plus its validator beside `RequirementEvidenceRule`:
  requirement, owning contract, lowest production seam, normal selector, distinct
  risk, and any escalation rationale (EVH-011).
- [x] 1.2 Add red governance tests for duplicate-layer rejection, explicit escalation
  rationale, and impact-map selector collection; register the map in the existing
  test-evidence authority without creating a competing catalog. Keep `tasks.md`
  progress as an archive-safe human record rather than an executable assertion
  (EVH-011).

## 2. Shared Collection

- [x] 2.1 Add red collector tests proving different deterministic lane queries derive
  from one successful project catalog while changed root, injected command, malformed
  output, empty output, and a failed collection do not return stale success; prove the
  prepared-process default uses the current interpreter rather than a nested launcher
  (DER-001).
- [x] 2.2 Implement the keyed, resettable successful-collection cache at the existing
  collector seam; migrate lane selection, replay registry, regression descent,
  workflow inventory, and asset governance callers without changing their selected
  sets or failure behavior. Mark the owning seam with `@impl DER-001` (DER-001,
  EVH-011).
- [x] 2.3 Run the focused selector, verify the collected deterministic partition and
  known-violation smoke cases, and record elapsed collection/setup/body timing in this
  progress section (DER-001).

## 3. Checker And Ledger Boundaries

- [x] 3.1 Add red checker tests for a reusable in-process repository-check seam and
  preserve a separate CLI invalid-input/exit-diagnostic test (DER-002).
- [x] 3.2 Refactor the architecture checker so `main()` delegates to that seam; move
  only the live repository contract test to the in-process seam and retain CLI
  subprocess coverage. Mark the owning seam with `@impl DER-002` (DER-002).
- [x] 3.3 Add red ledger tests separating the exact configured constants and
  `MAX+1` early rejection from a bounded canonical hash-chain round trip; include a
  known regression fixture for broken linkage (DER-003).
- [x] 3.4 Replace the all-4,096 successful round trip with the bounded representative
  proof, preserving exact-boundary assertions; document and mark any subsequently
  needed full-limit success proof as slow with its distinct risk. Mark the owning test
  surface with `@impl DER-003` (DER-003).
- [x] 3.5 Run focused architecture and ledger selectors, record their elapsed timing,
  and confirm no production ledger constant or checker CLI contract changed (DER-002,
  DER-003).

## 4. Focused Commands And Duration Guard

- [x] 4.1 Add red Make/contract tests for named intake, retained-observation,
  work-unit, and strict-checkpoint deterministic targets, including one stable purpose
  and elapsed-time report for each; prove they exclude live/release dependencies and
  do not replace `make verify`. Add red CI/duration-policy tests for JUnit parsing,
  five-second overflow, exact-selector waiver, missing reason/owner, and expired
  waiver rejection (DER-004, DER-005).
- [x] 4.2 Implement the timing wrapper and reviewed target selectors in `agent/Makefile`;
  keep the existing `verify` membership unchanged. Write the fast-lane JUnit report,
  print `--durations=20`, and add the project-owned duration-policy command with typed
  five-second waivers; invoke that command from `.github/workflows/agent-tests.yml`
  after canonical verification. Mark the owning implementations with `@impl DER-004`
  and `@impl DER-005` (DER-004, DER-005).
- [x] 4.3 Add duration-regression parser/checker coverage and record the CI baseline:
  a test over five seconds must have an exact, reviewed bounded waiver rather than a
  warning or a fabricated cross-machine local SLA (DER-005, EVH-011).
- [x] 4.4 Add red fixture tests for the reference benchmark report: required command,
  timestamp, Python/platform identity, selected-test count, distinct collection/setup/
  call durations, total, and invalid/missing phase data (DER-006).
- [x] 4.5 Implement the narrowly enabled phase-timing reporter and benchmark command;
  retain the report only as reviewed change evidence, not runtime product data or a
  universal CI wall-clock gate. Mark the owning surfaces with `@impl DER-006` (DER-006).
- [x] 4.6 Re-measure `make test-fast` after the three quick wins under the recorded
  reference baseline. Record collection/setup/call/total timing, residual top
  offenders, and an aggregate result of at most 35 seconds in the impact map and this
  progress section; otherwise leave the task open with the measured blocker (DER-001,
  DER-002, DER-003, DER-006).

## 5. Documentation And Completion Evidence

- [x] 5.1 Update `agent/AGENTS.md`, test-evidence metadata, the active acceleration
  plan, requirement registry/spec traceability, Make help, and deterministic CI
  guidance so contributors choose the smallest reviewed selector before complete
  verification; state that no `backend/` or `frontend/` path changed (DER-004,
  DER-005, DER-006, EVH-011).
- [x] 5.2 Run focused red-green tests after each group, then `cd agent && make format`,
  lint, test-assets, requirement coverage, `UV_OFFLINE=1 make verify`, strict OpenSpec
  validation, the separate duration-policy target over the verifier-produced fast-lane
  JUnit report, the reference benchmark command, `git diff HEAD --check`, and final
  protected-path status comparison.
  Record exact commands/results and final timings in this file before archive
  (DER-001, DER-002, DER-003, DER-004, DER-005, DER-006, EVH-011).
