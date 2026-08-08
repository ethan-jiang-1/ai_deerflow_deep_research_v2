# deployment-configuration Specification

> req: DEC-001, DEC-002, DEC-003, DEC-004, DEC-005, DEC-006

## Purpose
How the Deep Research downstream package is loaded, configured, materialized, provisioned, and diagnosed across environments without modifying upstream source.
## Requirements
### Requirement: Gateway loads one downstream package in every supported environment

The project SHALL provide local-development, local-production, and Docker assembly that
resolves `deerflow_deep_research` from the checked-out or mounted
`deep_research_harness/src` source while leaving upstream source unchanged. Each start
SHALL inject a secret-free, canonical, strictly parsed `v1:<64 lowercase hex>`
fingerprint of the effective startup-only provider/sandbox/normalized-worker inputs for
runtime drift detection; missing, malformed, or unknown-version fingerprints SHALL fail
closed and launch code SHALL NOT evaluate fingerprint command output as shell source.
Host package source SHALL NOT be mounted into the research sandbox.

The loadable-source mechanism is verified with contract tests: the `prepare.py`
preparation core performs upstream-equivalent sync plus `--no-deps` editable
installation into the backend environment, validates config-target agreement and
version, verifies harness/module origin, and computes a secret-free startup candidate.
The Docker Compose override read-only mounts `deep_research_harness/src` at the private
container target `/app/deep_research_harness/src`, exports that target as the
Gateway-only `PYTHONPATH`, and exports the container-effective candidate. Project-owned
live launch automation and deployment verification require a provisioned deployment
environment and remain outside this downstream package's scope.

#### Scenario: Editable source is resolved by the preparation core
- **WHEN** the preparation core runs against a caller-quiesced backend environment
- **THEN** it proves the AppConfig and upstream config-upgrade targets are the same canonical file, passes exact-current-version preflight, runs upstream-equivalent dependency sync before the `--no-deps` editable install, verifies compatible DeerFlow 2.1 harness and module origin, computes a secret-free startup candidate, and Python resolves `deerflow_deep_research` from the current `deep_research_harness/src` tree

#### Scenario: Mismatched upstream config is refused before fingerprinting
- **WHEN** the effective config version is missing, invalid, older, or newer than `config.example.yaml.config_version`
- **THEN** preparation performs no shared backend-environment mutation or fingerprint and directs the operator to upgrade an older config or reconcile the config/checkout pair for any other mismatch

#### Scenario: Ambiguous config targets are refused
- **WHEN** AppConfig resolution and the current upstream config-upgrade search order select different canonical files, including an unqualified root/backend shadow pair
- **THEN** preparation performs no shared backend-environment mutation or fingerprint and reports the conflicting paths without exposing their contents

#### Scenario: Docker exports the container-effective candidate
- **WHEN** the base-first Docker override renders the Gateway command
- **THEN** it read-only mounts `deep_research_harness/src` at `/app/deep_research_harness/src`, sets that exact Gateway-only `PYTHONPATH`, and computes and exports the candidate inside the container from the mounted source and effective config before the unchanged uvicorn tokens, without mounting host source into the research sandbox

#### Scenario: Startup-only drift requires restart
- **WHEN** live config reload changes effective database/checkpointer or sandbox values after the launcher captured the process-start fingerprint
- **THEN** doctor and runtime integration report `restart_required` before nested provider or sandbox access

### Requirement: Runtime configuration materialization is idempotent
The configurator SHALL resolve and mutate the same AppConfig and extensions-config targets the Gateway will use under the loaded launch environment, merge the `deep-research-control` tool group and `deep_research` reflected tool with comment/order/style-preserving YAML operations, and merge the public-skill enabled state with structured JSON operations that preserve unknown data and key order. It SHALL require the effective skills root to be its canonical repo `skills/` mount and SHALL fail rather than writing an inert fallback or alternate skill copy. It SHALL retain the JSON file's detected indentation/newline convention when representable and converge to a byte-stable result after the first write. It SHALL support check, dry-run, permission-restricted backup, atomic write, redacted diff, and hash-guarded rollback modes; repeated execution SHALL produce no semantic drift or further textual drift.

#### Scenario: Effective configuration targets are authoritative
- **WHEN** the launch environment selects explicit config/extensions paths or creates a root/backend shadow ambiguity
- **THEN** configure writes only the unambiguous effective targets or fails before every write, and doctor never reports a fallback file as active

#### Scenario: Noncanonical skills root is refused
- **WHEN** effective `skills.path` or `DEER_FLOW_SKILLS_PATH` resolves outside the canonical repo skills root used by the local/Docker assembly
- **THEN** configure performs no write and reports runtime not ready instead of materializing a public skill that the supported mount contract does not expose

#### Scenario: Entry drift is not a hidden runtime gate
- **WHEN** the reflected tool/group configuration is valid but the public skill or dedicated Agent is missing or cannot be inspected offline
- **THEN** check reports entry not-ready or unknown without reporting runtime configuration invalid, and the launcher defers the final decision to doctor's independent readiness axes

#### Scenario: Fresh and repeated configuration converge
- **WHEN** configure runs twice against fresh valid config fixtures
- **THEN** the first run creates the required semantic entries and the second run reports no changes

#### Scenario: Same-name foreign ownership is refused
- **WHEN** an existing tool or group uses a project-owned name with a different reflection path or incompatible definition
- **THEN** configure performs no write and reports the exact ownership conflict without exposing secret values

#### Scenario: Rollback preserves later operator edits
- **WHEN** a target changed after the configurator recorded its post-change hash
- **THEN** rollback removes only byte-identical project-owned entries/files or stops on ambiguity and never restores the whole stale backup over newer edits

#### Scenario: Detected online mutation is refused
- **WHEN** configure or rollback would mutate runtime files while an explicit/known local Gateway endpoint is reachable or a project-owned local/Docker Gateway process is detected
- **THEN** it performs no write and reports the offline operational precondition, while check and dry-run remain available

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

### Requirement: Diagnostics expose readiness without secrets

Doctor SHALL separately report its fingerprint inspection mode, boolean
`runtime_ready`, `entry_ready.status = ready | not_ready | unknown`, and
`durability = same_process | restart_durable | unavailable` with effective provider
kind. It SHALL also report
`work_unit_storage = ready | not_ready | unknown`. Prelaunch-candidate mode SHALL validate the launcher's freshly computed candidate
against the effective launch config without claiming to inspect a running process.
In-process mode SHALL compare live AppConfig with the fingerprint inherited by that
process; missing mode or expected fingerprint SHALL NOT be replaced by silent
recomputation.

Runtime readiness SHALL cover package origin/version, reflection resolution, config
ownership, source/mount paths, sandbox separation, the applicable fingerprint match,
supported worker count, provider compatibility, and the work-unit store's
shared-workspace transaction prerequisite. The latter SHALL be ready only when the
selected sandbox exposes the same physical thread workspace as the trusted host path and
the filesystem supports bounded POSIX locking, same-directory atomic replace, and
durability sync. Remote, non-mounted, custom, or otherwise unverified providers SHALL
make runtime readiness fail closed for work-unit execution; doctor SHALL NOT claim that
a host-only ledger can validate files written in a separate sandbox filesystem.

Doctor and runtime SHALL import one pure sandbox-mode classifier with these exact
outcomes: canonical `LocalSandboxProvider` paths are `ready` candidates;
`AioSandboxProvider` without `provisioner_url` is a `ready` candidate; AIO with a
non-empty `provisioner_url`, `E2BSandboxProvider`, and `BoxliteProvider` are
`not_ready`; every unrecognized/custom provider is `unknown`. Stable reason codes SHALL
distinguish `local_thread_mount`, `aio_local_thread_mount`,
`aio_provisioner_unmounted`, `e2b_unmounted`, `boxlite_unmounted`, and
`provider_unrecognized`. `runtime_ready` SHALL be false unless
`work_unit_storage == ready`, including the `unknown` case.

Runtime/store error reasons SHALL be the closed redacted set
`aio_provisioner_unmounted | e2b_unmounted | boxlite_unmounted |
provider_unrecognized | thread_mount_unavailable | workspace_alias_mismatch |
posix_primitives_unavailable | probe_cleanup_failed | ledger_corrupt |
accepted_artifact_diverged | lock_timeout`. `lock_timeout` SHALL accompany only
`work_unit_store_busy`; every other error reason SHALL accompany only
`work_unit_storage_unavailable`. The two ready-mode codes remain success checks, not
error reasons.

Lifecycle denial output SHALL expose the applicable closed value only as
`infrastructure_reason`; no doctor issue text, host path, provider URL, probe token, or
exception detail SHALL enter the wire result.

The classifier SHALL recognize both package-export and checked-in implementation class
paths for those four built-in providers. It SHALL NOT infer readiness by suffix or class
name; an otherwise similar path is custom/unrecognized and therefore `unknown`.

For a ready candidate, prelaunch doctor SHALL probe required locking, same-directory
replace, file fsync, and directory fsync primitives in the effective host thread-data
filesystem without disclosing its path. Success SHALL require real operations: two-open-
description nonblocking `fcntl.flock` acquisition/contended denial, descriptor-relative
exclusive no-follow regular-file creation, file fsync, same-directory
`os.replace(..., src_dir_fd=..., dst_dir_fd=...)`, result reopen/verification, directory
fsync, and cleanup. Capability introspection such as membership in `os.supports_dir_fd`
SHALL NOT count as a successful probe.

Runtime store construction SHALL additionally resolve the installed provider singleton,
require `uses_thread_data_mounts is True`, require
`provider.get(parent_sandbox.id) is parent_sandbox`, round-trip independently generated
bounded random base64url ASCII tokens in both host-write/sandbox-read and sandbox-write/
host-read directions, and repeat the filesystem primitive probe. Synchronous parent
sandbox `read_file`/`write_file` calls SHALL run through `asyncio.to_thread`. Host-created
probe files SHALL use exclusive mode `0600`; because the public sandbox write API has no
mode parameter, the sandbox-created alias file SHALL be opened no-follow from the trusted
host directory, verified regular, narrowed with `fchmod(0600)`, then read and removed.
Cleanup SHALL use trusted host descriptor-relative unlink/rmdir in `finally`. Because an
alias-mismatch file may exist only inside the sandbox and the public interface has no
delete method, cleanup SHALL also run a bounded, shell-quoted
`Sandbox.execute_command` for only the trusted derived virtual probe path and probe-only
empty directories through `asyncio.to_thread`, then verify absence. Caller/model text
SHALL never enter that command. Any cleanup residue or error SHALL return
`probe_cleanup_failed`. Probe files SHALL be randomized and never treated as control,
evidence, or research artifacts. Any other runtime failure SHALL return
`work_unit_storage_unavailable` before research artifact, ledger, accepted-ref, or
checkpoint mutation. Sandbox config already belongs to the startup fingerprint; this
change SHALL add no startup-only config field.

Runtime probes SHALL use hidden `.work-unit-probe-<32-lowercase-hex>` for aliasing and the
exact same-token filesystem family `.work-unit-fsprobe-<32-lowercase-hex>.lock`,
`.work-unit-fsprobe-<32-lowercase-hex>.src`, and
`.work-unit-fsprobe-<32-lowercase-hex>.dst` inside the current research `diagnostics/`
subtree. Prelaunch doctor, which has no research id or parent sandbox, SHALL use the exact
same-token host-side family
`.deep-research-work-unit-fsprobe-<32-lowercase-hex>.lock`,
`.deep-research-work-unit-fsprobe-<32-lowercase-hex>.src`, and
`.deep-research-work-unit-fsprobe-<32-lowercase-hex>.dst` directly under the existing
gateway-visible `get_paths().base_dir`, the parent filesystem for all thread data. It
SHALL NOT invent a user/thread id or use the Docker-daemon-only `host_base_dir`. No probe
SHALL be returned as a ref; files and any probe-only empty directories SHALL be removed
on success, denial, exception, and cancellation.

Entry readiness SHALL cover the public skill and dedicated Agent without disabling the
global tool: a known defect SHALL produce `not_ready`; `unknown` SHALL apply only when no
known defect exists and the authenticated Agent cannot be inspected offline; `ready`
SHALL require all entry checks to pass. Durability SHALL follow legacy
`checkpointer`-over-`database` precedence. Doctor's blocking exit status SHALL depend
only on runtime readiness. Doctor SHALL report next-build/restart requirements and
redact credentials, connection secrets, host user identifiers, full startup
inputs/fingerprints, full internal checkpoint keys, and resolved host workspace paths.

#### Scenario: Ready environment is classified accurately
- **WHEN** doctor inspects a correctly assembled SQLite environment whose local or locally mounted sandbox shares the trusted thread workspace
- **THEN** it reports runtime ready, entry readiness independently, SQLite restart recovery expected, work-unit storage ready, and no source mount inside the sandbox

#### Scenario: Prelaunch readiness is not confused with a running process
- **WHEN** the wrapper supplies a freshly computed SQLite candidate to prelaunch doctor before starting Gateway
- **THEN** doctor labels the result as prelaunch-candidate, verifies it against the same effective config, and does not claim that an existing process inherited that fingerprint

#### Scenario: Missing dedicated Agent is an entry warning
- **WHEN** package, reflected tool, paths, provider, and work-unit storage prerequisites are valid but the dedicated Agent is absent
- **THEN** doctor reports runtime ready and entry not ready without claiming the global control tool is unavailable

#### Scenario: Authenticated Agent cannot be guessed offline
- **WHEN** doctor runs without a current-user authenticated API context in an authenticated deployment
- **THEN** it reports the dedicated Agent check as unknown or warning rather than inspecting an arbitrary user directory

#### Scenario: Effective provider precedence is consistent
- **WHEN** legacy `checkpointer` and unified `database` select different backends
- **THEN** doctor reports the legacy checkpointer backend and the same durability class GraphHost will use

#### Scenario: Invalid persistent provider is unavailable
- **WHEN** the effective provider has a missing Postgres URL or an SQLite memory-mode connection
- **THEN** doctor reports unavailable or same-process durability as applicable and does not report restart recovery expected

#### Scenario: Unsupported worker input is not ready
- **WHEN** `GATEWAY_WORKERS` does not normalize under `${GATEWAY_WORKERS:-1}` to integer one, including malformed, zero, negative, or greater values
- **THEN** doctor reports runtime not ready and the launcher does not claim process-local action serialization is sufficient

#### Scenario: Sandbox workspace is not transaction-capable
- **WHEN** sandbox selection uses a remote/non-mounted provider or a filesystem whose workspace identity and POSIX transaction primitives cannot be verified
- **THEN** doctor reports runtime not ready with a redacted work-unit-storage issue and runtime returns `work_unit_storage_unavailable` before work-unit artifact, ledger, or checkpoint mutation

#### Scenario: Known provider modes classify identically offline and at runtime
- **WHEN** doctor and runtime inspect LocalSandbox, local-container AIO, provisioner-backed AIO, E2B, BoxLite, and an unrecognized custom provider
- **THEN** both use the same stable mode/reason classifier, local mounted modes are only ready after their applicable probes pass, known unmounted modes are not ready, custom mode is unknown but runtime-not-ready, and no host path is returned

#### Scenario: Runtime provider contradicts its ready config candidate
- **WHEN** offline config classifies a local mode as a ready candidate but the initialized provider does not expose thread-data mounts or the host/sandbox alias probe fails
- **THEN** runtime refuses store construction with `work_unit_storage_unavailable`, performs no research or checkpoint mutation, and does not trust the offline classification alone

#### Scenario: Capability introspection disagrees with an executable primitive
- **WHEN** a platform's feature sets omit descriptor-relative replace support but the actual `os.replace` call would work, or advertise a primitive whose real operation fails
- **THEN** readiness is determined only by the bounded executable probe and never by feature-set membership alone

#### Scenario: Secret-bearing failure is redacted
- **WHEN** a failing fixture contains a database URL, API key, or resolved host workspace path
- **THEN** doctor reports the failing field/provider/capability without printing the secret or host path

### Requirement: Deployment loads the downstream package from the canonical Harness root

Local, production, and Docker launch paths SHALL load
`deerflow_deep_research` from `deep_research_harness/src/`. Docker mounts, image build
inputs, `PYTHONPATH`, configuration materialization, public-skill source, and readiness
checks SHALL use the canonical Harness root and SHALL not retain an old-root fallback.
They SHALL preserve the distribution/import/public-tool identities and SHALL not require
changes under upstream `backend/` or `frontend/`. (`DEC-006`)

#### Scenario: Docker mount uses the new root without a second source path
- **WHEN** deployment configuration is rendered for a supported environment
- **THEN** it mounts only `deep_research_harness/src` as the downstream source and resolves the unchanged Python package without a `deerflow_research` fallback
