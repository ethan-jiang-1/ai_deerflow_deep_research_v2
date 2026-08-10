## Context

The proposal records why this change exists. The verified implementation facts that
shape its design are narrower:

- `scripts/_demo_core.py` builds every credential-backed registry entry when
  `DEERFLOW_DEMO_MODEL` is absent, while the default node-agent model resolver selects
  `app_config.models[0]`. The real demo therefore has an incidental ordering dependency.
- `BundleGraphExecutor._journal_envelope()` creates a `RunObservationRecorder` only
  after the lifecycle has selected an admitted Bundle. It is the correct point to add
  trusted execution provenance to Bundle-local evidence without making the Journal a
  Bundle selector.
- `BudgetMiddleware` raises a typed stop with a private detail for several distinct
  model/token/tool limits. The bridge currently collapses those to the broad
  `budget.exhausted` failure category. The bridge wall-time cap is already a distinct
  `provider.timeout` with `bridge_wall_time_budget` origin.
- Wave1 already publishes separate initial and repair Journal validation facts. Wave0
  and topic planning perform the corresponding parser/materialization work but do not
  currently publish it.

The accepted `demo-pipeline`, `run-event-journal`, `node-agent-runtime`,
`topic-planning-node`, and `wave0-node` specs remain the behavioral authorities. The
new deltas add bounded evidence only; they do not make a Journal, a profile, or a
diagnostic a lifecycle authority.

## Goals / Non-Goals

**Goals:**

- Make every all-real demo choose one explicit, testable profile before any Bundle
  exists.
- Retain enough redacted Bundle-local evidence to compare selected profiles and locate
  known budget or structured-output failure boundaries.
- Use one closed representation for budget-stop and parser/materialization evidence,
  with deterministic tests at the lowest responsible seam.
- Give operators a bounded, opt-in calibration procedure that uses fresh Bundles and
  read-only inspection rather than external logs or a new control surface.

**Non-Goals:**

- Select, rank, or change a default model; qualify a model from a single run; alter
  model/provider credentials, prompts, budgets, tool windows, retries, repair counts,
  routes, checkpoint state, terminal behavior, or legal lifecycle actions.
- Record raw model or provider traffic, URLs, prompts, drafts, exception text, secrets,
  or external diagnostics; create a global profile history outside a Bundle.
- Modify DeerFlow, `backend/`, or `frontend`, or use a real provider call as the
  acceptance proof for this change.

## Decisions

### 1. Resolve one profile at the real-demo composition root

The demo core will introduce a typed, redacted profile-resolution result over the
existing registered profiles. The result is either exactly one credential-backed
profile or the existing safe configuration prerequisite failure. It is resolved before
`DemoAdapter`/real-runtime composition can create an executor or dispatch a lifecycle
start. The selected config is the sole entry supplied to the demo `app_config`, so the
bridge may retain its current first-entry resolver without accidental selection.

```
DEERFLOW_DEMO_MODEL
        |
        v
trusted demo profile resolver -- invalid --> existing prerequisite result, no Bundle
        |
        v
one selected config + redacted evidence
        |
        v
all-real composition -> lifecycle admits Bundle -> Journal admission/summary
```

This applies to every all-real CLI/TUI composition. The existing prepared launcher
already exports `DEERFLOW_DEMO_MODEL`; it remains an explicit composition input, not a
second resolver default. Fixture and full-fake paths do not need a profile and must not
invent one.

Alternative considered: change `RuntimeNodeAgentBridge` to choose a model by selector.
Rejected because generic runtime model resolution has no authority to interpret a demo
operator's configuration and would scatter an admission prerequisite across every node.

### 2. Make profile provenance a Bundle-local observation, not state

The composition root creates a small immutable `execution profile evidence` value with
only:

- a registered profile identity; and
- a bounded version-controlled safe revision declared beside that profile in the
  registry.

The registry revision is bumped when the profile's model binding or supported connector
configuration changes, but it contains none of the changed values. It excludes
credentials, environment values, raw endpoint URL, prompt, provider body, and runtime
model-object properties. This makes a revision reviewable without using a digest as a
disguised endpoint or credential receipt.

That value travels only in the runtime-owned trusted envelope. During
`_journal_envelope`, the selected Bundle's recorder writes it to the admission event
and summary. The Journal contract permits this value only at those two locations and
requires them to match. It does not enter graph state, a checkpoint, a node request, a
model prompt, an artifact, a public control request, or a lifecycle result. The Journal
has one writer per selected Bundle and therefore remains the source of its retained
facts; the Bundle lifecycle remains the only authority for selection and legal actions.

The persisted Journal schema evolves additively: the new reader accepts existing
retained Journal versions without profile evidence, and new profile-aware entries are
validated strictly. Existing Bundle files are not rewritten. Inspection of a legacy
entry reports absence rather than guessing. A deployment rollback can lose visibility
of a newer diagnostic representation, but cannot affect an admitted Bundle's graph or
lifecycle; operational rollback must preserve the current reader for any retained
Bundle that requires the new evidence.

Alternative considered: retain profile provenance in a process-global log or add it to
checkpoint state. Rejected because it would either outlive the Bundle or turn an
execution configuration observation into graph/lifecycle data.

### 3. Preserve the broad failure contract and add an internal closed cause

`BudgetMiddleware` will attach a typed closed budget-stop cause at the point where it
knows the boundary. The bridge maps that cause, and its own wall-time deadline, to the
closed Journal vocabulary in `REJ-007`. A private per-invocation bridge result envelope
passes the cause to `_record_result` and is discarded before `run_agent` returns. The
existing `NodeFinishReason`, `RunFailureCode`, `NodeProblem`, graph-facing
`NodeExecutionResult`, provider-timeout origin, recovery table, and graph route do not
change. The private projection must not turn raw `PhaseAgentStop.detail` into a domain
or Journal value.

The Journal accepts a budget-stop reason only on the existing attributable model/tool
invocation event. For middleware stops it accompanies the existing `budget.exhausted`
category; for the bridge deadline it accompanies the existing `provider.timeout`
category as `bridge_wall_time`. The bridge's existing normalized timeout-origin contract
is not duplicated into the Journal. Other failure classes carry no reason. An `unknown`
closed value is preferable to parsing or retaining new raw error detail.

Alternative considered: expose middleware exceptions directly or add a retry wrapper
for each reason. Rejected because both approaches break redaction or create a competing
recovery authority.

### 4. Reuse Wave1's validation-event pattern at the other parser boundaries

Wave0 and topic planning will receive small local helpers that canonicalize only their
known parser/materializer failure families and publish through the existing optional
event recorder. They emit an `initial` validation fact whenever a candidate reaches the
relevant parser/materializer boundary; a repair fact exists only if the existing repair
returns a candidate that reaches the same boundary. Success is represented by an empty
code collection. A model/provider failure before a candidate exists remains a model-tool
or recovery fact, not a synthetic validation event.

Wave0's helper has the existing `WorkSpec`/`Attempt` correlation. Topic planning has
phase-level correlation because its current parser/materializer operation is not a
work-unit attempt. Both continue to swallow Journal-persistence faults as the existing
observation adapter does, preserving production behavior.

Alternatives considered: record all raw parser errors, or put validation decisions in
the generic work-unit controller. Rejected because raw errors can contain user/model
content and the planner is not a work unit; each existing deterministic boundary already
owns its own validation and one-repair behavior.

### 5. Treat calibration as a documented evidence loop, not automation

The operator procedure will use an explicit profile environment value, the existing
scripted all-real demo, and the existing read-only Bundle inspection command. Each
candidate run gets a fresh Bundle and fixed scripted question. An operator can compare
only the retained profile identity/revision, phase, closed failure category,
budget-stop reason, and canonical validation codes. It makes no quality or release
claim and does not change config based on results.

Deterministic proof comes first: resolver/preflight, journal serialization/redaction,
bridge mapping, and node event tests. A credentialed run is optional bounded evidence
after implementation, never a test required to apply or archive this change.

## Ownership And Flow

| Fact | Existing/new writer | Retained location | Cannot control |
| --- | --- | --- | --- |
| Selected real-demo profile | Trusted demo composition root | Runtime-only redacted evidence, then Bundle Journal admission/summary | Bundle selection, graph state, node prompt, lifecycle action |
| Bundle identity and lifecycle | Existing Bundle lifecycle | Existing Bundle/checkpoint/lifecycle projection | Profile resolver or Journal |
| Budget-stop cause | Budget middleware / bridge deadline mapping | Existing model-tool Journal event | Retry, route, checkpoint, terminal result |
| Parser/materializer validation | Wave0 or topic-planning deterministic boundary | Existing validation Journal event | Candidate admission, ledger, controller, route |
| Journal health | Existing observation store | Bundle diagnostics subtree | Graph execution or lifecycle behavior |

## Risks / Trade-offs

- **[Risk] Profile revision leaks configuration detail.** -> Use only the bounded
  version-controlled registry revision and lock serialization tests against
  credentials, endpoints, prompts, provider bodies, and dynamic configuration values.
- **[Risk] A retained profile is treated as proof of model quality.** -> Keep the
  calibration procedure operator-only and state that the Journal records outcomes, not
  qualification or a default-selection decision.
- **[Risk] New Journal facts accidentally affect recovery or routing.** -> Preserve the
  existing result/recovery contracts, keep the recorder optional and failure-isolated,
  and test unchanged terminal behavior alongside each new fact.
- **[Risk] Canonicalization hides a new defect behind `unknown` or a fallback code.** ->
  Use closed mappings, focused fixtures for every current known branch, and make a new
  producer reason an explicit future contract change instead of parsing raw detail.
- **[Risk] Bundle schema evolution makes retained records harder to inspect during
  rollback.** -> Keep new readers backward compatible, do not rewrite existing Bundles,
  and retain the new reader while any newly written Bundle needs its diagnostic view.

## Migration Plan

1. Add typed profile and closed diagnostic contracts plus red-before-green unit tests.
2. Bind the profile at real-demo preflight/composition, then thread only its safe
   evidence through the runtime envelope to Journal admission/summary creation.
3. Add bridge and node validation-event publication with focused deterministic tests;
   verify unchanged routing/recovery in the existing graph seams.
4. Update the operator procedure and test-evidence registries, then run the targeted
   tests and complete offline verification.
5. Do not migrate old Bundle files. On rollback, stop creating new profile-aware
   demos if needed; never use Journal state to resume, repair, or alter an existing
   Run.
