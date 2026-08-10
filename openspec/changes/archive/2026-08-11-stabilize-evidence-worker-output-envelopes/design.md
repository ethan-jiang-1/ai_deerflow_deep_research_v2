## Context

See [proposal.md](proposal.md) and
`_backlog/bugs/BUG-024-real-demo-flaky-against-model-contracts.md` for the causal
evidence boundary. The current Wave0 and Wave1
initial prompt builders contain a detailed JSON instruction, but their repair prompts
are materially weaker and neither the capability method nor the request consistently
makes the tool-then-final-response boundary explicit. The existing parsers, Wave1 local
semantic validation, submit validator, and work-unit controller already reject invalid
output and preserve their current bounds.

The Bundle-local Journal currently records `initial` and `repair` validation events.
The worker subgraphs emit those facts at their local boundary, but the shared submit
component also emits its later result using those same labels. That makes a
parser-accepted candidate which later fails submission validation indistinguishable
from a worker-local repair stage. The current event and manifest contracts are version
2, so the new closed shape and new stage require an additive versioned representation.

The focused live evidence-intake runner invokes a production bridge and parser but does
not establish `SelectedBundleContext`. It therefore cannot exercise the intended
production agent context or preserve authoritative Bundle-local evidence.

## Goals / Non-Goals

**Goals:**

- Give each Wave0/Wave1 worker and repair branch a concise, unambiguous completion
  contract that a real model can follow after a tool turn.
- Preserve an unambiguous retained distinction between worker-local structural
  validation and later shared submit validation without retaining response content;
  existing bounded-retention health still reports any loss.
- Make focused live calibration a valid explicit-profile, Bundle-bound regression loop.
- Keep existing deterministic admission, recovery, and lifecycle owners unchanged.

**Non-Goals:**

- Build a generic output-schema language, add a new model agent, or use prompt text as
  an acceptance mechanism.
- Treat the Journal as a retry controller, a support store outside the Bundle, or a
  source of raw model/tool data.
- Use calibration to select a default profile or claim full-demo/research quality.

## Decisions

### 1. Keep output envelopes local to each node, but render them consistently for initial and repair requests

Each node package will own a small private renderer for its final completion contract.
The renderer will be used by both its initial and repair request builders; the matching
runtime-loaded capability Markdown will state the same cognitive sequence and final
self-check. Wave0 and Wave1 retain separate renderers because their source, claim,
baseline, and uncertainty contracts are deliberately different.

For initial workers, the contract will make the ordered interaction explicit: use only
the already-authorized retrieval window, consume the resulting observation, and finish
the final assistant turn with one standalone JSON object. For repairs, it will state
the same standalone object shape with no tool. The compact contract will name the exact
top-level and item keys, the required source floor, prohibited output forms, and a
short final self-check. It will not show a long placeholder document that resembles a
second schema or competes with the typed model.

The output envelope is a cognitive aid, not a validator. Existing parse, local semantic,
submission, and controller behavior remains the direct consumer of the candidate.

**Alternatives considered:**

- Relaxing the parser or accepting fenced/embedded JSON would hide the observed
  protocol failure and create an ambiguous content-admission boundary.
- A shared cross-node schema renderer would reduce a few strings but obscure the
  intentional distinction between Wave0 source intake and Wave1 baseline-aware
  evidence extraction.
- A separate repair agent or larger retry budget would add control complexity without
  evidence that the current bounded recovery is inadequate.

### 2. Classify the final response structurally before existing parsing, without extracting or retaining it

A small pure classifier will accept the in-memory final summary immediately before the
existing Wave0/Wave1 parser. It will return the closed `FinalResponseShape` value and
will neither mutate the summary nor supply a parsed candidate. Classification uses this
precedence:

1. Whitespace-only content is `empty`.
2. Any Markdown code fence is `fenced`.
3. A trimmed response that parses as one JSON object is `json_object`.
4. A non-standalone response containing a parseable JSON object is `embedded_json`.
5. Every other non-empty response is `prose`.

The classifier will be shared deterministic utility code because both node packages
need the same closed vocabulary and precedence. It will return only the enum; no input,
substring, parsing error, or discovered object is persisted, logged, or exposed.
`domain/run_observation.py` will own both the typed `FinalResponseShape` vocabulary and
this pure classification function, keeping the Journal fact and its meaning in one
existing dependency-safe module. Embedded-object detection will use the standard JSON
decoder rather than bracket slicing and will not return the decoded value.
Each worker subgraph passes that enum to its existing local validation observation for
both success and failure. Invocation failures that produce no summary continue to emit
their existing invocation fact and no response-shape fact.

**Alternatives considered:**

- Classifying with prompt heuristics or model output would make a diagnostic fact depend
  on an untrusted candidate.
- Persisting a truncated response would improve debugging detail but violates the
  Bundle Journal redaction boundary.
- Treating every JSON-looking response as `json_object` would collapse precisely the
  embedded/fenced cases needed to diagnose this defect.

### 3. Add a version-3 Event Journal representation with strict stage/shape rules

`RunEvent` will gain `post_candidate` as a validation stage and an optional closed
`response_shape` field. New Wave0/Wave1 worker-local `initial` and `repair` events will
write their shape; topic-planning and other existing validation events remain
shape-less. A `post_candidate` event will have a non-empty canonical code collection
and no response shape. Non-validation events cannot carry either field. The validation
rules will reject impossible combinations before persistence.

Newly established events and Journal manifests will use schema version 3. Readers will
continue to accept version 1 and 2 Bundles with no response shape and no
`post_candidate` stage; they remain read-only historical evidence, not inferred new
facts. The writer will neither append a v3 event to an older manifest nor rewrite or
upgrade older events/manifests. An attempted observation write to an older Journal
therefore follows the existing persistence-failure/incomplete-health path and cannot
alter graph or lifecycle execution. Summaries retain their existing version because
their representation is unchanged. Journal inspection will expose the enum when
present, and the retention/health mechanism remains unchanged.

The record protocol and recorder will accept the optional typed shape. The Wave0/Wave1
subgraphs are the only production graph producers of worker-local shape facts; the
selected test-only calibration runner may reproduce the same named parser/validator
boundary for its one direct branch. The shared work-unit component is the sole producer
of a later `post_candidate` fact: when its existing typed
`SubmissionValidationFailure` is caught, it records the current canonical codes with
that stage. It will stop emitting an empty submit-validation event on success and will
never reuse `initial` or `repair` for this later boundary. This is diagnostic-only; the
same exception and terminal update continue through the current controller path.

**Alternatives considered:**

- Reusing `initial` or `repair` for submit validation is backward-compatible in shape
  but falsely states where the failure occurred.
- A separate diagnostics file or external log stream would duplicate Journal storage
  and break the Bundle lifetime/inspection contract.
- Leaving the version at 2 would make older event semantics ambiguous and weaken
  validation of the new field combinations.

### 4. Make selected live calibrations admitted, profile-provenanced direct branches

For every selected case in the existing twelve-branch evidence-intake corpus, the live
runner will resolve a single registered demo profile through the same trusted
composition boundary used for explicit demo selection. Before it resolves a production
node dependency, it will create a fresh test-owned Bundle through the existing Bundle
admission path, establish its Journal, and obtain its `SelectedBundleContext`. The
existing projection/resolver then builds the direct production bridge context from that
selection; a test-only identity or a raw Bundle path is not an acceptable substitute.
The resolved profile supplies both the sole configured model and its safe
`ExecutionProfileEvidence`; the runner will not select a model through credential order
and then attach profile evidence independently.

The runner still invokes one generated branch request, not a controller or full graph,
and retains each branch's existing production parser/validator. For Wave0/Wave1 worker
and repair cases, it uses the production structural classifier, parser, and applicable
Wave1 local semantic validator, records the resulting bounded validation fact through
the Bundle recorder, and reads it back through supported Journal inspection. The two
critic branches retain their existing typed parser and rubric boundary and do not emit
a worker-local response-shape or validation fact. The rubric executes only after all
mechanical invariants pass. A structural or semantic failure is an attributable live
failure, not a limited quality result. The trusted selected profile is recorded only in
the admitted Bundle's admission fact and summary.

Each explicit profile is selected independently, with credentials/preflight checked
before admission and provider invocation. The `requires_llm` lane remains opt-in; the
normal deterministic verification selection neither runs it nor treats it as proof of
research quality. The focused regression matrix invokes each changed initial worker
branch once per available explicit profile; each matrix entry remains a one-branch run.

**Alternatives considered:**

- Continuing to pass a synthetic adapter identity bypasses the production selection
  contract and has already failed before provider invocation.
- Running the full demo for every profile hides the worker contract behind unrelated
  lifecycle failures and makes the feedback loop too slow.
- Manually injecting a profile into a Journal event would make provenance caller-owned
  rather than admission-owned.

### 5. Verify by distinct risk rather than repeating full-real execution

The implementation will use the following proof layers:

| Risk | Lowest responsible evidence | Supplemental evidence |
| --- | --- | --- |
| Completion contract drifts between initial and repair branches | Node prompt/capability tests assert exact closed keys, tool posture, and prohibited forms. | None. |
| Shape/stage becomes malformed or leaks content | Domain/recorder tests round-trip v3 events, reject invalid combinations, preserve v1/v2 reads, and scan serialized bytes for forbidden raw data. | Journal inspection presentation test. |
| A candidate follows the wrong recovery or admission path | Scripted real Wave0/Wave1 work-unit integration exercises tool turn, malformed result, one repair, local semantic failure, and submit-validation rejection. | None. |
| A real profile returns prose after its tool turn | Selected Bundle-bound live calibration runs each changed initial worker branch once per available explicit profile and reports a hard invariant failure or bounded rubric. | After the focused loop is stable, one fresh all-real demo Bundle per available profile must advance through both Wave0 and Wave1; this does not claim later delivery quality. |

This preserves the evaluation-hardening rule that real dependencies prove only the
output-distribution risk which deterministic scripted turns cannot prove.

## Risks / Trade-offs

- [A stricter prompt still does not guarantee compliant model output] → Keep the parser
  and existing bounded recovery fail-closed; use the profile-scoped live loop to measure
  rather than assert quality.
- [A response classifier accidentally becomes a permissive parser] → It returns only a
  closed enum before the unchanged standalone JSON parser; embedded and fenced content
  remains non-admissible.
- [Version-3 Journal records are unreadable after an immediate code rollback] → Do no
  destructive migration or rewriting; current readers retain v1/v2 support, and a
  rollback treats a newer Bundle Journal as unavailable rather than fabricating an
  interpretation until the compatible reader is restored.
- [Additional facts consume bounded Journal capacity] → Emit one small enum at each
  existing worker-local validation boundary and one new event only on typed submit
  rejection; preserve the existing material-event retention priority and health truth.
- [Live tests become costly or flaky] → Keep them selected, explicit-profile,
  single-branch, bounded, and separate from normal verification; deterministic tests
  remain the required regression proof.

## Migration Plan

1. Add v3 event/manifest parsing and validation while retaining v1/v2 reader support.
2. Update the two worker-local producers and the shared submit producer, then prove
   their different stages in focused deterministic tests.
3. Align capability resources and request builders, then run the scripted bridge/work
   unit suite to confirm no controller or ledger behavior changed.
4. Update the selected live runner to admit its Bundle and bind explicit profile
   provenance for every existing calibration branch; retain worker response-shape facts
   only for the worker/repair branches that reach that production boundary.
5. After focused profile loops pass, run one fresh all-real demo Bundle per profile and
   inspect that it advances through both affected phases. Do not migrate, rewrite, or
   reconstruct historical Bundles. Rollback is source rollback only; no persisted data
   deletion is required.
