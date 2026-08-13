# Spec / Implementation Alignment Audit

> Audit date: 2026-08-12
> Snapshot: `65df2571108cc6b4b81f55d3ba8542786a810b39`
> Scope: `deep_research_harness/` against `openspec/specs/`
> Classification: current-state audit; no implementation, spec, configuration, or
> context file was changed

返回[总览](alignment-audit-00-current-state.md)。CONTEXT 与治理边界的发现分别见
[20 - Context](alignment-audit-20-context.md) 和
[30 - OpenSpec Governance](alignment-audit-30-openspec-governance.md)。

## Executive conclusion

The repository has a strong deterministic conformance baseline, but the green gates do
not prove complete semantic alignment.

- No P0 implementation/specification mismatch was found.
- Two P1 contradictions remain in approved main-spec authority: the Cognitive
  Evaluation Rubric/Runner boundary (A-003), and whether an external diagnostic may
  survive Bundle loss (A-004).
- The implementation currently makes a coherent choice for A-004 (Bundle-local only),
  but one approved main spec requires the opposite behavior. A-003 is less safely
  resolvable from current authority because newer evaluation-hardening requirements and
  current execution admission both depend on rubric criteria while the Cognitive
  Evaluation Suite contract forbids the Rubric as execution input.
- Requirement IDs are mechanically complete at the current `@impl` level, but that
  mechanism is intentionally too weak to establish requirement-by-requirement semantic
  conformance (A-009). This is a coverage limitation, not evidence that 183 or 248
  requirements are unimplemented.

The upstream-root/configuration residue and `CONTEXT.md`-only findings are intentionally
owned by the sibling governance and context reports. They are not duplicated here.

## Audit method

The audit used only repository-owned application, specification, governance, test, and
Git metadata. It did not inspect or modify `deerflow/` source.

Evidence was evaluated in both directions:

1. Main spec requirement to typed contract, production behavior, and deterministic test.
2. Material production behavior back to an approved main-spec owner.
3. Governance checker behavior itself, rather than treating a green exit code as proof
   of the stronger claim being audited.
4. Current Git history where it distinguishes a live contract from already-corrected
   historical state.

Finding labels have strict meanings:

- **Confirmed mismatch**: two current authorities, or current code and an approved main
  spec, require incompatible behavior.
- **Stale or ambiguous**: prose cannot be read as a unique current contract.
- **Coverage gap**: current checks do not establish the stronger alignment claim; this
  is not itself an implementation failure.
- **Aligned**: the inspected sources agree and the relevant deterministic evidence
  passed at the audited snapshot.

## Findings

### A-003 - P1 - Confirmed mismatch: Rubric/Runner execution boundary has two incompatible owners

#### Conflicting authority

The Cognitive Evaluation Suite main spec says a case-linked Rubric is available to
review but **must not be an execution input**:

- `openspec/specs/cognitive-evaluation-suite/spec.md:14-21`

The glossary selects the same interpretation more strongly: the Runner does not read a
quality rubric, and the Rubric is read only by upper review:

- `deep_research_harness/CONTEXT.md:310-319`
- `deep_research_harness/CONTEXT.md:328-334`

However, newer approved evaluation-hardening requirements make `review_criteria` part
of each executable scenario fixture and require admission to reject missing or invalid
rubric data before subject construction:

- Wave0: `openspec/specs/evaluation-hardening/spec.md:868-878`
- Wave1: `openspec/specs/evaluation-hardening/spec.md:910-938`
- Wave2: `openspec/specs/evaluation-hardening/spec.md:953-970`

This is not merely a naming disagreement. Current runtime admission reads the Rubric
file, extracts its criteria, and rejects the case when those criteria do not equal the
scenario fixture's `review_criteria` set:

- registry admission invokes rubric verification:
  `deep_research_harness/src/deerflow_deep_research/runtime/evaluation/controls.py:22-38`
- the Rubric is parsed and compared with executable scenario metadata:
  `deep_research_harness/src/deerflow_deep_research/runtime/evaluation/controls.py:80-113`
- typed HITL1/Wave0/Wave1/Wave2 scenario contracts require `review_criteria`:
  `deep_research_harness/src/deerflow_deep_research/domain/evaluation.py:233-276`,
  `314-346`, `398-423`, and `488-520`
- the Runner passes the complete case fixture into the execution context:
  `deep_research_harness/src/deerflow_deep_research/runtime/evaluation/runner.py:121-145`
- the multi-scenario production adapter passes each complete scenario and fixture to
  dependency/state factories:
  `deep_research_harness/src/deerflow_deep_research/runtime/evaluation/subjects.py:86-100`

The full Rubric prose is not passed directly to a model-facing node. Nevertheless, it is
a required input to execution admission, and its criterion identifiers remain available
inside the execution fixture. That behavior cannot satisfy the unqualified statement
that the Runner does not read the Rubric and the Rubric is not an execution input.

#### Impact

There is no single authoritative answer for a future evaluation change. An author could
correctly follow CES and remove Rubric-dependent admission, or correctly follow EVH and
preserve it. Either choice can be rejected by the other approved main spec.

The separation between objective execution evidence and later cognitive judgment is
still present; this finding does not claim that the Runner currently assigns a cognitive
grade. The conflict is specifically about admission and scenario metadata authority.

#### Required decision

Choose one of these contracts through an OpenSpec change before modifying the code:

1. **Review-only Rubric**: execution admission may retain only an opaque Rubric identity
   or digest; it must not parse criteria, and subject-facing fixtures must strip
   `review_criteria`. Review admission owns criterion validation.
2. **Case execution metadata**: criterion IDs are admitted execution metadata used to
   prove scenario/control integrity, while Rubric content remains non-model-facing and
   cannot determine execution output. CES and `CONTEXT.md` must state this narrower
   boundary explicitly.

The second option is closer to the current implementation and the newer EVH main-spec
requirements, but that is a design decision, not something this audit can authorize.
Synchronize CES, EVH, `CONTEXT.md`, ADR 0025, typed contracts, admission code, and the
focused evaluation tests in the same change.

### A-004 - P1 - Confirmed mismatch: external diagnostics after Bundle loss

#### Conflicting authority

The research-run-experience main spec explicitly permits an external diagnostic to
outlive Bundle loss and requires presentation to preserve its safe category/reference:

- `openspec/specs/research-run-experience/spec.md:73-85`

Two other approved capabilities forbid that behavior:

- every retained diagnostic must stay in the selected Bundle, and the system must not
  retain an external diagnostic, Support Handoff, or fallback Journal after Bundle
  loss: `openspec/specs/research-run-session/spec.md:62-78`
- post-loss inspection must not seek an external Journal or Support Handoff:
  `openspec/specs/run-event-journal/spec.md:128-149`

The domain glossary currently follows `research-run-experience`, saying an External Run
Observation may outlive the Bundle:

- `deep_research_harness/CONTEXT.md:145-150`

#### Current implementation choice

The implementation follows the Bundle-local `research-run-session` / `run-event-journal`
side, not the `research-run-experience` wording:

- the domain contract describes observations as Bundle-local:
  `deep_research_harness/src/deerflow_deep_research/domain/run_observation.py:1-11`
- the store is constructed for one already-selected Bundle root and has no external
  discovery/control surface:
  `deep_research_harness/src/deerflow_deep_research/runtime/run_observation.py:1-14`
  and `73-95`
- an unavailable Bundle projection does not expose legacy observation facts:
  `deep_research_harness/tests/contract/test_run_experience_failures.py:52-70`
- a terminal diagnostic is retained in the Bundle Journal and no external support file
  is created:
  `deep_research_harness/tests/contract/test_run_experience_failures.py:106-135`
- deleting the Bundle makes diagnosis unavailable and cannot block a fresh start:
  `deep_research_harness/tests/integration/test_observation_lifecycle_separation.py:26-59`

Thus this is not a speculative future conflict: one approved main spec currently
describes behavior that the typed implementation and deterministic evidence reject.

#### Required decision

Resolve ownership through an OpenSpec change. The smallest coherent change is to retain
the current Bundle-local implementation and remove the post-loss external-diagnostic
promise from `research-run-experience` and the glossary. If external diagnostics are
actually required, they need a distinct typed owner, retention/redaction contract,
inspection boundary, and deterministic tests proving that they cannot become Run
identity, lifecycle authority, or recovery data. Do not leave “may exist but is never
read” implicit; that distinction must be the explicit contract.

### A-009 - P2 - Coverage gap: green requirement coverage is not semantic traceability

#### What the current gate proves

The current requirement checker proves useful structural facts:

- all 388 alive main-spec requirement IDs have at least one deterministic test-file
  docstring `@impl` reference;
- unknown and retired production annotations are rejected;
- registry/main-spec ownership and missing IDs are checked.

That is a valid baseline. It is not a requirement-to-assertion proof.

`check_project_req_coverage.py` scans each `test_*.py` file that contains any test
function, then collects `@impl` IDs from module, class, and function docstrings:

- `openspec/governance/check_project_req_coverage.py:39-70`

It finally compares only the set of declared requirement IDs with the set of collected
docstring IDs:

- `openspec/governance/check_project_req_coverage.py:138-152`

Consequently, an annotation can count without being bound to the test function that
asserts the requirement's scenario, and the checker does not inspect assertion meaning.
Production annotations are validated when present, but production-source completeness
is not required:

- `openspec/governance/check_project_req_coverage.py:93-135`

#### More precise evidence is intentionally partial

The central evidence assets are stronger because they name collected selectors, seams,
asset class, authenticity, and risks. At the audited snapshot:

- `EVIDENCE_CLAIMS`: 400 records covering 205 unique requirement IDs;
- `REQUIREMENT_IMPACTS`: 171 records covering 140 unique requirement IDs;
- alive main-spec requirements: 388.

The impact validator validates only entries that exist; it does not require one for
every alive requirement:

- `deep_research_harness/tests/assets/requirement_evidence.py:1442-1487`

The evidence validator requires deterministic `@impl` for every alive ID, but stronger
asset-class requirements only for the small explicit policy set:

- policy set: `deep_research_harness/tests/assets/requirement_evidence.py:76-105`
- validator: `deep_research_harness/tests/assets/requirement_evidence.py:1606-1643`

This partiality is deliberate. The evaluation-hardening spec says only selectors used by
the evidence policy or inventories need central claims, and ordinary collected tests
must not be duplicated into a second exhaustive catalog:

- `openspec/specs/evaluation-hardening/spec.md:98-100`

Therefore, the 183 alive IDs without a central claim and the 248 without a requirement
impact are **not** 183 or 248 missing implementations. They quantify the limit of what
the stronger evidence catalogs can answer during this audit.

#### Recommendation

Do not make `EVIDENCE_CLAIMS` exhaustive. Instead, add a bounded semantic-alignment rule
for high-risk or changed requirements: record the owning production seam, exact scenario
selector, and the assertion/risk being proved when a requirement is introduced or
materially changed. Keep plain `@impl` as the inexpensive global inventory, and use the
stronger mapping for change review and periodic audits. A detector fixture should prove
that a file-level annotation with an unrelated test cannot satisfy that stronger rule.

## Aligned baseline

The following were aligned at the audited snapshot:

- 49 main specs passed both project structure validation and
  `openspec validate --all --strict` (49 passed, 0 failed).
- Requirement governance reported 392 registered IDs, 4 retired, 0 orphan; therefore
  388 alive IDs are owned by current main specs.
- No active OpenSpec change was present, so no pending delta competes with main-spec
  authority.
- Architecture governance, Agent Charter governance, fixture-source isolation,
  requirement-to-test coverage, Ruff, formatting, and lock consistency all passed.
- The current editable dependency metadata in `pyproject.toml` and `uv.lock` agrees on
  `../deerflow/backend/packages/harness`. Installation-path prose and upstream topology
  policy residue are covered by the sibling governance report.
- DRC-010 apply/archive guidance is live policy, not historical residue: its main-spec
  owner, checker, and focused tests remain present. It should not be removed merely
  because it is operationally detailed.
- The Charter authority boundary restored by `c4efe6f` is present at this snapshot; the
  prior missing-line state is historical and is not a current finding.

## Verification record

Run at `65df2571108cc6b4b81f55d3ba8542786a810b39`:

```text
cd deep_research_harness && UV_OFFLINE=1 make verify
  governance / lock / Ruff / format / test-assets / req coverage: passed
  fast:        2494 passed, 3 deselected
  integration: 237 passed, 4 skipped, 32 deselected
  workflow:    35 passed, 2784 deselected

openspec validate --all --strict
  49 passed, 0 failed
```

The four integration skips are the explicit real-Gateway-unavailable cases in
`tests/integration/test_gateway_identity.py`; they do not invalidate deterministic
spec/implementation alignment, but they also provide no live Gateway evidence.

## Recommended order

1. Resolve A-003 first because it affects what evaluation admission is allowed to read
   and therefore how future cognitive-program evidence is designed.
2. Resolve A-004 next by selecting one post-loss diagnostic contract across RER, RUS,
   REJ, the glossary, and tests.
3. Address A-009 as governance hardening after those semantic decisions. It should not
   block the two main-spec corrections and should not create an exhaustive duplicate
   test catalog.
