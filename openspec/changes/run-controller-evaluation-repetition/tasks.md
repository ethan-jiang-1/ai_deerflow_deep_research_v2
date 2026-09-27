# Tasks

## 1. Manifest code-revision provenance (CES-003 delta, red-green)

- [x] 1.1 Red first: a unit test asserts a finalized bundle manifest in a git worktree
      records the worktree's code revision, and that a manifest without the field
      still validates (additive). Confirm it fails against the current manifest
      model.
- [x] 1.2 Green: `EvaluationBundleManifest` gains additive optional
      `code_revision: str | None = None`; the runner resolves the repository
      revision at execution start (best-effort, absent outside a worktree); the
      finalized manifest carries it. Re-run the red test and the existing eval
      suite.

## 2. Live subjects (implementation discovery: the two cases need different subjects; no live subject exists yet)

- [x] 2.1 Enumerate the `subject_state` values the controller case declares and
      write the deterministic table of declared typed results each state's
      bounded recording fake may return (fresh per scenario; undeclared state
      fails closed). Unit-test the table against every declared state.
- [x] 2.2 Build the controller live subject: isolated DeerFlow home via the
      `configure.py` pattern with the real model endpoint (key from
      `DEEPSEEK_API_KEY`, injected at runtime only), committed skill/soul at the
      container paths, `file:read` route, public `deep_research` tool over the
      fake lifecycle; per scenario seed the minimal state-establishment
      conversation prefix, drive the `user_turn` through the real public
      `make_lead_agent` composition, capture skill-read evidence and the proposed
      action or clarification, aggregate per-scenario records plus the case's
      required telemetry into one `SubjectExecution`.
- [x] 2.3 Deterministic tests for the controller subject's capture path: a
      scripted model double proves the skill-read/action/clarification capture
      and telemetry aggregation (the real-model judgment itself is NOT claimed by
      these tests); a digest mismatch (uncommitted skill) fails the subject
      honestly.
- [ ] 2.4 Build the topic-planning node subject: the `topic_planning` node's real
      factory through `graph_context.run_agent` with the real model (the node
      cognitive program, not the lead agent), scenario state from the case
      fixture, same telemetry aggregation.
- [x] 2.5 Verify each case-declared execution timeout can hold a full
      multi-scenario real-model session; if not, stop and surface the bound
      question before any live spend.

## 3. The runs (staged spend, controller pipeline first)

- [x] 3.1 Preflight: `scripts/live_preflight.py` (or the entrypoint's own
      preflight) with `.env` exported; confirm the model credential and the
      registered case ids.
- [x] 3.2 Pipeline canary: ONE `run_selected_live_case` invocation for
      `public-controller-direction-loop@v1` (17 real-model turns). Inspect the
      bundle: execution status, telemetry completeness, sanity of captured
      proposals, manifest revision; confirm it is reviewable. Stop and fix
      before any further spend if anything is off.
- [ ] 3.3 Controller series: `run_selected_live_case_series` for
      `public-controller-direction-loop@v1` (3 fresh bundles); record bundle ids,
      per-execution status and `cost_usd`.
- [ ] 3.4 Topic-planning series: after its subject lands, the series for
      `topic-planning-direction-loop@v1` (6 scenarios × 3); record bundle ids,
      per-execution status and `cost_usd`.

## 4. Reviews and evidence

- [x] 4.1 For each retained bundle, submit a review per the versioned protocol
      (read-only; four-state result, evidence, confidence, unknowns, owning seam,
      follow-up), judging the rubric criteria from the recorded per-scenario
      proposals; record review ids.
- [x] 4.2 Write `evidence/controller-evaluation-results.md`: per case and
      repetition — execution status, per-scenario expected vs actual proposal,
      review result with confidence and unknowns, aggregate cost, the staged-spend
      narrative, and the explicit fake-lifecycle boundary (intent mapping measured;
      lifecycle execution owned by the handoff tests). State plainly anything
      UNVERIFIED.
- [ ] 4.3 Close the todo: update
      `_backlog/todos/todo-controller-evaluation-repetition.md` with the outcome and
      move it to `_done/_done_todos/` (DONE-010), keeping the three ledger indexes
      consistent.

## 5. Gates and closeout

- [x] 5.1 Refresh receipts for every lane whose covered surface this change touched
      (the manifest/subject code lands under `src/**` and `tests/**`); `make
      proof-status` must show every lane valid.
- [x] 5.2 Full gates: `UV_OFFLINE=1 make verify`, the repository closeout gate with
      this change's attestation, governance suite, doc hygiene, dependency
      direction — all zero; commit with the evidence.
