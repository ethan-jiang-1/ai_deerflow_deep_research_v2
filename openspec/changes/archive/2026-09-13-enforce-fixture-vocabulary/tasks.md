## 1. Composition terminology guard

- [x] 1.1 Add a `compositionAlias` entry (`\bfull[- ]fake\b`, case-insensitive) to `ACTIVE_TERMINOLOGY_RULES` in `openspec/governance/check_project_specs.py`, and exempt `#### Scenario:` heading lines from that rule only. Verify: `python3 openspec/governance/check_project_specs.py` exits 0 on the current tree.
- [x] 1.2 Replace the residual alias prose in `openspec/governance/req-registry.yaml` `DPL-005` with `no legacy no-graph command alias`. Verify: no `full-fake`/`full fake` remains in the scanned authority surfaces.
- [x] 1.3 Add `openspec/tests/governance/test_terminology_rules.py` asserting the rule flags a planted `full-fake`, and does not flag a `full_fake` literal or a `#### Scenario: Full-fake …` heading. Verify: `python3 -m pytest openspec/tests/governance/test_terminology_rules.py -q` passes.

## 2. Capability rename

- [x] 2.1 `git mv openspec/specs/research-fake-cli-onboarding openspec/specs/research-fixture-cli-onboarding` and retitle the spec heading to `# research-fixture-cli-onboarding Specification`. Verify: the old path no longer exists.
- [x] 2.2 Update `openspec/governance/req-registry.yaml`: the capability comment and the `FCO-001`/`FCO-002` capability field. Verify: `python3 openspec/governance/check_project_reqs.py` exits 0.
- [x] 2.3 Update the two test references: `deep_research_harness/tests/assets/requirement_evidence.py` and `deep_research_harness/tests/contract/test_main_spec_requirement_sources.py`. Verify: `UV_OFFLINE=1 uv run --no-sync python -m pytest tests/contract/test_main_spec_requirement_sources.py -q` passes.

## 3. Program verification

- [x] 3.1 Run the root closeout gate: `python3 openspec/governance/check_project_gate.py --phase closeout`. Verify: exit 0.
- [x] 3.2 Run the application gate from `deep_research_harness/`: `UV_OFFLINE=1 make verify`. Verify: every lane exits 0.
