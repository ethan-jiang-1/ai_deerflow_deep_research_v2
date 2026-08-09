# Research: CLI/TUI Entry Integrity Repair Plan

> Date: 2026-08-09  
> Question: Does `cli-tui-entry-integrity-repair_plan.md` recommend the right repairs?  
> Scope: current Harness source, tests, OpenSpec main specs, and official `uv` docs.
> The `deerflow/` framework source was not inspected or modified.
> Status: **Closed 2026-08-09** — all five recommended changes were implemented,
> verified, synchronized to their main specs where applicable, and archived. This note
> remains first-party audit context for `CLS-033`; it is not an active proposal queue.

## Outcome

The repair plan completed through these archived changes:

1. `2026-08-09-restore-noninteractive-policy-propagation` closed validated policy
   admission and its durable graph/HITL projection.
2. `2026-08-09-restore-demo-graph-composition` preserved full-fake demos while adding
   a distinct deterministic fixture-graph route.
3. `2026-08-09-repair-rendered-inspection-command` made `inspect <bundle-id>` the
   parser, renderer, and documentation grammar, with process-level proof.
4. `2026-08-09-stabilize-local-entry-environment` made explicit setup and
   `make lock-check` the dependency-state owners; ordinary entries use the locked,
   no-sync runner and preflight missing extras.
5. `2026-08-09-document-entry-surfaces` added the bounded README route map and its
   DRC-006 documentation contract.

The complete deterministic gate, `UV_OFFLINE=1 make verify`, passed after the final
documentation change. All affected main specs are synchronized, `openspec list --json`
has no active changes, and the implementation plus plan closeout are recorded in commits
`5370548`, `23e3626`, `9cadf73`, `f41846f`, and `55569c2`.

## Verdict

The plan identifies three real P0/P1 defects and has the right high-level split by
causal owner: non-interactive policy propagation, demo composition, rendered
inspection command, local entry environment, and documentation map. Its evidence
ladder is also aligned with the repository's test policy.

Two amendments are required before turning it into OpenSpec proposals:

1. Do **not** say that changing `make demo-scripted` from full-fake to a fixture graph
   merely restores the current contract. Main specs require the existing full-fake
   behavior to remain unchanged. Either add a distinct fixture-graph command, or make
   the semantic replacement an explicit delta to `demo-pipeline` and
   `runtime-operations`.
2. `uv run --locked --no-sync` prevents automatic environment synchronization, but
   `--no-sync` implies `--frozen`; it does not prove that `uv.lock` is current. The
   ordinary-entry design needs a separate verified lock-consistency precondition (or an
   intentional, documented setup-time check), rather than treating that command as the
   whole invariant.

## Classification

| Plan recommendation | Result | Evidence and required refinement |
| --- | --- | --- |
| Shared trusted policy, normal public calls stay interactive, policy enters initial graph/checkpoint state | **Correct** | `runtime-operations` requires a complete policy for non-interactive start/resume and its initial-state propagation ([spec](../../openspec/specs/runtime-operations/spec.md#L9-L23)). The tool currently admits a complete policy but only when `non_interactive`/`disable_clarification` is also true ([tool.py](../../deep_research_harness/src/deerflow_deep_research/tool.py#L148-L156)); `ResearchRunExperience` passes policy without that flag ([run_experience.py](../../deep_research_harness/src/deerflow_deep_research/runtime/run_experience.py#L319-L332)); and `_initial_graph_state()` omits it ([bundle_graph.py](../../deep_research_harness/src/deerflow_deep_research/runtime/bundle_graph.py#L685-L725)). |
| Implement `auto_proceed` at HITL2 and retain policy through resume/restart | **Correct** | The owning spec explicitly requires HITL2 to route `proceed` under `auto_proceed` ([runtime-operations](../../openspec/specs/runtime-operations/spec.md#L25-L67)). HITL1 already consumes `auto_profile` ([hitl1 node](../../deep_research_harness/src/deerflow_deep_research/graph/nodes/hitl1/node.py#L794-L825)); HITL2 presently always uses its recommendation and never reads policy ([hitl2 node](../../deep_research_harness/src/deerflow_deep_research/graph/nodes/hitl2/node.py#L19-L28)). Resume invokes the existing checkpoint rather than forming fresh initial state ([bundle_graph.py](../../deep_research_harness/src/deerflow_deep_research/runtime/bundle_graph.py#L619-L657)), so initial-state projection is the appropriate durability point. |
| Use one typed action-input path rather than demo answering HITL itself | **Correct, needs tightening** | The specification names `ResearchActionInput`, but no type by that exact name exists in current source. The proposal should say **introduce a closed typed input or restore the equivalent existing boundary**, and define validation/ownership in its delta. It must not make the presentation `context` an authority. This follows the shared run-experience contract ([research-run-experience](../../openspec/specs/research-run-experience/spec.md#L12-L20)) and the tool's existing trusted-runtime admission boundary ([tool.py](../../deep_research_harness/src/deerflow_deep_research/tool.py#L163-L189)). |
| Build a demo runtime that owns recipe + executor + transport; fail closed if a real executor is absent | **Correct** | `DemoLifecycleTransport` currently binds only `adapter` and `host`, and calls `run_deep_research()` without `bundle_graph_executor` ([`_demo_core.py`](../../deep_research_harness/scripts/_demo_core.py#L430-L475)). The supplied host is explicitly only a generic probe host ([`_demo_core.py`](../../deep_research_harness/scripts/_demo_core.py#L680-L683)). `BundleControl` consequently takes its fallback suspension/completion path when no executor is supplied ([bundle_control.py](../../deep_research_harness/src/deerflow_deep_research/runtime/bundle_control.py#L190-L213), [bundle_control.py](../../deep_research_harness/src/deerflow_deep_research/runtime/bundle_control.py#L231-L253)). The all-real and fixture recipe factories exist but are not consumed by that transport ([`_demo_core.py`](../../deep_research_harness/scripts/_demo_core.py#L656-L677)). |
| Make the fake/scripted CLI execute a fixture graph | **Unsupported as a restoration claim; needs an explicit spec decision** | `demo.py` currently declares itself a **full-fake** demo and binds the generic host ([demo.py](../../deep_research_harness/scripts/demo.py#L1-L12), [demo.py](../../deep_research_harness/scripts/demo.py#L97-L124)). `demo-pipeline` specifically calls `make demo --scripted` a fake lifecycle ([demo-pipeline](../../openspec/specs/demo-pipeline/spec.md#L52-L55)), and `runtime-operations` requires hardening not to alter full-fake behavior ([runtime-operations](../../openspec/specs/runtime-operations/spec.md#L77-L83)). The README/local-operations use the word "fixture" for this route ([README](../../deep_research_harness/README.md#L18-L23), [local operations](../../deep_research_harness/docs/local-operations.md#L82-L94)), so the repository is inconsistent; documentation is not enough to redefine the behavioral contract. |
| Change the scripted default question to contain an explicit comparison pair and supported-language evidence | **Correct** | The non-interactive HITL1 policy must block a comparison without an explicit pair or a language needing a human choice ([runtime-operations](../../openspec/specs/runtime-operations/spec.md#L25-L59)). The current default, "two approaches to renewable energy storage," has no named pair ([demo_real.py](../../deep_research_harness/scripts/demo_real.py#L50-L102)); this explains why repairing policy admission alone may truthfully block. |
| Repair rendered `inspect <bundle-id>` command and prove it by subprocess | **Correct** | The canonical main-spec command includes `inspect` ([research-cli-onboarding](../../openspec/specs/research-cli-onboarding/spec.md#L220-L233)); the renderer produces that shape ([`_terminal_failure_presentation.py`](../../deep_research_harness/scripts/_terminal_failure_presentation.py#L99-L103)); but argparse accepts a single positional `bundle_id` and no `inspect` verb ([demo_sessions.py](../../deep_research_harness/scripts/demo_sessions.py#L73-L80)). Existing adapter tests assert only the string ([test_demo_run_update_adapters.py](../../deep_research_harness/tests/integration/test_demo_run_update_adapters.py#L88-L108)); existing inspection tests call `run()` directly ([test_demo_sessions.py](../../deep_research_harness/tests/integration/test_demo_sessions.py#L53-L75)). A process-level regression is therefore the missing evidence. README and operations currently document the incompatible one-argument spelling ([README](../../deep_research_harness/README.md#L113-L124), [local operations](../../deep_research_harness/docs/local-operations.md#L106-L117)). |
| Explicit setup owns dependency changes; supported ordinary CLI/TUI entry commands use locked, no-sync execution | **Correct, needs a sharper invariant** | `uv run` locks and syncs automatically by default; `--locked` errors on an out-of-date lock; `--no-sync` skips environment synchronization ([uv: Locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/#automatic-lock-and-sync)). Extras are opt-in and selected with `--extra` ([uv: optional dependencies](https://docs.astral.sh/uv/concepts/projects/sync/#syncing-optional-dependencies)). The current `install` installs `operations` and `demo-tui`, but omits the separate `demo-real` extra ([Makefile](../../deep_research_harness/Makefile#L7-L8), [pyproject](../../deep_research_harness/pyproject.toml#L15-L22)); most ordinary demo targets use bare `uv run` ([Makefile](../../deep_research_harness/Makefile#L43-L72)). Define the protected surface precisely as `uv.lock` and project `.venv`; demos may still create intended ignored run/diagnostic files. |
| Treat `--locked --no-sync` as enough to establish a good environment | **Incorrect** | Official CLI help for installed `uv 0.7.3` says `--no-sync` **implies `--frozen`**; dependencies are ignored and the lock is not checked/updated. In this checkout, `uv lock --check` fails with “lockfile ... needs to be updated,” yet `env -u VIRTUAL_ENV uv run --locked --no-sync --extra operations python -c ...` starts successfully. Therefore the plan must retain `make lock-check` as a separate gate/precondition. The current Makefile already defines that target ([Makefile](../../deep_research_harness/Makefile#L79-L80)). |
| Keep `make verify` deterministic; treat live canaries as supplemental | **Correct** | `make verify` includes governance, lock check, lint, assets, requirements, and deterministic test lanes ([Makefile](../../deep_research_harness/Makefile#L40-L41)). The testing policy calls it the complete deterministic gate, defines the authenticity ladder, and says live evidence cannot replace lower-level proof ([testing and evaluation](../../deep_research_harness/docs/testing-and-evaluation.md#L50-L89), [testing and evaluation](../../deep_research_harness/docs/testing-and-evaluation.md#L125-L166)). |
| One-screen README Entry Surfaces map; separate exact operations/architecture/spec authority; no new single-consumer registry | **Correct** | The charter assigns README an early reading map and routes exact operational/architecture/test material to focused docs ([agent charter](../../openspec/specs/deep-research-agent-charter/spec.md#L68-L103)). It requires a change affecting observable behavior to use its owning capability contract, not policy prose ([agent charter](../../openspec/specs/deep-research-agent-charter/spec.md#L164-L182)). The README is 124 lines and already has a smaller entry table ([README](../../deep_research_harness/README.md#L18-L43)); adding a concise replacement table is within the documented warning posture. |
| Current user/operator/TUI/workbench positioning | **Correct** | The product vocabulary explicitly calls Dedicated Agent + reflected tool the current user route, marks the Primary User TUI as planned, bounds the demo TUI to contributor/operator visualization, scopes the workbench to fixture profile, and calls the operator CLI an operational rather than versioned public contract ([CONTEXT](../../deep_research_harness/CONTEXT.md#L173-L210)). |

## Proven Versus Reported Facts

Static inspection proves the causal defects above: missing policy projection, the unused
recipe factories/no executor injection, the parser-renderer mismatch, omitted
`demo-real` installation extra, and unsafe automatic `uv run` behavior.

The following are **reported historical/runtime observations in the plan**, not
independently re-executed here: the credentialed `demo-real` “completed in 0.4 seconds”
trace, exact `85 passed` focused-suite count, and actual concurrent `.venv` contention.
They are plausible consequences of the verified code, but their exact timings/counts
need fresh, reproducible command transcripts in the owning change. Credentials were not
used for this research.

The lock defect *was* rechecked: `uv 0.7.3`; `uv lock --check` exited nonzero because
`deep_research_harness/uv.lock` needs updating. No lockfile, environment, source, or
framework file was changed.

## Required Proposal Edits (Resolved)

1. Change 2 preserved full-fake `make demo*` behavior and added a distinct
   fixture-graph command; no existing route was silently reclassified.
2. Change 4 separated the read-only ordinary-entry invariant from lock freshness:
   `make install` owns synchronization, `make lock-check` owns freshness, and entry
   preflight directs missing extras to setup.
3. Change 1 introduced the closed, validated policy input at the trusted tool boundary
   and projected it into checkpointed graph state.
4. Change 3 selected and proved the canonical `inspect <bundle-id>` grammar across the
   parser, renderer, README, and operations documentation.

## Sources

- OpenSpec main specs and Harness paths are cited inline at the claim they support.
- Astral official documentation: [Locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/), accessed 2026-08-09.
- Local command evidence: `uv 0.7.3 (3c413f74b 2025-05-07)`, `uv lock --check`, and a
  no-write `uv run --locked --no-sync` probe, run from `deep_research_harness/` on
  2026-08-09.
