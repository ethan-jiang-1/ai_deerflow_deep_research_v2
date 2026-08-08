## ADDED Requirements

### Requirement: Targeted evidence retains classified invocation causes through work-unit failure

Targeted evidence SHALL normalize every non-successful worker or repair invocation
before it reaches the existing work-unit controller. It SHALL retain the applicable
closed worker category and safe provider observation when known, and it SHALL leave
retry, aggregation, target routing, and terminal projection with the existing
controller.

#### Scenario: A targeted worker timeout is not reduced to a generic worker error
- **WHEN** a targeted evidence worker receives a safe provider timeout result
- **THEN** it emits a classified work-attempt failure preserving the safe cause and
  does not write an accepted evidence artifact or advance the target loop
