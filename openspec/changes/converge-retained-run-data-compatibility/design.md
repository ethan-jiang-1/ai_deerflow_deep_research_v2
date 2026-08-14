## Context

This is a persisted-data clean cutover, not a compatibility window. The accepted
contracts currently retain four old-reader surfaces: graph checkpoint
`repair_counts`, Bundle terminal `REPAIR_EXHAUSTED`, Journal v1/v2, and terminal
`RunFailure` without `diagnostic_location`. Their local readers can outlive the
writer that created them. See `proposal.md` for the approved support boundary.

Verified current behavior establishes the implementation starting points:

- `ResearchGraphState`, `ResearchState`, the ownership table, and the rerun planner
  still carry or write `repair_counts`; gate attempt/budget fields are already the
  current repair authority.
- `TerminalReason` still decodes `REPAIR_EXHAUSTED`; Bundle State is the lifecycle
  authority and must not acquire an alternate terminal route.
- Run Observation contracts accept Journal v1/v2/v3, while the runtime marks an old
  manifest incomplete and refuses append; Journal writers already emit v3 and
  `RunSummary` already emits v2.
- `RunFailure` permits a non-provider legacy terminal to omit
  `diagnostic_location`; participant projections consume that typed result.

Ignored demo/report roots are a risk floor only. They are not an inventory and do not
authorize a local, external, host, deployment, or public-result migration.

## Goals / Non-Goals

**Goals:**

- Establish one source-controlled, bounded registration and dry-run route before any
  retained-data subtraction.
- Move the four readers to current-only contracts without a compatibility flag,
  implicit provenance upgrade, synthetic terminal mapping, or alternate lifecycle
  authority.
- Preserve current repair authority, Bundle lifecycle authority, Journal
  non-authority, Summary v2, and exact diagnostic-publication truth.
- Leave deterministic migration, restart/replay, negative-path, and post-cutover
  evidence that can prove the cutover rather than merely report a zero count.

**Non-Goals:**

- Discovering, importing, or supporting unregistered external/ignored data.
- Changing gate policy, route topology, terminal categories, Journal capacity,
  Summary v2, provider recovery, public APIs, or DeerFlow.
- Treating an observation, migration manifest, or participant projection as a
  lifecycle controller or recovery authority.

## Decisions

### 1. Source-controlled inventory is the sole migration admission record

Implementation SHALL add
`deep_research_harness/scripts/retained_run_data_inventory.json` and a local migration
runner beside it. The JSON file is a versioned, source-controlled, fail-closed manifest
with a separate record for each supported source datum. A record carries the family,
source schema, opaque stable identity, whole-input digest, and disposition. A migrate
record also names the exact current output digest; a reject record records no target.
There are no wildcards, directory roots, discovery globbing, host paths, or inferred
records.

The approved initial inventory has zero supported records in every family. This is a
positive data decision, not an inference that ignored/local/external data is absent.
The runner nevertheless validates its manifest and supports planted in-memory/test
records so a future approved inventory must pass the same decoder, digest, and
atomicity checks. The runner is an offline tool: production readers do not load the
inventory and a manifest entry does not grant a runtime compatibility route.

Alternative considered: scan ignored demo/report roots or accept an operator supplied
directory as inventory. Rejected because neither source provides a bounded support
promise, stable identity, integrity evidence, or ownership decision.

### 2. Migration is pre-cutover and family-specific

The runner uses the following fixed reader/writer matrix. `old reader` means only the
offline migration decoder, never the post-cutover runtime reader.

| Family | Old reader / admissible input | Offline disposition | Current runtime reader | Current writer |
| --- | --- | --- | --- | --- |
| Graph checkpoint | registered pre-cutover checkpoint containing `repair_counts` | validate whole record, remove only the retired field, write verified current schema atomically | current schema without `repair_counts`; all old/unregistered inputs reject before graph work | current schema without field |
| Bundle State | registered terminal Bundle with `REPAIR_EXHAUSTED` and sufficient unchanged terminal truth | remove the retired reason only; never map to another reason or terminal status | current Bundle schema without the retired enum; old input rejects before control | current Bundle schema without enum |
| Journal manifest/event | registered complete v2 manifest plus matching event set | validate correlation/sequence; materialize v3 only from retained facts; Summary remains v2 | v3 only; v1 and v2 are unavailable/unsupported observations | v3 manifest/event; Summary v2 |
| Persisted/public terminal result | missing `diagnostic_location` | reject only, even if registered | location required before participant projection | explicit `bundle_journal` only after verified publication, otherwise factual `unavailable` |

Graph and Bundle migration preserve identity, revision/atomicity, terminal status,
and existing typed facts. Journal migration does not infer v3-only response shape,
post-candidate stage, watermark, generation, or validation provenance. A missing
terminal location has no factual input from which either `bundle_journal` or
`unavailable` can be derived, so it has no migration arm.

The Journal row governs only manifest and event records. `RunSummary` v2 remains the
current writer representation, and this change leaves its existing decoder semantics
unchanged. Summary records are not migration-inventory entries, not an old-reader count,
and not a route to admit an old manifest/event record.

Alternative considered: keep a version-dispatching runtime reader. Rejected because it
would leave a second long-lived admission path and make a registered record's
historical support status influence lifecycle execution.

### 3. Cutover separates migration proof from runtime admission

The apply sequence is:

1. Add decoder, manifest validation, dry-run reporting, red-before-green tests, and
   reader/writer matrix evidence while current contracts still exist.
2. Run the dry run against the checked-in zero inventory and all deterministic planted
   records. A non-zero post-validation count, digest mismatch, partial record, or
   failed atomic write blocks subtraction.
3. Remove `repair_counts`, `REPAIR_EXHAUSTED`, Journal v1/v2 runtime readers, and the
   absent-location terminal branch in one dependency-ordered implementation change.
   Writers move to the current contracts in the same change.
4. Run current write/reload/replay tests, negative legacy reads, and post-cutover
   recounts. The only admitted current values are those in the matrix above.

This order prevents a decoder from being removed before registered migration proof and
prevents a partially migrated input from being resumed by an old reader. The graph
reader rejects before graph compilation, the Bundle reader before lifecycle control,
the Journal reader before append/projection, and the terminal reader before participant
projection.

### 4. Recovery is a complete local reader revert, not field repair

Failure detection is a decoder validation/digest/atomic-write failure, a current-reader
legacy input, or a replay/restart mismatch. The Data Owner can approve a complete local
reader hotfix/revert with its paired deterministic tests. That recovery restores the
complete affected current/old reader behavior as one reviewed patch; it does not enable
one legacy field, rewrite source payloads, infer diagnostic provenance, map a terminal
reason, or add a compatibility switch. Until that separately approved patch exists,
the terminal disposition is the bounded rejection at the named local boundary.

Alternative considered: a one-off compatibility flag or payload edit. Rejected because
either would make a partial historical surface an untracked lifecycle/recovery control.

### 5. Current terminal writes make location explicit without fabricating provenance

`RunFailure` validation changes so every current terminal result has a location. A
verified terminal diagnostic publication yields `bundle_journal`; a current terminal
without one yields `unavailable` with no invented reference and
`research_record_created=false`. This is a current writer decision from present typed
facts, distinct from trying to fill a missing location in old retained data.

## Risks / Trade-offs

- [Zero inventory can hide an unsupported record] -> The checked-in zero manifest is
  explicit, every unregistered reader fails closed, and later support requires a new
  approved change rather than a manual manifest edit.
- [A migration can lose or strengthen a fact] -> Whole-input digest, typed decode,
  exact output digest, atomic output, reload, and replay tests are mandatory; Journal
  provenance and terminal mapping are explicitly prohibited.
- [Reader subtraction breaks restart] -> Cover old and migrated/current records at the
  direct reader plus graph/lifecycle/projection handoff; a rejection must happen before
  a mutation or legal recovery action.
- [A rollback reintroduces only one unsafe branch] -> Permit only complete-reader
  hotfix/revert evidence and reject a field-specific flag or manual rewrite.
- [Ignored local data is mistaken for support] -> Keep it outside inventory and use
  its counts only as documented non-authoritative risk evidence.

## Migration Plan

1. Create the strict inventory/runner contract and deterministic fixtures for all four
   families, including empty inventory, unsupported source, digest mismatch, incomplete
   Journal, missing terminal location, and simulated atomic-write failure.
2. Produce and retain a source-owned dry-run report containing per-family registered,
   migrated, rejected, and failed counts plus the old/new reader-writer matrix. Verify
   the approved zero inventory yields zero migrated and zero unaccounted supported
   records.
3. Implement and test the graph and Bundle subtractions first: move graph schema to
   its next version without `repair_counts`, move Bundle State to its next version
   without `REPAIR_EXHAUSTED`, and remove writers, ownership rows, readers, fixtures,
   and positive compatibility tests together.
4. Implement and test Journal and terminal-result subtraction: retain v3/v2 summary,
   remove v1/v2 runtime acceptance, require explicit current terminal location, and
   remove absent-location positive compatibility fixtures.
5. Run restart/replay and post-cutover evidence. The required count is zero for every
   scoped legacy checkpoint, Bundle, and manifest/event runtime reader/writer and every
   supported old inventory record; rejected unregistered data is counted separately and
   never rewritten. Existing Summary decoding is excluded from that count.
6. For an emergency discovered after cutover, stop at the local rejection boundary.
   A Data Owner-approved complete local reader hotfix/revert, including tests and a new
   review record, is the only recovery route.
