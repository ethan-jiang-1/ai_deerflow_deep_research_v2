## Context

See `proposal.md` — Why for motivation. Verified current state:

- Six OpenSpec governance checkers exist under `openspec/governance/`:
  `check_project_reqs.py`, `check_project_specs.py`, `check_project_architecture.py`,
  `check_change_guidance.py`, `check_project_req_coverage.py`, and
  `check_harness_dependency_direction.py`. Four exit non-zero today (unregistered IDs,
  missing `> req:` headers, unregistered `.repro-tmp/` ignore entry, missing evidence),
  `check_change_guidance.py` passes vacuously (no active change), and
  `check_harness_dependency_direction.py` passes.
- `deep_research_harness/Makefile::verify` was intentionally de-governed by commit
  `54886b8`; the governance pytest suite was deleted by `62cc484`. Accepted
  `evaluation-hardening` EVH-005 and `deep_research_harness/docs/testing-and-evaluation.md`
  still describe the pre-removal composition — a committed-but-unpropagated drift.
- `DRC-012` and `PRS-009` freeze the dependency direction `openspec/ ->
  deep_research_harness/`: OpenSpec governance MAY inspect the Harness, but no Harness
  surface SHALL read, import, execute, or link OpenSpec content. Restoring a
  `governance` target inside `make verify` would violate this contract.
- `openspec` CLI is external npm package v1.9.0 (unmodifiable). Native `openspec
  archive` cannot be blocked from the CLI side; a hard stop is only enforceable inside
  repository agent workflows (skills).
- `openspec/change-guidance/core/change-practice.md` is part of the portable,
  product-neutral kernel with a digest-bound snapshot contract
  (`portable-change-guidance` PCG-001/PCG-005). Project-specific ID rules do not
  belong there.
- `polish-openspec-change` may write only inside `openspec/changes/<change>/` and may
  read governance files; it may never write the registry or accepted specs.

## Goals / Non-Goals

**Goals:**

- One OpenSpec root governance aggregate that combines the six registered checkers,
  runs from the repository root, preserves component exit codes, and owns no rule
  semantics.
- A read-only `plan` phase that makes delta mechanics (header declaration, title
  anchor, MODIFIED scenario completeness, ID collision, retired reuse) reachable at
  propose/polish time, with legal new IDs surfaced as non-authoritative reservations.
- A `closeout` phase that requires zero exit from every checker plus full
  registry/active-delta/main-header/evidence consistency before repository archive
  workflows proceed.
- A clean write separation: reservation is advisory output, apply tasks perform the
  authoritative registry write, closeout only detects inconsistency.
- Authoring rules reachable where authors work: delta mechanics in
  `openspec/config.yaml rules.specs`, archive gate in `rules.tasks`, propose→polish
  handoff in the propose skill, plan check in the polish skill, closeout stop in the
  archive skill.
- Converge the in-scope baseline drift (T0) so the six checkers all exit zero.
- MODIFY `deep-research-agent-charter` DRC-010 so the deterministic gate's stopping
  authority is kept distinct from advisory operation guidance and non-authoritative
  selected-change evidence: the gate may stop repository archive workflows on a
  component non-zero exit, derives that authority from the deterministic component
  checkers only, does not block or directly change native `openspec archive`, and
  recovers by fix-and-rerun.

**Non-Goals:**

- Modifying the external `openspec` CLI or claiming a native-archive hard stop.
- Restoring a governance target in `deep_research_harness/Makefile` or any Harness
  dependency on OpenSpec content.
- Modifying the portable core (`change-guidance/core/change-practice.md`) or the
  portable snapshot manifest.
- Registry↔main-header single-source generation (long-term item, not this change).
- Reader Roles / Line Budgets single-sourcing (T4 of the prior plan) and creating a
  follow-up change for it.
- Rewriting archived change history or renumbering archived IDs.
- Any Harness runtime, application, or API behavior change.

## Decisions

### 1. One aggregate script: `openspec/governance/check_project_gate.py`

A single stdlib-only script `check_project_gate.py` runs the six component checkers as
subprocesses from the repository root, preserves each exit code, and aggregates to a
final 0/1. It is orchestration-only by construction: it never imports checker internals
to re-decide semantics, never writes the registry, never judges prose, and never
reimplements delta/registry regex or parsing. Every semantic check, including in the
`plan` phase, is delegated to the component that owns it (Decision 2); closeout
aggregates the six default component exit statuses and adds no duplicate consistency
checker, because `check_project_reqs.py`, `check_project_specs.py`, and
`check_project_req_coverage.py` already own registry/header/evidence consistency
(Decision 3).

Alternatives considered:
- Re-register the checkers into `make verify` — rejected: violates DRC-012/PRS-009
  dependency direction and would re-introduce the 54886b8 regression.
- A shell wrapper — rejected: harder to test deterministically and to fail closed on
  empty scans.
- No aggregate, manual commands only — rejected: the复盘 finding is precisely that
  un-composed commands stay unreachable.

Rationale: the aggregate is a new registered governance entry (PRS-009 MODIFIED), so
its path, phase contract, and focused tests enter `project-structure.toml` and the
OpenSpec-side test tree at `openspec/tests/governance/` (newly created; kept outside
`deep_research_harness/tests` to preserve the dependency direction).

### 2. `--phase plan --change <name>`: read-only admission, delegated to semantic owners

Plan phase invokes the existing semantic owners in scoped modes; the aggregate itself
performs no parsing:

1. `check_change_guidance.py` — Focus Card / Program Focus grammar for active changes
   (reuses existing enforcement, no new semantics).
2. `check_project_specs.py --change <name>` (extended selected-change mode) — delta
   mechanics on the named change's delta specs: each delta declares owned requirement
   IDs on a `> req:` line before its first heading, and Requirement titles do not
   embed IDs (`### Requirement: Foo`, never `### Requirement: Foo (XXX-001)`).
3. `check_project_reqs.py --change <name>` (extended planning mode) — reservation
   semantics follow the ID lifecycle: an unregistered ID declared by the selected
   change that does not collide with any other active delta is a legal pending
   reservation, printed as `reservation: <id> (capability)` on stdout; an alive
   registered ID owned by the same capability is reported as `already-assigned`, not
   as a collision; a registered ID owned by a different capability fails as an
   already-assigned ownership violation; a `[DEPRECATED]` (retired) ID always fails
   as reused-retired and is never a reservation or an already-assigned pass.
   Nothing is written.
4. `openspec validate <name> --strict` — full MODIFIED requirement/scenario
   preservation (a MODIFIED block carries the full requirement and every surviving
   scenario). The native archive check is thereby made reachable at plan time; the
   aggregate does not reimplement scenario comparison.

The scoped component modes are implemented and tested inside their owning checkers
(selected-change scope is a view over the same rule logic), not in the aggregate.
These checks read `req-registry.yaml` and `openspec/changes/` only.

### 3. `--phase closeout`: full consistency gate via the six default components

Closeout runs all six checkers with exit-code preservation and aggregates their exact
exit statuses: any non-zero component exits non-zero overall, naming the failing
checker. Closeout adds **no duplicate consistency checker**: registry vs. active
delta/main spec header consistency is owned by `check_project_reqs.py` (unregistered /
foreign / orphan / reused-retired), main spec structure and `> req:` headers by
`check_project_specs.py`, and registered-alive/pending evidence by
`check_project_req_coverage.py`. The archive skill stops its workflow on a non-zero
closeout — an in-repository hard stop, honestly documented as not blocking a direct
native CLI invocation.

### 4. Write separation and authority

| Fact | Authority / writer |
| --- | --- |
| Rule semantics | Each component checker owns its rule; the aggregate owns none |
| Accepted ID authority | `openspec/governance/req-registry.yaml` |
| Plan reservations | Advisory stdout of `--phase plan`; never written, never authoritative |
| Registry writes | Apply tasks (explicit first task per new ID) |
| Closeout detection | `--phase closeout` (read-only) |
| Harness application evidence | `deep_research_harness` tests + `UV_OFFLINE=1 make verify` (independent) |

This resolves the polish/apply loop: polish runs plan (read-only), requires a
reservation plus an explicit apply registration task, and reports `not ready` if
either is missing. It never writes the registry.

### 5. Header lifecycle: delta `> req:` is planning declaration, main-spec header is an explicit apply edit

A delta's leading `> req:` line is a planning declaration owned by this change's
artifacts; it does not mutate any accepted main spec. The generic archive sync skill
merges MODIFIED requirement bodies and scenarios but does **not** merge top-level
`> req:` headers. Therefore the accepted main spec header repairs for `EXI-001`
(`execution-intent`), `LSA-001` (`low-scale-real-auto`), and `REG-022`
(`research-graph-lifecycle`) are explicit apply metadata edits to the main spec
files, executed as tasks, and re-checked (against the registry) after archive sync.
No artifact may claim that archive sync automatically adds those headers.

### 6. Delta mechanics live in `config.yaml rules.specs`, not the portable core

The three delta-mechanics rules (MODIFIED full-scenario carry, title-as-anchor no-ID,
new-ID `> req:` declaration) are injected into `openspec/config.yaml rules.specs`
where `openspec instructions specs` actually consumes them, and are executed by the
plan phase and strict validation. The portable core stays untouched because the rules
reference project-specific registry semantics (product-bound), and modifying the core
would trigger the digest-bound snapshot contract.

### 7. Skills wiring

- `openspec-propose`: final handoff must read `/polish-openspec-change <name>` instead
  of jumping to apply.
- `polish-openspec-change`: pass criteria gain a plan-phase check item; a failed plan
  check (missing header, title-embedded ID, collision, retired reuse, missing
  reservation+registration task) reports `not ready`.
- `openspec-archive-change`: before the archive flow, run `--phase closeout`; a
  non-zero result stops the workflow with the failing checker named. Its
  allowed-tools frontmatter is extended to `Bash(python3:*)`, `Bash(python:*)`, and
  `Bash(git:*)` alongside `Bash(openspec:*)` so the Python closeout gate is actually
  executable; no broader expansion.

These are in-repository workflow changes. The native CLI remains callable; no claim of
CLI-level enforcement is made.

### 8. T0 baseline convergence is in-scope

The four red checkers are repaired inside this change: registry registration for
`EXI-001`, `LSA-001`, `SCR-006` and `REG-022` (renumbered from the mistyped `RGL-014`),
explicit main spec `> req:` header edits for `execution-intent`, `low-scale-real-auto`,
and `research-graph-lifecycle` (apply metadata edits, re-checked after archive sync —
see Decision 5), `.repro-tmp/` registration in `project-structure.toml`, real `@impl`
evidence for `EXI-001`, `LSA-001`, `REG-022`, `SCR-006`, `REJ-009`, and the stale
`workflow-outcome-review.md` config context-path fix (only the configured context
path string changes to `profiles/workflow-control/workflow-control.md`; the canonical
review trigger name `workflow-outcome-review` in `rules.proposal` and its checker
mapping remain unchanged). This is required before any closeout
gate can pass and is therefore part of this change, not an unrelated blocker.
(The zero-active baseline was the pre-proposal investigation provenance; once this
change exists, `openspec list --json` shows it as the active change, and apply asserts
it is the expected selected change rather than re-asserting zero active changes.)

### 9. Gate composition is two independent columns

```text
OpenSpec root aggregate (six checkers)   |   deep_research_harness UV_OFFLINE=1 make verify
  plan: admission, read-only             |     lock, lint, assets, fast, integration, workflow
  closeout: full consistency             |     no OpenSpec reads/imports/execution
```

`config.yaml rules.tasks` lists the archive-gate command set explicitly with the
exit-code-direct-measure warning (`| tail` swallows exit codes), and the
`evaluation-hardening` EVH-005 delta codifies the composition so accepted spec,
documentation, and implementation stop drifting.

### 10. Candidate requirements reviewed and excluded from MODIFIED

The following candidate IDs were fully read with their surviving scenarios and
deliberately NOT modified: `DRC-004` (Focus Card semantics already enforced by
`check_change_guidance.py`; this change only wires that enforcement into the gate),
`DRC-012` (Harness dependency direction and the LLM-node authoring route are
unchanged), `EVH-010` (requirement-to-test coverage mechanics unchanged; T0 only
repairs evidence data), and `PRS-006` (ignore-policy semantics unchanged;
`.repro-tmp/` registration is data instantiation of the existing permitted
ignored-path rule). Modifying them would invent requirement churn without behavior
change. `DRC-010` is the one charter requirement this change deliberately modifies
(Decision 11); `DRC-004` and `DRC-012` remain excluded because their semantics are
unchanged.

### 11. DRC-010 is MODIFIED to separate deterministic gate authority from advisory surfaces

Accepted `deep-research-agent-charter` requirement `Selected control-placement
review has durable operation guidance` (`DRC-010`) owns the authoring-route boundary
that operation guidance and selected-change closeout evidence remain advisory and
never block a native OpenSpec operation. The new independent canonical project
governance gate stops the repository-managed archive agent workflow on a component
non-zero exit — an authority that must not be confused with guidance or evidence.
This change therefore MODIFIES `DRC-010` with one normative paragraph and one
scenario stating: the gate MAY stop the repository-managed archive agent workflow on
non-zero; its stopping authority derives solely from the deterministic component
checkers' exit statuses, not from operation guidance or selected-change evidence; it
does not block or directly change native `openspec archive`; recovery is to fix the
named finding and re-run the gate. All existing guidance and selected-change evidence
boundaries and every surviving scenario are preserved verbatim.

The separate `Operation-guidance integration evidence stays bounded` requirement
(also `DRC-010`) was compared and is NOT modified: its ban on evidence creating an
archive blocker is scoped to evidence/guidance surfaces, and the new gate is
deliberately separate, so no textual clarification is needed. `DRC-004` (Focus Card)
and `DRC-012` (dependency direction) remain unmodified: their semantics are
reused/read, not changed.

## Risks / Trade-offs

- [Risk: aggregate adds a new control layer] → Mitigation: orchestration-only by
  contract and by test; it adds no rule semantics, and it removes the current
  "rules exist but are unreachable" failure that the campaign measured. Net complexity
  decreases across the workflow.
- [Risk: plan-phase logic duplicates component checker semantics and drifts] →
  Mitigation: the plan phase performs no parsing of its own. It delegates to scoped
  component modes — `check_change_guidance.py` (Focus), `check_project_specs.py
  --change` (delta header/title), `check_project_reqs.py --change` (reservation /
  collision / retired / other-active), and `openspec validate <name> --strict`
  (MODIFIED scenario preservation). Closeout aggregates the six default component exit
  statuses without a duplicate consistency checker. Scoped modes are implemented and
  tested inside their owning checkers.
- [Risk: a hard stop in archive skill misleads about native CLI bypass] → Mitigation:
  skill text states the stop is in-repository workflow enforcement only; a direct
  `openspec archive` invocation is not blocked. Recovery is fix-and-rerun: the
  repository workflow stops, the author repairs the named checker/file, and the gate
  is re-run until zero.
- [Risk: gate-tightening slows future changes] → Mitigation: T0 convergence lands in
  the same change so the gate starts green; plan-phase failures are read-only and
  actionable (named checker/file).
- [Risk: evidence binding for five requirements lands decoratively or overclaims] →
  Mitigation: each `@impl` is bound to an existing test that already asserts the
  requirement's behavior, and evidence classes are stated honestly — policy-envelope
  snapshot tests for REJ-009, strict-msgpack/checkpoint tests for REG-022,
  scripted-real-workflow tests for SCR-006, and for EXI-001 a combined seam
  (non-interactive intake + HITL profile construction + wave2 gate budget). For
  LSA-001, deterministic mode-003 CLI/report contract tests prove wiring and gates
  only; real-provider/source behavior (real report content, real source URLs,
  `RESULT: PASS`) is evidenced by the retained dated real-run acceptance record
  `_backlog/_local_demo/runbook-003-medium-real-auto.md`, never by minimal-intent
  unit tests alone. New focused assertions are added where the existing suite lacks
  them.
- [Risk: this change is polished before the new gate exists (bootstrap)] → Mitigation:
  polish for this change (a bootstrap-era pass, before the gate existed) used the
  existing validation stack and the six standalone checkers; the gate landed in apply
  section 3 and is exercised end-to-end at this change's archive closeout (see
  Migration Plan step 0; the current checkout now contains the gate).

## Migration Plan

0. Bootstrap note: the plan/closeout gate machinery (`check_project_gate.py`, the
   scoped component modes) did not exist while this change was being proposed and
   polished, so this change's own polish ran the existing validation stack
   (`openspec validate <name> --strict`, `check_change_guidance.py`, `git diff
   --check`) plus the six standalone checkers. That bootstrap fallback remains valid
   for older checkouts that predate the gate; in the current checkout the gate has
   landed (apply section 3), and the archive closeout of this change exercises
   `--phase closeout` end-to-end. Task totals in this file above the original 30
   count bounded-review findings added as ordinary tasks (per 7.1); that growth is
   review bookkeeping, not plan inconsistency.
1. Apply T0 first: registry/header/evidence convergence (main spec `> req:` headers
   are explicit apply metadata edits — see Decision 5), config stale path + ignore
   policy registration; verify all six checkers exit zero.
2. Implement the scoped component modes (`check_project_specs.py --change`,
   `check_project_reqs.py --change`) and `check_project_gate.py` with `plan`/`closeout`
   phases and focused negative fixtures; register in `project-structure.toml`.
3. Wire `config.yaml rules.specs` / `rules.tasks` and the three skills.
4. Update `governance/README.md` and `docs/testing-and-evaluation.md`.
5. Run the full verification set (six checkers, Harness verify, strict validate, diff,
   gitlink scope) and confirm the `EVH-005`, `PRS-009`, `REG-022`, and `DRC-010`
   deltas match their main specs verbatim (whitespace-insensitive) with every
   surviving scenario. Archive sync (delta → main) is performed by the archive
   workflow; after sync, re-check that the main spec `> req:` headers for `EXI-001`,
   `LSA-001`, and `REG-022` are complete and consistent with the registry (the
   generic sync skill does not merge top-level headers).

Rollback is a normal source revert: no runtime state, data migration, or remote
setting is involved; `deerflow/` gitlink and nested worktree remain untouched.

## Open Questions

None. All decisions that could change the specs, approach, or task breakdown were
resolved from verified repository facts.
