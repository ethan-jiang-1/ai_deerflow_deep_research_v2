> req: EVH-021

## ADDED Requirements

### Requirement: Readiness critic activation has distinct conformance and judgment evidence

The active readiness critic branch SHALL retain separate collected evidence for
deterministic request/policy/candidate/route conformance and for bounded answerability
judgment. Scripted zero-API tests SHALL exercise the real readiness request, Node Agent
policy, candidate validation, conservative failure projection, materializer, and route
owner without claiming model quality. A separate bounded labeled evaluation corpus
SHALL assess supported, insufficient, and repair-required answerability judgments;
credentialed live execution is supplemental, explicitly selected, and reports only its
declared judgment disposition.

#### Scenario: Scripted conformance does not claim judgment quality
- **WHEN** a scripted readiness critic completes through the real policy and node path
- **THEN** its evidence claim is deterministic workflow conformance and not a live
  answerability-quality result

#### Scenario: Labeled answerability evaluation remains bounded
- **WHEN** a selected readiness evaluation case is assessed
- **THEN** it declares its question/evidence boundary, expected verdict class,
  criterion, permitted degradation, and whether live execution produced an assessable
  candidate without asserting evidence truth or research quality

#### Scenario: Failure projection has a direct deterministic proof
- **WHEN** model, policy, or structured-output failure is injected at the readiness
  branch seam
- **THEN** a collected deterministic test proves it cannot produce an all-ready result
  or bypass the existing repair/terminal owners
