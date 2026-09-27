# Walkthrough A — coding-agent fault replay (BUG-072)

Method per design.md: navigate from the symptom text alone through documented
entry surfaces; the fix commit and the bug card's fix section stayed closed
until the comparison step. All steps below quote the surface that routed them.

## The input (symptom text only)

`make demo-workspace-report` lists a bundle as `[resumable (status: suspended)]`
while the bundle's own `state.json` says `terminal_status: cancelled` — the
operator inventory reports a cancelled bundle as recoverable.

## Navigation log

| # | Step | Surface that routed it | Outcome |
| --- | --- | --- | --- |
| 1 | App-code change → read harness guide | root `AGENTS.md` owner table | 1 hop, direct |
| 2 | "commands and targets" → find the inventory command | harness `AGENTS.md` Information Map → `COMMANDS.md` | `COMMANDS.md:55` documents `make demo-workspace-report`, non-terminal ⇒ `resumable` |
| 3 | Command → owning script + contract | `Makefile:157-161` | invokes `scripts/soft_bundle.py workspace-report`; comment names **DPL-014** and the operator-view posture — the "named owning result contract" the owner table promises, present and correct |
| 4 | Contract text → the violated clause | `openspec/specs/demo-pipeline/spec.md` (DPL-014) | "lifecycle status read from the bundle's own run summary (`completed`, `stopped`, `cancelled`, or `blocked` are terminal)" — the symptom is a direct, quotable violation |
| 5 | "prove guards (make mutation-check)" → the red seam | harness `AGENTS.md` Verification section | registry entry `observations-are-published` names the causal file (`runtime/debug_driver.py`), the selector, and the reason ("BUG-072: the operator report then lies") |
| 6 | Narrowest test run | derived from root `AGENTS.md` run block (`.venv/bin/python -m pytest`) | `tests/integration/test_debug_driver_matrix.py::test_accepted_commands_keep_the_run_summary_truthful` — **1 passed in 0.79s** (1.45s wall), clean single-dot output |
| 7 | Verification width for this owner | harness `AGENTS.md` Verification section | `make mutation-check` (8/8 red this session, runner-recorded) + `make debugger-proof` (receipt-backed: exit 0, 86.05s, revision f51c8d2) |

## Comparison against the actual fix (commit `965ebf0`, opened after navigation)

- Same projection surface (`soft_bundle.py` workspace-report), same violated
  spec (DPL-014), same test seam (the driver-matrix summary assertion). The
  documented routing reached the correct consumer-side truth.
- **Mismatch — the producer side**: the fix's causal owner (the debugger drive
  path must publish lifecycle observations like ordinary runs) rests on
  **LDD-003** (`openspec/specs/local-workflow-debug-driving/spec.md`), which
  the navigation never reached and no routing surface mentions (verified:
  `AGENTS.md`, `docs/README.md`, `COMMANDS.md`, `local-operations.md`,
  `Makefile` — zero hits for the capability or `LDD-003`). Worse, the duty is
  not a clause but an *implication*: LDD-003 says the debug path uses "the same
  recipe, compile path, and durable saver/thread used by ordinary runs" and
  produces "the same trace frame kinds"; the fix commit itself derives the
  observation-publishing obligation from that phrasing. A navigator must both
  find an unrouted spec AND reconstruct the inference.

## ADR angle (task 1.5)

`docs/adr/0021-runner-cases-and-bundles-have-explicit-observations.md` is the
semantically adjacent decision record (explicit observations). Reachability:
**no document links into `docs/adr/` at all** — not the root or harness
`AGENTS.md`, not `docs/README.md` (the documentation index has no ADR row),
not runbooks; a reverse search across all harness markdown found zero
inbound links. The ADR tree is discoverable only by listing directories. The
closed plan's baseline table counts "ADR" as an existing coding-agent support
surface; existence is true, consumability is not.

## Friction findings (each carries the step that produced it)

- **F-A1 · uv-outside-make trap** (hit twice this session, e.g. step 6
  alternatives and the CI-lint verification): any `uv run`/`uvx` outside
  `make` dies with `failed to open file ~/.cache/uv/…: Operation not
  permitted` in sandboxed environments. The fix (workspace-local
  `UV_CACHE_DIR`, make wrapper, or `.venv/bin/`) is documented only in a
  `Makefile` comment (BUG-032 conclusion); the error message itself points
  nowhere. Cost: two dead ends before the comment was found.
- **F-A2 · unrouted, implication-only causal spec** (step "comparison"):
  producer-side duties for the debug path live in `local-workflow-debug-driving`
  (LDD-003), unreachable from any entry surface and only implied by the
  "same as ordinary runs" phrasing.
- **F-A4 · verification signals can be silently broken** (measured this
  session, before this change): the CI governance-suite step had been failing
  since 2026-09-26 with an import error while a stale gate-test fixture went
  red unseen — an agent trusting "CI exists ⇒ someone sees red" was wrong.
  Repaired in f51c8d2; recorded here because it is a verification-path
  consumability failure of exactly the class this walkthrough measures.
- **Non-friction, recorded as a working example**: the projection→contract→
  red-seam chain (steps 2–6) is fast (2 hops to the spec clause, one command
  to a 0.79s red test) and the Makefile comment naming DPL-014 is precisely
  the pattern the owner table promises.
