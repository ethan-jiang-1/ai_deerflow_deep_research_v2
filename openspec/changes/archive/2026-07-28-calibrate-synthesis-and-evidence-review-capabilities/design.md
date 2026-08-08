## Context

The node-agent capability contract already supports a validated package-local policy,
the required/legacy binding distinction, and deterministic catalog projection. Wave2
already binds distinct zero-tool synthesis and repair capabilities. Four
targeted-evidence branches remain explicit legacy requests: the gap worker, its
structured repair, SourceDiagnostic, and ClaimVerifier. Their existing graph and
work-unit code owns gap identity, work allocation, result validation, ledger
submission, and targeted-worker recovery. Critic parsing and materialization are
separate: malformed or out-of-scope critic output currently propagates from dispatch
before an artifact is written.

The preceding planning/intake calibration change has established branch-level evidence
through Wave1. This change closes the downstream evidence-evaluation loop without
reopening that completed cohort or treating a model response as an authority.

## Goals / Non-Goals

**Goals:**

- Migrate only the four targeted-evidence legacy branches to local capabilities with
  explicit required-retrieval or forbidden-tool postures; retain Wave2's existing
  required zero-tool bindings.
- Establish deterministic behavior evidence that synthesis uses assigned accepted
  evidence, targeted retrieval follows one gate-authorized gap, critics remain
  read-only within assigned references, and every repair remains non-inventive.
- Extend the prompt catalog and direct-branch evidence matrix from twelve to sixteen
  rows while keeping workflow bridge proof distinct from per-branch admission proof.

**Non-Goals:**

- No graph topology, public API, checkpoint schema, controller, retry, gate, ledger,
  provider-policy, backend, or frontend change.
- No live source-truth, critic-quality, report-quality, or general research-quality
  claim.
- No change to the already archived planner, Wave0, or Wave1 cohort.

## Decisions

### Treat the evidence-evaluation loop as the final closed cohort

Wave2 consumes accepted evidence and produces the gate-owned searchable-gap
projection. Targeted evidence consumes that projection, submits candidate evidence,
and dispatches read-only critics. The six branches form one production loop, but only
the four targeted branches require capability migration. Grouping their behavioral
proof lets a failing gap identity, forbidden tool call, or out-of-scope critic ref be
attributed to its producing branch.

Alternative: migrate every remaining branch together with a new report-writer or
readiness agent. Rejected because those deterministic/deferred surfaces do not belong
to the accepted-evidence loop and would hide the responsible admission seam.

### Retain existing deterministic admission and recovery owners

Capability metadata and Markdown describe bounded cognition only. Wave2's parser and
materializer retain finding/gap admission. The targeted work-unit validator, controller,
and ledger retain worker-result admission. Critic parsers and materializers retain
scoped critic admission; rejected critic output continues to propagate before
materialization. The existing gate owns the bounded searchable-gap projection and
routes; the existing worker and repair policies retain their failure bounds. This change
adds no critic retry, terminal, or route layer.

Alternative: allow a capability to declare its parser, route, or retry policy.
Rejected because a static prompt resource would then create a competing control
authority.

### Make each targeted branch locally explicit

The targeted worker gets one required-retrieval capability whose declared allowed
names exactly mirror its existing Wave0 worker bridge policy:
`duckduckgo_search`, `firecrawl_scrape`, `jina_ai`, `tavily_extract`,
`tavily_search`, `web_fetch`, and `web_search`. Its repair, SourceDiagnostic, and
ClaimVerifier each get a distinct forbidden-tool capability. Wave2 retains its two
existing forbidden capabilities. The catalog renders all six cases and shows requested
posture separately from the runtime policy.

Alternative: use one generic targeted capability with modes. Rejected because a
retrieval worker, structural repair, source diagnostic, and claim verification have
different authority limits and highest-risk behavior.

### Evidence follows direct branches and responsible seams

The capability matrix gains the four targeted rows, from twelve to sixteen, with
separate normal and highest-risk `REAL_NODE_FAKE_CAPABILITIES` claims. Wave2 keeps its
existing two rows. Separate `SCRIPTED_REAL_WORKFLOW` claims exercise the real bridge,
one-call worker path, and critic request/materializer path where they prove call
bounds, untrusted-data handling, and deterministic admission only. No aggregate count,
catalog projection, or scripted transcript proves model quality or source truth.

Alternative: one full mixed-graph test for the whole loop. Rejected because it cannot
identify whether an unwanted tool, unauthorized reference, or fabricated repair field
came from Wave2, the worker, or a critic.

## Risks / Trade-offs

- [Scripted transcripts can overstate research quality] -> Evidence claims declare
  deterministic authenticity and restrict assertions to posture, call bounds, scope,
  and admission.
- [Targeted worker policy could widen live tooling] -> Its exact seven-name required
  capability list is checked against the existing Wave0 worker bridge policy before
  model construction or dispatch.
- [Critic prompts could turn assigned references into authority] -> Existing typed
  parsers/materializers reject out-of-scope refs before artifact writes; capabilities
  retain no write, route, ledger, or gate fields.
- [Critic failure can be mistaken for a new recovery path] -> The change preserves
  existing exception propagation and proves no artifact write; it introduces no retry,
  terminal, or route semantics.
- [A repair can appear valid while inventing evidence] -> Focused risk cases assert
  no new source, claim, ref, gap, or finding can be admitted from a bounded draft.

## Migration Plan

1. Add targeted-evidence local declarations and Markdown policies; bind the four
   production builders as required and add their catalog cases.
2. Add direct branch acceptance cases and test-owned evidence metadata, then make
   only the smallest request, validation, or policy correction exposed by those cases.
3. Regenerate prompt catalog artifacts; run focused tests, test-asset governance, the
   offline deterministic gate, strict OpenSpec validation, and boundary checks.

Rollback is a normal code revert. The change introduces no persisted-state migration
or external interface.

## Open Questions

None. Any need to alter graph routes, recovery bounds, public interfaces, or runtime
tool policy ownership requires a revised proposal and design review.
