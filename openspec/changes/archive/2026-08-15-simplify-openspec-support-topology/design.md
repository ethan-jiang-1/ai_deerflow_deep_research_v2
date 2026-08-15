## Context

See `proposal.md` for motivation and scope. The relevant current architecture has four
project extension roots beside OpenSpec's native `config.yaml`, `specs/`, and
`changes/` surfaces:

- `agent-charter/` and `policies/` are one guidance-only authoring system but expose
  two entry routes;
- `guardrails/` contains a caller-driven closeout-evidence command that does not block
  operations or own archive;
- `governance/` contains the project structure registry, requirement registry, policy
  documents, and deterministic checkers.

`project-structure.toml` is the exact enumerable structure authority, subject to the
active `project-structure` delta and the synchronization protocol in
`architecture-policy.md`. The current registry and main spec omit the existing
`agent-charter/concepts.md`, while both structure and Charter governance pass. This is
a detector-sensitivity defect, not evidence that the extra member is canonical.

The pre-proposal residual scan found 25 current tracked files that refer to affected
paths, names, commands, or test nodes. A follow-on symbolic-path scan found one more
current consumer: the node-language contract constructs the
`agent-charter` / `concepts.md` path and must move to `node-edit-map.md`. Another 127
files under archived changes or completed backlog roots contain historical references.
Before the change scaffold was created, there were no active changes and no persisted
`guardrail-evidence/` data. This change is now the sole active change and does not
contain that directory.

All changed surfaces are repository-owned. No public API, runtime state, database,
external dependency, DeerFlow source, or DeerFlow gitlink pointer participates in the
cutover.

## Goals / Non-Goals

**Goals:**

- Perform one reviewable cutover from four ambiguous project extension roots to one
  Change Guidance route and one governance root.
- Preserve the behavior and authority of canonical policies and selected-change
  closeout evidence while changing their repository paths.
- Make exact Change Guidance and policy membership mechanically enforced and prove
  detector sensitivity with safely planted violations.
- Keep every current caller, registry entry, generated locator, test selector, and
  authoring pointer synchronized with the target topology.
- Retire the old current paths completely while preserving historical records.

**Non-Goals:**

- Rename the `deep-research-agent-charter` capability directory or DRC requirement
  IDs.
- Change Focus Card fields, canonical policy names or triggers, conditional review
  schemas, closed design postures, or operation-guidance authority.
- Change closeout attestation, dispositions, Git verification, task ownership, exit
  behavior, semantic-review ownership, or native apply/archive behavior.
- Modify product runtime code, root `AGENTS.md`, root `CLAUDE.md`, archived changes,
  completed backlog records, or any DeerFlow content or pointer.

## Decisions

### 1. Use one ordinary change with one structural owner

`project-structure` is the primary causal owner because the accepted decision is the
target topology and retirement set. `deep-research-agent-charter` answers the adjacent
guidance-route and policy-authority question; `selected-change-closeout-evidence`
answers the adjacent command/output compatibility question. Test-evidence registries
are downstream consumers of renamed test nodes, not another semantic owner.

The proposal therefore uses one ordinary Focus Card, not Program Focus. Splitting the
work would duplicate proposal, review, validation, and archive cost and would create an
intermediate topology with no independently useful invariant. Treating all three
capabilities as peer owners was rejected because it would obscure the single
structural decision and overstate unchanged SCC/DRC semantics.

### 2. Converge on two project extension roots

The cutover uses these direct mappings:

| Current | Target |
| --- | --- |
| `agent-charter/README.md` | `change-guidance/README.md` |
| `agent-charter/charter.md` | `change-guidance/principles.md` |
| `agent-charter/concepts.md` | `change-guidance/node-edit-map.md` |
| `policies/*.md` | `change-guidance/policies/*.md` |
| `policies/README.md` | merge unique route content into `change-guidance/README.md`, then retire |
| `guardrails/README.md` | `governance/closeout-evidence/README.md` |
| `guardrails/selected_change_closeout.py` | `governance/closeout-evidence/selected_change_closeout.py` |
| active-change `guardrail-evidence/` | active-change `closeout-evidence/` |
| `check_agent_charter.py` | `check_change_guidance.py` |
| `test_agent_charter_governance.py` | `test_change_guidance_governance.py` |

`openspec/README.md` is added as a small authority-aware navigation map. OpenSpec's
native surfaces do not move. The target adds one root file but retires three top-level
extension roots and one duplicate policy index, so the information architecture has
net negative routing complexity.

### 3. Use a coordinated clean break without compatibility paths

These repository paths are internal cross-boundary contracts with an enumerable
consumer set. The cutover updates every current consumer in the same change, and old
roots are rejected after the target is established. Symlinks, redirects, duplicate
files, and compatibility directories are not allowed because any of them creates a
second canonical route and weakens deletion evidence.

The clean break is authorized only while no active change contains persisted
`guardrail-evidence/` and no new current consumer is found. Apply must repeat both
checks immediately before physical migration. If either fact changes, the cutover
stops before moving or deleting the old surface; the proposal/design must be revised
with an explicit consumer or data migration. Silently dropping, copying, or inferring
ownership for unplanned evidence is not allowed.

### 4. Preserve semantic authorities while relocating their surfaces

| Surface | Authority after cutover | Preserved boundary |
| --- | --- | --- |
| Approved behavior | main specs plus this active delta until archive | Guidance does not create behavior |
| Exact topology | `project-structure.toml`, governed by `project-structure` | Root README and generated locator are projections |
| Policy applicability and review shape | Change Guidance route plus DRC contract/checker | Policies do not create runtime or archive authority |
| Closeout record acceptance | selected-change closeout command under governance | Caller declarations do not self-authorize; records remain non-authoritative |
| Native apply/archive | OpenSpec operation | Guidance and closeout evidence neither execute nor block it |
| Test selection/evidence metadata | existing test-owned registries and collector | Renamed selectors do not change evidence semantics |

Policy files move as one rename-aware set. Content changes are limited to relative
links, route terminology, and relocated command pointers; canonical policy names,
triggers, Focus Card fields, table schemas, posture values, and non-authority text are
compared before and after migration.

### 5. Make the Change Guidance checker exact and self-proving

The renamed checker keeps the existing proposal grammar and entry-document budgets.
Its policy registry points to `change-guidance/policies/`, and the canonical route
links are relative to `change-guidance/README.md`. It adds two explicit membership
checks:

1. the guidance root member set equals `README.md`, `principles.md`,
   `node-edit-map.md`, and `policies/`;
2. the policy directory file set equals the ten Markdown paths derived from the
   existing canonical policy registry.

The checker independently rejects all retired roots and any duplicate canonical tree.
It does not scan archived changes. Focused fixtures plant and then remove at least an
extra guidance file, an extra policy, a missing policy, a second policy index, a
legacy-only tree, and a duplicate tree. Each planted state must fail with a bounded
contract code, and the exact restored target must pass. This closes the current
presence-only gap without adding another registry.

### 6. Relocate closeout evidence without changing its protocol

The command file and README move together. The only code constant changed inside the
command is the dedicated persisted-output directory name. Validation still resolves
the selected active change, re-verifies the caller-supplied attestation immediately
before a write, checks current unchecked task labels, and returns structured domain
results with the existing process-exit behavior.

Focused tests first point to the target command and `closeout-evidence/` root, creating
the required red state. Green evidence must prove one valid contained write; no old
directory creation; rejection of the old root, `tasks.md`, and an outside path; stale
receipt re-verification; and absence of task or native archive effects. A wrapper or
fallback command at the old path was rejected because it would retain the misleading
surface and double the command contract.

### 7. Synchronize current projections from their owners

Current references are updated by ownership category rather than by global string
replacement:

- the three delta specs own pending behavior;
- `project-structure.toml` owns exact paths;
- `req-registry.yaml` keeps stable IDs/slugs while updating current human-facing
  descriptions where needed;
- `config.yaml`, `openspec/CONTEXT.md`, the new root README, governance README, policy
  links, and Harness entry documents are current navigation;
- Makefile, verification-gate tests, focused governance/closeout and node-language
  contract tests, and test/evidence registries are executable consumers.

After the structure registry changes, the architecture checker renders the bounded
`deep_research_harness/AGENTS.md` structure block. Apply replaces only the content
between its declared generated markers, records whether the render is an exact no-op,
and then runs full architecture governance. Human-authored text outside the markers is
not regenerated.

Archived changes and `_backlog/_done/` are excluded from current-path rewriting. The
active plan and change artifacts may describe retired paths as migration evidence;
those references are classified rather than forced to zero.

## Risks / Trade-offs

- [One change touches three capability contracts and many path consumers] -> Keep one
  primary owner, group tasks by detector, physical cutover, synchronization, and
  closure, and review the diff by contract before archive.
- [A newly created or symbolically constructed current consumer, or old evidence
  directory, is missed] -> Repeat the tracked-current residual and symbolic-path
  scans plus the active-data scan immediately before cutover; stop and revise migration
  design on any unclassified result.
- [A rename changes policy meaning] -> Compare canonical names, triggers, Focus Card
  grammar, review schemas, postures, and authority statements, allowing only route
  links and current human terminology to differ.
- [Presence checks still miss topology drift] -> Require exact-set comparison and a
  known extra-member failure before accepting the restored-tree pass.
- [Renamed test nodes silently lose requirement evidence] -> Update both evidence
  registries and run collection-aware asset checks plus the verification-gate contract.
- [A global replacement rewrites history] -> Restrict edits to current inventory and
  audit archive/completed-backlog diffs separately.
- [Partial work is mistaken for the accepted topology] -> Do not archive or retain a
  compatibility tree while any target gate, residual classification, or task remains
  incomplete.

## Migration Plan

1. Reconfirm this is the sole active change, scan all active changes for
   `guardrail-evidence/`, run the task-defined tracked-current residual query and
   the symbolic `agent-charter` / `concepts.md` path scan, classify every result,
   and record DeerFlow gitlink/nested-worktree metadata without opening upstream
   source.
2. Change focused topology and closeout fixtures to the final paths and demonstrate
   bounded red failures against the current tree.
3. Move guidance, policies, command/README, checker, and focused test through
   rename-aware filesystem operations; merge the policy index into the sole Change
   Guidance route and retire the old roots.
4. Update the command output root, exact-member checker, all current navigation,
   registries, Makefile/evidence selectors, and the three owning contract surfaces.
   Compare each relocated policy with the pre-cutover snapshot before accepting the
   target tree; only route links and current human terminology may differ.
5. Render and verify the bounded Harness `AGENTS.md` structure locator; run focused
   negative/positive tests, including the node-language map consumer, and all five
   governance checkers.
6. Run strict OpenSpec validation, the classified current-path residual audit,
   historical diff audit, submodule metadata checks, `git diff HEAD --check`, and
   `UV_OFFLINE=1 make verify`.
7. Perform the required control-placement plan review and archive-closeout review.
   Only after all ordinary tasks and both review obligations are complete may the
   delta specs be synchronized and the single change archived. Re-run main-spec,
   residual, and full verification gates after archive before closing the plan.

Before archive, all effects are reversible repository edits. On a failed task, keep
the change active and either repair within the approved scope or restore the complete
affected path/registry/checker group to the last committed baseline; never declare a
mixed topology canonical. If unplanned persisted evidence appears, preserve it in
place and revise the migration rather than moving it implicitly. If a missed current
link is found only after archive, create a focused repair change and do not resurrect
an old canonical copy.
