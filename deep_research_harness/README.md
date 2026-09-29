# DeerFlow Deep Research Harness

This independent Python project is the downstream **Deep Research Harness** for DeerFlow
2.1. It is a *runtime harness*, not a single question-to-report pipeline: it is the stable
execution and control environment that creates, drives, and disposes of research runs.

The Harness owns the lifecycle boundary for one continuing research run and gives each run
an independently deletable **Run Bundle** — the durable record of that run's Research
State, evidence, content, and Run Event Journal. The Harness itself owns no durable run
state: delete a Bundle and the Harness keeps working, while that run becomes permanently
unavailable and is never recreated. Its controller is a nested Python `StateGraph`, and
bounded agent loops execute inside graph nodes as two-part programs: a Node Cognitive
Control Program (what a model may think and propose) behind a Deterministic Control
Boundary (what code admits and routes). DeerFlow remains the host runtime and does not
import this package; the reflected `deep_research` tool and the public controller skill
are how DeerFlow reaches the Harness.

Three properties make this a harness rather than a plain application:

- **Explicit composition.** Every graph receives an explicit recipe: the public host is
  fixed to `all_real`, an explicitly composed fixture demo or test recipe reports
  `fixture`, and an explicitly composed test mix reports `mixed`. These labels identify
  implementation composition, not provider success, evidence acceptance, or report
  quality. Production node packages expose real factories only; deterministic fixture
  adapters live in the separate non-production
  `src_fixtures/deerflow_deep_research_fixtures/` package, excluded from the production wheel
  and reflected runtime. The same graph can therefore be exercised with zero credentials.
- **Models propose, code disposes.** Candidate work, evidence, and routes are admitted
  only by deterministic owners: validators, the evidence ledger, gates, and the graph.
- **Disposable runs, inspectable bundles.** Run Discovery reads Bundle directories only;
  no registry, cache, or diagnostic can establish, authorize, or recover a run.

See [runtime architecture](docs/runtime-architecture.md) and the
[run lifecycle walkthrough](docs/run-lifecycle-walkthrough.md) for authority boundaries
and the end-to-end vocabulary.

## Entry Surfaces

> Operational view of the surfaces. The vocabulary-side classification is
> **Entry Interfaces** in [`CONTEXT.md`](CONTEXT.md#entry-interfaces); keep the
> two name-mapped in the same PR that changes either.

| Surface | Primary reader/user | Purpose | Actual composition | Explicit non-goal |
| --- | --- | --- | --- | --- |
| Dedicated Agent + reflected `deep_research` tool | Primary User | Current product route for a research question | The reflected public tool is fixed to all real; see [runtime architecture](docs/runtime-architecture.md) | Not an operator CLI or a fixture/demo route selector |
| Standalone operator CLI | Contributor/operator | Local Gateway observation and explicit embedded smoke; see [local operations](docs/local-operations.md) for exact commands | `make demo-real PROFILE=<name>` uses the selected local public Gateway; embedded smoke is a separately labelled direct all-real graph | Not a versioned product CLI |
| Demo TUI visualizer | Contributor/operator | Visualize shared lifecycle results through Gateway, embedded smoke, auto-run, or fixture-graph mode | `make demo-tui PROFILE=<name>` uses the public Gateway; `make demo-tui-real-auto` is the 010 zero-operator embedded run; `make demo-tui-fixture` is a fixed fixture graph | Not a current Primary User TUI |
| Fixture-graph demonstrations | Contributor/maintainer | Zero-credential deterministic fixture-graph proof; see [local operations](docs/local-operations.md) and [testing and evaluation](docs/testing-and-evaluation.md) | `make demo` (interactive: reads stdin unless `--scripted`), `make demo-scripted`, and `make demo-tui-fixture` execute a fixed fixture recipe and graph executor | Not a product result or a mode selector |
| Operator soft-bundle CLI | Contributor/operator | Zero-credential 001–004 ladder plus retained-bundle inspection; ladder authority in [COMMANDS.md](COMMANDS.md) | `make soft-bundle DEMO_ARGS="create …"` then `run`/`status`/`verify`; 001–002 zero-credential, 003–004 need credentials and network | Not a product lifecycle surface |
| Configured-fixture local workbench | Local operator | Inspect bounded Run Bundle projections; see [local operations](docs/local-operations.md) | `make session-workbench` uses the configured fixture demo profile | Not a generic product UI or recovery client |
| Debugger workbench | Contributor/operator | Step/continue the real graph at node boundaries, inspect captured node context and bounded workspace, attach/replay exact bundles | `run/tui-workflow-debugger.sh` (or `make tui-debugger`); `--fixture` zero-credential, `--attach <id>`/`--replay <id>` lifecycle-validated | Local operator debugger; not a current Primary User TUI |

## Reading Map

This README is a human/operator entry page, not default context for an ordinary code
change. Coding agents begin with [`AGENTS.md`](AGENTS.md), then read only the owning
specification, implementation, and test seam selected by its focus gate.

| Need | Start here |
| --- | --- |
| Choose one human-facing reference | [Documentation index](docs/README.md) |
| Understand Harness, Run Bundle, graph, evidence, sandbox, or public-control boundaries | [Runtime architecture](docs/runtime-architecture.md) |
| Run profiles, demos, diagnostics, retained observations, workflow outcomes, or the workbench | [Local operations](docs/local-operations.md) |
| Run the local demo ladder end to end (001–004 / 010 / 020 / 030 / 031) | [Local runbooks](docs/runbooks/README.md) |
| Select and interpret deterministic, workflow-outcome, live, or release testing | [Testing and evaluation](docs/testing-and-evaluation.md) |
| Run or interpret a manually selected Cognitive Evaluation case | [Cognitive Evaluation Suite](docs/cognitive-evaluation-suite.md) |
| Inspect the generated graph topology | [Logical topology](docs/deep-research-topology.md) |
| One-page command cheat sheet for the demo ladder and diagnostics | [COMMANDS](COMMANDS.md) |
| Make an application code change | [`AGENTS.md`](AGENTS.md), then the owning source and narrowest test |
| Find application architecture and layer rules | [`docs/runtime-architecture.md`](docs/runtime-architecture.md) |

The focused documents preserve the detailed operational and evidence reference that
previously lived here. Open only the one needed for the current question.

Real-demo workflow outcomes, provider recovery, diagnostic locations, and fresh-start
semantics are kept in [Local operations](docs/local-operations.md), not in this entry
page.

## Quick Start

Requirements: Python 3.12 or newer, `uv`, and the sibling DeerFlow harness at
`../deerflow/backend/packages/harness`.

From the repository root, run these commands one line at a time:

```bash
cd deep_research_harness
make install
make lock-check
UV_OFFLINE=1 make verify
```

If the current directory is already `deep_research_harness/`, omit `cd deep_research_harness`. The project is
independently locked and resolves `deerflow-harness` from the sibling checkout through
an editable uv source. The `operations` extra contains the round-trip YAML dependency
used by project configuration scripts; runtime code does not acquire it implicitly.

`make install` is the one explicit local environment setup command: it prepares the
operations, demo TUI, and real-demo extras. Demo, retained-observation, workbench, and
prepared launcher entries do not synchronize dependencies; when that prepared
environment is absent or incomplete, run `make install`. The profile-launched Gateway
observer route (`make demo-real PROFILE=<name>`, `make demo-tui PROFILE=<name>`)
additionally needs `make profile-setup` and, on a fresh clone, `make profile-init
PROFILE=<name>`. Use `make lock-check`
separately to verify that dependency metadata matches `uv.lock`.

## Running Tests From The CLI

`make` owns the supported test selections and uses `uv` to run them in the locked
project environment. Run the deterministic project gate with:

```bash
cd deep_research_harness
UV_OFFLINE=1 make verify
```

For a focused CLI run, invoke the pytest module explicitly rather than relying on a
shell-installed `pytest` command. This example checks the public lifecycle guidance
without synchronizing or changing the environment:

```bash
cd deep_research_harness
UV_OFFLINE=1 uv run --no-sync --extra operations python -m pytest \
  tests/contract/test_public_skill.py -q
```

## Direction Controls

Refinement direction submission/continuation, the `resume` correlation contract, and
the provisioned dedicated Agent route are lifecycle contracts. The authoritative
statement lives in [Runtime architecture](docs/runtime-architecture.md) (see
**Public Controls** and **Ordinary Controller Loading**, which name the owning
capability specification `deep-research-harness-run-bundles`). This page intentionally
does not restate those rules.

## Frequent Commands

Only the three most common entry points live here; the authoritative command
inventory and the full demo ladder are [`COMMANDS.md`](COMMANDS.md) and the
[`Makefile`](Makefile) — keep all three in step in the same PR.

| Goal | Command |
| --- | --- |
| Run the zero-credential fixture-graph lifecycle | `make demo` |
| Run the deterministic project gate | `UV_OFFLINE=1 make verify` |
| Run a real or TUI demo route | `PROFILE=<profile> make demo-real` / `make demo-tui` — see [COMMANDS.md](COMMANDS.md) ladder |

## Bounded Real-Demo Calibration

Choose one registered, credential-backed profile explicitly for each comparison run:

```bash
PROFILE=<profile> make demo-real-scripted
make demo-sessions DEMO_ARGS="inspect <bundle-id>"
```

The scripted command uses its fixed question and starts a fresh Run Bundle; take the
printed Bundle id to the second, read-only command. Compare only the retained redacted
profile identity/revision, phase, failure category, budget-stop reason, and validation
codes. Repeat manually for another explicit profile when needed.

This is bounded diagnostic evidence: it does not qualify a model and does not select
or change a default model. It neither changes a prompt or budget nor reruns, resumes,
or controls an existing Bundle.

Run that inspection command from `deep_research_harness/`. It only reports a retained
observation: it cannot locate, resume, refine, cancel, or recreate a Run Bundle.
