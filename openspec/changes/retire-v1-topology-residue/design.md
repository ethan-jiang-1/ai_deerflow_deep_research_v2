## Context

See `proposal.md` for the motivation and Focus Card. At the Stage 1 planning baseline,
Git metadata identifies `deerflow/` as the repository's upstream gitlink, while the
downstream product is owned by `deep_research_harness/`. Four current documentation
surfaces contradict that topology or rely on the resulting old path:

- `openspec/config.yaml` names root `backend/` and `frontend/` as upstream mirrors and
  uses them as the proposal/archive protected boundary;
- `deep_research_harness/AGENTS.md` repeats the root-mirror claim;
- `openspec/agent-charter/charter.md` gives the same root-boundary description; and
- `deep_research_harness/README.md` points its editable install at a nonexistent sibling
  `../backend/packages/harness` path.

Active main specs also mention `backend/` and `frontend/`. Those occurrences are valid
negative guards against placing downstream source in legacy root paths, not assertions
that the directories are current DeerFlow mirrors. They must remain unchanged.

## Goals / Non-Goals

**Goals:**

- Make the four current explanatory surfaces describe the same verified V2 topology.
- Replace old proposal/archive path claims with bounded manual evidence for the
  `deerflow/` gitlink boundary.
- Correct the editable-install command while preserving its repository-root context.
- Leave a reviewable classification of retained `backend`/`frontend` terms and the
  limits of the available verification.

**Non-Goals:**

- Create a gitlink pointer/worktree detector, change a governance executable, or claim
  automatic enforcement of the upstream boundary (A-002 remains deferred).
- Modify application code, tests, dependencies, manifests, TOML registries, generated
  inventory, main specs, archived changes, or `deerflow/` content/worktree.
- Read DeerFlow source, replace every `backend`/`frontend` token, or weaken a valid
  legacy-root placement guard.

## Decisions

### 1. Treat this as a documentation-only change

The change declares `skip_specs: true`. It alters neither runtime behavior nor an
observable requirement: main specs already state the valid downstream placement guards
and no behavior contract needs a new or modified delta.

Rejected alternative: add a topology requirement solely to produce a delta spec. That
would make documentation correction look like a new runtime/structural behavior and
would unnecessarily alter main-spec authority.

### 2. Use an explicit occurrence allowlist instead of a token replacement

Apply only the stale root-mirror descriptions in `openspec/config.yaml`,
`deep_research_harness/AGENTS.md`, and `openspec/agent-charter/charter.md`; apply only
the invalid editable path in `deep_research_harness/README.md`. In `config.yaml`, revise
both its opening topology route and its proposal/archive instructions together, so the
document does not describe one boundary at the top and validate another at closeout.

The replacement language shall distinguish three facts:

1. `deep_research_harness/` is the downstream product.
2. `deerflow/` is the upstream gitlink leveraged as a host dependency and is not changed
   or source-browsed by ordinary downstream work.
3. Current closeout evidence is manual Git metadata/scope evidence, not a detector of
   the gitlink pointer or nested worktree.

Rejected alternative: global replacement of `backend` and `frontend`. Those terms occur
in valid dependency paths, domains, and legacy-root negative guards; global replacement
would create unrelated drift and could weaken an existing structural invariant.

### 3. Preserve valid legacy-root guards verbatim

The active main-spec guards saying no downstream source belongs under `backend/` or
`frontend/` remain valid even though those paths are not this checkout's upstream
mirror. Planning and apply review will classify every retained active non-archive
occurrence by meaning rather than require token count to reach zero.

Rejected alternative: make main-spec edits during Stage 1. No active requirement was
found to falsely call the legacy paths DeerFlow mirrors, so a delta would expand scope
without a behavior change.

### 4. Make closeout evidence bounded and explicit

Before and after apply, the change records the repository HEAD, worktree status,
`git ls-files --stage deerflow`, `git submodule status -- deerflow`, and the gitlink's
own `git -C deerflow status --porcelain=v1 --untracked-files=all`. These establish the
observed gitlink identity and the checked nested-worktree status only. The closeout
wording must state that they do not prove an automatic detector exists or prove every
possible future nested-worktree condition.

The apply evidence must also record a small classification table for every active
non-archive documentation/governance occurrence considered by the C-001 search. Each
row identifies the path, the term, and one of: target root-mirror claim, retained
`deerflow/backend/...` dependency path, retained domain/host-interface term, or retained
legacy-root negative guard. Historical archives, generated lockfile entries, and
`deerflow/` source content are excluded by the change boundary and are not reclassified.

Rejected alternative: say the gitlink is simply "kept clean." That wording obscures
which command checked which fact and can be mistaken for mechanical enforcement.

## Risks / Trade-offs

- [A text-only replacement could change a valid path or domain term] -> Use the explicit
  occurrence allowlist, reclassify remaining active occurrences manually, and require a
  scoped diff review before apply.
- [Readers may infer that a gitlink boundary permits browsing its source] -> State that
  ordinary work leverages the gitlink without modifying or source-browsing it; retain
  the root-guide boundary.
- [Manual evidence may be mistaken for a detector] -> Name the commands and their proof
  bounds in `config.yaml`, the change records, and closeout; retain A-002 as
  `DEFERRED-CODE-CHANGE`.
- [A valid YAML edit may leave the authoring route unreadable] -> Run both OpenSpec
  validation/doctor and the project Charter checker after editing `openspec/config.yaml`;
  stop on a parse or governance failure rather than changing unrelated files.
- [The README path may be correct only from one directory] -> Preserve the existing
  repository-root command context and cross-check the path with `pyproject.toml` and
  the lockfile without editing either.
- [An active main-spec negative guard may be removed accidentally] -> Treat every
  retained `backend`/`frontend` occurrence as a semantic classification result, not
  cleanup residue.

## Migration Plan

1. Reconfirm the Stage 1 baseline and record any unrelated worktree changes without
   overwriting them.
2. Apply C-001 and C-002 atomically in `openspec/config.yaml`, local `AGENTS.md`, and
   the Charter; apply C-003 only to the README command text.
3. Run strict OpenSpec validation, Markdown/link and whitespace checks, Git metadata
   checks, and the existing read-only verification command. Stop on a failure rather
   than modifying code or tests to obtain green output.
4. Complete one Adjustment Record each for C-001, C-002, and C-003, including observed
   side effects and the proof bounds; then obtain separate approval before archive or
   any Stage 2 work.

Rollback is a narrow revert of the four documentation surfaces in this change only.
It does not alter Git history, the gitlink pointer, the nested worktree, runtime data,
or dependency metadata.
