"""Reduced non-checkpointed invocation context.

@impl REG-001
@impl RUI-006
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from deerflow_deep_research.domain.bootstrap import BootstrapBundleStoreProtocol
from deerflow_deep_research.domain.context import GraphContextView
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies, PolicyRef
from deerflow_deep_research.domain.profile import RequestBundleStoreProtocol
from deerflow_deep_research.domain.publication import FinalDeliveryBundleStoreProtocol, PublicationBundleStoreProtocol
from deerflow_deep_research.domain.run_observation import BudgetStopReason, FinalResponseShape, RunEventCategory
from deerflow_deep_research.domain.synthesis import SynthesisBundleStoreProtocol
from deerflow_deep_research.domain.work_units import Attempt, AttemptArtifactWriter, WorkSpec, WorkUnitStoreProtocol


@runtime_checkable
class NodeDependencyResolver(Protocol):
    def resolve(self, *, logical_name: str, attempt_id: str, policy: PolicyRef) -> NodeBuildDependencies: ...


@dataclass(frozen=True)
class WorkUnitWorkerDependencies:
    work_spec: WorkSpec
    attempt: Attempt
    node_dependencies: NodeBuildDependencies
    artifact_writer: AttemptArtifactWriter | None = None


@runtime_checkable
class WorkUnitDependencyResolver(Protocol):
    async def resolve_worker(
        self,
        *,
        logical_name: str,
        work_spec: WorkSpec,
        attempt: Attempt,
        policy: PolicyRef,
    ) -> WorkUnitWorkerDependencies: ...


@runtime_checkable
class RunEventRecorderProtocol(Protocol):
    """Future local, sandbox, or pod producers share this closed observation seam.

    Implementations accept only validated scalar event facts and allocate durable
    sequence numbers; producers never receive a retained-session path or file handle.
    """

    async def record(
        self,
        *,
        category: RunEventCategory,
        phase: str,
        outcome: str | None = None,
        work_id: str | None = None,
        attempt_id: str | None = None,
        validation_stage: str | None = None,
        validation_codes: tuple[str, ...] = (),
        critic_kind: str | None = None,
        response_shape: FinalResponseShape | None = None,
        failure_category: str | None = None,
        worker_failure_category: str | None = None,
        budget_stop_reason: BudgetStopReason | None = None,
        retry_count: int | None = None,
        diagnostic_ref: str | None = None,
        recovery_correlation_id: str | None = None,
        provider_category: str | None = None,
        retry_ordinal: int | None = None,
        backoff_milliseconds: int | None = None,
        recovery_event_disposition: str | None = None,
        readiness_route: str | None = None,
        readiness_blocked_count: int | None = None,
        readiness_pass_guard: str | None = None,
        readiness_failure_codes: tuple[str, ...] = (),
        targeted_evidence_reason: str | None = None,
        targeted_gap_count: int | None = None,
    ) -> None: ...


@runtime_checkable
class RuntimeObservationProjectionProtocol(Protocol):
    """A non-checkpointed runtime projection with no control capability."""

    def emit(self, fields: Mapping[str, object], *, logger: logging.Logger | Any) -> None: ...

    async def aemit(self, fields: Mapping[str, object], *, logger: logging.Logger | Any) -> None: ...


@dataclass(frozen=True)
class WorkUnitControllerDependencies:
    store: WorkUnitStoreProtocol
    resolver: WorkUnitDependencyResolver

    def __post_init__(self) -> None:
        if not isinstance(self.store, WorkUnitStoreProtocol):
            raise TypeError("store must implement WorkUnitStoreProtocol")
        if not isinstance(self.resolver, WorkUnitDependencyResolver):
            raise TypeError("resolver must implement WorkUnitDependencyResolver")


@dataclass(frozen=True)
class GraphInvocationContext:
    graph_context: GraphContextView
    dependency_resolver: NodeDependencyResolver
    work_units: WorkUnitControllerDependencies | None = None
    bootstrap_bundle: BootstrapBundleStoreProtocol | None = None
    request_bundle: RequestBundleStoreProtocol | None = None
    synthesis_bundle: SynthesisBundleStoreProtocol | None = None
    publication_bundle: PublicationBundleStoreProtocol | None = None
    final_delivery_bundle: FinalDeliveryBundleStoreProtocol | None = None
    event_recorder: RunEventRecorderProtocol | None = None
    observation_projection: RuntimeObservationProjectionProtocol | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.graph_context, GraphContextView):
            raise TypeError("graph_context must be a GraphContextView")
        if not isinstance(self.dependency_resolver, NodeDependencyResolver):
            raise TypeError("dependency_resolver must implement NodeDependencyResolver")
        if self.bootstrap_bundle is not None and not isinstance(self.bootstrap_bundle, BootstrapBundleStoreProtocol):
            raise TypeError("bootstrap_bundle must implement BootstrapBundleStoreProtocol")
        if self.request_bundle is not None and not isinstance(self.request_bundle, RequestBundleStoreProtocol):
            raise TypeError("request_bundle must implement RequestBundleStoreProtocol")
        if self.synthesis_bundle is not None and not isinstance(self.synthesis_bundle, SynthesisBundleStoreProtocol):
            raise TypeError("synthesis_bundle must implement SynthesisBundleStoreProtocol")
        if self.publication_bundle is not None and not isinstance(
            self.publication_bundle, PublicationBundleStoreProtocol
        ):
            raise TypeError("publication_bundle must implement PublicationBundleStoreProtocol")
        if self.final_delivery_bundle is not None and not isinstance(
            self.final_delivery_bundle, FinalDeliveryBundleStoreProtocol
        ):
            raise TypeError("final_delivery_bundle must implement FinalDeliveryBundleStoreProtocol")
        if self.event_recorder is not None and not isinstance(self.event_recorder, RunEventRecorderProtocol):
            raise TypeError("event_recorder must implement RunEventRecorderProtocol")
        if self.observation_projection is not None and not isinstance(
            self.observation_projection,
            RuntimeObservationProjectionProtocol,
        ):
            raise TypeError("observation_projection must implement RuntimeObservationProjectionProtocol")


__all__ = ["GraphInvocationContext", "NodeDependencyResolver", "RuntimeObservationProjectionProtocol"]
