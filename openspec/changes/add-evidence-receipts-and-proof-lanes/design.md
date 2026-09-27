# Design

## Context

The repository already has real lanes (`make verify`, `make tui-journey`,
`make debugger-proof`, `make tui-experiences`) and a governance gate that
aggregates registered component checkers. What it lacks is any record tying a
lane's result to the revision being delivered, which is why a claim can outlive
its proof.

## Goals / Non-Goals

**Goals:** make a receipt cheap to produce, impossible to hand-write, invalid the
moment a covered surface changes, and easy to check. **Non-Goals:** no gate
verdict in this change, no runtime behavior, no new authority.

## Decisions

1. **Staleness is a surface diff, not a timestamp.** A receipt records the
   revision it ran at; it is stale when `git diff <revision>..HEAD -- <surfaces>`
   is non-empty for that lane's registered surfaces. Timestamps can be gamed by a
   clock and say nothing about which files changed.
2. **Receipts require a clean tree.** A dirty tree means the receipt cannot
   describe any commit, so the runner refuses to record a valid receipt (it may
   record a provisional one that no gate would accept).
3. **Only the runner writes receipts.** The receipt carries the command, exit
   code, revision, dirty flag, duration, tool versions and a SHA-256 of the
   transcript it teed; the checker (the follow-up change) re-hashes the
   transcript, so a hand-written "passed" has nothing to verify against.
4. **The transcript must carry the lane's success sentinel.** Each lane registers
   a sentinel string (`JOURNEY OK`, `experiences passed: 15/15`,
   `every lane exited 0`, ...); requiring it prevents substituting a transcript
   from a different lane.
5. **Journeys are part of a lane's definition for operator surfaces.** The
   registry names the experience journeys a lane must include, so "test the
   journey, not just the unit" is data rather than advice.
6. **Mutations are declarative and must go red.** `tests/mutations/registry.py`
   holds `(id, file, old, new, selector)` entries; the driver applies one at a
   time, runs the selector, restores the file, and fails the lane if the selector
   stays green. A guard nobody can make fail is not evidence.
7. **Cost control by two tiers.** The fast lane (seconds) serves iteration; the
   full lane (~75 s) serves handoff. The receipt records which lanes ran so the
   follow-up gate can require the full one only at closeout.

## Risks / Trade-offs

- [A lane's surfaces can be declared too narrowly, keeping a stale receipt valid]
  → the registry is reviewed like any authored policy, and the follow-up checker
  reports the surfaces it used, so a wrong declaration is visible rather than
  silent.
- [Mutation entries rot as code moves] → the driver fails loudly when an anchor
  no longer matches, so rot is detected instead of skipped.
- [Receipts add files to the workspace] → transcripts live under `.proof/`
  (gitignored) and the receipt JSON is small enough to commit with a change when
  a gate requires it.
