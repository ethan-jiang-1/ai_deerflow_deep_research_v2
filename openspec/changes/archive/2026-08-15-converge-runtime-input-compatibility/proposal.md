## Why

The runtime currently accepts a trusted-context compatibility marker, gives a
legacy deployment checkpointer precedence over the unified database setting, and
reads three endpoint aliases from an externally owned AppConfig shape. Existing
tests prove the local behavior and its fail-closed guards, but no repository record
identifies the supported host producers, deployment configurations, or AppConfig
versions that would authorize preserving, retiring, or expanding those surfaces.

The recommended disposition is a clean downstream cutover: only project-owned
canonical inputs remain supported, while every unregistered compatibility input is
explicitly denied or omitted at its narrow local boundary. It does not infer a
deployment decision from the prior run-input change; this proposal is the decision
record that recommends the cutover for approval.

## What Changes

- **BREAKING (trusted context):** retire the trusted
  `disable_clarification=true` compatibility marker. Only
  `non_interactive=true` with the existing closed policy admits marked lifecycle
  input; the retired marker receives the existing typed pre-mutation interactive
  requirement denial and never falls back to ordinary interactive execution.
- **BREAKING (deployment config):** retire legacy `checkpointer` precedence. A
  non-null legacy section is rejected before GraphHost/provider creation and safe
  diagnostics identify the configuration as unsupported; `database` becomes the
  sole local provider-classification input.
- **BREAKING (endpoint observation):** retain only the exact selected model
  configuration's `base_url` field for safe endpoint-authority observation.
  `openai_api_base` and `api_base` are retired observation aliases; their presence
  yields no endpoint observation and cannot alter model, provider, or lifecycle
  behavior. The local reader still rejects disagreement, malformed values, userinfo,
  and unknown reflection.
- Keep the two workstreams semantically independent: trusted-context owns only
  marker admission, while deployment-config owns checkpointer precedence and
  endpoint-observation aliases. They share the source inventory only; neither
  cutover is evidence for the other.
- Publish the clean-cutover notice in `deep_research_harness/docs/local-operations.md`.
  Emergency rollback is a separately approved hotfix/revert of the
  complete local reader change, never an in-process compatibility switch; it
  preserves all existing fail-closed guards.
- Preserve the current no-forgery boundaries: caller and presentation input cannot
  create trusted context; conflicting or malformed configuration stays fail closed;
  GraphHost and diagnostics select and report the same provider; diagnostic
  projection never leaks a DSN, secret, or unnormalised endpoint.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `runtime-integration`: make the trusted-context and effective-provider
  compatibility dispositions explicit, including the required denial and rollback
  boundaries before a legacy reader can be retired or retained.
- `runtime-operations`: make the canonical non-interactive marker and retired-marker
  denial explicit at lifecycle admission.
- `node-agent-runtime`: make the selected-model endpoint-alias support decision
  explicit while preserving the endpoint observation's non-authoritative,
  fail-closed role.

## Impact

- Planned implementation is limited to `deep_research_harness/` runtime admission,
  provider classification/diagnostics, and selected-model endpoint observation,
  plus focused deterministic tests and the three listed capability deltas.
- The project-owned source and test inventory is the evidence boundary for this
  clean cutover; no unregistered host, deployment, or AppConfig version receives a
  support promise. It does not make DeerFlow source, an external host, an external
  deployment, or external retained data part of this change.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/`
  gitlink. This proposal owns no DeerFlow boundary, provider implementation, new
  Gateway command, new graph authority, retained-data migration, or external Python
  support promise.

## Program Focus

- **Program outcome:** Every admitted runtime-host input has one explicit clean
  cutover disposition: canonical project-owned input is accepted, and each retired
  compatibility input is denied or omitted at its narrow local boundary.
- **Candidate / obligation budget:** EC-C05, EC-C07, PC-C07, RC-C04, EC-C03, RC-C05
- **Declared workstream order:** trusted-context, deployment-config
- **Program decision authority:** The post-migration convergence plan owner approves
  only the frozen scope, order, and whole-program archive closure. The Runtime and
  Deployment Owners respectively approve their compatibility facts; the program
  authority owns no trusted context, AppConfig fact, State write, or provider
  selection.
- **Shared archive invariant:** The canonical internal writer remains
  `non_interactive=true`; retired markers fail before Bundle/graph mutation;
  `database` is the sole provider-selection configuration and GraphHost/diagnostics
  agree without secret projection; endpoint observation derives only from the exact
  selected `base_url` and never becomes model, lifecycle, or endpoint authority.
- **Program failure / recovery:** A missing, stale, conflicting, or unsupported
  input fails through its named deterministic boundary without fallback. Emergency
  rollback may restore only the complete pre-cutover local reader through a
  separately approved hotfix/revert; it never rewrites an input, silently changes a
  selected provider, or promotes a diagnostic observation to authority. A failed
  workstream remains active for an approved repair or plan-level re-scope; neither
  workstream can archive independently.
- **Split / expansion rule:** No host producer, deployment provider, AppConfig
  version, legacy configuration reader, endpoint field, external Python consumer,
  retained-data migration, Gateway command, graph authority, or DeerFlow change
  receives new support in this program. Any such request requires a later approved
  change with its own inventory and migration decision.
- **Not in scope:** Changing graph topology, bundle/checkpoint ownership, local
  profile isolation, model creation semantics, actual provider implementations,
  external deployment configuration, retained Bundle data, or the `deerflow/`
  gitlink.

### Workstream Focus: trusted-context

- **Primary module / causal owner:** `runtime_adapter` trusted-envelope boundary
  together with `tool.py` lifecycle admission; the adapter establishes trusted
  context and the tool validates it before a Bundle can be published.
- **Seam classification:** deterministic-guardrail because marker acceptance is a
  closed pre-mutation validation decision, not a presentation or graph route.
- **Question:** How does lifecycle admission retire the unregistered
  `disable_clarification=true` marker while retaining canonical
  `non_interactive=true` validation, a stable denial, and a controlled hotfix
  rollback without making trusted context public input?
- **Necessary adjacent/external contracts:** `runtime-integration` answers where
  trusted context is constructed; `runtime-operations` answers closed-policy
  admission and no-write denial; `research-run-experience` answers that the only
  project writer is canonical; external host producers answer only their approved
  inventory rows, not runtime behavior.
- **Evidence seam:** Trusted-envelope-to-tool focused tests with canonical, alias,
  missing-policy, incidental-policy, stale, and forged-context inputs; a static
  internal-writer scan proves project writers remain canonical.
- **Not in scope:** Creating a public context argument, changing HITL policy
  semantics, backfilling a Bundle checkpoint, accepting a presentation marker, or
  discovering unregistered host behavior at runtime.
- **Triggered review policies:** change-admission, authority-and-projections, control-and-recovery, workflow-outcome-review, control-placement
- **Candidate / obligation IDs:** EC-C07, EC-C03
- **Target / retirement:** The target is the canonical `non_interactive=true`
  contract. `disable_clarification` is retired with explicit stale-marker denial,
  never an implicit fallback to interactive execution; rollback restores the whole
  prior reader only through a separately approved hotfix and cannot grow the producer
  inventory.
- **Surface grade:** Trusted runtime context is cross-boundary input; the internal
  writer is application-owned. Any alias window is a bounded compatibility promise,
  not a public caller argument.
- **Decision authority:** Runtime Integration Owner owns trusted-context semantics;
  Product Owner approves this clean cutover and any emergency rollback. The program
  authority owns none of these facts.
- **Negative path / recovery:** Missing policy, forged context, a stale marker, or
  a marker conflict cannot publish a Bundle or mutate graph state. Rollback restores
  only the whole prior reader through a separately approved hotfix and retains the
  same exact-policy and no-reinjection guards.

#### Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Trusted-context alias retirement | Product Owner approves clean cutover; no model or caller proposes trust | Runtime adapter establishes trusted envelope; tool admission validates canonical marker/policy and retired-marker denial | non-bypassable | Retired, forged, or incomplete input cannot publish a Bundle; rollback is a complete controlled revert | Reuses closed policy validator; avoids a public context option or second lifecycle authority | Envelope-to-tool tests and canonical-writer scan |

#### Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Retired trusted marker or closed-policy violation | Runtime admission validator | Runtime owner denies before publication; emergency recovery is a complete controlled revert | Typed pre-mutation interactive-requirement denial | Use canonical marker with a closed policy | Marked-start/resume/refine negative tests |

### Workstream Focus: deployment-config

- **Primary module / causal owner:** `runtime/checkpoint.py`
  `resolve_effective_provider()`; it classifies the effective provider consumed by
  GraphHost and diagnostics and is the only local location that can keep their
  reports in parity.
- **Seam classification:** deterministic-guardrail because provider precedence and
  endpoint-observation normalization must resolve or deny known shapes without
  selecting a provider, model, or lifecycle route through a diagnostic projection.
- **Question:** How does the local runtime reject unregistered legacy
  `checkpointer` input and restrict endpoint observation to selected `base_url`,
  while retaining independent notice, denial, and controlled hotfix rollback rules
  for the two retired configuration surfaces?
- **Necessary adjacent/external contracts:** `runtime-integration` answers
  effective-provider parity and safe diagnostics; `node-agent-runtime` answers the
  exact selected-config endpoint observation boundary; local configuration profiles
  answer that profile isolation continues to reject legacy checkpointer selection;
  external deployment/AppConfig owners answer their approved inventory rows only.
- **Evidence seam:** Provider-matrix and GraphHost/diagnostics parity tests with
  planted conflicts and malformed legacy inputs; selected-config alias tests with
  normalised agreement, disagreement, malformed, userinfo, and unknown shapes;
  redaction tests prove no DSN or credential projection.
- **Not in scope:** Changing `make_checkpointer`, AppConfig parsing, model factory
  behavior, the selected model, a remote endpoint, live provider connectivity, or
  accepting fields through model-object reflection.
- **Triggered review policies:** change-admission, authority-and-projections, control-and-recovery, workflow-outcome-review, control-placement
- **Candidate / obligation IDs:** EC-C05, PC-C07, RC-C04, RC-C05
- **Target / retirement:** `database` is the sole provider input, and selected
  `base_url` is the sole endpoint-observation field. Legacy `checkpointer`,
  `openai_api_base`, and `api_base` are independently retired; a hotfix rollback of
  one local reader cannot be used as support evidence for another.
- **Surface grade:** Deployment AppConfig and selected-config fields are
  cross-boundary configuration shapes; provider selection is a runtime-owned
  classification; the endpoint value is a safe non-authoritative observation.
- **Decision authority:** Deployment Owner owns checkpointer precedence and
  supported config versions; Runtime Integration Owner owns safe local
  classification/projection; Product Owner approves the clean cutover and any
  emergency rollback. The program authority owns none of these facts.
- **Negative path / recovery:** A stale or conflicting checkpointer input cannot
  silently reduce durability or diverge diagnostics from GraphHost. An unsupported,
  conflicting, malformed, or credential-bearing endpoint shape cannot create an
  endpoint observation. Rollback restores only a whole prior reader through an
  approved hotfix and never selects an unenumerated provider or endpoint alias.

#### Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Checkpointer precedence retirement | Deployment Owner approves database-only selection | `resolve_effective_provider()` classifies database-only input; GraphHost and diagnostics consume the same result | non-bypassable | Legacy input cannot silently select the wrong durability; rollback retains provider parity | Reuses provider classifier; avoids separate diagnostic selection | Provider matrix plus GraphHost/diagnostics parity tests |
| Endpoint alias retirement | Deployment/Product Owner approves selected-`base_url` observation only | `_configured_endpoint_authority()` normalizes only `base_url` and returns no observation for retired/unsafe shapes | non-bypassable | A retired or unsafe field cannot affect model/lifecycle authority or expose credentials; rollback is a complete controlled revert | Reuses selected-config normalizer; avoids model-object reflection | Alias agreement/disagreement, malformed, and redaction tests |

#### Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Legacy checkpointer or conflict with database | Provider classifier | Deployment owner may roll forward a database config or approve a complete revert | Safe unsupported-provider classification, never silent fallback | Remove legacy section and provide a supported database config | Provider conflict matrix and diagnostics parity tests |
| Retired, conflicting, or unsafe endpoint alias | Selected-config endpoint normalizer | Runtime owner emits no observation; emergency recovery is a complete controlled revert | Missing safe observation without lifecycle mutation | Use normalized selected `base_url` | Alias/secret negative tests |
