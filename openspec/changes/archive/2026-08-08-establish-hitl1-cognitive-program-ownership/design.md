## Context

See [proposal.md](proposal.md) for motivation and the bounded contract in
[`hitl1-node`](specs/hitl1-node/spec.md). HITL1 already invokes four distinct
zero-tool capability resources through the production phase renderer. Their current
bodies establish role and authority limits, while `prompts.py` still carries most of
the reusable brief/semantic method, branching language, and repair instructions.

The durable flow already has an appropriate shape and remains unchanged:

```text
bounded assignment data + exact capability resource
                 |
                 v
      renderer and zero-tool runtime bridge
                 |
                 v
          closed typed candidate result
                 |
                 v
 parser / Research Confirmation / HITL1 materializer
                 |
                 v
correlated Bundle-local profile write and declared graph route
```

`profile_ref` is already the canonical profile consumer path to topic planning. It is
an invariant this change protects, not a producer/consumer chain it modifies.

## Goals / Non-Goals

**Goals:**

- Make the four HITL1 capability resources the canonical, runtime-visible cognitive
  method owner for brief and semantic reply work.
- Reduce the prompt-builder interface to bounded task data, output contract, and
  resource selection so callers need not understand or replicate the cognitive method.
- Preserve one deterministic admission path from a closed candidate to a correlated,
  Bundle-local profile effect.
- Establish precise evidence tiers for resource loading, deterministic handoff, and
  credentialed cognitive quality.

**Non-Goals:**

- Changing `ResearchProfile`, `SemanticCandidate`, current human controls,
  correlation, State/reducer ownership, graph topology, or profile projection.
- Changing the capability metadata schema, capability ids, runtime tool posture,
  provider configuration, retry/call ceilings, or runtime bridge ownership.
- Combining brief and semantic intake into one model call or one resource; their
  assignments, output types, recovery behavior, and interaction effects differ.
- Migrating another cognitive program or changing any `backend/`/`frontend/` path.

## Decisions

### Keep four stable resources; make their bodies the complete method

The change reuses the existing brief, brief-repair, semantic-intake, and semantic-
intake-repair capability identities. Each body will state the actual task sequence,
decision branches, input-as-data rule, uncertainty disposition, self-check, repair
posture, completion condition, and authority limit. Capability metadata remains the
existing admission/tool-posture envelope, not a second method representation.

The new `hitl1-cognitive-program-v1` corpus is registered beside, rather than in
place of, the existing `hitl1-brief-v1` compatibility smoke. Its execution plan names
the exact four capability bodies and the `StructuredBrief` and `SemanticCandidate`
schema sources by project-relative path and SHA-256 digest. Its closed scenario set is
`normal-confirmation`, `complete-revision`, `proposal-question`, `ambiguity`,
`adversarial-input`, and `malformed-candidate-repair`. Each scenario declares the
expected capability ids, bounded assignment fragments, forbidden control effects, and
named rubric criteria. A dedicated closed `hitl1_cognitive_program` subject and
fixture adapter runs those scenarios only through the registered HITL1 node factory;
it is explicitly admitted to the selected-live allowlist beside the existing brief
smoke and may seed declared untrusted reply or invalid-draft data but may not replace parsing,
materialization, correlation, State writing, or routing.

This creates a reviewable method identity without widening capability metadata or
creating a registry that can override a runtime resource. The existing
`hitl1-brief-v1` case remains a narrow compatibility smoke instead of acquiring
semantic-intake semantics under a misleading historical name.

Alternative considered: combine initial and repair instructions in one capability with
a runtime mode flag. Rejected because it weakens the existing exact repair binding and
makes an invalid draft easier to treat as normal task input.

### Make prompt builders a narrow assignment seam

`build_brief_prompt()` and `build_semantic_intake_prompt()` continue to validate
presence/bounds and build `NodeExecutionRequest`. Their `objective` carries only the
current bounded assignment and generic data delimiting; `expected_output` remains the
typed schema/size contract. Reusable task procedures, semantic classification policy,
and repair instructions move to the selected capability body.

This is a deep module boundary: callers supply a small assignment interface and obtain
a closed candidate contract, while the cognitive procedure stays local to the runtime-
loaded resource. The source-level rule is not that Python may contain no prose; it is
that Python may not retain an independently sufficient HITL1 cognitive method.

Alternative considered: leave the method in Python and add explanatory Markdown.
Rejected because a static supplement cannot prove that changing Markdown changes the
production cognitive procedure, and it recreates two owners that must be synchronized.

### Preserve deterministic admission and recovery exactly

The node handler remains the only owner of semantic-call sequencing, bounded repair,
provider retry/fallback, cancellation propagation, correlation, checkpoint update,
profile publication, and graph route. `StructuredBrief` and `SemanticCandidate` are
advisory typed candidates; the parser and existing Research Confirmation/materializer
remain non-bypassable before any State or artifact change.

The resource bodies explicitly state this limit, but that text does not enforce it.
`RuntimeNodeAgentBridge` continues to enforce zero tools and the node handler continues
to enforce call/recovery bounds. A missing/malformed/mismatched resource must fail on
the current safe path rather than falling back to workflow documentation or an embedded
method copy.

Alternative considered: let a Markdown-defined candidate include an action, request
id, route, or profile payload that the node executes. Rejected because it would create
a competing controller and break the existing human-interaction correlation seam.

### Treat evaluation as three distinct evidence layers

1. Resource/renderer tests prove the exact selected body is in the final production
   system policy, is source-identifiable by digest, and preserves zero-tool posture.
2. Scripted node and integration transcripts prove the deterministic candidate-to-
   parser/materializer handoff and legal outcomes for normal, ambiguity, adversarial,
   malformed/repair, provider-failure, and cancellation cases. Scripted candidates do
   not establish language quality.
3. The immutable evaluation manifest and review record carry one closed evidence layer:
   `deterministic_handoff` or `credentialed_live_quality`. The ordinary runner has no
   caller-selectable live mode and emits only `deterministic_handoff`. The selected-live
   entrypoint performs credential preflight before calling its internal live execution
   path, which alone emits `credentialed_live_quality`. Reviews derive the layer from
   their verified manifest, not evaluator prose. There is no release-pass field or
   release authority in this corpus, its manifest, or review record. Without configured
   credentials, strict preflight creates no live manifest or review and no fabricated
   `ReviewResult`. The change closeout, outside the evaluation runner/reviewer record,
   marks live-quality evidence availability as `limited` with the preflight reason,
   never as a live or release pass.

The corpus stores no lifecycle authority. It references current method/schema digests
and records evidence; Bundle-local State remains the only lifecycle authority.

## Risks / Trade-offs

- [Markdown becomes long but still shallow] -> Keep each resource focused on one
  bounded task and retain the existing body-size admission limit; review method
  completeness rather than target a line count.
- [Python silently reacquires a parallel method] -> Add focused source/renderer tests
  that distinguish task data/schema from capability method markers.
- [A resource edit changes model behavior unexpectedly] -> Add normal, ambiguity,
  adversarial, and repair cases before broadening live evaluation; deterministic
  admission and recovery gates continue to fail closed.
- [Evaluation is mistaken for runtime authority] -> Keep corpus/digest/review data out
  of State, route selection, resource loading, and lifecycle projections.
- [Legacy checkpoint compatibility regresses] -> No State/schema migration is allowed;
  retain current reload and profile-publication transcripts.

## Migration Plan

1. Add focused red tests for renderer method ownership, candidate handoff, the closed
   HITL1 cognitive-program corpus, and manifest-derived evidence layers before moving
   any reusable method prose.
2. Move method/branch/repair text into the four existing resources and reduce builders
   to assignment/schema construction without changing their selected capability refs.
3. Run focused deterministic HITL1/resource/evaluation tests, then the existing
   required Deep Research verification gates. No Bundle data migration, deployment
   switch, or upstream configuration change is required. Do not run a paid/live
   evaluation as part of this change; missing credentials leave the change-closeout
   live-evidence availability explicitly `limited`, not a fabricated evaluation result.
4. If the cognitive method or evidence admits an implementation-owned defect, restore
   the prior resource/body and builder behavior in the same change, leave the defect as
   an unchecked task, and do not claim the cognitive corpus passed. Existing profile
   artifacts and Bundle State remain readable throughout.

## Open Questions

None. Live-provider availability affects only the supplemental evidence disposition;
it does not change this task breakdown or deterministic contract.
