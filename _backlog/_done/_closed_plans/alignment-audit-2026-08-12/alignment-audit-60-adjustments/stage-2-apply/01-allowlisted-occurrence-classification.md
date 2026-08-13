# Stage 2 Allowlisted Occurrence Classification

> Change: `retire-stale-context-concepts`
> Apply date: 2026-08-13
> Status: **AUTHORIZED - BEFORE EDITS**

Every row below is within the approved allowlist. Any additional finding is recorded
separately and is not permission to enlarge this change.

| C ID | Source occurrence before edit | Classification | Current owner or evidence | Intended target | Risk control / stop condition |
| --- | --- | --- | --- | --- | --- |
| C-004 | `CONTEXT.md` Evaluation Run Workspace says it contains its Bundle | `relocate-owner` | Runner creates `workspace/` and `bundle/` as siblings; `cognitive-evaluation-suite` owns the distinct domain boundary | `deep_research_harness/CONTEXT.md` | State only owner and sibling relation; stop if storage/runtime change is needed. |
| C-005.a | `CONTEXT.md` calls the Suite `new` and says V1 structural work `must` update governance | `retire` | Existing `evals/control/`, ignored `evals/runs/`, Runner source, and `tests/eval/` are current | `deep_research_harness/CONTEXT.md` | Retain control/run-data separation; stop if a structural spec or ignore-rule change is needed. |
| C-005.b | `CONTEXT.md` names an archived change as the source of the seam discipline | `relocate-owner` | `openspec/policies/local-context.md` is the current route | `deep_research_harness/CONTEXT.md` | Preserve the current policy link; do not edit the archive. |
| C-007 | `openspec/CONTEXT.md` says the Charter routes to one policy; Charter says choose one policy | `retire` | Charter checker parses comma-separated canonical policies; charter main spec permits that form | `openspec/CONTEXT.md`, `openspec/agent-charter/README.md` | Preserve one primary owner and only actually triggered policies; stop if checker/config changes are needed. |
| C-008 | `CONTEXT.md` says every LLM-Bearing Node has a smoke scenario | `retire` | Versioned `evals/control/registry.json` enumerates current coverage | `deep_research_harness/CONTEXT.md` | State registry boundary only; do not add a case or roadmap. |
| C-009 | `CONTEXT.md` says `limited` and `inconclusive` require a readable report | `retire` | `cognitive-evaluation-suite` requires a structured Review Record and non-pass semantics, not a separate reader | `deep_research_harness/CONTEXT.md` | Keep four states and non-pass rule; do not claim a report experience. |
| C-010.a | `CONTEXT.md` presents Primary User report reopen/copy/export as current | `retire` plus `keep-current` artifact fact | `final-delivery-node` owns the `report.md` artifact | `deep_research_harness/CONTEXT.md` | Keep `final/report.md`; do not create or label a public export capability planned. |
| C-010.b | `CONTEXT.md` describes Support Handoff as current Bundle-local behavior | `planned` | No current producer, schema, or public entry; A-004 remains separate | `deep_research_harness/CONTEXT.md` | Do not define storage, retention, reader, or presentation semantics. |
| C-010.c | `CONTEXT.md` calls dedicated Primary-User TUI and Local-First route current/planned product surfaces | `dormant` | `deployment-configuration` owns current Dedicated Agent/reflected-tool route | `deep_research_harness/CONTEXT.md` | Keep demo/evaluation local surfaces outside this label; do not rewrite historical ADR bodies. |
| C-011 | Five ADRs present historical decisions without current applicability boundary | `dormant`, `planned`, `retire`, or `keep-current` by listed sub-decision | Design table names current route/spec links | Five listed ADRs | Append only; stop if existing byte prefix changes or a postscript would settle A-004. |

## Quarantined And Unlisted Material

- C-006 is withdrawn and has no target edit.
- A-003 Rubric/Runner authority and A-004 post-Bundle-loss diagnostic semantics remain
  quarantined to their named future changes.
- Duplicate or otherwise unlisted wording is not changed in this Stage 2 apply.
