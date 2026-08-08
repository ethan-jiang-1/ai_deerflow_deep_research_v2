## 0. Captured Evidence And Scope

- [x] 0.1 Capture and preserve the real run `r_SnrIKUGQhUwUIAWyht4dq_zJLGNftutorg24_bhX62E`, its retained bundle, lifecycle/global diagnostic-reference mismatch, empty degraded profile, and strict-msgpack warnings in BUG-001 through BUG-004 and the active postmortem plan.
- [x] 0.2 Establish deterministic red-capable probes for Chinese `标准深度` parsing and retained `inspect` insufficiency; record that current evidence only proves Wave0 gate exhaustion, not the model/tool/validation cause.

## 1. Canonical Bundle Locator Foundation

> Current: complete. Canonical offline verification, strict OpenSpec validation, and diff checks passed again on 2026-07-22. Credentialed run `r_e8w-cpL9Juk5Q2JEM7Dsv47hZefpnbRaxYtY9MxN6aI` retained a complete Wave0 timeline; BUG-005 and `classify-deep-research-wave0-worker-failures` own the remaining safe failure classification.

- [x] 1.1 Write red start/bootstrap/request/work-unit/session tests for a controller-owned canonical bundle locator: trusted UTC-minute creation for real and full-fake recipes, all real artifact/`ContentRef` paths using it, metadata-only full-fake layout, marker/manifest locator binding, legacy absent-locator fallback to `r_<id>`, SQLite reopen, symlink/grammar rejection, and duplicate-root fail-closed behavior (REG-016, BON-006, WOU-009, RUI-009, RUS-004).
- [x] 1.2 Implement the locator through start checkpoint initialization/default/ownership, graph projection, bootstrap and request stores, work-unit/probe paths, retained-session publication/inspection/cleanup, and workbench; bind manifest locator label, preserve `research_id` as sole lifecycle identity, and never migrate legacy roots (REG-016, BON-006, WOU-009, RUI-009, RUS-004).

## 2. HITL1 Intake Contract And Regression Tests

- [x] 2.1 Write red domain and real-HITL1 lifecycle tests for Chinese aliases, machine JSON, ambiguous alias rejection, `must_answer` visibility, a typed correlated `accept_suggestion` action, persisted proposal reuse across interrupt replay, rejected-message cursor advancement without accepted consumption, three bounded zero-recognition responses across reissued request ids with `gate_blocked`/`input.invalid_response` plus one deterministic diagnostic ref, and old-checkpoint defaults (HIN-007, REG-015).
- [x] 2.2 Introduce frozen bounded profile parse/proposal/feedback contracts; remove cross-dimension synonym ambiguity; add controller-owned proposal/feedback/rejection-counter/rejected-message-cursor defaults and reducers without changing lifecycle route authority (HIN-007).
- [x] 2.3 Extend the generic human-input seam with separate bounded `action_ids` and `response_kind=action`/`action_id` contracts across `AnswerRun`, direct resume, brokered resume, session-operation pending projection, and workbench action control; reject unadvertised, mismatched, replayed, malformed, or text-spoofed acceptance before HITL1 (REG-015, RDO-005, RWB-006).
- [x] 2.4 Update real HITL1 and its compact prompt context so validated first brief is checkpointed before interrupt, explicit correlated acceptance deterministically materializes it, rejected input advances only its feedback cursor, recognized incomplete answers merge durably and reset rejection state, and a third rejected answer across reissued feedback requests becomes the specified explainable `gate_blocked`/`input.invalid_response` terminal with deterministic diagnostic ref rather than silently degrading (HIN-007).
- [x] 2.5 Run focused domain/graph/integration regressions and update node-level evidence selectors for every HIN-007/REG-015 scenario before proceeding to presentation changes.

## 3. Shared Presentation And CLI/TUI State

- [x] 3.1 Add red shared-contract tests for bounded intake feedback plus observed run-state/terminal fields; assert raw context, answer, model/tool content, exception text, secrets, paths, and fabricated phase progress never enter RunUpdate (RER-007).
- [x] 3.2 Extend `ResearchRunExperience` projections and diagnostics correlation so prompt adapters receive proposal/advertised-action/accepted/missing/rejection/accepted-round/rejection-retry facts and terminal adapters receive one correlated retained diagnostic reference, phase, durability, and inspectability truth (RER-007).
- [x] 3.3 Update `demo_real.py` to render visible acceptance and complete JSON guidance, recurring returned-only waiting state with elapsed/last-confirmed phase, and a uniform terminal receipt with exact inspection command and same-process/restart-durable semantics (REC-005).
- [x] 3.4 Update `demo_tui.py` to render the same shared intake feedback, typed action control, and terminal/run-state semantics without parsing lifecycle wire data or creating a second control path (RER-007, RED-006).
- [x] 3.5 Add deterministic CLI/TUI adapter tests for localized reply feedback, explicit acceptance, no hidden `must_answer`, recurring liveness, terminal receipt, Ctrl-C truth, and unsafe-content redaction; register evidence claims (REC-005, RER-007, RED-006).

## 4. Retained Execution Event Journal And Inspection

- [x] 4.1 Write red run-session/runtime tests for versioned `run-summary.json` and bounded `diagnostics/events.jsonl`: atomic independent validation, UTC timestamp plus monotonic sequence, closed event/category schema, one terminal diagnostic reference across incident/trace/summary/event/receipt, journal availability/completeness, legacy absence, corrupt files, hostile raw data rejection, bounded retention, and recorder-failure non-interference (RUS-004).
- [x] 4.2 Add a runtime-owned recorder whose sole `record(closed_event)` seam allocates sequences under the session lock and shares a pure deterministic diagnostic-reference helper; inject it into dispatch, graph node wrapper, node-agent bridge, and work-unit controller, publishing lifecycle/node/attempt/model-tool-category/validation/submit/retry/exhaustion/terminal facts without allowing providers or tools to write a session file (RUS-004).
- [x] 4.3 Define the same closed envelope for future sandbox/pod producers without adding a pod dependency or retaining raw remote logs; prove event ordering, summary correlation, and non-authoritative failure behavior (RUS-004).
- [x] 4.4 Extend `demo-sessions inspect` to render manifest creation time, safe relative locator label, validated summary, terminal/suspended status, last phase, diagnostic correlation, event availability, and bounded latest event timeline before fixed artifact references; retain legacy lookup, zero-write inspection, and no host-path/raw-body output (RUS-004, REC-005).
- [x] 4.5 Extend authorized local workbench diagnosis projections/rendering for terminal summary, bounded event timeline, and explicitly advertised HITL1 acceptance action while keeping broker authorization and lifecycle controls unchanged (RWB-005, RWB-006).
- [x] 4.6 Run a deterministic Wave0-all-attempts-fail integration fixture; prove inspect/workbench can explain `blocked@wave0` with correlated attempt categories and no secrets, raw exceptions, URLs, paths, prompts, answers, or tool/model bodies (RUS-004, RWB-005).

## 5. Checkpoint Serialization Compatibility

- [x] 5.1 Add a strict-msgpack red integration test that persists and resumes profile/work-unit state under `LANGGRAPH_STRICT_MSGPACK=true`, asserting no unregistered `ContentRef` or `AttemptStatus` warning and old checkpoint compatibility (RUI-008).
- [x] 5.2 Implement the smallest explicit serialization compatibility boundary or native-state normalization that satisfies strict msgpack without allowing arbitrary project type deserialization; test unknown type rejection (RUI-008).
- [x] 5.3 Run file-SQLite reopen and same-process resume coverage under normal and strict msgpack modes, then register the regression evidence (RUI-008).

## 6. Real Reproduction, Documentation, And Closure Decision

- [x] 6.1 Re-run the captured battery-comparison scenario after event logging is present; preserve only safe event/summary evidence and use it to identify the actual Wave0 terminal category. Do not declare a model/Tavily/validator root cause before this evidence exists.
- [x] 6.2 If the real Wave0 failure remains after observability work, create a separate focused bug/change with the correlated event evidence; otherwise add the exact remediation regression to this change. Do not close BUG-002 merely because inspect output became prettier.
- [x] 6.3 Update `agent/README.md`, relevant `agent/AGENTS.md` architecture guidance if contracts change, the active plan, BUG-001 through BUG-004 links/status, diagnostic command help, requirement registry, and test-evidence metadata.
- [x] 6.4 Run focused red-green suites, `cd agent && make format`, lint, test-assets, requirement coverage, strict-msgpack coverage, and a credentialed real acceptance/reproduction only if credentials are locally available; record redacted evidence only.
- [x] 6.5 From repo root run `cd agent && UV_OFFLINE=1 make verify`, `openspec validate harden-deep-research-real-cli-intake-and-observability --strict`, and `git diff HEAD --check`; compare protected-path baseline/final status and keep `backend/` and `frontend/` untouched before archiving or closing any bug.
