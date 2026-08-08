> req: PRS-015
> structure: openspec/governance/project-structure.toml

## ADDED Requirements

### Requirement: Cognitive evaluation paths have separate ownership

The canonical project-structure registry SHALL enumerate the pure Cognitive Evaluation contracts
under `deerflow_research/src/deerflow_deep_research/domain/evaluation.py`, the Runner
source under `deerflow_research/src/deerflow_deep_research/runtime/evaluation/`, the
source-controlled control surface under `deerflow_research/evals/control/`, and the ignored
generated run store under `deerflow_research/evals/runs/`. Control artifacts SHALL include
only registered Cases, Rubrics, Review Protocol, schemas, and registries. Run material SHALL
include only isolated workspaces, Bundles, and Review Records. Python source, production
prompts, and control authority SHALL not be placed in the run store; generated run material
shall not be placed in the control surface or `tests/eval/`.

#### Scenario: Canonical evaluation roots pass architecture governance
- **WHEN** the project-structure checker inspects the evaluation implementation and content roots
- **THEN** it accepts the governed domain contracts, runtime source, `evals/control/`, and `evals/runs/` only at their declared downstream locations and rejects an upstream or second source root

#### Scenario: Control and run subtrees cannot be mixed
- **WHEN** a generated Bundle or Review Record appears below `evals/control/`, or a Case, Rubric, protocol, or Python source appears below `evals/runs/`
- **THEN** structural governance fails with the owning path violation

#### Scenario: Run output is local and ignored
- **WHEN** a Runner creates a fresh `evals/runs/` workspace or Bundle
- **THEN** the path is ignored by version control, while control declarations remain reviewable and source-controlled

#### Scenario: Existing pytest evaluation remains distinct
- **WHEN** normal pytest collection or deterministic verification runs
- **THEN** `tests/eval/` remains its existing deterministic selection and does not collect or execute the Cognitive Evaluation Suite's long-running Runner cases
