# Deep Research Local Operations

This reference covers local profiles, demos, retained observations, and the terminal
workbench. It describes operator routes only. The Deep Research Harness and a selected
Run Bundle's local State determine lifecycle truth and legal controls; a CLI, TUI,
workbench, diagnostic, or retained observation does not.

## Command Route

Run commands from `deep_research_harness/`. Use the root README's
[quick start](../README.md#quick-start) first if dependencies are not installed.

| Goal | Command |
| --- | --- |
| Format and lint local code | `make format`, `make lint` |
| Prepare and inspect a profile | `make profile-setup`, `make profiles` |
| Initialize, check, or start the demo profile | `make profile-init PROFILE=demo`, `make profile-check PROFILE=demo`, `make profile-dev PROFILE=demo` |
| Run the interactive zero-credential demo | `make demo` |
| Run the deterministic non-interactive demo | `make demo-scripted` |
| Start the local Gateway profile, then run the real CLI | `make profile-dev PROFILE=demo`, then `make demo-real PROFILE=demo` |
| Start the Textual Gateway visualizer | `make demo-tui PROFILE=demo` |
| Run explicit direct local graph smoke | `make demo-real-embedded-smoke`, `make demo-real-scripted`, or `make demo-tui-embedded-smoke` |
| Start the fixture visualizer | `make demo-tui-fixture` |
| Run the fixture graph without the TUI | `make demo-fixture-graph` |
| Check local entry prerequisites | `make profile-preflight` |
| Open the standalone local workbench | `make session-workbench` |
| Inspect one retained observation | `make demo-sessions DEMO_ARGS="inspect <bundle-id>"` |
| Run the operator-only scripted-real workflow debug | `make debug-scripted-real-workflow` |
| Create/run/bind/inspect a soft bundle root | `make soft-bundle DEMO_ARGS="create"` |
| Prove a delivery lane and record a receipt | `make proof LANE=verify` |
| Report stale receipts and the rerun command | `make proof-status` |
| Require every registered guard to go red | `make mutation-check` |

The demo targets ignore a foreign active `VIRTUAL_ENV` and use the locked project
environment. A retained observation command is read-only: it does not discover a
Bundle, validate a Handle, or provide a lifecycle action.

Run `make install` before any local demo, retained-observation, workbench, or prepared
all-real launcher entry. It prepares the complete local optional dependency set; these
ordinary entries never synchronize it themselves. The profile-launched Gateway observer
route additionally needs `make profile-setup` — it installs the sibling framework
environment that `make install` does not touch — and `make profile-init PROFILE=<name>`
on a fresh clone (`profiles/` is not committed). Run `make lock-check` separately
when checking that dependency metadata agrees with the tracked lockfile.

`make debug-scripted-real-workflow` is an operator-only local debug command, not a
product command or a `make verify` substitute. It runs the complete production
control path (real node adapters, prompts, parsers, work-unit ledger, gates,
routes, and persistence) against a fixed narrow scripted external world: a
template scripted chat model and two scripted web tools. It reads no `.env`, makes
no network call, requires no credentials, and completes in well under ten seconds.
Its output labels the run `composition=all_real_adapters` and
`authenticity=scripted_real_workflow`, reports per-wave action counters, the
Bundle id, and the Event Journal entry, and states the boundary: it proves
production control-path integration for fixed legal inputs only — not live model
comprehension, web availability, coverage breadth, or the targeted/rerun/
provider-recovery branches. The baseline fails loudly on any missing or surplus
scripted model or tool call, or if the run enters `targeted_evidence` or `rerun`.

`make soft-bundle` is an operator-only CLI over the same local demo/session entry
points. It creates a stateless `soft_bundle_root`, runs mode 001, binds a real
`bundle_id`, and exposes `status`, `path`, `inspect`, `phases`, and `list`. It
prints only repository-relative local record locations and never accepts a path as a
lifecycle selector. It is not a product command and does not change the `deep_research`
tool contract.

## Run Bundle Lifecycle

The Harness allocates a fresh opaque `bundle_id` for an admitted `start`. That id names
the Run Bundle and the public target while the Bundle is available. A trusted
conversation has at most one active Bundle, including a Bundle awaiting user input;
any number of available ended Bundles may remain for inspection. The Bundle-local
Research State, evidence, and content are the only durable lifecycle record.

| Action | Meaning |
| --- | --- |
| `start` | Publish a fresh independent Run Bundle when no Bundle is active in the trusted scope. |
| `resume` | Submit only the correlated response to the current pending interaction. The response is supplied in the current user message, not tool arguments. |
| `refine` | Submit one bounded nonblank direction for an available Bundle, or explicitly continue its already pending terminal direction by omitting text and naming that Bundle. It does not consume a pending response. |
| `status` | Read the selected Bundle's typed lifecycle result. |
| `cancel` | Request a durable stop through the selected Bundle lifecycle. |

An ended Bundle can be refined only by naming its explicit `bundle_id`, and only when
no different Bundle is active in the same trusted scope. A Bundle holds at most one
pending direction. A nonblank direction waits for the completed terminal boundary of the
current round; it never replaces a correlated response or a writer in progress. A
textless continuation is valid only for an available terminal Bundle that already holds
that stored pending direction. It cannot submit or recover text, update a profile, or
restart automatically after `STOPPED`, `CANCELLED`, or `BLOCKED`.

Do not use `resume` as a generic refinement action, and do not treat Accepted Profile
Notes from Research Confirmation as a post-confirmation notes inbox. Follow the returned
legal next action: a pending human subject requires `resume`, an active pending direction
without one requires `status`, a capacity-legal terminal pending direction requires the
explicit selected continuation, and a capacity-legal terminal Bundle without a pending
direction accepts a new text-bearing direction. An exhausted terminal Bundle requires a
fresh `start`, even when its pending direction remains inspectable. If a Bundle is
missing, unreadable, or invalid, it is unavailable permanently for lifecycle purposes.
No session, observation, cache, or external state can restore it.

Known IM transports and non-interactive contexts refuse `start` and `resume`. Report
the returned typed outcome rather than assuming another action is legal.

## Retired Runtime Inputs

The trusted runtime accepts scripted lifecycle input only as
`non_interactive=true` with the exact closed `non_interactive_policy` containing
`auto_profile: true` and `auto_proceed: true`. The retired
`disable_clarification=true` marker is not an interactive fallback: `start`,
`resume`, and `refine` return `interactive_required` before Bundle publication,
sandbox/graph selection, or policy checkpoint writing. Caller arguments cannot
create this trusted context.

For generic infrastructure probes, `database` is the sole local provider setting.
A non-null legacy `checkpointer` section is refused before the provider opens; the
GraphHost and diagnostics report the redacted
`legacy_checkpointer_unsupported` outcome. Remove the legacy section and configure
the required `database` backend. This reference does not establish support for a
host, deployment, AppConfig version, or provider outside the source-controlled
downstream inventory.

Endpoint observation uses only the exact selected model configuration's safe,
normalized `base_url`. The retired `openai_api_base` and `api_base` fields, whether
alone or alongside `base_url`, produce no endpoint observation and do not alter model
selection, provider behavior, retries, routes, or lifecycle control. Use selected
`base_url` when a safe observation is required.

There is no in-process compatibility mode for these retired inputs. A material
deployment incident requires a separately approved hotfix or revert of the complete
affected local reader, followed by its deterministic tests. Do not rewrite input,
select a legacy provider, add an alias-specific switch, or treat a partial consumer
restore as recovery.

## Local Configuration Profiles

The upstream DeerFlow repository at the root remains unchanged. Local configuration
data lives in the downstream-owned top-level [`profiles/`](../../profiles/README.md)
directory; command tooling lives in this project. Run `make profile-setup` once, then
initialize, check, and start a scenario with `make profile-init PROFILE=demo`,
`make profile-check PROFILE=demo`, and `make profile-dev PROFILE=demo`.

Root `.env` remains the shared source for literal API keys and other secrets; profile
commands select the configuration and DeerFlow home themselves. A profile uses
contained SQLite state by default, or can deliberately select ephemeral
`database.backend: memory`. Changing startup-only profile settings requires a restart.
Docker, sandbox mounts, shared launcher logs, ports, and compatibility directories are
not isolated by a profile.

## Fixture And Real Demos

`make demo`, `make demo-scripted`, and `make demo-tui-fixture` are zero-credential fixture-graph
routes: no Gateway, config, model credentials, or network are needed.

These routes keep their Run Bundles in the harness-local `.deep-research-demo-runs/` tree.
An isolated run can point somewhere else with `DEERFLOW_DEMO_BUNDLE_ROOT=<path>` (blank
falls back to the default): tests and throwaway probes use it so they never read or write
the ambient workspace, where a leftover non-terminal Bundle would otherwise change what
the operator report and the demo CLI see (BUG-072). Their Make targets
add `src_fixtures` only to the selected child process. The production package and reflected
runtime neither import nor discover that package. These routes execute the fixed fixture recipe;
they are deterministic composition proof, not product research results.

`make demo-real PROFILE=<name>` and `make demo-tui PROFILE=<name>` are the default
real observer routes. Start the selected profile Gateway first with
`make profile-dev PROFILE=<name>`. The observer profile must pass its JSON logging,
durable SQLite history, public entry, and direct local Gateway health checks before it
creates a thread. Model and web credentials belong to that launched Gateway profile;
the CLI and TUI processes do not read local `DEERFLOW_DEMO_MODEL` or `TAVILY_API_KEY`
values themselves — the launched Gateway still needs those credentials, from the root
`.env`.
They use only public Gateway turns and returned typed lifecycle results, so assistant
text, heartbeat, gaps, and stream end do not create a result or a second controller.

Observer JSON logging is a **manual prerequisite that `profile-init` does not write**:
profile configuration is copied from the root `config.yaml`, whose shipped template has
`logging.enhance.enabled: false` / `format: text`, while the observer gate requires
`enabled: true` / `format: json`. Until that profile value is corrected and the Gateway
restarted, the observer route is refused with a generic "the selected local Gateway
profile is not ready" — and `make profile-check PROFILE=<name>` does **not** check
logging, so a green check does not cover this gate. Fix the profile before debugging
anything else.

For example:

```bash
make profile-init PROFILE=demo      # fresh clone: profiles/ is not committed
# edit profiles/demo/config.yaml: logging.enhance -> enabled: true, format: json
make profile-dev PROFILE=demo       # terminal A: launch the Gateway (foreground)
make demo-real PROFILE=demo DEMO_ARGS='--question "Compare battery storage costs"'
```

The Gateway TUI does not expose a local cancel button. A local Ctrl-C or window close
stops only the presentation process and makes no Gateway cancellation claim. Enter an
explicit ordinary-language user turn when the configured Agent should consider a
cancellation request.

`make demo-real-embedded-smoke`, `make demo-real-scripted`, and
`make demo-tui-embedded-smoke` retain the direct local all-real graph only for
explicit smoke work. They retain local model/Tavily preflight and do not claim Gateway
history, Console data, trace correlation, SSE liveness, or custom-event forwarding.

## Gateway Observer Operations

The default real CLI/TUI routes observe the profile-launched Gateway at
`http://127.0.0.1:8001` through the public thread-create and
`POST /api/threads/{thread_id}/runs/stream` interfaces. The observer renders only
predecessor-approved progress fields (`phase`, `operation`, `outcome`, and a bounded
`bundle_id` reference) from validated `deep_research.progress.v1` candidates; it never
displays raw SSE payloads, tool arguments, or non-Deep-Research tool results.

Process logs: the profile launcher tees the launched Gateway process's existing
`stderr` bytes to an owner-only rotating family below
`deep_research_harness/.deep-research-demo-runs/logs/`. Each launch prints its absolute
base path before starting the Gateway, for example:

```bash
make profile-dev PROFILE=demo
# Gateway stderr capture: .../deep_research_harness/.deep-research-demo-runs/logs/gateway-<pid>-<ts>-<nonce>.stderr.log
tail -f deep_research_harness/.deep-research-demo-runs/logs/gateway-*.stderr.log
```

The tee preserves normal `stderr` and DeerFlow's own logging; capture failure disables
only the file side and never changes the Gateway or any Run outcome. Log files are
`0600`/`0700`, bounded per process and retained for a bounded number of inactive
launches; an active process file is never deleted.

Correlation route for an observed run:

1. Process `stderr` lines carry DeerFlow's `trace_id`; the public stream response header
   `X-Trace-Id` is the same trace correlation for the observed turn.
2. SSE `metadata` carries the public `run_id`; the observer retains it as the safe
   process-local run correlation.
3. A validated `deep_research.progress.v1` candidate on the public `custom` channel
   carries the same `outer_run_id` plus the Bundle `bundle_id`.
4. Bundle inspection (e.g. `make demo-sessions DEMO_ARGS="inspect <bundle-id>"`) reads
   the returned Bundle's local Event Journal.

These surfaces have distinct roles and none is a second authority: `stderr` is
operational capture; SSE `custom` is a best-effort live projection; Gateway history
(public run stores/Console) is the durable outer-run record; and Bundle inspection is
the returned Bundle's own evidence. Only a validated returned typed Deep Research
result produces lifecycle presentation, and `end`, heartbeat, gap, assistant prose, or
elapsed time never manufacture a lifecycle outcome.

## Embedded Smoke Calibration

Choose one registered, credential-backed profile for each bounded calibration run:

```bash
PROFILE=<profile> make demo-real-scripted
make demo-sessions DEMO_ARGS="inspect <bundle-id>"
```

The explicitly labelled embedded-smoke scripted command keeps its fixed question and
creates a fresh Run Bundle in the local smoke runtime.
Use the printed Bundle id only with the read-only inspection command, then compare the
redacted profile identity/revision, phase, failure category, budget-stop reason, and
validation codes. Repeat manually with another explicit profile when a comparison is
needed; do not automate a model matrix from this procedure.

This evidence does not qualify a model and does not select or change a default model.
It does not change prompts, budgets, retries, or lifecycle controls, and a retained
observation cannot rerun or alter the Bundle that produced it.

## Retained Observations And Diagnostics

The project may retain a bounded diagnostic observation keyed by a `bundle_id` under
its local reports area. The observation can outlive a Run Bundle, but it is not a
Bundle locator or recovery record. It can show bounded diagnostic facts only; it cannot
authorize `status`, `resume`, `cancel`, `refine`, State reconstruction, or Bundle
recreation.

Use `make demo-sessions DEMO_ARGS="inspect <bundle-id>"` only to inspect such an observation.
There is still no observation-backed list, open, discovery, or lifecycle-control command;
a missing or corrupt observation is reported as unavailable for inspection and does not
alter the underlying Bundle result. The separate operator-only workspace pair
`make demo-workspace-report` (read-only inventory) and `make demo-clean` (guarded
cleanup: dry-run by default, `CONFIRM=1` deletes only terminal bundles, never
non-terminal ones; `DEMO_ARGS="--logs"` includes the logs subtree) is a view over local
files — never a lifecycle control surface.

When a returned lifecycle result says a Bundle is unavailable, start a distinct run if
its legal next action allows it. Do not try to migrate or copy local diagnostics into a
replacement Bundle.

## Local Workbench

`make session-workbench` opens a standalone local terminal projection for the configured
fixture demo profile. It consumes shared typed Bundle results and displays bounded
timeline and catalog observations. It is not a Gateway, Web UI, production terminal
workbench, generic filesystem explorer, or recovery client.

The workbench does not accept a filesystem path, profile, provider, principal, or
external persistence key as lifecycle authority. Its visible controls are enabled only
when the returned Bundle result makes them legal. Timeline, catalog, and retained
diagnostic data remain observational and cannot infer a lifecycle transition.

The project-owned live launch wrapper, in-container prelaunch doctor gate, and Postgres
durability profile are deferred to follow-up deployment work. See the suspended plans
under `_backlog/_done/_suspended_plans/` for historical context.
