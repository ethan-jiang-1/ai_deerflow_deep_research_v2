# Apply Impact Inventory

## Snapshot

- Current HEAD before implementation: `754d5838d397ef938df8e0ca8f8b77393232067f`
- Discovery command: `rg -n 'research_id|bundle_directory|deerflow_research/' deerflow_research openspec`
- Exact token counts in that command's scope: `research_id` 1,898,
  `bundle_directory` 374, and `deerflow_research/` 756.
- The working tree contains only this untracked OpenSpec change at this checkpoint.

The command output is the complete raw inventory. The classifications below are the
implementation routing record for every hit: a source, test, configuration, active
specification, or historical archive falls in exactly one category.

## Lifecycle Authority

These are authoritative now and must be replaced, rather than translated at a public
adapter:

| Current surfaces | Current authority | Target disposition |
| --- | --- | --- |
| `src/deerflow_deep_research/tool.py`, `domain/lifecycle.py` | Public action schema, derived `research_id`, and result projection | Expose only `bundle_id` and action-specific `resume`/`refine` inputs. |
| `runtime/research.py`, `runtime/graph_host.py`, `runtime/checkpoint.py` | Conversation-derived checkpoint namespace and graph state | Replace with the runtime-owned Bundle lifecycle and Bundle-contained State adapter. Generic infrastructure probe remains separate. |
| `domain/state.py`, `runtime/human_input.py` | Durable graph/checkpoint State, current pending response, and terminal facts | Move the durable control payload to Bundle-local State; retain only typed transient graph delivery. |
| `runtime/session_lifecycle_binding.py`, `domain/session_lifecycle_binding.py` | Binding, owner index, and checkpoint reopen/selection | Remove as Deep Research control/recovery authority; retain only bounded observations where still useful. |
| `runtime/session_operations.py`, `domain/session_operations.py`, `runtime/session_workbench.py`, `domain/session_workbench.py` | Broker/index/session-reference discovery and control | Resolve only a trusted-scope Bundle directory plus Bundle-local State. |
| `runtime/run_session.py`, `domain/run_session.py`, `runtime/legacy_state_migration.py` | Retained manifest and legacy state recovery path | Observation-only or remove; never recreate State or a Bundle. |

## Bound Content Consumers

These occurrences carry a Run identity/path into real contained storage and must receive
one runtime-bound Bundle reference instead:

| Current surfaces | Classification | Target disposition |
| --- | --- | --- |
| `domain/bundle.py`, `domain/bootstrap.py`, `domain/work_units.py`, `domain/wave1.py` | Bound-content contract | Replace identity/path pairs with typed Bundle identity/reference and contained relative-path helpers. |
| `runtime/bootstrap_bundle.py`, `runtime/request_bundle.py`, `runtime/work_unit_storage.py`, `runtime/work_unit_store.py` | Bound-content writer | Bind every authoritative read/write to the selected Bundle and revalidate availability before I/O. |
| `engine/work_units/{kernel,validation}.py`, `graph/components/work_units.py` | Work/evidence path consumer | Remove caller `research_id` and physical locator overloads. |
| `graph/nodes/{bootstrap,hitl1,topic_planning,wave0,wave1,wave2_synthesis,targeted_evidence}/` | Graph/node consumer | Consume the runtime-bound Bundle context only; no node selects a root/checkpoint. |
| `src_fake/deerflow_deep_research_fixtures/` | Fixture-only bound-content consumer | Keep fixture source isolated while it uses the same public Bundle contracts. |

## Projections And Evidence

These hits do not own lifecycle facts, but must migrate vocabulary and assertions so no
adapter-local authority survives:

| Current surfaces | Classification | Target disposition |
| --- | --- | --- |
| `domain/run_experience.py`, `runtime/run_experience.py`, `runtime/projection.py`, `runtime/run_diagnostics.py` | Typed projection | Consume one Bundle lifecycle result, including `unavailable` and legal next action. |
| `scripts/{_demo_core,demo,demo_real,demo_sessions,demo_tui,_terminal_failure_presentation}.py` | CLI/demo projection | Project `bundle_id`; do not derive a session, path, or recovery route. |
| `config/public-skill/`, `config/agent-template/`, `README.md`, `docs/`, `run/README.md` | Public/operations documentation | Describe Harness, Run Bundle, active/ended/unavailable, and distinct `resume`/`refine` behavior observationally. |
| `tests/**` and `tests/fixtures/**` | Deterministic evidence and test adapters | Replace old identity fixtures with Bundle-scoped cases; retain negative legacy-input tests only where strict schema rejection requires them. |

## Structural Consumers

All active `deerflow_research/` path hits in the module guide, `CLAUDE.md`, Makefile,
Docker configuration, profiles, scripts, tests, root-level documentation, OpenSpec main
specifications, requirement/evidence governance, and `project-structure.toml` are
structural consumers. They move together after the registry and generated locator are
updated. The Python distribution, `deerflow_deep_research` import namespace, and
`deep_research` public tool are unaffected names, not old-root aliases.

## Historical And Unaffected Hits

- `openspec/changes/archive/**` records historical behavior and paths. It is retained
  unless an active command or current contract would link to the obsolete root.
- Generic `infra_probe` checkpoint handling and Cognitive Evaluation workspaces are
  unaffected domains. They must remain discoverable only through their own contracts,
  never as Deep Research lifecycle recovery.
- Ordinary lexical uses such as a list `index`, model prompt wording, or generic
  checkpointer documentation are unaffected unless they select/restore a Deep Research
  Run. The accepted-contract audit records the decision for the active requirements.

## Completion Test

After the root move, task 8.2 reruns the raw command against `deep_research_harness/`
and `openspec/`. Every remaining match must be either an intentional archived historical
record or a named negative/detector case; no active lifecycle, content, configuration,
or structural consumer may retain the retired authority.
