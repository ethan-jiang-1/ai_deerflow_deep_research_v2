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
| OpenSpec archives | 16 | Historical proposal, design, spec, and task evidence | Preserve the completed decision/evidence, but rewrite imported terminology in the checked-out archive to current terms |
| Closed backlog plans and bug records | 35 | Completed decisions and incidents | Preserve the completed decision/evidence, but rewrite imported terminology in the checked-out record to current terms |
| External migration reference library | 70 | Detailed imported workflow research, including the retired external mental model | Delete after proving no current guidance or implementation links to it |
| Active backlog | 0 before this plan | No active work used the labels | Keep that invariant; this plan intentionally avoids reproducing the labels |

There is no live Harness source symbol or active current OpenSpec identity using the
spaced retired actor label. The existing current-language test rejects the old symbol
variants from source, tests, selected main specs, the runtime policy, testing docs, and
the requirement registry. Its blind spots are `CONTEXT.md`, ADRs, `AGENTS.md`, Change
Guidance, and the external reference library; this is why two current avoidance
sentences escaped despite the supposed retirement.

Historical Git objects cannot be erased by a working-tree cleanup, but the checked-out
repository can and must be clean. The terminal invariant is therefore: no tracked file
teaches, names, or expects the retired external model. Archive and closed-plan records
keep their completed decisions and evidence while using current terms; the imported
reference library is deleted rather than translated into a new source of guidance.

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

## Adequacy Review

The current materials establish the right architecture but do not yet make it hard to
miss during implementation:

- `node-edit-map.md` has only a three-row symptom map. It correctly identifies the
  cognitive program as the first modification seam, but it has no preflight for writing
  a new LLM-Bearing Node and no ordered prompt/context/feedback/evaluation review.
- `deep_research_harness/AGENTS.md` links the map only after the conditional phrase
  “for a behavior symptom.” A Coding Agent adding or reshaping a node can start in a
  `node.py`, graph builder, parser, or test without ever taking that route.
- All eleven node reader projections share compact structural headings, and there are
  twenty capability Markdown resources. Their local content is often strong, but no
  shared reader contract requires each of the six LLM-Bearing Nodes to expose the full
  cognitive reading order. Some current reader notes lead with a node/materializer test
  and defer capability/prompt inspection, which recreates the deterministic-first habit.
- The current-language test protects terminology in selected source/spec/policy paths,
  but it does not prove that a newly written or changed LLM node has a cognitive contract,
  exact prompt/context/feedback links, or appropriate evaluation evidence.

The work is therefore not a prompt-writing campaign. It is an authoring-path repair:
the first file a Coding Agent reads must make the cognitive program visible, route it to
the real model-bearing sources, and explain exactly where Python/LangGraph control starts
and stops.

## Node Edit Map As The LLM-Node Authoring Gate

`openspec/change-guidance/node-edit-map.md` becomes the compact mandatory entry point
before a Coding Agent creates, changes, or reviews an LLM-Bearing Node. It remains
guidance only; it never becomes runtime configuration, state authority, or a second
node specification.

Its revised one-page shape must answer two distinct situations:

| Situation | Required first decision | Required reading order |
| --- | --- | --- |
| Writing a new LLM-Bearing Node or direct model branch | State the user-serving cognitive responsibility and its deterministic handoff before creating Python control | Cognitive Control Contract/capability, prompt and model-visible context, feedback/repair, proof/evaluation, then parser/materializer/gate/route |
| Changing an existing model-bearing behavior | Classify whether the fault is cognitive or deterministic; do not infer it from the first code file opened | Same cognitive order for a cognitive symptom; name the evidence that rejects cognition before a deterministic-only edit |
| Changing a deterministic or human-decision node | State why no cognitive program is the causal owner | Read its actual typed/domain/graph owner; do not add a prompt surface merely to satisfy the map |

The map must make the six cognitive-contract questions from this plan visibly
actionable, with links to the glossary and local-context policy rather than copied
definitions. `deep_research_harness/AGENTS.md`, Change Guidance's root route, and the
relevant reader-interface contract must describe the map as the first read for LLM-node
authoring, not merely an optional terminology reference.

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
controller, or create a new global prompt handbook. Its historical-document cleanup is
terminology-only: it preserves what was decided, changed, and verified while replacing
the imported mental model with the current project vocabulary.

## Implementation Sequence

1. **Freeze the scope with red guards.** Extend the current-language guard to scan every
   tracked working-tree surface, including OpenSpec archive and closed backlog records.
   It must reject each retired external label and planted legacy code/document variant.
   Keep the test's forbidden tokens assembled from fragments so the checked-out text can
   reach a literal zero-hit scan while the negative control remains real. Remove the
   WFO-001 scenario-title exception only after a red/green spec validation demonstrates
   the current title can change safely.
2. **Remove active terminology residue.** Make `node-edit-map.md` current-only; rewrite
   the two glossary/ADR avoidance sentences in current Python/LangGraph terms; migrate
   the WFO-001 title/body together; remove legacy test expectations; and delete the
   non-authoritative external migration reference library after a tracked-link audit.
3. **Clean every retained record.** Rewrite imported terminology in OpenSpec archive,
   closed-plan, bug, and remaining tracked materials without changing their factual
   decision, evidence, requirement ID, date, path, or recorded validation outcome.
   Delete rather than translate the external migration reference library. Prove every
   tracked link remains valid after the cleanup.
4. **Make the node edit map the first read.** Rewrite it as the current-only LLM-node
   authoring gate described above; give `AGENTS.md` and the Change Guidance root an
   explicit create/change/review route to it; and remove any wording that relegates it
   to a terminology lookup after code navigation has begun. Add a contract test with a
   planted missing authoring-gate route so that a future guide cannot silently demote it.
5. **Make cognitive review executable.** Put the six-question authoring checklist in
   the existing local-context guidance, not a new top-level manual. Update every
   one of the six LLM-Bearing Node reader projections and every direct model-branch
   capability inventory that lacks the cognitive reading order or its exact links. Keep
   prompt source, context construction, feedback, deterministic handoff, and evaluation
   evidence separately named. Do not impose this cognitive reading order on the five
   deterministic/human node projections.
6. **Prove both absence and usability.** Plant a forbidden-term violation in each
   current-surface category; plant a missing capability/prompt/feedback/evaluation link
   and a missing authoring-gate route in a node reader fixture; and show each is rejected.
   Run the narrow reader, language, prompt, evidence-board, and Change Guidance contracts
   before the full deterministic verification and OpenSpec validation.
7. **Close with a zero-residual audit.** Re-run the tracked full-repository scan and
   require zero literal hits in every checked-out file. Confirm the external reference
   library is absent, every retained record uses current language, and every link remains
   valid. Record any unavailable live evaluation separately; do not substitute a passing
   unit test for cognitive-quality proof.

## Risks And Controls

| Risk | Control |
| --- | --- |
| A terminology cleanup corrupts a historical decision or validation record | Preserve facts, dates, IDs, paths, and outcomes; rewrite only imported vocabulary, review each archive/closed-record diff, and rely on immutable Git commits for the prior wording |
| A new checklist becomes a competing behavior authority | Keep definitions in `CONTEXT.md`, checklist ownership in the existing local-context policy, and node notes as links/projections only |
| Coding Agents respond by putting deterministic rules into prompts | Require an explicit deterministic handoff and review the code-owned boundary separately |
| Coding Agents respond by adding guards instead of improving cognition | Require the cognitive hypothesis/first-seam evidence for every relevant deterministic proposal |
| “Prompt engineering” becomes untestable prose | Pair prompt/context/feedback edits with deterministic composition proof and bounded cognitive evaluation when the claim is about judgment |
| The legacy-token allowlist grows silently | No checked-out-file allowlist exists; the guard's test-only fragment construction proves a prohibited literal would still be detected |

## Completion Criteria

- Every tracked document, source file, test expectation, archive, and closed record uses
  only Deep Research/LangGraph terminology and contains no imported external actor or
  Markdown-control label.
- A full tracked-file scan has zero literal prohibited-term hits; a planted violation
  proves the guard detects it without retaining those literals in the working tree.
- The external migration reference library is absent and no current file links to it.
- The node edit map is the explicitly linked first read before any Coding Agent creates,
  changes, or reviews an LLM-Bearing Node; a planted route omission is rejected.
- Every in-scope LLM-Bearing Node reader note gives the cognitive-first reading order
  and exact source/proof links without becoming runtime configuration or a duplicate
  specification.
- Every in-scope capability/prompt change can identify the cognitive responsibility,
  input boundary, method/tool posture, candidate quality/uncertainty, feedback/repair,
  deterministic handoff, and appropriate deterministic/evaluation evidence.
- Focus Cards and closeout evidence distinguish a cognitive-program improvement from a
  deterministic boundary change, and the full verification/strict OpenSpec gates pass.

## Reopen Triggers

Open a focused correction when any tracked file introduces a retired external label,
when a Coding Agent cannot identify the cognitive program before editing a deterministic
owner, when a node note lacks a prompt/context/feedback/evaluation route, or when a
deterministic-only test is offered as proof of an asserted model-quality improvement.

## Progress

This checklist is the execution state for this plan. Mark an item complete only with its
named evidence recorded in the OpenSpec change or closeout record.

- [x] P1. Scan all tracked files, separate current, archive, closed-record, and external-reference hits, and record the zero-residual target.
- [x] P2. Review the existing node map, agent entry route, eleven reader projections, and twenty capability resources; record the cognitive-first authoring gap.
- [x] P3. Define the current LLM-node vocabulary, cognitive-note review questions, node-edit-map authoring-gate role, ownership boundaries, and completion criteria.
- [ ] P4. Create the single governed OpenSpec change with its primary owner, adjacent contracts, Focus Card, proposal, design, delta specs, and implementation tasks.
- [ ] P5. Add red terminology and authoring-route guards, including planted legacy-token and missing cognitive-reading-order violations.
- [ ] P6. Remove imported vocabulary from all tracked records, delete the external reference library, repair links, and demonstrate the full tracked-file scan has zero prohibited-term hits.
- [ ] P7. Promote `node-edit-map.md` to the mandatory LLM-node authoring entry route and update the agent guide, Change Guidance route, local-context policy, and six LLM-node reader projections.
- [ ] P8. Audit every direct model-branch capability/prompt/context/feedback/evaluation route against the six cognitive-contract questions and implement the needed note or proof corrections.
- [ ] P9. Run focused language, reader-interface, prompt, evidence-board, Change Guidance, governance, and full deterministic verification; record any unavailable live evidence honestly.
- [ ] P10. Sync approved main specs, archive the OpenSpec change, rerun post-archive checks, move this plan to `_done/_closed_plans/`, and commit the closeout.
