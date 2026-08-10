> req: DPL-011, DPL-012

## ADDED Requirements

### Requirement: All-real demo admission binds one explicit configured model profile

Before an all-real demo composes its graph executor or the Bundle lifecycle admits a
Run, the trusted demo composition boundary SHALL resolve a non-blank
`DEERFLOW_DEMO_MODEL` selector to exactly one credential-backed registered model
profile. The selected profile SHALL be the only model configuration passed to the
all-real demo bridge; model choice SHALL NOT depend on registry order, credential
enumeration order, or a node-agent resolver's first-configured-model behavior.

Each registered profile SHALL carry one bounded version-controlled safe revision. A
material change to the profile's model binding or supported connector configuration
SHALL update that revision without putting the changed configuration value itself in a
Bundle or Journal. The revision is not an endpoint, credential, or deployment-environment
identifier.

An absent selector, unknown selector, or selector with other than one matching
credential-backed profile SHALL use the existing safe model-configuration prerequisite
failure. It SHALL create neither a Bundle nor an Event Journal, and SHALL NOT choose a
replacement model. The selector is a deployment/configuration input only: it SHALL NOT
become a graph route, checkpoint field, public lifecycle control, or model-visible
instruction. (`DPL-011`)

#### Scenario: Explicit selected profile enters one all-real composition
- **WHEN** an all-real demo starts with a supported selector and its corresponding
  credential
- **THEN** the preflight and composition resolve exactly that one registered profile,
  construct the all-real executor with it, and make its safe identity and declared
  revision available only
  to the Bundle-local Journal boundary

#### Scenario: Ambiguous or absent profile fails before Bundle admission
- **WHEN** an all-real demo has no selector, an unknown selector, or a test registry
  whose selector resolves zero or more than one credential-backed profile
- **THEN** it returns the existing safe model-configuration prerequisite result before
  graph construction, Bundle admission, or Journal creation and does not infer a model
  from configuration order

#### Scenario: Existing launcher policy remains explicit at the composition boundary
- **WHEN** a documented all-real launcher supplies its existing profile policy through
  `DEERFLOW_DEMO_MODEL`
- **THEN** the demo composition treats that exported value as the one explicit selector
  and does not add a second defaulting path

### Requirement: Profile calibration is bounded, explicit, and observational

Operator documentation SHALL provide a bounded calibration procedure that starts a
fresh all-real Bundle for one explicitly selected registered profile, uses the existing
scripted real-demo question and read-only Bundle inspection command, and records only
the resulting Journal evidence for later comparison. The procedure SHALL require the
operator to select each candidate profile explicitly and SHALL NOT automatically run a
model matrix, designate a qualified profile from one run, alter the configured default,
change a prompt or budget, or relax a graph contract. (`DPL-012`)

#### Scenario: An operator calibrates one selected profile
- **WHEN** an operator follows the documented calibration procedure with
  `DEERFLOW_DEMO_MODEL` set to one supported profile
- **THEN** the resulting fresh Bundle can be inspected through the existing read-only
  command for its redacted profile provenance and bounded execution facts

#### Scenario: Calibration evidence cannot select a model or control a Run
- **WHEN** a retained calibration Journal contains a success, failure, or repeated
  failure pattern
- **THEN** it supplies no lifecycle action beyond the existing typed outcome and no
  command or automation changes a default model, reruns a Bundle, or changes a budget
