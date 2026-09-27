# Phase-0 evidence table — agent-support walkthroughs

One page, per the closed plan's acceptance: input · bound bundle/case + version ·
expected vs actual · authoritative result · proof strength · gap owner · lowest
red seam. Walk sources: [walkthrough A](walkthrough-a-coding-agent.md) (coding
agent, BUG-072 replay), [walkthrough B](walkthrough-b-dedicated-agent.md)
(dedicated agent, `public-controller-direction-loop@v1`). Proof strength:
`receipt-backed` (lane receipt / runner-recorded) · `recorded` (deterministic
artifact or command output on disk) · `UNVERIFIED` (needs a live run).

| # | Input (intent / case) | Expected vs actual | Authoritative result | Proof | Gap owner | Lowest red seam |
| --- | --- | --- | --- | --- | --- | --- |
| A-1 | BUG-072 symptom → projection + contract | Owner-table routing should reach the projection's owning contract — it does: `COMMANDS.md:55` → `Makefile:157` (names DPL-014) → spec clause "read from the bundle's own run summary" in 2 hops | Routing works; no gap | recorded | — | — (working example, kept for calibration) |
| A-2 | BUG-072 symptom → causal owner | The producer-side duty should be routable — it is not: the fix rests on LDD-003 (`local-workflow-debug-driving`), which no entry surface mentions, and the duty is an *implication* of "same … as ordinary runs", not a clause | Causal spec unrouted + implication-only | recorded | entry routing (harness `AGENTS.md` Information Map / `docs/README.md`) | behavior already pinned (`observations-are-published` mutation); the navigation gap has none |
| A-3 | "consult the ADRs" (any decision) | The closed plan counts ADR as an existing support surface — zero documents link into `docs/adr/` (reverse search across all harness markdown: 0 hits) | ADR tree is an island; discoverable only by directory listing | recorded | docs index (`docs/README.md` Living References) | none today (a doc-hygiene row would be the seam if fixed) |
| A-4 | run the narrowest test / any `uv` command outside `make` | Should just work — `uv run`/`uvx` outside make dies on the global uv cache EPERM (hit twice this session); the fix lives only in a `Makefile` comment (BUG-032) | Tooling works only through make or `.venv/bin/`; the error message points nowhere | recorded | entry docs (run block / local-operations) | none (the Makefile comment is the only carrier) |
| A-5 | trust CI red/green as verification signal | "CI exists ⇒ someone sees red" — the governance-suite step had failed on every run since 2026-09-26 (import error) while a stale gate fixture went red unseen; repaired this session | Verification signals can be silently broken; local agents had no way to notice | receipt-backed (f51c8d2: suite 55 OK, guard red-first) | repaired (CI lane + `test_ci_governance_steps.py`) | `test_ci_governance_steps.py` (red-first proven) |
| B-1 | direction-loop case → typed result honesty | Typed surface should present truth — measured: cancelled bundle inspects `cancelled@bootstrap`, report says `[terminal (cancelled)]`, invalid id gets a bounded closed rejection | Honest presentation holds on every probe | recorded (commands this session) | — | lifecycle contract tests + driver-matrix test |
| B-2 | direction-loop case → forbidden actions | Runtime should refuse, not just advise — closed `ADVERTISED_ACTIONS`, `exclusive_control_call_required`, `invalid_arguments` shape, `BUNDLE_ID_PATTERN`, production-owned admission; direction semantics contract-pinned (resume-only-for-human-subject, exhausted-terminal fresh start, terminal keeps refine) | Runtime layer enforces; review layer is live-only | recorded | — | `tests/contract/test_research_lifecycle_contract.py` |
| B-3 | "does the model itself choose right?" | Phase 0 cannot answer it: `evals/runs/` empty, no recorded case runs; case contract requires a live external model | Actual model selection remains an **open evidence question**, not a measured failure | UNVERIFIED | phase-2 eval route (case + runner + protocol all in place) | fail-closed telemetry runner (`execution_evidence_invalid`) |

## Branch decisions (each cites rows)

- **Phase 1 — local machine-readable diagnostic projection (`demo-sessions --format json`): NO-GO.**
  Its premise was "the coding agent gets stuck parsing human-formatted local
  diagnostics" (closed plan, gap table). Neither walk measured that stall: A's
  frictions were routing and tooling (rows A-2/A-3/A-4), never output parsing;
  B answered every question from the typed surface (rows B-1/B-2). Reopen
  trigger: a future walkthrough that measurably stalls on parsing inspection
  output. Per the todo's own rule — no measured failure, no work manufactured.
- **Phase 2 — controller/node evaluation repetition: GO (as an evidence upgrade,
  pending human budget and scheduling).** Not because phase 0 found a failure,
  but because row B-3 is the one question the walkthrough leaves open, and the
  existing route (registered case, fail-closed runner, review protocol) is the
  only way to upgrade it from UNVERIFIED. Recorded as a new focused todo;
  intersects `todo-adopt-framework-engineering-protocols`'s reproducibility
  item — owner + dedup to be decided before scheduling.
- **Phase 3 — public-tool diagnostic reads: NO-GO (keep the current surface).**
  No measured insufficiency of `legal_next_action` + typed result in any
  examined scenario (rows B-1/B-2); the plan already reserves this for explicit
  human approval of product purpose and disclosure scope, and phase 0 adds no
  new argument for opening it.
- **Surfaced follow-ups (not phases, not this change's work):** the routing
  gaps A-2 (unrouted debug-driving spec), A-3 (ADR island), A-4 (uv-trap
  pointer) are cheap, separately schedulable doc-routing fixes. They are
  recorded here with owners; opening them is the human's call, not implied.
