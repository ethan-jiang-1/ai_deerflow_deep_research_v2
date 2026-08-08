## 1. Admission And Evidence Setup

- [x] 1.1 **Apply agent:** before the first target edit, re-read the selected control-placement and workflow-outcome reviews, this task list, `BUG-022`, `BUG-023`, and the retained `blocked@hitl1` counterexample; add every actionable mismatch as an unchecked ordinary task. Done when the direct owner, legal recovery, and lowest deterministic seam remain explicit for every planned edit.
- [x] 1.2 Register `DPL-009` and `HIN-013` in `openspec/governance/req-registry.yaml`; add the smallest-sufficient `@impl` references and requirement-evidence/assets entries for the new focused tests, including a known-violation detector where the evidence tooling requires one. Run the affected asset/requirement checks before behavior edits.
- [x] 1.3 Reconcile the committed tactical patch, BUG-022/023 wording, and plan status against the approved deltas, including the 60-second web-read deadline and existing HITL1 two-invocation limit. Correct any drift before treating an implementation task as complete.
- [x] 1.4 Correct the Change Focus Card's primary-owner field to the canonical governance spelling, preserving the two explicitly bounded direct owners, then rerun the governance gate before final verification.
- [x] 1.5 Replace free-form Control Placement Review posture descriptions with the canonical governance posture enum while preserving each row's recovery boundary, then rerun the governance gate.

## 2. Bounded Demo Web Reads

- [x] 2.1 Add deterministic unit coverage at `tests/unit/test_demo_core.py` for direct Tavily timeout, network/protocol, usage-limit, HTTP 429, and HTTP 500-599 failures that recover on a later attempt; assert a 60-second attempt timeout, a fresh client per attempt, and the exact cancellable one-/two-second backoff. (`DPL-009`)
- [x] 2.2 Add deterministic unit coverage for exhausted three-attempt search/fetch; authentication, malformed input, non-429 4xx, HTTP status outside 429 or 500-599, and unknown one-attempt outcomes; cancellation during both an attempt and backoff; redacted unavailable payloads; and unchanged same-run fetch provenance. (`DPL-009`)
- [x] 2.3 Reconcile `scripts/_demo_core.py` with the new tests and `DPL-009`: keep retry classification at the direct read boundary, preserve cancellation and bounded payloads, and do not add graph state, lifecycle retry, raw provider output, or a global retry helper. Run `UV_OFFLINE=1 uv run --no-sync --extra operations python -m pytest tests/unit/test_demo_core.py -q`. (`DPL-009`)

## 3. HITL1 Structured-Brief Contract

- [x] 3.1 Add a deterministic prompt/parser compatibility fixture in `tests/graph/test_hitl1_prompts.py` that parses the model-visible expected JSON from both initial and structural-repair requests, proves each covers every parser-required `StructuredBrief` field and advertises only parser-accepted fields, admits canonical advertised values/bounds, and rejects an extra field. (`HIN-013`)
- [x] 3.2 Add deterministic HITL1 node/lifecycle coverage showing an output-contract failure uses only the existing repair/exhausted path, writes no partial profile/checkpoint authority, and preserves the typed structured-output incident. (`HIN-001`, `HIN-013`)
- [x] 3.3 Reconcile `graph/nodes/hitl1/prompts.py`, its parser, and only necessary domain helpers with the compatibility fixtures; keep output-language guidance in the instruction/parser check and retain the existing two-invocation bound. Run `UV_OFFLINE=1 uv run --no-sync --extra operations python -m pytest tests/graph/test_hitl1_prompts.py tests/graph/test_hitl1_node.py tests/integration/test_hitl1_lifecycle.py -q`. (`HIN-013`)

## 4. Shared Terminal Projection

- [x] 4.1 Add a red returned-terminal fixture proving that a typed HITL1 provider failure and `output.structured_invalid` render in the standalone CLI with their safe category, phase, diagnostic reference, durability truth, and only the existing legal next action, distinct from genuine `research.blocked`; assert raw question, prompt, provider body, URL, secret, and exception text are absent. (`REC-002`, `REC-006`)
- [x] 4.2 Repair only the existing terminal materializer or CLI projection boundary that omits the non-provider category; do not infer from retained files, add a CLI classifier, or promise resume. Run `UV_OFFLINE=1 uv run --no-sync --extra operations python -m pytest tests/integration/test_demo_real.py -q`. (`REC-002`, `REC-006`)

## 5. Integration Evidence And Bug Resolution

- [x] 5.1 Run the combined deterministic lane: `cd deerflow_research && UV_OFFLINE=1 uv run --no-sync --extra operations python -m pytest tests/unit/test_demo_core.py tests/graph/test_hitl1_prompts.py tests/graph/test_hitl1_node.py tests/integration/test_hitl1_lifecycle.py tests/integration/test_demo_real.py -q`; record failures as new unchecked tasks before a live run.
- [x] 5.2 After task 5.1 is green and real-demo preflight passes, run exactly one bounded canary with `cd deerflow_research && bash run/real-research.sh`. Record only its run reference, terminal/suspension phase, safe category, diagnostic reference, and whether it reached the first HITL1 suspension or later phase; do not manually loop retries or claim availability from success.
- [x] 5.3 Update BUG-022 and BUG-023 with the deterministic and canary evidence. Close either bug only when its stated acceptance criteria are met; retain or file a new scoped bug for any distinct typed cause. Update `_backlog/plans/real-research-reliability.md` phase/status accordingly.

## 6. Verification And Closeout

- [x] 6.1a Repair the pre-existing overlong line in `tests/contract/test_operation_guidance_probe_evidence.py` that blocks the required downstream lint gate, without changing its test behavior; rerun lint before resuming 6.1.
- [x] 6.1b Apply the repository formatter to the two changed focused tests and the one pre-existing formatting violation reported by the full lint gate, without behavioral edits; rerun the complete format check before resuming 6.1.
- [x] 6.1c Diagnose and repair the three full-integration lifecycle tests that currently receive a `Command` instead of their declared terminal mapping; establish the correct handler/graph result contract with the smallest regression evidence, then rerun their focused lane before resuming 6.1.
- [x] 6.1 Run `cd deerflow_research && UV_OFFLINE=1 make verify`, `openspec validate harden-real-research-external-io --strict`, and `git diff HEAD --check`; record `git status --porcelain=v1 --untracked-files=all` for both repository roots and verify `backend/` and `frontend/` remain clean.
- [x] 6.2 Re-read all changed requirements, evidence mappings, and deterministic test results; update the active backlog plan with the final evidence and any remaining bounded operational limitation before proposing archive.
- [x] 6.3 **Archive-closeout agent:** before archive, re-read the selected control-placement review, actual committed range, unresolved tasks, BUG-022/023 state, and deterministic plus bounded-canary evidence. Add any actionable correction as an unchecked task; archive only when no competing owner/control fact was introduced and the recorded evidence proves the declared closure condition.
