## Context

See [proposal.md](proposal.md) for motivation and the delta specs for the observable
command contract. The current Makefile has one explicit `uv sync` target, but it
installs only `operations` and `demo-tui`; most other local entries invoke bare
`uv run`, which can lock and synchronize as a side effect. Profile commands already
use no-sync execution, while `profile-setup` separately installs only the operations
environment.

At planning time `cd deep_research_harness && uv lock --check` succeeds and the
current project environment contains the `operations`, `demo-tui`, and `demo-real`
distributions. No lockfile refresh is therefore planned. The design must still keep
lock freshness separate: `uv run --no-sync` has frozen behavior and is not an
assertion that the tracked lock matches dependency metadata.

## Goals / Non-Goals

**Goals:**

- Give all supported local CLI, TUI, fixture-graph, observation, workbench, and
  documented prepared all-real launcher routes one explicit environment-preparation
  path.
- Fail missing or incomplete setup deterministically before an adapter, Python import,
  model preflight, or lifecycle action begins.
- Use synchronization-disabled execution for ordinary local Make targets, retaining
  the current foreign-`VIRTUAL_ENV` isolation and fixture-source child-process scope.
- Prove the no-mutation property with a real clean-copy subprocess boundary rather
  than static Makefile strings alone.

**Non-Goals:**

- Treat no-sync execution as a lock-freshness check, automatically refresh `uv.lock`,
  or modify dependency metadata without a separately reviewed need.
- Change the profile resolver, root DeerFlow launcher, graph recipes, providers,
  retained-observation authority, or the ignored run/diagnostic artifact policy.
- Require credentials, network access, or real model execution for this change's
  deterministic evidence.

## Decisions

### One complete explicit environment owner

`make install` will run a locked synchronization with the closed extra set
`operations`, `demo-tui`, and `demo-real`, clearing a foreign `VIRTUAL_ENV` before
invoking uv. This is the only downstream target allowed to synchronize the project
environment. `profile-setup` will retain its profile-specific order: first the
unchanged root `make install`, then recursive invocation of the downstream
`make install` target. It therefore prepares the same complete environment that the
profile-gated workbench requires.

Using a different setup target for every extra was rejected: it would make an ordinary
command's readiness depend on hidden setup history and would reintroduce competing
environment owners. Installing every advertised local-demo extra is a deliberate
contributor setup cost, not a runtime side effect.

### Deterministic entry preflight and common runner

The Makefile will add a shared preflight target that checks the project `.venv` exists
and that the distributions corresponding to the closed setup extra set are present,
using the prepared environment's own Python and local package metadata. The preflight
does not invoke `uv sync`, `uv lock`, a provider, a graph, or an adapter. Its sole
failure message is the bounded action `make install`.

Supported command targets will depend on that preflight and use a shared runner that
clears `VIRTUAL_ENV` and invokes `uv run --locked --no-sync`; individual target flags
continue to select their declared extras, `.env` handling, fixture `PYTHONPATH`, and
arguments. `run/real-research.sh` will invoke the same preflight before directly
executing its quoted question with the no-sync runner, rather than trying to tunnel the
question through a Make variable. This preserves its current shell-quoting boundary.
The only exemptions in this entry surface are explicit environment setup and the
independent `lock-check`.

The runner deliberately does not report lock freshness. `make lock-check` continues
to run `uv lock --check` and is the only command in this surface whose result means
dependency metadata agrees with `uv.lock`. Combining both flags does not widen that
claim because no-sync remains frozen behavior.

### Permitted outputs and setup-state snapshots

The protected setup state is exactly tracked `uv.lock` plus the project `.venv` tree.
The checks will snapshot both after explicit setup and before each ordinary command.
Expected local operational output remains limited to the ignored paths already owned
by the repository: `.deep-research-demo-runs/`, `.reports/`, `.pytest_cache/`,
`.ruff_cache/`, `.node-prompt-review/`, and `evals/runs/`. Tests will name only the
paths exercised by their commands rather than treating all ignored files as a blanket
permission.

No new marker file records readiness. The environment itself and its installed
distribution metadata are the direct fact consumed by preflight, avoiding a second
state record that could become stale or authoritative.

### Evidence at the command boundary

Focused contract tests will cover the exact setup target, shared runner, foreign
environment clearing, preflight message, and preservation of the separate
`lock-check` command. A process test will create an isolated Harness copy, provide a
read-only sibling path needed by the existing editable DeerFlow dependency, run the
explicit setup once, and then run only credential-free supported paths: help,
full-fake, fixture-graph, retained inspection, and bounded profile/workbench checks.
It will compare the lock digest and a stable environment-tree snapshot around each
ordinary invocation.

The process test will also remove or deliberately omit a required distribution from a
prepared copy to prove the preflight stops before adapter execution and names
`make install`. It will run the direct launcher only through its bounded missing-
credential preflight, never against a provider. A two-process help/read-only smoke
will run in that prepared copy and assert no setup-state mutation. The deterministic CI
bootstrap will invoke `make install` once before this offline evidence so uv can
satisfy the clean-copy setup from its local cache; the canonical offline `make verify`
command remains unchanged. Real demo execution stays outside this proof because
credentials are neither required nor a replacement for command-environment evidence.

Every process-test child will remove `DEEPSEEK_API_KEY`, `ANTHROPIC_API_KEY`,
`OPENAI_API_KEY`, and `TAVILY_API_KEY` from its inherited environment. Before invoking
the direct launcher, the isolated copy will receive a test-owned empty `.env` before
the setup-state snapshot. The expected launcher result is the existing bounded missing-
credential preflight, not a provider request; neither inherited secrets nor a local
developer `.env` may turn this deterministic test into a real run.

## Risks / Trade-offs

- [A manually created partial `.venv` looks usable to uv] -> The preflight checks the
  complete declared distribution set with the environment's Python before any target
  adapter starts.
- [No-sync may hide an outdated lock] -> `make lock-check` remains mandatory in the
  documented setup and deterministic verification gate; neither preflight nor runner
  emits a freshness claim.
- [A clean-copy setup depends on network availability] -> The deterministic CI
  bootstrap invokes `make install` to populate the declared complete extra set once,
  then subprocess evidence runs offline against that local uv cache and remains
  focused on credential-free or bounded credential-preflight routes.
- [Snapshot assertions mistake intended diagnostics for dependency mutation] -> Tests
  snapshot only `uv.lock` and `.venv` and explicitly allow the few ignored outputs
  created by the exercised command.
- [Inherited credentials turn launcher evidence into a paid run] -> Every test child
  removes the four supported model/web key variables and uses a test-owned empty `.env`;
  the launcher assertion stops at its bounded missing-credential preflight.
- [Recursive `profile-setup` obscures the upstream boundary] -> It continues to call
  the existing root target first and only delegates to the named downstream setup;
  it neither edits nor inspects DeerFlow source.

## Migration Plan

1. Add the focused red command-contract and clean-copy tests, then implement the
   shared Makefile preflight/runner and complete explicit setup path.
2. Run `uv lock --check`; refresh `uv.lock` only if reviewed project dependency
   metadata requires it, then rerun the check. The current passing check means no
   lockfile edit is expected merely for this change.
3. Update the concise setup wording and static command contracts, run focused tests,
   the offline deterministic gate, and strict OpenSpec validation.
4. If rollback is required, revert the Makefile/docs/tests and rerun explicit
   `make install`; do not make an ordinary command synchronize as a rollback path.
