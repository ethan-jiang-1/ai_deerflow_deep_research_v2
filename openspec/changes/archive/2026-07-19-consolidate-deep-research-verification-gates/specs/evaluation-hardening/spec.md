> req: EVH-009, EVH-010

## MODIFIED Requirements

### Requirement: Release gate combines deterministic CI with optional LLM canary

The release system SHALL expose five focused, pairwise-disjoint selections: network-free fast correctness, network-free integration correctness, network-free deterministic workflow conformance, credentialed short live behavioral evaluation, and manual full-real release acceptance. In this stable requirement title, `optional` means that credentialed LLM execution is outside the default deterministic path; an explicitly selected live/release run remains strict and cannot skip. `make test` SHALL remain the exact pytest-only union of the three focused zero-API selections. `make install` SHALL prepare the locked `operations` and `demo-tui` extras required by that union and the canonical verifier through `uv sync --locked`; it SHALL NOT rewrite `uv.lock`. The canonical complete deterministic verification command SHALL be `cd agent && make verify`, an explicit local aggregate of those selections plus root governance, lock consistency, lint, test-asset governance, and requirement coverage; it is not itself a disjoint lane. `verify` SHALL export target-specific `UV_NO_SYNC=1` to every prerequisite recipe, including subprocesses launched by a prerequisite, so existing `uv run` commands cannot implicitly synchronize the environment. After `make install` or matching CI setup succeeds, `UV_OFFLINE=1 make verify` SHALL be executable without package provisioning, environment mutation, model API, credentialed command, live/release/Postgres selection, or network test; an unprepared environment SHALL fail rather than repair itself. Its `governance` member SHALL run the three root OpenSpec checkers against the repository root. OpenSpec archive guidance SHALL reference that canonical command for deterministic verification instead of copying its components, while strict change validation and boundary/diff evidence remain separate archive conditions. Existing agent `jobs.deterministic` workflow definitions SHALL prepare the same locked extras then delegate to the same target without becoming evidence that remote CI is configured or operational. Real-model tests SHALL carry the `requires_llm` marker, the live selector SHALL be `requires_llm and not release_e2e`, and the release selector SHALL be `requires_llm and release_e2e`; governance SHALL reject a `release_e2e` test missing `requires_llm`. Missing credentials in an explicitly selected live or release lane SHALL fail preflight rather than silently skip. Live evaluation SHALL include the existing start-to-HITL1, HITL1-to-topic-planning, and one-topic Wave0 prefixes plus directly seeded Wave1, Wave2 synthesis, and targeted-evidence focused-node canaries. Every selected live case SHALL report stable case identity, hard-invariant outcomes, typed metric statuses and evidence bases, attempts/retries, tokens, tool calls, cost when available, wall time, and bounded redacted diagnostics. Full-real acceptance SHALL use unique thread, run, and research identities and report every retry.

#### Scenario: Canonical local verification contains every deterministic gate
- **WHEN** a developer invokes `cd agent && make verify` on the local checkout
- **THEN** it SHALL run root governance against the repository root, lock consistency, lint, test-asset governance, requirement coverage, fast correctness, integration correctness, and deterministic workflow conformance while excluding provisioning, live, release, Postgres, and other credentialed or network-dependent test lanes

#### Scenario: Canonical setup makes verification offline-capable
- **WHEN** a developer completes `cd agent && make install`
- **THEN** it SHALL have installed the locked `operations` and `demo-tui` extras without rewriting `uv.lock`, so `UV_OFFLINE=1 make verify` can execute without resolving, downloading, synchronizing, or mutating the environment

#### Scenario: Verification refuses implicit environment preparation
- **WHEN** `UV_OFFLINE=1 make verify` reaches a `uv run` prerequisite
- **THEN** the target-scoped exported `UV_NO_SYNC=1` value SHALL be inherited by that prerequisite and its subprocesses, so an absent or incomplete prepared environment fails rather than being synchronized during verification

#### Scenario: Archive and workflow definitions do not fork the gate list
- **WHEN** local contract governance inspects OpenSpec archive guidance and the existing agent deterministic workflow definitions
- **THEN** deterministic archive guidance and each scoped `jobs.deterministic` definition SHALL delegate to `cd agent && UV_OFFLINE=1 make verify` or its agent-working-directory equivalent, and SHALL NOT maintain a second component command list; strict change validation and boundary/diff conditions remain separate from that command

#### Scenario: Release workflow changes cannot evade deterministic contract selection
- **WHEN** `.github/workflows/agent-release-e2e.yml` is the only workflow file changed on a pull request or main-branch push
- **THEN** the existing `agent-tests.yml` PR/push path filters SHALL select its deterministic contract without changing the release workflow's own trigger or making hosted execution a completion condition for this change

#### Scenario: Archive finalization keeps scoped conditions explicit
- **WHEN** a change is prepared for archive
- **THEN** guidance SHALL require strict validation of that named change, `git diff HEAD --check` covering staged or unstaged changes, a recorded porcelain-v1 worktree/protected-path status baseline including untracked files, clean protected paths before and after this change (or direction/a clean worktree before applying), and applicable boundary/config/doctor/infra-probe evidence separately from the one canonical deterministic verification command

#### Scenario: Untracked protected file cannot evade boundary evidence
- **WHEN** a new untracked file appears below `backend/` or `frontend/` after the recorded worktree baseline
- **THEN** final boundary validation SHALL detect the protected-path status change rather than treating an empty tracked diff as proof that the change respected the boundary

#### Scenario: Protected-path checks use repository-root semantics
- **WHEN** final validation checks `backend/`, `frontend/`, `agent/uv.lock`, or `openspec/` paths after invoking an agent-local Make target
- **THEN** it SHALL return to the repository root before issuing Git or OpenSpec commands, so a relative pathspec cannot silently resolve under `agent/` and omit the intended surface

#### Scenario: Pytest selection remains distinct from complete verification
- **WHEN** a developer invokes `cd agent && make test` instead of `make verify`
- **THEN** it SHALL retain only the exact union of fast, integration, and workflow pytest selections, while the canonical complete verification gate additionally runs governance, lock, lint, asset, and requirement-coverage checks

#### Scenario: Remote CI is not required for local completion
- **WHEN** the canonical gate and its local composition contracts pass on a checkout with no hosted runner, branch protection, required checks, repository secrets, or team approval configuration
- **THEN** this change's deterministic verification and archive condition SHALL be satisfied without claiming that remote CI is configured or operational

#### Scenario: Deterministic workflow selection is explicit and non-empty
- **WHEN** deterministic verification collects fast correctness, integration correctness, and workflow conformance
- **THEN** the focused selections SHALL be pairwise disjoint, workflow SHALL select at least one zero-API `workflow` test, all three SHALL exclude live/release/Postgres tests, and their union SHALL equal the complete deterministic collection

#### Scenario: Late-node live canary uses production dependencies honestly
- **WHEN** Wave1, Wave2 synthesis, or targeted evidence is selected for focused live evaluation
- **THEN** its seed SHALL publish minimum valid predecessor authority through existing checkpoint/store interfaces, the case SHALL invoke the real focused node with a bounded derivative of its production policy and real external dependencies, apply reducer preview before gate evaluation where the production wrapper requires it, apply only the production gate/submit semantics that actually belong to that node, and disclaim public-entry, predecessor-lifecycle, production-recipe, and full-pipeline coverage

#### Scenario: Scheduled live budget is bounded as a whole
- **WHEN** all six focused live cases are enabled in the nightly job
- **THEN** each case SHALL have one outer attempt and explicit model/tool/token/time bounds, declared scenario deadlines SHALL sum to at most 900 seconds, each web case SHALL be at most 240 seconds, each zero-tool case SHALL be at most 120 seconds, and the existing 20-minute job SHALL retain at least five minutes for setup and cleanup

#### Scenario: Explicit live selection keeps strict preflight
- **WHEN** an operator or schedule explicitly selects live or release tests without every credential required by the selected cases
- **THEN** preflight SHALL fail with a typed readiness error rather than skip cases or silently reduce the selected set

#### Scenario: Focused live report is auditable without raw output
- **WHEN** a selected live case completes, degrades, or fails
- **THEN** its versioned report SHALL preserve the case identity, invariant results, metric applicability/authority, attempts, resource use, duration, and redacted typed diagnostics without model text, credentials, source URLs, or host paths

#### Scenario: Release acceptance uses isolated identity
- **WHEN** full-real acceptance is invoked more than once
- **THEN** every invocation SHALL use new thread, run, and research identities and SHALL NOT inherit a prior blocked or completed checkpoint

#### Scenario: Release acceptance remains singular
- **WHEN** the live suite expands to later provider-sensitive nodes
- **THEN** no additional routine full-real pipeline SHALL be introduced and the existing release lane SHALL remain the sole `FULL_REAL_PIPELINE` proof

#### Scenario: Test-only rebalancing does not spend release E2E by default
- **WHEN** implementation leaves the release runner and public entry unchanged and focused live cases expose no full-pipeline-only uncertainty
- **THEN** final validation SHALL collect the release selector and validate a committed minimal redacted attestation of the existing accepted run without requiring a fresh full-real execution

#### Scenario: Successful release proof survives local report cleanup
- **WHEN** raw `.reports/release` artifacts are absent from a clean checkout
- **THEN** a committed attestation SHALL still record schema version, scenario, source observation date, `source_report_sha256`, attestation base revision explicitly distinct from run revision, explicit unknown run revision, attempt/retry counts, all eight hard invariant results, accepted/citation counts, aggregate token/tool/time values, scoped source-archive scan verdicts, and scoped attestation scan verdicts without invocation ids, provider response shapes, model text, source URLs, credentials, or host paths

#### Scenario: Attestation provenance does not merge authorities
- **WHEN** an attestation contains release-run facts and redaction scan verdicts
- **THEN** it SHALL distinguish facts derived from the hashed source JSON, scan results recorded by the archived release gate with its committed source locator and original live/release target scope, and scans of the generated attestation itself rather than claiming every fact came from one source

#### Scenario: Attestation does not invent missing run metadata
- **WHEN** the source report has no embedded execution timestamp or code revision
- **THEN** the attestation SHALL preserve only the supported observation date, SHALL mark run revision unknown, and SHALL NOT substitute file modification time or a later repository revision as execution metadata

#### Scenario: Committed release documents cannot contradict the attestation
- **WHEN** a committed parity or release-status document describes the same evidence epoch
- **THEN** it SHALL agree with the attestation's achieved/not-achieved state or explicitly declare itself superseded

#### Scenario: Material release impact triggers scope review
- **WHEN** implementation must change production behavior or interfaces, including the release runner/public entry, or a focused live discovery cannot be validated below the full pipeline
- **THEN** the change SHALL return to proposal/design review before authorizing and recording a fresh isolated release run

### Requirement: Test selection and requirement traceability are mechanical

Stable commands and markers SHALL separately select fast correctness, integration correctness, deterministic workflow conformance, live evaluation, and release acceptance. The canonical complete deterministic command SHALL include the exact union of the three zero-API focused selections while excluding credentialed and deferred-provider tests. Every alive requirement SHALL retain at least one collected deterministic test-side `@impl` reference. Governance SHALL additionally scan Python module/class/function docstrings and comment tokens under the canonical production root `agent/src/**/*.py`, using the same top-level registry-entry and `[DEPRECATED]` semantics as requirement governance, and reject every production-source `@impl` ID that is absent from the canonical registry or marked `[DEPRECATED]`. Source decoding, parsing, or tokenization failure SHALL fail closed with an actionable repository-relative location; arbitrary string literals, tests, docs, generated reports, and archived artifacts SHALL NOT be treated as ownership. Production-source annotations remain optional implementation ownership and SHALL NOT substitute for collected test evidence. Governance SHALL reject focused-selection overlap, an empty workflow selection, scenario families without deterministic cases, cases without collected claims, contradictory inventory mappings, unknown requirement ids, uncovered alive requirements, and cross-lane requirements missing any asset class or authenticity declared by their evidence policy. Asset classes SHALL be treated as independent required evidence, not a single ordered minimum; a test-side `@impl` reference records implementation ownership but does not replace a required cross-lane evidence claim. Each validator SHALL have direct invalid-fixture coverage for every rule it owns; a collector, syntax-aware discovery scan, archive scan, or runtime detector that could succeed on an empty or mis-scoped input SHALL additionally retain a focused detector smoke case. `openspec/governance/req-registry.yaml` SHALL remain the only requirement registry and the named `req-registry.yaml.tmp` temporary copy SHALL be absent as a repository artifact.

For this requirement, function docstrings include both synchronous and async functions.

#### Scenario: Unknown or retired production ownership fails closed
- **WHEN** a Python docstring or comment under the canonical production source root contains an `@impl` ID that is unknown to the registry or marked `[DEPRECATED]`
- **THEN** requirement coverage SHALL fail with the offending requirement ID and repository-relative source path (and line when available)

#### Scenario: Valid production ownership does not create a coverage mandate
- **WHEN** production source references only alive registered IDs and some alive requirements intentionally have no production annotation
- **THEN** production ownership validation SHALL pass while existing test-side deterministic coverage remains independently required for every alive requirement

#### Scenario: Production discovery cannot pass from the wrong root
- **WHEN** a detector smoke fixture places a known invalid annotation under the canonical production source subtree
- **THEN** the syntax-aware source scan SHALL discover and reject it rather than pass from an empty or mis-scoped input

#### Scenario: Invalid production source cannot bypass ownership validation
- **WHEN** a Python source file under the canonical production root cannot be decoded, parsed, or tokenized
- **THEN** requirement coverage SHALL fail closed with an actionable repository-relative diagnostic rather than silently omit the file

#### Scenario: Temporary registry copy cannot become authority
- **WHEN** requirement governance inspects the repository registry surfaces
- **THEN** `req-registry.yaml` SHALL be the sole registry and `req-registry.yaml.tmp` SHALL be absent as a repository artifact

#### Scenario: Cross-lane requirement needs every declared evidence class
- **WHEN** an alive requirement is listed in the requirement-evidence policy with required deterministic, workflow, live, or release asset classes and one class is absent
- **THEN** requirement coverage SHALL fail with the requirement id, missing class or authenticity, and observed claims

#### Scenario: Ordinary requirement does not inherit a blanket workflow mandate
- **WHEN** a requirement is not authenticity-sensitive
- **THEN** an appropriate collected deterministic claim at its responsible seam SHALL satisfy coverage without an artificial workflow case

#### Scenario: Focused selections partition deterministic collection
- **WHEN** collection is performed for fast correctness, integration correctness, workflow conformance, and the complete deterministic aggregate
- **THEN** the three focused selector sets SHALL be pairwise disjoint and their union SHALL equal the aggregate, while live, release, and Postgres selectors remain excluded

#### Scenario: Empty scan cannot masquerade as enforcement
- **WHEN** collection, syntax discovery, archive scanning, or runtime detection is added or materially changed and its input is empty, relocated, or mis-scoped
- **THEN** a focused smoke case SHALL prove that a known target violation is detected, while pure validation rules SHALL retain direct minimal invalid-fixture tests

#### Scenario: Test-evidence authority survives change archival
- **WHEN** this delta is active, synchronized, or archived and a later change needs the current test-evidence contract
- **THEN** pending modifications SHALL be discoverable from the one active owning delta, approved semantics SHALL be discoverable from the `evaluation-hardening` main spec, exact evidence metadata SHALL remain in test-owned registries, executable collection SHALL remain agent-owned, and the governance authority/lifecycle policy plus concise OpenSpec/agent pointers SHALL route contributors without treating archived proposal, design, or tasks as current authority
