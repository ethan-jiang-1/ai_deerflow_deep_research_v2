> req: TOP-009

## ADDED Requirements

### Requirement: Topic planning records canonical parser and materialization evidence

After an initial or existing one-repair topic-planning model result reaches the planner
parser and deterministic materializer, the node SHALL publish one Journal validation
fact for that stage. A successful parser/materializer result SHALL publish an empty
code collection. A failed result SHALL publish only one or more codes from this closed
set: `topic_plan_empty`, `topic_plan_json_invalid`, `topic_plan_extra_fields`,
`topic_plan_invalid`, `topic_count_profile_mismatch`, `topic_coverage_empty`,
`topic_duplicate_slug`, `topic_overlap`, `topic_coverage_uncovered`, and
`topic_materialization_invalid`. The node SHALL collapse dynamic field paths, coverage
question text, parser messages, and validation exception detail to the applicable
closed code.

The initial and repair facts SHALL remain separately correlated to the same phase and
their order of occurrence. A model/provider invocation that fails before it produces a
candidate reaches no parser/materializer fact and retains its existing invocation or
provider-recovery behavior. This evidence SHALL not add a repair, alter the existing
one-repair bound, change planner-owned checkpoint materialization, or affect its
exhausted route. (`TOP-009`)

#### Scenario: Initial malformed topic plan is repaired with two validation facts
- **WHEN** an initial planner result reaches parsing or materialization with an invalid
  candidate and the existing repair result reaches validation
- **THEN** the Journal records an `initial` fact with only the applicable closed code
  and a distinct `repair` fact with its own empty or closed code collection

#### Scenario: Valid initial plan records a successful validation fact
- **WHEN** an initial planner candidate parses and materializes into the existing
  accepted bounded topic registry
- **THEN** the Journal records one `initial` validation fact with an empty code
  collection and does not invoke repair

#### Scenario: Dynamic validation detail cannot escape into the Journal
- **WHEN** a planner materialization failure includes a question, field path, or
  exception-rendered detail
- **THEN** the Journal retains only the corresponding closed canonical code and the
  existing planner/controller behavior is unchanged
