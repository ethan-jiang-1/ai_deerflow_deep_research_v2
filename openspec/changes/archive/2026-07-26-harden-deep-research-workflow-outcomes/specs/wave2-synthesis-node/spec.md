## ADDED Requirements

### Requirement: Wave2 synthesis retains direct invocation incidents through gate handling

Wave2 synthesis SHALL normalize a non-successful initial or structured-output repair
invocation before its phase/gate logic decides the route. A known invocation failure
that terminally blocks SHALL retain a direct Wave2 incident; a failure eligible for
an existing bounded phase repair SHALL record that disposition without treating it
as successful synthesis. Raw exceptions and generic synthesis errors SHALL not
replace a known safe provider or configuration category.

#### Scenario: A Wave2 provider failure blocks with its known cause
- **WHEN** the Wave2 synthesis invocation returns a known non-retryable provider
  failure and no legal gate repair applies
- **THEN** the lifecycle retains that category and `wave2_synthesis` phase in the
  terminal incident instead of surfacing an opaque graph exception
