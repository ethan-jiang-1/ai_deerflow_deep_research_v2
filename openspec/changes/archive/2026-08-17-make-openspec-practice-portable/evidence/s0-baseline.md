# S0 Baseline

> Evidence role: pre-change and active-Change admission baseline; not implementation proof

## Pre-Change HEAD

- Active changes before this Program: none (`openspec list --json` returned an empty change list before proposal creation).
- Product entry: `openspec/product/deep-research.md`, 26 lines at `HEAD`; warning/hard budgets are 60/80.
- Change admission: ordinary `## Change Focus` and bounded `## Program Focus`; conditional Control Placement, Workflow Outcome, and Node Agent reviews are enforced by `check_change_guidance.py`.
- Governance commands return zero on a conforming tree and non-zero on a detected violation: `check_change_guidance.py`, `check_project_reqs.py`, `check_project_specs.py`, `check_project_architecture.py`, and `check_project_req_coverage.py`.
- Requirement owners affected here: `DRC-001`, `DRC-005`, `DRC-012`, `DRC-014`, and `PRS-009`; the new pending namespace is `PCG`.
- Glossary authority remains `deep_research_harness/CONTEXT.md`.

## Upstream Boundary

- `HEAD` gitlink and index entry: `66b9e7f21212490cf92fafac137542b9deb06615` at `deerflow`.
- `git submodule status -- deerflow` reported the same revision; the nested worktree emitted no porcelain entries at admission.
- These observations prove only unchanged metadata/worktree state; they do not approve a pointer change or prove upstream compatibility.

## Active-Change State

- The proposal is strict-valid and Change Guidance Program grammar passes.
- Before registry admission, `check_project_reqs.py` intentionally reported pending `PCG-001` through `PCG-006` as unregistered.
- S0 registers those identities without claiming implementation; all five governance checkers must pass before S1.
