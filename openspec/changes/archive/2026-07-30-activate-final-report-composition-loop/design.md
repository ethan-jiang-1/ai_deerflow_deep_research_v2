## Context

See `proposal.md` for motivation. Current real final delivery deterministically
formats placeholder report bytes, publishes them through the publication bundle, and
optimistically records completion before the final gate determines its route. The
current real final gate is fixture-sequence based rather than the accepted
artifact/evidence verifier. Readiness computes an admitted report plan but currently
returns only a synthesized `ContentRef`; it does not persist the referenced bytes.
The final node therefore has neither a usable immutable plan nor a model branch.

## Goals / Non-Goals

**Goals:**

- Make one real final-delivery invocation produce a bounded layout candidate and
  deterministically rendered report/citation artifacts from admitted readiness and
  accepted-evidence facts.
- Persist/read the immutable readiness plan and implement its deterministic final
  artifact/evidence gate before publication can complete, while proving the twentieth
  direct model branch independently.
- Separate prompt/policy/bridge conformance from optional composition-quality judgment.

**Non-Goals:**

- No retrieval, web tools, citation discovery, readiness re-judgment, model feedback
  loop, model retry, new topology, public API, or provider-default change.
- No raw checkpoint, provider response, prompt, unbounded sandbox path, or rejected
  candidate becomes durable state or a published artifact.

## Decisions

### 1. Readiness persists the admitted plan before final delivery consumes it

The readiness controller will serialize its already admitted `ReadinessReportPlan` to
the canonical `readiness_report_plan` path and create the `ContentRef` from the exact
persisted bytes. A new narrow `FinalDeliveryBundleStoreProtocol`, injected only through
the final node's declared `final_delivery_bundle` capability, will read it back through
contained path and hash verification. The protocol exposes only the bounded plan and
accepted-evidence reads plus final-artifact re-read verification required below; it is
implemented by the existing work-unit store but does not expose work planning, worker,
ledger mutation, or generic store control to final delivery. This is a readiness
persistence correction, not a second readiness judgment or a final-delivery-owned
checkpoint write.

Alternative: reconstruct a plan from the critic summary in final delivery. Rejected
because it creates an independent semantic projection and makes the purported plan
reference non-authoritative.

### 2. Trusted projection precedes one zero-tool composer invocation

The final node will read the admitted readiness report plan and only the accepted
evidence material necessary to support its bounded conclusions through the declared
`final_delivery_bundle` read-only controller. It will construct a size-bounded request
that distinguishes trusted assignment from delimited evidence data. The composer
receives neither store handles nor filesystem/tool access.

Alternative: let the composer read report-plan and evidence artifacts directly.
Rejected because artifact selection and raw paths would widen the authority boundary
and make the composition contract unbounded.

### 3. The composer chooses layout; deterministic rendering preserves plan meaning

A closed typed layout candidate will contain only a complete, duplicate-free ordering
of deterministically derived writable-conclusion and mandatory-uncertainty entry
identities. It contains no Markdown body, conclusion text, limitation text, claim map,
or citation references. The deterministic evaluator will verify that each order is a
permutation of the corresponding admitted plan entries. The deterministic renderer
will then inject the plan's exact conclusion/limitation text and the associated
`backing_claim_ids` values (which the current readiness critic defines as accepted
submission references) into fixed report/citation-map structures. Consequently every
approved entry is present, no unapproved fact can enter a rendered report, and no
candidate can strengthen, paraphrase, omit, or rebind an approved entry. Only fresh
admitted bytes go to the existing publication bundle. The composer cannot write
`report_refs`, terminal fields, a gate result, or a route.

Alternative: admit arbitrary report Markdown with structural plan/reference checks.
Rejected because those checks cannot mechanically prove that generated prose neither
adds nor strengthens factual claims, contrary to FID-003's accepted deterministic
bound.

### 4. A fresh final-attempt gate view prevents stale artifacts or optimistic completion

The final node will return a typed, non-checkpointed final-attempt gate view for every
visit. The graph wrapper will validate that view against the node's proposed update
before evaluating the real final gate, as it already does for other gate preview
surfaces. After `publication_bundle.publish_final` returns its pair, the declared
read-only controller will re-read both returned contained paths at the bounded size,
compare each byte digest to its returned `ContentRef`, and validate the fixed report
and citation-map shape before constructing a published view. A no-publication view
carries the specific deterministic failure class instead. The view therefore carries
only fresh paired content references, their verification facts, accepted-evidence
presence, and the failure classification needed by the gate. A prior visit's
`report_refs` cannot make a later failed or unreadable-plan visit pass. The real final
node will not write `COMPLETED`; the final gate writes terminal completion only after it
verifies this fresh view and accepted evidence. Repair/evidence-blocked outcomes remain
non-terminal, while exhaustion retains the existing blocked terminal result.

Alternative: let the gate read checkpointed `report_refs` or retain the node's
optimistic completed update. Rejected because wrapper gate evaluation otherwise sees
pre-visit state, allowing stale artifacts to satisfy a current visit or a repair route
to retain `COMPLETED`.

### 5. A real final gate owns recovery and outcomes

Bridge, plan-read, candidate, or publisher failure will not create a local retry. A
real final gate will deterministically verify the fresh post-publication view and
accepted evidence, then retain its established repair bound and legal `repair`,
`evidence_blocked`, `pass`, and `exhausted` outcomes. An absent accepted-evidence set
constructs an `evidence_blocked` no-publication view before the immutable publisher is
called; it remains a gate fact rather than a prompt request to invent citations.
Publisher conflicts and post-publication verification failures remain publisher/store
facts and cannot trigger a model-owned retry; their existing repair path remains
bounded and may exhaust rather than overwrite the immutable final artifact.

Alternative: give the composer an additional repair prompt. Rejected because it
introduces a second recovery controller and would require separate product behavior.

### 6. Capability, runtime bridge, catalog, and evidence all name the new branch

The branch uses one package-local forbidden-tool capability and one dedicated runtime
policy/bridge. The prompt catalog renders the same production request text. Capability
and cognitive evidence registries receive a discrete twentieth row with separate
success and highest-risk claims. A deterministic scripted bridge proves actual policy
and parser/publisher handoff; a selected labeled corpus evaluates only whether an
assessable candidate preserves approved conclusion/uncertainty/citation constraints.

Alternative: reuse readiness's bridge/evaluation corpus. Rejected because distinct
composition input, candidate, publisher handoff, and judgment criteria would be hidden
by another branch's proof.

## Risks / Trade-offs

- [Bounded projection omits useful prose context] -> candidate is conservatively
  rejected or assessed as limited; it cannot fetch or invent additional evidence.
- [Model attempts polished but unsupported prose] -> its closed layout schema admits
  no prose field; deterministic rendering emits only exact approved plan text.
- [Provider failure delays completion] -> use the existing final gate bound, not an
  unbounded model retry.
- [Read authority is missing or misdeclared] -> fail before request construction and
  prove direct-factory and graph-wrapper behavior.
- [Plan reference is absent, unreadable, or hash-divergent] -> invoke no composer,
  publish no final artifact, emit a fresh no-publication view, and let the deterministic
  final gate own the bounded outcome.
- [Fixture gate could claim pass without artifacts or stale refs] -> replace it with
  a fresh-attempt deterministic report/citation-map and accepted-evidence gate before
  accepting completion.
- [Credentialed quality evaluation is unavailable] -> retain deterministic conformance
  and record no quality disposition rather than treating fixtures as model judgment.

## Migration Plan

1. Add immutable readiness-plan persistence/read verification and a real final gate,
   with focused failure tests, while retaining full-fake behavior and topology.
2. Add final-delivery typed projection/layout-candidate/evaluator/renderer seams,
   declared reader capability, local capability resource, dedicated bridge policy, and
   source-faithful catalog case.
3. Replace only real formatter composition with admitted layout rendering, immutable
   publication, and post-publication fresh-view verification; preserve publisher
   idempotence/conflict semantics and the deterministic gate owners.
4. Add deterministic conformance/failure and selected evaluation assets, then run the
   offline verifier and strict OpenSpec checks. Rollback restores the deterministic
   formatter without a state or topology migration.
