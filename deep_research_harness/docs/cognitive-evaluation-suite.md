# Cognitive Evaluation Suite

Run these commands from `deep_research_harness/`. The suite is a manually selected,
local evidence workflow. It does not resume a prior execution, run an automatic
review, or decide cognitive quality in Python.

## Prepare A Case

Construct the declared production node dependencies in the owning runtime, then bind
the corresponding fixed V1 subject. The only accepted execution selection is the
registered Case id and version.

```python
from pathlib import Path

from deerflow_deep_research.runtime.evaluation import (
    CognitiveEvaluationRunner,
    EvaluationOperations,
    EvaluationReviewService,
    load_case_registry,
    production_node_subject,
    production_scenario_node_subject,
)
from deerflow_deep_research.graph.nodes.hitl1 import NODE_SPEC as HITL1_NODE_SPEC
from deerflow_deep_research.graph.nodes.wave0 import NODE_SPEC as WAVE0_NODE_SPEC
from deerflow_deep_research.graph.nodes.wave1 import NODE_SPEC as WAVE1_NODE_SPEC
from deerflow_deep_research.graph.nodes.wave2_synthesis import NODE_SPEC as WAVE2_NODE_SPEC

registry = load_case_registry()
runner = CognitiveEvaluationRunner(
    registry=registry,
    runs_root=Path("evals/runs"),
    subjects={
        "hitl1_brief": production_node_subject(
            subject="hitl1_brief",
            node_spec=HITL1_NODE_SPEC,
            dependencies=production_hitl1_dependencies,
            state_factory=hitl1_state_from_case_fixture,
        ),
        "hitl1_cognitive_program": production_scenario_node_subject(
            subject="hitl1_cognitive_program",
            node_spec=HITL1_NODE_SPEC,
            dependencies_factory=production_hitl1_dependencies_from_scenario,
            state_factory=hitl1_state_from_cognitive_program_scenario,
        ),
        "wave0_cognitive_program": production_scenario_node_subject(
            subject="wave0_cognitive_program",
            node_spec=WAVE0_NODE_SPEC,
            dependencies_factory=production_wave0_dependencies_from_scenario,
            state_factory=wave0_state_from_cognitive_program_scenario,
        ),
        "wave1_cognitive_program": production_scenario_node_subject(
            subject="wave1_cognitive_program",
            node_spec=WAVE1_NODE_SPEC,
            dependencies_factory=production_wave1_dependencies_from_scenario,
            state_factory=wave1_state_from_cognitive_program_scenario,
        ),
        "wave2_cognitive_program": production_scenario_node_subject(
            subject="wave2_cognitive_program",
            node_spec=WAVE2_NODE_SPEC,
            dependencies_factory=production_wave2_dependencies_from_scenario,
            state_factory=wave2_state_from_cognitive_program_scenario,
            expected_failure_factory=wave2_expected_invalid_candidate,
        ),
    },
    available_services=frozenset({"model"}),
)
operations = EvaluationOperations(
    runner=runner,
    review=EvaluationReviewService(registry=registry, runs_root=Path("evals/runs")),
)
result = await operations.run(case_id="hitl1-brief", version="v1")
```

The result reference names a new isolated Bundle. Inspect `manifest.json`,
`observations.json`, `output.json`, `artifacts.json`, `resources.json`, and
`diagnostics.json` beneath it. `completed` says that the declared branch finished;
it is not a cognitive pass. `failed` retains the observable execution failure and is
not an assessment result.

Every manifest records an evidence layer. Ordinary `runner.run(...)` creates only
`deterministic_handoff`: it proves the declared resource, candidate, and admission
handoff, not language quality. The review record derives that layer from the verified
manifest; reviewers cannot supply a live layer or release claim.
Manifests with a missing or unknown layer are unsupported and fail closed as
`bundle_manifest_invalid` before a Review Record or quality claim is written. The
reader does not default, backfill, or upgrade their provenance; explicit
`deterministic_handoff` and `credentialed_live_quality` records remain distinct.

`wave0-cognitive-program@v1` is a closed deterministic-only subject. Its five
scenarios bind the two runtime-loaded Wave0 methods and worker schema to normal
retrieval handoff, hostile retrieved instructions, retrieval shortfall, one
pre-parser repair, and post-candidate validation isolation. Scripted model/tool
adapters exercise the production Wave0 node, bridge, and controller dependencies;
they do not claim provider behavior or source-quality judgment.

`wave1-cognitive-program@v1` is the matching closed deterministic-only subject for
baseline-aware extraction and zero-tool repair. Its six scenarios cover normal and
adversarial retrieval observations, baseline duplicate containment, parser and local-
semantic one-repair boundaries, and post-candidate validation isolation. It binds both
Wave1 capability resources and the worker schema; it does not evaluate critic quality,
source quality, or provider behavior.

`wave2-cognitive-program@v1` is a closed deterministic-only synthesis corpus. Its
five fresh-Bundle scenarios cover accepted-evidence synthesis, instruction-like
evidence containment, an honest uncertainty gap paired with a backed finding, one
parser repair, and invalid repaired-candidate non-publication. The initial and repair
methods are loaded from their distinct capability resources; invocation data carries
only trusted assignment/output/category facts plus delimited untrusted evidence or
draft. The real zero-tool bridge remains the runtime enforcer, and parser/semantic
validation remains the admission owner. Its retained facts cover only resources,
bounded prompts, grounding, repair, admission, and the invalid-candidate no-write
negative; a valid node's internal materialization, preview, or later gate result is
not corpus evidence.

## Selected Live Cases

`run_selected_live_case` accepts only the registered V1 ids:
`hitl1-brief@v1`, `hitl1-cognitive-program@v1`, `wave0-worker@v1`,
`public-controller-direction-loop@v1`, and `topic-planning-direction-loop@v1`. The
HITL1 cognitive program case keeps normal confirmation, revision, question, ambiguity,
adversarial reply, and malformed-candidate repair in one digest-bound corpus. The last two cover the public controller's
intent/subject decision surface and the topic-planning program's canonical
profile/direction handling; they do not replace the deterministic direction-loop tests.
`wave0-cognitive-program@v1` is deliberately absent: selected-live admission rejects
it before runs-root, manifest, review, subject, provider, or release evidence exists.
Its live source-quality evidence is therefore not collected, rather than represented
as a deterministic success.
`wave1-cognitive-program@v1` is likewise deliberately absent and has the same boundary.
`wave2-cognitive-program@v1` is also deliberately absent: selected-live admission
rejects it before any runs root, manifest, review, subject, provider, or credentialed
live evidence layer can exist.

Every selected live case requires an explicitly configured model credential; the Wave0
Case also requires `TAVILY_API_KEY`. Call it only after deliberately wiring the declared
production subject and dependencies. `run_selected_live_case` executes once.
`run_selected_live_case_series` performs only the case declaration's fresh repetition
count (three for the two direction-loop cases), with a new isolated Evaluation Bundle
per invocation. Neither entrypoint retries, resumes, auto-reviews, or changes production
prompt/code.

Credential preflight happens before a subject, provider, production Bundle, Evaluation
Bundle, or Review Record is created. A missing credential is an honest limited live
disposition, not a deterministic pass or failure and not a release requirement. These
manual operations are not collected by pytest or routine CI.

The public controller direction-loop case has a manual runner:
`scripts/controller_live_eval.py` builds the isolated real-model composition home (the
API key is read from `DEEPSEEK_API_KEY` at runtime and never committed), wires the
controller live subject, and invokes the selected-live entrypoint — `--mode single`
for one execution or `--mode series` for the declared repetitions. Optional
`--price-in`/`--price-out` (per million tokens) price the recorded token telemetry;
without them `cost_usd` records 0.0 and the execution output marks `cost_unpriced`.

After preflight succeeds, the selected-live helper is the only path that writes a
`credentialed_live_quality` manifest layer. That layer remains a bounded evaluation
record, not release authority and never a profile, State, or route input.

## Review A Bundle

A person or approved human-controlled interface separately supplies a
`ReviewSubmission` using the exact controls retained in the Bundle manifest. The
review service verifies every declared digest first, never reruns the subject, and
writes a distinct `reviews/<review-id>/record.json` beside the immutable Bundle.
Review can be deferred indefinitely; inspecting a Bundle never resumes execution. It
records execution status separately from the four-state cognitive review result, including
unknowns and variance, so a completed execution is not by itself a cognitive pass.
