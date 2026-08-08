> req: DEC-003, DEC-004

## MODIFIED Requirements

### Requirement: Public entry skill is committed and enabled

The project SHALL keep the `deep-research-controller` skill source under
`deep_research_harness/config/public-skill/`, materialize it under `skills/public/`, and
store its enabled state in `extensions_config.json`. The committed skill SHALL be the
focused cognitive workflow for the public Deep Research controller. It SHALL describe
how to classify a natural-language turn as a new research request, a correlated pending
answer, an independent same-Run direction, a status request, an explicit cancellation,
an unrelated request, or an ambiguous follow-up. It SHALL include the decision criteria,
ordered procedure, representative positive and negative examples, edge cases, target
selection rules, and typed-result handling needed to choose one legal next action.

The skill SHALL map a correlated answer only to `resume` and an independent bounded
Run direction only to `refine`; use of words such as "note", "remember", or "adjust"
SHALL NOT by itself select an action. When the current semantic subject or intended
effect is ambiguous, the workflow SHALL require clarification before any Deep Research
lifecycle call. Every lifecycle candidate SHALL be emitted as one exclusive
`deep_research` tool call. The skill may propose an action, but strict tool schema,
trusted context, Bundle-local State, and runtime lifecycle handlers SHALL remain the
only admission and effect authorities.

When a current typed result identifies an explicit available terminal Bundle with a
pending direction, the skill SHALL propose the textless `refine` continuation form only
after the user explicitly asks to continue that queued direction. It SHALL send that
selected `bundle_id` and omit `refinement`; it SHALL not reproduce or infer redacted
direction text, use a Handle or discovery as a terminal target, silently continue after
a stop/cancel/block result, or treat a new text-bearing direction as a continuation.
For any terminal typed result whose legal next action is `start` because capacity is
exhausted, the skill SHALL not propose either continuation or a new same-Bundle direction
regardless of whether a pending direction is projected. The runtime remains the sole
authority for the terminal-pending predicate, capacity, and any resulting graph
transition.

After Research Confirmation, the workflow SHALL NOT represent a request to persist or
edit `custom_notes`, `scope_boundaries`, or the canonical profile as an available hidden
lifecycle action. It SHALL make no lifecycle call or profile-write claim for that
request alone. A clear independent same-Run direction in that turn remains eligible for
the ordinary `refine` path, but still makes no profile-write claim; otherwise the
workflow MAY ask whether the user intends such a direction before proposing `refine`.

The skill SHALL describe the public entry as an all-real lifecycle, distinguish typed
action codes and the selected Bundle refinement projection for pending, applied, blocked,
unavailable, conflict, cancelled, and ended outcomes from completed research, and direct
configuration or readiness failures through documented legal controls. It SHALL NOT contain graph topology, phase prompt bodies, fixture
controls, answer payloads, caller-supplied authority, security-isolation claims, or any
rule that treats conversation memory as Run recovery. Its size bound SHALL permit the
approved focused workflow and SHALL remain within the actual DeerFlow skill loader's
supported bounded resource limit rather than enforcing a minimal byte count as a
quality property. (`DEC-003`)

For the dedicated Agent's ordinary non-slash route, the full committed workflow SHALL
be read through DeerFlow's actual skill loader before that Agent proposes a lifecycle
action. A direct normal-discovery path SHALL read the canonical public `SKILL.md`; a
configured deferred-discovery path MAY first obtain its canonical location through
`describe_skill`, but SHALL still read that file. The successful read SHALL carry the
committed content, cause DeerFlow to capture the skill reference in its durable context,
and be followed by a later AIMessage containing exactly one `deep_research` call and no
sibling tool call. Durable skill context is a re-readable reference, not a duplicate
authority or persistent copy of the full Markdown. Explicit slash activation remains
supported but SHALL NOT be represented as proof of ordinary-language loading.

The public skill SHALL NOT declare `allowed-tools` frontmatter as a controller-specific
permission boundary. That DeerFlow policy applies to every Agent that loads the public
skill; the dedicated Agent's configured groups, the existing sandbox policy, and the
lifecycle runtime are the applicable enforcement boundaries.

#### Scenario: Public skill is available
- **WHEN** configuration is materialized and enabled skills are loaded
- **THEN** the public Deep Research entry skill is discoverable with content matching its committed source beneath the canonical Harness root

#### Scenario: Public skill is available through real DeerFlow loading
- **WHEN** configuration is materialized, enabled skills are discovered, and the Deep Research skill is activated through DeerFlow's supported loader
- **THEN** the full committed workflow is loaded from the canonical public path with matching content and is present in the actual composed lead-agent context

#### Scenario: Ordinary natural-language loading precedes lifecycle control
- **WHEN** a user sends a non-slash turn to the configured dedicated Agent and the Deep Research workflow is relevant
- **THEN** the actual lead-agent sequence reads the canonical public `SKILL.md`, captures its matching durable skill reference, and only a later AIMessage may issue one exclusive `deep_research` lifecycle call

#### Scenario: Deferred discovery still reads the workflow
- **WHEN** DeerFlow deferred skill discovery is enabled for the dedicated Agent and a non-slash Deep Research turn is relevant
- **THEN** `describe_skill` may expose the canonical location before the Agent reads the matching `SKILL.md`, but neither metadata nor slash activation substitutes for that read or permits a sibling lifecycle call

#### Scenario: Public skill does not alter other Agents' tool policy
- **WHEN** the committed public skill frontmatter and the lead-agent tool-policy input are inspected
- **THEN** the skill declares no `allowed-tools` controller workaround, and the dedicated Agent's own configured group list remains the source of its ordinary-loader tool availability

#### Scenario: Pending answer and direction remain distinct
- **WHEN** the workflow is given a visible pending subject and a follow-up that either answers it or independently redirects the Run
- **THEN** it instructs the lead agent to propose only `resume` for the correlated answer and only `refine` for the independent direction, without placing the answer in tool arguments or consuming the pending subject as a side effect

#### Scenario: Ambiguous note causes clarification before mutation
- **WHEN** a user says to "note" or "fix" something but the current subject and intended lifecycle effect do not distinguish an answer from a Run direction
- **THEN** the workflow requires one clarification and no `deep_research` lifecycle call

#### Scenario: Post-confirmation profile note is not a hidden mutation
- **WHEN** an accepted profile exists and a user asks to save or edit a profile note without a clear bounded same-Run direction
- **THEN** the workflow makes no lifecycle call, does not promise a profile write, and may clarify whether the user intends an independent Run Refinement

#### Scenario: Explicit stop is not inferred from criticism
- **WHEN** a user criticizes the current direction without explicitly asking to stop
- **THEN** the workflow selects a bounded refinement only when the desired direction is clear and otherwise asks for clarification; it does not infer `cancel`

#### Scenario: Terminal queued direction requires an explicit continuation request
- **WHEN** a typed result shows an available terminal Bundle with a pending direction
- **THEN** the workflow does not continue it automatically; only a later clear user request to continue that queued direction may produce one exclusive `deep_research(action="refine", bundle_id=..., refinement omitted)` call

#### Scenario: Ambiguous terminal follow-up does not consume a direction
- **WHEN** a terminal Bundle has a pending direction and the user's follow-up does not clearly request continuation or submit a distinct bounded direction
- **THEN** the workflow asks for clarification and makes no lifecycle call

#### Scenario: Exhausted terminal result is not presented as refinable
- **WHEN** a typed terminal result names `start` as its legal next action because no future full rerun is legal, with or without a pending direction
- **THEN** the workflow does not propose textless or text-bearing `refine`, explains only the typed bounded disposition, and follows the returned fresh-start path

#### Scenario: Real lifecycle is represented honestly
- **WHEN** the entry skill handles a research request or lifecycle result
- **THEN** it preserves the returned real lifecycle mode, submitted-action code, and Bundle refinement projection, distinguishes `resume` from `refine`, does not fabricate findings or completion after a pending, blocked, unavailable, or conflict outcome, and does not describe a fixture path as a public research capability

#### Scenario: Every lifecycle action is exclusive
- **WHEN** the workflow proposes start, resume, status, cancel, or refine
- **THEN** it instructs the lead agent to issue exactly one `deep_research` call in that AI turn and no sibling tool call

#### Scenario: Legacy custom path is rejected
- **WHEN** validation finds the project entry skill under `skills/custom/deep-research-controller/` instead of the public path
- **THEN** the configuration check fails and identifies the legacy location

### Requirement: Dedicated Agent is provisioned in the effective user scope

The project SHALL provision `deep-research` Agent files only at
`{DEER_FLOW_HOME}/users/{effective_user}/agents/deep-research/`, reference the public
skill, and use the dedicated Agent only as a recommended UX route. Its committed
template and authenticated current-user API fixture SHALL use the ordered tool groups
`[deep-research-control, file:read]`. `file:read` SHALL be an existing,
operator-owned effective DeerFlow group; this project SHALL NOT define, merge, repair,
delete, or rename that group or any tool assigned to it. It exposes the full configured
group surface, not a skill-path-only reader.

Before downstream configuration creates or replaces its dedicated-Agent files, reports
that route ready, or offers its authenticated provisioning fixture as ready, it SHALL
verify that the effective configuration contains one unambiguous `file:read` group and a
tool assigned to that group whose resolved public name is `read_file`. Missing,
duplicate, or misbound prerequisites SHALL leave the dedicated entry route `not_ready`,
make no Agent file mutation, and never produce a control-only, copied-prompt, or
slash-only fallback Agent. The public skill and global control tool remain independently
governed by their existing readiness contracts.

Its SOUL guidance SHALL contain only stable Deep Research identity, truthful typed-outcome
posture, and the prohibition on fabricating research completion. The SOUL SHALL NOT
duplicate the action decision table, examples, target-selection logic, or lifecycle
admission rules owned by the public skill and runtime.

Offline filesystem configuration SHALL provision only explicit no-auth user `default`;
authenticated provisioning SHALL use current-user `POST /api/agents` only when the
operator has independently enabled `agents_api.enabled`. It SHALL NOT enable that
security-sensitive API automatically. The global control tool SHALL remain usable when
the Agent is absent.

#### Scenario: No-auth user is isolated
- **WHEN** configure provisions an explicit non-production `DEER_FLOW_AUTH_DISABLED=1` installation
- **THEN** it writes the Agent under `users/default/agents/deep-research/` and writes nothing under the shared legacy Agent root

#### Scenario: Existing read group is preflighted without downstream ownership
- **WHEN** configuration evaluates the ordinary dedicated-Agent route
- **THEN** it accepts only one effective `file:read` group with a resolved `read_file` tool, leaves the group and all of its configured tools outside the downstream manifest, and records no probe file or synthetic replacement tool

#### Scenario: Missing or invalid read prerequisite cannot create a reduced Agent
- **WHEN** `file:read` is absent, duplicated, lacks `read_file`, or its configured binding does not resolve to `read_file`
- **THEN** the dedicated entry route is `not_ready`, no Agent files are created or replaced, the authenticated fixture is not presented as ready, and the configuration does not silently use only `deep-research-control` or require slash activation

#### Scenario: Template and authenticated fixture expose the same group boundary
- **WHEN** no-auth provisioning materializes the Agent or an authenticated user requests the current-user Agent fixture after the preflight passes
- **THEN** both surfaces contain the same ordered `deep-research-control` and `file:read` groups, and neither claims that those groups expose only the public skill path

#### Scenario: Production cannot use offline auth-disabled provisioning
- **WHEN** auth-disabled provisioning is requested with `DEER_FLOW_ENV` or `ENVIRONMENT` set to production
- **THEN** configure refuses the Agent write and does not weaken or bypass DeerFlow authentication

#### Scenario: Unvalidated authenticated identity is refused
- **WHEN** offline configuration receives an arbitrary `--user-id` or runs for an authenticated deployment without current-user API attribution
- **THEN** filesystem provisioning fails without creating or modifying any user's Agent directory and directs the authenticated user to the current-user API

#### Scenario: Offline rollback does not own authenticated Agent state
- **WHEN** an authenticated user created the Agent through `POST /api/agents` and an operator rolls back the offline configuration manifest
- **THEN** rollback leaves that user's Agent untouched and directs user-owned deletion through the authenticated Agent API

#### Scenario: Rollback leaves the operator-owned read group untouched
- **WHEN** an offline configuration manifest is rolled back after it materialized the dedicated Agent
- **THEN** rollback removes only byte-identical downstream-owned Agent files and leaves the effective `file:read` group and all of its tools unchanged

#### Scenario: SOUL and skill have distinct responsibilities
- **WHEN** the provisioned Agent's composed configuration is inspected
- **THEN** SOUL supplies stable identity and honesty posture, the ordinary loader supplies the public skill's follow-up decision workflow, and neither surface claims lifecycle admission authority

#### Scenario: Dedicated Agent preserves real lifecycle honesty
- **WHEN** the dedicated Agent invokes or explains a lifecycle action
- **THEN** it identifies the selected all-real public mode, follows the typed result, does not claim exclusive tool isolation, and does not describe pending, blocked, conflict, or unavailable research as completed
