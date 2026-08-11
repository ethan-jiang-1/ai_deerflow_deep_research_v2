## Context

See `proposal.md` for motivation and the delta specs for the changed requirements.
The current implementation has one logical policy registry but two physical policy
homes: nine documents beneath the Charter tree and `control-placement` under
`openspec/policies/`. `check_agent_charter.py`, its focused contract test, the
structure registry, and active navigation documents encode the old paths.

`project-structure` currently declares `PRS-009` in its main-spec header, but its
current main-spec body lacks the requirement block. The archived delta contains the
historical requirement, whose old tree cannot be copied forward because this change
replaces that topology.

## Goals / Non-Goals

**Goals:**

- Create one visible Charter entry, one complete policy library, one executable
  guardrail boundary, and one deterministic governance mechanism surface under
  `openspec/`.
- Preserve the existing policy names, triggers, review records, closed postures,
  Focus Card requirements, and non-authority boundaries during the move.
- Make active links, structural inventory, checker registry, and focused evidence agree
  on the same canonical paths.
- Replace stale deferred-V2 wording with the current closeout-evidence boundary.

**Non-Goals:**

- Alter a runtime owner, lifecycle route, permission, state schema, policy applicability
  inference, or semantic review decision.
- Fix `selected_change_closeout.py`, create an archive wrapper, or turn operation
  guidance into a guardrail executor.
- Rewrite historical archive/closed-plan path references, add compatibility copies, or
  change root upstream instructions.

## Decisions

### 1. Use four top-level OpenSpec responsibilities

The target tree is deliberately shallow:

```text
openspec/
  agent-charter/{README.md,charter.md}
  policies/{README.md,<nine Charter-routed policies>,control-placement.md}
  guardrails/{README.md,selected_change_closeout.py}
  governance/{registry,structure authority,checkers}
```

The Charter remains the only selection/routing authority. `policies/` is the only
prose library. `guardrails/` contains executable bounded-evidence contracts; it does
not acquire policy prose merely to increase its file count. `governance/` retains
deterministic validation and inventories, not Charter/policy semantics.

Rejected alternative: move only `agent-charter/` to `openspec/` while retaining an
`agent-charter/policies/` child. It reduces one path segment but preserves the split
policy home and hides most policy documents from the OpenSpec root.

### 2. Move canonical documents without compatibility copies

Apply uses `git mv` for the two Charter documents and nine policy documents. The old
`openspec/governance/agent-charter/` and nested `policies/` directories disappear once
empty. No redirect Markdown files, symlinks, or duplicate canonical documents remain.

Rejected alternative: retain old link shims. They would make two paths appear
canonical, weaken the structure check, and keep authoring context ambiguous.

### 3. Keep one policy registry and categorize it in the index

`check_agent_charter.py` continues to have one `POLICY_REGISTRY`, now resolving every
document under `openspec/policies/`. The Charter index links every entry through the
new relative path. The policy-library README groups existing names as
Charter-routed design/admission guidance or cross-cutting review guidance; the latter
contains `control-placement` only for now.

The category is navigation metadata. It does not add policy inference or alter the
existing special `control-placement` record checks.

Rejected alternative: retain “external policy” as a separate type. Its current sole
member is selected by the same Charter, registry, Focus Card, and checker, so the
label describes layout history rather than a real authority boundary.

### 4. Repair terminology without expanding guardrail semantics

The DRC delta describes selected-change closeout evidence as an already delivered,
caller-declared, Git-verified, non-authoritative capability. It removes statements
that `add-cross-session-cognitive-guardrails` remains deferred, while preserving the
explicit absence of a semantic evaluator, automatic task writer, archive coordinator,
or archive blocker.

`control-placement` keeps its trigger, four closed postures, review table, and
conditional task/guidance integration. The separate SCC change owns output containment,
unchecked-task parsing, command documentation, and command tests.

### 5. Restore PRS-009 with the replacement topology

The project-structure delta adds the `PRS-009` requirement block because no current
main-spec block exists to modify. It is a restoration of a header-declared approved
identity, with the new canonical paths as its current behavior. It does not resurrect
the archive's obsolete `openspec/governance/agent-charter/` tree.

The exact paths remain only in `project-structure.toml`; prose specs state the
relationship and no-duplicate constraint, not a competing full inventory.

### 6. Prove migration at the checker boundary before broad verification

First update the focused contract fixture and checker expectations so a fixture with
only the legacy topology fails and the new topology passes. Then update current
authoring/documentation pointers, run the focused checker/test, run governance gates,
and finally run `UV_OFFLINE=1 make verify`.

Rejected alternative: use a broad path replacement followed only by full verification.
It gives poor failure localization for relative links, registry entries, and fixture
expectations.

## Risks / Trade-offs

- [A stale current link reaches the deleted tree] -> Search active non-archive material
  for both old path prefixes and include the focused route test before broad checks.
- [Moving prose silently changes policy semantics] -> Compare moved file content apart
  from deliberately scoped path/terminology edits; preserve canonical names and record
  schemas.
- [PRS-009 is treated as a new arbitrary requirement] -> Record its header/body drift in
  the design and use its existing ID/capability rather than minting a new requirement.
- [The policy index becomes a duplicate Charter] -> Put selection principles only in
  `agent-charter/README.md`; the library index lists category, trigger, and link only.
- [Guardrails becomes a miscellaneous directory] -> Enforce the command/evidence-only
  boundary in both its README and the change exclusions.

## Migration Plan

1. Land the modified delta specs and focused contract expectations.
2. Move the Charter and policy files, then update the single checker registry and
   structure inventory before any current reader links.
3. Update all active links and terminology, including `openspec/config.yaml` and
   downstream entry documents.
4. Verify the old tree is absent, active references use only the new paths, and no
   archive/closed-plan records were changed for path modernization.
5. Run focused and full deterministic verification; archive only after strict OpenSpec
   validation and scoped diff review.

Rollback before archive is a normal Git revert of the atomic migration commit. There
is no persistent data migration or runtime rollout.
