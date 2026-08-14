## MODIFIED Requirements

### Requirement: Cognitive evaluation paths have separate ownership

The Cognitive Evaluation contracts, Runner source, control surface, and ignored run
store SHALL retain their existing separate-domain semantics beneath
`deep_research_harness/`. Evaluation control and run paths SHALL not be accepted as
Deep Research Bundle discovery/control paths, and a root move SHALL not merge their
registries or storage areas. The exact structural registry SHALL retain the
`runtime/evaluation` directory and its supported `__init__.py` facade, but SHALL not
retain the retired `runtime/evaluation/contracts.py` re-export path. (`PRS-015`)

#### Scenario: Evaluation paths move without joining Deep Research discovery
- **WHEN** structural governance validates evaluation source and `evals/` paths after the move
- **THEN** they resolve beneath `deep_research_harness/` and remain outside Deep Research
  Run Bundle discovery

#### Scenario: Retired evaluation contract path is absent from the registry
- **WHEN** structural governance validates the registered evaluation paths after the compatibility cutover
- **THEN** it requires the supported facade, rejects an unregistered replacement, and does not enumerate `runtime/evaluation/contracts.py`
