## 1. Apply Admission And Evidence Setup

- [x] 1.1 Obtain and record a separate explicit Stage 2 apply authorization. Re-read
  `proposal.md`, `design.md`, this task list, the C-004/C-005/C-007..C-011 adjustment
  reviews, and the A-003/A-004 quarantine before making a target edit.
- [x] 1.2 Capture the fresh apply baseline in
  `_backlog/plans/alignment-audit-2026-08-12/alignment-audit-60-adjustments/stage-2-apply/`:
  HEAD, `git status --porcelain=v1 --untracked-files=all`, active OpenSpec changes,
  `git ls-files --stage deerflow`, `git submodule status -- deerflow`, and
  `git -C deerflow status --porcelain=v1 --untracked-files=all`. Record the proof
  bounds; do not source-browse or edit DeerFlow.
- [x] 1.3 Create the allowlisted occurrence-classification record under `stage-2-apply/`.
  Give every proposed source term its C ID, exact before text/location, named current
  owner/evidence, one design classification, intended target, risk control, and stop
  condition. Include the C-007 source rows for both `openspec/CONTEXT.md` and
  `openspec/agent-charter/README.md`. Register unlisted findings separately without
  editing them.
- [x] 1.4 Create separate, initially incomplete Adjustment Records for C-004, C-005.a,
  C-005.b, C-007, C-008, C-009, C-010.a, C-010.b, C-010.c, and C-011. Each must contain
  the template's Before/After, risk, possible side effects, controls, verification,
  observed-effects, and remaining-owner fields before its target edit begins.

## 2. Current Vocabulary Corrections

- [x] 2.1 Apply C-004 only in `deep_research_harness/CONTEXT.md`: distinguish DeerFlow
  host workspace, Deep Research Run Bundle, Runner-owned Evaluation Run Workspace, and
  sibling Evaluation Run Bundle. Do not edit storage code or infer an unverified
  lifecycle relationship.
- [x] 2.2 Apply C-005.a and C-005.b only in `deep_research_harness/CONTEXT.md`: retire
  completed-work future tense and current reliance on an archived change name, while
  preserving control/run-data separation, Runner ownership, `tests/eval/` role, and the
  current `local-context` policy route.
- [x] 2.3 Apply C-008 and C-009 only in `deep_research_harness/CONTEXT.md`: replace the
  false all-node smoke assertion with the registry-as-current-coverage boundary, and
  remove the unowned readable-report requirement while retaining the structured Review
  Record and non-pass semantics of `limited` and `inconclusive`.
- [x] 2.4 Apply C-010.a, C-010.b, and C-010.c only in
  `deep_research_harness/CONTEXT.md`: retain current `final/report.md` artifact fact;
  retire current report reopen/copy/export; label Support Handoff `planned`; label the
  dedicated Primary-User TUI and its Local-First route `dormant`; retain the current
  Dedicated Agent plus reflected-tool route. Do not create a public interface, export,
  UI, Support Handoff schema, or post-loss retention statement.

## 3. OpenSpec Routing Correction

- [x] 3.1 Apply C-007 only in `openspec/CONTEXT.md` and
  `openspec/agent-charter/README.md`: state that a change has one primary causal owner
  and may select every canonical policy actually triggered; each selected policy remains
  tied to its route-table trigger. Keep the Charter as a short information map that
  links rather than restates policy-selection detail. Preserve the rule that policy
  guidance does not create behavior, permission, or runtime authority. Do not edit
  `openspec/config.yaml`, a policy, or its checker.

## 4. Historical ADR Status Postscripts

- [x] 4.1 Apply C-011 to ADR 0002 and ADR 0003 by appending the dated uniform
  status/applicability postscript from `design.md`; preserve each title and every byte
  of existing historical body text. State the dormant dedicated-TUI route without
  changing current Deployment Owner responsibility.
- [x] 4.2 Apply C-011 to ADR 0006 and ADR 0008 by appending the dated uniform postscript;
  preserve titles and bodies. Mark Support Handoff planned and the dedicated-TUI
  Local-First route dormant, but stop rather than state any Bundle-loss retention,
  external reader, or participant presentation semantics.
- [x] 4.3 Apply C-011 to ADR 0010 by appending the dated uniform postscript; preserve its
  title and body. Retain `final/report.md` as a current Bundle artifact and record the
  historical Primary User export claim as non-current without creating a planned export
  commitment.
- [x] 4.4 For every C-011 ADR append, record its pre-append byte length and SHA-256 in
  the Adjustment Record. Apply all five postscripts with one actual ISO-8601 apply date.
  After the append, verify that exact prefix is unchanged and the only suffix is the
  approved dated postscript. Stop rather than overwrite, reformat, or merge a
  pre-existing user edit.
- [x] 4.5 Put the `design.md`-designated relative current-owner/route link in each ADR
  postscript and record `source ADR -> relative target -> target exists`. For ADR 0006,
  run this check after C-010.b has established the planned Support Handoff glossary
  entry and record that it is a terminology/status pointer to that file, not a behavior
  contract.
  Where `design.md` names a heading, record that heading's presence too. Do not
  substitute an archived change, a runtime source path, or a generic repository landing
  page for the designated owner/route.

## 5. Per-Adjustment Review And Verification

- [x] 5.1 After each C item, review the scoped diff against its Adjustment Record.
  Complete exact After text, observed side effects (or bounded `none observed`),
  verification result, remaining mismatch owner, and the A-003/A-004 quarantine check.
  Stop and leave the item unchecked if its wording needs a frozen-path edit or product
  decision.
- [x] 5.2 Re-scan only the allowlisted current authority and classify every remaining
  reviewed occurrence. Confirm C-006 has no target edit, archived changes remain
  historical only, and no unlisted current claim was silently changed.
- [x] 5.3 Run documentation/governance validation: `openspec validate
  retire-stale-context-concepts --strict`, `openspec doctor --json`,
  `python3 openspec/governance/check_agent_charter.py`, a manual record of every added
  relative Markdown link as `source -> target -> exists`, and `git diff HEAD --check`.
  Record command outcomes and their proof bounds; do not edit implementation or test
  code to chase a failure.
- [x] 5.4 Run the required existing deterministic closeout gate,
  `cd deep_research_harness && UV_OFFLINE=1 make verify`, and record its outcome,
  skips, warnings, and proof boundary. This is evidence only; this change adds no
  red/green behavior test because it changes no behavior.

## 6. Local Re-Audit And Closeout

- [x] 6.1 Complete the Stage 2 local re-audit in the `stage-2-apply/` evidence directory:
  compare before/after C-004, C-005, C-007..C-011, list resolved safe residues, and
  explicitly preserve A-003/A-004 for their separate changes.
- [x] 6.2 Review the complete final diff and worktree against the proposal allowlist and
  frozen-path list. Confirm no code, tests, cases, registries, main specs, governance
  executables, archives, `openspec/config.yaml`, or DeerFlow content changed.
- [x] 6.3 Obtain an explicit archive authorization only after all authorized tasks and
  Adjustment Records are complete. Archive the change using the OpenSpec archive
  workflow, record the archive result, and stop for a separate Stage 3 read-only
  re-audit authorization.
