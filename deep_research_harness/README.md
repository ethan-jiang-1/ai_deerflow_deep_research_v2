# DeerFlow Deep Research Harness

This independent Python project contains the downstream Deep Research Harness for
DeerFlow 2.1. The Harness creates and controls independently deletable Run Bundles;
each Bundle's local Research State, evidence, and content are the durable record for
one continuing Deep Research run. Its controller is a nested Python `StateGraph`, and
bounded agent loops execute inside graph nodes. DeerFlow remains the host runtime and
does not import this package.

Production node packages expose real factories only. Deterministic fixture adapters live in
the separate `src_fake/deerflow_deep_research_fixtures/` package, which is excluded from the
production wheel and reflected runtime. Every graph receives an explicit recipe: the public
host is fixed to `all_real`, an explicitly composed fixture demo or test recipe reports
`fixture`, and an explicitly composed test mix reports `mixed`. `full_fake` is retained only
as read-only metadata for retired records. These labels identify implementation composition,
not provider success, evidence acceptance, or report quality.

| Entry point | Recipe | Boundary |
| --- | --- | --- |
| `make demo`, `make demo-scripted`, `make demo-tui-fake` | full fake | zero credentials; retained deterministic presentation-only demonstrations |
| `make demo-fixture-graph` | fixture | deterministic graph-composition verification; `src_fake` is enabled only for that child process |
| `make demo-real`, `make demo-tui` | all real | local model and web-search prerequisites |
| reflected `deep_research` tool | all real | public control surface; never imports or selects fixtures |
| `make session-workbench` | configured fixture demo | typed Run Bundle projections only |

## Reading Map

This README is a human/operator entry page, not default context for an ordinary code
change. Coding agents begin with [`AGENTS.md`](AGENTS.md), then read only the owning
specification, implementation, and test seam selected by its focus gate.

| Need | Start here |
| --- | --- |
| Choose one human-facing reference | [Documentation index](docs/README.md) |
| Understand Harness, Run Bundle, graph, evidence, sandbox, or public-control boundaries | [Runtime architecture](docs/runtime-architecture.md) |
| Run profiles, demos, diagnostics, retained observations, workflow outcomes, or the workbench | [Local operations](docs/local-operations.md) |
| Select and interpret deterministic, workflow-outcome, live, or release testing | [Testing and evaluation](docs/testing-and-evaluation.md) |
| Run or interpret a manually selected Cognitive Evaluation case | [Cognitive Evaluation Suite](docs/cognitive-evaluation-suite.md) |
| Inspect the generated graph topology | [Logical topology](docs/deep-research-topology.md) |
| Make a code or governance change | [`AGENTS.md`](AGENTS.md), then the [Agent Charter](../openspec/governance/agent-charter/README.md) policy triggered by the change |
| Find exact path and layer rules | [`project-structure.toml`](../openspec/governance/project-structure.toml) |

The focused documents preserve the detailed operational and evidence reference that
previously lived here. Open only the one needed for the current question.

Real-demo workflow outcomes, provider recovery, diagnostic locations, and fresh-start
semantics are kept in [Local operations](docs/local-operations.md), not in this entry
page.

## Quick Start

Requirements: Python 3.12 or newer, `uv`, and the sibling DeerFlow harness at
`../backend/packages/harness`.

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

One available Run Bundle retains at most one pending Run Refinement. A nonblank
`refinement` submits that independent same-Run direction; `resume` remains only the
correlated answer to the visible pending subject, and an Accepted Profile Note remains
content accepted during Research Confirmation rather than a later lifecycle inbox. The
pending direction takes effect only at the completed terminal boundary of the current
round, so it never overwrites an in-flight writer or replaces a pending response.

The same `refine` action also has a narrow explicit continuation form: it omits
`refinement`, names an available terminal `bundle_id`, and can consume only the already
pending direction in that Bundle. It never reconstructs hidden text or mutates a
profile. Stopped, cancelled, and blocked Bundles do not restart automatically. Consumers
must follow the typed result's legal next action: it may require `resume`, `status`, a
selected continuation, a new text-bearing direction, or a fresh `start` when the Bundle
has no remaining refinement capacity.

The recommended ordinary-language route is the provisioned dedicated Agent. Its
controller workflow is loaded from the committed public skill through DeerFlow's
configured `file:read` group before a later exclusive lifecycle call. The Harness
preflights that existing group and its public `read_file` binding but does not create,
repair, or narrow it; the full configured group remains the operator-visible permission
boundary. [Runtime architecture](docs/runtime-architecture.md) and [local
operations](docs/local-operations.md) own the operational detail.

## Frequent Commands

| Goal | Command |
| --- | --- |
| Walk the zero-credential full-fake lifecycle | `make demo` |
| Verify deterministic fixture-graph composition | `make demo-fixture-graph` |
| Run the credentialed all-real demo with a question | `make demo-real DEMO_ARGS='--question "Compare battery storage costs"'` |
| Run the prepared all-real research launcher | `bash run/real-research.sh` |
| Run the deterministic project gate | `UV_OFFLINE=1 make verify` |
| Inspect one retained observation, read-only | `make demo-sessions DEMO_ARGS="inspect <bundle-id>"` |

Run that inspection command from `deep_research_harness/`. It only reports a retained
observation: it cannot locate, resume, refine, cancel, or recreate a Run Bundle.
