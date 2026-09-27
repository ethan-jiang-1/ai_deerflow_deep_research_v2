# Tasks

## 1. Lane registry

- [x] 1.1 Register every real lane (verify, tui-journey, debugger-proof, tui-experiences, doc hygiene, closeout gate) with command, working directory, covered surfaces and success sentinel in `deep_research_harness/proof-lanes.toml`. Verify: a focused test loads the registry, rejects an unknown lane or an empty surface list, and every registered command resolves to a real Make target or script.
- [x] 1.2 Register the operator-facing lanes' required journeys (the experience ids they must include) and mark credential-gated lanes. Verify: the registry loader rejects an operator lane that names no journey, rejects an unknown key or a missing sentinel, and accepts a credential-gated lane only with `requires_credentials` set.
- [x] 1.3 Assert the surface map is total: enumerate the deliverable roots and fail when any file matches no lane's surfaces. Verify: a focused test plants an uncovered file and asserts the lane fails, then asserts the real tree passes.

## 2. Receipt runner

- [x] 2.1 Implement `scripts/proof_receipt.py run --lane <lane>`: run the lane, tee the transcript under `.proof/transcripts/`, refuse a valid receipt on a dirty tree, record the fixed field set (including `python -V`, `uv --version`, `openspec --version` and the transcript SHA-256), and record `unverified` instead of a pass for a credential-gated lane without credentials. Verify: focused tests show a red lane recording exit 1, a dirty tree refused, a green lane recording exit 0 with every field present, and a credential-gated lane recording `unverified` (never a pass).
- [x] 2.4 Implement `--export` so a change can paste the receipt handle into its tasks, and assert `.proof/` stays out of git. Verify: a focused test asserts `git status --porcelain` is unchanged by a run.
- [x] 2.2 Implement `verify` / `--stale`: report a receipt as stale when a covered surface changed after its revision, and print the exact rerun command. Verify: a focused test edits a covered file and asserts staleness, then edits an uncovered file and asserts it stays valid.
- [x] 2.3 Wire `make proof LANE=<lane>` and document it in the testing document. Verify: the target runs and its exit code matches the lane's.

## 3. Mutation lane

- [x] 3.1 Implement `scripts/mutation_check.py` over `tests/mutations/registry.py`: apply each mutation, run its selector, require red, restore, and fail when any mutation stays green or its anchor no longer matches. Verify: a focused test with a planted toothless mutation (a behaviour removal whose selector stays green) exits non-zero.
- [x] 3.2 Seed the registry with the mutations demonstrated during the debugger work (stop-on-HITL, pending-request carrying, observation publishing, HITL log content, Start Run mode forwarding, pause honoured, hermetic demo root). Verify: `make mutation-check` reports each as RED.

## 4. Gates

- [x] 4.1 Run `check_doc_hygiene.py`, `check_project_gate.py --phase closeout`, `UV_OFFLINE=1 make verify` and the new lane commands from the repository root and `deep_research_harness/` as applicable, measuring every exit code directly. Verify: every measured exit code is 0.

## Evidence

Receipts produced by this change's own runner and recorded by the lane (all at
revision `78167d9`, clean tree, transcripts under `.proof/`):

| lane | exit code | handle |
| --- | --- | --- |
| `doc-hygiene` | 0 | `.proof/receipts/doc-hygiene.json` |
| `verify` | 0 | `.proof/receipts/verify.json` |
| `mutation-check` | 0 (25.4s) | `.proof/receipts/mutation-check.json` |

Observed while landing, each measured directly:

- `proof_receipt.py self-test` -> OK, 5 lanes, surface map total (it plants an
  unknown key, empty surfaces, a missing sentinel and journeys on a fast lane,
  and rejects all four).
- `make mutation-check` -> 7/7 mutations RED, exits 0 with its sentinel; the
  driver's `--self-test` shows a no-op mutation being reported GREEN, which is
  what makes the lane fail rather than pass silently.
- `make proof LANE=doc-hygiene` on a dirty tree -> status `provisional`, exit 1
  (a dirty tree never yields a valid receipt).
- Staleness by content change: appending a line to `AGENTS.md` (a covered
  surface) turns the receipt `STALE` with `rerun: make proof LANE=doc-hygiene`;
  reverting it restores `valid`; a bare `touch` (mtime only, unchanged content)
  correctly stays valid.
- Two real defects were found by this discipline while landing the tooling: the
  staleness rule first compared `revision..HEAD` and so ignored uncommitted
  edits, and a top-level `tests/mutations/` directory had to be documented in the
  test taxonomy (the repository's own contract test refused it).
