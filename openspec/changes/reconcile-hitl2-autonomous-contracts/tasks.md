## 1. Baseline And Plan Review

- [ ] 1.1 **Owner: apply agent.** Re-read the proposal's Control Placement Review,
  `workflow-control.md`, these tasks, and the archived
  `2026-07-30-introduce-hitl2-human-decision-experience` counterexample before edits;
  verify a five-capability keep/retire matrix records HITL1 pending input, internal
  HITL2 routes/rerun/readiness, retired HITL2 human interaction, and dormant decoder
  exclusions, and add every actionable review finding as an unchecked task.
- [ ] 1.2 Capture the deterministic red baseline by running `rg -n` for the exact stale
  clauses `HITL-2 presentation SHALL render`, `must re-suspend at HITL2`,
  `user chooses rerun at HITL2`, `retained HITL-1 or HITL-2 session`,
  `semantic HITL-1/HITL-2 guidance`, `Existing HITL2 choice identifiers`,
  `second human stop`, `awaiting_hitl2`, and `active_hitl2_subject` across the five
  main specs, `openspec/governance/req-registry.yaml`, the lifecycle walkthrough, and
  affected tests; record the expected matches before changing them so the same scan is
  a falsifiable green check in task 4.1.
- [ ] 1.3 Run `python3 openspec/governance/check_project_gate.py --phase plan --change reconcile-hitl2-autonomous-contracts` from the repository root and verify exit 0 before applying the contract migration.

## 2. Contract And Reader Synchronization

- [ ] 2.1 Sync all five reviewed deltas into their exact main capabilities
  (`research-graph-lifecycle`, `research-run-experience`, `rerun-node`,
  `research-demo-tui`, and `research-cli-onboarding`) and verify each modified block
  retains every surviving main-spec scenario while no main spec promises an HITL2
  prompt, choice response, second Answer, or re-suspension.
- [ ] 2.2 Update only the existing `REN-001` and `REN-006` summaries in
  `openspec/governance/req-registry.yaml` to describe internal graph/control input and
  autonomous new-generation HITL2 evaluation; verify no requirement ID is added,
  removed, or reassigned with `python3 openspec/governance/check_project_reqs.py`.
- [ ] 2.3 Rewrite section 4 of
  `deep_research_harness/docs/run-lifecycle-walkthrough.md` so HITL2 validates and
  continues autonomously after Wave2 pass, retain the actual internal route/topology
  vocabulary only where it remains true, and verify
  `python3 openspec/governance/check_doc_hygiene.py` exits 0.
- [ ] 2.4 Audit every remaining `HITL2`/`hitl2` occurrence under `openspec/specs/` and
  classify it as autonomous contract, internal route/topology, rerun/readiness control,
  or conditional future activation; verify no unclassified current-human-interaction
  claim remains and archives are not edited.

## 3. Test Fixture And Evidence Migration

- [ ] 3.1 Rewrite the focused adapter expectations first so current choice behavior is
  exercised through HITL1 and autonomous HITL2 yields no second `AwaitingInput`/Answer;
  run the selected tests against the still-stale fixtures and record at least one
  expected deterministic failure before migrating fixture data (red evidence).
- [ ] 3.2 Remove `awaiting_hitl2()` and `awaiting_invalid_hitl2_choice()` as
  production-shaped fixtures, replace invalid-choice coverage with a typed HITL1
  language-choice fixture, and verify
  `.venv/bin/python -m pytest tests/integration/test_demo_run_update_adapters.py tests/contract/test_run_experience_contract.py`
  passes from `deep_research_harness/`.
- [ ] 3.3 Rewrite the CLI/TUI tests that currently consume a synthetic HITL2 prompt so
  HITL1 follow-up/language choice proves typed adapter behavior and autonomous HITL2
  proves zero additional answer rounds; verify
  `.venv/bin/python -m pytest tests/integration/test_demo_real.py tests/integration/test_demo_tui.py tests/integration/test_demo_cli.py`
  passes from `deep_research_harness/`.
- [ ] 3.4 Migrate
  `test_active_hitl2_subject_survives_independent_direction_admission` to a valid current
  HITL1 pending subject while preserving its actual refinement-admission assertion;
  verify `.venv/bin/python -m pytest tests/integration/test_refinement_round_workflow.py`
  passes from `deep_research_harness/`.
- [ ] 3.5 Update only test-owned evidence/requirement registries whose renamed or
  replaced test references changed, retain the existing autonomous HITL2 evidence
  references, and verify `.venv/bin/python scripts/check_test_assets.py` exits 0 from
  `deep_research_harness/` without adding an `evaluation-hardening` semantic change.
- [ ] 3.6 Run the lowest responsible autonomous seam
  `.venv/bin/python -m pytest tests/unit/test_hitl2_real.py tests/graph/test_research_graph.py tests/integration/test_demo_cli.py tests/contract/test_run_experience_contract.py`
  from `deep_research_harness/` and verify valid/malformed HITL2, full graph completion,
  no second prompt, and retained HITL1 typed-choice coverage all pass.

## 4. Closeout And Scope Proof

- [ ] 4.1 Re-run the exact bounded scan from task 1.2 against current authority/docs/tests
  and verify it exits 1 with no stale matches; separately run
  `rg -n -i 'HITL[-_ ]?2|hitl2' openspec/specs deep_research_harness/docs/run-lifecycle-walkthrough.md`
  and review every remaining match as an allowed autonomous/internal/conditional use.
- [ ] 4.2 Verify the change contains no runtime, public API, topology, checkpoint schema,
  dependency, or `deerflow/` edit by reviewing `git diff --name-only` and
  `git diff --submodule=short`; any such edit keeps this task unchecked until removed
  or the proposal is explicitly re-scoped.
- [ ] 4.3 From `deep_research_harness/`, run `UV_OFFLINE=1 make verify` directly and
  verify exit 0; do not make the Harness gate read, import, execute, or link OpenSpec
  content.
- [ ] 4.4 From the repository root, run
  `python3 openspec/governance/check_doc_hygiene.py --self-test`,
  `python3 openspec/governance/check_doc_hygiene.py`, and
  `python3 openspec/governance/check_project_gate.py --phase closeout` directly and
  verify every exit code is 0 without a pipeline.
- [ ] 4.5 From the repository root, run
  `openspec validate reconcile-hitl2-autonomous-contracts --strict` and
  `git diff HEAD --check` directly and verify both exit 0.
- [ ] 4.6 Record `git status --porcelain=v1 --untracked-files=all`,
  `git ls-files --stage deerflow`, `git submodule status -- deerflow`,
  `git -C deerflow status --porcelain=v1 --untracked-files=all`, and review
  `git diff --submodule=short`; verify the recorded gitlink pointer is unchanged and
  treat this only as scope evidence, not upstream compatibility proof.
- [ ] 4.7 **Owner: archive agent.** Before archive, compare the approved five-capability
  scope, actual tasks, synced main-spec/registry/walkthrough/test diff, the task 1.2 ->
  4.1 red/green evidence, and all unresolved checkboxes; add every actionable finding
  as an unchecked task and mark this review complete only when no stale current HITL2
  interaction claim or out-of-scope runtime change remains.
