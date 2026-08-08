## Context

See [proposal.md](proposal.md) for motivation. Wave2 already binds dedicated
forbidden-tool resources and the runtime provides a dedicated zero-tool bridge, but
the current resource bodies are short policy summaries while `prompts.py` owns most
of the executable cognitive method. The real node already performs one initial
candidate invocation, parser/local semantic validation, and at most one repair before
the existing materializer, preview builder, and gate handle persistence and routing.

The existing evidence-judgment calibration collection shares Wave2 rows with targeted
evidence and readiness. It is insufficient as the ownership-change corpus because it
composes one request and cannot prove fresh real-node handoff or a closed Wave2-only
denominator.

The current typed `EvaluationCase` contract and its control loader admit only the
existing HITL1, Wave0, and Wave1 cognitive-program fixture families. Wave2 therefore
needs one parallel closed fixture/loader branch before its registry can represent the
five-case denominator; a generic evaluation abstraction or selected-live behavior
change is neither required nor in scope.

## Goals / Non-Goals

**Goals:**

- Make each existing Wave2 capability resource the sole model-visible home of its
  reusable cognitive method.
- Keep Python as a bounded projection of trusted assignment, output contract,
  validation category, and delimited untrusted data.
- Prove exact runtime injection, zero-tool enforcement, accepted-evidence-only
  admission, one-repair containment, and invalid-repair non-publication.
- Add a closed deterministic Wave2 corpus that reports handoff facts without claiming
  live model quality.

**Non-Goals:**

- Changing `SynthesisResult`, accepted-evidence discovery, relation/gap semantics,
  materialization, gate preview, gate budget/route, or the targeted-evidence loop.
- Migrating targeted-evidence, readiness, HITL2, or final-delivery cognition.
- Adding tools, a provider retry policy, persistent control state, a public API, or
  a credentialed-live claim.

## Decisions

### 1. Move reusable method text into the two activated capability bodies

The initial resource will describe how to read only assigned accepted evidence, form
supported findings and relations, represent uncertainty as honest gaps, reject
instruction-like data, self-check references, and complete with one candidate. The
repair resource will describe the same-assignment, closed-category, no-invention
repair method and its own self-check. Both retain forbidden tool posture and no
lifecycle authority.

`build_synthesis_prompt` and `build_synthesis_repair_prompt` will retain only the
dynamic facts the model needs for this invocation. Keeping a duplicate detailed method
in Python was rejected because it permits the runtime policy resource and the actual
procedure to drift. Moving parser, evidence aliases, materialization, or route
instructions into Markdown was rejected because those remain deterministic owners.

### 2. Retain the existing one-repair and outcome boundary

The Wave2 node will continue to translate only closed parser/semantic categories into
one repair request. The repair receives the same evidence, bounded draft, and compact
category, then re-enters the existing parser/semantic validation. It cannot receive
raw exceptions, a second retry allowance, artifact authority, preview authority, or
route authority.

Provider/configuration/cancellation outcomes continue through the existing invocation
normalizer and typed incident path. Valid candidates continue to materialize before a
typed preview reaches the existing gate. This reuses the current control path instead
of adding a capability-managed controller.

### 3. Use two complementary deterministic evidence layers

Direct renderer/prompt tests will prove that the loaded full body, not a marker or
parallel objective, reaches the real context. Scripted real-node/bridge tests will
prove the accepted-evidence, zero-tool, one-repair, and non-publication handoffs.

A new closed `wave2_cognitive_program` corpus will exercise only fresh production
Wave2 dependencies with scripted adapters. It is intentionally separate from the
mixed evidence-judgment collection so its denominator cannot accidentally inherit
targeted-evidence or readiness semantics. Existing selected-live mechanics will
reject it before any credentialed side effect. A real-model quality claim remains
separate and requires explicit later authorization.

`domain/evaluation.py` will receive a parallel Wave2 scenario/fixture type and
`EvaluationCase` subject branch whose validation closes exactly the five required
case kinds and the two capability plus `SynthesisResult` schema controls.
`runtime/evaluation/controls.py` will extend its existing contained rubric binding to
that typed fixture. The shared runner, evidence-layer model, and selected-live
allowlist stay unchanged: Wave2 exclusion follows the existing unregistered-case
admission path rather than a new special-case control layer.

Because the existing semantic validator requires at least one backed finding whenever
accepted evidence is non-empty, the honest-gap scenario will pair an accepted-evidence
finding with a bounded uncertainty gap. A gaps-only candidate remains a distinct
invalid initial or repaired candidate for the existing one-repair/non-publication
boundary; it is not reused to stand in for uncertainty judgment.

The production Wave2 node necessarily invokes its existing materializer and preview
builder after a valid candidate. The corpus adapter will therefore use a fresh,
contained scripted Bundle dependency for each scenario and record only the declared
resource, bounded prompt, accepted-evidence, one-repair, deterministic-admission, or
invalid-candidate non-publication observations. It may assert that an invalid repaired
candidate causes no write, but it does not elevate a valid candidate's internal write,
preview, or later gate disposition into a corpus proof claim.

### 4. Limit spec deltas to the changed capability and evidence behavior

`wave2-synthesis-node` receives the runtime-method ownership and bounded-repair
contract. `evaluation-hardening` receives only the Wave2 closed corpus contract.
`node-agent-capabilities`, graph lifecycle, targeted evidence, and readiness specs
remain unchanged because their current declarations and owners are preserved.

## Risks / Trade-offs

- [Capability body duplicates a dynamic assignment or schema] -> Keep trusted
  invocation data in Python and method prose in Markdown; renderer tests prove the
  four-layer boundary.
- [Candidate prose gains control authority] -> Retain parser, materializer, preview,
  and gate handoff tests with forged-reference and gap-projection negatives.
- [Repair grows into retry policy] -> Assert exactly one existing zero-tool repair and
  no repair after deterministic post-candidate paths.
- [A shared corpus silently expands scope] -> Use a Wave2-only case family with a
  closed denominator and selected-live rejection test.
- [A sibling corpus motivates generic evaluation changes] -> Add only the parallel
  typed Wave2 fixture and its existing loader/rubric branch; reject a runner,
  evidence-layer, or selected-live policy abstraction as outside this change.
- [Deterministic tests are misreported as quality evidence] -> Record only
  deterministic-handoff evidence; leave live quality explicitly unclaimed.

## Migration Plan

1. Add `WSN-008` and `EVH-029` to the requirement registry and implement the two
   owning delta requirements.
2. Establish focused red renderer, prompt, real-node, and corpus tests before moving
   method prose into the two capability resources and reducing dynamic objectives.
3. Add the parallel typed fixture/control-loader branch, then the closed Wave2 corpus
   and its test-owned evidence claims, and run focused deterministic verification and
   the complete offline gate.
4. Sync the two deltas only after all deterministic evidence is green; archiving
   changes no persisted Bundle data, public API, or deployment configuration.

Rollback restores the previous capability bodies and prompt observations. Existing
artifacts, selected Bundles, gate state, and routes are unaffected.
