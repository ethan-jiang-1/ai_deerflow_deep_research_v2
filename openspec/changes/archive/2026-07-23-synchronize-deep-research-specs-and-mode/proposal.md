## Why

Deep Research now has complete real and fake implementations for all eleven
logical nodes, while its public reflected tool intentionally remains a
full-fake development boundary. The main specifications, module guide, and
lifecycle projection do not consistently express that distinction: several
specifications retain archive placeholders or incomplete requirement headers,
and an all-real standalone demo is reported as `full_fake`.

This creates two risks: contributors are guided by historical phase status
instead of current capability, and users of the standalone real demo receive a
false safety label. The repository needs one mechanically checked specification
baseline and truthful recipe-derived lifecycle mode projection before further
Deep Research work is planned.

## What Changes

- Extend the existing requirement-traceability governance so complete main-spec
  Purpose text and requirement-header declarations are reconciled with the
  append-only requirement registry and requirement evidence collection.
- Repair the affected main-spec headers and replace archive-generated `TBD`
  Purpose placeholders, change-number chronology, superseded fake/real claims,
  and other archive-only terminology with concise descriptions of current
  behavior.
- Replace the chronological, stale `agent/AGENTS.md` status narrative with a
  current capability matrix that distinguishes node implementation availability,
  the all-real standalone demo recipe, and the deliberately full-fake public
  reflected-tool boundary.
- Make `DeepResearchControlResult.implementation_mode` derive from the
  resolved `ResearchGraphRecipe` and carry that immutable recipe fact through
  lifecycle projections. Full-fake public-tool responses remain `full_fake`;
  standalone all-real demo responses report an all-real mode.
- Add deterministic regression coverage for mode projection and specification
  governance, including a current-terminology audit for active authority. The
  lowest responsible seams are the lifecycle result projection and repository
  governance/documentation checks; no live provider or full-system acceptance
  evidence is required.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `research-graph-lifecycle`: Lifecycle results identify the implementation
  recipe that actually executed, while preserving the full-fake public entry
  contract.
- `demo-pipeline`: Standalone fake and real demo recipes surface their actual
  implementation mode through the shared lifecycle projection.
- `bootstrap-node`, `hitl1-node`, `topic-planning-node`, and `wave0-node`:
  Mixed-prefix requirements stop describing later real phases as permanently
  fake and use the recipe-derived mode contract instead.
- `research-demo-tui`: The standalone TUI's selected-mode label is tied to the
  shared lifecycle result, so its default all-real path cannot inherit the
  public full-fake label.
- `evaluation-hardening`: Existing requirement-traceability governance verifies
  that every main spec has a real Purpose and declares exactly its active,
  registry-owned requirement IDs.

## Impact

- Affected source: `agent/src/deerflow_deep_research/domain/lifecycle.py` and
  `agent/src/deerflow_deep_research/runtime/research.py`.
- Affected documentation: `agent/AGENTS.md`, `agent/README.md` where the
  capability boundary is described, and affected `openspec/specs/*/spec.md`
  main specifications.
- Affected governance and tests: `openspec/governance/check_project_reqs.py`,
  `openspec/governance/check_project_req_coverage.py`,
  `openspec/governance/check_project_specs.py`, the requirement registry, and
  focused agent contract/unit tests.
- No configuration, mount, restart, dependency, MCP, ACP, subagent, public-skill
  behavior, dedicated-Agent behavior, `backend/`, or `frontend/` changes are in
  scope. The public reflected tool continues to use the default full-fake recipe.
