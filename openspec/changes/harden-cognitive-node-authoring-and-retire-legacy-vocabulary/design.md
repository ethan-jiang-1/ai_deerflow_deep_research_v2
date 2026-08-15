## Context

See `proposal.md` for motivation. The current glossary, Change Guidance, prompt catalog,
cognitive-program evidence board, and node readers already describe the two-part
LLM-Bearing Node model, but the route is not mandatory at node-authoring time. The
current terminology guard scans only selected current surfaces, leaving current
avoidance prose and all retained historical material outside its scope.

This change is documentation/governance wiring. It does not modify a runtime prompt,
LLM invocation, tool posture, candidate schema, parser, materializer, gate, graph
route, state, provider, or DeerFlow interface.

## Goals / Non-Goals

**Goals:**

- Make the node edit map the single compact first read for LLM-node authoring.
- Make the cognitive-program reading order and its six review questions visible from
  the Harness guide, Change Guidance root, and eight local LLM-node readers.
- Converge every checked-out tracked record on current terms and prove zero literal
  residuals with a real deterministic negative control.
- Reuse the existing prompt catalog and cognitive-program evidence board as the exact
  branch inventory, without adding a second registry.

**Non-Goals:**

- Change runtime model behavior, capability semantics, prompt content, or quality.
- Add an LLM controller, a new glossary, a global authoring handbook, or a runtime
  Markdown configuration surface.
- Modify or browse the `deerflow/` gitlink.

## Decisions

### One authoring gate, not another handbook

`node-edit-map.md` becomes the short routing surface. The product glossary remains the
definition authority; the local-context policy owns the cross-node checklist; each
`workflow.md` owns only its exact local links. This gives an author one initial route
without copying definitions or prompts into a new default document.

Alternative considered: add a detailed global prompt-engineering manual. Rejected
because it would be a second authoring surface, would drift from package-local prompt
composition, and would be loaded more often than the exact node context.

### Cognitive first, deterministic handoff explicit

The eight LLM-node reader projections -- Wave2 synthesis, HITL1, topic-planning,
Wave0, Wave1, targeted-evidence, readiness, and final delivery -- use one ordered
route: capability/contract, prompt/context, feedback/repair, proof/evaluation, then
deterministic handoff. The order is not a claim that every failure is cognitive. A
deterministic symptom names its typed/domain/graph owner and records why cognitive work
is not causal. The three non-model projections -- bootstrap, HITL2, and rerun -- retain
their existing reader interfaces without fabricated prompt sections.

Alternative considered: require a cognitive checklist in all eleven projections.
Rejected because it would misclassify intentional deterministic/human work as model
work and create misleading maintenance routes.

### A zero-residual working tree with a real test

The terminology guard enumerates the tracked working tree without extension, path,
archive, or backlog exclusions and scans raw bytes from every materialized ordinary
file or symbolic-link value. Gitlink entries are metadata pointers rather than project
text; the guard records their exclusion by mode instead of silently filtering a path.
Its test code constructs forbidden tokens from fragments, allowing the working-tree
scan to reach zero while still testing a planted residual. Archive and closed-record
cleanup changes only imported terminology; it preserves identifiers, paths, dates,
decisions, and validation facts. The imported external reference library is deleted
after link audit instead of translated into an alternate guide.

Alternative considered: exclude archive and backlog history from the guard. Rejected
because those tracked texts remain discoverable to Coding Agents and continue to teach
the wrong model.

### Existing inventories are the proof source

The prompt catalog is the source-faithful composition inventory and the cognitive
program evidence board is the twenty-branch review inventory. The change audits reader
links against those existing surfaces and only adds missing navigation or deterministic
proof. It does not mint a third prompt/capability registry.

## Risks / Trade-offs

| Risk | Mitigation |
| --- | --- |
| Terminology rewrites make historical records harder to compare with earlier commits | Preserve factual content and use Git history for the earlier wording; review archive/closed-record diffs separately |
| Broad textual scan creates false positives or misses files | Build the scan from `git ls-files`, use fragment-only test tokens, and plant violations in current, archived, and closed fixtures |
| More guidance becomes a competing authority | Keep the glossary, policy, map, and local reader roles distinct and test their links rather than copying detail |
| Authors treat the checklist as a prompt-only obligation | Require the deterministic handoff and existing lowest responsible proof/evaluation route in each reader |

## Migration Plan

1. Add red current-language and reader-route fixtures before editing guidance.
2. Update the map, entry routes, eight LLM readers, Charter/reader requirements, and
   associated contract tests.
3. Audit all direct branch capability/prompt/evidence routes; correct only missing
   navigation and proof links.
4. Remove terminology residuals and the imported reference library, then repair links.
5. Run focused contracts, governance checks, zero-residual scan, and full deterministic
   verification. Sync main specs and archive only after all checks are green.

Rollback before archive restores the whole change's guidance, record wording, and
deletions together. After archive, a discovered residual is repaired in a focused new
change; no compatibility terminology is restored.
