"""Pure final-publication contracts and store interfaces.

@impl FID-001
@impl FID-002
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import Field, model_validator

from deerflow_deep_research.domain.failure_codes import FailureCode
from deerflow_deep_research.domain.lifecycle import FrozenContract
from deerflow_deep_research.domain.state import ContentRef

FINAL_DELIVERY_GATE_VIEW_KEY = "_final_delivery_gate_view"


class FinalDeliveryLayoutCandidate(FrozenContract):
    schema_version: int = 1
    conclusion_order: tuple[str, ...] = Field(default=(), max_length=8)
    uncertainty_order: tuple[str, ...] = Field(default=(), max_length=8)

    @model_validator(mode="after")
    def validate_unique_orders(self) -> FinalDeliveryLayoutCandidate:
        if len(set(self.conclusion_order)) != len(self.conclusion_order):
            raise ValueError("conclusion_order_duplicate")
        if len(set(self.uncertainty_order)) != len(self.uncertainty_order):
            raise ValueError("uncertainty_order_duplicate")
        return self


class FinalDeliveryGateView(FrozenContract):
    published_refs: tuple[ContentRef, ContentRef] | None = None
    accepted_evidence_present: bool
    failure_code: FailureCode | None = None

    @model_validator(mode="after")
    def validate_view_shape(self) -> FinalDeliveryGateView:
        if self.published_refs is None and self.failure_code is None:
            raise ValueError("final_delivery_gate_failure_required")
        if self.published_refs is not None and self.failure_code is not None:
            raise ValueError("final_delivery_gate_view_conflict")
        return self


@runtime_checkable
class PublicationBundleStoreProtocol(Protocol):
    async def publish_final(self, report: bytes, citation_map: bytes) -> tuple[ContentRef, ContentRef]: ...


@runtime_checkable
class FinalDeliveryBundleStoreProtocol(Protocol):
    """Read-only content boundary consumed by final delivery."""

    async def read_readiness_report_plan(self, ref: ContentRef) -> bytes: ...

    async def read_synthesis_evidence(self, accepted_refs: tuple[str, ...]) -> tuple[object, ...]: ...

    async def read_final_artifacts(self, refs: tuple[ContentRef, ContentRef]) -> tuple[bytes, bytes]: ...


__all__ = [
    "FINAL_DELIVERY_GATE_VIEW_KEY",
    "FinalDeliveryBundleStoreProtocol",
    "FinalDeliveryGateView",
    "FinalDeliveryLayoutCandidate",
    "PublicationBundleStoreProtocol",
]
