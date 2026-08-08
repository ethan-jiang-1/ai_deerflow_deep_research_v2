## Context

`agent/` is a repository-local filesystem interface consumed by the structural
registry, its checkers, module commands, CI, Docker, and ignored local data. The
Python package identity is independent of that interface. The change spans tracked
files and ignored data, so a source move alone cannot be either atomic or safe for an
operator's existing session history.

## Goals / Non-Goals

**Goals:**

- Establish `deerflow_research/` as the single root for every tracked Deep Research
  consumer.
- Keep distribution, import, and public tool identities stable.
- Make CI/Docker contracts mechanically checkable at their resolved paths.
- Preserve retained sessions and diagnostics through an explicit, non-destructive
  local migration.

**Non-Goals:**

- Automatic migration of secrets, virtual environments, shell configuration, IDE
  tasks, GitHub settings, or other external automation.
- A compatibility source root or a broad rewrite of historical artifacts.
- A change to DeerFlow upstream behavior, graph behavior, or public APIs.

## Decisions

### One filesystem root, no compatibility alias

Use `git mv agent deerflow_research` in the same tracked change that updates every
repository-owned consumer. The structure registry is updated first as the exact path
inventory, its test fixtures are made to prove the new root and reject a stale root,
and the generated guide block is rendered through its owning checker.

An alias or symlink was rejected because it would create two valid-looking source,
test, Docker, and retained-data entry points; it also makes CI path filters ambiguous.
The public Python identities already resolve from `src/` and therefore do not need a
compatibility layer.

### Separate host path and private container path

The Compose host mount changes to `../deerflow_research/src`. Its private container
target becomes `/app/deerflow_research/src`, and the Gateway-only `PYTHONPATH` is
changed in lockstep. This makes host and container paths express the same owner.

Keeping `/app/agent/src` was rejected: the target has no documented external API and
would leave an unexplained old name in the executable contract. The rendered Compose
configuration, not YAML text alone, is the proof seam.

### Retained data is copied only after explicit confirmation

New runtime defaults resolve under `deerflow_research/`. A project-owned migration
entrypoint preflights both `agent/.deep-research-demo-runs/` and
`agent/.reports/deep-research-diagnostics/`, requires the operator to quiesce Deep
Research processes and pass an explicit confirmation flag, and copies each contained
regular-file tree through staging. An existing destination is `already_migrated` only
when its complete relative tree is byte-equivalent; any other destination, symlink, or
unsupported material fails without overwrite or deletion. A failure after one of the
two roots is published reports a retryable partial result rather than a false complete
migration.

Copy rather than move preserves the only local recovery source. A transparent legacy
fallback was rejected because it would keep two mutable retained roots and make
ownership, cleanup locks, and operator recovery ambiguous. `.env` and `.venv` remain
outside the command: the former is a secret-handling decision and the latter is a
rebuildable environment.

### CI identity changes only with external evidence

Update workflow filters, cwd, artifacts, fixtures, and release attestations, but leave
workflow file names, display names, job IDs, concurrency/status identifiers, badges,
and branch-protection assumptions untouched. Before merge, an operator checks branch
protection, badges, and external automation. Any discovered identity consumer is a
separate approved compatibility decision.

### Classify residual old-root references

The implementation uses an inventory and allowlist rather than a global replacement.
Each residual `agent/` occurrence is classified as generic DeerFlow terminology,
deliberately historical archive evidence, an external/operator item, or a defect. Only
the last category blocks the tracked migration. Active commands, guides, docs, specs,
and tests are tracked consumers and must move.

## Risks / Trade-offs

- [Ignored data is not moved by Git] -> Require an explicit preflighted copy command,
  conflict refusal, and an operator checklist before using the renamed checkout.
- [A consumer is absent from the audit] -> Re-run the current inventory before the
  move, use focused contract tests, and perform a post-move residual allowlist review.
- [A workflow path update changes required checks] -> Preserve status identity and
  require a branch-protection/external-automation audit before merge.
- [Partial rename reaches a branch] -> Keep registry, move, path consumers, and
  focused tests in one atomic tracked commit; block merge on the full gate.
- [Operator later rolls back tracked code] -> Rollback reverts tracked files only;
  it never touches copied local data, which remains recoverable at both locations.

## Migration Plan

1. Re-run the tracked and ignored-state inventory at the implementation commit and
   record any drift from the planning audit.
2. Add focused failing tests for canonical-root resolution, Compose rendering,
   workflow paths, and retained-data migration outcomes.
3. Update the registry/checkers and all active repository-owned consumers, render
   generated evidence, and use `git mv` for the module tree in the same change.
4. Quiesce local Deep Research processes, then run the operator data preflight and,
   when approved, migrate both retained-state and diagnostic-journal roots; separately
   recreate/copy `.env` securely and rebuild `.venv`.
5. Run the structural checker, focused contracts, `uv lock --check`, updated module
   verification, `docker compose config`, `git diff --check`, and residual allowlist
   scan. Check required workflow status identity with GitHub settings before merge.
6. To roll back, revert only the tracked commit. Do not delete either ignored retained
   root; the operator chooses when old local data can be removed after verification.
