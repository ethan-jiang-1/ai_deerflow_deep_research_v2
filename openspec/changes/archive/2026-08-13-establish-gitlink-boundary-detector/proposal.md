## Why

The repository currently records the `deerflow/` gitlink pointer and nested-worktree
status as manual closeout evidence. That evidence does not make a later unapproved
pointer change, a replacement of the gitlink with an ordinary directory, or nested
worktree dirtiness fail deterministically. The `project-structure` governance boundary
is the smallest existing owner that can protect this repository-level fact without
reading or modifying DeerFlow source.

## What Changes

- Add a `project-structure` requirement for a deterministic, read-only validation of
  the root `deerflow/` gitlink and its declared pinned commit.
- Extend the structure registry with one exact `[upstream_gitlink]` path/commit lock,
  then extend the full `check_project_architecture.py` path to validate only root and
  nested Git metadata: gitlink mode, committed pointer, index/worktree pointer drift,
  nested-worktree cleanliness, and metadata-command failures.
- Add focused temporary-Git-metadata fixtures for the passing boundary and each closed
  rejection: absent or non-gitlink path, malformed registry entry, pointer mismatch,
  failed metadata query, uncommitted pointer drift, and dirty nested worktree. Tests
  also assert the fixed read-only Git command vectors at the evaluator seam.
- Define intentional upstream bumps as an explicit reviewed update of both the root
  gitlink pointer and its registry lock within a dedicated owning change. The checker
  verifies that declaration; it does not authorize an upstream bump or prove runtime
  compatibility.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `project-structure`: Architecture governance will mechanically validate the declared
  upstream gitlink boundary through Git metadata only.

## Impact

- Affected governance surfaces: `openspec/governance/project-structure.toml`,
  `openspec/governance/check_project_architecture.py`, the requirement registry,
  corresponding architecture-governance documentation, and the narrow archive-evidence
  wording in `openspec/config.yaml`.
- Affected deterministic evidence: focused architecture contract fixtures and the
  existing project-structure requirement-evidence registration.
- No Deep Research runtime, public API, graph, dependency, or DeerFlow source changes.
- `deerflow/` remains an upstream gitlink. The detector may execute Git metadata
  queries rooted at that path but MUST NOT read tracked source files, write to it,
  initialize it, change its checkout, or inspect its implementation.
- The existing `--imports-only` architecture-checker mode will retain static manifest
  parsing but will not query the gitlink; only the full architecture-governance path
  owns the mechanical gitlink check.
- Archive-time Git observations remain supplementary scope/diff evidence. Once this
  change is applied, their authoring guidance must not imply that full architecture
  governance lacks the new metadata-only detector or that the detector establishes
  compatibility.

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_project_architecture.py`;
  it is the existing deterministic evaluator for the exact repository structure
  registry, so it owns checking the new registry fact rather than the Harness runtime
  or closeout-evidence helper.
- **Seam classification:** deterministic-guardrail - the change compares declared and
  observed Git metadata before architecture governance reports success, with no model,
  human-input, graph, or runtime authority.
- **Question:** Can full repository architecture governance fail closed when the
  declared `deerflow/` gitlink is absent, not a gitlink, at a different committed SHA,
  modified relative to the root index, backed by a dirty nested worktree, or
  uninspectable through the defined Git metadata command?
- **Necessary adjacent/external contracts:** Git CLI metadata for the repository root and
  the `deerflow/` nested worktree, solely to obtain mode, commit identity, diff state,
  and porcelain cleanliness; no DeerFlow source interface is admitted.
- **Evidence seam:** `deep_research_harness/tests/contract/test_architecture_governance.py`
  creates tiny temporary parent/nested Git metadata fixtures and calls the existing
  checker seam directly; the live repository checker remains the integration proof.
- **Not in scope:** DeerFlow source inspection or modification; Gitlink bump authorization;
  runtime compatibility testing; native OpenSpec archive behavior; generic submodule
  management; a new closeout command; changes to application Python, tests outside the
  focused governance/evidence surfaces, or `deerflow/` itself.
- **Triggered review policies:** change-admission, control-and-recovery, control-placement

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| The root gitlink mode, declared SHA, index/worktree pointer state, and nested cleanliness | A reviewer may approve an intentional upstream bump outside the checker; no cognitive or human value is consumed at validation time | `project-structure.toml` declares one lock; `check_project_architecture.py` compares it with root/nested Git metadata | non-bypassable | A nonmatching, moved, missing, or dirty boundary rejects architecture governance; correction is an explicit reviewed change, never an automatic reset or checkout | Reuses the existing architecture registry, checker CLI, and temporary-fixture contract seam instead of adding an archive controller or a second upstream scanner | Focused temporary Git fixtures for each rejection plus the existing live architecture-governance test |
