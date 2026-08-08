> req: HIN-013

## ADDED Requirements

### Requirement: HITL1 brief expected output remains compatible with strict admission

Every initial and structural-repair HITL1 brief request SHALL advertise a JSON output
contract compatible with current strict `StructuredBrief` admission: `required_keys`
SHALL include every parser-required field and name only fields the parser accepts;
advertised closed enum values, canonical schema version, and documented value bounds
SHALL be parser-valid. Parser-defaulted fields need not be advertised as required. The
descriptor SHALL not advertise a model-output field that the parser forbids or cannot
persist. System-owned presentation-language constraints SHALL be expressed as an
instruction and validated from the accepted `brief_summary`; they SHALL not advertise
an unsupported `brief_summary_language` field.

The compatibility relation SHALL have deterministic fixture evidence: a valid object
formed from the advertised expected contract is admitted by the strict parser, while
an advertised-forbidden extra field is rejected before profile or checkpoint state is
written. This requirement preserves the existing two-invocation brief/repair bound,
existing typed `output.structured_invalid` outcome, and graph-owned blocked route.
(`HIN-013`)

#### Scenario: Expected brief fields are admitted by the strict parser
- **WHEN** a deterministic HITL1 fixture constructs a complete brief from the
  model-visible required keys, enum values, and bounds
- **THEN** strict `StructuredBrief` admission accepts it and HITL1 can present the
  resulting advisory proposal without adding a profile artifact

#### Scenario: Language constraint does not invent an output field
- **WHEN** the original request has an accepted Chinese or English output-language
  constraint
- **THEN** the HITL1 request instructs the required `brief_summary` language without
  advertising the unsupported `brief_summary_language` output key

#### Scenario: An unsupported field remains a bounded invalid candidate
- **WHEN** a model candidate contains an extra field not in the strict brief contract
- **THEN** HITL1 admits no partial profile or checkpoint state, follows only its
  existing bounded structural-repair/blocked behavior, and never treats that field as
  a language or lifecycle authority
