# Execution Intent Specification

## Purpose

The optional research-intent declaration for non-interactive automatic runs and its
deterministic consumption: a declared minimal intent flows through existing channels
(minimal profile → the existing `single_topic` planner derivation; profile intent
fields in graph state → the wave2 gate budget resolver), while an absent intent keeps
today's behavior byte-identical. No envelope, recipe, or capability API change carries
the intent.

## Requirements

### Requirement: Non-interactive runs may declare research intent

The non-interactive start policy SHALL accept an optional `profile_intent`
(`minimal`; absent = today's behavior). The declared intent SHALL drive the
existing consumption channels: `minimal` yields the minimal profile (which the
existing `single_topic` planner derivation consumes — exactly one topic) and the
wave2 gate budget resolver (reading the HITL-owned profile intent fields in
state) yields two evidence rounds; absent intent keeps today's gate budget and
profile behavior. No envelope, recipe, or capability API change is made for
intent transport. (`EXI-001`)

#### Scenario: Minimal intent drives single-topic and the two-round gate budget
- **WHEN** a non-interactive start declares `profile_intent=minimal`
- **THEN** the planner is required to emit exactly one topic and the wave2 gate
  budget resolves to two evidence rounds from the profile intent fields in state

#### Scenario: Absent intent keeps today's behavior
- **WHEN** a non-interactive start declares no intent
- **THEN** the wave2 gate budget remains the default one round and the profile
  behavior is today's
