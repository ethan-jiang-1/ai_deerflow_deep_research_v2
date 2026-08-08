> req: TOP-006

## ADDED Requirements

### Requirement: Topic planning capability preserves confirmed-profile planning boundaries

The real topic-planning initial and structured-repair requests SHALL bind distinct
forbidden local capabilities. The initial candidate SHALL be evaluated only against
the checkpointed confirmed profile's coverage, bounded expansion, and non-overlap
contracts. The repair candidate SHALL receive only the original bounded assignment,
validation facts, and untrusted draft; it SHALL not introduce external facts, alter
profile authority, expose model-visible tools, or write a topic registry. Existing
parser/materializer and node recovery owners remain the only admission and outcome
authorities. (`TOP-006`)

#### Scenario: A valid plan preserves profile coverage without tools
- **WHEN** a scripted real planner produces a valid candidate for a confirmed profile
- **THEN** its request exposes no model-visible tool, the deterministic materializer
  records only a bounded covering non-overlapping registry, and the candidate itself
  supplies no route, stable id, or checkpoint authority

#### Scenario: Repair cannot extend the research assignment
- **WHEN** a malformed planner draft is repaired through the real planner node
- **THEN** the repair uses no tool and either yields a contract-valid plan constrained
  to the same profile or follows the existing exhausted outcome without topic state
