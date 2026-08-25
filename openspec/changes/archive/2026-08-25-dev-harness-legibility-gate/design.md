# Design: dev-harness-legibility-gate

## Context

`check_change_guidance.py` already mechanically enforces the entry-chain line budgets
(declared in `openspec/change-guidance/local/deep-research.md` under `## Line Budgets`)
and the `CLAUDE.md` imports-`AGENTS.md` contract. What remains unguarded is the drift
that lives in the doc layer's *content*: the ADR index going stale against its
directory, relative links in the entry chain breaking, and encoding/newline drift.
See proposal.md — Why.

## Goals / Non-Goals

**Goals:**

- Add one self-contained, standard-library-only deterministic checker that rejects the
  three unguarded drift classes (ADR index ↔ directory, entry-chain relative links,
  UTF-8/trailing-newline), each with a negative-control proof.
- Register it as a `project-structure` requirement so it cannot drift silently out of
  the structural inventory.

**Non-Goals:**

- No product-runtime behavior, no graph/node/state change, no `deerflow/` touch.
- Do NOT aggregate into `check_project_gate.py` (PRS-009 owns the six-component
  closeout and forbids a separate consistency checker).
- Do NOT wire into `make verify` (Harness gate stays application-independent).
- Do NOT re-check line budgets or the CLAUDE import contract (already owned).
- Do NOT author the ADR index content here (it is `_backlog` work; this checker only
  verifies it stays consistent).

## Decisions

1. **Standalone checker in `openspec/governance/`, not a gate component.**
   PRS-009 states closeout `SHALL NOT add a separate consistency checker`; `make verify`
   must not reach OpenSpec content. A standalone checker is the only placement that
   respects both boundaries. *Alternative (fold into check_change_guidance.py) rejected:
   that checker owns Change Guidance + line budgets, and ADR-index/link checking is a
   different concern.*

2. **Self-contained rules as module constants, no separate policy doc.**
   The three rule sets are small and deterministic; they live in the checker's docstring
   and constants, mirroring `check_harness_dependency_direction.py`. *Alternative (a
   `doc-hygiene-policy.md`) rejected to keep the change to one new file.*

3. **G4 resolved by relabel, not implementation.**
   `architecture-policy.md` claims a generated locator block in
   `deep_research_harness/AGENTS.md` and registry markers that do not exist and are not
   checked. This change adds a structural path, which triggers that policy's
   "regenerate the bounded locator" step. Relabeling the block as future plan makes the
   obligation honest. *Alternative (implement the generated block + checker integration)
   rejected as ceremony: nothing consumes or checks it.*

4. **Negative control via `--self-test`, no separate test file.**
   `--self-test` builds a clean fixture and one planted violation per rule, asserting
   zero and non-zero respectively. *Alternative (a `openspec/tests/governance/` pytest
   file) rejected to avoid an extra registered structural path.*

5. **Rule scope: ADR index ↔ directory, entry-chain relative links, UTF-8/trailing
   newline.** These are the unguarded, mechanical drift classes. Line budgets and the
   CLAUDE import contract are deliberately out of scope (already enforced).

## Risks / Trade-offs

- **[ADR index prerequisite]** The checker's index rule needs `docs/adr/README.md` to
  exist. → It is authored as `_backlog` work before apply; the checker reports a clear
  "index missing" (non-zero) rather than skipping silently.
- **[False positives on anchors/external links]** Markdown links may target headings
  (`#anchor`) or `http(s)` URLs. → The link rule ignores `http(s)`, bare `#...`, and
  mailto targets; only relative file targets are resolved.
- **[Too strict → blocks unrelated work]** The checker is standalone, so a doc violation
  does not block archive; it only surfaces as a non-zero exit when run.
- **[Rule drift]** The checker's rule set is code, not prose. → PRS-020 + the registry
  row + the closeout task keep it discoverable; `--self-test` keeps it honest.
- **[Budget surface creep]** Re-checking already-owned line budgets would duplicate
  `check_change_guidance.py`. → Deliberately excluded (Non-Goal).
