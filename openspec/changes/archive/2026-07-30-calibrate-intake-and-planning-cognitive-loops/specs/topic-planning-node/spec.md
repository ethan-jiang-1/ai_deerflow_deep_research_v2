> req: TOP-007

## ADDED Requirements

### Requirement: Topic-planning calibration keeps the confirmed profile authoritative

The initial and repair topic-planning policies SHALL expose model-visible criteria for
a decision-ready `TopicPlan`: each topic is scoped to the confirmed profile, every
must-answer question has an explicit binding, topics are distinct rather than
overlapping, and scopes, search dimensions, and exclusions contain no asserted
external research fact. The initial policy SHALL distinguish the required single-topic
profile from a bounded multi-topic profile. A degraded profile SHALL retain the
existing broader, conservative planning posture without inventing missing profile
requirements.

The repair policy SHALL receive only the same confirmed profile, invalid plan draft,
and compact validation facts. It SHALL preserve the profile boundary and shall not
retrieve evidence, add sources or requirements, assign stable identifiers, write
topic state, or select a route. The existing deterministic materializer remains the
sole owner of identifier derivation, duplicate and overlap rejection, complete
coverage validation, topic-registry publication, and exhausted routing.

#### Scenario: Confirmed constraints remain visible in a bounded plan candidate
- **WHEN** a confirmed profile contains multiple must-answer questions and explicit
  scope constraints
- **THEN** the planning request asks for a bounded, distinct topic candidate whose
  bindings and scope/exclusion fields account for those constraints without asserting
  sources, findings, identifiers, or lifecycle outcomes

#### Scenario: Degraded profile does not create new requirements
- **WHEN** planning receives a degraded confirmed profile
- **THEN** the request asks for broader conservative coverage of the supplied
  must-answer questions and does not use the absence of a dimension to fabricate a
  new profile requirement

#### Scenario: Repair cannot turn validation feedback into planning authority
- **WHEN** a topic plan fails coverage, duplicate, overlap, or structural validation
- **THEN** the one repair request is limited to the same profile and compact failure
  facts, and a still-invalid plan reaches the existing deterministic non-publication
  and exhausted outcome
