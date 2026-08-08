## Context

See [proposal.md](proposal.md) for the problem statement. The verified current
surfaces are deliberately narrow:

- `domain/human_interaction.py` already supplies frozen proposal, semantic-candidate,
  feedback, resolution, and typed interaction-projection contracts without graph or
  runtime imports.
- `graph/nodes/hitl1/node.py` currently combines proposal shaping, exact-text
  recognition, semantic-candidate resolution, revision checks, interaction feedback,
  profile materialization, profile writing, and graph state updates. The graph state
  already distinguishes advisory `proposed_profile` from the published `profile_ref`.
- `runtime/run_experience.py` already consumes the typed interaction projection and
  has a legacy context fallback. The new boundary can preserve that wire shape.
- `tests/scenarios/release.py` reaches the real public entry, but starts from an
  English question and injects a hand-written JSON profile after HITL1. Its
  `_LiveWebSearch` helper has no scenario-specific source filter.
- `tests/assets/release_attestation.py` validates one strict version-1 schema with
  exactly eight historical hard invariants, and
  `docs/release-attestation-2026-07-17.json` is the committed redacted evidence for
  that earlier run. A new release report cannot truthfully be compared to it merely
  because it uses the same scenario id.

The approved product decision is that the conversation remains model-led. Code only
decides whether a bounded candidate plus a verified human decision can become an
authoritative fact. The existing exact-confirmation recognition remains invisible to
the Primary User and is a reliability fast path, not the primary interaction model.

## Goals / Non-Goals

**Goals:**

- Concentrate candidate-to-fact rules for one complete research proposal in one pure
  domain module with a small typed input/output port.
- Leave HITL1 responsible for graph lifecycle effects while making its accepted and
  outstanding-decision mappings single, testable paths.
- Make the one full-real release lane exercise the actual conversational handoff and
  produce bounded evidence for the fixed Chinese Python 3.12 scenario.
- Keep a deterministic test path for every new rule; real model and web execution is
  supplementary, manually selected evidence.

**Non-Goals:**

- No new `ResearchState` field, checkpoint migration, provider policy, terminal
  controller, host product interface, or production source restriction.
- No attempt to deterministically infer arbitrary meaning from the original request.
  The request remains verbatim user authority; a model only proposes a bounded
  profile that the user may confirm or revise.
- No claim that one release run proves broad research quality, source truth, or all
  user interactions.
- No rewrite, extension, or inferred revalidation of the historical version-1
  attestation. A deterministic fixture is not a new release attestation.

## Decisions

### 1. Add one pure confirmation port, not another graph controller

The new domain module will compose the existing `human_interaction` and profile
contracts. It will define frozen inputs and closed results conceptually equivalent to:

```text
Current complete proposal + verified decision evidence
                 |
                 v
        Research Confirmation
          /                \
         v                  v
Accepted Research Facts   Outstanding User Decision
         |                  |
         v                  v
HITL1 profile writer      HITL1 typed interaction projection
and accepted route        and existing follow-up route
```

`AcceptedResearchFacts` carries only the current complete proposal and a bounded
decision basis. `OutstandingResearchDecision` carries the current or revised advisory
proposal, the next proposal version effect, and optional bounded feedback. It is not
a checkpoint record and has no request id, route, runtime handle, provider fact, or
raw response text.

The input distinguishes three proven decision bases:

1. a verified visible-control selection;
2. an exact normalized clear text confirmation; and
3. a semantic candidate produced for a response that HITL1 already verified as
   correlated to the current interrupt.

The module treats a brief and a semantic candidate as data, never as authority. It
validates the current proposal is complete before accepting it; changes from a valid
semantic revision become a new outstanding proposal; questions, ambiguity, invalid
candidates, and supplied bounded semantic feedback preserve one outstanding decision.
The current profile rules for comparison subjects and output language move into this
boundary so the graph adapter no longer patches revisions ad hoc.

Alternative considered: put a few more helpers in `hitl1/node.py`. Rejected because
the late bugs all required a coordinated change across proposal facts, semantic
admission, and presentation, and that shape would remain split across the same
callers. A new global decision/controller service was also rejected: it would own
unrelated lifecycle transitions and turn a local handoff into a competing authority.

### 2. Retain existing durable authority and make HITL1 a shallow adapter

No new accepted-fact checkpoint field is added. `request_text` remains the original
user-provided request; `proposed_profile` remains the durable advisory proposal;
`profile.json`, its `ContentRef`, and the existing profile state fields remain the
durable record only after HITL1 receives `AcceptedResearchFacts`.

HITL1 will continue to:

1. generate the advisory brief through its existing zero-tool bounded bridge;
2. validate response correlation before making a confirmation request;
3. invoke the existing semantic-intake bridge only for non-exact free text;
4. translate its direct control, clear-text, semantic candidate, or bounded failure
   into the new domain input; and
5. perform exactly one of two existing lifecycle mappings:
   - accepted facts -> `finalize_profile`, request-bundle write, and current accepted
     route;
   - outstanding decision -> current follow-up route, existing advisory profile,
     version, feedback, consumed ids, and typed projection.

This adapter begins only after HITL1 has presented an interactive complete proposal.
The existing `non_interactive_policy.auto_profile` path has no Primary User decision,
does not create this proposal/confirmation handoff, and remains outside Research
Confirmation in this change. Its current behavior must remain covered as a
compatibility case rather than being accidentally recast as user-authorized facts.

The prompt for the profile brief will explicitly ask the model to preserve stated
scope, first-party-source, language, and deliverable constraints in its existing
advisory fields. It remains a candidate-only prompt and gains no tool, route,
checkpoint, or acceptance capability. Partial-profile collection and the closed
language-choice path remain outside the new module until a complete proposal exists.

This decision preserves the `ResearchRunExperience` wire shape: it continues to
render the existing typed `InteractionProjection` and visible control without
parsing a new context protocol. Its complete-proposal formatter will expand the
bounded `PromptView.proposed_scope` capacity from eight to at least seventeen lines:
five scalar dimensions, up to eight must-answer questions, scope boundaries, custom
notes, one comparison-subject line, and output language. It will derive one labeled,
normalized line for each typed material value without the current global `[:8]` or
per-value 96-character truncation. The existing profile bounds keep that projection
finite; the formatter may normalize whitespace and control characters, but it must
not hide the tail of a typed scope or note. This is a projection of typed proposal
fields, not a dump of raw model output or response metadata. The legacy context
fallback is untouched in this change. This is required because a constraint hidden
from the shared confirmation view cannot be treated as knowingly confirmed.

### 3. Make the existing release runner data-driven around one smoke transcript

`ReleaseScenario` will own the fixed request, natural confirmation text, allowed
first-party source set, and report expectations so `execute_full_real_release` does
not carry another unreviewed transcript. The selected transcript is:

1. send the approved Chinese Python 3.12 request;
2. require the public `start` result to contain a complete typed HITL1 interaction;
3. send the natural text `确认` as the correlated response, never a profile JSON;
4. follow the existing HITL2 continuation and completion path.

The release-only source set has three verified stable Python 3.12 documents:

- `https://docs.python.org/3.12/whatsnew/3.12.html`
- `https://docs.python.org/3.12/library/venv.html`
- `https://docs.python.org/3.12/library/removed.html`

The test adapter will add the scenario's first-party restriction to its search query
and reject/filter any returned URL whose canonical URL is outside the scenario set.
Because the real Wave1 contract requires two distinct URLs that are new relative to
Wave0, the test adapter will also expose a phase-bound candidate view for this smoke.
The existing `wave0-source-intake` policy receives one stable declared page and the
existing `wave1-evidence-extraction` policy receives the other two declared pages.
When search returns only part of a phase view, the adapter may boundedly fetch the
missing members from those same declared URLs; it still fails closed if the complete
phase view cannot be formed. The bridge selects the view from the existing policy
identity, never from query-text heuristics. This is test-only source scheduling to
make the fixed three-page corpus compatible with the unchanged Wave1 new-source
floor; it does not broaden production source policy or create a new source authority.
The model-facing Wave1 initial and repair prompts also state that the candidate must
retain at least two distinct URLs that are new relative to the accepted Wave0
baseline, and their response examples show two source items. This makes the existing
validator floor actionable to the model without weakening the validator or allowing
the prompt to invent a URL when the untrusted observations do not contain enough
sources.
The completed release check will independently resolve cited record references to
their accepted `SourceRef.canonical_url` values and reject any cited URL outside the
same set, while requiring at least two distinct source-set URLs. This double check
verifies the real producer-to-consumer handoff instead of trusting a model statement
or a presentation-only assertion.

Before cleanup, the runner will derive only bounded evidence from `final/report.md`:
non-empty content and Chinese-script presence. From the citation map and accepted
records it will derive the cited claim count, declared-source-set-only verdict, and
distinct-source count. `ReleaseOutcome` and `ReleaseReport` retain booleans, counts,
and a fixed declared-source-set identifier only; they do not retain report text, raw
model text, source snippets, source URLs, or credentials. These fields extend the
fresh release report's hard-invariant map rather than create a second release runner.

Alternative considered: a production source-policy controller that enforces Python
documentation. Rejected because the product must remain open-web and the restriction
exists solely to make this small release proof repeatable. Alternative considered:
fake the HITL1 profile for the release test. Rejected because that is the bypass the
smoke test is meant to detect. Expanding the declared source set or weakening the
production Wave1 two-new-source floor was also rejected: both would change a
controlling contract instead of repairing the test-owned integration seam.

### 4. Version the release attestation instead of rewriting history

The existing version-1 validation contract and
`docs/release-attestation-2026-07-17.json` remain unchanged. Version 1 has exactly
its current eight invariant names and its own report hash, provenance, and redaction
verdicts; it is historical evidence for the old run, not a compatibility envelope for
the new smoke path. The implementation must not append fields to v1, reuse its source
hash for a new report, or compare an arbitrary local release report to that artifact.

A future version-2 attestation is a separate redacted projection of one successful,
separately selected `release-full-real-acceptance` run. It retains the existing
aggregate/provenance facts where the source report supports them, preserves the eight
legacy hard-invariant results, and adds a closed smoke-evidence set: confirmation
handoff completion, non-empty report, Chinese-script presence, minimum cited-claim
count, declared-source-set-only verdict, and minimum distinct-source count. Its
bounded source identity is a fixed source-set identifier and counts, never a source
URL or source body. The builder verifies a complete successful matching release
report; the operator's selected-run provenance and approval are external evidence it
cannot infer from JSON. It produces no durable claim during normal deterministic
tests.

The validator will dispatch by schema version while keeping v1's exact behavior.
Version-2 validation will require its fixed field/invariant set, matching report hash,
provenance separation, and the existing sensitivity scan. A local raw release report
is compared only to an attestation with its matching hash and version; an unpaired
report is evidence awaiting explicit operator review, not evidence for the historical
v1 artifact. This pairing validates payload integrity, not that an external provider
was actually invoked. Deterministic tests use synthetic, redacted bounded values to
prove v1 preservation, valid v2 admission, mixed-version rejection, mismatched
source-report rejection, and URL/body/credential rejection. They do not generate or
commit a new attestation.

Alternative considered: expand `RELEASE_INVARIANTS` in place. Rejected because the
current v1 validator deliberately requires exactly the old eight names, so that would
make the old attestation falsely appear to prove conditions it never observed.

### 5. Keep structural and evidence metadata in their current owners

Implementation will add the confirmation module and its focused test to the existing
project-structure registry, regenerate the `AGENTS.md` locator, and add the new
`RCF-001`, `HIN-014`, `EVH-024`, `RER-012`, and `PRS-016` entries to the requirement
registry.
It will update only the central evidence claims and requirement impacts that change
for the new deterministic tests, versioned attestation contract, and the existing
release selector. No static asset will claim that a credentialed release execution
occurred.

## Risks / Trade-offs

- [A model fails to preserve the user-requested source or language constraint in its
  advisory proposal] -> Strengthen the bounded brief prompt and fail the manual
  smoke rather than silently accepting an altered scope; the user can still revise
  the proposal in normal interaction.
- [The exact-source release corpus becomes temporarily unavailable in search results]
  -> The test-only adapter fails closed with bounded diagnostics. It does not widen
  the source set automatically or change production behavior.
- [Refactoring changes existing follow-up state accidentally] -> Keep existing state
  fields and response-correlation checks, introduce red-before-green domain and
  lifecycle tests, and require restart-durable revision coverage.
- [Chinese-script detection is a weak proxy for readability] -> Treat it as only a
  structural release invariant; the manually selected smoke still exposes the report
  for operator review and makes no broad quality claim.
- [A fresh report is mistakenly paired with the historical attestation] -> Keep the
  versioned schema and source-hash pairing fail-closed; leave an unpaired report as
  uncommitted evidence until a separately selected run is reviewed and produces v2.
- [New requirement identifiers temporarily make the repository registry incomplete]
  -> Register all four IDs in the same implementation change before running the full
  deterministic gate or archive checks.

## Migration Plan

1. Add the pure module, its registered paths, and direct tests before changing the
   HITL1 adapter.
2. Replace duplicated complete-proposal branches with the port while retaining the
   current state field names and profile artifact format; old checkpoints therefore
   continue through existing parsing and typed projection paths.
3. Change the release scenario, versioned attestation contract, and deterministic
   release-control-plane tests. Do not run the credentialed release lane as part of
   ordinary implementation verification.
4. After a separately authorized successful release run only, use the bounded v2
   builder and validator to prepare a reviewable attestation; otherwise preserve v1
   alone and make no fresh evidence claim.
5. Run focused tests, the canonical offline verification gate, strict OpenSpec
   validation, architecture/requirement checks, and diff/boundary checks before
   archive.
6. Roll back by reverting the domain/HITL1/release changes together. No data
   migration or external contract rollback is required because no durable schema or
   host API changes.
