## Why

Most local demo entry targets currently invoke bare `uv run`. A command can therefore
lock or synchronize the project as a side effect, and `make install` does not prepare
the `demo-real` extra required by the advertised real CLI and TUI. This makes ordinary
help and demo invocation contend over dependency state and turns a missing setup step
into an unrelated import or lifecycle failure.

The project already treats explicit setup and independent lock validation as separate
operations. This change makes that boundary true for every supported local demo entry
without redefining the existing profile or deterministic verification contracts.

## What Changes

- Make `make install` the explicit synchronization owner for the extras required by
  all supported local demo CLI and TUI targets, including `demo-real`.
- Make ordinary demo, inspection, workbench, and documented prepared all-real launcher
  entries run against the prepared project environment with locking and
  synchronization disabled. They must not create or update `uv.lock` or the project
  `.venv`.
- Add a fast deterministic command-environment preflight so a missing or incomplete
  local environment fails before Python with the single corrective action
  `make install`, while clearing a foreign `VIRTUAL_ENV` remains deliberate.
- Retain `make lock-check` as the independent lock-freshness assertion. A reviewed
  lockfile refresh is permitted only as an explicit repository update; `--no-sync`
  and ordinary target execution never stand in for that check.
- Add clean-copy/process and concurrent read-only command evidence. Declared ignored
  demo-run and diagnostic artifacts remain allowed outputs and are not treated as
  dependency-state mutation.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `demo-pipeline`: Require supported demo and retained-observation Make targets plus
  the documented prepared all-real launcher to preflight and use an explicitly
  prepared, non-mutating project environment, with `make install` and
  `make lock-check` retaining distinct responsibilities.
- `local-configuration-profiles`: Require `make profile-setup` to reuse the complete
  explicit project setup so the profile-gated workbench does not claim readiness with
  a partial optional-extra environment; ordinary profile commands retain their
  existing no-sync behavior.

## Impact

- Primary owner: `deep_research_harness/Makefile` and its command-environment target
  composition.
- Adjacent local code: `run/real-research.sh`, focused command-contract and
  clean-process tests, test-evidence metadata, the deterministic CI environment
  bootstrap, and concise operator setup text where it names a setup command.
- Existing contracts preserved: `profile-setup` remains the profile-specific explicit
  synchronization owner; ordinary profile commands stay locked and no-sync; and
  `UV_OFFLINE=1 make verify` remains the canonical deterministic aggregate with no
  implicit synchronization.
- No public tool, graph, profile, provider, lifecycle, or DeerFlow-framework behavior
  changes. `deerflow/`, `backend/`, and `frontend/` are out of scope.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/Makefile`, which selects
  the local project environment and decides whether a named command may synchronize
  dependencies before it executes a CLI, TUI, or read-only inspection adapter.
- **Question:** How can explicit setup prepare every supported local demo extra while
  ordinary Make targets and the documented prepared all-real launcher fail clearly
  when that environment is absent or incomplete, and otherwise execute without
  mutating `uv.lock` or the project `.venv`?
- **Necessary adjacent/external contracts:** `pyproject.toml` answers the closed
  optional-extra set that setup must synchronize; `demo-pipeline` answers the demo
  target and foreign-environment contract; `local-configuration-profiles` answers why
  profile setup remains a separate explicit owner and profile commands remain
  no-sync; `run/real-research.sh` answers how the documented direct all-real launcher
  invokes the same preflight and no-sync boundary without passing its question through
  Make; `evaluation-hardening` answers why `make lock-check`, the offline
  `make verify` gate, and its CI bootstrap retain their current independent roles;
  uv's documented `--locked` and `--no-sync` semantics answer which command flags may
  enforce each invariant.
- **Evidence seam:** a clean-copy subprocess contract runs explicit setup, then
  supported help, full-fake, fixture-graph, profile check, inspection, and the direct
  launcher's bounded credential-preflight entries, comparing the tracked lock and
  project environment state before and after each ordinary command; a focused
  concurrent read-only/help smoke covers overlapping invocations.
- **Not in scope:** automatic lock refresh or environment synchronization from an
  ordinary command; changing ignored run/diagnostic artifact policy; modifying
  profiles, DeerFlow source, `backend/`, `frontend/`, public tool authority, graph
  composition, or provider behavior.
- **Triggered review policies:** control-placement

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Whether a local entry may execute in the project environment | No cognitive candidate or human judgment; command class is fixed by the supported Make target or documented launcher | One shared Make preflight evaluates the prepared project `.venv` and complete entry dependency set before Python starts; the launcher invokes that preflight before its direct no-sync runner | non-bypassable | An ordinary command either executes with synchronization disabled in the prepared environment or exits with `make install`; it cannot sync, resolve, or fall through to an import failure | One environment boundary replaces per-target bare `uv run` behavior and avoids presentation adapters or the direct launcher owning dependency recovery | Clean-copy subprocess tests observe the actual Make command and launcher boundary, verifying missing/incomplete setup fails before adapter execution |
| Whether dependency metadata is fresh | No candidate or human judgment | `make lock-check` runs `uv lock --check`; explicit `make install` consumes the reviewed locked state | non-bypassable | `--no-sync` does not establish lock freshness; an out-of-date lock is reported only by the independent lock check, and ordinary commands never write `uv.lock` | Reuses the existing lock-check gate and avoids a second stale-lock detector or conflating setup with validation | Focused lock-check and clean-process tests distinguish lock consistency from no-sync command execution and compare the tracked lock before and after ordinary entries |
