## Why

Deep Research currently spreads one research run across a conversation-derived
`research_id`, an application-selected bundle directory, external graph checkpoints,
and retained session/binding/index records. That topology contradicts the agreed
Deep Research Harness model: a Run Bundle must be the only durable record of one
independently deletable Run. This change makes the model true across lifecycle,
storage, controls, adapters, structure, and deterministic evidence before further
Deep Research work builds on the old authority split.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/runtime/` after the structural move, which owns trusted conversation context, lifecycle persistence, Run Bundle discovery, and the existing DeerFlow binding.
- **Question:** How does the Deep Research Harness create, locate, control, and expose one Run Bundle whose Bundle-local Research State is the only lifecycle authority, while allowing one active Run per outer conversation and retained ended Runs?
- **Necessary adjacent/external contracts:** `domain/` answers the typed `bundle_id`, lifecycle State, and control-result contract; `project-structure` answers the canonical filesystem-root migration and generated locator; `node-prompt-catalog` answers the moved ignored-review path; existing public DeerFlow invocation/context APIs answer how the runtime receives trusted outer-conversation scope without changes to `backend/` or `frontend/`; the named node, content-store, CLI/TUI, workbench, configuration, and evidence capabilities answer how they consume the runtime-owned Bundle contract without becoming a second controller.
- **Evidence seam:** Bundle-lifecycle integration and State-persistence tests prove creation, discovery, action-specific `resume`/`refine` control, safe refinement, loss, and isolation; contained-store tests prove identity/root propagation; adapter contract tests prove shared typed outcomes; deterministic EVH-024 control-plane tests prove the public release runner observes only Bundle facts; architecture/configuration tests prove the canonical root move. A successful credentialed report/citation execution is separate manual issue evidence.
- **Not in scope:** Changes under `backend/` or `frontend/`; renaming `deerflow-deep-research`, `deerflow_deep_research`, or `deep_research`; automatic migration, reconstruction, or external-checkpoint recovery of a lost Bundle; treating Cognitive Evaluation Bundles as Deep Research Run Bundles; new model roles or evaluation workflow semantics; or making a new credentialed release attempt succeed. The runner's deterministic lifecycle-authority migration remains in scope; its operational acceptance is deferred to `_backlog/plans/evh-024-release-acceptance-diagnosis.md`.
- **Triggered review policies:** local-context, change-admission, authority-and-projections, participant-outcomes, human-interaction-integrity, control-and-recovery, workflow-outcome-review, control-placement, agent-information-map

## What Changes

- **BREAKING:** Rename the downstream filesystem root from `deerflow_research/` to
  `deep_research_harness/`. Preserve the distribution name
  `deerflow-deep-research`, import namespace `deerflow_deep_research`, and public
  tool name `deep_research`.
- Add the canonical Deep Research Harness / Run Bundle lifecycle contract. A fresh,
  opaque `bundle_id` is the directory identity, Run identity, and public control
  identity; the previous conversation-derived `research_id` identity is retired.
- Make a Run Bundle's contained Research State, evidence, and content the sole
  durable ownership boundary for one continuing Deep Research Run. A Bundle-local
  non-terminal State is active, including while awaiting user input; a terminal
  refinement round is ended; an explicit refinement may reactivate an available ended
  Bundle for a later round.
- Replace durable active-Bundle pointers, external session bindings/indexes, and
  external-checkpoint recovery as lifecycle authority. A conversation may retain a
  transient Current Bundle Handle, but the runtime validates it against the Bundle;
  when it is absent, discovery reads only Bundle directories and Bundle-local State
  within the trusted conversation scope.
- Establish one runtime-owned Run Bundle lifecycle module as the only creator,
  locator, State mutator, refinement-admission point, and control authority. Tool,
  graph, CLI, TUI, workbench, and content-store adapters consume typed Bundle facts
  and never construct lifecycle paths, select a checkpoint namespace, or retain an
  independent active-Run controller.
- Define safe refinement admission and a non-ambiguous public action contract.
  `resume` remains the correlated response to an already-pending interaction;
  `refine` requires bounded refinement text and may target a `bundle_id`; an ended
  Bundle requires an explicit target rather than Handle-based guessing. A refinement
  takes effect only at a durable safe control point, never mutates State beneath an
  in-flight writer, and cannot reactivate an ended Bundle while another Bundle is active
  in the same trusted scope.
- Define deletion and failure truthfully. External removal or unavailability of a
  Bundle makes that Run unavailable permanently; it is not recovered from an
  external checkpoint, session record, log, cache, or replacement State. A fresh
  independent Run remains legal. Cognitive Evaluation Run Bundles remain a separate
  domain, storage area, and discovery path.
- Preserve the existing EVH-024 full-real release selector's deterministic
  Bundle-authoritative execution and observation boundary. It continues to call the
  public entry and cannot use a legacy identity, GraphHost snapshot, external
  checkpoint, or workspace-derived path as a lifecycle or result authority. A new
  credentialed successful report/citation execution is deferred to the linked
  release-acceptance diagnosis issue and is not this change's closeout gate.
- Migrate structural registry entries, commands, mounts/profiles, fixtures,
  documentation, public-agent instructions, and deterministic tests to the canonical
  root and `bundle_id` vocabulary while keeping historical archives factual.

## Capabilities

### New Capabilities

- `deep-research-harness-run-bundles`: Defines the authoritative Harness, Run
  Bundle, Bundle-local State, identity, discovery, refinement, deletion, isolation,
  and typed-control semantics.

### Modified Capabilities

- `research-graph-lifecycle`: Moves Deep Research lifecycle persistence and action
  transitions to Bundle-local State and removes external checkpoint recovery as a
  lifecycle authority.
- `runtime-integration`: Makes the public runtime/tool boundary use the opaque
  `bundle_id`, trusted conversation scope, and shared typed outcomes.
- `research-run-session`: Retires the retained-session record as a lifecycle owner
  and preserves only inspection facts compatible with Bundle authority.
- `research-session-lifecycle-binding`: Removes external binding/index authorization
  and checkpoint identity as a way to control or recover a Run.
- `research-session-discovery-and-operations`: Replaces session discovery and
  operation resolution with scoped Bundle-local discovery and control.
- `research-session-artifact-view`: Rebinds retained inspection to an available Run
  Bundle without treating view data as lifecycle authority.
- `research-local-session-workbench`: Makes the local workbench consume typed Bundle
  controls and status rather than preserve a local controller.
- `research-run-experience`: Projects Bundle-owned lifecycle outcomes and legal next
  actions consistently to human and AI consumers.
- `bootstrap-node`: Publishes the initial Bundle and its State/content atomically
  before a Run becomes discoverable.
- `work-unit-kernel`: Gives content-producing stores one runtime-supplied Bundle
  identity/root and preserves contained-write semantics without caller-supplied
  lifecycle paths.
- `hitl1-node`: Keeps human-input artifacts and State facts bound to the current Run
  Bundle rather than a derived research identity or external checkpoint namespace.
- `node-agent-runtime`: Carries the authoritative Bundle context through node-agent
  execution without creating a parallel checkpoint or path authority.
- `node-prompt-catalog`: Moves the ignored prompt-review workspace to the canonical
  Harness root without making it runtime authority.
- `topic-planning-node`: Keeps planning artifacts and State reads/writes within the
  current Bundle identity/root.
- `wave1-node`: Keeps worker evidence and work-unit artifacts within the current
  Bundle identity/root.
- `wave2-synthesis-node`: Keeps synthesis evidence/content and State interaction
  within the current Bundle identity/root.
- `research-cli-onboarding`: Uses `bundle_id`-based lifecycle outcomes and truthful
  unavailable/ended/refinement guidance.
- `research-demo-tui`: Uses the same `bundle_id` vocabulary and lifecycle outcome
  contract as the public tool.
- `demo-pipeline`: Removes derived research/session identity from demo lifecycle
  wiring and fixtures.
- `research-fake-cli-onboarding`: Keeps deterministic fake onboarding aligned with
  the real Bundle lifecycle contract.
- `project-structure`: Declares `deep_research_harness/` as the canonical downstream
  filesystem root and updates the structural registry/locator protocol.
- `deployment-configuration`: Updates deployment-facing paths, mounts, and commands
  to the canonical root without changing package/import/public-tool identities.
- `local-configuration-profiles`: Updates local profiles and run locations to the
  canonical root and scoped Bundle layout.
- `fixture-source-isolation`: Keeps fixture isolation valid after the structural-root
  move and Bundle identity migration.
- `deep-research-agent-charter`: Moves the downstream agent-entry/documentation
  routes to the canonical root while preserving their bounded information-map role.
- `cognitive-evaluation-suite`: Preserves the separate Cognitive Evaluation Bundle
  domain and updates its governed root references without granting it Deep Research
  discovery or lifecycle authority.
- `evaluation-hardening`: Requires deterministic evidence for Bundle creation,
  discovery, refinement, loss, isolation, the absence of external recovery authority,
  and EVH-024's Bundle-bound release execution. The manually selected full-real
  success acceptance remains a separately owned diagnostic issue.

## Impact

The implementation will replace the Deep Research runtime/session/checkpoint authority
stack; update Bundle and content-store contracts; migrate the downstream root in
governance, build, container, profile, fixture, documentation, and test consumers; and
update local presentation/adapters to a single typed result vocabulary. It also migrates
the existing release runner's execution/inspection boundary without changing its model,
source-set, interaction, or report-quality semantics. The change is
intentionally confined to the downstream project and its OpenSpec governance. It does
not add a host integration API, alter the upstream DeerFlow services, or require a
successful credentialed release execution before closeout.

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Fresh Bundle identity and first publication | None | The runtime-owned lifecycle module creates one fresh opaque `bundle_id` and atomically publishes Bundle-local State/content. | non-bypassable | A discoverable Run always has its authoritative Bundle and never derives identity from a conversation. | Replaces `research_id` plus separately selected bundle directory. | Focused lifecycle creation and atomic Bundle-publication tests. |
| Current Bundle Handle and absent-handle discovery | None | The lifecycle module validates the handle, or scans only trusted conversation scope and Bundle-local State. | non-bypassable | A handle cannot prove existence/status; absence, corruption, or ambiguity fails closed. | Avoids a durable active pointer, registry, binding, or index. | Handle continuation, absent-handle, ambiguity, and cross-conversation discovery tests. |
| Run Refinement admission | A Primary User supplies bounded refinement text; `resume` remains a distinct correlated pending-input response. | The lifecycle module validates the target Bundle and durably admits `refine` at a safe control point. | human-decision | No in-flight writer is overwritten; an ended target cannot be reactivated while another Bundle is active in its scope. | Reuses one Bundle lifecycle boundary instead of adapter-local mutation/retry logic. | Action-separation, concurrent refinement, pending-input, safe-point, and ended-Bundle reactivation tests. |
| Bundle loss | None | Filesystem availability plus Bundle-local State are evaluated by the lifecycle module. | non-bypassable | A deleted/unavailable Bundle cannot be reconstructed, rebound, or recovered from an external checkpoint. | Removes recovery authority from session/binding/checkpoint/cache layers. | Deletion-before-control, deletion-during-run, and fresh-independent-start tests. |
| Human/AI control outcome projection | None | A typed Bundle lifecycle result owns `bundle_id`, availability/lifecycle outcome, and legal next action; adapters only project it. | advisory | A presentation, diagnostic, or retained view cannot authorize/resume a Run. | Avoids tool/CLI/TUI/workbench-specific lifecycle inference. | Public-tool, CLI/TUI, and workbench contract tests. |
| EVH-024 full-real release execution and observation | The model proposes HITL1 content and a Primary User gives natural confirmation. | Bundle lifecycle and contained report/citation artifacts own lifecycle/result facts; the release runner invokes and observes the public entry. | non-bypassable | The release selector cannot inject a profile, derive a legacy identity/path, or recover/observe through GraphHost or an external checkpoint. | Retains one existing release runner rather than adding a parallel release workflow. | Release control-plane and selected full-real acceptance tests. |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Bundle missing or deleted before/during a control action | Bundle availability and Bundle-local State, evaluated by the lifecycle module | None; external records are observation-only and may not recover the Run. | `unavailable` for that Run, not a synthetic terminal State. | Start a fresh independent Run; inspect only still-available external observations. | Bundle-loss lifecycle integration tests. |
| Current Handle is absent, stale, corrupt, or points outside trusted scope | Scoped Bundle discovery in the lifecycle module | One bounded scoped inspection; no global fallback or index lookup. | Typed unavailable/not-found/ambiguous control outcome as appropriate. | Provide an explicit valid available Bundle target or start a fresh Run. | Handle/discovery and isolation contract tests. |
| Concurrent start or refinement could produce competing active Runs | Scope coordination and Bundle-local State mutation in the lifecycle module | One bounded serialized admission attempt; no adapter retry controller or second active pointer. | Typed conflict/unchanged outcome with the existing active Bundle preserved. | Continue, control, or refine the selected active Bundle. | Concurrent start/refinement deterministic tests. |
| Refinement arrives while another writer owns an in-flight State update or the Run awaits a response | Bundle-local State and safe control-point protocol | The lifecycle module persists an admitted `refine` action for the next legal durable point; it never rewrites an in-flight write or consumes the pending response. | Existing Run remains active or reaches its normal typed disposition; no partial overwrite. | Submit the correlated `resume` response, observe status, or wait for the typed next control outcome. | Action-separation, safe-point ordering, and State reload tests. |
| Legacy external checkpoint/session/binding exists after the Bundle is gone | Bundle availability remains the sole lifecycle fact; legacy record is observation-only. | None; no automatic migration or recovery path. | `unavailable` for that legacy Run reference. | Start a fresh independent Run or inspect non-authoritative diagnostics. | No-external-recovery and legacy-record regression tests. |
| Selected EVH-024 execution finds the Bundle missing or unreadable | Bundle lifecycle availability and Bundle-contained output artifacts. | None; the release runner records a bounded failed attempt and never reads a legacy snapshot or workspace path. | Release proof fails rather than inferring a result. | Re-run only through a newly selected release execution. | Bundle-authoritative release control-plane tests. |
