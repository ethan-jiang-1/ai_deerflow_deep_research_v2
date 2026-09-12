# fixture-source-isolation Delta

> req: FSI-001, FSI-003

## MODIFIED Requirements

### Requirement: Fixture implementation source is physically and package-wise separate

The project SHALL keep production Deep Research source exclusively beneath
`deep_research_harness/src/deerflow_deep_research/`. Deterministic fixture
implementations SHALL live beneath `deep_research_harness/src_fixtures/` in the distinct
top-level Python package `deerflow_deep_research_fixtures`; that package SHALL not
shadow, extend, or share the production package name. The production distribution,
editable installation used by the reflected runtime, and Docker source mount SHALL
exclude fixture source. Production source SHALL not import the fixture package; fixture
source MAY import only the documented production contracts permitted by the
fixture-composition boundary below.

#### Scenario: Production wheel excludes fixture implementations
- **WHEN** the project builds or inspects its production distribution
- **THEN** it contains `deerflow_deep_research` and contains no `deerflow_deep_research_fixtures` module or fixture node implementation

#### Scenario: Reverse fixture dependency is rejected
- **WHEN** structural validation finds a production-source import of the fixture package or a production node package containing a fixture factory implementation
- **THEN** validation fails before the package is accepted or a graph is compiled

### Requirement: Fixture source remains separate under the canonical Harness root

Deterministic fixture implementations SHALL live only beneath
`deep_research_harness/src_fixtures/deerflow_deep_research_fixtures/`, distinct from
production source at `deep_research_harness/src/deerflow_deep_research/`. Production
wheels, editable runtime, Docker mounts, and Deep Research Bundle discovery SHALL not
import, include, or treat fixture paths/Bundles as production Run authority. (`FSI-003`)

#### Scenario: Fixture root cannot become a production or Bundle-discovery root
- **WHEN** structural or lifecycle validation encounters a fixture source/run location
- **THEN** it rejects it as a production source or Deep Research Run Bundle candidate while allowing explicit test/demo composition
