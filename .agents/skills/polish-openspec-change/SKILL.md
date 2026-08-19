---
name: polish-openspec-change
description: Iteratively review and refine an active OpenSpec change after proposal generation. Use when given a change name or path and asked to polish, harden, review for apply readiness, or repeatedly resolve issues in its proposal, design, delta specs, tasks, or verification plan before `/opsx:apply`.
---

# Polish OpenSpec Change

Treat `<change-name-or-path>` as either an active change name, its directory, or a path to one of its artifacts. Polish the planning artifacts until their readiness is earned by evidence, not asserted from confidence alone.

## Boundaries

- Read and use `.agents/skills/openspec-explore/SKILL.md` before beginning. Use its curious, grounded, risk-seeking exploration stance to choose what to inspect.
- This skill has explicit authority to correct OpenSpec artifacts when existing decisions, accepted contracts, or implementation facts determine the correction. That is the only departure from `openspec-explore`'s usual no-auto-capture posture.
- Write only inside `openspec/changes/<change>/`. Do not start `/opsx:apply`, modify target code, tests, experiments, accepted specs, governance files, or task completion state.
- Do not run paid or real Agent experiments. Planning checks and read-only source investigation are allowed.
- Do not invent product behavior, broaden scope, choose between conflicting semantics, or claim a runtime fact without evidence. Escalate those matters to the user.

## Select And Ground The Change

1. Run `openspec list --json`.
2. Resolve the input:
   - A bare name means `openspec/changes/<name>/`.
   - A directory must be the change root or contain one in its parent chain.
   - An artifact path resolves by walking upward to the directory containing `.openspec.yaml`.
3. Require the resolved directory to be an active change beneath `openspec/changes/`. If it is missing, archived, outside that tree, or ambiguous, show the available active changes and ask the user to choose.
4. Run `openspec status --change "<name>" --json`. Use its artifact graph and `applyRequires` as the source of truth; do not assume a particular OpenSpec schema or a fixed set of artifacts.
5. Read every completed change artifact, including all delta specs and `verification-plan.yaml` when present. For incomplete or unfamiliar artifact types, read `openspec instructions <artifact-id> --change "<name>" --json` before judging what is missing.
6. Read only the context needed to establish facts: affected accepted specs, requirement registry references, relevant charter/guideline constraints, and the relevant implementation surface. Record which source established each important conclusion.

## Polish Loop

Make at least two distinct passes. Do not simply rephrase the same checklist on every pass.

### Pass 1: Whole-Change Coherence

Review the change as one executable argument:

- Does the proposal state a bounded problem, intended outcome, exclusions, and source of authority?
- Does the design make the proposed behavior, ownership, state/transition, failure, recovery, compatibility, and evidence boundaries coherent?
- Do the delta specs state observable, testable requirements with no unsupported behavior?
- Can every requirement be traced through design, tasks, and the verification plan, including its proof class and realistic evidence boundary?
- Do terms, invariants, source-of-record claims, identifiers, and scope mean the same thing in every artifact?
- Are tasks dependency-ordered, small enough to execute, and supplied with a genuine done condition instead of a vague aspiration?
- Does the plan follow the project charter: Agent judgment, Markdown control flow, and Engine deterministic authority stay in their proper boundaries?

### Later Passes: Risk-Led Review

For each later pass, choose the highest-risk remaining concern rather than seeking superficial completeness. Examples include an ambiguous authority boundary, a hidden state transition, incompatible pre-existing behavior, missing degradation or rollback, an unverifiable success claim, a task that cannot produce its required proof, or a new control layer that adds complexity without a clear reduction elsewhere.

Inspect the relevant artifact and source facts deeply enough to either resolve the concern or explain precisely why it remains uncertain. After any edit, re-read every artifact affected by that edit and run another risk-led pass. Stop churning once a pass finds no materially new actionable issue.

## Resolve Findings In The Same Invocation

Classify each finding before acting:

| Finding | Action |
| --- | --- |
| A stale reference, missing derived task, inconsistent terminology, omitted verification detail, or other correction determined by existing facts | Correct all affected change artifacts immediately. Keep proposal, design, delta specs, tasks, and verification plan synchronized. |
| A question answerable by accepted specs, source code, tests, or another authoritative project fact | Investigate it, then correct the artifacts if the evidence settles it. |
| A new product decision, scope tradeoff, permission/risk decision, conflicting authoritative sources, or unavailable runtime fact | Do not guess or paper over it. State the question, evidence, impact on readiness, and the smallest meaningful options. Report `not ready`. |

Never merely list a mechanically resolvable defect for someone else to repair. Conversely, never turn an unresolved decision into a fake certainty just to reach apply readiness.

## Verify Readiness

After the final clean risk-led pass, require all of the following before saying `ready for apply`:

1. Every artifact in `applyRequires` is complete, and no required planning artifact has an unresolved contradiction or decision.
2. Run, from the repository root:

   ```bash
   python3 openspec/governance/check_project_gate.py --phase plan --change "<name>"
   git diff --check
   ```

   The plan gate is the canonical project planning check when
   `openspec/governance/check_project_gate.py` exists. It sequences the owning
   component checks (Change Guidance for the Focus Card, the selected-change scope of
   the specification checker for delta headers/titles, the planning scope of the
   requirement checker for reservations/collisions/retired reuse, and native strict
   validation for MODIFIED preservation) and runs every subprocess from the repository
   root with exact exit-code propagation. The gate already invokes
   `openspec validate "<name>" --strict` as its strict-validation owner, so the
   canonical existing-gate path runs the plan aggregate once and does NOT run a
   separate native strict invocation — a second strict run would duplicate the same
   owner and could drift apart from the gate's composition.

   **Bootstrap (gate not yet present):** when `check_project_gate.py` does not exist in
   this checkout (for example while the change that introduces it is still being
   applied), do not claim the missing gate passed. Instead run the existing checks it
   would sequence: `openspec validate "<name>" --strict`, the Change Guidance checker
   (`python3 openspec/governance/check_change_guidance.py`), any named standalone
   project checks the discovered repository guidance or change instructions explicitly
   require, and `git diff --check`. Report plainly which checks ran and that the gate
   itself was not available.

   Also run any project-specific planning or governance checks that the discovered
   repository guidance, change instructions, or verification plan explicitly names.
   Do not assume a particular script name, runtime, or governance layout exists.

3. The plan output may print `reservation: <id> (capability)` lines for legal new
   requirement IDs. Use those lines only as an advisory report: separately read the
   change's `tasks.md` and require every reservation to map to an explicit apply task
   that registers that ID in the requirement registry. The gate never parses
   `tasks.md`; this mapping check is the polish pass's own obligation. A reservation
   without a matching registration task is `not ready`.
4. Treat an unrelated pre-existing project-wide check failure as an external blocker, not as permission to edit unrelated files or to call the change fully ready.

## Report

For each pass, state the concern examined, the authoritative facts checked, and the repairs made. Finish with exactly one clear outcome:

- `ready for apply`: name the clean final pass, list validation results, summarize artifact changes, and stop without applying.
- `not ready`: identify only the unresolved decisions or failed checks, their impact, and the next user decision or factual investigation needed.
