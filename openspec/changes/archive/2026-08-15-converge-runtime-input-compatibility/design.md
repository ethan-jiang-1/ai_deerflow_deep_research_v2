## Context

This design implements the clean-cutover disposition in `proposal.md`. Three
verified local facts shape it:

- `tool.py` currently treats either non-interactive marker as trusted admission
  input and converts policy failures into the existing `interactive_required` wire
  result before lifecycle dispatch.
- `resolve_effective_provider()` currently mirrors upstream provider precedence by
  returning a legacy `checkpointer` selection before `database`; GraphHost then
  opens the generic provider and diagnostics projects the same selection.
- `_configured_endpoint_authority()` currently reads `base_url`,
  `openai_api_base`, and `api_base` only from the exact selected model config. The
  resulting value is an optional safe observation, not model, provider, graph, or
  lifecycle authority.

The source and focused test inventory contains no registered external host producer,
deployment configuration, or AppConfig version that receives compatibility support.
The design therefore makes the local clean break explicit rather than creating an
unbounded compatibility switch. DeerFlow remains a public dependency only; neither
its source nor its behavior is modified or inferred here.

## Goals / Non-Goals

**Goals:**

- Admit only canonical `non_interactive=true` policy input and deny the retired
  marker before Bundle/graph mutation without changing interactive behavior.
- Refuse a legacy checkpointer before any generic provider is opened, and make
  GraphHost and diagnostics expose the same bounded, redacted reason.
- Limit safe endpoint observation to selected `base_url`; retired or unsafe aliases
  yield no observation and cannot influence model creation or lifecycle behavior.
- Preserve the existing canonical writer, provider/durability parity, no-secret
  projection, no-reinjection, and old-entry/workspace-drift guards with narrow,
  planted negative tests.

**Non-Goals:**

- Parsing or modifying DeerFlow AppConfig, `make_checkpointer`, provider behavior,
  model-factory selection, remote endpoints, graph topology, or retained Bundle data.
- Adding a public configuration API, runtime compatibility flag, background
  discovery, new Gateway command, external support promise, or a persistent
  migration reader.
- Treating diagnostics or endpoint observation as a source of model, provider,
  Bundle, checkpoint, or lifecycle truth.

## Decisions

### 1. Retire trusted-marker support in the pre-dispatch admission function

`_admitted_start_action_input()` remains the only local deterministic conversion of
trusted runtime context into typed start input. It first detects the retired
`disable_clarification` marker, including a context that also supplies canonical
`non_interactive`, and raises the same local validation failure that maps to the
existing `interactive_required` wire result. It evaluates the closed policy only for
the canonical marker.

This reuses the established no-public-context and pre-Bundle denial path. It avoids a
new error projection, a policy field in State, or an interactive fallback that would
turn a stale producer into a different lifecycle request. The existing internal
writer remains the proof that project-owned scripted starts already use the target.

Alternative rejected: accept both markers behind a time- or producer-based switch.
There is no authoritative producer inventory to bound that switch, and it would make
an unsupported external surface look supported.

### 2. Reject legacy provider configuration before the factory seam

Introduce one runtime-owned provider-configuration validator/error beside
`resolve_effective_provider()`. It detects a non-null legacy `checkpointer` without
reading its connection details. GraphHost calls the validator before its saver context
in both action execution and checkpoint inspection; diagnostics calls the same
validator before projecting provider fields. Each maps the shared typed error to its
existing bounded surface, so neither can call the generic provider factory or claim a
legacy durability class.

After validation, `resolve_effective_provider()` classifies only `database` or the
existing default. This keeps one classifier for GraphHost and diagnostics and avoids
an unavailable pseudo-provider that could accidentally reach the saver factory.

Alternative rejected: leave the classifier's legacy result and make diagnostics
report it as unsupported. That would still let GraphHost call the upstream factory
with the retired section, violating the pre-open denial requirement.

### 3. Make endpoint observation a one-field projection

The selected-config normalizer reads `base_url` only after the existing model entry is
selected. If either retired alias appears, or if `base_url` is missing/unsafe, it
returns no endpoint observation. It does not inspect the constructed model object,
call the provider, alter the selected model, or raise a lifecycle failure. Existing
authority normalization and redaction checks remain the sole output contract.

Alternative rejected: reject AppConfig or model creation when a retired alias exists.
The downstream reader owns only a safe observation, not AppConfig parsing or model
factory compatibility, so such a rejection would claim authority outside this change.

### 4. Notice and rollback are operational, not runtime compatibility controls

`deep_research_harness/docs/local-operations.md` documents the three retired inputs,
canonical replacements, the stable denial/omission outcomes, and the legal next
action. No runtime flag or hidden reader is added. An emergency rollback is an
explicitly approved hotfix/revert of the complete affected local reader change, with
the same deterministic tests rerun; it cannot rewrite config, resurrect a retired
input selectively, or enlarge the support inventory.

## Risks / Trade-offs

- [An unregistered external producer still uses the retired marker] -> It receives
  `interactive_required` before mutation; the notice names canonical replacement and
  the only recovery is a separately approved rollback or later support change.
- [A deployment retains `checkpointer`] -> GraphHost cannot open the provider and
  diagnostics cannot misstate durability; the operator removes the section and uses
  `database`.
- [An AppConfig relies on a retired endpoint alias] -> Safe endpoint observation is
  absent, but model construction and lifecycle behavior do not change because this
  reader never owned either; the operator uses selected `base_url` for observation.
- [A hotfix accidentally restores only one consumer] -> Provider and diagnostics
  parity tests, plus the declared whole-reader revert rule, make partial recovery an
  invalid rollback.

## Migration Plan

1. Add red-before-green focused tests for retired-marker no-write denial, legacy
   provider pre-open refusal/diagnostic parity, and selected-config retired-alias
   omission. Retain canonical and database/base-URL positive controls.
2. Implement the three local readers/guards without changing upstream configuration
   parsing or model/provider factories. Update the project-owned configuration and
   lifecycle reference with canonical replacements and legal next actions.
3. Run focused tests, the required offline verification lane, strict OpenSpec and
   governance validation, and the declared gitlink scope evidence before archive.
4. If deployment evidence after release proves a material unsupported consumer,
   stop further rollout and approve a whole-reader hotfix/revert or a separately
   scoped support change. Do not add a runtime bypass or mutate affected inputs.
