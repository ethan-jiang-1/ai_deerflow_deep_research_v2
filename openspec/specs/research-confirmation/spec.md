# research-confirmation Specification

> req: RCF-001

## Purpose

Provide one bounded, deterministic admission boundary between a model-led research
conversation and the facts that may direct active research, while preserving a
single actionable User Decision whenever those facts are not yet accepted.

## Requirements

### Requirement: Research Confirmation admits only user-authorized research facts

For an interactive complete current research proposal, Research Confirmation SHALL
receive that proposal together with an explicitly attributed current User Decision.
It SHALL return exactly one of these closed outcomes:

- Accepted Research Facts containing only the complete current proposal that the
  Primary User directly confirmed; or
- one outstanding User Decision containing the current or a complete revised
  advisory proposal and bounded feedback where needed.

The original research request remains user-provided authority outside this outcome.
A model-generated brief, semantic interpretation, unstated default, or arbitrary
candidate SHALL remain advisory and SHALL NOT itself become an Accepted Research
Fact. A semantic confirmation is eligible only when it represents a verified current
human response to the displayed proposal. A direct visible control or an exact
unambiguous local confirmation may take the same admission path without a model
interpretation. A revision SHALL become a new outstanding User Decision and require
a later explicit confirmation. This capability SHALL not own graph routes,
checkpoint writes, profile artifact persistence, provider failures, retries, or
terminal handling. (`RCF-001`)

The existing non-interactive auto-profile policy is outside this capability: it does
not present an interactive proposal or supply a Primary User Decision, and this
requirement SHALL neither recast it as accepted user facts nor alter its lifecycle.

#### Scenario: A model proposal remains advisory before user confirmation
- **WHEN** a complete proposal has been generated from a research request but no
  current User Decision confirms it
- **THEN** Research Confirmation returns one outstanding User Decision and no
  Accepted Research Facts

#### Scenario: A natural confirmation accepts only the visible current proposal
- **WHEN** a Primary User gives an exact clear confirmation or a verified semantic
  interpretation of one correlated reply confirms the current complete proposal
- **THEN** Research Confirmation returns Accepted Research Facts containing that
  unchanged proposal and no candidate-created route, artifact, or control value

#### Scenario: A complete semantic revision needs a fresh decision
- **WHEN** a verified human reply is interpreted as a valid complete revision of the
  current proposal
- **THEN** Research Confirmation returns one outstanding User Decision with the
  revised advisory proposal and no Accepted Research Facts

#### Scenario: Ambiguity preserves an actionable decision
- **WHEN** a reply is ambiguous, a semantic candidate is invalid, or the existing
  semantic path supplies bounded unavailable feedback
- **THEN** Research Confirmation returns the current outstanding User Decision with
  bounded feedback and does not infer a preference, accept a fact, or terminally
  resolve the research lifecycle
