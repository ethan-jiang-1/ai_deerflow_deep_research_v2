## 1. Apply Preparation And Bounded Edit

- [x] 1.1 Before editing, re-read this change's proposal, design, DRC-001 delta, the
  canonical Charter route, and the four enumerated current targets. Capture a focused
  residual-wording baseline showing the singular policy-routing text; do not inspect
  or modify archived changes or `deerflow/` source.
- [x] 1.2 Align `openspec/policies/README.md`, `openspec/config.yaml`, and
  `deep_research_harness/AGENTS.md` with the trigger-based rule: select every
  canonical policy whose route-table trigger applies, record those canonical names in
  the single Focus Card field, and add only the conditional review record each
  selected policy requires.
- [x] 1.3 Sync the approved DRC-001 delta into the main
  `deep-research-agent-charter` specification. Preserve exactly one primary causal
  owner and the guidance-only/non-runtime-authority boundary; do not alter policy
  triggers, parser/checker behavior, or the policy library's contents.

## 2. Focused Evidence

- [x] 2.1 Re-run the focused wording check after the edits. Confirm that the four
  current entry points use compatible plural trigger-based language, that the
  Charter remains the sole routing authority, and that residual singular occurrences
  are historical archives only.
- [x] 2.2 Run `openspec validate reconcile-policy-routing-cardinality --strict`,
  `openspec doctor --json`, `python3 openspec/governance/check_agent_charter.py`, and
  `git diff --check`. Record exact results and their limits in this task file before
  requesting archive authorization.

  - Verified 2026-08-13: the four current targets consistently say to select every
    canonical policy whose route-table trigger applies; `openspec/agent-charter/README.md`
    remains the sole routing authority; no current target contains `one relevant policy`
    or `choose only the policy`. Matches in archived changes and the alignment audit are
    historical evidence, not current authority.
  - Passed 2026-08-13: `openspec validate reconcile-policy-routing-cardinality --strict`;
    `openspec validate --specs` (`49 passed, 0 failed`); `openspec doctor --json`
    (healthy); `python3 openspec/governance/check_agent_charter.py`; and
    `git diff --check`.
  - Limits: these checks prove document/spec structure, current wording, and Focus Card
    shape only. They do not infer whether every future proposal selects all semantically
    applicable policies, and they do not prove runtime behavior or automatic enforcement.

## 3. Closeout After Separate Authorization

- [x] 3.1 Before archive, run `cd deep_research_harness && UV_OFFLINE=1 make verify`,
  `openspec validate reconcile-policy-routing-cardinality --strict`, and
  `git diff HEAD --check`; record `git status --porcelain=v1 --untracked-files=all`,
  `git ls-files --stage deerflow`, `git submodule status -- deerflow`,
  `git -C deerflow status --porcelain=v1 --untracked-files=all`, and review
  `git diff --submodule=short`. Treat these as manual observed gitlink evidence only,
  not automatic detector protection.

  - Passed 2026-08-13: `UV_OFFLINE=1 make verify` exited `0`. Its deterministic
    governance, lock, Ruff, test-asset, and requirement-coverage gates passed; fast
    was `2495 passed, 3 deselected, 2 warnings`; integration was `237 passed, 4 skipped,
    32 deselected, 16 warnings`; and workflow was `35 passed, 2785 deselected, 42
    warnings`. The four integration skips are real-Gateway app-stack tests unavailable
    in this environment. The warnings are existing Pydantic deprecation/serializer
    warnings and are not treated as a claim about live, credentialed, or release-E2E
    evidence.
  - Passed 2026-08-13: `openspec validate reconcile-policy-routing-cardinality --strict`,
    `openspec doctor --json`, `python3 openspec/governance/check_agent_charter.py`,
    and `git diff HEAD --check`.
  - Observed 2026-08-13: `git status --porcelain=v1 --untracked-files=all` contains
    this active change, its applied four current-authority targets, and pre-existing
    Stage 7 audit/backlog work; `git ls-files --stage deerflow` is
    `160000 66b9e7f21212490cf92fafac137542b9deb06615 0 deerflow`;
    `git submodule status -- deerflow` reports the same pointer;
    `git -C deerflow status --porcelain=v1 --untracked-files=all` is empty; and
    `git diff --submodule=short` has no gitlink diff. These are manual observations,
    not automatic future protection.
- [ ] 3.2 After separate archive authorization, archive the completed change through
  the normal OpenSpec workflow, re-run the post-archive strict/doctor/Charter checks,
  update N-002 as completed, and re-audit the Stage 7 ledger before closing the
  alignment plan.
