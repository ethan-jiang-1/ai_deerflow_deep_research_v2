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
| Run an interactive all-real demo | `make demo-real` |
| Run a non-interactive all-real demo | `make demo-real-scripted` |
| Start the Textual real or fixture visualizer | `make demo-tui`, `make demo-tui-fake` |
| Open the standalone local workbench | `make session-workbench` |
| Inspect one retained observation | `make demo-sessions DEMO_ARGS='<bundle_id>'` |

The demo targets ignore a foreign active `VIRTUAL_ENV` and use the locked project
environment. A retained observation command is read-only: it does not discover a
Bundle, validate a Handle, or provide a lifecycle action.

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

`make demo`, `make demo-scripted`, and `make demo-tui-fake` are zero-credential fixture
routes: no Gateway, config, model credentials, or network are needed. Their Make targets
add `src_fake` only to the selected child process. The production package and reflected
runtime neither import nor discover that package. These routes demonstrate lifecycle
presentation; they are not research results.

`make demo-real`, `make demo-real-scripted`, and `make demo-tui` require one of
`DEEPSEEK_API_KEY`, `ANTHROPIC_API_KEY`, or `OPENAI_API_KEY`, plus `TAVILY_API_KEY`.
The real commands load `.env` when present and accept explicitly exported credentials.
They use the shared typed Bundle lifecycle result, so their displays do not derive an
id, infer lifecycle state from output files, or create a second controller.

For example:

```bash
make demo-real DEMO_ARGS='--question "Compare battery storage costs"'
```

The CLI and TUI show progress only after a returned typed update. A local Ctrl-C stops
the presentation process; it is not a claim that the Bundle was cancelled. Use a
returned legal `cancel` action when the run must be stopped.

## Retained Observations And Diagnostics

The project may retain a bounded diagnostic observation keyed by a `bundle_id` under
its local reports area. The observation can outlive a Run Bundle, but it is not a
Bundle locator or recovery record. It can show bounded diagnostic facts only; it cannot
authorize `status`, `resume`, `cancel`, `refine`, State reconstruction, or Bundle
recreation.

Use `make demo-sessions DEMO_ARGS='<bundle_id>'` only to inspect such an observation.
There is no observation-backed list, open, discovery, cleanup, or lifecycle-control
command. A missing or corrupt observation is reported as unavailable for inspection and
does not alter the underlying Bundle result.

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
