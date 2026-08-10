"""Real topic planning node behavior.

@impl TOP-001
@impl TOP-002
@impl TOP-003
@impl TOP-004
@impl TOP-006
@impl EVH-015
@impl TOP-007
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import pytest

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef, bundle_profile_path
from deerflow_deep_research.domain.context import (
    GraphContextView,
    NodeAgentBundleContext,
    NodeAgentContext,
    NodeExecutionResult,
    SelectedBundleContext,
)
from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.domain.lifecycle import LifecycleStatus, TerminalReason
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.profile import ResearchProfile, compute_profile_content_hash, profile_state_fields
from deerflow_deep_research.domain.run_experience import (
    FailureCertainty,
    NodeProblem,
    ProviderObservation,
    RunFailureCode,
)
from deerflow_deep_research.domain.run_observation import RunEventCategory
from deerflow_deep_research.domain.state import MAX_TOPIC_REGISTRY_BYTES, ContentRef, PhaseStatus
from deerflow_deep_research.graph.nodes.topic_planning import node as topic_planning_node

BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "B" * 43)
BUNDLE_ID = BUNDLE.bundle_id.value


def _profile() -> ResearchProfile:
    return ResearchProfile(
        schema_version=2,
        depth="deep_dive",
        audience="domain_expert",
        format="annotated_bibliography",
        cost_tolerance="extensive",
        time_budget="overnight",
        must_answer=("Q1", "Q2"),
        scope_boundaries="Grid-scale stationary storage only.",
        custom_notes="Prioritize peer-reviewed lifecycle evidence.",
        comparison_required=True,
        comparison_subjects=("lithium-ion batteries", "vanadium redox flow batteries"),
        request_language="en",
        output_language="zh",
    )


PROFILE = _profile()
PROFILE_REF = ContentRef(
    sandbox_path=bundle_profile_path(BUNDLE),
    content_hash=compute_profile_content_hash(PROFILE),
    schema_version=1,
    short_summary="canonical profile",
)


class _ProfileReader:
    def __init__(self, profile: ResearchProfile = PROFILE, profile_ref: ContentRef = PROFILE_REF) -> None:
        self.profile = profile
        self.profile_ref = profile_ref
        self.refs: list[ContentRef] = []

    async def read_profile(self, profile_ref: ContentRef) -> ResearchProfile:
        self.refs.append(profile_ref)
        if profile_ref != self.profile_ref:
            raise ValueError("profile_ref_unexpected")
        return self.profile


def test_topic_planning_receives_a_selected_bundle_context_without_legacy_identity_or_checkpoint() -> None:
    """TOP-008: planning cannot choose its own Bundle or external State."""
    context = SelectedBundleContext(bundle=BUNDLE)
    assert context.bundle == BUNDLE
    assert set(SelectedBundleContext.model_fields) == {"bundle"}


def _topic(title: str, scope: str, *bindings: str) -> dict[str, object]:
    return {
        "title": title,
        "scope": scope,
        "must_answer_bindings": list(bindings),
        "search_dimensions": [],
        "exclusions": [],
    }


def _plan_json(*topics: dict[str, object]) -> str:
    return json.dumps({"schema_version": 1, "topics": list(topics)})


def _state(**overrides: object) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": 2,
        "bundle_id": BUNDLE_ID,
        "outer_thread_id": "thread-1",
        "request_text": "Compare storage options",
        "research_depth": "deep_dive",
        "target_audience": "domain_expert",
        "output_format": "annotated_bibliography",
        "cost_tolerance": "extensive",
        "time_budget": "overnight",
        "must_answer_questions": ("Q1", "Q2"),
        "degraded_profile": False,
        "phase": "topic_planning",
        "generation": 0,
        "execution_trace": (),
    }
    payload.update(profile_state_fields(PROFILE, PROFILE_REF))
    payload.update(overrides)
    return payload


class _Caps:
    def __init__(self, *results: object) -> None:
        self._results = list(results)
        self.requests: list[object] = []

    async def run_agent(self, *, context: NodeAgentContext, request: object) -> NodeExecutionResult:
        self.requests.append(request)
        if not self._results:
            raise AssertionError("unexpected run_agent")
        result = self._results.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result  # type: ignore[return-value]


def _result(
    summary: str,
    *,
    finish_reason: NodeFinishReason = NodeFinishReason.SUCCESS,
    problem: NodeProblem | None = None,
) -> NodeExecutionResult:
    return NodeExecutionResult(finish_reason=finish_reason, summary=summary, problem=problem)


def _deps(
    caps: _Caps,
    *,
    recorder: object | None = None,
    request_bundle: _ProfileReader | None = None,
) -> NodeBuildDependencies:
    graph = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    selected_bundle = SelectedBundleContext(bundle=BUNDLE)
    return NodeBuildDependencies(
        graph_context=graph,
        agent_context=NodeAgentContext(
            research_scope_id=BUNDLE_ID,
            node_name="topic_planning",
            attempt_id="g0-tp-a1",
            workspace_root=graph.workspace_root,
            attempt_root=f"{graph.workspace_root}/topic_planning",
            policy_name="topic-planning",
            bundle_context=NodeAgentBundleContext.from_selected_bundle(selected_bundle),
        ),
        capabilities=caps,
        event_recorder=recorder,  # type: ignore[arg-type]
        request_bundle=request_bundle or _ProfileReader(),
        selected_bundle=selected_bundle,
    )


def _covering_plan() -> str:
    return _plan_json(
        _topic("Batteries", "Grid battery economics", "Q1"),
        _topic("Solar", "Utility-scale solar economics", "Q2"),
    )


def _large_compact_plan() -> str:
    topics: list[dict[str, object]] = []
    for index in range(8):
        topics.append(
            {
                "title": f"Topic {index} " + "t" * 70,
                "scope": f"Distinct scope {index} " + "s" * 220,
                "must_answer_bindings": ["Q1" if index != 1 else "Q2"],
                "search_dimensions": [f"dimension {index}-{item} " + "d" * 64 for item in range(4)],
                "exclusions": [f"exclusion {index}-{item} " + "e" * 64 for item in range(4)],
            }
        )
    return _plan_json(*topics)


def _broad_parser_valid_plan() -> str:
    topics: list[dict[str, object]] = []
    for index, binding in enumerate(("Q1", "Q2")):
        topics.append(
            {
                "title": f"Broad topic {index} " + "t" * 88,
                "scope": f"Broad distinct scope {index} " + "s" * 300,
                "must_answer_bindings": [binding],
                "search_dimensions": [f"dimension {index}-{item} " + "d" * 84 for item in range(5)],
                "exclusions": [f"exclusion {index}-{item} " + "e" * 84 for item in range(5)],
            }
        )
    return _plan_json(*topics)


async def test_valid_plan_routes_next_and_records_registry() -> None:
    """@impl TOP-006
    @impl EVH-015
    """
    caps = _Caps(_result(_covering_plan()))
    result = await topic_planning_node.build_real(_deps(caps))(_state())
    assert result["route"] == "next"
    assert result["topic_refs"] == ("batteries", "solar")
    assert len(result["topic_registry"]) == 2
    assert result["topic_registry"][0]["topic_id"] == "batteries"
    assert len(caps.requests) == 1
    assert "deep_dive" in caps.requests[0].objective
    request = caps.requests[0]
    assert request.tools_enabled is False
    assert request.capability_ref is not None
    assert request.capability_ref.capability_id == "topic-planning-profile-decomposition"
    assert {topic["must_answer_bindings"][0] for topic in result["topic_registry"]} == {"Q1", "Q2"}


async def test_compact_plan_above_old_structured_truncation_routes_next() -> None:
    """@impl TOP-010

    A retained compact candidate is not clipped at the old 4096-byte cap.
    """
    summary = _large_compact_plan()
    assert 4_096 < len(summary.encode("utf-8")) <= 16_384

    result = await topic_planning_node.build_real(_deps(_Caps(_result(summary))))(_state())

    registry = result["topic_registry"]
    assert result["route"] == "next"
    assert len(registry) == 8
    assert len(json.dumps(registry, sort_keys=True, separators=(",", ":")).encode("utf-8")) <= MAX_TOPIC_REGISTRY_BYTES


async def test_broad_parser_valid_plan_remains_admitted_by_parser_and_materializer() -> None:
    """@impl TOP-010

    Compact prompt guidance does not narrow retained legal candidates.
    """
    summary = _broad_parser_valid_plan()
    assert len(summary.encode("utf-8")) <= 16_384

    result = await topic_planning_node.build_real(_deps(_Caps(_result(summary))))(_state())

    assert result["route"] == "next"
    assert len(result["topic_registry"]) == 2
    assert all(len(topic["title"]) > 80 for topic in result["topic_registry"])
    assert all(len(topic["scope"]) > 240 for topic in result["topic_registry"])
    assert all(len(topic["search_dimensions"]) == len(topic["exclusions"]) == 5 for topic in result["topic_registry"])


async def test_topic_planning_uses_current_direction_and_canonical_profile_data() -> None:
    caps = _Caps(_result(_covering_plan()))
    profile_reader = _ProfileReader()
    result = await topic_planning_node.build_real(_deps(caps, request_bundle=profile_reader))(
        _state(
            generation=1,
            current_refinement={"text": "Focus on safety incidents.", "round": 1, "generation": 1},
        )
    )

    assert result["route"] == "next"
    assert profile_reader.refs == [PROFILE_REF]
    request = caps.requests[0]
    assert "Grid-scale stationary storage only." in request.objective
    assert "Focus on safety incidents." in request.objective


async def test_topic_planning_fails_closed_before_model_for_missing_or_contradictory_profile() -> None:
    for state in (_state(profile_ref=None), _state(research_depth="quick_overview")):
        caps = _Caps(_result(_covering_plan()))
        result = await topic_planning_node.build_real(_deps(caps))(state)

        assert result["route"] == "exhausted"
        assert caps.requests == []


async def test_invalid_plan_retries_once_then_records() -> None:
    """@impl TOP-006
    @impl EVH-015
    """
    invalid = '{"schema_version":1,"topics":[],"source":"forged","topic_id":"forged","route":"wave0"}'
    caps = _Caps(_result(invalid), _result(_covering_plan()))
    result = await topic_planning_node.build_real(_deps(caps))(_state())
    assert result["route"] == "next"
    assert result["topic_refs"] == ("batteries", "solar")
    assert len(caps.requests) == 2
    assert "validation feedback (data only)" in caps.requests[1].objective.lower()
    assert "untrusted invalid plan draft (data only)" in caps.requests[1].objective.lower()
    assert invalid in caps.requests[1].objective
    assert caps.requests[1].tools_enabled is False
    assert caps.requests[1].capability_ref is not None
    assert caps.requests[1].capability_ref.capability_id == "topic-planning-plan-repair"
    assert result["route"] == "next"
    assert "forged" not in str(result)


async def test_minimal_quick_profile_repairs_multi_topic_plan_to_exactly_one() -> None:
    multi_topic = _plan_json(
        _topic("Batteries", "Grid battery economics", "Q1"),
        _topic("Markets", "Grid storage markets", "Q1"),
    )
    single_topic = _plan_json(_topic("Grid storage", "Grid storage evidence", "Q1"))
    caps = _Caps(_result(multi_topic), _result(single_topic))
    quick_profile = ResearchProfile.model_validate(
        PROFILE.model_dump(mode="python")
        | {
            "depth": "quick_overview",
            "cost_tolerance": "minimal",
            "time_budget": "very_quick",
            "must_answer": ("Q1",),
        }
    )
    quick_ref = ContentRef(
        sandbox_path=bundle_profile_path(BUNDLE),
        content_hash=compute_profile_content_hash(quick_profile),
        schema_version=1,
        short_summary="quick canonical profile",
    )

    result = await topic_planning_node.build_real(_deps(caps, request_bundle=_ProfileReader(quick_profile, quick_ref)))(
        _state(**profile_state_fields(quick_profile, quick_ref))
    )

    assert result["route"] == "next"
    assert result["topic_refs"] == ("grid-storage",)
    assert len(caps.requests) == 2
    assert "validation feedback (data only)" in caps.requests[1].objective.lower()


async def test_repeated_invalid_plan_exhausts_without_topic_state() -> None:
    """@impl TOP-006
    @impl EVH-015
    """
    caps = _Caps(_result("not-json"), _result('{"still":"invalid"}'))
    result = await topic_planning_node.build_real(_deps(caps))(_state())
    assert result["route"] == "exhausted"
    assert result["terminal_status"] == LifecycleStatus.BLOCKED.value
    assert result["terminal_reason"] == TerminalReason.GATE_BLOCKED.value
    assert result["phase_status"] == PhaseStatus.TERMINAL.value
    assert "topic_refs" not in result
    assert "topic_registry" not in result
    assert all(request.tools_enabled is False for request in caps.requests)
    assert caps.requests[1].capability_ref is not None
    assert caps.requests[1].capability_ref.capability_id == "topic-planning-plan-repair"


async def test_uncovered_question_is_repaired_then_exhausts() -> None:
    # Only Q1 is covered on both attempts; Q2 stays uncovered.
    partial = _plan_json(_topic("Batteries", "Grid battery economics", "Q1"))
    caps = _Caps(_result(partial), _result(partial))
    result = await topic_planning_node.build_real(_deps(caps))(_state())
    assert result["route"] == "exhausted"
    assert "topic_registry" not in result


async def test_run_agent_failure_exhausts_without_topic_state() -> None:
    for failure in (
        RuntimeError("model unavailable"),
        _result("", finish_reason=NodeFinishReason.FAILED),
    ):
        result = await topic_planning_node.build_real(_deps(_Caps(failure)))(_state())
        assert result["route"] == "exhausted"
        assert "topic_refs" not in result
        assert "topic_registry" not in result


async def test_known_invocation_problem_survives_topic_planning_terminal_update() -> None:
    """@impl WFO-001"""
    sentinel = "provider body must not become terminal state"
    problem = NodeProblem(
        code=RunFailureCode.CONFIGURATION_MODEL_MISSING,
        phase="topic_planning",
        certainty=FailureCertainty.DIRECT,
    )
    caps = _Caps(_result(sentinel, finish_reason=NodeFinishReason.FAILED, problem=problem))

    result = await topic_planning_node.build_real(_deps(caps))(_state())

    assert result["route"] == "exhausted"
    assert result["terminal_status"] == LifecycleStatus.BLOCKED.value
    assert result["latest_incident"] == {
        "schema_version": 1,
        "code": "configuration.model_missing",
        "phase": "topic_planning",
        "certainty": "direct",
    }
    assert sentinel not in str(result)


class _RecoveryRecorder:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def record(self, **kwargs: object) -> None:
        self.calls.append(kwargs)


class _ValidationRecorder:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def record(self, **kwargs: object) -> None:
        self.calls.append(kwargs)


def _validation_events(recorder: _ValidationRecorder) -> list[dict[str, object]]:
    return [call for call in recorder.calls if call["category"] is RunEventCategory.VALIDATION]


async def test_valid_initial_topic_plan_publishes_a_phase_validation_fact() -> None:
    """@impl TOP-009
    @impl REJ-007
    """

    recorder = _ValidationRecorder()
    result = await topic_planning_node.build_real(_deps(_Caps(_result(_covering_plan())), recorder=recorder))(_state())

    assert result["route"] == "next"
    assert _validation_events(recorder) == [
        {
            "category": RunEventCategory.VALIDATION,
            "phase": "topic_planning",
            "validation_stage": "initial",
            "validation_codes": (),
        }
    ]


async def test_invalid_initial_topic_plan_then_repair_records_ordered_closed_codes() -> None:
    """@impl TOP-009
    @impl REJ-007
    """

    invalid_draft = "not-json untrusted-draft=keep-out"
    recorder = _ValidationRecorder()
    caps = _Caps(_result(invalid_draft), _result(_covering_plan()))

    result = await topic_planning_node.build_real(_deps(caps, recorder=recorder))(_state())

    assert result["route"] == "next"
    assert _validation_events(recorder) == [
        {
            "category": RunEventCategory.VALIDATION,
            "phase": "topic_planning",
            "validation_stage": "initial",
            "validation_codes": ("topic_plan_json_invalid",),
        },
        {
            "category": RunEventCategory.VALIDATION,
            "phase": "topic_planning",
            "validation_stage": "repair",
            "validation_codes": (),
        },
    ]
    assert invalid_draft not in str(_validation_events(recorder))


async def test_invalid_initial_and_repair_topic_plans_record_distinct_validation_facts() -> None:
    """@impl TOP-009
    @impl REJ-007
    """

    initial_draft = "not-json initial-draft=keep-out"
    repair_draft = '{"unexpected":"repair-draft=keep-out"}'
    recorder = _ValidationRecorder()
    caps = _Caps(_result(initial_draft), _result(repair_draft))

    result = await topic_planning_node.build_real(_deps(caps, recorder=recorder))(_state())

    assert result["route"] == "exhausted"
    assert _validation_events(recorder) == [
        {
            "category": RunEventCategory.VALIDATION,
            "phase": "topic_planning",
            "validation_stage": "initial",
            "validation_codes": ("topic_plan_json_invalid",),
        },
        {
            "category": RunEventCategory.VALIDATION,
            "phase": "topic_planning",
            "validation_stage": "repair",
            "validation_codes": ("topic_plan_extra_fields",),
        },
    ]
    retained = str(_validation_events(recorder))
    assert initial_draft not in retained
    assert repair_draft not in retained


async def test_topic_plan_materialization_collapses_dynamic_coverage_detail() -> None:
    """@impl TOP-009
    @impl REJ-007
    """

    uncovered_question = "Q2"
    partial_plan = _plan_json(_topic("Batteries", "Grid battery economics", "Q1"))
    recorder = _ValidationRecorder()
    caps = _Caps(_result(partial_plan), _result(_covering_plan()))

    result = await topic_planning_node.build_real(_deps(caps, recorder=recorder))(_state())

    assert result["route"] == "next"
    events = _validation_events(recorder)
    assert [event["validation_codes"] for event in events] == [
        ("topic_coverage_uncovered",),
        (),
    ]
    assert uncovered_question not in str(events)
    assert partial_plan not in str(events)


async def test_topic_planning_invocation_failure_before_candidate_emits_no_validation_fact() -> None:
    """@impl TOP-009
    @impl REJ-007
    """

    recorder = _ValidationRecorder()
    caps = _Caps(RuntimeError("provider failure raw-detail=keep-out"))

    result = await topic_planning_node.build_real(_deps(caps, recorder=recorder))(_state())

    assert result["route"] == "exhausted"
    assert "topic_registry" not in result
    assert _validation_events(recorder) == []


def test_topic_planning_validation_code_mappers_are_closed_and_redacted() -> None:
    """@impl TOP-009"""

    for code in (
        "topic_plan_empty",
        "topic_plan_json_invalid",
        "topic_plan_extra_fields",
        "topic_plan_invalid",
    ):
        assert topic_planning_node._canonical_parser_validation_code(ValueError(code)) == code
    assert (
        topic_planning_node._canonical_parser_validation_code(ValueError("raw parser detail=keep-out"))
        == "topic_plan_invalid"
    )

    for code in (
        "topic_count_profile_mismatch",
        "topic_coverage_empty",
        "topic_duplicate_slug",
        "topic_overlap",
        "topic_coverage_uncovered",
        "topic_materialization_invalid",
    ):
        assert topic_planning_node._canonical_materialization_validation_code(ValueError(code)) == code
    assert (
        topic_planning_node._canonical_materialization_validation_code(
            ValueError("topic_coverage_uncovered:dynamic question=keep-out")
        )
        == "topic_coverage_uncovered"
    )
    assert (
        topic_planning_node._canonical_materialization_validation_code(ValueError("raw materializer detail=keep-out"))
        == "topic_materialization_invalid"
    )


def _provider_timeout_problem() -> NodeProblem:
    return NodeProblem(
        code=RunFailureCode.PROVIDER_TIMEOUT,
        phase="topic_planning",
        certainty=FailureCertainty.DIRECT,
        provider_observation=ProviderObservation(
            configured_service_label="topic-planner-model",
            response_kind="no_response",
        ),
    )


@pytest.mark.parametrize(
    "code",
    [
        pytest.param("provider.usage_unavailable", id="usage-unavailable"),
        pytest.param("budget.exhausted", id="budget-exhausted"),
        pytest.param("policy.denied", id="policy-denied"),
    ],
)
async def test_closed_phase_stops_do_not_enter_provider_recovery(code: str) -> None:
    problem = NodeProblem.model_validate(
        {
            "code": code,
            "phase": "topic_planning",
            "certainty": "direct",
        }
    )
    caps = _Caps(_result("raw stop detail must not survive", finish_reason=NodeFinishReason.FAILED, problem=problem))
    recorder = _RecoveryRecorder()

    result = await topic_planning_node.build_real(_deps(caps, recorder=recorder))(_state())

    assert result["route"] == "exhausted"
    assert len(caps.requests) == 1
    assert recorder.calls == []
    assert result["latest_incident"] == {
        "schema_version": 1,
        "code": code,
        "phase": "topic_planning",
        "certainty": "direct",
    }


@pytest.mark.parametrize(
    "budget_stop_reason",
    (
        pytest.param("per_call_output_cap", id="response-output-cap"),
        pytest.param("token_admission", id="pre-provider-token-admission"),
    ),
)
async def test_topic_planning_budget_stops_publish_no_state_or_recovery(budget_stop_reason: str) -> None:
    """@impl TOP-010

    Budget details stay bridge-owned; the node remains a closed stop.
    """
    problem = NodeProblem(
        code=RunFailureCode.BUDGET_EXHAUSTED,
        phase="topic_planning",
        certainty=FailureCertainty.DIRECT,
    )
    caps = _Caps(_result("untrusted budget body", finish_reason=NodeFinishReason.FAILED, problem=problem))
    recorder = _RecoveryRecorder()

    result = await topic_planning_node.build_real(_deps(caps, recorder=recorder))(_state())

    assert budget_stop_reason in {"per_call_output_cap", "token_admission"}
    assert result["route"] == "exhausted"
    assert result["terminal_status"] == LifecycleStatus.BLOCKED.value
    assert result["latest_incident"]["code"] == "budget.exhausted"
    assert "topic_refs" not in result
    assert "topic_registry" not in result
    assert len(caps.requests) == 1
    assert recorder.calls == []


@pytest.mark.parametrize(
    "code",
    [
        pytest.param("provider.usage_unavailable", id="usage-unavailable"),
        pytest.param("budget.exhausted", id="budget-exhausted"),
        pytest.param("policy.denied", id="policy-denied"),
    ],
)
async def test_provider_retry_followed_by_closed_phase_stop_retains_history_without_final_observation(
    monkeypatch: pytest.MonkeyPatch,
    code: str,
) -> None:
    final_problem = NodeProblem.model_validate(
        {
            "code": code,
            "phase": "topic_planning",
            "certainty": "direct",
        }
    )
    caps = _Caps(
        _result("raw provider body", finish_reason=NodeFinishReason.FAILED, problem=_provider_timeout_problem()),
        _result("raw stop detail", finish_reason=NodeFinishReason.FAILED, problem=final_problem),
    )
    recorder = _RecoveryRecorder()

    async def fake_sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    result = await topic_planning_node.build_real(_deps(caps, recorder=recorder))(_state())

    assert result["route"] == "exhausted"
    assert len(caps.requests) == 2
    incident = result["latest_incident"]
    assert incident["code"] == code
    assert incident["diagnostic_ref"].startswith("diag_")
    assert "provider_observation" not in incident
    assert incident["provider_recovery"]["disposition"] == "retry_followed_by_terminal_failure"
    assert [call["category"] for call in recorder.calls] == [
        RunEventCategory.ATTEMPT,
        RunEventCategory.RETRY,
        RunEventCategory.ATTEMPT,
    ]


async def test_provider_timeout_recovers_once_then_retains_safe_terminal_incident(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl WFO-001

    BUG-010: one eligible topic-planning timeout receives one phase-owned recovery;
    its exhausted result remains a typed incident and cannot publish topic authority.
    """
    sentinel = "raw provider body secret=sentinel /Users/alice/private"
    first = _provider_timeout_problem()
    second = _provider_timeout_problem()
    caps = _Caps(
        _result(sentinel, finish_reason=NodeFinishReason.FAILED, problem=first),
        _result(sentinel, finish_reason=NodeFinishReason.FAILED, problem=second),
    )
    recorder = _RecoveryRecorder()
    sleeps: list[float] = []

    async def fake_sleep(delay: float) -> None:
        sleeps.append(delay)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    result = await topic_planning_node.build_real(_deps(caps, recorder=recorder))(_state())

    assert result["route"] == "exhausted"
    assert result["terminal_status"] == LifecycleStatus.BLOCKED.value
    assert len(caps.requests) == 2
    assert sleeps == [1.0]
    assert "topic_refs" not in result
    assert "topic_registry" not in result
    incident = result["latest_incident"]
    assert incident["code"] == "provider.timeout"
    assert incident["phase"] == "topic_planning"
    assert incident["diagnostic_ref"].startswith("diag_")
    assert incident["provider_recovery"] == {
        "trigger_category": "provider.timeout",
        "trigger_observation": {
            "configured_service_label": "topic-planner-model",
            "response_kind": "no_response",
        },
        "trigger_invocation_ordinal": 1,
        "model_attempts": 2,
        "automatic_retries": 1,
        "disposition": "exhausted",
    }
    assert [call["category"] for call in recorder.calls] == [
        RunEventCategory.ATTEMPT,
        RunEventCategory.RETRY,
        RunEventCategory.ATTEMPT,
        RunEventCategory.EXHAUSTION,
    ]
    assert all(call["phase"] == "topic_planning" for call in recorder.calls)
    assert sentinel not in str(result)


async def test_initial_provider_timeout_recovers_once_then_accepts_a_valid_plan(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timeout = _provider_timeout_problem()
    caps = _Caps(
        _result("", finish_reason=NodeFinishReason.FAILED, problem=timeout),
        _result(_covering_plan()),
    )
    sleeps: list[float] = []

    async def fake_sleep(delay: float) -> None:
        sleeps.append(delay)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    result = await topic_planning_node.build_real(_deps(caps))(_state())

    assert result["route"] == "next"
    assert result["topic_refs"] == ("batteries", "solar")
    assert len(caps.requests) == 2
    assert caps.requests[0] == caps.requests[1]
    assert sleeps == [1.0]
    assert "latest_incident" not in result


async def test_structured_output_repair_timeout_does_not_start_provider_recovery(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timeout = _provider_timeout_problem()
    caps = _Caps(
        _result("not-json"),
        _result("", finish_reason=NodeFinishReason.FAILED, problem=timeout),
    )
    recorder = _RecoveryRecorder()
    sleeps: list[float] = []

    async def fake_sleep(delay: float) -> None:
        sleeps.append(delay)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    result = await topic_planning_node.build_real(_deps(caps, recorder=recorder))(_state())

    assert result["route"] == "exhausted"
    assert len(caps.requests) == 2
    assert "validation feedback (data only)" in caps.requests[1].objective.lower()
    assert sleeps == []
    assert "topic_refs" not in result
    assert "topic_registry" not in result
    assert result["latest_incident"]["provider_recovery"] == {
        "trigger_category": "provider.timeout",
        "trigger_observation": {
            "configured_service_label": "topic-planner-model",
            "response_kind": "no_response",
        },
        "trigger_invocation_ordinal": 2,
        "model_attempts": 2,
        "automatic_retries": 0,
        "disposition": "retry_not_started_budget_consumed",
    }
    assert [call["category"] for call in recorder.calls] == [
        RunEventCategory.VALIDATION,
        RunEventCategory.ATTEMPT,
    ]


async def test_empty_must_answer_uses_request_text_for_coverage() -> None:
    plan = _plan_json(_topic("Storage options", "All storage options", "Compare storage options"))
    caps = _Caps(_result(plan))
    degraded_profile = ResearchProfile.model_validate(
        PROFILE.model_dump(mode="python") | {"must_answer": (), "degraded_profile": True}
    )
    degraded_ref = ContentRef(
        sandbox_path=bundle_profile_path(BUNDLE),
        content_hash=compute_profile_content_hash(degraded_profile),
        schema_version=1,
        short_summary="degraded canonical profile",
    )
    result = await topic_planning_node.build_real(
        _deps(caps, request_bundle=_ProfileReader(degraded_profile, degraded_ref))
    )(_state(**profile_state_fields(degraded_profile, degraded_ref)))
    assert result["route"] == "next"
    assert result["topic_refs"] == ("storage-options",)
