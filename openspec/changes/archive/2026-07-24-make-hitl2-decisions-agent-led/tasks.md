## 1. Baseline And Red Regressions

- [x] 1.1 Record protected-path worktree status. Add deterministic public lifecycle,
  SQLite-restart, local-broker, mixed-recipe, and blocking-I/O regressions that prove a
  valid HITL1 response completes the ordinary route without a second HITL2 response.
  Preserve HITL1 retry, stale-request, cancel, and terminal-resume coverage. (`ALR-001`,
  `DPL-001`, `HIT-002`)
- [x] 1.2 Add pure boundary-policy and real-node regressions: a valid Wave2-pass
  predecessor selects graph-owned `proceed`; malformed or unknown predecessors fail
  closed and create no pending input. (`ALR-001`, `HIT-001`)
- [x] 1.3 Add readiness regressions proving valid evidence/provenance with no consumed
  HITL2 request is not blocked, while missing evidence and invalid provenance remain
  structural failures. (`REA-001`, `REA-005`)
- [x] 1.4 Add public fake CLI and TUI regressions proving a normal scope response
  reaches the fixture terminal without a second route-selection input; retain
  graph-only coverage for each non-default fixture route and truthful fixture-stop
  attribution. (`DPL-001`, `RED-001`, `HIT-002`)
- [x] 1.5 Add a CLI documentation regression proving user-copyable quick-start
  commands contain no inline shell comments. (`FCO-001`)

## 2. Autonomous HITL2 And Readiness

- [x] 2.1 Implement the pure bounded HITL2 boundary validator and continuation result,
  annotate it with `@impl ALR-001`, and reject malformed or non-topological input
  without inventing a route. (`ALR-001`, `HIT-001`)
- [x] 2.2 Update the fake HITL2 node to consume its configured fixture route without a
  `PendingResearchInterrupt`; make terminal attribution truthful for fixture control.
  (`DPL-001`, `HIT-002`)
- [x] 2.3 Update the real HITL2 node to apply only the validated autonomous `proceed`
  route and remove its HITL2 interrupt/resume path. Do not add a speculative authority
  marker. (`ALR-001`, `ALR-002`, `HIT-002`)
- [x] 2.4 Remove `check_hitl2_consumption` from readiness hard rules and its public
  requirement/evidence claims; retain evidence and provenance checks. (`REA-001`,
  `REA-005`)

## 3. Presentation And Onboarding

- [x] 3.1 Update CLI/TUI rendering so autonomous HITL2 progress is not an internal
  route menu. Keep HITL1 and any independently specified future prompt submission
  graph-owned. (`DPL-002`, `RED-003`)
- [x] 3.2 Update `agent/README.md` quick-start and interaction documentation with
  paste-safe zsh commands and the current no-HITL2-prompt boundary; keep fake-output
  claims explicit. (`FCO-001`)
- [x] 3.3 Update the smallest affected test-evidence registries and documentation
  guidance for `ALR` and modified `REA` requirements. (`ALR-001`, `ALR-002`,
  `REA-001`)

## 4. Verification And Hygiene

- [x] 4.1 Run focused policy, readiness, lifecycle, CLI, TUI, and documentation
  regressions in the locked deterministic environment; run interactive and scripted
  fake-demo transcripts. (`ALR-001`, `DPL-001`, `REA-001`, `FCO-001`)
- [x] 4.2 Run `cd agent && make format`, `make lint`, and `make test-assets`; record
  that live model, Gateway, frontend, database-server, and Docker checks are
  inapplicable to this downstream deterministic change.
- [x] 4.3 From the repository root, run `cd agent && UV_OFFLINE=1 make verify`,
  `openspec validate make-hitl2-decisions-agent-led --strict`, `git diff HEAD --check`,
  and protected-path status comparison; confirm `backend/` and `frontend/` remain
  clean. Update BUG-007 only after these conditions pass.
