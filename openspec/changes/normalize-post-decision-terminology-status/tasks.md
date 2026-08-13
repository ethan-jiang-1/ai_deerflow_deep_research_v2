## 1. Apply Admission And Protected Baseline

- [ ] 1.1 Obtain explicit APPLY authorization for `normalize-post-decision-terminology-status`; record its date, docs-only boundary, exact allowlist, and the fact that archive/commit are not authorized.
- [ ] 1.2 Capture fresh `HEAD`, `git status --porcelain=v1 --untracked-files=all`, active OpenSpec changes, gitlink/nested-worktree metadata, and focused diffs for the three target documents before an edit.
- [ ] 1.3 Record the pre-existing concept-map changes in `deep_research_harness/AGENTS.md`, `deep_research_harness/CONTEXT.md`, `openspec/agent-charter/README.md`, and `openspec/agent-charter/concepts.md`; stop for direction if their ownership or a target-occurrence overlap cannot be separated.
- [ ] 1.4 Re-read the six owning main-spec blocks, Stage 4/5 post-archive dispositions, this change's proposal/design, and the A-004-T01 deferral. Add any newly actionable finding as an unchecked task before an edit.
- [ ] 1.5 Create separate apply-time D-001 and D-002 Adjustment Records with exact before/after wording, risk, possible side effects, controls, evidence limits, and deferred-work owner. Do not mark either applied yet.

## 2. Allowlisted Terminology And ADR Applicability

- [ ] 2.1 Apply D-001 only to the allowlisted Cognitive Evaluation Runner, Evaluation Execution Case, Evaluation Rubric, and short Rubric explanatory occurrences in `deep_research_harness/CONTEXT.md`: deterministic admission may read only Rubric identity/version and unique criterion IDs as non-model control metadata; Rubric prose, weights, thresholds, evaluator guidance, cognitive judgment, model-facing quality input, execution output quality meaning, and Runner quality verdicts remain excluded.
- [ ] 2.2 Add only a dated current-status/applicability postscript to ADR 0025. Preserve its title and historical body; state that the Runner remains execution-only and reports only `completed` or `failed` despite the narrowly admissible deterministic metadata.
- [ ] 2.3 Apply D-002 only to the allowlisted Bundle Loss, External Run Observation, Run Event Journal, and Support Handoff definitions in `deep_research_harness/CONTEXT.md`: supported retained diagnostic/Journal reading and participant presentation are Bundle-local and unavailable after loss; physical residual bytes are not asserted; Support Handoff remains planned and is not a fallback.
- [ ] 2.4 Revise only the existing dated current-status/applicability postscript in ADR 0006. Preserve its title and historical body; replace A-004 quarantine wording with the accepted Bundle-local/unavailable boundary without claiming an implemented support capability.
- [ ] 2.5 Re-check every changed sentence against the exact occurrence allowlist and both design matrices. Do not modify main specs, deltas, source, tests, configurations, governance executables, archives, DeerFlow, or A-004-T01 scenario titles.

## 3. Review And Verification

- [ ] 3.1 Review the scoped documentation diff with the accepted A-003/A-004 requirements. Confirm that it introduces no behavioral requirement, current-conformance claim, external-retention reader, physical-erasure assertion, or changed status for dormant Dedicated TUI and planned Support Handoff.
- [ ] 3.2 Confirm that user-owned concept-map changes remain intact and that the diff contains only the three allowlisted documents plus Stage 6 evidence and the progressive ledger. Stop on an unapproved path or overlapping user edit.
- [ ] 3.3 Run `openspec validate normalize-post-decision-terminology-status --strict`, `openspec doctor --json`, `python3 openspec/governance/check_agent_charter.py`, applicable Markdown/link checks, and `git diff HEAD --check`; record the structural/documentation proof limits.
- [ ] 3.4 Run `cd deep_research_harness && UV_OFFLINE=1 make verify` before archive. Record skips, warnings, and the fact that a documentation-only gate does not prove physical erasure, live behavior, future paths, or universal semantic conformance.
- [ ] 3.5 Complete both Adjustment Records with changed occurrences, observed side effects (including `none observed` with an evidence bound), remaining mismatches, and the still-open A-004-T01 tooling owner.

## 4. Archive Gate And Ledger

- [ ] 4.1 The current archive agent performs a closeout review of the actual allowlist, unfinished tasks, D-001/D-002 records, protected user-worktree result, and A-004-T01. Add any actionable finding as an unchecked task.
- [ ] 4.2 Obtain separate archive authorization after all applicable tasks and evidence are reviewable. APPLY authorization, validation, and passing tests do not authorize archive or commit.
- [ ] 4.3 Before archive, re-capture the worktree/gitlink baseline and rerun `UV_OFFLINE=1 make verify`, strict OpenSpec validation, and whitespace checks. Confirm no unapproved path or user-owned change is absorbed.
- [ ] 4.4 Archive through the normal OpenSpec workflow only after the archive authorization. Do not rewrite archived artifacts or imply that A-004-T01 is resolved.
- [ ] 4.5 Re-establish the no-active-change baseline, update the progressive ledger with the actual D-001/D-002 disposition and observed side effects, then stop pending separate Stage 7 authorization.
