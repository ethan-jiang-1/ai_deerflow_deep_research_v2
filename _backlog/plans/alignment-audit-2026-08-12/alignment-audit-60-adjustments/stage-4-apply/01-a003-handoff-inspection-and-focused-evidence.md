# Stage 4 Apply - A-003 Handoff Inspection And Focused Evidence

> Change: `reconcile-evaluation-rubric-authority`
> Date: 2026-08-13
> Status: **BOUNDED LOCAL CONFORMANCE OBSERVED - NO DEFERRED CODE CHANGE TRIGGERED**

## Source-To-Consumer Inspection

This inspection answers only the selected A-003 boundary for the local
Cognitive Evaluation path. It does not claim coverage of uninspected future subjects,
live/credentialed execution, or a source-controlled invalid-Rubric fixture that does
not exist in the current suite.

| Boundary | Identity/version | Criterion IDs | Rubric content, weights, thresholds, guidance, disposition | Finding |
| --- | --- | --- | --- | --- |
| Source-controlled Rubric -> registry admission | `controls.py:90-113` compares `case_id` and `version`; it also contains a current `schema_version` format check. | `criteria[].id` is the only criterion member extracted and its set/uniqueness is compared to scenario `review_criteria`. | Not extracted or interpreted. | Conforms to the selected narrow semantic boundary. `schema_version` remains current format evidence, not a new required behavior in this apply. |
| Typed Case / scenario contract | The Case retains declared controls. | `domain/evaluation.py` retains `review_criteria` as a bounded tuple and validates only uniqueness. | No Rubric prose field or quality-result field is present in the cognitive-program scenario contracts. | IDs are retained as structural control metadata. |
| Runner -> execution context / Bundle input | Case identity is observed and retained. | `runner.py:121-145` copies the complete fixture to `ExecutionContext`; `runner.py:303-315` preserves the fixture in Bundle `inputs.json`. | The fixture has scenario IDs, not the Rubric's criterion prose or review disposition fields. | IDs can remain in a non-model fixture and retained evidence. This alone is not a selected-boundary violation. |
| Generic scenario adapter -> factory | No Rubric identity is projected by the adapter. | `subjects.py:86-124` passes the complete scenario/fixture to caller-supplied factories without reading `review_criteria`. | The adapter does not load or interpret the source Rubric. | The adapter is a visibility boundary, not a quality evaluator. Consumers still require inspection. |
| Cognitive-program node/model consumers | No source consumer reads Case/Rubric identity. | Repository search finds `review_criteria` only in the typed evaluation contracts and `_verify_case_rubric`; no HITL1/Wave0/Wave1/Wave2 node source consumes it. | No node source reads any Rubric JSON or its prose/weight/threshold/guidance/disposition fields. | No inspected model-facing quality interpretation was found. |
| Wave2 real node/bridge test | Not supplied to the model path. | The test's factories project `assignment`, accepted submission refs, and accepted evidence only. | `test_cognitive_evaluation_suite.py:1360-1525` uses the real Wave2 node and bridge; its prompt construction does not project `review_criteria` or Rubric content. | Concrete deterministic evidence for the Wave2 handoff; it remains scripted, not live. |
| HITL1, Wave0, Wave1 scenario-adapter evidence | Not supplied by the adapter test. | The existing adapter test receives registered scenarios but its state factory projects only `scenario_id`; it uses a stub `NodeSpec`. | No Rubric content is available to the test double. | No prohibited local source consumer was found, but this is weaker than a real-node prompt observation. |
| Runner status / output / review | Runner owns only execution completion/failure. | IDs do not alter status. | `runner.py` publishes execution evidence only; `review.py:28-79` receives an explicit separate ReviewSubmission and owns its four-state cognitive result. | No Runner quality verdict or automatic review path was found. |

## Conformance Disposition

No inspected path consumes Rubric criterion prose, weights, thresholds, evaluator
guidance, or a quality disposition in a subject fixture, model-facing context,
execution output, or Runner status. No inspected path interprets criterion IDs as
model-facing quality instruction, scoring, or a verdict. `DEFERRED-CODE-CHANGE` is
therefore **not triggered** by this apply inspection.

This is not a claim that all execution paths, future factory implementations, or live
provider behavior are protected. A later code change that creates a direct consumer
must first add a red deterministic test for the affected handoff before implementation.

## Existing Focused Evidence

Command run:

```bash
cd deep_research_harness && UV_OFFLINE=1 .venv/bin/python -m pytest tests/eval/test_cognitive_evaluation_suite.py
```

Result: **56 passed in 3.49s**.

| Existing evidence | What it proves | What it does not prove |
| --- | --- | --- |
| `test_source_controlled_v1_registry_exposes_only_the_declared_cases` | Normal source-controlled registry loading succeeds. | No malformed/mismatched cognitive-program Rubric rejection. |
| Cognitive-program fixture tests | Duplicate `review_criteria` and other typed fixture failures reject during Case validation. | They do not mutate a source-controlled Rubric JSON and call `load_case_registry()` to directly exercise `_verify_case_rubric()`. |
| `test_wave0_cognitive_program_runner_and_review_retain_deterministic_handoff_only` | Runner completion and separate review evidence layer remain distinct. | It uses a scripted subject and cannot prove every real node prompt excludes IDs. |
| `test_wave2_cognitive_program_production_scenarios_record_only_declared_handoffs` | A scripted real Wave2 node/bridge receives the intended state projection and preserves the declared deterministic handoff. | It is not live evidence and it is not equivalent real-node evidence for HITL1, Wave0, or Wave1. |
| `test_multi_scenario_adapter_uses_only_the_registered_factory_and_declared_scenarios` | HITL1/Wave1 scenarios pass through the generic adapter. | Its `NodeSpec` is a test double, not a model-facing consumer. |

The missing direct invalid-Rubric registry fixture remains a disclosed evidence gap.
This alignment-only change neither adds it nor converts the gap into a false passing
claim. A future owned implementation/evidence change must add a red fixture before
changing this control behavior.
