## Context

At the current HEAD, the local `.github/` workflows and `.agents/skills/` tree match
the last tracked revision byte-for-byte but are ignored and absent from the Git index.
An isolated clean clone therefore lacks both the deterministic workflow and the
`polish-openspec-change` lifecycle skill; its existing workflow contract fails before
it can evaluate workflow content. The Repository Governance Owner has approved the
repository-tracked route, not a versioned external installer.

The program's five workstreams come from the audited Candidate map. Delivery is a
prerequisite because the other four subtract local repository assets and must not be
validated through the machine-local residue that hides the delivery failure.

## Goals / Non-Goals

**Goals:**

- Make the existing deterministic CI, manual-live isolation, and OpenSpec lifecycle
  discoverable from a clean clone through one tracked repository route.
- Add a falsifiable trackedness guard under the existing deterministic CI delivery
  requirement and make the structural registry enumerate the actual delivery and test
  paths.
- Retire only the audited markers, scaffold, report/test pair, demo helpers/tests,
  and planner helper/export after each owning seam retains its distinct behavior.
- Preserve current deterministic, manual-live, suspended, evidence, entry, and
  profile-projection contracts throughout the whole program.

**Non-Goals:**

- Do not create an external installer, alter workflow trigger scope or credentials,
  run manual-live CI, or make any live/release claim.
- Do not change public APIs, persisted records, profile schemas, planner output,
  canonical demo behavior, or DeerFlow code.
- Do not split the program, archive a completed workstream independently, or use an
  ignored local artifact as a compatibility fallback.

## Decisions

### Restore one repository-owned delivery route

Restore the two historical workflow definitions and the exact project skill tree as
tracked files, remove their broad root ignore rules, and retain `.openspec-target` as
the sole declared `codex` target. The deterministic workflow remains the existing
canonical `make verify` plus duration-policy route; the credentialed workflow remains
`workflow_dispatch` only. This reuses accepted commands and lifecycle artifacts rather
than creating an installer, wrapper, or second skill-discovery authority.

The structural registry will enumerate required delivery artifacts, while a focused
repository delivery contract uses the actual Git index and ignore facts to prove those
paths are tracked and not hidden. Its controlled negative case removes tracking,
removes a path, or adds ignore coverage in an isolated fixture and must fail before
availability is claimed.

The bounded clean-clone preflight SHALL make a dedicated temporary index from `HEAD`,
add only an explicit delivery allowlist to that index, and write a short-lived commit
and temporary branch from its tree. A `--no-local` clone of that branch SHALL validate
workflow and skill discovery, then remove the temporary clone, index, branch, and
other preflight state. The allowlist and temporary index keep unrelated staged or
unstaged user work out of the proof and do not modify or consume the user's real Git
index. This is integration evidence only; it is not a claim that remote CI,
credentials, or live evaluation executed.

Alternative considered: a versioned external source. It was rejected by the approved
repository-tracked decision and because no current installer, version, or clean setup
route exists. Alternative considered: relying on a file-presence test. It was rejected
because ignored local files made that test pass while a clean clone failed.

### Keep program ownership and order explicit

| Workstream | Semantic owner | Writer scope | Entry condition | Completion evidence |
| --- | --- | --- | --- | --- |
| delivery | repository-delivery | root ignore, workflow, skill, structural-delivery, and delivery-test surfaces | approved repository-tracked decision | trackedness guard and bounded clean clone |
| test-structure | project-structure | markers, empty scaffold, exact structural row, focused tests | delivery closed | structure, asset, lane, and suspension guards |
| evidence-report | evaluation-hardening | imported workflow report/test and their exact evidence metadata | delivery closed | provenance comparison plus retained evidence checks |
| demo-adapter | demo-adapter | private helper/tests and canonical test additions | delivery closed | focused canonical preflight/profile tests |
| topic-planner | topic-planning | legacy helper/export/test and canonical test additions | delivery closed | focused canonical assignment and negative tests |

Delivery is first. The four subsequent workstreams can repair only within their own
declared writer scope, and none can silently absorb another's candidate or contract.
The program decision authority controls scope, ordering, and archive closure only;
it is not a runtime fact authority or shared code owner.

### Subtract only after behavior and provenance transfer

`test-structure` deletes a marker only after confirming its directory has a real
tracked resident, and removes the empty E2E scaffold with the exact registry entry.
It retains EVH-024, current lane selection, non-empty collection, and registry joins.

`evidence-report` compares the report's historical failure/provenance statements to
the dated baseline, accepted attestation, and current regression-descent policy before
deleting the superseded report and its shape-only test. After that comparison, it
updates the `EVH-005` registry description to name those retained evidence owners
rather than the retired imported workflow report. It never rewrites a frozen record to make removal
appear safe or changes the accepted `EVH-005` requirement.

`demo-adapter` moves the only unique selected-profile and blank-credential cases onto
the canonical profile/preflight APIs before deleting the private wrappers and their
implementation-shape tests. `topic-planner` moves the supported short-state field
coverage to canonical Bundle-profile assignment tests, retaining profile mismatch and
current-refinement generation rejections before removing the legacy helper/export.

Alternative considered: broad source/test cleanup first. It was rejected because the
current helpers, report, and scaffolding have distinct evidence obligations that would
otherwise become unprovable after deletion.

### Recovery remains local until program closure

If delivery fails its guard or clean-clone preflight, no subtraction begins. If a later
workstream fails, restore or forward-repair only that workstream and dependent later
workstreams; delivery remains intact once independently verified. A non-convergent
workstream leaves the program active for plan-level re-scope or whole-program rollback.
No partial archive is legal.

## Risks / Trade-offs

- [Risk] Local ignored artifacts drift before implementation -> Recompare each restored
  file with its historical tracked blob immediately before staging; any mismatch is a
  planning finding, not an opportunity to import local changes.
- [Risk] A delivery test proves only the current checkout -> Pair its planted negative
  fixture with the bounded clean-clone preflight and retain the Git-index assertion.
- [Risk] Removing a shape-only test hides a unique historical fact -> Complete a
  fact-by-fact provenance comparison and preserve the correct historical owner first.
- [Risk] Canonical demo/planner tests omit a legacy-only field -> Add those assertions
  before deletion and retain all existing fail-closed cases.
- [Risk] The manual-live workflow could be mistaken for deterministic CI -> Assert
  manual selection and preserve credential-bounded execution without running it.

## Migration Plan

1. Restore and stage repository delivery artifacts, remove their ignore coverage, add
   structural enumeration and the delivery guard, then run its focused test and a
   clean-clone preflight.
2. Only after delivery passes, execute the four subtraction workstreams in declared
   order, adding behavior/provenance transfer evidence before each deletion.
3. Run each focused suite after its workstream, then the full deterministic and
   governance verification set; record unrun external/manual-live evidence explicitly.
4. On a failed workstream, use its declared forward repair or rollback and retain the
   active program until all 16 budget IDs have closure evidence.
