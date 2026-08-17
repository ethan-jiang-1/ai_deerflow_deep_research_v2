# S0 Consumer And Ownership Ledger

> Evidence role: current non-archive consumers, compatibility posture, target owner, and retirement gate

| Current surface | Active consumers / bindings | Compatibility posture | Target owner | Retirement gate |
| --- | --- | --- | --- | --- |
| `change-guidance/README.md` | OpenSpec/Harness entries, config, governance checker/tests, charter and structure owners | Local navigation interface | local router | All active links use core/profiles/local routes |
| `principles.md` | router, manifest/test, closed evidence | Split by paragraph | core, profiles, local | One target owner per paragraph; no duplicate current prose |
| `node-edit-map.md` | router, Harness guide, product page, charter/structure owners, checker/tests/manifest | Semantic contract; filename not authority | `profiles/node-agent/node-agent.md` | `DRC-012` route plus non-model branch passes semantic-parity guard |
| ten `policies/*.md` files | router, config, checker/tests/manifest, charter | Canonical policy/review contract | core, profiles, or local | Enabled registry and active links point at one owner |
| `openspec/config.yaml` | native OpenSpec authoring and checker/tests | Local composition/path/grammar contract | project local | Portable prose linked, not copied; Program/budgets stay local |
| `product/deep-research.md` | OpenSpec/config/router/governance entries, Harness docs, checker/tests, charter/structure owners | Clean navigation cutover | `product/README.md` | Every current consumer updated; old path deleted; archives unchanged |
| `deep_research_harness/CONTEXT.md` | product and domain consumers | Persisting glossary authority | unchanged | Product README links it; no glossary body/authority moves |
| `project-structure.toml` | architecture checker/test and guide locator | Persisted exact structure authority | unchanged registry | New paths registered; no duplicate machine schema |
| `check_change_guidance.py` | governance CLI, Make/CI consumers, focused tests | Compatible CLI path/arguments/0-or-1 result | local wrapper | Pure grammar delegated; filesystem/product/local checks remain |
| `test_change_guidance_governance.py` | focused deterministic evidence | Reshapes with target contract | local governance tests | Kernel, composition, authoring, product, deletion negatives close |

Archive and `_backlog/_done/` references are historical evidence, not current consumers, and are not rewritten. No unresolved current consumer remains at S0; S2 and S3 reconfirm immediately before clean cutover.

## Final Paragraph And Rule Ownership

| Semantic block / registered policy identities | Final editable owner | Local binding / deletion disposition |
| --- | --- | --- |
| Principles; change admission; authority and projections; context selection | `change-guidance/core/change-practice.md` | Product-neutral; retired `principles.md` and corresponding thin policy files deleted |
| Control and recovery; human interaction integrity; participant outcomes; control placement; workflow outcome review | `change-guidance/profiles/workflow-control/workflow-control.md` | Independently selectable profile; five thin policy files deleted |
| Ordered authoring route; non-model work; node-agent workflow integrity | `change-guidance/profiles/node-agent/node-agent.md` | Complete seven-decision contract; `node-edit-map.md` and thin node policy deleted |
| DeerFlow downstream boundary | `change-guidance/profiles/deerflow-downstream/deerflow-downstream.md` | Framework-neutral downstream-boundary profile; thin policy file deleted |
| Local context; Program/operation extensions; information map; reader roles; path and line budgets | `change-guidance/local/deep-research.md` | Deep Research-only authority; local thin policy files deleted |
| Policy enablement and proposal/review admission | `openspec/config.yaml` plus `governance/check_change_guidance.py` | Local registry/wrapper only; portable documents do not gain repository authority |
| Requirement semantics (`PCG-*`, `DRC-*`, `PRS-*`) | Owning main spec/delta and `req-registry.yaml` | Guidance is a reader route, never the requirement authority |

The focused exact-member, missing-owner, retired-tree, stale-link, and semantic-parity
negative tests reject duplicate or absent editable owners. Every current block above has
one owner; no compatibility copy or unresolved current inbound consumer remains.
