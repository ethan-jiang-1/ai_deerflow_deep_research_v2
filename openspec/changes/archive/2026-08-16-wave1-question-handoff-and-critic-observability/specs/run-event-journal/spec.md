> req: REJ-008

## Purpose

Make Wave1 critic review dispatch failures queryable by a fixed critic kind without
widening the Journal's observation-only boundary or retaining any raw critic output.

## ADDED Requirements

### Requirement: Wave1 critic boundary facts carry a closed critic kind

The current v3 `RunEvent` contract SHALL gain one bounded optional field
`critic_kind` whose closed values are exactly `source_diagnostic` and
`claim_verifier`. The field SHALL be present only on a `post_candidate` VALIDATION
fact whose phase is `wave1` and whose validation-code collection is drawn from the
named critic review boundary's canonical codes; it SHALL be absent from every other
event, and a Wave1 critic dispatch model/tool invocation-failure fact SHALL NOT carry
it. The critic kind SHALL be derived from the fixed dispatch assignment, never from
model output, prompt content, or validation detail. The Journal SHALL retain no raw
critic output, prompt, tool observation, URL, artifact path, or exception text for
that fact. Version-1 and version-2 records and v3 records written before this change
SHALL remain readable with the field absent, and the field SHALL remain an
observation with no admission, retry, gate, route, terminal, or lifecycle authority.

#### Scenario: A critic-boundary fact carries exactly one closed critic kind
- **WHEN** a Wave1 critic typed result fails the review-artifact validation boundary
- **THEN** the retained `post_candidate` VALIDATION fact carries the canonical code collection, the work/attempt correlation, and exactly one closed `critic_kind` matching the dispatched critic, with no raw output

#### Scenario: The critic kind is rejected outside the critic boundary
- **WHEN** an event for another phase, stage, or category attempts a `critic_kind` value
- **THEN** the Journal append or inspection boundary rejects it before persistence or projection

#### Scenario: Legacy records without the critic kind remain readable
- **WHEN** a Journal retains v3 events written before this change or v1/v2 records
- **THEN** inspection reads them with `critic_kind` absent and performs no migration or rewrite
