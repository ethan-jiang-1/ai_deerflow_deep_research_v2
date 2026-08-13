# Stage 7 N-002 Post-Archive Closeout

> Date: 2026-08-13
> Change: `2026-08-13-reconcile-policy-routing-cardinality`
> Status: **N-002 RESOLVED - ALIGNMENT AUDIT PLAN CLOSED**

## Change Applied

The archived change reconciled four current contributor entry points with the existing
Charter route:

1. `openspec/policies/README.md` selects every canonical policy whose route-table
   trigger applies;
2. `openspec/config.yaml` uses the same selection rule and preserves one primary
   module / causal owner;
3. `deep_research_harness/AGENTS.md` records every selected policy and the conditional
   review records those routes require; and
4. DRC-001 requires the same rule and adds scenarios for multiple applicable triggers
   and the guidance-only boundary.

The change did not modify policy triggers, Focus Card parsing, the Charter checker,
application code, runtime behavior, or `deerflow/`. It was archived at
[`2026-08-13-reconcile-policy-routing-cardinality`](../../../../../openspec/changes/archive/2026-08-13-reconcile-policy-routing-cardinality/).

## Post-Archive Evidence

| Check | Result | Proof limit |
| --- | --- | --- |
| Current-target wording search | No `one relevant policy` or `choose only the policy` match in the four current targets. | Does not erase historical audit/archive references. |
| `openspec list --json` | No active changes. | Does not create authority for a future change. |
| `openspec validate --all --strict` | `49 passed, 0 failed`. | Structural validation, not universal semantic equivalence. |
| `openspec doctor --json` | Healthy. | Root health only. |
| Charter checker and requirement coverage | Both passed. | Focus Card shape and ID-level coverage only. |
| `git diff --check` | Passed. | Whitespace only. |
| Pre-archive deterministic gate | `UV_OFFLINE=1 make verify` exited `0`: fast `2495 passed`; integration `237 passed, 4 skipped`; workflow `35 passed`. | No live, credentialed, release-E2E, Postgres, or real-Gateway-app evidence. |
| Gitlink metadata | Pointer remains `66b9e7f21212490cf92fafac137542b9deb06615`; nested worktree is clean; no gitlink diff. | Manual observation, not A-002 automatic protection. |

## Final Disposition

N-002 was the only current no-code authority conflict preventing the audit plan from
closing. It is now resolved: current contributor routing consistently selects every
actually triggered canonical policy, records selected policies as one comma-separated
Focus Card field, retains one primary causal owner, and leaves policies as
guidance-only rather than runtime authority.

The three remaining independent backlog items do not reopen this alignment audit:

| Item | Classification | Why it remains separate |
| --- | --- | --- |
| A-002 | `DEFERRED-CODE-CHANGE` | A future automatic gitlink/nested-worktree detector needs its own governance design. |
| A-004-T01 | `DEFERRED-TOOLING-CHANGE` | Misleading legacy scenario titles require validator support before a narrowly scoped rename. |
| A-009 | `OPTIONAL-HARDENING` | Stronger assertion-semantic traceability is not required by the completed alignment plan. |
