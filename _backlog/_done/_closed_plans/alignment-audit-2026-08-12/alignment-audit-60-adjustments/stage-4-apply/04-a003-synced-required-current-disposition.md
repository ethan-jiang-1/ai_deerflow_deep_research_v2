# Stage 4 Apply - A-003 Synced Required/Current Disposition

> Change: `reconcile-evaluation-rubric-authority`
> Date: 2026-08-13
> Task: 3.4
> Status: **ONE REQUIRED-BEHAVIOR ANSWER; BOUNDED LOCAL CONFORMANCE OBSERVED**

## Required-Behavior Re-Read

The synced owning requirements were re-read together:

| Owner | Required answer after sync |
| --- | --- |
| CES | A Case-linked Rubric may contribute only case/version identity and a unique criterion-ID set to deterministic admission before subject construction. Criterion content and cognitive disposition are review-only. A Runner emits only `completed` or `failed`. |
| EVH Wave0, Wave1, Wave2 | Each cognitive-program scenario declares a non-empty unique criterion-ID set. Admission compares that set and the selected Rubric identity/version. Retained IDs remain non-model control metadata; content and quality semantics cannot enter the subject or model-facing input. |
| HITL1 | HITL1 uses the same case-control-integrity rule and same prohibition at its cognitive-program boundary, while retaining its separate bounded model-method and graph controls. |

The three specifications now give **one required-behavior answer**: Rubric
identity/version plus the unique criterion-ID set are the only permitted deterministic
admission facts. IDs can remain after admission only as non-model control metadata.
Criterion prose, weights, thresholds, evaluator guidance, quality disposition, scoring,
quality instruction, and a Runner verdict are prohibited execution authority. Review,
not Runner completion, owns the cognitive result.

## Independent Current-Behavior Disposition

The bounded source-to-consumer inspection in
`01-a003-handoff-inspection-and-focused-evidence.md` found no prohibited local
crossing. `controls.py` extracts only criterion IDs for deterministic comparison;
the generic adapter does not interpret them; no inspected cognitive-program node reads
the Rubric or `review_criteria`; and the Runner retains execution-only completion while
the separately submitted review owns the four-state result.

Therefore **no `DEFERRED-CODE-CHANGE` remains from the bounded inspected path**. This
is independent of the required-behavior conclusion above and is not a claim of complete
route coverage or future mechanical prevention.

## Evidence Limits And Follow-Up Ownership

- The existing suite has no source-controlled invalid-Rubric registry fixture that
  directly exercises `_verify_case_rubric()` through `load_case_registry()`.
- Wave2 has scripted real-node/bridge prompt evidence; HITL1, Wave0, and Wave1 have
  adapter/source inspection only, not equal real-node model-context proof.
- No live or credentialed provider behavior was inspected.

Those are evidence limits, not observed prohibited crossings. If a future change adds
a Rubric-derived consumer or expands the handoff, its owning code-and-test change must
first add a red deterministic handoff test, then implement the change. Stage 6 remains
the owner of later terminology propagation; it must preserve this bounded disposition
rather than restating it as universal code conformance.
