"""Real-model live subject for the public controller direction-loop case.

These runs measure intent mapping and proposal selection, not lifecycle
execution: the subject drives each declared scenario's user turn through the
real lead-agent composition (committed controller skill, dedicated Agent
SOUL, ``file:read`` route, public ``deep_research`` schema) with a real model,
and records what the model itself proposed. The lifecycle layer is a bounded
recording fake that answers only with the declared typed results for the
scenario's ``subject_state``; lifecycle execution semantics stay owned by the
scripted handoff tests. Each scenario also gets a minimal state-establishment
conversation prefix carrying only neutral state facts (bundle id, status,
what is pending) — never a directive — so the model has the same visibility
an operator would have.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from deerflow_deep_research.domain.evaluation import SubjectExecution
from deerflow_deep_research.domain.identifiers import LogicalPhase
from deerflow_deep_research.domain.lifecycle import (
    BundleAvailability,
    BundleControlResult,
    BundleRefinementDisposition,
    BundleRefinementProjection,
    Durability,
    LegalNextAction,
    LifecycleAction,
    LifecycleStatus,
    PendingInputProjection,
    ResultCode,
    TerminalReason,
)
from deerflow_deep_research.runtime.bundle_control import BundleControl

from .runner import ExecutionContext, Subject

SKILL_CONTAINER_PATH = "/mnt/skills/public/deep-research-controller/SKILL.md"


def _rid(stem: str) -> str:
    """A deterministic in-pattern bundle id (``^b_[A-Za-z0-9_-]{43}$``)."""

    return "b_" + (stem * 43)[:43]


_IDS = {
    "fresh": _rid("n"),
    "correlated": _rid("c"),
    "active": _rid("a"),
    "queued": _rid("q"),
    "terminal": _rid("t"),
    "exhausted": _rid("e"),
    "profiled": _rid("p"),
    "conflict": _rid("k"),
    "precommit": _rid("r"),
    "ended": _rid("d"),
    "unavailable": _rid("u"),
}


def _refinement(
    disposition: BundleRefinementDisposition = BundleRefinementDisposition.NONE,
) -> BundleRefinementProjection:
    return (
        BundleRefinementProjection(disposition=disposition)
        if disposition
        in {
            BundleRefinementDisposition.NONE,
            BundleRefinementDisposition.PENDING,
        }
        else BundleRefinementProjection(disposition=disposition, current_round=1)
    )


def _pending_input() -> PendingInputProjection:
    return PendingInputProjection(request_id="req_" + "p" * 8, pending_phase="hitl1", generation=0, mode="text")


_PENDING_REQUEST_ID = "req_" + "p" * 8


def _dump(result: BundleControlResult) -> dict[str, Any]:
    return result.model_dump(mode="json", exclude_none=True)


def _suspended_result(
    action: LifecycleAction,
    *,
    code: ResultCode,
    bundle_id: str,
    legal: LegalNextAction,
    disposition: BundleRefinementDisposition = BundleRefinementDisposition.NONE,
) -> dict[str, Any]:
    return _dump(
        BundleControlResult(
            action=action,
            code=code,
            availability=BundleAvailability.AVAILABLE,
            durability=Durability.RESTART_DURABLE,
            bundle_id=bundle_id,
            status=LifecycleStatus.SUSPENDED,
            phase=LogicalPhase.HITL1,
            generation=0,
            request_id=_PENDING_REQUEST_ID,
            pending_input=_pending_input(),
            refinement=_refinement(disposition),
            legal_next_action=legal,
        )
    )


def _active_result(
    action: LifecycleAction,
    *,
    code: ResultCode,
    bundle_id: str,
    legal: LegalNextAction,
    disposition: BundleRefinementDisposition = BundleRefinementDisposition.NONE,
) -> dict[str, Any]:
    return _dump(
        BundleControlResult(
            action=action,
            code=code,
            availability=BundleAvailability.AVAILABLE,
            durability=Durability.RESTART_DURABLE,
            bundle_id=bundle_id,
            status=LifecycleStatus.ACTIVE,
            phase=LogicalPhase.WAVE0,
            generation=0,
            refinement=_refinement(disposition),
            legal_next_action=legal,
        )
    )


def _terminal_result(
    action: LifecycleAction,
    *,
    code: ResultCode,
    bundle_id: str,
    legal: LegalNextAction,
    reason: TerminalReason = TerminalReason.COMPLETED,
    disposition: BundleRefinementDisposition = BundleRefinementDisposition.NONE,
) -> dict[str, Any]:
    return _dump(
        BundleControlResult(
            action=action,
            code=code,
            availability=BundleAvailability.AVAILABLE,
            durability=Durability.RESTART_DURABLE,
            bundle_id=bundle_id,
            status=LifecycleStatus.COMPLETED,
            phase=LogicalPhase.FINAL_DELIVERY,
            generation=0,
            terminal_reason=reason,
            refinement=_refinement(disposition),
            legal_next_action=legal,
        )
    )


def _rerun_result(
    action: LifecycleAction,
    *,
    code: ResultCode,
    bundle_id: str,
    legal: LegalNextAction,
) -> dict[str, Any]:
    """An applied refinement that restarted the run as a fresh generation."""

    return _dump(
        BundleControlResult(
            action=action,
            code=code,
            availability=BundleAvailability.AVAILABLE,
            durability=Durability.RESTART_DURABLE,
            bundle_id=bundle_id,
            status=LifecycleStatus.ACTIVE,
            phase=LogicalPhase.RERUN,
            generation=1,
            refinement=BundleRefinementProjection(disposition=BundleRefinementDisposition.APPLIED, current_round=1),
            legal_next_action=legal,
        )
    )


def _cancelled_result(action: LifecycleAction, bundle_id: str) -> dict[str, Any]:
    return _dump(
        BundleControlResult(
            action=action,
            code=ResultCode.CANCELLED,
            availability=BundleAvailability.AVAILABLE,
            durability=Durability.RESTART_DURABLE,
            bundle_id=bundle_id,
            status=LifecycleStatus.CANCELLED,
            phase=LogicalPhase.FINAL_DELIVERY,
            generation=0,
            terminal_reason=TerminalReason.USER_STOPPED,
            refinement=_refinement(),
            legal_next_action=LegalNextAction.START,
        )
    )


def _unavailable_result(action: LifecycleAction) -> dict[str, Any]:
    return _dump(
        BundleControlResult(
            action=action,
            code=ResultCode.RESEARCH_NOT_FOUND,
            availability=BundleAvailability.UNAVAILABLE,
            durability=Durability.UNAVAILABLE,
            legal_next_action=LegalNextAction.START,
        )
    )


def _suspended_start() -> dict[str, Any]:
    return _suspended_result(
        LifecycleAction.START, code=ResultCode.SUSPENDED, bundle_id=_IDS["fresh"], legal=LegalNextAction.RESUME
    )


# Declared typed results per subject_state. Only these answers exist; any
# other action on the state gets the honest not-found projection. Every entry
# mirrors the case's own scenario declarations (expected_action/result).
_DECLARED_RESULTS: dict[str, dict[str, dict[str, Any]]] = {
    "no_active_bundle": {
        "start": _suspended_start(),
    },
    "suspended_with_correlated_subject": {
        "start": _suspended_result(
            LifecycleAction.START,
            code=ResultCode.ACTIVE_BUNDLE_EXISTS,
            bundle_id=_IDS["correlated"],
            legal=LegalNextAction.RESUME,
        ),
        "status": _suspended_result(
            LifecycleAction.STATUS,
            code=ResultCode.STATUS_OK,
            bundle_id=_IDS["correlated"],
            legal=LegalNextAction.RESUME,
        ),
        "resume": _terminal_result(
            LifecycleAction.RESUME,
            code=ResultCode.COMPLETED,
            bundle_id=_IDS["correlated"],
            legal=LegalNextAction.REFINE,
        ),
        "refine": _suspended_result(
            LifecycleAction.REFINE,
            code=ResultCode.REFINEMENT_PENDING,
            bundle_id=_IDS["correlated"],
            legal=LegalNextAction.RESUME,
            disposition=BundleRefinementDisposition.PENDING,
        ),
        "cancel": _cancelled_result(LifecycleAction.CANCEL, _IDS["correlated"]),
    },
    "active_or_suspended_bundle": {
        "start": _active_result(
            LifecycleAction.START,
            code=ResultCode.ACTIVE_BUNDLE_EXISTS,
            bundle_id=_IDS["active"],
            legal=LegalNextAction.CANCEL,
        ),
        "status": _active_result(
            LifecycleAction.STATUS, code=ResultCode.STATUS_OK, bundle_id=_IDS["active"], legal=LegalNextAction.CANCEL
        ),
        "refine": _active_result(
            LifecycleAction.REFINE,
            code=ResultCode.REFINEMENT_PENDING,
            bundle_id=_IDS["active"],
            legal=LegalNextAction.STATUS,
            disposition=BundleRefinementDisposition.PENDING,
        ),
        "cancel": _cancelled_result(LifecycleAction.CANCEL, _IDS["active"]),
    },
    "active_bundle": {
        "start": _active_result(
            LifecycleAction.START,
            code=ResultCode.ACTIVE_BUNDLE_EXISTS,
            bundle_id=_IDS["active"],
            legal=LegalNextAction.CANCEL,
        ),
        "status": _active_result(
            LifecycleAction.STATUS, code=ResultCode.STATUS_OK, bundle_id=_IDS["active"], legal=LegalNextAction.CANCEL
        ),
        "refine": _active_result(
            LifecycleAction.REFINE,
            code=ResultCode.REFINEMENT_PENDING,
            bundle_id=_IDS["active"],
            legal=LegalNextAction.STATUS,
            disposition=BundleRefinementDisposition.PENDING,
        ),
        "cancel": _cancelled_result(LifecycleAction.CANCEL, _IDS["active"]),
    },
    "active_bundle_with_pending_direction": {
        "start": _active_result(
            LifecycleAction.START,
            code=ResultCode.ACTIVE_BUNDLE_EXISTS,
            bundle_id=_IDS["conflict"],
            legal=LegalNextAction.CANCEL,
        ),
        "status": _active_result(
            LifecycleAction.STATUS,
            code=ResultCode.STATUS_OK,
            bundle_id=_IDS["conflict"],
            legal=LegalNextAction.CANCEL,
            disposition=BundleRefinementDisposition.PENDING,
        ),
        "resume": _terminal_result(
            LifecycleAction.RESUME, code=ResultCode.COMPLETED, bundle_id=_IDS["conflict"], legal=LegalNextAction.REFINE
        ),
        "refine": _active_result(
            LifecycleAction.REFINE,
            code=ResultCode.REFINEMENT_CONFLICT,
            bundle_id=_IDS["conflict"],
            legal=LegalNextAction.STATUS,
            disposition=BundleRefinementDisposition.PENDING,
        ),
        "cancel": _cancelled_result(LifecycleAction.CANCEL, _IDS["conflict"]),
    },
    "suspended_with_queued_direction": {
        "start": _suspended_result(
            LifecycleAction.START,
            code=ResultCode.ACTIVE_BUNDLE_EXISTS,
            bundle_id=_IDS["queued"],
            legal=LegalNextAction.CANCEL,
            disposition=BundleRefinementDisposition.PENDING,
        ),
        "status": _suspended_result(
            LifecycleAction.STATUS,
            code=ResultCode.STATUS_OK,
            bundle_id=_IDS["queued"],
            legal=LegalNextAction.CANCEL,
            disposition=BundleRefinementDisposition.PENDING,
        ),
        "resume": _terminal_result(
            LifecycleAction.RESUME, code=ResultCode.COMPLETED, bundle_id=_IDS["queued"], legal=LegalNextAction.REFINE
        ),
        "refine": _suspended_result(
            LifecycleAction.REFINE,
            code=ResultCode.REFINEMENT_PENDING,
            bundle_id=_IDS["queued"],
            legal=LegalNextAction.CANCEL,
            disposition=BundleRefinementDisposition.PENDING,
        ),
        "cancel": _cancelled_result(LifecycleAction.CANCEL, _IDS["queued"]),
    },
    "terminal_with_queued_direction": {
        "start": _suspended_start(),
        "status": _terminal_result(
            LifecycleAction.STATUS,
            code=ResultCode.STATUS_OK,
            bundle_id=_IDS["terminal"],
            legal=LegalNextAction.REFINE,
            disposition=BundleRefinementDisposition.PENDING,
        ),
        "refine": _rerun_result(
            LifecycleAction.REFINE,
            code=ResultCode.REFINEMENT_APPLIED,
            bundle_id=_IDS["terminal"],
            legal=LegalNextAction.STATUS,
        ),
    },
    "terminal_available_bundle": {
        "start": _suspended_start(),
        "status": _terminal_result(
            LifecycleAction.STATUS, code=ResultCode.STATUS_OK, bundle_id=_IDS["ended"], legal=LegalNextAction.REFINE
        ),
        "refine": _rerun_result(
            LifecycleAction.REFINE,
            code=ResultCode.REFINEMENT_APPLIED,
            bundle_id=_IDS["ended"],
            legal=LegalNextAction.STATUS,
        ),
    },
    "terminal_exhausted_without_queued_direction": {
        "start": _suspended_start(),
        "status": _terminal_result(
            LifecycleAction.STATUS,
            code=ResultCode.STATUS_OK,
            bundle_id=_IDS["exhausted"],
            legal=LegalNextAction.START,
            reason=TerminalReason.RERUN_EXHAUSTED,
        ),
        "refine": _terminal_result(
            LifecycleAction.REFINE,
            code=ResultCode.REFINEMENT_CONFLICT,
            bundle_id=_IDS["exhausted"],
            legal=LegalNextAction.START,
            reason=TerminalReason.RERUN_EXHAUSTED,
            disposition=BundleRefinementDisposition.PENDING,
        ),
    },
    "terminal_exhausted_with_queued_direction": {
        "start": _suspended_start(),
        "status": _terminal_result(
            LifecycleAction.STATUS,
            code=ResultCode.STATUS_OK,
            bundle_id=_IDS["exhausted"],
            legal=LegalNextAction.START,
            reason=TerminalReason.RERUN_EXHAUSTED,
            disposition=BundleRefinementDisposition.PENDING,
        ),
        "refine": _terminal_result(
            LifecycleAction.REFINE,
            code=ResultCode.REFINEMENT_CONFLICT,
            bundle_id=_IDS["exhausted"],
            legal=LegalNextAction.START,
            reason=TerminalReason.RERUN_EXHAUSTED,
            disposition=BundleRefinementDisposition.PENDING,
        ),
    },
    "confirmed_profile_active_bundle": {
        "start": _active_result(
            LifecycleAction.START,
            code=ResultCode.ACTIVE_BUNDLE_EXISTS,
            bundle_id=_IDS["profiled"],
            legal=LegalNextAction.CANCEL,
        ),
        "status": _active_result(
            LifecycleAction.STATUS, code=ResultCode.STATUS_OK, bundle_id=_IDS["profiled"], legal=LegalNextAction.CANCEL
        ),
        "refine": _active_result(
            LifecycleAction.REFINE,
            code=ResultCode.REFINEMENT_PENDING,
            bundle_id=_IDS["profiled"],
            legal=LegalNextAction.STATUS,
            disposition=BundleRefinementDisposition.PENDING,
        ),
        "cancel": _cancelled_result(LifecycleAction.CANCEL, _IDS["profiled"]),
    },
    "confirmed_profile_active_bundle_after_clarification": {
        "start": _active_result(
            LifecycleAction.START,
            code=ResultCode.ACTIVE_BUNDLE_EXISTS,
            bundle_id=_IDS["profiled"],
            legal=LegalNextAction.CANCEL,
        ),
        "status": _active_result(
            LifecycleAction.STATUS, code=ResultCode.STATUS_OK, bundle_id=_IDS["profiled"], legal=LegalNextAction.CANCEL
        ),
        "refine": _active_result(
            LifecycleAction.REFINE,
            code=ResultCode.REFINEMENT_PENDING,
            bundle_id=_IDS["profiled"],
            legal=LegalNextAction.STATUS,
            disposition=BundleRefinementDisposition.PENDING,
        ),
        "cancel": _cancelled_result(LifecycleAction.CANCEL, _IDS["profiled"]),
    },
    "terminal_precommit_recovery_with_first_round_applied": {
        "start": _suspended_start(),
        "status": _dump(
            BundleControlResult(
                action=LifecycleAction.STATUS,
                code=ResultCode.STATUS_OK,
                availability=BundleAvailability.AVAILABLE,
                durability=Durability.RESTART_DURABLE,
                bundle_id=_IDS["precommit"],
                status=LifecycleStatus.COMPLETED,
                phase=LogicalPhase.FINAL_DELIVERY,
                generation=1,
                terminal_reason=TerminalReason.COMPLETED,
                refinement=BundleRefinementProjection(disposition=BundleRefinementDisposition.APPLIED, current_round=1),
                legal_next_action=LegalNextAction.REFINE,
            )
        ),
        "refine": _dump(
            BundleControlResult(
                action=LifecycleAction.REFINE,
                code=ResultCode.REFINEMENT_CONFLICT,
                availability=BundleAvailability.AVAILABLE,
                durability=Durability.RESTART_DURABLE,
                bundle_id=_IDS["precommit"],
                status=LifecycleStatus.COMPLETED,
                phase=LogicalPhase.FINAL_DELIVERY,
                generation=1,
                terminal_reason=TerminalReason.COMPLETED,
                refinement=BundleRefinementProjection(
                    disposition=BundleRefinementDisposition.APPLIED_WITH_PENDING, current_round=1
                ),
                legal_next_action=LegalNextAction.START,
            )
        ),
    },
    "unavailable_explicit_target": {
        "start": _suspended_start(),
        "status": _dump(
            BundleControlResult(
                action=LifecycleAction.STATUS,
                code=ResultCode.UNAVAILABLE,
                availability=BundleAvailability.UNAVAILABLE,
                durability=Durability.UNAVAILABLE,
                legal_next_action=LegalNextAction.START,
            )
        ),
        "resume": _unavailable_result(LifecycleAction.RESUME),
        "refine": _unavailable_result(LifecycleAction.REFINE),
        "cancel": _unavailable_result(LifecycleAction.CANCEL),
    },
}

# Neutral state-establishment prefixes: facts only (bundle id, status, what is
# pending) so the model has operator-equivalent visibility, never a directive.
_SUBJECT_TURN = "Investigate primary-source policy evidence for grid-storage safety."


def _prefix(bundle_id: str, fact: str) -> list[BaseMessage]:
    return [
        HumanMessage(content=_SUBJECT_TURN),
        AIMessage(content=f"Deep Research bundle {bundle_id} {fact}"),
    ]


# Neutral state facts per subject_state: id and status only, never a directive.
_STATE_FACTS: dict[str, tuple[str, str]] = {
    "suspended_with_correlated_subject": (
        _IDS["correlated"],
        "is suspended at a human checkpoint on that subject, awaiting your input.",
    ),
    "active_or_suspended_bundle": (_IDS["active"], "is active on that subject."),
    "active_bundle": (_IDS["active"], "is active on that subject."),
    "active_bundle_with_pending_direction": (
        _IDS["conflict"],
        "is active on that subject; a run direction is already pending for it.",
    ),
    "suspended_with_queued_direction": (
        _IDS["queued"],
        "is suspended on that subject, and a run direction you gave earlier is queued for it.",
    ),
    "terminal_with_queued_direction": (
        _IDS["terminal"],
        "completed on that subject; a run direction you gave earlier remains queued on it.",
    ),
    "terminal_available_bundle": (_IDS["ended"], "completed on that subject and remains available."),
    "terminal_exhausted_without_queued_direction": (
        _IDS["exhausted"],
        "exhausted its rerun capacity on that subject; no direction is queued.",
    ),
    "terminal_exhausted_with_queued_direction": (
        _IDS["exhausted"],
        "exhausted its rerun capacity on that subject; a direction you gave earlier "
        "remains inspectable but not applicable.",
    ),
    "confirmed_profile_active_bundle": (
        _IDS["profiled"],
        "is active on that subject with your confirmed profile notes.",
    ),
    "confirmed_profile_active_bundle_after_clarification": (
        _IDS["profiled"],
        "is active on that subject; after your clarification, the profile notes stand confirmed.",
    ),
    "terminal_precommit_recovery_with_first_round_applied": (
        _IDS["precommit"],
        "completed on that subject; a pre-commit recovery already applied its first round.",
    ),
    "unavailable_explicit_target": (
        _IDS["unavailable"],
        "was started on that subject but is no longer available for control.",
    ),
}

_STATE_PREFIX: dict[str, list[BaseMessage]] = {
    "no_active_bundle": [],
    **{state: _prefix(bundle_id, fact) for state, (bundle_id, fact) in _STATE_FACTS.items()},
}


def _control_factory(state: str, calls: list[dict[str, Any]]) -> type[Any]:
    """A BundleControl subclass answering only with this state's declared results.

    Subclassing keeps the real class surface (``action_from_wire``,
    ``unavailable_wire_result``) intact for the tool's dispatch path while
    replacing exactly the lifecycle execution the fake owns.
    """

    declared = _DECLARED_RESULTS.get(state)
    if declared is None:
        raise ValueError(f"controller_live_subject_state_undeclared:{state}")

    class _DeclaredBundleControl(BundleControl):  # type: ignore[misc,valid-type]
        def __init__(self, **kwargs: Any) -> None:
            super().__init__(**kwargs)

        async def dispatch(
            self,
            *,
            action: LifecycleAction,
            bundle_id: str | None = None,
            refinement: str | None = None,
            **_: Any,
        ) -> dict[str, Any]:
            wire = action.value if hasattr(action, "value") else str(action)
            calls.append({"action": wire, "bundle_id": bundle_id, "refinement": refinement})
            answer = declared.get(wire)
            if answer is None:
                return BundleControl.unavailable_wire_result(action=action, code="research_not_found")
            return dict(answer)

    return _DeclaredBundleControl


def _skill_digest_from_home(app_config: Any) -> str:
    """Digest of the skill exactly as the composition's home materialized it."""

    skills_path = None
    skills = getattr(app_config, "skills", None)
    if skills is not None:
        skills_path = getattr(skills, "path", None)
    if not skills_path:
        raise ValueError("controller_live_skills_path_unavailable")
    skill_file = Path(str(skills_path)) / "public" / "deep-research-controller" / "SKILL.md"
    return hashlib.sha256(skill_file.read_bytes()).hexdigest()


def _message_digest(messages: list[BaseMessage]) -> str:
    payload = [
        {"type": message.type, "content": message.content if isinstance(message.content, str) else str(message.content)}
        for message in messages
    ]
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _usage(message: AIMessage) -> tuple[int, int]:
    usage = getattr(message, "usage_metadata", None)
    if not isinstance(usage, Mapping):
        return 0, 0
    return int(usage.get("input_tokens", 0) or 0), int(usage.get("output_tokens", 0) or 0)


def _capture(messages: list[BaseMessage], *, skip: int = 0) -> dict[str, Any]:
    """Read the model's observable proposal from one turn's transcript.

    ``skip`` excludes the seeded state-establishment prefix so only responses
    the model itself produced during this turn are counted.
    """

    skill_read_index: int | None = None
    control_index: int | None = None
    control_calls: list[dict[str, Any]] = []
    other_tool_calls: list[dict[str, Any]] = []
    input_tokens = 0
    output_tokens = 0
    model_calls = 0
    for index, message in enumerate(messages):
        if index < skip or not isinstance(message, AIMessage):
            continue
        model_calls += 1
        turn_in, turn_out = _usage(message)
        input_tokens += turn_in
        output_tokens += turn_out
        for call in message.tool_calls or []:
            name = call.get("name")
            args = call.get("args") or {}
            if name == "read_file" and args.get("path") == SKILL_CONTAINER_PATH and skill_read_index is None:
                skill_read_index = index
            elif name == "deep_research":
                if control_index is None:
                    control_index = index
                control_calls.append(
                    {
                        "action": args.get("action"),
                        "bundle_id": args.get("bundle_id"),
                        "refinement": args.get("refinement"),
                    }
                )
            else:
                other_tool_calls.append({"name": name})
    skill_read_first = skill_read_index is not None and (control_index is None or skill_read_index < control_index)
    proposal: dict[str, Any]
    if control_calls:
        first = control_calls[0]
        proposal = {
            "kind": "action",
            "action": first["action"],
            "bundle_id": first["bundle_id"],
            "refinement": first["refinement"],
            "all_calls": control_calls,
        }
    else:
        final_text = next(
            (
                m.content
                for m in reversed(messages)
                if isinstance(m, AIMessage) and isinstance(m.content, str) and m.content.strip()
            ),
            "",
        )
        proposal = {"kind": "clarification", "text": final_text}
    return {
        "skill_read_first": skill_read_first,
        "skill_read": skill_read_index is not None,
        "proposal": proposal,
        "other_tool_calls": other_tool_calls,
        "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens, "model_calls": model_calls},
    }


async def _drive_turn(
    app_config: Any, messages: list[BaseMessage], *, thread_id: str, recursion_limit: int
) -> dict[str, Any]:
    """One real lead-agent turn through the public factory (no private APIs).

    The assembly reads ``app_config`` from the factory config's context (the
    public path has no explicit app_config parameter), while the trusted
    runtime context reaches ToolNode through the ``context`` invoke argument —
    the same split the composition's own tests exercise.
    """

    from deerflow.agents.lead_agent import make_lead_agent

    factory_config = {
        "configurable": {"agent_name": "deep-research", "user_id": "default"},
        "context": {"thread_id": thread_id, "run_id": thread_id, "user_id": "default", "app_config": app_config},
    }
    invoke_config = {
        "configurable": {"thread_id": thread_id, "run_id": thread_id, "user_id": "default"},
        "recursion_limit": recursion_limit,
    }
    runtime_context = {"thread_id": thread_id, "run_id": thread_id, "user_id": "default", "app_config": app_config}
    agent = make_lead_agent(factory_config)
    return await asyncio.to_thread(agent.invoke, {"messages": messages}, invoke_config, context=runtime_context)


def controller_live_subject(
    *,
    app_config: Any,
    provider: str,
    model: str,
    control_override: Callable[[str, list[dict[str, Any]]], Any],
    price_input_per_mtok: float | None = None,
    price_output_per_mtok: float | None = None,
    recursion_limit: int = 128,
) -> Subject:
    """Build the real-model public-controller subject for the direction-loop case."""

    async def invoke(context: ExecutionContext) -> SubjectExecution:
        from deerflow_deep_research.runtime.runtime_adapter import STARTUP_FINGERPRINT_ENV
        from deerflow_deep_research.runtime.startup_snapshot import capture_startup_fingerprint

        # The adapter verifies this fingerprint against app_config; the subject
        # owns the composition session, so it publishes the matching snapshot.
        os.environ[STARTUP_FINGERPRINT_ENV] = capture_startup_fingerprint(app_config, worker_value=None)

        scenarios = context.fixture.get("scenarios")
        if not isinstance(scenarios, list) or not scenarios:
            raise ValueError("evaluation_scenarios_missing")
        execution_plan = context.fixture.get("execution")
        runtime_controls = execution_plan.get("runtime_controls", []) if isinstance(execution_plan, Mapping) else []
        skill_digest = _skill_digest_from_home(app_config)
        updates: list[dict[str, Any]] = []
        input_tokens = 0
        output_tokens = 0
        model_calls = 0
        tool_calls = 0
        prompt_digests: list[str] = []
        for position, scenario in enumerate(scenarios):
            if not isinstance(scenario, Mapping):
                raise ValueError("evaluation_scenario_invalid")
            scenario_id = scenario.get("scenario_id")
            state = scenario.get("subject_state")
            user_turn = scenario.get("user_turn")
            if not isinstance(scenario_id, str) or not isinstance(state, str) or not isinstance(user_turn, str):
                raise ValueError("evaluation_scenario_invalid")
            context.observe("scenario.invoked", {"subject": "public_controller", "scenario_id": scenario_id})
            prefix = _STATE_PREFIX[state]
            messages = [*prefix, HumanMessage(content=user_turn)]
            prompt_digests.append(_message_digest(messages))
            calls: list[dict[str, Any]] = []
            with control_override(state, calls):
                result = await _drive_turn(
                    app_config,
                    messages,
                    thread_id=f"controller-live-{scenario_id}-{position}",
                    recursion_limit=recursion_limit,
                )
            captured = _capture(list(result.get("messages", [])), skip=len(prefix))
            captured["scenario_id"] = scenario_id
            captured["subject_state"] = state
            captured["expected_action"] = scenario.get("expected_action")
            captured["expects_clarification"] = scenario.get("expects_clarification")
            captured["lifecycle_calls"] = calls
            updates.append(captured)
            usage = captured["usage"]
            input_tokens += usage["input_tokens"]
            output_tokens += usage["output_tokens"]
            model_calls += usage["model_calls"]
            tool_calls += (
                len(captured["proposal"].get("all_calls", []))
                + (1 if captured["skill_read"] else 0)
                + len(captured["other_tool_calls"])
            )
            context.observe(
                "scenario.completed",
                {
                    "subject": "public_controller",
                    "scenario_id": scenario_id,
                    "proposal": captured["proposal"]["kind"],
                    "action": captured["proposal"].get("action"),
                    "skill_read_first": captured["skill_read_first"],
                },
            )
        cost = 0.0
        cost_unpriced = price_input_per_mtok is None or price_output_per_mtok is None
        if not cost_unpriced:
            cost = round(
                input_tokens / 1_000_000 * float(price_input_per_mtok or 0.0)
                + output_tokens / 1_000_000 * float(price_output_per_mtok or 0.0),
                6,
            )
        resource_use: dict[str, int | float | str | bool] = {
            "model_calls": model_calls,
            "tool_calls": tool_calls,
            "provider": provider,
            "model": model,
            "composed_prompt_digest": hashlib.sha256(json.dumps(prompt_digests).encode("utf-8")).hexdigest(),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost,
        }
        for control in runtime_controls:
            if isinstance(control, Mapping) and control.get("name") == "skill_digest":
                resource_use["skill_digest"] = skill_digest
            elif isinstance(control, Mapping):
                resource_use[str(control["name"])] = str(control["digest"])
        return SubjectExecution(
            output={"scenario_updates": updates, "cost_unpriced": cost_unpriced},
            resource_use=resource_use,
        )

    return invoke


__all__ = ["SKILL_CONTAINER_PATH", "controller_live_subject"]
