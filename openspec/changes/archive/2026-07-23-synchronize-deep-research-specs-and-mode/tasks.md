## 1. Establish Red Tests

- [x] 1.1 Add failing lifecycle contract/unit tests for all-fake, mixed, and all-real `ResearchGraphRecipe` mode classification, including normal, status, resumed, terminal, and handler-denial projections. @impl REG-004, DPL-003
- [x] 1.2 Add failing demo CLI/TUI coverage that proves the all-real standalone recipe cannot return `implementation_mode=full_fake`, while the reflected public tool and fake demo remain `full_fake`. @impl DPL-003, RED-001
- [x] 1.3 Add minimal invalid-fixture tests for missing registry-owned header IDs, foreign header IDs, requirement-coverage reuse of ownership projection, missing/empty/archive-placeholder Purpose text, and forbidden historical terminology in active authority while archives remain excluded. @impl EVH-010

## 2. Implement Truthful Recipe Projection

- [x] 2.1 Define the closed `full_fake | mixed | all_real` lifecycle mode contract and add a pure `ResearchGraphRecipe` derivation from its normalized implementation map. @impl REG-004
- [x] 2.2 Thread the recipe-derived mode through every handler result path, including snapshot projection and handler denials, without persisting it in `ResearchState` or accepting it from caller/session input; retain generic top-level reflected-tool denials as default full-fake. @impl REG-004
- [x] 2.3 Update affected lifecycle, demo, TUI, bootstrap, HITL1, topic-planning, and Wave0 deterministic tests; preserve assertions that the default reflected public tool remains full-fake. @impl REG-004, DPL-003, RED-001, BON-005, HIN-005, TOP-005, WAN-005

## 3. Unify Requirement Governance

- [x] 3.1 Extend `check_project_reqs.py` with a pure active-main-spec ownership projection that validates registry capability ownership and exact pre-heading `> req:` declarations. @impl EVH-010
- [x] 3.2 Make `check_project_req_coverage.py` consume that ownership projection and preserve existing production-annotation and evidence checks. @impl EVH-010
- [x] 3.3 Extend `check_project_specs.py` to reject missing, empty, and archive-placeholder Purpose text while preserving its existing main-spec structural checks. @impl EVH-010
- [x] 3.4 Reconcile every active main-spec header with its non-retired registry-owned IDs, including the currently omitted DER, EVH, DPL, RED, REC, RER, RDO, and RWB IDs; update inaccurate registry descriptions and remove all orphan outcomes without retiring active behavior. @impl EVH-010
- [x] 3.5 Replace every archive-generated main-spec Purpose placeholder with a concise current-capability purpose; add/update focused governance fixtures for all new checker rules, including the active-terminology scan and its explicit current `full_fake` allowlist. @impl EVH-010

## 4. Replace Stale Active Documentation

- [x] 4.1 Keep the active delta specs as the sole pending authority for early-node mixed-prefix wording; when specs are synchronized/archived, replace the historical sentences with recipe-derived `mixed` mode rather than retaining parallel requirements. @impl BON-005, HIN-005, TOP-005, WAN-005
- [x] 4.2 Remove every numbered-change completion narrative, skeleton/phase-roadmap term, and superseded fake/real assertion from active main specs, registry descriptions, `agent/AGENTS.md`, and `agent/README.md`; retain `full_fake` only where it names the current all-fake recipe, fake-demo behavior, or public reflected-tool boundary. @impl EVH-010
- [x] 4.3 Replace `agent/AGENTS.md` chronological Current Status prose with a capability matrix covering all eleven node factories, standalone all-real demo selection, default public full-fake selection, and unchanged upstream boundary. @impl REG-004
- [x] 4.4 Update `agent/README.md` to match the capability matrix and lifecycle-mode vocabulary; retain explicit full-fake warnings only for the public tool and fake demo surfaces. @impl DPL-003, RED-001, REG-004
- [x] 4.5 Keep `agent/config/public-skill/deep-research-controller/SKILL.md` and `agent/config/agent-template/SOUL.md` as accurate current descriptions of the default public full-fake entry without historical terminology. @impl REG-004

## 5. Verify And Prepare Archive Evidence

- [x] 5.1 Run focused lifecycle/demo/governance tests, then `python3 openspec/governance/check_project_reqs.py`, `python3 openspec/governance/check_project_specs.py`, and `python3 openspec/governance/check_project_architecture.py` from the repository root.
- [x] 5.2 Run `cd agent && UV_OFFLINE=1 make verify`; record the deterministic evidence and ensure no live or release credential is required.
- [x] 5.3 Run `openspec validate synchronize-deep-research-specs-and-mode --strict`, `git diff HEAD --check`, and protected-path status checks confirming `backend/` and `frontend/` remain unchanged.
