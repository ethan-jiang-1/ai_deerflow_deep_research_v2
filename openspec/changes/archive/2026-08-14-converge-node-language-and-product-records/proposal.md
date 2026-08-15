## Why

The application has completed its node-capability migration, yet the current
request contract and product records still retain a legacy/required dual mode and
the retired imported-actor identity. `CONTEXT.md` also repeats design and lifecycle
records owned elsewhere, making the glossary a second authority. This change
converges the closed current contract and its language without expanding an
application-internal surface into a public compatibility promise.

## What Changes

- **BREAKING (application-internal):** remove the legacy/required capability selector
  and require one validated `NodeAgentCapabilityRef` for every request. A missing,
  invalid, or package-mismatched ref is rejected before final prompt text is
  returned, tool resolution, model construction, or agent construction; no generic
  or legacy fallback remains.
- Replace the current imported-actor identity only where it names the current
  product, model-visible program, or runtime/governance mechanism. The bounded term
  table is: `LLM-Bearing Node` for product identity, `Node Cognitive Control
  Program` for model-visible local cognition, and `node-agent` for the runtime and
  governance mechanism. Historical records and a logical workflow phase that is not
  an identity are not renamed by this change.
- Make `deep_research_harness/CONTEXT.md` a glossary of current definitions and
  `_Avoid_` distinctions only. Move any unique current route to the existing
  ADR/spec/policy owner before deleting duplicated design/status prose, and remove
  the dormant `Local-First Deployment` entry without rewriting ADR history or
  changing the separate local Cognitive Evaluation entry surface.
- Retain the distinct Evaluation Run Workspace, Evaluation Run Bundle, Cognitive
  Evaluation Review / Review Record, Evaluation Run, and product Run Bundle meanings;
  retain generated-projection freshness guards and archive/completed-backlog history
  as evidence-only records.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `node-agent-capabilities`: requests use one mandatory validated capability ref and
  the current specification no longer presents legacy cohorts or binding modes as
  current behavior.
- `node-agent-runtime`: the bounded runtime uses the current `node-agent` mechanism
  identity while preserving its existing deterministic execution and failure
  boundaries.
- `node-prompt-catalog`: the model-facing renderer is named and specified as a Node
  Cognitive Control Program path with mandatory capability policy composition.
- `cognitive-program-evidence`: current catalog/evidence terminology and request
  admission describe the closed capability-ref contract without changing the
  20-branch evidence obligation.
- `workflow-failure-outcomes`: failure prose uses the current `node-agent` mechanism
  term while preserving the existing phase-owned outcome boundary and all prior
  scenarios.
- `research-run-experience`: terminal presentation prose uses the current
  `node-agent` mechanism term without changing its typed lifecycle authority or
  retained-incident behavior.

## Impact

- Application-internal code and tests under `deep_research_harness/src/` and
  `deep_research_harness/tests/`, including the request contract, prompt renderer,
  node-agent bridge, agent factory, node policy resource, catalog evidence, and
  current-language assertions.
- The six listed OpenSpec capability deltas, their owned requirement/coverage records,
  terminology-bearing requirement/evidence registry rows, and focused deterministic
  evidence.
- `deep_research_harness/CONTEXT.md` plus existing ADR/spec/policy routes that own
  the retained glossary semantics.
- The root package export remains exactly `deep_research_tool` (with `__version__`);
  this change adds no export, entry point, third-party Python support promise,
  DeerFlow modification, or DeerFlow source browsing.

## Program Focus

- **Program outcome:** The application has one required node capability contract and one current terminology set, while its product glossary contains definitions rather than duplicate design authority.
- **Candidate / obligation budget:** NC-C01, NC-C02, NC-C03, EC-C02, OR-C03, OR-C05, EV-C01, OR-C07, OR-C08
- **Declared workstream order:** node-contract-language, glossary-records
- **Program decision authority:** Post-migration convergence plan owner approves only this frozen budget, order, and whole-program archive closure; it owns no runtime fact, writer, or semantic workstream decision.
- **Shared archive invariant:** Both workstreams close with no current legacy/required capability selector or imported-actor identity, a glossary-only `CONTEXT.md` that retains all current distinctions and `_Avoid_` entries, unchanged ADR history, and evidence that the retained current guards still fail closed.
- **Program failure / recovery:** A failed workstream is forward-repaired within its declared writer scope, or that workstream and any dependent later workstream are rolled back to the pre-change invariant. If neither path closes the frozen budget, the program stays active for approved plan-level re-scope or whole-program rollback; no workstream partially archives.
- **Split / expansion rule:** No new Candidate, external Python compatibility support, runtime feature, DeerFlow boundary, or separate change enters this program. Any necessary expansion returns to the remediation map for explicit approval and preserves the eight-change budget.
- **Not in scope:** Altering `deep_research_tool` or the root package export; changing graph lifecycle, tool permissions, provider behavior, 20-branch evidence scope, evaluation data/import compatibility, generated-projection ownership, ADR history, archive/backlog facts, or DeerFlow.

### Workstream Focus: node-contract-language

- **Primary module / causal owner:** `domain/context.py` `NodeExecutionRequest`; it owns the application-internal request shape presented to the prompt renderer and node-agent bridge.
- **Seam classification:** cognitive-program because a typed request carries bounded cognitive policy into deterministic prompt admission, while graph lifecycle and state authority remain outside this workstream.
- **Question:** How can every LLM-bearing request use one validated local capability ref and one current terminology set without adding a public Python compatibility promise or changing deterministic runtime ownership?
- **Necessary adjacent/external contracts:** `agents/phase_prompt.py` and `agents/capabilities.py`: whether a ref is admitted before any policy rendering; `runtime/node_agent_bridge.py`: whether failed admission occurs before tools, model, or agent construction; node catalog and capability requirements: whether all 20 branches retain explicit policy/evidence coverage; root package facade: whether these module paths carry an external support promise.
- **Evidence seam:** Request-construction and prompt-render tests paired with a bridge contract whose planted missing, invalid, and package-mismatched refs prove tool/model resolvers and agent construction are not reached; catalog joins retain the current 20-branch denominator.
- **Not in scope:** New node capabilities, changing tool posture or budgets, graph routes/state writers/recovery, external Python consumer support, root export changes, or a semantic evaluation of model quality.
- **Triggered review policies:** change-admission, node-agent-workflow-integrity, workflow-outcome-review, control-placement
- **Candidate / obligation IDs:** NC-C01, NC-C02, OR-C03
- **Target / retirement:** Require `NodeAgentCapabilityRef` on `NodeExecutionRequest`; retire the legacy/required capability selector, the imported-actor product/model/runtime identity, and their associated current code/spec/test/registry spellings.
- **Surface grade:** application-internal typed contract and AI-facing product language; clean break is permitted because the root facade, package metadata, documentation, and entry points do not promise these names to third parties.
- **Decision authority:** Node Cognition owner decides the request and terminology contract; the bridge and agents layers retain their existing deterministic execution/admission responsibilities, and the program authority does not substitute for either.
- **Negative path / recovery:** Missing refs fail at request construction; invalid or package-mismatched refs fail at prompt admission before tools/model/agent work. A failed migration restores the previous internal code as one unit before archive; no legacy fallback or inferred capability is introduced.

#### Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `NodeExecutionRequest` through the rendered local policy | node-agent | A selected LLM-Bearing Node follows its static Node Cognitive Control Program plus a graph-provided assignment; it cannot decide graph authority or its own capability | The typed ref and trusted assignment are bounded inputs; source/tool/model material remains untrusted data and cannot select a capability | Capability metadata states the existing posture; `RuntimeNodeAgentBridge` continues to enforce the resolved tool window, sandbox, and budgets | The node-agent returns the existing typed candidate; existing parser/evaluator/materializer and graph owners alone may admit it | Agents loader/prompt admission rejects invalid refs before invocation; bridge projects the existing bounded safe failure without retry or fallback being added | Request/prompt unit tests plus bridge tests with resolver/agent-construction spies and catalog evidence joins |

#### Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Missing, malformed, unknown, or package-mismatched capability ref | The typed request and agents capability loader determine admission; the bridge projects its existing safe invocation failure fact | No retry or inference is legal in this workstream; the graph/runtime's existing failure handling remains bounded as currently specified | Existing capability-admission failure, before tool/model/agent construction | Correct the graph-owned request builder or capability resource, then start a legal later attempt through existing graph control | Request/prompt and bridge negative tests prove both denial and zero tool/model/agent construction |

#### Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Capability selection for every node request | No cognitive candidate or human judgment may choose, infer, or override a capability; a graph builder supplies the typed ref | `NodeExecutionRequest` carries the direct ref; the agents-owned loader validates resource and metadata, then the bridge admits the validated policy before execution | non-bypassable | Every request has one valid local capability policy before rendering or runtime resolution; repair means correcting the declared builder/resource, never falling back to legacy | Removes the legacy/required discriminator and its duplicate renderer/bridge branches without creating another controller | Constructor, renderer, and bridge planted-negative tests; 20-branch catalog join |

### Workstream Focus: glossary-records

- **Primary module / causal owner:** `deep_research_harness/CONTEXT.md` glossary; it owns current product-term definitions and `_Avoid_` distinctions, not design decisions or behavior.
- **Seam classification:** wiring because this workstream repairs the route from glossary terms to their existing ADR/spec/policy owners without creating or modifying runtime control.
- **Question:** How can the product record retain the real evaluation and Run distinctions while removing duplicated design/status prose and dormant product direction without rewriting the owners' historical evidence?
- **Necessary adjacent/external contracts:** ADR 0002/0008 and the current entry documentation: whether Local-First history remains discoverable after its glossary entry is removed; ADR 0011 and local-context policy: where the node cognitive modification seam is routed; ADR 0022-0026 and cognitive-evaluation-suite spec: where review, rubric, execution, and immutable-record behavior remain owned; projection generators/guards: whether current generated records retain freshness protection; archive/backlog lifecycle: whether historical terms remain evidence-only.
- **Evidence seam:** A paragraph-to-owner ledger and documentation/term tests or deterministic scans showing each removed paragraph has no unique current rule, retained glossary terms remain present, and current generated-projection/archival guards remain intact.
- **Not in scope:** Changing ADR decisions/status payloads, Evaluation Bundle retention or Python import support, creating an evaluation review runtime, changing current entry behavior, rewriting archive/backlog evidence, or adding a fourth term registry.
- **Triggered review policies:** change-admission
- **Candidate / obligation IDs:** NC-C03, EC-C02, OR-C05, EV-C01, OR-C07, OR-C08
- **Target / retirement:** Retain glossary definitions and `_Avoid_` entries; retire the six non-glossary design/status tail sections and the dormant `Local-First Deployment` definition after their existing owners and current routes are verified.
- **Surface grade:** current documentation vocabulary with historical ADR/archive links; glossary definitions are current explanatory terms, while ADR and archive text remain historical evidence and are not rewritten.
- **Decision authority:** Product record owner maintains glossary scope; each existing ADR/spec/policy owner remains authoritative for its own decision, behavior, or routing; archive/backlog lifecycle owns historical evidence.
- **Negative path / recovery:** A missing owner, broken current route, lost canonical term, or stale generator check stops deletion. Recovery restores the affected glossary prose or supplies the missing route within this workstream before any archive; no historical record is altered to make deletion appear safe.
