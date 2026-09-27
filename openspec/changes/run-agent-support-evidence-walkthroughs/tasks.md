# Tasks

## 1. Walkthrough A — coding-agent fault replay (BUG-072)

- [x] 1.1 From the BUG-072 symptom text alone (operator inventory reports a
      cancelled bundle as resumable), navigate the documented entry surfaces
      (root AGENTS.md routing → harness AGENTS.md Information Map → owning
      docs/code) and record each hop: which surface routed the next step, where
      the trail required guessing, and which prescribed surface never answered.
      The fix commit and the bug card's fix section stay closed during this
      navigation.
- [x] 1.2 From the located owner, identify the owning main-spec requirement and
      the narrowest reddenable test seam; run that test narrowly and record the
      loop time, the command form that worked, and any output that was unsafe
      or awkward to parse. Note (do not re-plant) the existing mutation guard
      that already proves this seam goes red.
- [x] 1.3 Run the verification command the entry surface prescribes for this
      owner at its narrowest useful width; record actual frictions (e.g.
      tooling that only works through `make` because of the workspace-local uv
      cache, duration, output shape).
- [x] 1.4 Open the fix commit and the bug card's fix section; compare against
      the independent navigation: same owner? same spec? same test seam?
      Record every mismatch as an evidence row with its routing gap.
- [x] 1.5 Check the ADR angle: does a current ADR cover the fixed behavior, and
      was it reachable from the routing surfaces during step 1.1? Record.

## 2. Walkthrough B — dedicated-agent case walk (public-controller-direction-loop@v1)

- [x] 2.1 Read the registered case, contract, and rubric; extract what the case
      treats as intent ambiguity/direction change, which public-tool actions it
      exercises, and what evidence strength the rubric demands.
- [x] 2.2 Walk the case's scripted journey read-only (case loader or the
      debugger exploration console): record the typed result fields actually
      produced (`code/status/phase/terminal_incident/legal_next_action`), the
      controller skill surface the case loads, and which forbidden actions the
      runtime demonstrably refuses (cite the guard that proves each refusal).
- [x] 2.3 Determine what local records can and cannot prove: check
      `evals/runs/` for recorded runs of the case; mark every claim about
      *actual model choice* (as opposed to test-prewritten actions) with its
      true proof strength, UNVERIFIED where no live evidence exists locally.
- [x] 2.4 Record the consumability verdict for the dedicated-agent path: can
      intent mapping, typed result, honest presentation, and forbidden-action
      knowledge each be answered from the typed surface and the exploration
      console without parsing TUI text? Each unanswered question becomes a
      table row with a gap owner.

## 3. Evidence table, branch decisions, ledger, closeout

- [x] 3.1 Write `evidence/phase-0-evidence-table.md`: one page, one row per
      measured finding (input; bound bundle/case and version; expected vs
      actual; authoritative result; proof strength; gap owner; lowest red
      seam).
- [x] 3.2 Write the per-branch go/no-go — phase 1 (local JSON diagnostic
      projection), phase 2 (controller/node evaluation repetition), phase 3
      (public-tool diagnostic reads) — each citing table rows; a branch
      without a measured failure gets no-go with the reason stated.
- [x] 3.3 Update `_backlog/todos/todo-agent-support-walkthroughs-and-diagnostics.md`
      with the phase-0 outcome and branch decisions; keep the ledger index and
      counts consistent (three places per the backlog ritual).
- [ ] 3.4 Refresh receipts for the lanes the walkthrough exercised; run the
      repository closeout gate (every component checker zero) and record the
      command and exit codes.
