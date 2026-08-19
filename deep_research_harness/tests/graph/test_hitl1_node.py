"""Real HITL1 node behavior.

@impl HIN-001
@impl HIN-002
@impl HIN-003
@impl HIN-004
@impl HIN-005
@impl HIN-008
@impl HIN-007
@impl HIN-010
@impl NAC-003
@impl NAC-004
@impl EVH-012
@impl NAC-005
@impl EVH-013
@impl HIN-011
@impl HIC-004
@impl EVH-014
@impl HIN-012
@impl RER-010
@impl RER-011
"""

from __future__ import annotations

import asyncio
import json
from contextvars import ContextVar
from dataclasses import replace
from typing import Any

import pytest

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef
from deerflow_deep_research.domain.context import GraphContextView, NodeAgentContext, NodeExecutionResult
from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.domain.lifecycle import (
    AcceptedHumanResponse,
    InternalCancelDecision,
    LifecycleStatus,
    ResponseKind,
    TerminalReason,
    make_hitl_request_id,
)
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.profile import ResearchProfile
from deerflow_deep_research.domain.run_experience import (
    FailureCertainty,
    NodeProblem,
    ProviderObservation,
    ProviderRecoveryProjection,
    RunFailureCode,
)
from deerflow_deep_research.domain.run_observation import RunEventCategory
from deerflow_deep_research.domain.state import BundleLocalState, ContentRef, PhaseStatus
from deerflow_deep_research.graph.nodes.hitl1 import node as hitl1_node

BUNDLE_ID = "r_" + "A" * 43
_BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "B" * 43)
_GRAPH_STATE_SEED: ContextVar[dict[str, Any] | None] = ContextVar("hitl1_graph_state_seed", default=None)


def test_hitl1_receives_a_selected_bundle_context_without_legacy_identity_or_checkpoint() -> None:
    """HIN-015: node input cannot select a Run or checkpoint."""
    from deerflow_deep_research.domain.context import SelectedBundleContext

    bundle = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "B" * 43)
    context = SelectedBundleContext(bundle=bundle)
    assert context.bundle == bundle
    assert "bundle_id" not in context.model_fields
    assert "checkpoint" not in context.model_fields


def _brief_json(**overrides: object) -> str:
    payload: dict[str, object] = {
        "schema_version": 2,
        "brief_summary": "A structured research intake brief.",
        "depth": "standard",
        "audience": "practitioner",
        "format": "detailed_report",
        "cost_tolerance": "moderate",
        "time_budget": "standard",
        "must_answer": ["Q1"],
        "scope_boundaries": "Scope",
        "custom_notes": "",
        "comparison_required": False,
        "comparison_subjects": None,
        "request_language": "en",
        "output_language": "en",
    }
    payload.update(overrides)
    return json.dumps(payload)


def _state(**overrides: object) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": 2,
        "bundle_id": BUNDLE_ID,
        "outer_thread_id": "thread-1",
        "start_message_id": "human-start",
        "request_digest": "d_" + "B" * 43,
        "request_text": "Research storage options",
        "phase": "hitl1",
        "generation": 0,
        "consumed_request_ids": (),
        "consumed_message_ids": (),
        "execution_trace": (),
    }
    payload.update(overrides)
    _GRAPH_STATE_SEED.set(payload)
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


class _RequestStore:
    def __init__(self, bundle_state: BundleLocalState | None = None) -> None:
        self.writes: list[ResearchProfile] = []
        self.events: list[tuple[str, bool]] = []
        self._state = bundle_state

    def _initial_state(self) -> BundleLocalState:
        seed = _GRAPH_STATE_SEED.get() or {}
        return BundleLocalState(
            bundle_id=_BUNDLE.bundle_id,
            implementation_mode="all_real",
            generation=int(seed.get("generation", 0)),
            start_message_id=str(seed.get("start_message_id") or "human-start"),
            start_request_digest=seed.get("request_digest"),
            hitl1_visit_count=sum(item == "hitl1" for item in seed.get("execution_trace", ())),
            profile_ref=seed.get("profile_ref"),
            research_depth=seed.get("research_depth", ""),
            target_audience=seed.get("target_audience", ""),
            output_format=seed.get("output_format", ""),
            cost_tolerance=seed.get("cost_tolerance", ""),
            time_budget=seed.get("time_budget", ""),
            must_answer_questions=tuple(seed.get("must_answer_questions", ())),
            comparison_required=bool(seed.get("comparison_required", False)),
            comparison_subjects=tuple(seed.get("comparison_subjects", ())),
            request_language=seed.get("request_language", ""),
            output_language=seed.get("output_language", ""),
            degraded_profile=bool(seed.get("degraded_profile", False)),
            pending_profile=seed.get("pending_profile"),
            profile_followup_round=int(seed.get("profile_followup_round", 0)),
            proposed_profile=seed.get("proposed_profile"),
            profile_rejection_round=int(seed.get("profile_rejection_round", 0)),
            profile_feedback_cursor_message_id=seed.get("profile_feedback_cursor_message_id", ""),
            proposal_version=int(seed.get("proposal_version", 0)),
            interaction_feedback=seed.get("interaction_feedback"),
            consumed_request_ids=tuple(seed.get("consumed_request_ids", ())),
            consumed_message_ids=tuple(seed.get("consumed_message_ids", ())),
        )

    async def read_bundle_state(self) -> BundleLocalState:
        if self._state is None:
            self._state = self._initial_state()
        return self._state

    async def write_bundle_state(
        self,
        state: BundleLocalState,
        *,
        expected_revision: int,
    ) -> BundleLocalState:
        current = await self.read_bundle_state()
        if expected_revision != current.revision:
            raise ValueError("state_revision_conflict")
        self._state = replace(state, revision=expected_revision + 1)
        self.events.append(("state", self._state.profile_ref is not None))
        return self._state

    async def write_profile(self, profile: ResearchProfile) -> ContentRef:
        self.writes.append(profile)
        self.events.append(("profile", False))
        return ContentRef(
            sandbox_path=(
                f"workspace/deep-research/scopes/{_BUNDLE.scope_bucket}/{_BUNDLE.bundle_id.value}/request/profile.json"
            ),
            content_hash="h_" + "A" * 43,
        )


def _result(
    summary: str,
    *,
    finish_reason: NodeFinishReason = NodeFinishReason.SUCCESS,
    problem: NodeProblem | None = None,
) -> NodeExecutionResult:
    return NodeExecutionResult(
        finish_reason=finish_reason,
        summary=summary,
        error_code=("provider_failure" if problem is not None else None),
        problem=problem,
    )


def _deps(caps: _Caps, store: _RequestStore | None = None, recorder: object | None = None) -> NodeBuildDependencies:
    if store is None:
        store = getattr(caps, "request_store", None)
        if store is None:
            store = _RequestStore()
            caps.request_store = store
    graph = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    return NodeBuildDependencies(
        graph_context=graph,
        agent_context=NodeAgentContext(
            research_scope_id=BUNDLE_ID,
            node_name="hitl1",
            attempt_id="g0-hitl1-a1",
            workspace_root=graph.workspace_root,
            attempt_root=f"{graph.workspace_root}/hitl1",
            policy_name="hitl1-profile",
        ),
        capabilities=caps,
        request_bundle=store,
        event_recorder=recorder,  # type: ignore[arg-type]
    )


def _accepted(request_id: str, value: str, message_id: str = "human-1") -> dict[str, Any]:
    return AcceptedHumanResponse(
        request_id=request_id,
        message_id=message_id,
        value=value,
        response_kind=ResponseKind.TEXT,
    ).model_dump(mode="json")


def _option(request_id: str, option_id: str, message_id: str = "human-option") -> dict[str, Any]:
    return AcceptedHumanResponse(
        request_id=request_id,
        message_id=message_id,
        value=option_id,
        response_kind=ResponseKind.OPTION,
        option_id=option_id,
    ).model_dump(mode="json")


def _complete_response() -> str:
    return json.dumps(
        {
            "depth": "deep_dive",
            "audience": "domain_expert",
            "format": "annotated_bibliography",
            "cost_tolerance": "extensive",
            "time_budget": "overnight",
            "must_answer": ["Q1", "Q2"],
        }
    )


def _semantic_candidate_json(intent: str, **overrides: object) -> str:
    payload: dict[str, object] = {"intent": intent}
    payload.update(overrides)
    return json.dumps(payload)


def _revision_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": 2,
        "depth": "deep_dive",
        "audience": "domain_expert",
        "format": "annotated_bibliography",
        "cost_tolerance": "extensive",
        "time_budget": "overnight",
        "must_answer": ["Q1", "Q2"],
        "scope_boundaries": "Revised scope",
        "custom_notes": "",
        "comparison_required": False,
        "comparison_subjects": None,
        "request_language": "en",
        "output_language": "en",
    }
    payload.update(overrides)
    return payload


def _current_proposal() -> dict[str, object]:
    payload = json.loads(_brief_json())
    return {
        "schema_version": 2,
        **{
            field: payload[field]
            for field in (
                "depth",
                "audience",
                "format",
                "cost_tolerance",
                "time_budget",
                "must_answer",
                "scope_boundaries",
                "custom_notes",
            )
        },
        "comparison_required": False,
        "comparison_subjects": None,
        "request_language": "en",
        "output_language": "en",
    }


def _partial_profile(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": 2,
        "depth": None,
        "audience": None,
        "format": None,
        "cost_tolerance": None,
        "time_budget": None,
        "must_answer": [],
        "scope_boundaries": "",
        "custom_notes": "",
        "comparison_required": False,
        "comparison_subjects": None,
        "request_language": "en",
        "output_language": "en",
    }
    payload.update(overrides)
    return payload


def _v2_proposal(
    *,
    comparison_required: bool = False,
    comparison_subjects: list[str] | None = None,
    request_language: str = "en",
    output_language: str | None = "en",
) -> dict[str, object]:
    return {
        "schema_version": 3,
        **_current_proposal(),
        "comparison_required": comparison_required,
        "comparison_subjects": comparison_subjects,
        "request_language": request_language,
        "output_language": output_language,
    }


async def test_hitl1_request_id_uses_selected_bundle_not_legacy_graph_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """HIN-002/HIN-015: graph checkpoint identity cannot select a HITL request."""

    proposal = _v2_proposal()
    seen: list[str] = []

    def capture_interrupt(value: dict[str, Any]) -> None:
        seen.append(value["request"]["request_id"])
        raise RuntimeError("suspended")

    monkeypatch.setattr(hitl1_node, "interrupt", capture_interrupt)
    for legacy_research_id in (BUNDLE_ID, "r_" + "Z" * 43):
        store = _RequestStore(
            BundleLocalState(
                bundle_id=_BUNDLE.bundle_id,
                implementation_mode="all_real",
                start_message_id="human-start",
                proposed_profile=proposal,
                proposal_version=1,
            )
        )
        with pytest.raises(RuntimeError, match="suspended"):
            await hitl1_node.build_real(_deps(_Caps(), store))(
                _state(bundle_id=legacy_research_id, proposed_profile={"depth": "quick_overview"})
            )

    expected = make_hitl_request_id(
        bundle_id=_BUNDLE.bundle_id.value,
        phase="hitl1",
        generation=0,
        ordinal=1,
    )
    assert seen == [expected, expected]


async def test_bundle_pending_profile_survives_graph_replay_and_reuses_the_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """HIN-015: Bundle State, rather than a replayed graph projection, owns pending HITL1."""

    seen: list[dict[str, Any]] = []

    def capture_interrupt(value: dict[str, Any]) -> None:
        seen.append(value)
        raise RuntimeError("suspended")

    monkeypatch.setattr(hitl1_node, "interrupt", capture_interrupt)
    store = _RequestStore(
        BundleLocalState(
            bundle_id=_BUNDLE.bundle_id,
            implementation_mode="all_real",
            start_message_id="human-start",
            proposed_profile=_v2_proposal(),
            proposal_version=1,
        )
    )
    with pytest.raises(RuntimeError, match="suspended"):
        await hitl1_node.build_real(_deps(_Caps(), store))(_state(bundle_id="r_" + "X" * 43))

    suspended = await store.read_bundle_state()
    assert suspended.pending_request_id is not None
    assert suspended.hitl1_visit_count == 1
    restarted = _RequestStore(suspended)
    with pytest.raises(RuntimeError, match="suspended"):
        await hitl1_node.build_real(_deps(_Caps(), restarted))(
            _state(
                bundle_id="r_" + "Y" * 43,
                proposed_profile={"depth": "quick_overview"},
                proposal_version=99,
            )
        )

    replayed = await restarted.read_bundle_state()
    assert seen[0]["request"]["request_id"] == seen[1]["request"]["request_id"] == suspended.pending_request_id
    assert replayed.hitl1_visit_count == 1
    assert seen[1]["request"]["interaction"]["subject"]["proposal"]["depth"] == "standard"


async def test_accepted_profile_writes_content_before_its_bundle_state_reference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """HIN-004: final graph projection follows artifact then Bundle State publication."""

    store = _RequestStore(
        BundleLocalState(
            bundle_id=_BUNDLE.bundle_id,
            implementation_mode="all_real",
            start_message_id="human-start",
            proposed_profile=_v2_proposal(),
            proposal_version=1,
        )
    )
    monkeypatch.setattr(
        hitl1_node,
        "interrupt",
        lambda value: _accepted(value["request"]["request_id"], "confirmed", "human-accepted"),
    )

    result = await hitl1_node.build_real(_deps(_Caps(), store))(_state())
    persisted = await store.read_bundle_state()

    assert result["route"] == "accepted"
    assert store.events[-2:] == [("profile", False), ("state", True)]
    assert persisted.profile_ref == result["profile_ref"]
    assert persisted.pending_request_id is None
    assert persisted.consumed_message_ids == ("human-accepted",)


async def test_first_visit_generates_brief_and_interrupts(monkeypatch: pytest.MonkeyPatch) -> None:
    caps = _Caps(_result(_brief_json()))
    store = _RequestStore()
    seen: list[dict[str, Any]] = []

    def fake_interrupt(value: dict[str, Any]) -> None:
        seen.append(value)
        raise RuntimeError("interrupt")

    monkeypatch.setattr(hitl1_node, "interrupt", fake_interrupt)
    run = hitl1_node.build_real(_deps(caps, store))
    proposal = await run(_state())
    assert proposal["route"] == "needs_followup"
    with pytest.raises(RuntimeError, match="interrupt"):
        await run(_state(proposed_profile=proposal["proposed_profile"], execution_trace=("hitl1",)))

    assert len(caps.requests) == 1
    assert "Research storage options" in caps.requests[0].objective
    assert caps.requests[0].capability_ref is not None
    assert caps.requests[0].capability_ref.capability_id == "hitl1-profile-brief"
    assert caps.requests[0].tools_enabled is False
    assert seen[0]["phase"] == "hitl1"
    assert seen[0]["request"]["mode"] == "text"
    context = json.loads(seen[0]["request"]["context"])
    assert "action_ids" not in context
    assert "json" not in context["instructions"].lower()
    assert seen[0]["request"]["action_ids"] == ["accept_suggestion"]


async def test_generic_comparison_suspends_for_a_pair_without_acceptance(monkeypatch: pytest.MonkeyPatch) -> None:
    request_text = "比较两种储能路线的成本、风险与适用场景"
    caps = _Caps(_result(_brief_json(brief_summary="一份结构化的储能研究配置。")))
    store = _RequestStore()
    seen: list[dict[str, Any]] = []

    def fake_interrupt(value: dict[str, Any]) -> None:
        seen.append(value)
        raise RuntimeError("comparison followup")

    monkeypatch.setattr(hitl1_node, "interrupt", fake_interrupt)
    run = hitl1_node.build_real(_deps(caps, store))
    proposal = await run(_state(request_text=request_text))
    assert proposal["proposed_profile"]["comparison_required"] is True
    assert proposal["proposed_profile"]["comparison_subjects"] is None
    assert proposal["proposed_profile"]["output_language"] == "zh"

    with pytest.raises(RuntimeError, match="comparison followup"):
        await run(
            _state(
                request_text=request_text,
                proposed_profile=proposal["proposed_profile"],
                execution_trace=("hitl1",),
            )
        )

    pending = seen[0]["request"]
    assert pending["mode"] == "text"
    assert pending["action_ids"] == []
    assert pending["interaction"]["missing_material"] == ["comparison_subjects"]
    assert pending["interaction"]["controls"] == []
    assert "comparison_subjects" in json.loads(pending["context"])["missing_dimensions"]
    assert store.writes == []


async def test_explicit_source_pair_and_language_are_projected_before_acceptance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request_text = "Compare lithium-ion batteries and vanadium redox flow batteries"
    caps = _Caps(_result(_brief_json()))
    seen: list[dict[str, Any]] = []

    def fake_interrupt(value: dict[str, Any]) -> None:
        seen.append(value)
        raise RuntimeError("complete proposal")

    monkeypatch.setattr(hitl1_node, "interrupt", fake_interrupt)
    run = hitl1_node.build_real(_deps(caps))
    proposal = await run(_state(request_text=request_text))
    assert proposal["proposed_profile"]["comparison_subjects"] == {
        "subjects": ["lithium-ion batteries", "vanadium redox flow batteries"]
    }

    with pytest.raises(RuntimeError, match="complete proposal"):
        await run(
            _state(
                request_text=request_text,
                proposed_profile=proposal["proposed_profile"],
                execution_trace=("hitl1",),
            )
        )

    interaction = seen[0]["request"]["interaction"]
    assert interaction["subject"]["proposal"]["comparison_subjects"] == [
        "lithium-ion batteries",
        "vanadium redox flow batteries",
    ]
    assert interaction["subject"]["proposal"]["output_language"] == "en"
    assert seen[0]["request"]["action_ids"] == ["accept_suggestion"]


async def test_unsupported_request_language_uses_only_the_correlated_language_choice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    caps = _Caps(_result(_brief_json()))
    seen: list[dict[str, Any]] = []

    def fake_interrupt(value: dict[str, Any]) -> None:
        seen.append(value)
        raise RuntimeError("language choice")

    monkeypatch.setattr(hitl1_node, "interrupt", fake_interrupt)
    run = hitl1_node.build_real(_deps(caps))
    proposal = await run(_state(request_text="12345"))
    with pytest.raises(RuntimeError, match="language choice"):
        await run(
            _state(
                request_text="12345",
                proposed_profile=proposal["proposed_profile"],
                execution_trace=("hitl1",),
            )
        )

    pending = seen[0]["request"]
    assert pending["mode"] == "choice"
    assert [option["id"] for option in pending["options"]] == ["zh", "en"]
    assert pending["action_ids"] == []
    assert "interaction" not in pending


async def test_final_answer_round_blocks_missing_comparison_pair_without_writing_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = _RequestStore()
    pending = _v2_proposal(
        comparison_required=True,
        comparison_subjects=None,
        request_language="zh",
        output_language="zh",
    )

    monkeypatch.setattr(
        hitl1_node,
        "interrupt",
        lambda value: _accepted(value["request"]["request_id"], _complete_response()),
    )
    result = await hitl1_node.build_real(_deps(_Caps(), store))(
        _state(
            request_text="比较储能路线",
            pending_profile=pending,
            profile_followup_round=2,
            execution_trace=("hitl1", "hitl1"),
        )
    )

    assert result["route"] == "exhausted"
    assert result["terminal_reason"] == TerminalReason.GATE_BLOCKED.value
    assert "profile_ref" not in result
    assert result["execution_trace"] == ("hitl1",)
    assert store.writes == []


@pytest.mark.parametrize("request_text", ("比较两种储能路线", "12345"))
async def test_non_interactive_missing_pair_or_language_blocks_without_artifact(request_text: str) -> None:
    store = _RequestStore()
    result = await hitl1_node.build_real(_deps(_Caps(), store))(
        _state(request_text=request_text, non_interactive_policy={"auto_profile": True})
    )

    assert result["route"] == "exhausted"
    assert result["terminal_reason"] == TerminalReason.GATE_BLOCKED.value
    assert "profile_ref" not in result
    assert store.writes == []


async def test_non_interactive_auto_profile_stays_outside_interactive_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl HIN-014

    The existing non-interactive policy reaches its profile writer without an
    interrupt or a model-backed interactive confirmation.
    """
    caps = _Caps()
    store = _RequestStore()
    monkeypatch.setattr(
        hitl1_node,
        "interrupt",
        lambda _value: (_ for _ in ()).throw(AssertionError("non-interactive policy must not interrupt")),
    )

    result = await hitl1_node.build_real(_deps(caps, store))(_state(non_interactive_policy={"auto_profile": True}))

    assert result["route"] == "accepted"
    assert result["degraded_profile"] is True
    assert result["proposed_profile"] is None
    assert result["execution_trace"] == ("hitl1", "hitl1_auto_profile")
    assert len(store.writes) == 1
    assert store.writes[0].degraded_profile is True
    assert caps.requests == []


async def test_non_interactive_declared_minimal_intent_seeds_trio_and_must_answer() -> None:
    """@impl HIN-014

    A declared minimal intent constructs the single-topic profile trio and the
    must-answer question, without a model call.

    @impl EXI-001
    @impl LSA-001  # deterministic single-topic profile wiring; real-provider
                   # behavior is separately evidenced by runbook-003
    """
    caps = _Caps()
    store = _RequestStore()
    result = await hitl1_node.build_real(_deps(caps, store))(
        _state(non_interactive_policy={"auto_profile": True, "profile_intent": "minimal"})
    )

    assert result["route"] == "accepted"
    assert result["research_depth"] == "quick_overview"
    assert result["cost_tolerance"] == "minimal"
    assert result["time_budget"] == "very_quick"
    assert result["must_answer_questions"] == ("Research storage options",)
    assert result["degraded_profile"] is True
    assert len(store.writes) == 1
    written = store.writes[0]
    assert written.depth.value == "quick_overview"
    assert written.cost_tolerance.value == "minimal"
    assert written.time_budget.value == "very_quick"
    assert written.must_answer == ("Research storage options",)
    assert written.degraded_profile is True
    assert caps.requests == []


async def test_non_interactive_absent_intent_keeps_degraded_profile_but_seeds_must_answer() -> None:
    """@impl HIN-014

    Absent intent keeps the current degraded profile (no dimension fields) while
    the product fix seeds the must-answer question.
    """
    store = _RequestStore()
    result = await hitl1_node.build_real(_deps(_Caps(), store))(_state(non_interactive_policy={"auto_profile": True}))

    assert result["route"] == "accepted"
    written = store.writes[0]
    assert written.depth is None
    assert written.cost_tolerance is None
    assert written.time_budget is None
    assert written.must_answer == ("Research storage options",)
    assert written.degraded_profile is True


async def test_non_interactive_overlong_request_blocks_without_profile() -> None:
    """@impl HIN-014

    An automatic request longer than the must-answer bound fails closed through
    the blocked path: no profile artifact, never a truncated question.
    """
    store = _RequestStore()
    result = await hitl1_node.build_real(_deps(_Caps(), store))(
        _state(request_text="x" * 257, non_interactive_policy={"auto_profile": True})
    )

    assert result["route"] == "exhausted"
    assert result["terminal_reason"] == TerminalReason.GATE_BLOCKED.value
    assert "profile_ref" not in result
    assert store.writes == []


@pytest.mark.parametrize(
    "confirmation",
    (
        "可以",
        "好的",
        "同意",
        "确认",
        "可以，我觉得你说的挺好",
        "yes",
        "yes please",
        "looks good",
        "i agree",
        "confirm",
        "confirmed",
    ),
)
async def test_local_clear_confirmations_bypass_the_semantic_bridge(
    monkeypatch: pytest.MonkeyPatch,
    confirmation: str,
) -> None:
    store = _RequestStore()
    monkeypatch.setattr(
        hitl1_node,
        "interrupt",
        lambda value: _accepted(value["request"]["request_id"], confirmation),
    )

    result = await hitl1_node.build_real(_deps(_Caps(), store))(
        _state(proposed_profile=_v2_proposal(), execution_trace=("hitl1",))
    )

    assert result["route"] == "accepted"
    assert len(store.writes) == 1


async def test_v2_semantic_revision_must_include_and_reprojects_typed_pair_and_language(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = _v2_proposal(
        comparison_required=True,
        comparison_subjects=["lithium-ion batteries", "vanadium redox flow batteries"],
    )
    revision = _revision_payload(
        schema_version=2,
        comparison_required=True,
        comparison_subjects=["sodium-ion batteries", "zinc-bromine flow batteries"],
        request_language="en",
        output_language="zh",
    )
    caps = _Caps(_result(_semantic_candidate_json("revise_proposal", revision=revision)))
    response_count = 0
    seen: list[dict[str, Any]] = []

    def fake_interrupt(value: dict[str, Any]) -> dict[str, Any] | None:
        nonlocal response_count
        seen.append(value)
        response_count += 1
        if response_count == 1:
            return _accepted(value["request"]["request_id"], "make it a different comparison")
        raise RuntimeError("revised proposal")

    monkeypatch.setattr(hitl1_node, "interrupt", fake_interrupt)
    run = hitl1_node.build_real(_deps(caps))
    revised = await run(_state(proposed_profile=original, proposal_version=1, execution_trace=("hitl1",)))
    assert revised["proposal_version"] == 2
    assert revised["proposed_profile"]["comparison_subjects"] == {
        "subjects": ["sodium-ion batteries", "zinc-bromine flow batteries"]
    }
    assert revised["proposed_profile"]["output_language"] == "zh"

    with pytest.raises(RuntimeError, match="revised proposal"):
        await run(
            _state(
                proposed_profile=revised["proposed_profile"],
                proposal_version=2,
                execution_trace=("hitl1", "hitl1"),
            )
        )
    subject = seen[-1]["request"]["interaction"]["subject"]["proposal"]
    assert subject["comparison_subjects"] == ["sodium-ion batteries", "zinc-bromine flow batteries"]
    assert subject["output_language"] == "zh"
    assert seen[0]["request"]["interaction"]["controls"][0]["id"] == "accept_current_proposal"


async def test_first_visit_retries_once_on_invalid_brief(monkeypatch: pytest.MonkeyPatch) -> None:
    caps = _Caps(_result('{"missing":true}'), _result(_brief_json()))
    seen: list[dict[str, Any]] = []

    def fake_interrupt(value: dict[str, Any]) -> None:
        seen.append(value)
        raise RuntimeError("interrupt")

    monkeypatch.setattr(hitl1_node, "interrupt", fake_interrupt)
    proposal = await hitl1_node.build_real(_deps(caps))(_state())
    with pytest.raises(RuntimeError, match="interrupt"):
        await hitl1_node.build_real(_deps(caps))(
            _state(proposed_profile=proposal["proposed_profile"], execution_trace=("hitl1",))
        )
    assert len(caps.requests) == 2
    assert "validation category (data)" in caps.requests[1].objective.lower()
    assert "structured_output_invalid" in caps.requests[1].objective
    assert [request.capability_ref.capability_id for request in caps.requests] == [
        "hitl1-profile-brief",
        "hitl1-profile-brief-repair",
    ]
    assert "untrusted invalid candidate (data)" in caps.requests[1].objective.lower()
    assert '{"missing":true}' in caps.requests[1].objective
    assert "validation category (data)" in caps.requests[1].objective.lower()
    assert all(request.tools_enabled is False for request in caps.requests)
    assert seen


async def test_brief_lifecycle_field_is_repaired_without_route_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl NAC-005
    @impl EVH-013

    A model-supplied lifecycle field is rejected by the typed result boundary.
    """
    caps = _Caps(_result(_brief_json(route="accepted")), _result(_brief_json()))
    monkeypatch.setattr(
        hitl1_node,
        "interrupt",
        lambda _value: (_ for _ in ()).throw(AssertionError("proposal is not accepted in this visit")),
    )

    proposal = await hitl1_node.build_real(_deps(caps))(_state())

    assert proposal["route"] == "needs_followup"
    assert proposal["proposed_profile"] is not None
    assert "profile_ref" not in proposal
    assert [request.capability_ref.capability_id for request in caps.requests] == [
        "hitl1-profile-brief",
        "hitl1-profile-brief-repair",
    ]
    assert "untrusted invalid candidate (data)" in caps.requests[1].objective.lower()
    assert '"route": "accepted"' in caps.requests[1].objective
    assert "validation category (data)" in caps.requests[1].objective.lower()


async def test_natural_confirmation_writes_current_proposal_and_routes_accepted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl HIN-009
    @impl HIN-011
    @impl HIC-004

    Scripted semantic output proves graph admission only, not live language quality.
    """
    caps = _Caps(_result(_brief_json()), _result(_semantic_candidate_json("accept_current_proposal")))
    store = _RequestStore()

    def fake_interrupt(value: dict[str, Any]) -> dict[str, Any]:
        return _accepted(value["request"]["request_id"], "确认，按这个方案开始吧。")

    monkeypatch.setattr(hitl1_node, "interrupt", fake_interrupt)
    proposal = await hitl1_node.build_real(_deps(caps, store))(_state())
    result = await hitl1_node.build_real(_deps(caps, store))(
        _state(proposed_profile=proposal["proposed_profile"], execution_trace=("hitl1",))
    )

    assert result["route"] == "accepted"
    assert result["profile_ref"].sandbox_path.endswith("/request/profile.json")
    assert result["research_depth"] == "standard"
    assert result["target_audience"] == "practitioner"
    assert result["output_format"] == "detailed_report"
    assert result["cost_tolerance"] == "moderate"
    assert result["time_budget"] == "standard"
    assert result["must_answer_questions"] == ("Q1",)
    assert result["pending_profile"] is None
    assert result["profile_followup_round"] == 0
    assert result["consumed_message_ids"] == ("human-1",)
    assert result["proposal_version"] == 0
    assert result["interaction_feedback"] is None
    assert store.writes[0].depth == "standard"
    assert len(caps.requests) == 2
    assert caps.requests[1].tools_enabled is False


async def test_semantic_revision_publishes_new_visible_proposal_before_acceptance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    caps = _Caps(_result(_semantic_candidate_json("revise_proposal", revision=_revision_payload())))
    store = _RequestStore()
    monkeypatch.setattr(
        hitl1_node,
        "interrupt",
        lambda value: _accepted(value["request"]["request_id"], "改成面向领域专家的深度版本。", "human-revise"),
    )

    revised = await hitl1_node.build_real(_deps(caps, store))(
        _state(proposed_profile=_current_proposal(), proposal_version=1, execution_trace=("hitl1",))
    )

    assert revised["route"] == "needs_followup"
    assert revised["proposed_profile"]["depth"] == "deep_dive"
    assert revised["proposed_profile"]["audience"] == "domain_expert"
    assert revised["proposal_version"] == 2
    assert revised["interaction_feedback"] is None
    assert revised["profile_rejection_round"] == 0
    assert revised["consumed_message_ids"] == ("human-revise",)
    assert store.writes == []

    seen: list[dict[str, Any]] = []

    def capture_interrupt(value: dict[str, Any]) -> None:
        seen.append(value)
        raise RuntimeError("interrupt")

    monkeypatch.setattr(hitl1_node, "interrupt", capture_interrupt)
    with pytest.raises(RuntimeError, match="interrupt"):
        await hitl1_node.build_real(_deps(_Caps()))(
            _state(
                proposed_profile=revised["proposed_profile"],
                proposal_version=revised["proposal_version"],
                consumed_request_ids=revised["consumed_request_ids"],
                consumed_message_ids=revised["consumed_message_ids"],
                profile_feedback_cursor_message_id=revised["profile_feedback_cursor_message_id"],
                execution_trace=("hitl1", "hitl1"),
            )
        )
    interaction = seen[0]["request"]["interaction"]
    assert interaction["subject"]["proposal_version"] == 2
    assert interaction["subject"]["proposal"]["depth"] == "deep_dive"
    assert interaction["controls"] == [
        {
            "id": "accept_current_proposal",
            "label": "Start with the current proposal",
            "consequence": "Start research using the proposal currently shown.",
        }
    ]


async def test_source_constrained_revision_stays_advisory_until_later_natural_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A source/citation constraint is a visible proposal field, never lifecycle authority."""
    revision = _revision_payload(
        must_answer=["Compare the alternatives using first-party sources and cite each material claim."],
        scope_boundaries="Use official first-party sources only; cite each material claim.",
        custom_notes="Prefer primary documentation and include citations.",
    )
    caps = _Caps(
        _result(
            _semantic_candidate_json(
                "ask_about_proposal",
                explanation="The current format keeps the requested comparison readable.",
            )
        ),
        _result(_semantic_candidate_json("revise_proposal", revision=revision)),
        _result(
            _semantic_candidate_json(
                "clarify",
                clarification="Would you like to revise any other profile setting?",
            )
        ),
        _result(_semantic_candidate_json("accept_current_proposal")),
    )
    store = _RequestStore()
    seen: list[dict[str, Any]] = []

    def fake_interrupt(value: dict[str, Any]) -> dict[str, Any]:
        seen.append(value)
        replies = (
            ("为什么建议这个报告格式？", "human-question"),
            ("请只使用官方一手资料，并为每个重要结论给出引用。", "human-revise-sources"),
            ("我还不确定是否需要继续改。", "human-ambiguous"),
            ("确认，按这个新版方案开始。", "human-confirm"),
        )
        reply, message_id = replies[len(seen) - 1]
        return _accepted(value["request"]["request_id"], reply, message_id)

    monkeypatch.setattr(hitl1_node, "interrupt", fake_interrupt)
    question = await hitl1_node.build_real(_deps(caps, store))(
        _state(proposed_profile=_current_proposal(), proposal_version=1, execution_trace=("hitl1",))
    )
    revised = await hitl1_node.build_real(_deps(caps, store))(
        _state(
            proposed_profile=question["proposed_profile"],
            proposal_version=question["proposal_version"],
            interaction_feedback=question["interaction_feedback"],
            profile_feedback_cursor_message_id=question["profile_feedback_cursor_message_id"],
            consumed_request_ids=question["consumed_request_ids"],
            consumed_message_ids=question["consumed_message_ids"],
            execution_trace=("hitl1", "hitl1"),
        )
    )

    assert question["interaction_feedback"]["kind"] == "proposal_explanation"
    assert revised["route"] == "needs_followup"
    assert revised["proposal_version"] == 2
    assert revised["proposed_profile"]["scope_boundaries"] == revision["scope_boundaries"]
    assert revised["proposed_profile"]["custom_notes"] == revision["custom_notes"]
    assert store.writes == []

    clarification = await hitl1_node.build_real(_deps(caps, store))(
        _state(
            proposed_profile=revised["proposed_profile"],
            proposal_version=revised["proposal_version"],
            profile_feedback_cursor_message_id=revised["profile_feedback_cursor_message_id"],
            consumed_request_ids=revised["consumed_request_ids"],
            consumed_message_ids=revised["consumed_message_ids"],
            execution_trace=("hitl1", "hitl1", "hitl1"),
        )
    )

    assert clarification["interaction_feedback"]["kind"] == "clarification"
    assert clarification["profile_rejection_round"] == 0
    assert clarification["profile_followup_round"] == 0
    assert clarification["proposed_profile"] == revised["proposed_profile"]

    accepted = await hitl1_node.build_real(_deps(caps, store))(
        _state(
            proposed_profile=clarification["proposed_profile"],
            proposal_version=clarification["proposal_version"],
            interaction_feedback=clarification["interaction_feedback"],
            consumed_request_ids=clarification["consumed_request_ids"],
            consumed_message_ids=clarification["consumed_message_ids"],
            profile_feedback_cursor_message_id=clarification["profile_feedback_cursor_message_id"],
            execution_trace=("hitl1", "hitl1", "hitl1", "hitl1"),
        )
    )

    assert accepted["route"] == "accepted"
    assert accepted["profile_ref"].sandbox_path.endswith("/request/profile.json")
    assert len(store.writes) == 1
    assert store.writes[0].scope_boundaries == revision["scope_boundaries"]
    assert len(caps.requests) == 4
    assert all(request.tools_enabled is False for request in caps.requests)
    for descriptor in seen:
        context = json.loads(descriptor["request"]["context"])
        assert "action_ids" not in context
        assert "json" not in context["instructions"].lower()
        assert descriptor["request"]["action_ids"] == ["accept_suggestion"]
        assert descriptor["request"]["interaction"]["controls"][0]["id"] == "accept_current_proposal"
    interaction = seen[2]["request"]["interaction"]
    assert interaction["subject"]["proposal_version"] == 2
    assert interaction["subject"]["proposal"]["scope_boundaries"] == revision["scope_boundaries"]
    assert interaction["subject"]["proposal"]["custom_notes"] == revision["custom_notes"]


async def test_semantic_question_retains_proposal_with_bounded_feedback(monkeypatch: pytest.MonkeyPatch) -> None:
    caps = _Caps(
        _result(
            _semantic_candidate_json(
                "ask_about_proposal",
                explanation="The detailed format fits the requested comparison and source requirements.",
            )
        )
    )
    store = _RequestStore()
    monkeypatch.setattr(
        hitl1_node,
        "interrupt",
        lambda value: _accepted(value["request"]["request_id"], "为什么建议详细报告？", "human-question"),
    )

    update = await hitl1_node.build_real(_deps(caps, store))(
        _state(proposed_profile=_current_proposal(), proposal_version=1, execution_trace=("hitl1",))
    )

    assert update["route"] == "needs_followup"
    assert update["proposed_profile"] == _current_proposal()
    assert update["proposal_version"] == 1
    assert update["interaction_feedback"] == {
        "kind": "proposal_explanation",
        "message": "The detailed format fits the requested comparison and source requirements.",
    }
    assert update["profile_rejection_round"] == 0
    assert update["profile_followup_round"] == 0
    assert update["consumed_message_ids"] == ("human-question",)
    assert store.writes == []


async def test_semantic_clarification_retains_proposal_without_consuming_legacy_round(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    caps = _Caps(
        _result(
            _semantic_candidate_json(
                "clarify",
                clarification="Do you want a different depth, audience, report format, cost tolerance, or time budget?",
            )
        )
    )
    monkeypatch.setattr(
        hitl1_node,
        "interrupt",
        lambda value: _accepted(value["request"]["request_id"], "这个不是很确定", "human-clarify"),
    )

    update = await hitl1_node.build_real(_deps(caps))(
        _state(proposed_profile=_current_proposal(), proposal_version=1, execution_trace=("hitl1",))
    )

    assert update["route"] == "needs_followup"
    assert update["interaction_feedback"]["kind"] == "clarification"
    assert update["profile_rejection_round"] == 0
    assert update["profile_followup_round"] == 0


async def test_question_ambiguity_and_semantic_fallback_preserve_one_current_proposal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl HIN-011
    @impl HIC-004
    @impl EVH-014

    Scripted candidates exercise admission; only node-owned fallback text is asserted.
    """
    timeout = _provider_problem(RunFailureCode.PROVIDER_TIMEOUT)
    caps = _Caps(
        _result(
            _semantic_candidate_json(
                "ask_about_proposal",
                explanation="The detailed format fits the requested comparison.",
            )
        ),
        _result(
            _semantic_candidate_json(
                "clarify",
                clarification="Would you like to revise depth, audience, or report format?",
            )
        ),
        _result("", finish_reason=NodeFinishReason.FAILED, problem=timeout),
        _result("", finish_reason=NodeFinishReason.FAILED, problem=timeout),
        _result("", finish_reason=NodeFinishReason.FAILED, problem=timeout),
    )
    store = _RequestStore()
    seen: list[dict[str, Any]] = []

    async def fake_sleep(_delay: float) -> None:
        return None

    def fake_interrupt(value: dict[str, Any]) -> dict[str, Any]:
        seen.append(value)
        replies = (
            ("为什么推荐这个报告格式？", "human-question"),
            ("我还不确定。", "human-ambiguous"),
            ("我还想知道更多。", "human-fallback"),
        )
        reply, message_id = replies[len(seen) - 1]
        return _accepted(value["request"]["request_id"], reply, message_id)

    monkeypatch.setattr(hitl1_node.asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(hitl1_node, "interrupt", fake_interrupt)
    initial = _state(proposed_profile=_current_proposal(), proposal_version=1, execution_trace=("hitl1",))

    question = await hitl1_node.build_real(_deps(caps, store))(initial)
    clarification = await hitl1_node.build_real(_deps(caps, store))(
        _state(
            proposed_profile=question["proposed_profile"],
            proposal_version=question["proposal_version"],
            interaction_feedback=question["interaction_feedback"],
            profile_feedback_cursor_message_id=question["profile_feedback_cursor_message_id"],
            consumed_request_ids=question["consumed_request_ids"],
            consumed_message_ids=question["consumed_message_ids"],
            execution_trace=("hitl1", "hitl1"),
        )
    )
    fallback = await hitl1_node.build_real(_deps(caps, store))(
        _state(
            proposed_profile=clarification["proposed_profile"],
            proposal_version=clarification["proposal_version"],
            interaction_feedback=clarification["interaction_feedback"],
            profile_feedback_cursor_message_id=clarification["profile_feedback_cursor_message_id"],
            consumed_request_ids=clarification["consumed_request_ids"],
            consumed_message_ids=clarification["consumed_message_ids"],
            execution_trace=("hitl1", "hitl1", "hitl1"),
        )
    )

    assert question["interaction_feedback"]["kind"] == "proposal_explanation"
    assert clarification["interaction_feedback"]["kind"] == "clarification"
    assert fallback["route"] == "needs_followup"
    assert fallback["proposed_profile"] == _current_proposal()
    assert fallback["interaction_feedback"]["kind"] == "semantic_unavailable"
    assert fallback["profile_rejection_round"] == 0
    assert fallback["profile_followup_round"] == 0
    assert store.writes == []
    fallback_message = fallback["interaction_feedback"]["message"].lower()
    assert "json" not in fallback_message
    assert "accept_suggestion" not in fallback_message
    assert len(caps.requests) == 5
    assert all(request.tools_enabled is False for request in caps.requests)
    assert all(descriptor["request"]["interaction"]["controls"] for descriptor in seen)


async def test_semantic_invalid_output_repairs_once_then_preserves_proposal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    invalid = _semantic_candidate_json("accept_current_proposal", route="next", checkpoint="forged")
    caps = _Caps(_result(invalid), _result('{"intent":"unknown"}'))
    monkeypatch.setattr(
        hitl1_node,
        "interrupt",
        lambda value: _accepted(value["request"]["request_id"], "我还想修改", "human-invalid"),
    )

    update = await hitl1_node.build_real(_deps(caps))(
        _state(proposed_profile=_current_proposal(), proposal_version=1, execution_trace=("hitl1",))
    )

    assert update["route"] == "needs_followup"
    assert update["proposed_profile"] == _current_proposal()
    assert update["interaction_feedback"]["kind"] == "semantic_invalid"
    assert update["profile_rejection_round"] == 0
    assert len(caps.requests) == 2
    assert "validation category (data)" in caps.requests[1].objective.lower()
    assert "semantic_candidate_invalid" in caps.requests[1].objective
    assert "untrusted invalid candidate (data)" in caps.requests[1].objective.lower()
    assert invalid in caps.requests[1].objective
    assert "checkpoint" in caps.requests[1].objective.lower()
    assert "profile_ref" not in update
    assert all(request.tools_enabled is False for request in caps.requests)
    assert caps.requests[0].capability_ref is not None
    assert caps.requests[0].capability_ref.capability_id == "hitl1-semantic-intake"
    assert caps.requests[1].capability_ref is not None
    assert caps.requests[1].capability_ref.capability_id == "hitl1-semantic-intake-repair"


async def test_legacy_complete_proposal_projects_compatible_first_interaction_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[dict[str, Any]] = []

    def capture_interrupt(value: dict[str, Any]) -> None:
        seen.append(value)
        raise RuntimeError("interrupt")

    monkeypatch.setattr(hitl1_node, "interrupt", capture_interrupt)
    with pytest.raises(RuntimeError, match="interrupt"):
        await hitl1_node.build_real(_deps(_Caps()))(
            _state(proposed_profile=_current_proposal(), execution_trace=("hitl1",))
        )

    interaction = seen[0]["request"]["interaction"]
    assert interaction["subject"]["proposal_version"] == 1
    assert interaction["feedback"] is None
    assert seen[0]["request"]["action_ids"] == ["accept_suggestion"]


async def test_cancel_routes_without_profile_write(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _RequestStore()
    monkeypatch.setattr(
        hitl1_node,
        "interrupt",
        lambda _value: InternalCancelDecision().model_dump(mode="json"),
    )
    result = await hitl1_node.build_real(_deps(_Caps(), store))(
        _state(
            proposed_profile=_current_proposal(),
            proposal_version=2,
            interaction_feedback={"kind": "clarification", "message": "Please clarify the report format."},
        )
    )
    assert result["route"] == "cancel"
    assert result["terminal_status"] == LifecycleStatus.CANCELLED.value
    assert result["terminal_reason"] == TerminalReason.USER_CANCELLED.value
    assert result["phase_status"] == PhaseStatus.TERMINAL.value
    assert result["pending_profile"] is None
    assert result["proposed_profile"] is None
    assert result["proposal_version"] == 0
    assert result["interaction_feedback"] is None
    assert store.writes == []


async def test_response_mismatch_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(hitl1_node, "interrupt", lambda _value: _accepted("wrong", _complete_response()))
    proposal = await hitl1_node.build_real(_deps(_Caps(_result(_brief_json()))))(_state())
    with pytest.raises(ValueError, match="response_mismatch"):
        await hitl1_node.build_real(_deps(_Caps()))(
            _state(proposed_profile=proposal["proposed_profile"], execution_trace=("hitl1",))
        )


async def test_incomplete_response_checkpoints_followup_and_next_visit_asks_missing_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        hitl1_node,
        "interrupt",
        lambda value: _accepted(value["request"]["request_id"], '{"depth":"quick_overview","audience":"layperson"}'),
    )
    first = await hitl1_node.build_real(_deps(_Caps()))(
        _state(pending_profile=_partial_profile(), execution_trace=("hitl1",))
    )
    assert first["route"] == "needs_followup"
    assert first["profile_followup_round"] == 1
    assert first["pending_profile"]["depth"] == "quick_overview"
    assert first["consumed_message_ids"] == ("human-1",)

    seen: list[dict[str, Any]] = []

    def followup_interrupt(value: dict[str, Any]) -> None:
        seen.append(value)
        raise RuntimeError("interrupt")

    monkeypatch.setattr(hitl1_node, "interrupt", followup_interrupt)
    followup_state = _state(
        pending_profile=first["pending_profile"],
        profile_followup_round=first["profile_followup_round"],
        consumed_request_ids=first["consumed_request_ids"],
        consumed_message_ids=first["consumed_message_ids"],
        execution_trace=("hitl1",),
    )
    with pytest.raises(RuntimeError, match="interrupt"):
        await hitl1_node.build_real(_deps(_Caps()))(followup_state)
    context = json.loads(seen[0]["request"]["context"])
    assert context["missing_dimensions"] == ["format", "cost_tolerance", "time_budget", "must_answer"]
    assert seen[0]["suspension_cursor"] == "human-1"


async def test_followup_response_merges_checkpointed_progress(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _RequestStore()

    def fake_interrupt(value: dict[str, Any]) -> dict[str, Any]:
        return _accepted(
            value["request"]["request_id"],
            '{"format":"faq","cost_tolerance":"minimal","time_budget":"very_quick","must_answer":["Q2"]}',
            "human-2",
        )

    monkeypatch.setattr(hitl1_node, "interrupt", fake_interrupt)
    result = await hitl1_node.build_real(_deps(_Caps(), store))(
        _state(
            pending_profile=_partial_profile(depth="quick_overview", audience="layperson"),
            profile_followup_round=1,
            execution_trace=("hitl1",),
        )
    )
    assert result["route"] == "accepted"
    assert result["research_depth"] == "quick_overview"
    assert result["target_audience"] == "layperson"
    assert result["output_format"] == "faq"
    assert result["consumed_message_ids"] == ("human-2",)
    assert store.writes[0].audience == "layperson"


async def test_unrecognized_answer_is_rejected_without_degrading_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _RequestStore()
    monkeypatch.setattr(
        hitl1_node,
        "interrupt",
        lambda value: _accepted(value["request"]["request_id"], '{"depth":"superficial"}', "human-3"),
    )
    result = await hitl1_node.build_real(_deps(_Caps(), store))(
        _state(
            pending_profile=_partial_profile(depth="standard"),
            profile_followup_round=2,
            execution_trace=("hitl1", "hitl1"),
        )
    )
    assert result["route"] == "needs_followup"
    assert result["profile_followup_round"] == 2
    assert result["profile_rejection_round"] == 1
    assert result["profile_feedback_cursor_message_id"] == "human-3"
    assert result["consumed_message_ids"] == ("human-3",)
    assert store.writes == []


async def test_checkpointed_brief_proposal_is_adopted_only_by_explicit_action(monkeypatch: pytest.MonkeyPatch) -> None:
    caps = _Caps(_result(_brief_json()))
    store = _RequestStore()
    calls: list[dict[str, Any]] = []

    def first_interrupt(value: dict[str, Any]) -> dict[str, Any]:
        calls.append(value)
        raise RuntimeError("persist proposal")

    monkeypatch.setattr(hitl1_node, "interrupt", first_interrupt)
    initial = await hitl1_node.build_real(_deps(caps, store))(_state())
    monkeypatch.setattr(
        hitl1_node,
        "interrupt",
        lambda value: AcceptedHumanResponse(
            request_id=value["request"]["request_id"],
            message_id="human-accept",
            value="accept_suggestion",
            response_kind=ResponseKind.ACTION,
            action_id="accept_suggestion",
        ).model_dump(mode="json"),
    )
    result = await hitl1_node.build_real(_deps(caps, store))(
        _state(proposed_profile=initial["proposed_profile"], execution_trace=("hitl1",))
    )
    assert calls == []
    assert result["route"] == "accepted"
    assert result["research_depth"] == "standard"
    assert result["proposed_profile"] is None
    assert caps.requests and len(caps.requests) == 1


async def test_brief_failure_exhausts_without_interrupt_or_profile_write(monkeypatch: pytest.MonkeyPatch) -> None:
    """@impl NAC-005
    @impl EVH-013

    A failed repair can neither publish a profile nor acquire lifecycle authority.
    """
    caps = _Caps(_result("not-json"), _result('{"still":"invalid"}'))
    store = _RequestStore()
    monkeypatch.setattr(hitl1_node, "interrupt", lambda _value: (_ for _ in ()).throw(AssertionError("no interrupt")))
    result = await hitl1_node.build_real(_deps(caps, store))(_state())
    assert result["route"] == "exhausted"
    assert result["terminal_status"] == LifecycleStatus.BLOCKED.value
    assert result["terminal_reason"] == TerminalReason.GATE_BLOCKED.value
    assert store.writes == []
    assert [request.capability_ref.capability_id for request in caps.requests] == [
        "hitl1-profile-brief",
        "hitl1-profile-brief-repair",
    ]
    assert all(request.tools_enabled is False for request in caps.requests)


async def test_run_agent_failure_exhausts_without_partial_state(monkeypatch: pytest.MonkeyPatch) -> None:
    for failure in (
        RuntimeError("model unavailable"),
        _result("", finish_reason=NodeFinishReason.FAILED),
    ):
        caps = _Caps(failure)
        monkeypatch.setattr(
            hitl1_node,
            "interrupt",
            lambda _value: (_ for _ in ()).throw(AssertionError("no interrupt")),
        )
        result = await hitl1_node.build_real(_deps(caps))(_state())
        assert result["route"] == "exhausted"
        assert result["pending_profile"] is None
        assert result["proposed_profile"] is None
        assert result["profile_rejection_round"] == 0
        assert "profile_ref" not in result


async def test_typed_bridge_problem_survives_hitl1_blocked_route_without_raw_detail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl HIN-006
    @impl WFO-001

    The route remains bounded, while later lifecycle projection retains its cause.
    """
    sentinel = "model provider body secret=sentinel /Users/alice/private"
    problem = NodeProblem(
        code=RunFailureCode.CONFIGURATION_MODEL_MISSING,
        phase="hitl1",
        certainty=FailureCertainty.DIRECT,
    )
    result = NodeExecutionResult(
        finish_reason=NodeFinishReason.FAILED,
        error_code="model_not_configured",
        summary=sentinel,
        problem=problem,
    )
    monkeypatch.setattr(
        hitl1_node,
        "interrupt",
        lambda _value: (_ for _ in ()).throw(AssertionError("no interrupt")),
    )

    update = await hitl1_node.build_real(_deps(_Caps(result)))(_state())

    assert update["route"] == "exhausted"
    assert update["latest_incident"] == {
        "schema_version": 1,
        "code": "configuration.model_missing",
        "phase": "hitl1",
        "certainty": "direct",
    }
    assert sentinel not in str(update)


def _provider_problem(
    code: RunFailureCode,
    *,
    status: int | None = None,
    label: str | None = None,
    authority: str | None = None,
    timeout_origin: str | None = None,
) -> NodeProblem:
    return NodeProblem(
        code=code,
        phase="hitl1",
        certainty=FailureCertainty.DIRECT,
        provider_observation=ProviderObservation(
            configured_service_label=label,
            configured_endpoint_authority=authority,
            response_kind="http_response" if status is not None else "no_response",
            http_status=status,
            timeout_origin=timeout_origin,  # type: ignore[arg-type]
        ),
    )


async def test_semantic_transient_exhaustion_stops_at_three_calls_and_keeps_proposal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timeout = _provider_problem(RunFailureCode.PROVIDER_TIMEOUT)
    caps = _Caps(
        _result("", finish_reason=NodeFinishReason.FAILED, problem=timeout),
        _result("", finish_reason=NodeFinishReason.FAILED, problem=timeout),
        _result("", finish_reason=NodeFinishReason.FAILED, problem=timeout),
    )
    sleeps: list[float] = []

    async def fake_sleep(delay: float) -> None:
        sleeps.append(delay)

    monkeypatch.setattr(hitl1_node.asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(
        hitl1_node,
        "interrupt",
        lambda value: _accepted(value["request"]["request_id"], "我还想考虑", "human-timeout"),
    )

    update = await hitl1_node.build_real(_deps(caps))(
        _state(proposed_profile=_current_proposal(), proposal_version=1, execution_trace=("hitl1",))
    )

    assert update["route"] == "needs_followup"
    assert update["proposed_profile"] == _current_proposal()
    assert update["proposal_version"] == 1
    assert update["interaction_feedback"]["kind"] == "semantic_unavailable"
    assert update["profile_rejection_round"] == 0
    assert len(caps.requests) == 3
    assert sleeps == [1.0, 1.0]
    assert all(request.tools_enabled is False for request in caps.requests)


async def test_semantic_cancellation_propagates_without_checkpoint_feedback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    caps = _Caps(_result("", finish_reason=NodeFinishReason.CANCELLED))
    monkeypatch.setattr(
        hitl1_node,
        "interrupt",
        lambda value: _accepted(value["request"]["request_id"], "我还想考虑", "human-cancelled-model"),
    )

    with pytest.raises(asyncio.CancelledError):
        await hitl1_node.build_real(_deps(caps))(
            _state(proposed_profile=_current_proposal(), proposal_version=1, execution_trace=("hitl1",))
        )


class _RecoveryRecorder:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def record(self, **kwargs: object) -> None:
        self.calls.append(kwargs)


async def test_initial_timeout_retries_once_after_one_second_and_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    timeout = _provider_problem(RunFailureCode.PROVIDER_TIMEOUT)
    caps = _Caps(
        _result("", finish_reason=NodeFinishReason.FAILED, problem=timeout),
        _result(_brief_json()),
    )
    recorder = _RecoveryRecorder()
    sleeps: list[float] = []

    async def fake_sleep(delay: float) -> None:
        sleeps.append(delay)

    monkeypatch.setattr(hitl1_node.asyncio, "sleep", fake_sleep)
    update = await hitl1_node.build_real(_deps(caps, recorder=recorder))(_state())

    assert update["route"] == "needs_followup"
    assert len(caps.requests) == 2
    assert caps.requests[0] == caps.requests[1]
    assert all(request.tools_enabled is False for request in caps.requests)
    assert sleeps == [1.0]
    assert [call["category"] for call in recorder.calls] == [
        RunEventCategory.ATTEMPT,
        RunEventCategory.RETRY,
        RunEventCategory.ATTEMPT,
    ]
    scheduled = recorder.calls[1]
    assert scheduled["retry_ordinal"] == 1
    assert scheduled["backoff_milliseconds"] == 1_000
    assert scheduled["recovery_event_disposition"] == "scheduled"
    assert len({call["attempt_id"] for call in (recorder.calls[0], recorder.calls[2])}) == 2


async def test_two_transient_failures_are_exhausted_with_one_terminal_reference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = _provider_problem(RunFailureCode.PROVIDER_TIMEOUT, label="deepseek-v4-pro")
    second = _provider_problem(RunFailureCode.PROVIDER_UNAVAILABLE, status=503, label="deepseek-v4-pro")
    caps = _Caps(
        _result("", finish_reason=NodeFinishReason.FAILED, problem=first),
        _result("", finish_reason=NodeFinishReason.FAILED, problem=second),
    )
    recorder = _RecoveryRecorder()

    async def fake_sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr(hitl1_node.asyncio, "sleep", fake_sleep)
    update = await hitl1_node.build_real(_deps(caps, recorder=recorder))(_state())

    incident = update["latest_incident"]
    assert update["route"] == "exhausted"
    assert incident["code"] == "provider.unavailable"
    assert incident["diagnostic_ref"].startswith("diag_")
    assert incident["provider_recovery"] == {
        "trigger_category": "provider.timeout",
        "trigger_observation": {
            "configured_service_label": "deepseek-v4-pro",
            "response_kind": "no_response",
        },
        "trigger_invocation_ordinal": 1,
        "model_attempts": 2,
        "automatic_retries": 1,
        "disposition": "exhausted",
    }
    assert incident["provider_observation"]["http_status"] == 503
    assert [call["category"] for call in recorder.calls] == [
        RunEventCategory.ATTEMPT,
        RunEventCategory.RETRY,
        RunEventCategory.ATTEMPT,
        RunEventCategory.EXHAUSTION,
    ]


async def test_retry_timeout_origins_remain_in_their_trigger_and_final_roles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = _provider_problem(
        RunFailureCode.PROVIDER_TIMEOUT,
        timeout_origin="bridge_wall_time_budget",
    )
    second = _provider_problem(
        RunFailureCode.PROVIDER_TIMEOUT,
        timeout_origin="provider_sdk_timeout",
    )
    caps = _Caps(
        _result("", finish_reason=NodeFinishReason.FAILED, problem=first),
        _result("", finish_reason=NodeFinishReason.FAILED, problem=second),
    )
    captured: dict[str, object] = {}

    def derive_reference(**kwargs: object) -> str:
        captured.update(kwargs)
        return "diag_" + "T" * 24

    async def fake_sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr(hitl1_node, "derive_provider_diagnostic_reference", derive_reference)
    monkeypatch.setattr(hitl1_node.asyncio, "sleep", fake_sleep)
    update = await hitl1_node.build_real(_deps(caps))(_state())

    incident = update["latest_incident"]
    assert incident["diagnostic_ref"] == "diag_" + "T" * 24
    assert incident["provider_recovery"]["trigger_observation"]["timeout_origin"] == "bridge_wall_time_budget"
    assert incident["provider_observation"]["timeout_origin"] == "provider_sdk_timeout"
    problem = captured["problem"]
    recovery = captured["recovery"]
    assert isinstance(problem, NodeProblem)
    assert problem.provider_observation is not None
    assert problem.provider_observation.timeout_origin == "provider_sdk_timeout"
    assert isinstance(recovery, ProviderRecoveryProjection)
    assert recovery.trigger_observation.timeout_origin == "bridge_wall_time_budget"


async def test_retry_trigger_timeout_origin_does_not_invent_a_final_origin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = _provider_problem(
        RunFailureCode.PROVIDER_TIMEOUT,
        timeout_origin="bridge_wall_time_budget",
    )
    second = _provider_problem(RunFailureCode.PROVIDER_AUTHENTICATION_FAILED, status=401)
    caps = _Caps(
        _result("", finish_reason=NodeFinishReason.FAILED, problem=first),
        _result("", finish_reason=NodeFinishReason.FAILED, problem=second),
    )

    async def fake_sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr(hitl1_node.asyncio, "sleep", fake_sleep)
    update = await hitl1_node.build_real(_deps(caps))(_state())

    incident = update["latest_incident"]
    assert incident["provider_recovery"]["trigger_observation"]["timeout_origin"] == "bridge_wall_time_budget"
    assert "timeout_origin" not in incident["provider_observation"]


async def test_retry_followed_by_authentication_preserves_final_observation(monkeypatch: pytest.MonkeyPatch) -> None:
    first = _provider_problem(RunFailureCode.PROVIDER_TIMEOUT)
    second = _provider_problem(RunFailureCode.PROVIDER_AUTHENTICATION_FAILED, status=401)
    caps = _Caps(
        _result("", finish_reason=NodeFinishReason.FAILED, problem=first),
        _result("", finish_reason=NodeFinishReason.FAILED, problem=second),
    )

    async def fake_sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr(hitl1_node.asyncio, "sleep", fake_sleep)
    update = await hitl1_node.build_real(_deps(caps))(_state())

    incident = update["latest_incident"]
    assert incident["code"] == "provider.authentication_failed"
    assert incident["provider_recovery"]["disposition"] == "retry_followed_by_terminal_failure"
    assert incident["provider_observation"]["http_status"] == 401


async def test_retry_followed_by_malformed_output_never_issues_third_call(monkeypatch: pytest.MonkeyPatch) -> None:
    first = _provider_problem(RunFailureCode.PROVIDER_TIMEOUT)
    caps = _Caps(
        _result("", finish_reason=NodeFinishReason.FAILED, problem=first),
        _result('{"missing": true}'),
    )

    async def fake_sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr(hitl1_node.asyncio, "sleep", fake_sleep)
    update = await hitl1_node.build_real(_deps(caps))(_state())

    assert len(caps.requests) == 2
    assert update["latest_incident"]["code"] == "output.structured_invalid"
    assert update["latest_incident"]["provider_recovery"]["disposition"] == "retry_followed_by_terminal_failure"


async def test_repair_slot_transient_has_no_third_call_and_offers_distinct_new_start() -> None:
    unavailable = _provider_problem(RunFailureCode.PROVIDER_UNAVAILABLE, status=503)
    caps = _Caps(
        _result('{"missing": true}'),
        _result("", finish_reason=NodeFinishReason.FAILED, problem=unavailable),
    )
    update = await hitl1_node.build_real(_deps(caps))(_state())

    assert len(caps.requests) == 2
    assert all(request.tools_enabled is False for request in caps.requests)
    recovery = update["latest_incident"]["provider_recovery"]
    assert recovery["trigger_invocation_ordinal"] == 2
    assert recovery["automatic_retries"] == 0
    assert recovery["disposition"] == "retry_not_started_budget_consumed"


async def test_non_retryable_http_observation_is_terminal_feedback_without_recovery() -> None:
    bad_request = _provider_problem(RunFailureCode.INTERNAL_UNEXPECTED, status=400)
    caps = _Caps(_result("", finish_reason=NodeFinishReason.FAILED, problem=bad_request))
    update = await hitl1_node.build_real(_deps(caps))(_state())

    assert len(caps.requests) == 1
    incident = update["latest_incident"]
    assert "provider_recovery" not in incident
    assert incident["provider_observation"]["http_status"] == 400
    assert incident["diagnostic_ref"].startswith("diag_")


async def test_unproven_provider_code_is_not_retried_or_projected() -> None:
    unproven = NodeProblem(
        code=RunFailureCode.PROVIDER_TIMEOUT,
        phase="hitl1",
        certainty=FailureCertainty.DIRECT,
    )
    caps = _Caps(_result("", finish_reason=NodeFinishReason.FAILED, problem=unproven))
    update = await hitl1_node.build_real(_deps(caps))(_state())

    assert len(caps.requests) == 1
    assert update["latest_incident"] == {
        "schema_version": 1,
        "code": "provider.timeout",
        "phase": "hitl1",
        "certainty": "direct",
    }


async def test_cancellation_during_provider_backoff_does_not_create_second_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timeout = _provider_problem(RunFailureCode.PROVIDER_TIMEOUT)
    caps = _Caps(_result("", finish_reason=NodeFinishReason.FAILED, problem=timeout))
    entered_backoff = asyncio.Event()

    async def blocking_sleep(_delay: float) -> None:
        entered_backoff.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(hitl1_node.asyncio, "sleep", blocking_sleep)
    task = asyncio.create_task(hitl1_node.build_real(_deps(caps))(_state()))
    await asyncio.wait_for(entered_backoff.wait(), timeout=1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert len(caps.requests) == 1


async def test_cancellation_during_automatic_retry_propagates_without_terminal_incident(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timeout = _provider_problem(RunFailureCode.PROVIDER_TIMEOUT)
    retry_started = asyncio.Event()

    class _BlockingRetryCaps:
        def __init__(self) -> None:
            self.requests: list[object] = []

        async def run_agent(self, *, context: NodeAgentContext, request: object) -> NodeExecutionResult:  # noqa: ARG002
            self.requests.append(request)
            if len(self.requests) == 1:
                return _result("", finish_reason=NodeFinishReason.FAILED, problem=timeout)
            retry_started.set()
            await asyncio.Event().wait()
            raise AssertionError("unreachable")

    async def fake_sleep(_delay: float) -> None:
        return None

    caps = _BlockingRetryCaps()
    monkeypatch.setattr(hitl1_node.asyncio, "sleep", fake_sleep)
    task = asyncio.create_task(hitl1_node.build_real(_deps(caps))(_state()))
    await asyncio.wait_for(retry_started.wait(), timeout=1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert len(caps.requests) == 2
