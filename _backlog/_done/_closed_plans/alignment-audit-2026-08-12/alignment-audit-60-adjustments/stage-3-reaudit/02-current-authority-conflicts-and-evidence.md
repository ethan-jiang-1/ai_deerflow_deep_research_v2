# Stage 3 Current Authority Conflicts And Evidence

> Date: 2026-08-13
> Status: evidence only; no specification or implementation decision made

## A-003: Rubric / Runner Authority Remains Conflicted

`cognitive-evaluation-suite` says a case-linked Rubric is available to review but
"SHALL NOT be an execution input" at
`openspec/specs/cognitive-evaluation-suite/spec.md:14-21`. The current glossary makes
the same review-only claim.

`evaluation-hardening` instead requires cognitive-program scenarios to declare rubric
criteria and requires admission to reject absent, duplicate, or invalid rubric data,
including at `openspec/specs/evaluation-hardening/spec.md:868-878` and the equivalent
Wave1/Wave2 requirements. Current admission implements that second contract:

- `runtime/evaluation/controls.py:34-38` invokes rubric verification while loading
  every registered case;
- `controls.py:80-113` reads the declared Rubric JSON, extracts criterion IDs, and
  rejects a mismatch against scenario `review_criteria`; and
- `domain/evaluation.py` makes `review_criteria` a typed scenario field.

This is a conflict over execution-admission input and control-integrity metadata. It
does not mean the Runner currently makes a quality verdict or supplies Rubric prose to
a model-facing node. Nonetheless, the unqualified CES prohibition cannot coexist with
the required parsing and validation behavior. A product decision is still required.

## A-004: Post-Loss Diagnostic Authority Remains Conflicted

`research-run-experience` says an external diagnostic may outlive Bundle loss and may
be presented as a safe category/reference while the lifecycle result remains unavailable
at `openspec/specs/research-run-experience/spec.md:73-85`. The glossary's `External Run
Observation` entry says the same at `deep_research_harness/CONTEXT.md:145-150`.

`research-run-session` and `run-event-journal` prohibit that behavior: diagnostics,
summaries, and Journal records remain inside the Bundle and inspection must not seek an
external Journal or Support Handoff after loss. See
`research-run-session/spec.md:62-78` and `run-event-journal/spec.md:128-149`.

Current behavior follows the Bundle-local side:

- the observation domain and store are constructed for a selected Bundle root;
- the deterministic failure contract exposes no legacy observation after Bundle loss;
- the integration lifecycle test deletes a Bundle, obtains `UNAVAILABLE` for both
  status and diagnosis, starts a fresh independent Bundle, and asserts no `.reports`
  external store exists.

Therefore A-004 is not merely future-policy ambiguity. One approved main spec and the
current glossary promise a category of post-loss observation that current implementation
and two other main specs exclude. The Stage 2 `planned` label for Support Handoff did
not decide this question and must not be read as external-retention approval.

## A-009: Requirement Coverage Is Deliberately Non-Semantic

`check_project_req_coverage.py` collects `@impl` IDs from module/class/function
docstrings for every parsed test file and compares the resulting set with main-spec
requirement IDs. It does not bind an ID to a particular assertion or inspect assertion
meaning (`check_project_req_coverage.py:39-70` and `138-153`). Passing coverage proves
ID-level deterministic-test inventory, not scenario-by-scenario semantic equivalence.

The stronger evidence catalog is intentionally selective:

- `evaluation-hardening/spec.md:98-100` requires central claims only for selectors
  referenced by policy or an explicit inventory; it forbids duplicating ordinary tests
  into an exhaustive second catalog.
- `validate_requirement_impacts` validates each listed impact but does not require an
  entry for every alive requirement (`requirement_evidence.py:1442-1487`).
- `validate_requirement_evidence` requires deterministic `@impl` for every alive ID
  and applies richer claim classes only to the explicit policy set
  (`requirement_evidence.py:1606-1644`).

This is an accurately disclosed evidence limit, not proof of missing implementations.
The candidate next action remains optional hardening: require a bounded semantic
mapping when a high-risk requirement is introduced or materially changed, without
turning the existing evidence catalog into a duplicate exhaustive test registry.

## A-002: Automatic Gitlink Protection Is Still Deferred

`openspec/config.yaml:83` requires manual gitlink/submodule/nested-worktree evidence
and explicitly disclaims automatic detection or protection. Current governance and
contract-test paths do not contain an automatic detector for the gitlink pointer or
nested DeerFlow worktree. The observed pointer remains unchanged and clean, but that
manual fact is not future protection.

This is still `DEFERRED-CODE-CHANGE`. It is neither resolved by documentation nor
within the authorized scope of Stage 3.
