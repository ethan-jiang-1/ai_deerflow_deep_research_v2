# Rubrics Are Case-Specific Review Authorities

The Node Cognitive Control Contract defines a node's enduring cognitive responsibility
and quality standard. A versioned Evaluation Rubric refines that standard for one
Evaluation Execution Case. It is associated with the Case but is not Runner input; only
the upper review reads it. The Evaluation Review Protocol owns review method and output
shape rather than case quality criteria. This preserves an objective Runner while keeping
case-specific expectations independently evolvable.

## Current Status And Applicability (2026-08-13)

This postscript records current applicability only. It does not alter this ADR's
historical title, decision text, or runtime authority.

- **Current applicability:** Deterministic Case admission may compare only a
  Case-linked Rubric's identity/version and unique criterion-ID set as non-model
  case-control-integrity metadata.
- **Execution boundary:** Rubric prose, weights, thresholds, evaluator guidance, and
  cognitive judgment remain review-only. They do not enter subject fixtures,
  model-facing execution input, execution output, or Runner completion status; the
  Runner reports only `completed` or `failed` and produces no cognitive quality verdict.
- **Current owner or route:** [Evaluation Rubric](../../CONTEXT.md) is explanatory;
  application evaluation contracts under `evals/` and `tests/eval/`
  owns the required behavior.
