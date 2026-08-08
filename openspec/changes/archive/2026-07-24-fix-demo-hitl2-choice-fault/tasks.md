## 1. Baseline And Red Regressions

- [x] 1.1 From the repository root, record `git status --porcelain=v1 --untracked-files=all` and confirm the existing BUG-006/backlog and new change artifacts are preserved while `backend/` and `frontend/` remain clean.
- [x] 1.2 Add a failing `ResearchRunExperience` contract test that establishes and caches a validated non-empty-trace HITL2 `AwaitingInput`, then supplies the result of a locally initiated `AnswerRun`/`resume` as a same-research non-record `response_invalid` denial. Assert a same-request immutable snapshot/prompt copy with `choice_input_invalid`, empty trace delta, no session publication or diagnostic write, no raw rejected value, and no `protocol.invalid_result`. (`RER-003`)
- [x] 1.3 Add failing negative fixtures proving that a non-`resume` outbound dispatch, mismatched research IDs, an internally inconsistent or non-choice cached prompt/request, non-empty trace, `response_mismatch`, bundle/record-bearing denial fields, a denial `Command` with a new request artifact, missing cached update/request, and malformed lifecycle data retain the existing fail-closed fault behavior rather than re-presenting a cached prompt. (`RER-003`)
- [x] 1.4 Add a failing credential-free public fake-CLI regression that supplies a normal HITL1 answer, the rendered HITL2 display line, and then `proceed`; assert canonical-ID guidance, safe correction feedback, no raw rejected value or fabricated phase progress, and successful terminal completion. (`DPL-002`, `RER-003`)
- [x] 1.5 Add shared-update rendering fixtures for the real CLI and Textual adapter that prove `choice_input_invalid` feedback is actionable and redacted without parsing lifecycle wire data; one renderer fixture is sufficient for both TUI modes because its prompt renderer is mode-independent. (`DPL-002`, `RER-003`)

## 2. Shared Recovery Contract

- [x] 2.1 Extend the existing frozen `PromptView.rejection_category` literal with `choice_input_invalid` and annotate the owning domain/runtime surfaces with `@impl RER-003`; preserve compatibility for prompts without feedback and do not add a duplicate feedback field. (`RER-003`)
- [x] 2.2 In `ResearchRunExperience`, cache each validated `AwaitingInput` complete update. Before trace mutation, recognize only an exact current-research, empty-trace, ordinary-mapping non-record `resume/response_invalid` denial returned for the local `resume` dispatch while the cache's snapshot, prompt, and request consistently identify HITL2 `choice`; return an immutable cached-update copy with `choice_input_invalid` and an empty trace delta. Leave every other denial and malformed result on the existing fail-closed path. (`RER-003`)
- [x] 2.3 Preserve graph authority and observability boundaries: do not publish a new session fact, mutate durability/checkpoint/trace, emit raw rejected input, reconstruct a snapshot from denial data, or manufacture a diagnostic record on the recoverable local choice correction; verify a later valid option follows the normal graph response path. (`RER-003`)

## 3. Standalone Presentation And Documentation

- [x] 3.1 Update `demo.py` and `demo_real.py` to label choice entry as an advertised option ID, render closed invalid-choice feedback, and remain in their existing `AwaitingInput` loops until a later valid answer, EOF, interrupt, terminal, or non-retryable fault. (`DPL-002`)
- [x] 3.2 Update `demo_tui.py` to render the same closed feedback through its existing pending-prompt state while preserving its UI-owned option-ID submission and lifecycle-worker ownership. (`DPL-002`)
- [x] 3.3 Update `agent/README.md` with the exact standalone choice-entry contract and correction behavior; keep all claims scoped to the agent-owned demos and do not alter `backend/` or `frontend/`. (`DPL-002`)
- [x] 3.4 Register the new deterministic selectors and smallest requirement impacts in `agent/tests/assets/evidence.py` and `agent/tests/assets/requirement_evidence.py`; update only the test-evidence registries required for `DPL-002` and `RER-003`. (`DPL-002`, `RER-003`)

## 4. Verification And Change Hygiene

- [x] 4.1 Run the focused domain/runtime, adapter, and public fake-CLI regressions with the locked `operations` and `demo-tui` environment; run the piped `make demo` correction journey as credential-free public-entry evidence. (`DPL-002`, `RER-003`)
- [x] 4.2 Run `cd agent && make format`, `make lint`, `make test-assets`, and the applicable focused deterministic test selections; record any intentionally inapplicable live-model, Gateway, frontend, database-server, or Docker checks.
- [x] 4.3 From the repository root, run `cd agent && UV_OFFLINE=1 make verify`, then `openspec validate fix-demo-hitl2-choice-fault --strict` and `git diff HEAD --check`; compare final protected-path status with the baseline and confirm `backend/` and `frontend/` remain clean.
