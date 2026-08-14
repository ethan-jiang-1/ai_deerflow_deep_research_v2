## Context

See [proposal.md](proposal.md) for motivation and scope. Today, the demo transport
can bind without a graph executor; `BundleControl` then writes `all_real` as a
fallback. Bundle State accepts a missing implementation mode with the same default,
while the domain profile/checkpoint path retains absent-schema/v1 compatibility and
two duplicate parser conveniences. These are distinct facts with distinct owners:
the executor supplies composition, Bundle State records accepted lifecycle truth,
the profile parser proposes a candidate, and HITL1 alone accepts profile/proposal
facts into the selected Bundle.

The Owner packet authorizes a clean cutover. Source-controlled current fixtures and
writers are the supported input inventory. No private/external Bundle, profile,
proposal, or checkpoint payload is thereby presumed absent or migrated; it is
unsupported and rejected. The emergency rollback boundary is reader restoration,
not payload mutation.

## Goals / Non-Goals

**Goals:**

- Make graph-backed executor composition the sole source of a demo Bundle's persisted
  mode and route the zero-credential CLI/TUI through the existing fixture graph.
- Close the State enum and reader so a supported persisted State has an explicit
  `fixture`, `mixed`, or `all_real` composition fact.
- Define a source-controlled current matrix for profile content and HITL1
  proposal/checkpoint values, then remove old/missing-schema readers, duplicate
  helpers, and the two clean-cutover Python exports.
- Preserve existing graph ownership, current refinement compatibility, explicit
  mixed fixtures, and zero-write/fail-closed behavior under unsupported input.

**Non-Goals:**

- No no-graph simulator, public mode selector, new public Python facade, external
  input support, data migration, or acceptance of private retained data.
- No graph topology, model/tool/provider behavior, semantic-provider quality,
  human-control vocabulary, evaluation runtime/review semantics, root export, or
  DeerFlow source/API change.

## Decisions

### 1. Only a trusted graph executor supplies initial composition truth

`BundleControl` start admission will require its graph executor to obtain the
implementation mode. A missing executor is an early bounded admission/start failure;
it cannot allocate State with `all_real`, reproject a synthetic completion, or fall
through to the old demo path. `BundleGraphExecutor` continues to derive the mode from
the chosen `ResearchGraphRecipe`, and that mode is the sole State writer input.

The zero-credential CLI and TUI will construct the already-existing fixture recipe
and executor through the demo composition boundary. The implementation preserves the
fixed public all-real route and explicit mixed test seam. This reuses one composition
contract instead of carrying an honest-but-parallel simulator contract.

### 2. Bundle State is a clean persisted-schema cutover

The current State schema will be advanced as needed to make `implementation_mode`
required and restrict it to `fixture`, `mixed`, and `all_real`. State validation and
deserialization reject a missing, `full_fake`, or unknown mode before a lifecycle,
inspection, or review consumer gets a projection. A rejection is read-only: it does
not backfill a field, select `all_real`, rewrite a version, or create a terminal
result.

This is intentionally not a migration. The authorized support inventory is the
source-controlled current State writer and fixtures, which will be updated atomically.
Any retained input outside that inventory is denied. Emergency rollback restores the
former reader as one code change; it does not transform rejected State and does not
reopen support after this change archives.

### 3. Remove the no-graph and duplicate constructor surfaces together

`DemoLifecycleTransport.bind_full_fake()` and every command/documentation route that
depends on it are removed. `ResearchGraphRecipe.all_real()` remains the one
application-internal production factory; generic explicit composition remains
`from_adapters()`. `ResearchGraphRecipe.create()` is deleted without a deprecation
window because the authorized Python support boundary contains no third-party
consumer. Tests that merely assert the alias shape will instead protect the absence
of caller-selectable production composition.

The fixture package continues to import only the generic composition seam. This
prevents the credential-free demo cutover from giving fixtures runtime/controller or
production authority.

### 4. Separate raw human text from versioned retained input

The canonical `parse_profile_input()` continues to convert a bounded raw human reply
into `ProfileParseResult`. That result is a candidate, never a checkpoint/proposal or
lifecycle fact. It is not a persisted compatibility reader and should not be made
less expressive merely because retained input support closes.

Before target edits, the profile-proposal workstream creates one matrix with these
rows and no implied rows:

| Family | Supported current writer/reader | Rejected input | Owner of acceptance | No-write proof |
| --- | --- | --- | --- | --- |
| Bundle State composition | current graph executor and Bundle State codec | absent, `full_fake`, unknown, or old schema/mode | Bundle State codec before lifecycle projection | decode/reload leaves payload and State store unchanged |
| Profile content | current versioned request-bundle profile writer/reader | absent/legacy version or external shape | request-bundle reader before HITL1 consumer | no `profile_ref`, profile facts, or content rewrite |
| HITL1 pending/proposed profile | current versioned HITL1 writer/reader | absent-schema, legacy version, alias, or malformed shape | HITL1 before State reducer/write | no proposal/control/continuation mutation |
| Raw semantic reply | `parse_profile_input()` result | invalid/extra JSON or unrecognized candidate as already specified | HITL1 interaction admission | existing candidate/visible-control behavior remains |

The exact current schema constants and fields are recovered from source-owned codecs
and their deterministic tests during apply, then the matrix is committed as change
evidence. Its clean-cutover addendum records the tracked consumers, no-supported-doc/
root-facade evidence, denial form, migration target, emergency rollback boundary, and
review/removal trigger for each removed Python surface. No local ignored sample
contributes a supported row.

### 5. Canonical parser/result replaces compatibility helpers

The profile domain retains `parse_profile_input()` and `ProfileParseResult` as the
single parsing/result contract. `parse_profile_response()` is removed after all
tracked test consumers read `.partial` or the complete result deliberately. The
redundant legacy profile helper and v1/default reader paths are removed only after the
matrix proves source-controlled writers/fixtures are v2/current and negative tests
cover rejected old shapes.

Evaluation's one parser-wrapper test changes only its test seam. It neither imports
an evaluation facade nor changes any Case, Bundle, Review Record, evidence layer, or
quality claim.

## Risks / Trade-offs

- [Rejected retained State may be useful to an operator] -> It is explicitly
  unsupported rather than misrepresented. Restore the reader only for an emergency
  rollback; create a later inventory-led change before offering migration/support.
- [Fixture graph is slower/more detailed than full-fake presentation] -> The approved
  zero-credential product route is graph proof. Keep it deterministic and use the
  fixture final-delivery fact/trace, never a simulated research-completed claim.
- [A direct module import may exist outside the repository] -> The Owner packet
  authorizes clean cutover. Retain no alias; document migration targets and make
  removed-surface/import failure deterministic.
- [Closing default readers could accidentally reject a current writer] -> Add red
  source-controlled writer/reader round-trip tests before deletion, and require the
  matrix plus reader-to-HITL1/State no-write tests before cleanup.
- [A test-only migration broadens evaluation scope] -> Limit it to the current parser
  assertion; evaluation runtime, review, and evidence contracts are explicit
  exclusions and remain covered by their existing tests.

## Migration Plan

1. Re-read the Program and Workstream Focus records, the owner packet, current specs,
   sources, and tests. Produce the source-controlled schema/consumer matrix and add a
   task for any newly discovered in-scope discrepancy before changing targets.
2. Add red deterministic tests for no-executor start, no full-fake route/import,
   explicit recipe mode persistence, State/profile/proposal input rejection, and the
   canonical parser result. Keep a known current writer round-trip for every supported
   matrix row.
3. Migrate demo CLI/TUI to the fixture graph and remove no-graph binding/routes.
   Require executor-backed State admission, close the State mode schema, remove the
   constructor alias, and update current docs/specs/tests in the same workstream.
4. Move parser consumers to `ProfileParseResult`, delete duplicate/legacy helpers,
   close v1/missing-schema profile/proposal readers, and prove rejected data cannot
   mutate HITL1/State or generate visible completion/control facts.
5. Run focused suites, then the complete deterministic verification, governance,
   strict OpenSpec, and git/submodule checks. A failure is repaired only in its owner
   scope or rolled back under the Program Focus. No workstream archives separately.

## Open Questions

None. The Owner packet chose the fixture-graph target, clean Python cutovers, the
supported source-controlled input scope, rejection posture, and rollback boundary.
