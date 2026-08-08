"""Closed final-delivery composition and gate-view contracts.

@impl FID-001
@impl FID-002
@impl FID-003
"""

from __future__ import annotations

from deerflow_deep_research.domain.lifecycle import FinalVerdict, FrozenContract
from deerflow_deep_research.domain.publication import (
    FINAL_DELIVERY_GATE_VIEW_KEY,
    FinalDeliveryGateView,
    FinalDeliveryLayoutCandidate,
)


class FinalDeliveryRequest(FrozenContract):
    generation: int


class FinalDeliveryResult(FrozenContract):
    route: FinalVerdict


__all__ = [
    "CONTRACTS",
    "FINAL_DELIVERY_GATE_VIEW_KEY",
    "FinalDeliveryGateView",
    "FinalDeliveryLayoutCandidate",
    "FinalDeliveryRequest",
    "FinalDeliveryResult",
]


CONTRACTS = (FinalDeliveryRequest, FinalDeliveryResult)
