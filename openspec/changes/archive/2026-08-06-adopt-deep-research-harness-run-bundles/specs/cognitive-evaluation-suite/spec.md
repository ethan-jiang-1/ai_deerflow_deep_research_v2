> req: CES-008

## ADDED Requirements

### Requirement: Cognitive Evaluation Bundles remain a separate domain after the Harness move

The Cognitive Evaluation Suite SHALL retain its distinct evaluation control surface,
evaluation-run workspace, and immutable Evaluation Run Bundle semantics under the
canonical `deep_research_harness/` project root. A Cognitive Evaluation Bundle SHALL
not be a Deep Research Run Bundle, Current Bundle Handle target, scoped discovery
candidate, lifecycle State source, or recovery source. Deep Research Bundle loss SHALL
not alter evaluation records, and evaluation records SHALL not restore a lost Deep
Research Run. (`CES-008`)

#### Scenario: Separate evaluation record cannot recover Deep Research
- **WHEN** an Evaluation Run Bundle contains observations about a Deep Research execution whose Run Bundle was deleted
- **THEN** Deep Research control returns unavailable and evaluation data remains read-only evaluation evidence
