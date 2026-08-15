## Why

Deep Research currently spreads its OpenSpec-specific guidance and governance support
across four peer extension roots whose names do not reveal their authority: the
guidance-only Charter and policy library are split, the `guardrails/` name overstates a
non-authoritative evidence command, and the mechanically enforced governance root is
not distinguished from either. The structure registry also fails to reject an
unregistered `agent-charter/concepts.md`, so the documented exact topology can drift
while the current checkers remain green.

This change makes the smallest durable cutover: preserve OpenSpec's native
`config.yaml`, `specs/`, and `changes/` surfaces, while reducing the four project
extension roots to one `change-guidance/` authoring route and one `governance/` root
with exact, planted-violation-tested membership.

## What Changes

- **BREAKING**: replace `openspec/agent-charter/` and `openspec/policies/` with one
  `openspec/change-guidance/` tree. Its `README.md` becomes the sole policy route,
  `charter.md` becomes `principles.md`, `concepts.md` becomes `node-edit-map.md`, and
  all ten canonical policies move beneath `change-guidance/policies/` without changing
  their canonical names, triggers, review schemas, or guidance-only authority.
- **BREAKING**: move the selected-change closeout command from
  `openspec/guardrails/` to `openspec/governance/closeout-evidence/` and rename its
  contained persisted-output root from `guardrail-evidence/` to
  `closeout-evidence/`. Preserve its attestation, task-reference, stdout, exit-code,
  containment, non-authority, and native archive boundaries.
- Retire all three former extension roots without symlinks, duplicate canonical
  copies, redirects, or compatibility directories. Archived changes and completed
  backlog records keep their historical paths.
- Rename the Charter checker and focused contract test to change-guidance names, keep
  current callers and evidence selectors synchronized, and make the checker reject
  unregistered guidance files, missing or extra policies, a second policy index,
  legacy-only trees, and duplicate trees through planted negative fixtures.
- Add a short `openspec/README.md` that distinguishes OpenSpec-native workflow files,
  change guidance, and project governance. Update current authoring pointers and the
  checker-rendered Harness structure locator without expanding root agent guidance.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `project-structure`: PRS-009 moves the canonical Deep Research OpenSpec extension
  topology to `change-guidance/` and `governance/closeout-evidence/`, requires exact
  enumerable membership, and retires the three old roots.
- `deep-research-agent-charter`: DRC-001, DRC-005, DRC-006, DRC-009, and DRC-010 adopt
  the human-facing Change Guidance route and relocated closeout command while
  preserving policy names, admission fields, review records, and non-authority
  boundaries. The capability slug and DRC requirement IDs remain stable.
- `selected-change-closeout-evidence`: SCC-002 changes only the canonical command and
  contained persisted-output paths while retaining the existing evidence behavior and
  native-operation boundary.

## Impact

- Current paths and consumers: the OpenSpec config and context, governance registry and
  checkers, three main capability specs through their deltas, Harness entry documents
  and Makefile, focused governance/closeout and node-language tests, and
  requirement/evidence selector metadata.
- Migration scope: 25 current tracked files matched the pre-change residual scan. A
  follow-on symbolic-path scan also found the node-language contract's constructed
  `agent-charter` / `concepts.md` consumer; it is included in the synchronization and
  focused verification tasks. The 127 matching archived-change and completed-backlog
  files are historical evidence and are explicitly excluded from rewriting.
- Compatibility: repository-internal path contracts receive one coordinated clean
  break. No active change currently contains persisted `guardrail-evidence/`; if that
  fact changes before physical cutover, implementation must stop and add an explicit
  consumer/data migration rather than silently deleting or stranding evidence.
- No runtime behavior, public API, package dependency, database, root `AGENTS.md`, root
  `CLAUDE.md`, or DeerFlow gitlink/source change. Ordinary downstream work neither
  modifies nor source-browses `deerflow/`.

## Change Focus

- **Primary module / causal owner:** `project-structure` capability; it owns the canonical OpenSpec extension topology, exact structural enumeration, synchronization protocol, and retirement of superseded paths.
- **Seam classification:** wiring because the change relocates repository-owned authoring, checker, and evidence-command entry surfaces while preserving their semantic owners and runtime behavior.
- **Question:** Can the four ambiguous project extension roots become one guidance route and one governance root, with exact deterministic membership and no second authority or compatibility tree?
- **Necessary adjacent/external contracts:** `deep-research-agent-charter` answers whether the authoring route, policy links, human-facing terms, Focus Card, review schemas, and guidance-only authority remain intact after relocation; `selected-change-closeout-evidence` answers whether the command and contained output path can move while all other I/O, task-led evidence, exit-code, containment, non-authority, and native archive contracts remain intact; `deep_research_harness/tests/assets/evidence.py` and `requirement_evidence.py` answer whether renamed canonical test nodes remain collected and mapped without changing evaluation-hardening semantics. No DeerFlow interface is required.
- **Evidence seam:** direct project-structure and change-guidance checker fixtures with planted missing, extra, duplicate, and legacy trees; selected-change closeout contract tests for the new command/output root and escape rejection; the node-language contract for the renamed node-edit map; verification-gate and test-asset contract tests for renamed commands and node IDs; final strict OpenSpec validation, current-path residual classification, historical diff audit, and `UV_OFFLINE=1 make verify`.
- **Not in scope:** renaming the `deep-research-agent-charter` capability slug or DRC IDs; changing policy triggers, Focus Card fields, review table schemas, or posture values; changing closeout dispositions, attestation schema, Git verification, task or archive authority; modifying runtime code, root agent guides, archived artifacts, completed backlog records, or any DeerFlow source or gitlink pointer.
- **Triggered review policies:** local-context, authority-and-projections, change-admission, agent-information-map, control-placement

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Canonical membership of the Change Guidance and governance-support trees | A contributor may propose files or paths, but prose and filesystem presence cannot declare themselves canonical. | The active `project-structure` delta owns pending topology; `project-structure.toml` enumerates it and the architecture/change-guidance checkers evaluate the checked-out tree. | non-bypassable | Missing, extra, duplicate, or legacy-only members fail; archive cannot treat a partial migration as the canonical topology. | Reuses the existing registry and checker lifecycle while removing two routing roots and the undetected-extra-member gap. | Planted missing, extra, duplicate, and legacy-tree fixtures must fail, and the restored exact target tree must pass. |
| Persisted selected-change closeout-evidence destination | The caller declares an attestation, disposition, task references or limitation, and requested output; none can authorize its own acceptance or archive. | `selected_change_closeout.py` re-verifies Git and task facts, validates the payload, and admits writes only beneath the selected active change's dedicated `closeout-evidence/` root. | non-bypassable | A request outside the new contained root, a stale receipt, or an invalid boundary writes nothing and cannot modify tasks or native OpenSpec state. | Reuses the existing command, payload, and containment evaluator while retiring the misleading `guardrails/` route and old output-root name. | Focused contract tests prove the new contained write, old-root non-creation, escape rejection, re-verification, and absence of task/archive side effects. |
