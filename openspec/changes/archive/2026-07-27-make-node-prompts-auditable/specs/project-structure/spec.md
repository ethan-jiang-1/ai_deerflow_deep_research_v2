> req: PRS-011

## ADDED Requirements

### Requirement: Prompt catalog paths have canonical ownership and registration

The project structure registry SHALL register the agents-owned final-prompt renderer,
the graph-owned canonical prompt-case registry, the prompt-dump script, its focused
deterministic tests, and the committed `agent/node_prompts/` generated-artifact root.
The agents renderer SHALL retain its existing allowed import direction and SHALL not
import graph or runtime code; the graph case registry SHALL not render or invoke an
agent. The generated artifact root SHALL remain a review projection rather than a
source or runtime authority. (`PRS-011`)

#### Scenario: Architecture governance recognizes prompt catalog ownership
- **WHEN** the architecture checker scans the prompt renderer, graph catalog,
  generator, tests, and generated catalog root
- **THEN** it accepts their registered paths and import directions without granting
  generated Markdown execution authority
