> req: FSI-001, FSI-002

## Purpose

Keep deterministic fixture implementations outside the deployable Deep Research source
package while preserving explicit, reproducible fixture recipes for tests and local demos.

## ADDED Requirements

### Requirement: Fixture implementation source is physically and package-wise separate

The project SHALL keep production Deep Research source exclusively beneath
`deerflow_research/src/deerflow_deep_research/`. Deterministic fixture implementations
SHALL live beneath `deerflow_research/src_fake/` in the distinct top-level Python package
`deerflow_deep_research_fixtures`; that package SHALL not shadow, extend, or share the
production package name. The production distribution, editable installation used by the
reflected runtime, and Docker source mount SHALL exclude fixture source. Production source
SHALL not import the fixture package; fixture source MAY import only the documented production
contracts permitted by the fixture-composition boundary below.

#### Scenario: Production wheel excludes fixture implementations
- **WHEN** the project builds or inspects its production distribution
- **THEN** it contains `deerflow_deep_research` and contains no
  `deerflow_deep_research_fixtures` module or fixture node implementation

#### Scenario: Reverse fixture dependency is rejected
- **WHEN** structural validation finds a production-source import of the fixture package or a
  production node package containing a fixture factory implementation
- **THEN** validation fails before the package is accepted or a graph is compiled

### Requirement: Fixture catalog is explicitly composed only by test and demo roots

The fixture package SHALL expose one complete deterministic adapter catalog and matching
fixture gate-definition catalog for the fixed logical topology, plus a test/demo-only recipe
factory that passes those paired selections through the documented
`ResearchGraphRecipe.from_adapters()` composition seam. The composition contract SHALL
deterministically identify which selected adapters require a gate; its gate-definition
selection SHALL contain exactly those logical names, with no missing, unknown, or extraneous
entry. A mixed test recipe SHALL start
from those fixture selections, explicitly overlay the named production real adapters, and
rebuild the gate selection from the final adapter choices, replacing or removing fixture gates
as required before it calls that seam. It MAY import
`ResearchGraphRecipe` solely for that call. A test or credential-free demo SHALL explicitly
load that catalog when it constructs a fixture or mixed recipe. A production composition root
SHALL not discover, import, or substitute that catalog. The fixture package SHALL not call
`ResearchGraphRecipe.all_real()` or `.create()`, or import `GraphHost`, a research action
handler, or a control host. Missing, duplicate, unknown, or incomplete fixture catalog entries
SHALL fail before graph compilation and SHALL not select a fallback adapter.

#### Scenario: Credential-free demo composes the fixture catalog explicitly
- **WHEN** a supported fake demo is selected in a checkout with the fixture source root
  enabled for that command
- **THEN** it runs the deterministic fixture lifecycle without model credentials, network
  access, or a production-to-fixture import

#### Scenario: Public assembly cannot fall back to fixtures
- **WHEN** a production or reflected composition root lacks fixture source or supplies an
  incomplete adapter selection
- **THEN** it fails with a bounded construction/configuration outcome before graph invocation
  and does not run a fixture node

#### Scenario: Mixed test composition pairs gate behavior explicitly
- **WHEN** a test composes fixture adapters with a named subset of production real adapters
- **THEN** it supplies the matching fixture and real gate definitions through
  `ResearchGraphRecipe.from_adapters()`, and a missing, unknown, extraneous, or
  adapter-mismatched gate definition fails before graph compilation

#### Scenario: Real ungated adapter cannot retain a fixture gate
- **WHEN** a mixed test recipe replaces a fixture adapter with a real adapter that has no gate
  contract
- **THEN** it removes the fixture gate before composition, and retaining that gate is rejected
  before graph compilation

#### Scenario: Fixture composition cannot gain public runtime authority
- **WHEN** fixture source imports a production runtime controller, action handler, or control host,
  or invokes a `ResearchGraphRecipe` factory other than `from_adapters()`
- **THEN** structural validation rejects that dependency before fixture code is used by a test or demo
