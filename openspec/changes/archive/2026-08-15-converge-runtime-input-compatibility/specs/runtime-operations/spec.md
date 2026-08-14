> req: RUO-001

## MODIFIED Requirements

### Requirement: Non-interactive mode requires policy

A trusted runtime that marks an input-bearing lifecycle request non-interactive with
the sole canonical `non_interactive=true` marker SHALL provide one closed
`non_interactive_policy` value with exactly the `auto_profile` and `auto_proceed`
keys, both set to the boolean value `true`. Missing keys, extra keys, false values,
non-boolean values, or a non-mapping policy SHALL be denied with
`INTERACTIVE_REQUIRED` before Bundle publication or graph mutation. The retired
trusted `disable_clarification=true` marker SHALL also be denied with
`INTERACTIVE_REQUIRED` before Bundle publication or graph mutation, regardless of
whether a policy-shaped value is present, and SHALL not fall back to interactive
execution. The policy is a validated trusted input value, not a public tool argument,
caller-selected graph option, or presentation decision. Only a new `start` may turn
canonical marked input into the typed action input carried to graph execution; a later
marked `resume` or `refine` remains subject to the same validation but cannot create
or replace a graph-state input. `ResearchRunExperience` SHALL emit only the canonical
marker.

Only a new `start` executed through a trusted-composed `BundleGraphExecutor` SHALL
write the admitted policy into initial graph values. The selected Bundle's graph
checkpoint SHALL own that value for all later graph work. A `resume` or `refine`
against an existing Bundle SHALL read the checkpointed value and SHALL NOT insert,
replace, or clear policy from a later runtime context. Policy admission SHALL NOT
instantiate or select a graph executor; an uncomposed fallback lifecycle retains its
existing behavior. When the runtime does not mark an action non-interactive, ordinary
interactive behavior SHALL remain unchanged regardless of an incidental policy-shaped
context value.

#### Scenario: Non-interactive with policy is allowed
- **WHEN** trusted runtime context marks a new `start` with canonical
  `non_interactive=true` and contains
  `non_interactive_policy={"auto_profile": true, "auto_proceed": true}`, and trusted
  runtime composition supplies a `BundleGraphExecutor`
- **THEN** the lifecycle admits one typed action input, writes its policy only through
  initial graph values, and the resulting selected Bundle checkpoint owns the policy

#### Scenario: Compatibility marker uses the same closed policy
- **WHEN** trusted runtime context marks a new `start`, `resume`, or `refine` with
  `disable_clarification=true`, with or without a complete policy
- **THEN** the lifecycle returns `INTERACTIVE_REQUIRED` without publishing a Bundle,
  writing graph state, creating a profile artifact, or taking the ordinary interactive
  path

#### Scenario: Policy admission preserves uncomposed fallback
- **WHEN** trusted runtime context marks a new `start` canonical non-interactive and
  contains a complete closed policy, but no trusted-composed `BundleGraphExecutor` is
  available
- **THEN** the lifecycle retains its existing uncomposed fallback lifecycle and does
  not create graph state from the policy

#### Scenario: Non-interactive without policy is denied
- **WHEN** a trusted runtime marks an input-bearing action canonical non-interactive
  but the policy is absent, has an unknown or missing key, or either required value is
  not the boolean value `true`
- **THEN** the action returns `INTERACTIVE_REQUIRED` without publishing a Bundle,
  writing graph state, or creating a profile artifact

#### Scenario: Resume cannot reinject a policy
- **WHEN** a later `resume` or `refine` carries a complete policy-shaped canonical
  context for an available Bundle that already has a graph checkpoint
- **THEN** the context passes the same closed validation but the invocation consumes
  only the checkpointed policy value, and the later context cannot replace or add a
  policy field

#### Scenario: Interactive mode is unaffected
- **WHEN** the runtime does not mark a lifecycle invocation non-interactive
- **THEN** the invocation follows the existing interactive path and a policy-shaped
  context value does not create non-interactive graph behavior
