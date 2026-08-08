# Phase 0 Apply Ledger

All checkboxes below are intentionally unchecked. They implement only this
change-local governance and reader-contract work; they do not create reader files or
runtime behavior. A source difference, unresolved product decision, or scope
violation stops the change rather than authorizing a compensating edit.

| Ledger ID | Deliverable | Owning task | Apply-time done condition |
| --- | --- | --- | --- |
| P-00 | `.openspec.yaml` | 3.2 | OpenSpec resolves this exact active change under the generated `spec-driven` schema. |
| P-01 | `proposal.md` | 2.3 | The product review leads; its 11 individual records and its separate audit evidence agree with source. |
| P-02 | `design.md` | 2.3 | The seven fields, authority boundary, audit-only rule, and successor boundary agree. |
| P-03 | `specs/cognitive-node-interface/spec.md` | 2.1 | CNI-001 through CNI-004 define only the future reader contract and its negative boundaries. |
| P-04 | `specs/node-agent-reader-interface/spec.md` | 2.2 | NRI-003 preserves the six existing reader obligations and defines coexistence only. |
| P-05 | `tasks.md` | 3.1 | The two source-audit tasks point to every individual node and branch row through their closed ledgers, without duplicating a task per row. |

## 1. Revalidate the closed source audit

- [x] 1.1 Run `cd agent && UV_OFFLINE=1 uv run pytest tests/graph/test_topology_and_implementation.py tests/contract/test_workflow_node_inventory.py tests/domain/test_node_agent_capability.py tests/graph/test_node_agent_capability_cohort.py tests/graph/test_bootstrap_node.py tests/unit/test_rerun_real.py tests/unit/test_hitl2_real.py tests/unit/test_readiness_real.py tests/unit/test_final_delivery_real.py`. Confirm the ordered 11-node topology, six current direct-model owners, 16 individual capability bindings, and five remaining current mechanisms.
- [x] 1.2 Reconcile every individual row of the Product Responsibility Review and Charter Model-Branch Evidence Appendix against that source audit. Preserve the separation of product responsibility, participation mode, commitment state, current mechanism, deterministic authority, and audit-only branch evidence.
- [x] 1.3 Reconcile every individual row of the 16-Branch Evidence Ledger against `tests/assets/node_agent_capabilities.py`, including its capability binding and production entrypoint. Do not replace an individual row with a node aggregate.
- [x] 1.4 If a denominator, current mechanism, capability binding, or source/spec observation differs, stop for a new Scope Card rather than editing a classification or future commitment by inference.

## 2. Capture the bounded reader contract

- [x] 2.1 Add CNI-001 through CNI-004 to `specs/cognitive-node-interface/spec.md`: the fixed future-reader fields and structure, separate closed audits, deterministic authority seams, and separately admitted deferred/conditional participation. Do not create a reader, checker, or runtime behavior.
- [x] 2.2 Add NRI-003 to `specs/node-agent-reader-interface/spec.md` to preserve the six current package-local reader obligations while defining their coexistence with a later all-node rollout.
- [x] 2.3 Reconcile `proposal.md` and `design.md` with both deltas: product responsibility remains first; current mechanism remains source-audited; direct-branch evidence remains audit-only; and future activation or reader rollout remains outside this change.

## 3. Perform one propagation and scope gate

- [x] 3.1 Re-read every change artifact as one contract. Confirm the seven field order, five structural headings, 11-node and 16-branch individual ledgers, deterministic authority boundary, and no implicit model, tool, route, state, lifecycle, checker, or reader-file work.
- [x] 3.2 Run `openspec status --change define-cognitive-node-operating-model --json`, `openspec validate define-cognitive-node-operating-model --strict`, `git diff --check`, `git diff --name-only -- agent backend frontend`, and `git diff --name-only -- openspec/specs`. Require strict validation and whitespace checks to pass, and the two excluded path checks to have no output.
- [x] 3.3 Record `git status --porcelain=v1 --untracked-files=all`. Confirm this change touches only its change-local OpenSpec artifacts; preserve unrelated existing work without incorporating it.
- [x] 3.4 Stop after the gate and present the result for explicit apply/closure direction. Do not archive, create a successor change, modify reader documents/checker, or write outside this change root without a new explicit instruction.
