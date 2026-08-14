# Clean-Cutover Matrix

This is the source-controlled clean-cutover inventory for
`converge-runtime-input-compatibility`. It enumerates only project-owned writers,
local readers, and repository evidence. It does not promise compatibility to an
unregistered DeerFlow host producer, deployment, AppConfig version, retained data,
or external Python consumer.

## Plan-Review Result

- The frozen obligation budget is exactly `EC-C05`, `EC-C07`, `PC-C07`, `RC-C04`,
  `EC-C03`, and `RC-C05`.
- Trusted-context and deployment-config remain independent decisions. The first
  owns marker admission at the envelope-to-tool boundary; the second owns provider
  classification and the selected-config endpoint observation. Neither workstream
  creates a shared runtime authority or compatibility switch.
- Every affected reader is in `deep_research_harness/`; no DeerFlow source reader,
  provider factory, AppConfig parser, host producer, or model factory enters scope.
- The current reader and focused-test seams agree with the approved negative paths,
  so no plan correction or additional ordinary task is required before implementation.

## Retired Inputs

| Obligation | Project-owned writer / reader | Retired input | Canonical replacement | No-support inventory boundary | Denial or omission outcome | Whole-reader hotfix/revert recovery |
| --- | --- | --- | --- | --- | --- | --- |
| `EC-C07` | `ResearchRunExperience` writes `non_interactive`; `tool._admitted_start_action_input()` reads trusted context | `disable_clarification=true`, alone or with canonical context | `non_interactive=true` plus the exact closed `non_interactive_policy` | Only source-controlled scripted writer and local lifecycle reader are inventoried; no host producer or caller context gains a support promise | `interactive_required` before Bundle publication, graph-policy write, sandbox/graph selection, or interactive fallback | An approved emergency change may restore the complete prior admission reader; it does not selectively re-enable the marker or rewrite context |
| `EC-C05` | Local AppConfig is consumed by `resolve_effective_provider()`; GraphHost and diagnostics use its local result | Any non-null legacy `checkpointer`, with or without `database` | `database` is the sole provider-classification input | Only the downstream classifier, GraphHost, diagnostics, and their tests are inventoried; DeerFlow parsing, provider factories, deployments, and config versions are not supported by this change | Shared redacted `legacy_checkpointer_unsupported` result before generic saver/provider opening; no legacy durability claim | An approved emergency change may restore the complete prior classifier and both GraphHost/diagnostics readers in parity; it does not select a legacy provider silently |
| `PC-C07` | Exact selected model config is read by `_configured_endpoint_authority()` | `openai_api_base` or `api_base`, alone or alongside `base_url` | Safe normalized selected-config `base_url` only | Only the downstream selected-config observer and its tests are inventoried; model construction, model-object reflection, endpoints, and AppConfig shapes remain outside this decision | No endpoint observation; aliases cannot change model, provider, retry, route, or lifecycle behavior | An approved emergency change may restore the complete prior local observer; it does not add an alias-specific runtime switch or make aliases authoritative |
| `RC-C04` | The three local readers above own their respective boundaries; operations documentation records the recovery procedure | No independent runtime recovery input exists | A separately approved complete reader hotfix/revert | The source inventory does not establish a host, deployment, AppConfig-version, or retained-data migration path | Recovery is unavailable in-process; normal operation uses the canonical input or removes retired configuration | Revert the complete affected reader with its paired tests and parity checks. A partial consumer restore, payload rewrite, or selective compatibility bypass is invalid |

## Retained Falsifiable Guards

| Obligation | Guard | Evidence seam | Why it is not a compatibility decision |
| --- | --- | --- | --- |
| `EC-C03` | Canonical marked input requires exactly the closed policy and cannot reinject it after start | Trusted-envelope-to-tool tests, including canonical positives and pre-mutation denials | It tests canonical admission integrity; it does not admit a retired marker or enumerate a producer |
| `RC-C05` | Provider/diagnostics parity and safe endpoint normalization/redaction stay fail closed | Provider/diagnostic parity and selected-config endpoint tests | It tests that local projections do not leak or become authority; it does not retain legacy config or endpoint aliases |

## Evidence Boundary

Focused deterministic tests prove the listed downstream readers and project-owned
writer only. Credentialed and external-runtime lanes were intentionally unrun: these
local reader cutovers have deterministic evidence, and an external lane would not
establish an unregistered host, deployment, AppConfig, retained-data, or consumer
compatibility promise. Those lanes do not expand the clean-cutover support surface.
