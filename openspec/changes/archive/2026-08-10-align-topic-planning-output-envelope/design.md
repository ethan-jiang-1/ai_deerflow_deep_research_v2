## Context

See `proposal.md` for the observed BUG-024 evidence. The current planner advertises
the broad TopicPlan schema to the model, enforces a 2048 output-token cap only after a
provider response arrives, and silently byte-truncates the structured summary at
4096 bytes before parsing. Three independent profiled Bundles reached the first guard
across two models. These controls are local to the planner, but their sizes do not
describe one coherent candidate envelope.

The topic-planning node remains a bounded Node Agent. Capability Markdown and the
prompt projection direct its cognitive work; the runtime bridge controls model,
tools, budgets, cancellation, and safe failures; `parse_plan_output` and
`materialize_topic_plan` alone decide whether a candidate can become planner-owned
checkpoint state.

## Goals / Non-Goals

**Goals:**

- Give the planner and repairer one explicit compact JSON target that covers the
  confirmed assignment without repeating it.
- Make the local output-token and structured-result guards large enough to carry that
  bounded target, with a 12288 total-token admission budget and the existing 60-second
  limit.
- Lock the cognitive contract and policy values at focused deterministic seams before
  using bounded real Bundles as supplemental evidence.

**Non-Goals:**

- Do not change the broad authoritative TopicPlan schema, deterministic
  parser/materializer, IDs, coverage, state writer, graph edges, or lifecycle outcome.
- Do not tune Wave0/Wave1, select a default model, alter provider credentials, or
  introduce a retry/fallback/diagnostic controller.

## Decisions

### 1. Use a model-visible compact envelope while retaining parser authority

The initial and repair capability programs will require compact field values and only
necessary dimensions/exclusions. `prompts.py` will project those same target bounds in
the expected-output payload. The parser stays broader because it owns lawful candidate
admission after a candidate reaches it; a prompt target must not become a second
controller or change parser or materializer semantics for a candidate that the runtime
has retained.

The alternative was to shrink `TopicPlan` field maxima globally. That would conflate a
real-demo output-shaping change with a product-wide parser compatibility change and
would reject candidates that the existing materializer can lawfully handle.

### 2. Calibrate the one local policy as a matched envelope

`_topic_planning_node_agent_policy()` will use a 4096 output-token cap, a 16384-byte
structured-result cap, and a 12288 total-token budget. The observed fixed scripted-demo
request renders to 4230 bytes, so its reserved 4096-token output ceiling projects to
8326 and is admitted within the selected local total. The total increase is local to
topic planning; it retains one model call, zero tools, and the existing 60-second
limit. The structured-result cap uses the existing bounded topic-registry capacity as
a local retained-candidate ceiling and avoids corrupting a compact JSON candidate by
truncating it at 4096 bytes. Candidate JSON and a materialized state registry are not
identical payloads, so the existing state validator continues to decide publication
after materialization.

The alternative was to preserve the 8192 total budget while lowering the output cap to
at most the 3961 conservative accounting units available to the observed prompt. That
would reintroduce an unverified output ceiling: the evidence establishes only that the
real response exceeded 2048. Raising only the output cap while retaining 8192 would
make the observed request fail pre-provider at `token_admission`; lifting a shared
middleware limit would broaden unrelated nodes and still not address JSON truncation.

### 3. Keep all recovery and lifecycle owners unchanged

`BudgetMiddleware` continues to emit the closed budget reason. The bridge continues
normalization. Topic planning continues to own its existing distinction between a
non-provider stop and one structured-output repair, and the graph continues to own
the exhausted route and `BLOCKED` terminal state. The Journal only observes those
facts; it neither selects a new limit nor authorizes recovery.

## Risks / Trade-offs

- [A model still produces an oversized response] -> The existing closed budget result
  and terminal path remain intact; bounded real calibration determines whether the
  compact cognitive contract improves the actual path.
- [A compact target omits useful distinctions] -> The deterministic parser remains
  broader and coverage validation stays unchanged; focused tests require all
  must-answer bindings and non-overlap behavior.
- [A retained candidate near 16384 bytes materializes above the state cap] -> Existing
  state validation remains the publication control. A focused regression uses a compact
  valid candidate above the old truncation point whose materialized registry fits that
  existing state bound; the equal numeric limits are not treated as an identity proof.
- [Wave1 remains blocked after planning passes] -> It stays outside this change and is
  re-investigated with the explicit-profile Journal only after the planner blocker is
  removed.

## Admission Calibration

The source-faithful initial request for the observed fixed scripted-demo profile
renders to 4230 UTF-8 bytes: 2611 bytes of trusted system policy/capability text and
1619 bytes of user message. `BudgetMiddleware` refuses a request before provider
invocation when its rendered byte upper bound plus `per_call_output_token_cap` exceeds
`total_token_budget`. The selected 4096/12288 pair projects to 8326 and is therefore
admitted, leaving 3962 conservative accounting units for the compact-envelope prompt
updates. The deterministic evidence must render the final changed prompt rather than
rely on these pre-change measurements.

This does not promise that every maximally sized confirmed profile is admitted. An
oversized rendered request retains the existing closed `token_admission` outcome with
no provider call, topic state, retry, route, or lifecycle change.

## Migration Plan

1. Add focused red tests for the initial/repair compact envelope, the exact
   topic-planning policy pair, and the source-faithful fixed-demo request's admission;
   prove existing parser, repair, state, route, and failure behavior remains unchanged.
2. Update the two capability programs, prompt projection, and local execution policy;
   run the narrow deterministic test set and the normal offline verification gate.
3. After the final prompt's deterministic admission proof is green, run one explicit
   `deepseek-v4-pro` and one explicit `deepseek-v4-flash` scripted Bundle as bounded
   supplemental evidence. Inspect only the Bundle-local Journal and record whether
   each advances past topic planning.
4. If deterministic evidence regresses, restore the previous local policy and
   capability content together. No data migration, checkpoint migration, or external
   rollout is required.
