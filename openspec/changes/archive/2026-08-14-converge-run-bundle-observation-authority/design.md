## Context

See [proposal.md](proposal.md) for motivation and scope. The verified current
runtime has one canonical text-bearing refinement admission boundary:
`BundleLifecycle.admit_refinement()`. It returns a `RefinementAdmission`, whose
`state` is produced by the shared Bundle-local transition path. The remaining
`BundleLifecycle.refine()` method merely calls that boundary and returns
`admission.state`.

`BundleWorkbench.refine()` is the sole production consumer of that wrapper. It
then projects that State with `result_for_state()` into its existing
`BundleControlResult`. The public `BundleControl` already calls
`admit_refinement()` directly and separately maps the admission disposition for
the public refinement action. The workbench must retain its existing projection;
it is not a public-control replacement.

The root package exports only `__version__` and `deep_research_tool`. The direct
wrapper callers are internal production code and two focused lifecycle test
modules, so no supported external Python compatibility window is required.

The accepted registry and four accepted session-named specs still describe
deleted session/binding mechanisms. In contrast, Bundle-local State owns
lifecycle truth (`DRH-*`), the Event Journal owns observation (`REJ-*`), and the
workbench is a typed, read-only/control projection. Existing negative tests
already establish that the retired session-store and binding modules cannot be
imported and that a contained Journal cannot reopen a deleted Bundle.

## Goals / Non-Goals

**Goals:**

- Make `admit_refinement()` the only internal text-bearing refinement admission
  handoff while preserving the workbench's existing `BundleControlResult`
  projection and legal-next-action behavior.
- Make accepted capability names, registry ownership, annotations, and evidence
  describe the current Bundle, Journal, workbench, and worker-failure owners.
- Preserve the Bundle-loss, scoped denial, replay/conflict, pending-response,
  textless-continuation, and no-resurrection guards with deterministic evidence.

**Non-Goals:**

- Change a public tool schema or exported Python API, add an external compatibility
  layer, migrate persisted records, or change provider/checkpoint recovery.
- Add a session/binding/broker mechanism, a new human control, a live evaluation,
  or any DeerFlow source/interface work.
- Alter RDO/RSV behavior or reuse deprecated RUS/RES identifiers.

## Decisions

### Use the canonical admission result without changing the workbench projection

`BundleWorkbench.refine()` will call `BundleLifecycle.admit_refinement()` with
the same trusted scope, selected Bundle id, text, and operation key it supplies
today. It will project `admission.state` with its existing
`result_for_state(action=REFINE, ...)` call. Its current `BundleAlreadyActive`,
`BundleLifecycleError`, `TypeError`, and `ValueError` handling stays in place.

This preserves the workbench's current state-derived `BundleControlResult`; in
particular it does not adopt `BundleControl`'s public disposition-to-result-code
mapping. The latter is a separate public-control concern. A direct admission
handoff removes the state-only API without introducing a second projection rule.

Alternative considered: expose `RefinementAdmission` directly from the workbench
or duplicate the public-control disposition mapping. Both alter the existing
workbench contract and add a new consumer-specific control interpretation.

### Remove the state-only wrapper after all direct consumers migrate

The implementation will first add red deterministic evidence that the workbench
does not call `BundleLifecycle.refine()` and that the wrapper is absent. It will
then migrate the workbench and the focused direct lifecycle tests to consume
`RefinementAdmission.state`, delete `BundleLifecycle.refine()`, and update the
tests' `@impl` ownership. No forwarding alias, deprecated callable, or dynamic
fallback will remain.

Alternative considered: retain a deprecated wrapper for one release. The verified
call graph and root exports provide no supported external consumer; retaining it
would preserve the competing state-only handoff this change removes.

### Converge capability records without a dual-name compatibility layer

The accepted `research-session-discovery-and-operations` and
`research-session-artifact-view` specs will move unchanged to
`run-bundle-discovery-and-operations` and `run-bundle-artifact-view`. Their
RDO/RSV identifiers remain live and their registry prefix owners change to the
new capability names.

The accepted `research-run-session` and
`research-session-lifecycle-binding` specs will be removed. Every RUS/RES entry
will remain in the registry, marked `[DEPRECATED]`, and never appear in an active
or accepted requirement header again. Existing valid clauses transfer only to
the owners named in the delta removals: Bundle lifecycle (`DRH-*`), Event Journal
(`REJ-*`), Run Experience (`RER-*`), worker failure classification (`WFC-001`),
workflow outcomes (`WFO-001`), and the renamed RDO/RSV capabilities.

Alternative considered: keep empty old specs or aliases. Those would leave
positive capability paths for mechanisms that no longer exist and obscure the
single owner mapping.

### Treat observation and structural negatives as retained behavioral evidence

Tests and evidence metadata that cite RUS/RES will be reassigned to the actual
current requirement owner, not discarded merely because the former capability is
retired. A planted import/path violation and a planted Journal-control-method
violation will continue to prove respectively that deleted surfaces cannot return
and that observation cannot become lifecycle control. `PRS-006` owns removal of
the old broker/index structural root, and `RUI-003` owns the complementary rule
that trusted scope/checkpoint namespaces cannot become identity, an index, or a
recovery source. Requirement registry and main-spec source tests will also carry
known-invalid/orphan or duplicate-owner fixtures where their existing checkers
support them.

Alternative considered: rely on strict OpenSpec validation alone. It validates
artifact shape but cannot prove that a removed runtime surface stays removed or
that evidence annotations point to the new owner.

## Risks / Trade-offs

- [Admission result could be projected differently by the workbench] -> Add a
  red-before-green test that blocks the wrapper and asserts the existing typed
  workbench projection for pending response, conflict/replay, text-bearing
  refinement, and Bundle-loss paths.
- [Retiring a capability could orphan an ID or leave a stale evidence claim] ->
  Inventory every RUS/RES and session-named capability reference, migrate it to
  its named owner, mark retired IDs in the registry, and run requirement/spec/
  coverage governance checks with planted invalid controls.
- [A retained Journal or artifact record could be mistaken for recovery] -> Keep
  Bundle-loss and observation-separation tests; prove no Journal control surface
  and no session/binding module can reappear.
- [A broad compatibility edit could expand into data or host migration] -> Limit
  edits to the downstream harness and OpenSpec/governance/evidence paths named by
  this change; no historical data reader, external API, or DeerFlow source is
  admitted.

## Migration Plan

1. Add focused failing handoff and removed-surface evidence before changing
   production code or accepted specs.
2. Migrate the workbench and focused direct callers, then remove the wrapper and
   make the focused runtime suite pass.
3. Move RDO/RSV specs to their Bundle names; retire the obsolete RUS/RES specs;
   update registry, `@impl`, evidence, and governance mappings as one atomic
   owner migration.
4. Run focused runtime and governance checks, then the full deterministic gate.
   Before archive, inspect the selected diff and gitlink evidence required by the
   repository task policy.

Rollback is a normal source/spec revert before archive. There is no persisted-data
or external-client migration to reverse, and no retained record is modified by this
change.
