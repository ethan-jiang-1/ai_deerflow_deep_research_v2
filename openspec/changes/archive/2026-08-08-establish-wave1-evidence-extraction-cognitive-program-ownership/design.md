## Context

See `proposal.md`. Wave1 already has required-tool extraction and forbidden-tool repair
resources, but its Python objectives remain independently sufficient cognitive methods.
The subgraph has exactly two pre-persistence repair categories and retains later
submission validation outside repair.

## Goals / Non-Goals

**Goals:** Move reusable baseline-aware extraction/repair method into the two loaded
resources; preserve all existing deterministic ownership and prove the boundary at
renderer, prompt, and real worker seams.

**Non-Goals:** Change worker schemas, source/claim validation, two-source floor,
critics, artifacts, ledger, controller/gate/retry, graph topology, providers, or UI.

## Decisions

### 1. Two resources own cognition; Python projects invocation data

The extraction resource owns one-retrieval, baseline-aware candidate and uncertainty
method. The repair resource owns one zero-tool non-inventive reformat method. Python
keeps assignment serialization, response shape, limits, category validation,
delimiters, parser, and recovery placement. Retaining detailed prompt prose was
rejected because it would leave two cognitive owners.

### 2. Both parser and local-semantic failure use existing repair only

The subgraph may enter repair after either initial parse or local semantic failure, but
only once and before persistence. Post-candidate submission validation never repairs.
This reuses the existing split rather than adding a model-driven validator/retry loop.

### 3. A typed, deterministic Wave1 corpus joins existing production seams

Renderer/prompt and scripted real bridge/worker/validator/ledger regressions are the
required evidence. The existing evaluation control family is intentionally typed per
cognitive program, rather than accepting an unowned generic fixture. This change adds
only the Wave1 sibling contract, production-scenario adapter, and closed control assets
needed for normal handoff, adversarial retrieval text, baseline duplicate containment,
parser/local-semantic repair, and post-candidate validation isolation. It reuses the
existing runner, registry, immutable controls, and selected-live rejection behavior;
no provider/web call is authorized.

### 4. Evaluation has one bounded owner, not a parallel workflow

The new `wave1_cognitive_program` fixture binds the two capability digests and worker
schema digest to closed scenarios. It invokes only the real Wave1 production branch
through scripted external adapters. It is deterministic handoff evidence, not a source-
quality, model-quality, selected-live, release, admission, critic, controller, or route
authority. Generalizing the family prematurely was rejected because it would widen an
otherwise small Wave1 change and erase program-specific scenario constraints.

## Risks / Trade-offs

- [Method duplicates the contract] -> Keep schemas, limits, and delimiters in Python and
  assert objectives are bounded projections.
- [Baseline is mistaken for evidence] -> Assert baseline duplicates stay non-new through
  existing semantic/submit validation.
- [Repair expands recovery] -> Retain exact two existing pre-persistence categories and
  the no-repair-after-submission-validation regression.
- [Corpus duplicates production orchestration] -> The adapter calls the registered
  Wave1 production factory with fresh scenario dependencies; it owns no prompt, parser,
  admission, recovery, or route logic.

## Migration Plan

1. Add red boundary regressions.
2. Expand Markdown and narrow prompts until focused tests pass.
3. Add the closed corpus and prove that selected-live admission rejects it before any
   run bundle, provider call, or evidence-layer claim.
4. Run deterministic verification. Rollback is a normal code revert; no persistent
   migration is introduced.
