# Design

## Context

See proposal.md — Why. The instruments and preconditions exist: the debugger
exploration console is journey-proven (`make debugger-proof`, 14 experiences),
the proof-lane receipts are live and currently valid at the working revision,
and the eval registry carries the controller direction-loop cases. Nothing in
this change runs a real model or touches product code; the only writers are
evidence files under this change and the backlog todo.

## Goals / Non-Goals

**Goals:**

- Produce measured evidence (not self-assessment) for whether each of the two
  agent paths fails today in a way phases 1–3 would fix.
- Make every friction row reproducible: it quotes the navigation step, the
  command, and what was missing — a later agent can re-walk the same step.
- Give each phase branch a go/no-go that cites table rows, so the ledger stops
  carrying an unverified assumption.

**Non-Goals:**

- No ten-dimension self-score, no aggregate quality grade — the closed plan
  forbids replacing hands-on with scoring.
- No live-model reruns: phase 0 uses existing records and scripted journeys;
  anything needing credentials stays UNVERIFIED and, if it matters, feeds the
  phase-2 go decision instead of being silently executed.
- No fixing of frictions found — each finding gets an owner and a lowest red
  seam row; fixes are later changes' work.

## Decisions

- **Specimen for A: BUG-072** (operator inventory reported a cancelled bundle
  as resumable; demo-CLI integration test rode the ambient workspace). Chosen
  because it is the most recent fixed fault, small, replayable offline, and its
  ground truth (fix commit + closed card) is available for comparison. The
  navigation runs from the symptom text only — the fix commit stays closed
  until the comparison step. Alternative (BUG-073 stop-policy defects) touches
  the debugger driver this change also uses as an instrument, which would
  tangle the two walks.
- **Case for B: `public-controller-direction-loop@v1`** — the registered case
  whose subject is exactly intent ambiguity and direction change on the public
  tools, per the closed plan's phase-2 lead. The scripted journey plus the case
  loader are the evidence source; `evals/runs/` (currently empty locally) is
  checked for recorded runs before any claim about actual model choice.
- **Proof-strength vocabulary** (one per table row): `receipt-backed` (a lane
  receipt or recorded runner output covers it), `recorded` (deterministic
  artifact on disk, e.g. case JSON, bundle state), `UNVERIFIED` (needs a live
  run or a surface not exercisable offline).
- **Friction log format**: free-form steps in `evidence/`, but each friction
  entry ends with a one-line finding suitable for the table row.

## Risks / Trade-offs

- Walking as the session agent means the navigator has prior session context;
  the replay mitigates this by requiring each step to cite the surface that
  routed it, so "I already knew" must still name where the knowledge is
  supposed to live — and a missing home is itself a finding.
- One specimen per path is a sample of one; the go/no-go therefore speaks about
  *these* paths and cites rows, not about all conceivable failures. The todo
  keeps the branches reviewable rather than declaring the question closed
  forever.
