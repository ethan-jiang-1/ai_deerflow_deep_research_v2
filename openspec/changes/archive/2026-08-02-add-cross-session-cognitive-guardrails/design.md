## Context

See `proposal.md` for motivation and the delta specs for normative behavior. Change
2 established that `operations.apply/archive.guidance` is advisory and that a shared
worktree does not provide a reliable selected-change boundary. This change introduces
one local, deterministic evidence surface under `openspec/guardrails/`; it does not
change a DeerFlow runtime surface or OpenSpec's native archive flow.

## Goals / Non-Goals

**Goals:**

- Verify an explicit, committed Git range before any record names reviewed coverage.
- Make the accepted boundary and a review disposition durable inside the selected
  OpenSpec change without creating a second task ledger.
- Give later sessions a small, machine-readable record they can inspect without
  claiming semantic review quality, fresh-session independence, or archive approval.

**Non-Goals:**

- Infer a range from branch names, changed paths, a merge base, or the entire
  worktree.
- Judge the truth of a review, a finding, a task, or a model output.
- Intercept, wrap, invoke, or block `openspec archive`; modify `backend/`,
  `frontend/`, or any DeerFlow runtime path.

## Decisions

### 1. One standard-library command owns only boundary and record shape

Add `openspec/guardrails/selected_change_closeout.py` with two explicit operations:
`verify-boundary` and `record-review`. It uses Python's standard library plus Git
subprocess calls, so the deterministic tool adds no provider, model, or package
dependency. `openspec/guardrails/README.md` documents the input/output contract and
states that the tool is not an OpenSpec operation hook.

`verify-boundary` consumes one JSON attestation and prints one JSON receipt for
inspection; it never persists the receipt. `record-review` consumes the attestation
again plus a review payload, resolves the declared name to an active change root, and
performs the same Git verification as its final pre-write step. It writes only the
final evidence record when the caller explicitly passes an output path that resolves
below that root; an escaping or unresolved output path is rejected before any file
write. Neither operation edits `tasks.md` or invokes an OpenSpec command.

Rejected alternative: an archive wrapper or a config-defined command. OpenSpec 1.7
does not make operation guidance enforceable, and a wrapper would falsely imply that
direct native archive is prevented.

### 2. Attestation v1 is local, explicit, and reproducible

The v1 attestation is JSON with exactly these required semantic fields:

```json
{
  "change_name": "example-change",
  "repository_identity": "/absolute/canonical/repository/root",
  "base_commit": "<commit>",
  "head_commit": "<commit>"
}
```

The command first resolves `change_name` to an active change root below the current
planning home's `openspec/changes/`; an unknown or archived name is `unknown-change`.
It resolves the supplied repository path with `git rev-parse --show-toplevel` and
requires it to equal the declared canonical root. It resolves both commit objects to
full commit IDs, checks `git merge-base --is-ancestor base head`, requires current
`HEAD` to equal the resolved head, and requires `git status --porcelain` to be empty.
It computes the evidence digest from `git diff --binary base head` and the changed-path
count from the same exact range.

The resulting `boundary-verified` record repeats the canonical change name,
repository identity, resolved commits, literal `base..head` range, changed-path count,
and SHA-256 diff digest. Invalid input yields `missing-boundary` plus closed failure
codes such as `missing-field`, `repository-mismatch`, `unknown-commit`,
`non-ancestor`, `head-drift`, or `dirty-worktree`. A failure result does not include a
diff summary or coverage claim.

Rejected alternative: use a branch name, a path allowlist, or automatic merge-base
discovery. Each can be useful review context but cannot prove that uncommitted or
shared-worktree edits belong to the selected OpenSpec change.

### 3. Evidence records reference ordinary tasks rather than owning findings

`record-review` accepts the same attestation and a review payload. It re-verifies the
attestation immediately before the output write, so a prior `verify-boundary` receipt
is useful for inspection but cannot authorize a later record after HEAD or worktree
state changes. Its only allowed dispositions are:

- `review-required`: requires one or more task references. Each reference is an
  exact unchecked task label (the text after `- [ ]` on its checkbox line) in the
  selected change's `tasks.md`; the command verifies that the matching task exists but
  does not add or complete it.
- `inconclusive`: requires a non-empty `evidence_limitation` and may not claim that
  review passed.

The persisted record nests the boundary receipt and retains the disposition, task
references or limitation, and schema version. It rejects `clear`, `approved`,
`semantic-pass`, arbitrary status strings, and empty required fields. This makes the
record useful to a resumed session while keeping semantic assessment and task authoring
with the reviewing agent and ordinary task ledger.

Rejected alternative: a new finding database or auto-generated checklist. Either
would duplicate `tasks.md`, create stale state, and obscure who owns the correction.

### 4. Persistence is change-local but opt-in

The tool prints JSON to stdout for direct deterministic tests. A caller that needs a
durable cross-session artifact supplies `record-review` with an explicit output path
under `openspec/changes/<change_name>/guardrail-evidence/`; the tool creates only that
requested final record file after the re-verification succeeds. The directory moves
with the selected change on native archive but does not participate in archive control
or spec synchronization.

The record is evidence only. A later invocation must re-verify Git facts before it
can make a new coverage statement; an old receipt cannot remain valid after HEAD or
worktree state changes, including a prior evidence-file write.

Rejected alternative: a central dossier outside the change. It would require separate
retention and identity rules while giving no stronger Git attribution.

### 5. Governance follows the existing lightweight route

Implementation confirms the active-delta `SCC` requirement registration,
synchronizes the charter delta, and registers only the new guardrail documentation,
command, and focused fixtures in the existing governance evidence/structure metadata.
The existing `DRC-010` route changes only to name the separate evidence protocol;
guidance remains advisory.

The focused test suite creates temporary Git repositories with local identity and
commits. It covers the success receipt; unknown-change, missing-field, repository,
commit, ancestry, HEAD, and worktree rejection; task-reference and disposition
validation; output-path containment; stdout versus explicit record write; and proves
that no test path invokes native archive or edits a task file.

## Risks / Trade-offs

- [A committed-only contract adds a closeout step] -> Make it explicit in the route
  and retain `missing-boundary` rather than scanning a convenient but ambiguous tree.
- [Absolute repository identity is not portable across clones] -> Treat it as a
  local evidence receipt; a later clone must issue a new attestation against its own
  Git root and commits.
- [Task text can change after a record is written] -> Re-verify task references when
  creating each record; retain historical evidence without treating it as current
  closure.
- [Reviewers mistake a record for approval] -> Use only closed non-clear dispositions
  and repeat the native-archive boundary in CLI output, README, charter route, and
  focused tests.
- [Git command behavior differs across platforms] -> Keep the command surface to
  stable Git plumbing, normalize subprocess failures into the closed result codes,
  and exercise it in isolated local fixtures.

## Migration Plan

1. Add red focused fixtures for the JSON contract, Git verification, rejection
   results, task-reference checks, and no-side-effect boundary.
2. Add the `openspec/guardrails/` command and README, then make the fixtures pass.
3. Add the registry, Charter, project-structure, and requirement-evidence updates;
   keep operation guidance concise and advisory.
4. Record this change's own plan and archive review work as ordinary tasks, run the
   focused and governance checks, and verify strict OpenSpec validation before native
   archive.

Rollback removes the command, route, registrations, and focused fixtures together.
Existing evidence records remain historical files and never require runtime data
migration because they have no archive or lifecycle authority.
