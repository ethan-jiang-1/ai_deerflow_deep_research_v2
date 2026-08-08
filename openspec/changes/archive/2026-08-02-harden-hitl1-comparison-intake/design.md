## Context

See [proposal.md](proposal.md) for motivation and scope. Current profile completeness
covers only five enum dimensions and `must_answer`; profile content is schema version
1, and the checkpoint short fields omit comparison and language facts. Complete
advisory proposals send every raw text response to the semantic worker. In addition,
the lifecycle reserves `CHOICE` options for HITL2, while local and retained run
experiences assume HITL1 is text-only.

This change adds profile facts and a bounded option wire without adding another
controller: `domain/profile.py` validates/canonicalizes the facts, HITL1 admits them
and writes/routes state, lifecycle/runtime transports only a current correlated
response, and topic planning consumes accepted checkpoint facts.

## Goals / Non-Goals

**Goals:**

- Type, validate, canonicalize, and persist comparison scope and request/output
  language before profile materialization.
- Detect supported Chinese/English comparison/language signals and clear
  confirmations locally, with deterministic recovery for missing values.
- Preserve existing bounded zero-tool semantic intake only for non-local revisions,
  questions, and ambiguity.
- Keep legacy retained records readable without inventing modern accepted facts.

**Non-Goals:**

- General language identification, translation, arbitrary entity extraction, or a
  universal natural-language comparison parser.
- Changes to semantic worker retries, provider behavior, graph topology, or upstream
  DeerFlow/backend/frontend APIs.
- Granting projections, prompt text, controls, or semantic candidates authority to
  write profiles or choose routes.

## Decisions

### Profile v2 is the only fact owner

Introduce profile schema version 2 and extend `StructuredBrief`,
`PartialResearchProfile`, and `ResearchProfile` with these facts:

| Fact | Representation and invariant | Writer and direct consumer |
| --- | --- | --- |
| `comparison_required` | Immutable bool from the original request's bounded comparison signal. | HITL1 seed builder; profile completeness. |
| `comparison_subjects` | Frozen `ComparisonSubjects(subjects: tuple[str, str])`; NFKC-normalized, trimmed, whitespace-collapsed, 1-256 chars each, distinct after normalized case-folding; user order is retained. | Typed parser/semantic revision candidate; profile, HITL1, planner. |
| `request_language` | Immutable `zh`, `en`, `unspecified`, or `legacy_unspecified`. | Local detector or legacy reader; profile consumers. |
| `output_language` | Mutable accepted `zh` or `en`, absent only while an unsupported request awaits choice. | HITL1 input admission; presentation and planner. |

`missing_dimensions()` gains `comparison_subjects` only when
`comparison_required=true` and `output_language` for every non-degraded v2 profile.
`ProfileParseResult`, merge/finalize, proposal payloads, `profile_state_fields()`,
state validators/ownership, canonical JSON/hash, and planner inputs use the same
facts. No prompt catalog or interaction projection is a second source of truth.

Canonical JSON includes the v2 schema and ordered subjects. Formatting-equivalent
subjects retain one canonical hash; a reordered explicit pair changes it. Blank,
duplicate, third, or unrecognized-language values fail before checkpointing.

**Rejected alternatives:** `must_answer` or scope prose cannot prove cardinality or
downstream meaning. A prompt-only language instruction leaves the brief model able to
choose a default.

### A local intake seed prevents model-selected comparison pairs

Before invoking the brief agent, HITL1 derives immutable `ComparisonIntakeSeed` from
the NFKC-normalized original request. It sets `comparison_required=true` only for:

- Chinese markers `比较` or `对比`.
- English word-boundary markers `compare`, `comparison`, `versus`, or `vs`.

The seed extracts an initial pair only from the bounded source grammars:
`比较|对比 <subject> 和|与|vs <subject>` and
`compare|comparison <subject> and|with|vs|versus <subject>`. Both values must pass
`ComparisonSubjects`. A marker without a valid pair, including
`比较两种储能路线的成本、风险与适用场景`, yields a comparison-required incomplete profile.

The profile-input parser accepts the same pair through structured
`comparison_subjects: [first, second]` and, while requesting pair completion only, a
narrow `first | second` plain-text grammar. It never guesses arbitrary prose. HITL1
overwrites any brief-model pair with the local seed, so model generation cannot satisfy
an absent pair. A later semantic revision may propose a complete pair only as a new
advisory profile version that needs ordinary later confirmation.

This lets `Compare lithium-ion batteries and vanadium redox flow batteries` begin
with its explicit source pair, while generic comparisons ask for two subjects. Inputs
outside the marker set retain existing non-comparison behavior; this is an explicit
bounded fallback, not a universal classifier.

**Rejected alternatives:** A brief model default is the bug. A model-based detector
would move a deterministic admission decision outside the profile contract.

### Local language evidence is separate from accepted preference

The normalized original request produces `zh` if it has any Han character; otherwise
it produces `en` if it has any ASCII alphabetic character; otherwise it is
`unspecified`. Chinese takes precedence so Chinese text mentioning English product
names does not silently become English. Other scripts and punctuation/digit-only input
are intentionally unsupported rather than guessed.

For `zh` or `en`, HITL1 seeds `output_language` to that value before brief validation.
The brief receives the fixed presentation-language constraint but cannot author the
fact. Deterministic HITL1 subject, feedback, and follow-up templates use the accepted
language. The bounded brief summary must pass the same supported-language check;
opposite-language summary text is a structured-output validation error using the
existing one-repair limit, never translated after the fact.

For `unspecified`, HITL1 sends a `CHOICE` request containing exactly the fixed,
bilingual `zh` and `en` options, no interaction projection, and no action id. The
current selected option changes only `output_language`; `request_language` remains
`unspecified`. A structured profile revision may explicitly change output language,
but no brief or semantic candidate selects it by default.

**Rejected alternatives:** Latin-character counting misclassifies Chinese product
requests. Free-text aliases recreate the ambiguous path that the option is meant to
eliminate.

### Non-interactive auto-profile cannot bypass typed admission

The existing authorized `non_interactive_policy.auto_profile` remains available for
ordinary scripted runs, but it is not an authority to invent a required comparison
pair or accepted output language. Before it writes a degraded profile, HITL1 applies
the same local intake seed and profile validation as the interactive path. It may
continue only when any required pair is explicit and valid in the original request and
the output language is deterministically supported; it writes those typed facts along
with the existing degraded defaults for the remaining legacy dimensions.

When a supported comparison has no explicit valid pair, or output language requires a
human choice, non-interactive HITL1 cannot issue a recovery interrupt. It SHALL instead
take the existing terminal `GATE_BLOCKED` path with no profile artifact or final profile
fields. `auto_proceed` and all non-comparison supported-language auto-profile behavior
remain unchanged.

**Rejected alternative:** Defaulting a pair or language only for scripted execution
would make the same accepted profile mean something the source request did not state.

### Exact confirmation is deterministic and comes first

`normalize_clear_confirmation()` applies NFKC, Unicode whitespace collapse,
case-folding, outer trim, and removal only of terminal `.`, `!`, `?`, `。`, `！`, or
`？`. It accepts exactly:

- Chinese: `可以`, `好的`, `同意`, `确认`, `可以，我觉得你说的挺好`.
- English: `yes`, `yes please`, `looks good`, `i agree`, `confirm`, `confirmed`.

After request-id validation and only for a complete current proposal, HITL1 checks
this set before `_classify_proposal_reply()`. A match creates the same internal
`accept_suggestion` decision as the visible control, retains proposal-version
correlation, writes once, and makes zero bridge/model calls. Extra words,
modifications, questions, mixed language, and all other replies keep the current
semantic-intake route.

**Rejected alternatives:** A contains-match accepts `yes, but change the format`.
Sending an unambiguous action to the model makes a deterministic result provider-
dependent.

### Language choice is a typed option, not a control/action

Add the closed `SupportedLanguage` option family to `HumanInputOption` while retaining
the existing HITL2 decision family. A HITL1 `CHOICE` is valid only when it advertises
the exact two language options and has neither `interaction` nor `action_ids`.
`OPTION` responses require the current request id and option id; existing HITL2 options
and normal HITL1 text remain compatible.

Extend `PendingInputProjection`, `PendingSessionInput`, `AnswerRun`, local runtime,
and retained-session broker to submit an advertised option id. Each validates against
the current pending request; the retained broker repeats that validation under its
namespace lock. It sends the normal correlated `OPTION` response and never maps labels
or free text to options. The existing visible-control map remains only for
`accept_current_proposal`.

#### Control Placement Review (voluntary review record)

| Surface | Visible value | Trusted binding/executor | Effect owner | Rationale |
| --- | --- | --- | --- | --- |
| Current proposal acceptance | Complete proposal including pair/language. | Existing control-to-advertised-action binding. | HITL1 validates and materializes. | Preserves existing graph-authorized acceptance. |
| `zh`/`en` language selection | Exact two options only for unsupported request evidence. | Lifecycle/runtime validates a current option response. | HITL1 records preference and resumes intake. | Input value, never route action or control alias. |
| Natural reply | Raw text for complete proposal. | Exact local matcher or bounded semantic bridge. | HITL1 admission/resolution. | Adapters and prompts never infer actions. |

This is a voluntary review record only; it creates no runtime authority beyond the
affected capability deltas.

### Checkpoints and retained content remain compatible without invention

`ResearchState` retains its current schema version. New controller-owned bounded short
fields for ordered subjects, request language, and output language default safely when
absent, use the domain validators, and are read directly by topic planning. Existing
checkpoints therefore decode without a state-version bump.

Profile content has its own v2 boundary. A legacy v1 reader returns an explicit legacy
view (`legacy_unspecified`, no comparison requirement) and retains the recorded v1
bytes/hash for verification. It never reserializes a v1 accepted profile as v2. A
resumed v1 HITL1 proposal becomes an incomplete v2 intake that asks only for newly
required facts; a completed v1 profile already downstream remains readable without
synthetic fields. New profile writes are v2.

**Rejected alternatives:** Defaulting historic data to English/no-comparison silently
rewrites meaning. Rejecting all v1 records violates retained inspection.

### Topic planning consumes typed facts directly

Extend `PlannerInputs`, its state reader, payload, initial request, and repair request
with exact comparison subjects plus request/output language. The planner preserves the
pair as scope and uses the accepted output language for planning communication. It
does not read `profile.json`, parse `request_text`, or infer/translate an absent fact.
Its materializer, zero-tool posture, retries, and state authority do not change.

## Node Agent Review

The proposal's Node Agent Review is the admission record. `ComparisonIntakeSeed` and
exact confirmation remain `no-agent`; only residual revision/question/ambiguity
classification is a zero-tool `node-agent`. The current runtime bridge owns its
budget/cancellation/retry enforcement; semantic resolver plus HITL1 retain candidate
admission, state write, artifact promotion, and route authority.

## Workflow Outcome Review

The proposal's Workflow Outcome Review is the outcome record. Missing pair and
language-choice states are correlated non-terminal HITL1 recovery until the existing
answer-round bound; a still-missing required pair then blocks rather than degrading
into an invented profile. Local confirmation has no model/provider path. Semantic
provider/output failure continues to use its existing bounded non-terminal fallback;
this change adds no retry.

## Risks / Trade-offs

- [A natural comparison form is not in the bounded grammar] -> It remains ordinary
  non-comparison intake instead of inventing a pair; add only reviewed regression
  grammar in a later change.
- [Brief summary fails language validation] -> It consumes the existing structural
  repair slot and then fails closed, never translating or defaulting silently.
- [v2 content is opened by a v1-only binary] -> Deploy one compatible application
  version and do not roll a v2 in-progress workspace back to v1-only code.
- [Option id leaks into action binding] -> Keep language IDs out of `action_ids` and
  visible-control maps; test stale/misadvertised option rejection at both runtimes.
- [Semantic revision changes new facts invisibly] -> Require a full typed candidate,
  display it in a new proposal version, and require later correlation-confirmed action.

## Migration Plan

1. Add v2 profile contracts, legacy reader, deterministic detector/parser/normalizer,
   canonical serialization tests, and state defaults/ownership validation.
2. Extend lifecycle, run experience, and retained-session option transport with strict
   current-request checks before enabling the HITL1 language-choice branch.
3. Merge intake seed into validated briefs and non-interactive admission, block missing
   pairs or unselectable languages, localize deterministic HITL1 material, implement
   local confirmation, and persist v2 fields.
4. Propagate accepted checkpoint facts to topic-planning initial/repair prompts and add
   node, lifecycle/reload, and prompt evidence.
5. Run focused intake/planner suites, strict OpenSpec validation, architecture checks,
   and the full offline deterministic gate. Credentialed demo replay remains
   supplemental and records provider behavior separately.

Rollback is code-only before any v2 profile is accepted. Once v2 content exists, keep
the compatible reader deployed; never rewrite or recompute legacy artifacts during a
rollback.

## Open Questions

None. Markers, subject grammar, language detector, confirmation set, option transport,
and legacy behavior are explicit decisions for this change.
