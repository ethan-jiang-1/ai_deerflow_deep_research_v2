"""Wave0 real work-unit component.

@impl WOU-001
@impl WOU-002
@impl WOU-003
@impl WOU-004
@impl REG-002
@impl WFO-001
"""

from __future__ import annotations

import base64
import hashlib
from collections.abc import Callable, Mapping
from datetime import datetime
from typing import Any

from deerflow_deep_research.domain.bundle import (
    RunBundleRef,
    bundle_result_path,
    bundle_source_content_path,
)
from deerflow_deep_research.domain.invocation import RunEventRecorderProtocol, WorkUnitControllerDependencies
from deerflow_deep_research.domain.node_spec import PolicyRef
from deerflow_deep_research.domain.run_observation import (
    FinalResponseShape,
    RunEventCategory,
    classify_final_response_shape,
)
from deerflow_deep_research.domain.work_units import (
    Attempt,
    CandidateResult,
    SourceRef,
    Wave0SourceMeta,
    WorkerAttemptFailure,
    WorkerFailureCategory,
    WorkSpec,
    canonical_json_bytes,
    compute_candidate_hash,
)
from deerflow_deep_research.domain.workflow_outcomes import (
    InvocationFailure,
    invoke_and_normalize,
    worker_failure_for_invocation,
)
from deerflow_deep_research.engine.work_units.kernel import WorkIntent
from deerflow_deep_research.graph.components.work_units import (
    WorkUnitComponentResult,
    run_controlled_work_unit_component,
)

from .prompts import (
    WAVE0_REPAIR_VALIDATION_CATEGORY,
    build_wave0_assignment_projection,
    build_wave0_repair_prompt,
    build_wave0_result_document,
    build_wave0_worker_prompt,
    parse_wave0_worker_output,
)

WAVE0_REAL_POLICY = PolicyRef(name="real-wave0", version="v1")
_WAVE0_VALIDATION_CODES = frozenset(
    {
        "wave0_worker_output_empty",
        "wave0_worker_output_json_invalid",
        "wave0_worker_output_invalid",
    }
)


def _content_hash(data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    return "h_" + base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def _canonical_validation_code(error: ValueError) -> str:
    """Collapse parser detail to the closed Journal vocabulary."""

    code = str(error)
    return code if code in _WAVE0_VALIDATION_CODES else "wave0_worker_output_invalid"


async def _observe_validation(
    event_recorder: RunEventRecorderProtocol | None,
    *,
    spec: WorkSpec,
    attempt: Attempt,
    stage: str,
    codes: tuple[str, ...],
    response_shape: FinalResponseShape,
) -> None:
    """Publish parser evidence without allowing observation persistence to affect a worker."""

    if event_recorder is None:
        return
    try:
        await event_recorder.record(
            category=RunEventCategory.VALIDATION,
            phase="wave0",
            work_id=spec.work_id,
            attempt_id=attempt.attempt_id,
            validation_stage=stage,
            validation_codes=codes,
            response_shape=response_shape,
        )
    except Exception:
        return


def materialize_wave0_intents(
    topic_registry: Mapping[str, Any] | tuple[Mapping[str, Any], ...] | None,
    *,
    topic_filter: tuple[str, ...] | None = None,
) -> tuple[WorkIntent, ...]:
    """Build one real source-intake ``WorkIntent`` per topic in the planner registry.

    When *topic_filter* is non-empty, only topics whose ``topic_id`` is in the
    filter set get a WorkIntent. This supports scoped rerun (TOPIC/FINDING).

    @impl WAN-001
    @impl REN-004
    """
    filter_set: frozenset[str] | None = frozenset(topic_filter) if topic_filter else None
    intents: list[WorkIntent] = []
    for entry in topic_registry or ():
        if not isinstance(entry, Mapping):
            continue
        topic_id = entry.get("topic_id")
        if not isinstance(topic_id, str) or not topic_id.strip():
            continue
        if filter_set is not None and topic_id not in filter_set:
            continue
        intents.append(
            WorkIntent(
                worker_role="wave0_intake",
                scope=(topic_id,),
                result_contract="wave0.source-intake",
                result_schema_version=1,
                required_outputs=(),
            )
        )
    if not intents:
        raise ValueError("topic_registry_empty")
    return tuple(intents)


async def run_wave0_work_units_real(
    state: Mapping[str, Any],
    *,
    controller: WorkUnitControllerDependencies,
    topic_registry: Mapping[str, Any] | tuple[Mapping[str, Any], ...] | None,
    topic_filter: tuple[str, ...] | None = None,
    clock: Callable[[], datetime],
    fault_hook: Callable[[str], None] | None = None,
    event_recorder: RunEventRecorderProtocol | None = None,
) -> WorkUnitComponentResult:
    """Run real Wave0 source intake: one worker per topic through the bridge.

    @impl WAN-001
    @impl WAN-002
    """
    intents = materialize_wave0_intents(topic_registry, topic_filter=topic_filter)
    bundle = getattr(controller.store, "bundle", None)
    if not isinstance(bundle, RunBundleRef):
        raise ValueError("selected_bundle_context_missing")

    async def worker(spec: WorkSpec, attempt: Attempt) -> CandidateResult:
        resolved = await controller.resolver.resolve_worker(
            logical_name="wave0",
            work_spec=spec,
            attempt=attempt,
            policy=WAVE0_REAL_POLICY,
        )
        writer = resolved.artifact_writer
        if writer is None:
            raise ValueError("wave0_artifact_writer_missing")
        capabilities = resolved.node_dependencies.capabilities
        outcome = await invoke_and_normalize(
            lambda: capabilities.run_agent(
                context=resolved.node_dependencies.agent_context,
                request=build_wave0_worker_prompt(spec, topic_registry),
            ),
            phase="wave0",
        )
        if isinstance(outcome, InvocationFailure):
            raise worker_failure_for_invocation(outcome.problem)
        result = outcome.result
        initial_response_shape = classify_final_response_shape(result.summary)
        try:
            output = parse_wave0_worker_output(result.summary)
        except ValueError as parse_error:
            await _observe_validation(
                event_recorder,
                spec=spec,
                attempt=attempt,
                stage="initial",
                codes=(_canonical_validation_code(parse_error),),
                response_shape=initial_response_shape,
            )
            assignment = build_wave0_assignment_projection(spec, topic_registry)
            repair_outcome = await invoke_and_normalize(
                lambda: capabilities.run_agent(
                    context=resolved.node_dependencies.agent_context,
                    request=build_wave0_repair_prompt(
                        result.summary,
                        result.untrusted_tool_results,
                        assignment=assignment,
                        validation_category=WAVE0_REPAIR_VALIDATION_CATEGORY,
                    ),
                ),
                phase="wave0",
            )
            if isinstance(repair_outcome, InvocationFailure):
                raise worker_failure_for_invocation(repair_outcome.problem) from parse_error
            repaired = repair_outcome.result
            repair_response_shape = classify_final_response_shape(repaired.summary)
            try:
                output = parse_wave0_worker_output(repaired.summary)
            except ValueError as repair_error:
                await _observe_validation(
                    event_recorder,
                    spec=spec,
                    attempt=attempt,
                    stage="repair",
                    codes=(_canonical_validation_code(repair_error),),
                    response_shape=repair_response_shape,
                )
                raise WorkerAttemptFailure(WorkerFailureCategory.STRUCTURED_OUTPUT) from repair_error
            await _observe_validation(
                event_recorder,
                spec=spec,
                attempt=attempt,
                stage="repair",
                codes=(),
                response_shape=repair_response_shape,
            )
        else:
            await _observe_validation(
                event_recorder,
                spec=spec,
                attempt=attempt,
                stage="initial",
                codes=(),
                response_shape=initial_response_shape,
            )
        metas: list[Wave0SourceMeta] = []
        source_refs: list[SourceRef] = []
        for index, source in enumerate(output.sources):
            cache_name = f"source-{index}.json"
            content = canonical_json_bytes(
                {
                    "source_id": source.source_id,
                    "canonical_url": source.canonical_url,
                    "title": source.title,
                    "fetch_status": source.fetch_status,
                }
            )
            await writer.write_source(cache_name, content)
            content_ref = bundle_source_content_path(bundle, spec.work_id, attempt.attempt_id, cache_name)
            content_hash = _content_hash(content)
            byte_count = len(content)
            metas.append(
                Wave0SourceMeta(
                    source_id=source.source_id,
                    canonical_url=source.canonical_url,
                    title=source.title,
                    content_ref=content_ref,
                    fetch_status=source.fetch_status,
                )
            )
            source_refs.append(
                SourceRef(
                    source_id=source.source_id,
                    canonical_url=source.canonical_url,
                    content_ref=content_ref,
                    content_hash=content_hash,
                    byte_count=byte_count,
                )
            )
        document = build_wave0_result_document(spec, attempt, tuple(metas), output.baseline_facts, output.limitations)
        result_bytes = canonical_json_bytes(document)
        await writer.write_result(document)
        payload: dict[str, Any] = {
            "schema_version": 1,
            "bundle_id": spec.bundle_id,
            "generation": spec.generation,
            "phase": spec.phase,
            "work_id": spec.work_id,
            "attempt_id": attempt.attempt_id,
            "worker_role": spec.worker_role,
            "spec_hash": spec.spec_hash,
            "result_contract": spec.result_contract,
            "result_ref": bundle_result_path(bundle, spec.work_id, attempt.attempt_id),
            "result_hash": _content_hash(result_bytes),
            "result_schema_version": spec.result_schema_version,
            "result_byte_count": len(result_bytes),
            "output_refs": (),
            "source_refs": source_refs,
        }
        payload["candidate_hash"] = compute_candidate_hash(payload)
        return CandidateResult.model_validate(payload)

    return await run_controlled_work_unit_component(
        state,
        logical_name="wave0",
        policy=WAVE0_REAL_POLICY,
        controller=controller,
        intents=intents,
        clock=clock,
        fault_hook=fault_hook,
        worker=worker,
        event_recorder=event_recorder,
    )


__all__ = [
    "WAVE0_REAL_POLICY",
    "materialize_wave0_intents",
    "run_wave0_work_units_real",
]
