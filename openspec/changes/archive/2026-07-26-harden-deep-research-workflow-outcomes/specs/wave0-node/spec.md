## ADDED Requirements

### Requirement: Wave0 retains classified invocation causes through work-unit failure

Wave0 SHALL normalize every non-successful worker invocation before passing it to
the existing work-unit controller. It SHALL map tool failures, structured-output
failures, and invocation failures to the existing closed worker categories, retain a
safe provider category in the bounded attempt/event observation when known, and let
the controller own retry, aggregation, gate routing, and terminal projection.

#### Scenario: A Wave0 provider timeout remains visible to the controller
- **WHEN** a Wave0 worker receives a safe provider timeout result
- **THEN** it produces the existing closed invocation failure category plus the safe
  provider observation for the bounded attempt record, without accepting a candidate
  or raising an unclassified generic exception
