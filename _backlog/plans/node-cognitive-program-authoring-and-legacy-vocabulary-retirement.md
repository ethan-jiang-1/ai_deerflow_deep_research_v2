# Plan: Node Cognitive Program Authoring and Legacy Vocabulary Retirement

> Type: architecture / terminology / authoring guidance | Updated: 2026-08-15 | Status: audit recorded; requires one governed OpenSpec change before implementation

## Problem

Deep Research is a LangGraph application with bounded LLM-bearing graph nodes. It is
not the earlier external Markdown-driven workflow from which some research material and
early implementation language were copied. When a Coding Agent sees that historical
vocabulary, it can mistake a node's cognitive work for conventional controller code,
edit deterministic routing or validation first, and omit the prompt, context, feedback,
or evaluation work that actually determines model behavior.

The existing architecture already makes the correct distinction:

- an **LLM-Bearing Node** has a **Node Cognitive Control Program** that proposes;
- its **Deterministic Control Boundary** admits legal tools, candidates, state, and
  routes;
- the graph's deterministic control is Python/LangGraph `StateGraph` code, not
  Markdown-driven control; and
- a behavior symptom starts at the cognitive-program seam before a parser, gate,
  route, or bridge is changed.

That distinction is presently too easy to miss. `node-edit-map.md` is intentionally
short, the guidance policy names only the first seam, and the node `workflow.md`
projections do not share a precise authoring/review checklist for the model-bearing
parts of a node. A Coding Agent can therefore read a node note, understand its route
and validation, and still fail to inspect the model-visible program.

## Audit Baseline

The audit used `git grep` over every tracked file, deliberately excluding the
`deerflow/` gitlink's source as required by the repository boundary. The two retired
external actor/control labels occurred in the following currently checked-out files.
Counts below are matching lines, not a claim that every occurrence is current
architecture.

| Surface | Matches | Meaning | Required disposition |
| --- | ---: | --- | --- |
| Current Harness | 3 | Two current imported-control-label avoidance statements and the test that requires the old-term note in the terminology map | Remove/rewrite the avoidance wording; replace the test with a current-surface prohibition |
| Current OpenSpec | 1 exact phrase; 1 hyphenated scenario-title exception | The terminology map names the retired labels; WFO-001 retains an old scenario title only for a prior modified-requirement validator constraint | Remove the map's legacy note; migrate the scenario title and delete its exception after validating the current spec contract |
| OpenSpec archives | 16 | Historical proposal, design, spec, and task evidence | Retain as archive evidence; exclude from current-authoring discovery and do not rewrite its historical account |
| Closed backlog plans and bug records | 35 | Completed decisions and incidents | Retain as closed evidence; not an authoring source |
| External migration reference library | 70 | Detailed imported workflow research, including the retired external mental model | Delete after proving no current guidance or implementation links to it |
| Active backlog | 0 before this plan | No active work used the labels | Keep that invariant; this plan intentionally avoids reproducing the labels |

There is no live Harness source symbol or active current OpenSpec identity using the
spaced retired actor label. The existing current-language test rejects the old symbol
variants from source, tests, selected main specs, the runtime policy, testing docs, and
the requirement registry. Its blind spots are `CONTEXT.md`, ADRs, `AGENTS.md`, Change
Guidance, and the external reference library; this is why two current avoidance
sentences escaped despite the supposed retirement.

Historical Git objects cannot be erased by a working-tree cleanup. The practical
terminal invariant is therefore: no current source, current product/governance docs,
current authoring route, or non-historical reference library teaches the retired
external model; historical OpenSpec and closed-backlog records remain isolated evidence,
not a compatibility or terminology source.

## Terminology Decision

The following are the only terms a current Coding Agent needs to use for this concern.

| Concern | Current term | Owner / first reading surface |
| --- | --- | --- |
| A graph node whose work includes an LLM invocation | **LLM-Bearing Node** | Product glossary in `deep_research_harness/CONTEXT.md` |
| The model-visible, node-local work program | **Node Cognitive Control Program** | Node Cognitive Control Contract, capability Markdown, prompt composition, model-visible context, and structured feedback |
| Code that constrains and accepts effects | **Deterministic Control Boundary** | Typed parser, validator, gate, materializer, domain owner, and Python/LangGraph graph control |
| Deterministic movement among legal nodes | **Python/LangGraph `StateGraph` control** | Graph builder, typed state, gate and route owners |

The retired external actor/control vocabulary is prohibited from current identity,
prompt/policy naming, code symbols, product or governance documentation, authoring
guidance, and test expectations. A current document may explain a concrete Python
controller only when it names that actual code owner; it must not use an imported
Markdown-control metaphor as shorthand.

No new compatibility alias, terminology translation table, or duplicate glossary is
permitted. `deep_research_harness/CONTEXT.md` remains the product-definition authority;
Change Guidance routes a maintainer to it but does not copy definitions.

## Cognitive Note Contract

Every note that directs or helps maintain an LLM-Bearing Node must make the cognitive
program visible before deterministic machinery. This is authoring and review guidance,
not runtime authority and not permission for a Markdown file to choose a route or
accept state.

### Capability Markdown: What To Review

For every direct model branch, its capability Markdown and actual prompt composition
must let a reviewer answer these questions without inferring them from a parser or
graph edge:

1. What user-serving cognitive responsibility does this branch own, and what useful
   candidate should it propose?
2. Which inputs are trusted facts, which are untrusted or incomplete evidence, and
   which facts are deliberately not shown to the model?
3. What bounded method, tool posture, source/evidence discipline, and uncertainty
   behavior should guide its judgment?
4. What candidate shape, evidence standard, limitations, and abstention/repair
   behavior make the response useful?
5. What structured feedback reaches the model after a rejected or incomplete
   candidate, and what does the repair attempt need to change?
6. Which deterministic owner validates, materializes, publishes, records, or routes
   the candidate after the model proposes it?

The contract must state bounded method and observable quality expectations, never
require hidden chain-of-thought disclosure. Deterministic code enforces safety and
admission; it cannot stand in for a missing cognitive role, evidence strategy, prompt
context, or feedback loop.

### Node Reader Note: Reading Order

Each LLM-Bearing Node's package-local `workflow.md` remains a concise, non-runtime
reader projection. For a cognitive symptom it must direct the Coding Agent through this
order before deterministic edits:

1. the branch's Node Cognitive Control Contract and capability Markdown;
2. the prompt builder and the exact model-visible context it composes;
3. the structured output, parser feedback, and repair path returned to the model;
4. the focused prompt/branch test and any applicable Cognitive Evaluation Case, Rubric,
   or retained review evidence; then
5. the separate deterministic admission, materialization, ledger, gate, and graph-route
   owners.

For a deterministic symptom, the same note must explicitly say why the cognitive
program is not the first owner. This preserves the existing seam classification rather
than treating every model-bearing node as a prompt-only system.

The reader note links to its authoritative source paths and must not reproduce a full
prompt, implementation listing, or a second behavioral specification. The shared
Change Guidance policy owns the checklist; node notes provide exact local links and
symptom routing.

### Change Admission And Review

An active change classified as `cognitive-program` must state a falsifiable cognitive
hypothesis, the affected branch/capability, and the narrow evidence that will show the
model behavior improved or the hypothesis was rejected. A deterministic-guardrail
change prompted by a node behavior symptom must state the evidence that the cognitive
program was inspected first and why it is not the causal owner.

Prompt text alone is not proof. Deterministic tests prove composition, bounds, and
admission; a Cognitive Evaluation Case/Review is required whenever the claim concerns
model judgment, evidence quality, or repair behavior beyond deterministic shape.

## Single Guidance Route And Ownership

This work strengthens existing owners rather than adding an instruction hierarchy.

| Fact or decision | Owner | Projection / guard |
| --- | --- | --- |
| Product vocabulary and two-part node model | `deep_research_harness/CONTEXT.md` | Current-language contract scans the complete current authoring surface |
| Cross-node authoring rule and Focus Card seam classification | `openspec/change-guidance/policies/local-context.md` and `principles.md` | Change Guidance checker plus proposal/contract tests |
| One-page symptom-to-first-edit navigation | `openspec/change-guidance/node-edit-map.md` | Compact current-only map; no legacy glossary content |
| Exact node-local reading paths | Package `workflow.md` reader interfaces | Reader-interface inventory and planted missing-path/section violations |
| Prompt/feedback composition and branch evidence | Existing prompt catalog, capability, and cognitive-program-evidence owners | Existing focused tests plus bounded evaluation evidence |

`deep_research_harness/AGENTS.md` should remain a compact entry point that links to
this route. It must not become a second checklist or a cached inventory of every node.

## Delivery Shape

Create one OpenSpec change after this plan is reviewed. Its primary causal owner should
be `deep-research-agent-charter`, because the failure is authoring/admission guidance
and current vocabulary, not a runtime behavior change. Necessary adjacent contracts
are expected to include `node-agent-reader-interface`, `node-prompt-catalog`, and
`cognitive-program-evidence` only where their exact reader or proof contracts must
change. The change must use a normal `Change Focus` card with `cognitive-program` only
if its own causal question is model-program authoring; terminology/route changes may
instead be `wiring` with a precise rationale.

The change must not modify `deerflow/`, turn Markdown into runtime control, add an LLM
controller, create a new global prompt handbook, or use a broad mechanical rename that
rewrites archive evidence.

## Implementation Sequence

1. **Freeze the scope with red guards.** Extend the current-language guard to scan all
   current product, architecture, authoring, and agent-entry surfaces. It must reject
   each retired external label and planted legacy code/document variants while excluding
   only archived OpenSpec, closed backlog evidence, and Git history. Remove the WFO-001
   scenario-title exception only after a red/green spec validation demonstrates the
   current title can change safely.
2. **Remove active terminology residue.** Make `node-edit-map.md` current-only; rewrite
   the two glossary/ADR avoidance sentences in current Python/LangGraph terms; migrate
   the WFO-001 title/body together; remove legacy test expectations; and delete the
   non-authoritative external migration reference library after a tracked-link audit.
3. **Make cognitive review executable.** Put the six-question authoring checklist in
   the existing local-context guidance, not a new top-level manual. Update every
   LLM-Bearing Node reader projection and every direct model-branch capability inventory
   that lacks the cognitive reading order or its exact links. Keep prompt source,
   context construction, feedback, deterministic handoff, and evaluation evidence
   separately named.
4. **Prove both absence and usability.** Plant a forbidden-term violation in each
   current-surface category; plant a missing capability/prompt/feedback/evaluation link
   in a node reader fixture; and show each is rejected. Run the narrow reader, language,
   prompt, evidence-board, and Change Guidance contracts before the full deterministic
   verification and OpenSpec validation.
5. **Close with a residual audit.** Re-run the tracked full-repository scan, classify
   every remaining legacy hit as immutable archive or closed historical evidence, and
   confirm the external reference library and all current-authoring hits are gone. Record
   any unavailable live evaluation separately; do not substitute a passing unit test for
   cognitive-quality proof.

## Risks And Controls

| Risk | Control |
| --- | --- |
| A lexical cleanup erases historical evidence or claims to erase Git history | Delete only the non-authoritative external reference library; preserve archived changes and closed plans as isolated history, and make the guard's scope explicit |
| A new checklist becomes a competing behavior authority | Keep definitions in `CONTEXT.md`, checklist ownership in the existing local-context policy, and node notes as links/projections only |
| Coding Agents respond by putting deterministic rules into prompts | Require an explicit deterministic handoff and review the code-owned boundary separately |
| Coding Agents respond by adding guards instead of improving cognition | Require the cognitive hypothesis/first-seam evidence for every relevant deterministic proposal |
| “Prompt engineering” becomes untestable prose | Pair prompt/context/feedback edits with deterministic composition proof and bounded cognitive evaluation when the claim is about judgment |
| The legacy-token allowlist grows silently | No current-surface allowlist; archive/closed-history exclusions are fixed, documented scope boundaries and every new exception requires a new approved change |

## Completion Criteria

- The current guidance path teaches only Deep Research/LangGraph terminology and uses no
  imported external actor or Markdown-control label.
- No current implementation, test expectation, product/governance document, current
  agent entry guide, main spec, or non-historical reference file contains a prohibited
  legacy label; a planted violation proves the guard detects it.
- The external migration reference library is absent and no current file links to it.
- Every in-scope LLM-Bearing Node reader note gives the cognitive-first reading order
  and exact source/proof links without becoming runtime configuration or a duplicate
  specification.
- Every in-scope capability/prompt change can identify the cognitive responsibility,
  input boundary, method/tool posture, candidate quality/uncertainty, feedback/repair,
  deterministic handoff, and appropriate deterministic/evaluation evidence.
- Focus Cards and closeout evidence distinguish a cognitive-program improvement from a
  deterministic boundary change, and the full verification/strict OpenSpec gates pass.

## Reopen Triggers

Open a focused correction when a current document introduces a retired external label,
when a Coding Agent cannot identify the cognitive program before editing a deterministic
owner, when a node note lacks a prompt/context/feedback/evaluation route, or when a
deterministic-only test is offered as proof of an asserted model-quality improvement.
