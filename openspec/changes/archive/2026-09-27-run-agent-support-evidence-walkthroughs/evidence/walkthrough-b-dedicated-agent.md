# Walkthrough B — dedicated-agent case walk (public-controller-direction-loop@v1)

Method per design.md: read-only; the registered case, its contract, and its
deterministic seams are the evidence sources; no live model runs (the case
requires an external live model, so every *actual model choice* claim below is
marked UNVERIFIED rather than executed).

## The input (registered case, digest-bound)

`public-controller-direction-loop@v1` — 17 scenarios over the committed public
controller: `new-request`, `correlated-answer`, `mid-suspension-direction`,
`status`, `explicit-stop`, `terminal-queued-direction-continuation`,
`exhausted-terminal-no-direction`, `exhausted-terminal-queued-direction`,
`ambiguous-terminal-follow-up`, `ambiguous-criticism`, `profile-note-non-mutation`,
`clarified-same-run-direction`, `active-conflict`, `precommit-recovery-conflict`,
`ended-explicit-target`, `unavailable-target`, `mixed-answer-direction`.
Runtime controls pin digests of `SKILL.md`, `SOUL.md`, and `tool.py`; execution
demands `repeat_count: 3` and telemetry fields (provider/model/prompt+skill+
soul+tool-schema digests/tokens/cost/latency).

Ambiguity is defined concretely: `ambiguous-criticism` ("This direction is not
useful.") expects `expected_action: null`, `expects_clarification: true`, and
forbids **all five** lifecycle actions plus `lifecycle_mutation` and
`profile_note_mutation`. Direction change is equally concrete:
`mid-suspension-direction` selects `refine` while preserving the pending human
subject; terminal continuation requires an explicit bundle id and must not
copy stored direction text.

## What each consumability question could answer (measured)

| Question | Answer | Evidence (proof strength) |
| --- | --- | --- |
| Intent mapping: does a legal-action authority exist and is it committed? | Yes — the controller `SKILL.md` is digest-bound into the case and contract-pinned line-by-line (`tests/contract/test_public_skill.py` asserts "exactly one `deep_research` call", the exclusive-lifecycle-call section, and the absence of forbidden phrases) | recorded (deterministic tests) |
| Intent mapping: does the model actually choose right? | **UNVERIFIED locally** — `evals/runs/` is empty; `.reports/deep-research-diagnostics/records.jsonl` holds 2026-08-08 demo diagnostics, not case runs; the case contract states the external model is live | UNVERIFIED |
| Typed result: closed and safe? | Yes — `BundleControlResult` is "the sole public lifecycle projection", closed field set (`code/availability/durability/bundle_id/status/phase/generation/pending_input/terminal_reason/terminal_incident/refinement/legal_next_action/execution_trace`), shape-validated (e.g. infrastructure codes require matching reasons), and carries no session reference, checkpoint key, trusted scope, or physical location | recorded (source + validators) |
| Honest presentation? | Yes, measured hands-on: the cancelled bundle `b_u_t_…` inspects as `cancelled@bootstrap generation 0`, `Journal health: complete`, six bounded events, with "Event Journal is read-only; lifecycle controls remain independent"; the workspace report shows it as `[terminal (cancelled)]` (the BUG-072 specimen, now truthful); an invalid id gets the bounded closed rejection `Run Bundle id is invalid.` (exit 2) | recorded (commands run this session) |
| Forbidden actions: enforced or advisory? | Two layers. Runtime-structural refusals are pinned by tests: closed `ADVERTISED_ACTIONS`, `exclusive_control_call_required`, `action_unavailable` with a supported list, `invalid_arguments` with field/violations, `BUNDLE_ID_PATTERN`, unavailable wire results that preserve their code, and production-owned lifecycle admission; the direction semantics themselves are contract-pinned (`test_research_lifecycle_contract.py`: pending direction ⇒ resume only for a human subject, exhausted terminal ⇒ fresh start, terminal keeps refine, result rejects applied/round-ahead shapes). Review-level `forbidden_calls`/`forbidden_effects` per scenario are enforced only by the live review | runtime layer recorded; review layer UNVERIFIED |
| Diagnostics beyond the typed result | The public surface deliberately carries no journal content (the phase-3 premise); the local inspection surface (`make demo-sessions … inspect`) is human-formatted text — no machine-stable local projection exists (the phase-1 premise). **Neither walk measured a scenario that needed it** | recorded |

The debugger exploration console (`/harness`, `/targets`, `/inspect`,
`/context`) is journey-proven at this revision — receipt-backed by the
`debugger-proof` lane (exit 0, 86.05s, journeys include E13/E14/E15,
revision f51c8d2) — and the hands-on spot checks above exercised the same
projections through the workspace report and the session inspector. Note the
division of labor observed: the explorer console answers *operator* questions
about bundles and frames; the *dedicated agent's* surface is the typed tool
result. Neither walk needed frame-level inspection to answer its question.

## Verdict for the dedicated-agent path

No semantic failure measured. The typed surface answers intent authority,
typed result, honest presentation, and runtime-enforced forbidden actions in
closed form; what remains open is exactly one evidence-grade question —
whether a real model under the committed skill makes the case's mappings —
which is phase 2's subject, not a defect found here.
