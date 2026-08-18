# Design: Wave2 Synthesis Validation-Feedback Contract Fidelity

## Context

Three observed defects from the same two real mode-003 runs (BUG-040/041/043 in
`_backlog/bugs/`):

1. Wave2's first output mirror-fed the evidence's wave1 claim-verdict shape
   (`claims[]` with `claim_id/verdict/support_refs/counter_refs/reason`), which
   `SynthesisResult`'s `extra_forbidden` rejected as `synthesis_output_not_object`/
   extra-key violation (BUG-043).
2. The repair prompt (`build_synthesis_repair_prompt`) never carried the
   open-question disposition contract — no `open_questions` parameter at all — so
   when the repair produced a correctly-shaped but coverage-incomplete draft
   (3 gaps covering 3 of 4 wave1 open questions), the model could not know the 4th
   question existed, and the coverage validator rejected it again → blocked
   (BUG-040).
3. That blocked terminal projected only the generic `output.structured_invalid`
   because `node.py`'s second-validation `except ValueError:` branch builds
   `NodeProblem(code=OUTPUT_STRUCTURED_INVALID)` and discards the real category
   (BUG-041).

Owners today: `graph/nodes/wave2_synthesis/prompts.py`
(`build_synthesis_prompt`, `build_synthesis_repair_prompt`,
`_expected_synthesis_output`, `parse_synthesis_output`),
`graph/nodes/wave2_synthesis/node.py` (`_synthesis_validation_category`,
`_validate_synthesis_semantics`, the initial/repair invocation loop, and the
`_exhausted_update` path), `domain/run_experience.py` (`NodeProblem`,
`TerminalIncidentProjection`), and the materializer/preview/gate owners that must
stay unchanged.

## Goals / Non-Goals

Goals:

- The repair face of the wave2 loop carries the same trusted open-question contract
  as the initial face, plus the concrete failing detail, so coverage repairs are
  non-blind.
- The initial (and repair) output contract is concrete enough that the evidence
  shape no longer dominates: a minimal example object + an explicit "not a claims
  verdict list" contrast.
- A bounded terminal after a still-invalid repair projects the real semantic
  category (`synthesis_question_coverage_invalid`, etc.), and parse failures keep
  the generic `output.structured_invalid`.

Non-Goals (design-level):

- No gate/verdict/materializer/preview/graph changes; deterministic admission and
  route authority stay byte-identical.
- No new model capability or tool posture; zero-tool request shape is unchanged.
- No provider/bridge changes, no live-model or research-quality claims.
- No soft-bundle CLI behavior (covered by its own change, BUG-042).

## Decisions

### D1 — The validation failure carries a typed detail, not just a string category

Today `_validate_synthesis_semantics` raises `ValueError("synthesis_question_coverage_invalid")`
and `_synthesis_validation_category` reduces it to a coarse bucket ("semantic_invalid").
For non-blind repair and faithful terminal projection we need the concrete failing
fact. Introduce a small typed carrier — a `SynthesisValidationFailure(ValueError)`
subclass (or a dataclass re-raised as ValueError) that holds the exact
`category` string (e.g. `synthesis_question_coverage_invalid`) and a bounded
`detail` payload (e.g. the list of projected ids missing from both collections,
duplicated, or foreign). `_synthesis_validation_category` still derives the coarse
repair-safe bucket for parse-vs-semantic routing, but the concrete category and
detail are now available at both the repair-prompt call site and the
second-validation terminal call site. This keeps the deterministic validator the
sole owner of the fact while making the projection faithful.

Alternative rejected: keep string-only ValueError and reparse the message. Fragile,
would couple the terminal to error-string matching; the typed carrier is the same
`ValueError` contract (so the existing `except ValueError:` seams stay valid) with
structured fields attached.

### D2 — Repair request gains the open-question contract + trusted verification detail

`build_synthesis_repair_prompt(draft, evidence, *, validation_category)` gains
`open_questions: Iterable[tuple[str, str]]` and
`validation_detail: object | None` keyword arguments. The node passes the same
`open_question_pairs` it built for the initial prompt and a trusted monotone
encoding of the failing coverage (missing / duplicated / foreign ids). The repair
objective reuses the existing trusted "closed output contract" wording plus the
concrete detail. Both initial and repair requests keep `tools_enabled=False`, the
same capability ref, and the same `_expected_synthesis_output()` contract (which D3
makes concrete). The repair stays a data-receiving bounded request; it gains no
tool, route, retry, or admission authority.

Naming note: this `validation_detail` is the free-form repair-time id detail carried
by `SynthesisValidationFailure` (D1); it is distinct from the terminal projection's
`validation_category` (D4), which is a bounded category string and never carries the
id detail.

### D3 — `_expected_synthesis_output()` becomes concrete with a negative contrast

Add to the JSON contract a `"example"` key holding one minimal valid
findings/relations/gaps object and an `"instruction"`/negative-contrast list: "return
findings, relations, gaps, summary — NOT a wave1 claims verdict list (`claims[]` with
`claim_id/verdict/support_refs/counter_refs/reason`)". The same builder is shared by
initial and repair, so both faces get the same concrete contract. The parser and
validator are untouched; a claims-shaped candidate still fails deterministically.

Alternative rejected: only strengthening the prose instruction (`required_keys`
wording). The bugs show prose alone lost to evidence mirror pressure; a concrete
example object and an explicit forbidden-shape contrast are the smallest content
addition that gives the model a ground-truth target.

### D4 — `NodeProblem`/`TerminalIncidentProjection` gain an optional bounded `validation_category`

Add an optional `validation_category: str | None` field (bounded `max_length`,
pattern-friendly lowercase/dotted/underscored string, e.g.
`synthesis_question_coverage_invalid`) to `NodeProblem` and
`TerminalIncidentProjection`. The second-validation `except ValueError:` branch now
recomputes the concrete category from the caught error and passes it into
`NodeProblem`; parse failures leave it `None` (generic `output.structured_invalid`
remains). `_exhausted_update` already maps `NodeProblem` →
`TerminalIncidentProjection`; the new field flows through. This field carries the
concrete category string only — the repair-time id detail lives on the
`SynthesisValidationFailure` carrier (D1) and never enters the projection, keeping
the terminal field compatible with the journal `failure_category` pattern.

### D6 — The projection consumers read `validation_category`, not just `code`

BUG-041's symptom lives in three outward faces: the terminal `RunFailure`/incident,
`run-summary.json`'s `failure_category`, and the journal event's
`failure_category` (which `soft-bundle inspect` renders as `failure …`). Adding the
field alone fixes none of them. The two projection writers in
`runtime/run_experience.py` SHALL consume the new field:

- `_publish_observation` (the journal event + run-summary writer): project
  `failure_category = incident.validation_category or incident.code.value` — when a
  semantic category is present, the journal/run-summary carry
  `synthesis_question_coverage_invalid`; otherwise the current code string stands.
  `RecordBearingLifecycleFact.failure_category`'s pattern
  (`^[a-z]+(?:[._][a-z]+)*$`) already accepts the category strings (lowercase
  dotted/underscored), so no enum/pattern change is needed.
- `_failure_for_terminal` (the terminal `RunFailure` projected to the demo terminal
  and operator): thread `validation_category` through `_failure(...)` into
  `RunFailure`. On the demo terminal the wave2 generic path — `demo_real.py`
  `_failure_lines` (the non-provider branch that already renders `failure.code` and
  `worker_failure_category`) SHALL add one detail line for
  `failure.validation_category`, so the terminal shows the concrete category. The
  provider-only `_terminal_failure_presentation.py` path is NOT involved: a wave2
  `OUTPUT_STRUCTURED_INVALID` failure has no provider fields, so
  `provider_terminal_details` returns `None` and the generic branch renders.)

The `validation_category` is a faithful projection of the deterministic validator's
category; no route, gate, lifecycle, or recovery reader consumes it (existing
provider/budget branch checks compare against specific codes and are unaffected:
they only activate for their own recovery fields).

### D5 — Keep the generic `output.structured_invalid` for pure parser failures

The existing WSN-001 behavior "parser failure → `output.structured_invalid`" is
preserved exactly. The new category-specific projection applies only when the
failure is a semantic validation failure with a typed detail. This keeps the change
additive and prevents over-retyping JSON-shape failures that carry no semantic
category.

## Risks / Trade-offs

- [Terminal projection gains a data field that could be misread as authority] →
  spec + design limit it to a faithful projection of the validator category; no
  route/gate/lifecycle reader consumes it; `exclude_none` keeps old checkpoints
  compatible.
- [Repair prompt grows larger (open questions + detail + example)] → bounded: the
  question list is capped at 64 as today, the detail names only failing ids, and the
  example is one minimal object; request size stays within the existing bounded
  context.
- [`SynthesisValidationFailure` subclass may change `except ValueError` matching] →
  it IS a `ValueError`, so existing seams still catch it; tests assert both the
  category routing and the generic catch.
- [Prompt-content change may not fully stop evidence mirroring on every model] →
  this is a prompt-contract fidelity fix, not a claim of universal behavior change;
  the deterministic validator still rejects any wrong shape and the repair loop now
  has the contract to recover. Live confirmation stays an operator runbook step,
  never a CI gate.

## Migration Plan

No data or schema migration: the new fields default to absent (`None`), checkpoints
written before the change deserialize as today, and `run-summary.json` gains the
category field only when a semantic terminal actually occurs. Rollback = revert the
prompt/node changes; the generic terminal behavior returns automatically.

## Open Questions

None that change specs, approach, or tasks.