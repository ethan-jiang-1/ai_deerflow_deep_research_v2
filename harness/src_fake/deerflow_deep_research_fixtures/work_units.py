"""Deterministic work-unit worker used only by fixture adapters."""

from __future__ import annotations

import base64
import hashlib
from collections.abc import Callable, Mapping
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from deerflow_deep_research.domain.bundle import RunBundleRef, bundle_output_path, bundle_result_path
from deerflow_deep_research.domain.invocation import RunEventRecorderProtocol, WorkUnitControllerDependencies
from deerflow_deep_research.domain.lifecycle import LogicalPhase
from deerflow_deep_research.domain.node_spec import PolicyRef
from deerflow_deep_research.domain.work_units import (
    BUNDLE_ID_RE,
    CONTENT_HASH_RE,
    WORKER_ROLE_RE,
    Attempt,
    CandidateResult,
    OutputRef,
    WorkSpec,
    canonical_json_bytes,
    compute_candidate_hash,
)
from deerflow_deep_research.engine.work_units.kernel import WorkIntent
from deerflow_deep_research.engine.work_units.validation import ResultContractHandler, register_result_contract
from deerflow_deep_research.graph.components.work_units import (
    WorkUnitComponentResult,
    run_controlled_work_unit_component,
)


class FixtureResultDocument(BaseModel):
    """Small deterministic artifact record written by a fixture worker."""

    model_config = ConfigDict(frozen=True)

    schema_version: Literal[1]
    bundle_id: str = Field(pattern=BUNDLE_ID_RE.pattern)
    generation: int = Field(ge=0, le=2)
    phase: LogicalPhase
    work_id: str
    attempt_id: str
    worker_role: str = Field(pattern=WORKER_ROLE_RE.pattern)
    spec_hash: str = Field(pattern=CONTENT_HASH_RE.pattern)
    result_contract: Literal["fixture.work-unit"]
    fixture_marker: Literal["non_research_fixture"]
    output_paths: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()


register_result_contract(ResultContractHandler("fixture.work-unit", 1, FixtureResultDocument))


def _content_hash(data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    return "h_" + base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


async def run_fixture_work_unit_component(
    parent_state: Mapping[str, Any],
    *,
    logical_name: str,
    policy: PolicyRef,
    controller: WorkUnitControllerDependencies,
    intents: tuple[WorkIntent, ...],
    clock: Callable[[], datetime],
    fault_hook: Callable[[str], None] | None = None,
    event_recorder: RunEventRecorderProtocol | None = None,
) -> WorkUnitComponentResult:
    """Use deterministic artifacts while retaining the production ledger protocol."""

    bundle = getattr(controller.store, "bundle", None)
    if not isinstance(bundle, RunBundleRef):
        raise ValueError("selected_bundle_context_missing")

    async def worker(spec: WorkSpec, attempt: Attempt) -> CandidateResult:
        resolved = await controller.resolver.resolve_worker(
            logical_name=logical_name,
            work_spec=spec,
            attempt=attempt,
            policy=policy,
        )
        writer = resolved.artifact_writer
        if writer is None:
            raise ValueError("fixture_artifact_writer_missing")

        output_refs: list[OutputRef] = []
        for relative_path in spec.required_outputs:
            content = canonical_json_bytes(
                {
                    "fixture_marker": "non_research_fixture",
                    "phase": spec.phase.value,
                    "scope": list(spec.scope),
                    "work_id": spec.work_id,
                }
            )
            await writer.write_output(relative_path, content)
            output_refs.append(
                OutputRef(
                    path=bundle_output_path(
                        bundle,
                        spec.work_id,
                        attempt.attempt_id,
                        relative_path,
                    ),
                    content_hash=_content_hash(content),
                    schema_version=1,
                    byte_count=len(content),
                )
            )

        document = FixtureResultDocument(
            schema_version=1,
            bundle_id=spec.bundle_id,
            generation=spec.generation,
            phase=spec.phase,
            work_id=spec.work_id,
            attempt_id=attempt.attempt_id,
            worker_role=spec.worker_role,
            spec_hash=spec.spec_hash,
            result_contract="fixture.work-unit",
            fixture_marker="non_research_fixture",
            output_paths=spec.required_outputs,
        )
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
            "result_ref": bundle_result_path(
                bundle,
                spec.work_id,
                attempt.attempt_id,
            ),
            "result_hash": _content_hash(result_bytes),
            "result_schema_version": spec.result_schema_version,
            "result_byte_count": len(result_bytes),
            "output_refs": tuple(output_refs),
            "source_refs": (),
        }
        payload["candidate_hash"] = compute_candidate_hash(payload)
        return CandidateResult.model_validate(payload)

    return await run_controlled_work_unit_component(
        parent_state,
        logical_name=logical_name,
        policy=policy,
        controller=controller,
        intents=intents,
        clock=clock,
        fault_hook=fault_hook,
        worker=worker,
        event_recorder=event_recorder,
    )


__all__ = ["FixtureResultDocument", "run_fixture_work_unit_component"]
