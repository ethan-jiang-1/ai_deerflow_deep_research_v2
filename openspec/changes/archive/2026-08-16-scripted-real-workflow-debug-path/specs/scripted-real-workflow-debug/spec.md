> req: SCR-001, SCR-002, SCR-003, SCR-004, SCR-005

## Purpose

Provide an operator-only, credential-free, network-free debug command that runs the
complete production Deep Research control path — real node adapters, prompts, parsers,
work-unit ledger, gates, and persistence — against a fixed narrow scripted external
world, so every graph/bridge/gate change can be verified in seconds without a live
model or web dependency.

## ADDED Requirements

### Requirement: Scripted-real composition root is operator-only and all-real

The debug command SHALL construct one dedicated composition root that combines all
production REAL node adapters, the production REAL gate definitions, and the production
persistence path with scripted model and web-tool capabilities. It SHALL build this
composition through the existing recipe seam (`ResearchGraphRecipe.all_real` factory
arguments) and SHALL NOT modify `ResearchGraphRecipe.all_real()`, add any fake mode
flag or scripted switch to `make demo-real`, read `.env` or require model or Tavily
credentials on its own execution path, or become part of the Primary User route. (The
one framework-owned dotenv load that `deerflow.config` performs at import time is not
command authority; the command SHALL not load dotenv itself and SHALL complete with no
provider variables present in the environment.) The composition's authenticity
SHALL be labeled `scripted_real_workflow`, never `LIVE_REAL_DEPENDENCIES` or a fixture
label, and its adapter kinds SHALL remain all REAL. (`SCR-001`)

#### Scenario: Command builds through the recipe seam without touching all_real defaults
- **WHEN** an operator runs the debug command on a machine with no model or web credentials
- **THEN** the command starts and completes with no provider variables present, its own execution path never loads dotenv, and it reports `composition=all_real_adapters` with every node adapter kind REAL and authenticity `scripted_real_workflow`

#### Scenario: Real demo surface is unchanged
- **WHEN** the change is applied
- **THEN** `make demo-real` retains its existing all-real behavior with no new mode flag, no fake fallback, and no scripted option exposed to users

### Requirement: Baseline scenario exercises one bounded action per wave

The fixed baseline case SHALL drive exactly: one topic plan covering the fixed
must-answer question; one Wave0 source-intake worker run that admits one candidate via
one scripted `web_search` call; one Wave1 extraction worker run proposing at least two
new source URLs beyond the Wave0 baseline (the production `WAVE1_MINIMUM_NEW_SOURCE_URLS`
floor) followed by exactly two critic reviews (source diagnostic and claim verifier)
whose outputs align with the extraction's declared source ids and claim ids; one Wave2
synthesis response producing a single finding whose `backing_refs` are drawn from the
accepted submission refs and whose `gaps` contain no searchable entries; a readiness
critic response that passes every assigned question with `backing_claim_ids` drawn only
from accepted submission refs; and one final-delivery composer response whose
`conclusion_order` and `uncertainty_order` are arrays containing only the plan entry
ids supplied in the composer prompt. Scripted model responses SHALL carry
`usage_metadata` with total and output token accounting, and responses that depend on
runtime facts (accepted refs, plan entry ids) SHALL be filled by template extraction
from the trusted prompt assignment, never fabricated constants. (`SCR-002`)

#### Scenario: Every wave action happens with the declared budget
- **WHEN** the baseline command completes
- **THEN** the reported per-wave counters show 11 model calls, 2 `web_search` calls, 0
  `web_fetch` calls, at least one accepted Wave0 record, both Wave1 review artifacts, a
  Wave2 finding with a backing ref from the accepted submission set, and a published
  report and citation-map pair

#### Scenario: HITL stays automatic and the run never enters targeted or rerun
- **WHEN** the baseline command completes
- **THEN** the execution trace contains the HITL1 auto-confirmation step and the
  autonomous HITL2 visit, and it does not contain `targeted_evidence` or `rerun`

### Requirement: Script exhaustion is strict and failures fail the command

The command SHALL fail when any scripted model or tool response is missing (exhaustion),
when any extra model or tool call occurs beyond the declared queue, when a wave action
is skipped, or when the run enters `targeted_evidence` or `rerun`. A passed run SHALL
therefore mean every real action in the baseline actually occurred, not merely that the
graph reached a terminal state. (`SCR-003`)

#### Scenario: Missing response fails loudly
- **WHEN** a scripted capability queue is shorter than the production path requires
- **THEN** the command exits non-zero with a bounded exhaustion failure instead of a completed run

#### Scenario: Extra model or tool call fails loudly
- **WHEN** the production path invokes more model or web-tool calls than the baseline declares
- **THEN** the command exits non-zero and reports the surplus call instead of a completed run

### Requirement: Completion output states what the run proves and does not prove

The completion output SHALL include `composition=all_real_adapters`,
`authenticity=scripted_real_workflow`, a zero-network and zero-credential assertion, the
per-wave action counters, the Bundle id, the Event Journal entry point, and total wall
time. It SHALL state that the run proves only production control-path integration for
fixed legal inputs, and SHALL NOT claim to prove real model comprehension or prompt
obedience, Tavily or web availability, real page quality, latency, cost or rate limits,
multi-topic concurrency, coverage breadth, research depth quality, or the
`targeted_evidence`/rerun/provider-recovery branches. (`SCR-004`)

#### Scenario: Output carries the authenticity and boundary labels
- **WHEN** the baseline command completes
- **THEN** its output contains the `all_real_adapters` composition label, the
  `scripted_real_workflow` authenticity label, the zero-network/zero-credential
  assertion, per-wave counters, a Bundle id, and a Journal entry reference

#### Scenario: Output never claims live-model or web evidence
- **WHEN** the baseline command completes
- **THEN** its output does not claim live provider quality, web availability, coverage,
  or model-judgment evidence

### Requirement: Debug command is a fast local operator target with a wall-time contract

The command SHALL be reachable via a dedicated Make target
(`make debug-scripted-real-workflow`) that does not alter or reuse the demo-real mode
selection, and its CLI contract test SHALL assert zero `.env` reads, zero network
access, strict script exhaustion, and a completion wall time under 10 seconds; a
timeout is a test failure, not a skip. It SHALL be documented as an operator-only local
debug tool, not a product command or a substitute for `make verify`. (`SCR-005`)

#### Scenario: Wall-time contract is enforced by the contract test
- **WHEN** the CLI contract test runs the baseline on the fixed local composition
- **THEN** it fails if the run exceeds 10 seconds or performs any credential or network access

#### Scenario: The target stays separate from the demo surface
- **WHEN** an operator lists the Makefile demo targets
- **THEN** the new target appears as a distinct operator debug target and the existing
  demo targets remain unchanged
