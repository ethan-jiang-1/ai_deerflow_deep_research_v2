## Context

See `proposal.md` for the ownership drift. Each affected ID already has an approved
requirement block in its owning main spec and matching archived delta, registry entry,
implementation evidence, and test mapping. Only the header declaration failed to
remain synchronized after archive.

## Goals / Non-Goals

**Goals:**

- Restore exact registry-to-main-spec ownership for the six existing IDs.
- Re-establish a green deterministic governance baseline before unrelated changes.

**Non-Goals:**

- Change requirement wording, ownership, behavior, implementation, or evidence.
- Re-run or reinterpret the archived change that introduced the requirements.

## Decisions

### 1. Repair only the owning header lines

Append each missing ID to the existing `> req:` header of the main spec that already
contains its tagged requirement block. This preserves the approved main-spec body and
the registry's current capability mapping.

Rejected alternative: create duplicate delta requirements. There is no pending
behavior to specify, and a duplicate delta would misrepresent metadata repair as a
semantic change.

### 2. Treat both requirement checkers as the acceptance seam

Run `check_project_reqs.py` to prove unique current ownership and
`check_project_req_coverage.py` to prove the restored owners retain implementation and
test evidence. The remaining governance checks must stay green to catch accidental
adjacent edits.

Rejected alternative: validate only that each ID appears as text. Body references
already exist and do not prove that the main header declares ownership.

## Risks / Trade-offs

- [A header could claim the wrong requirement] -> Match every added ID to its tagged
  requirement block, archived delta capability path, and registry capability before
  editing.
- [A broad cleanup could hide unrelated drift] -> Limit implementation to four header
  lines, inspect a scoped diff for those paths, and preserve unrelated worktree
  modifications when reviewing repository-wide status.
