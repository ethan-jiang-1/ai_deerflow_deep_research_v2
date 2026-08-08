## Why

Wave2 synthesis and targeted evidence already constrain tools, candidate schemas, and deterministic
admission, but their evidence currently proves structural conformance rather than the quality of the
bounded synthesis, gap, retrieval, and review judgments. The next roadmap step makes those existing
model-visible criteria and feedback boundaries explicit without turning a model candidate into evidence,
an artifact, a gate verdict, or a route.

## What Changes

- Calibrate Wave2's existing accepted-evidence synthesis and zero-tool repair policies so candidates
  distinguish supported findings, bounded relations, honest gaps, and the difference between a candidate
  gap and deterministic searchable-gap projection. The repair receives only the same accepted-evidence
  assignment, bounded invalid draft, and a compact closed parser/semantic-failure category rather
  than a raw exception; it cannot retrieve or create backing.
- Calibrate targeted evidence's existing one-retrieval worker, zero-tool repair, SourceDiagnostic, and
  ClaimVerifier policies so every candidate remains scoped to one gate-projected gap or assigned
  references, preserves provenance and uncertainty, and cannot make a critic verdict, result artifact,
  ledger entry, or convergence decision authoritative.
- Add a third, separate twelve-case evidence-judgment calibration corpus: one normal and one highest-risk
  case for each Wave2 synthesis/repair and targeted worker/repair/SourceDiagnostic/ClaimVerifier branch.
  It reuses the typed optional live-rubric report contract while remaining distinct from the intake/planning
  and evidence-intake corpora, `LIVE_CANARIES`, and the lane-neutral `ScenarioCase` registry.
- Retain deterministic request composition, tool posture, repair/review containment, materialization,
  non-admission, gate, and route proof. Credentialed live evaluation is explicitly selected and
  supplemental: the targeted worker uses a real model-and-web branch runner after strict preflight;
  Wave2 and targeted zero-tool branches use a real model-only runner after model preflight.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `wave2-synthesis-node`: Make accepted-evidence synthesis and repair judgment criteria model-visible
  while preserving read-only execution, deterministic materialization, searchable-gap projection, and
  gate authority.
- `targeted-evidence-loop`: Make gap-scoped retrieval, repair, and assigned-reference review criteria
  model-visible while preserving worker/controller, artifact, ledger, convergence-gate, and route authority.
- `evaluation-hardening`: Add a separate evidence-judgment corpus with branch-specific deterministic
  conformance and selected live judgment evidence without changing canonical live-canary governance.

## Impact

- Affected production code is limited to the Wave2 and targeted-evidence capability Markdown, prompt
  builders, and only the existing repair/review invocation seams needed to deliver bounded feedback.
- Affected test-owned evidence includes the prompt catalog, branch evidence ledger, requirement evidence,
  calibration corpus, selected live runner/report resolver, and focused graph/integration/live tests.
- No modification is proposed under `backend/` or `frontend/`; no public API, graph topology, provider
  selection, evidence schema, checkpoint, ledger, gate, or route contract changes.

## Change Focus

- **Primary module / causal owner:**
  `agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/` owns the first
  accepted-evidence synthesis candidate and its zero-tool repair.
- **Question:** Can the existing Wave2 and necessary targeted-evidence branches produce conservative,
  assignment-faithful synthesis and gap/evidence-review candidates for a bounded labeled corpus while
  preserving their current deterministic artifact, admission, convergence, and route owners?
- **Necessary adjacent/external contracts:** `graph/nodes/targeted_evidence/` answers whether the
  gate-projected gap and assigned-reference branches preserve gap identity, provenance, uncertainty, and
  review-only scope; `evaluation-hardening` answers how a third separate corpus, strict model/web
  preflight, deterministic conformance, and selected live judgment evidence remain distinguishable.
- **Evidence seam:** Wave2 and targeted prompt builders plus their real node/subgraph repair or critic
  invocation seams for deterministic request/admission assertions; a separate selected `requires_llm`
  calibration case with a typed rubric for each judgment claim.
- **Not in scope:** `backend/`, `frontend/`, Wave0/Wave1 intake, HITL1/topic planning, HITL2/readiness/
  final delivery, provider selection, runtime bridge policy, tool inventory, graph topology, retry or
  convergence budgets, evidence schemas, canonical live-canary count or deadline budget, checkpoint/ledger
  mutation, gate/route authority, and any claim that a source or research conclusion is true.
- **Triggered charter policies:** change-admission, node-agent-workflow-integrity, workflow-outcome-review

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Wave2 synthesis | node-agent | Given graph-assigned topic context and accepted evidence, what supported findings, relations, and honest gaps can be proposed without treating a gap as routing authority? | Topic registry, accepted submission refs, and output contract are graph-assigned scope; evidence text remains untrusted data. | Forbidden; the generated request and zero-tool bridge middleware enforce no dispatch. | `SynthesisResult`; parser/semantic validator, materializer, gate-preview builder, and Wave2 gate alone admit content or derive a projection. | Existing one zero-tool repair; malformed, gaps-only, or unbacked output follows the current non-publication/exhaustion path. | Real Wave2 request/repair tests plus artifact and gate-preview non-admission tests. |
| Wave2 synthesis repair | node-agent | Can one invalid bounded synthesis draft be corrected only against the same accepted-evidence assignment, or honestly retain a gap? | Supplied accepted evidence and a compact parser/semantic-failure category constrain repair; draft is untrusted. | Forbidden; repair request and bridge middleware expose no tools. | `SynthesisResult`; existing parser, semantic validator, materializer, preview builder, and gate remain owners. | One existing repair only; failure remains existing exhausted/non-publication behavior. | Real-node repair test proves bounded feedback, no tools, and no artifact/projection on invalid repair. |
| Targeted evidence worker | node-agent | For one gate-projected gap, which bounded source metadata and resolution status can one permitted retrieval support? | Assigned gap id is trusted and immutable; retrieved material is untrusted. | Exactly one permitted retrieval; request window is enforced by bridge middleware and local capability/runtime policy. | `TargetedWorkerOutput`; existing validator, work-unit controller, materializer, and ledger admit only valid same-gap candidates. | Existing single zero-tool repair after parser/schema/wrong-gap failure; controller owns later failures and convergence. | Real targeted worker path proves exact tool posture, same-gap validation, and controller/ledger non-admission. |
| Targeted evidence repair | node-agent | Can one invalid targeted-worker draft be made contract-valid for the same gap using only retained observations and closed validation facts? | Assigned gap and closed failure metadata are trusted bounds; draft is untrusted. | Forbidden; repair request and bridge middleware expose no tools. | `TargetedWorkerOutput`; existing validator/controller/materializer/ledger owners remain unchanged. | One existing repair; invalid result follows existing fail-closed work-attempt path. | Subgraph repair test proves one no-tool call, preserved gap identity, and no artifact or ledger record on failure. |
| Targeted SourceDiagnostic | node-agent | What bounded diagnostics can be proposed about only the assigned source references and delimited content? | Assigned references are trusted bounds; source contents are untrusted. | Forbidden; generated request and zero-tool bridge middleware prevent tool dispatch. | Diagnostic candidate; existing validator/materializer bind identity and decide artifact admission. | Current targeted dispatch directly propagates invocation, parser, and validation failure; this change adds no suppression, retry, or gate authority. | Focused critic test proves assigned-reference containment, no artifact on malformed/out-of-scope output, and unchanged direct failure boundary. |
| Targeted ClaimVerifier | node-agent | What support, counterevidence, or uncertainty can be proposed for supplied claims against only assigned evidence references? | Assigned references constrain candidate refs; claim/evidence material is untrusted. | Forbidden; generated request and zero-tool bridge middleware prevent tool dispatch. | Claim-verdict candidate; existing validator/materializer bind references and publish any review artifact. | Current targeted dispatch directly propagates invocation, parser, and validation failure; this change adds no suppression, retry, or route authority. | Focused critic test proves reference containment, no artifact on malformed/out-of-scope output, and unchanged direct failure boundary. |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Wave2 initial parse, semantic, or gaps-only failure | Wave2 parser and semantic validator | Wave2 node invokes its existing one zero-tool repair with bounded draft, compact parser/semantic-failure category, and assigned evidence | Existing non-publication or exhausted Wave2 outcome | Existing gate/phase handling only after a valid candidate; no model route | Real-node malformed/gaps-only repair tests and artifact/preview absence assertions |
| Wave2 invocation or repair failure | Invocation normalization and Wave2 phase owner | Existing bounded phase/gate handling; no new retry | Existing classified incident or blocked/exhausted terminal | Existing lifecycle projection | Invocation-failure test retains phase/cause and no synthesis authority |
| Targeted initial parse, schema, or wrong-gap failure | Targeted subgraph parser and same-gap validator | Targeted subgraph invokes exactly one existing zero-tool repair | Existing work-attempt failure with no result/source artifact or ledger record | Existing controller and convergence-gate path | Targeted repair/failure tests prove one repair and no publication on invalid result |
| Targeted worker or repair invocation failure | Invocation normalization and work-unit controller | Existing controller retry/allocation and convergence bounds | Existing classified work-attempt failure | Existing controller/gate decision only | Focused invocation failure test proves safe cause reaches controller without authority |
| Targeted critic malformed, out-of-assignment, or invocation failure | Targeted `dispatch_critic` plus parser/model validation and materializer | Current direct dispatch propagates the failure; the change adds no local recovery, retry, terminal projection, or route writer | No targeted-node terminal disposition is proposed; the failure remains outside this change's calibration scope | Existing outer graph/runtime handling, without a new critic retry or route | Critic containment tests prove no artifact before propagation and preserve the direct failure boundary |
| Selected live calibration hard-invariant or execution failure | Test-owned selected runner and production branch parser/local validator | None; live evaluation has one outer attempt and does not invoke production recovery | Strict failed selected live run without rubric disposition | Operator fixes credentials/configuration or records failure outside production state | Selected-runner tests prove preflight, tool bounds, parser/validator boundary, and no rubric result |
