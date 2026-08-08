"""Deterministic materializer for Wave2 synthesis artifacts.

@impl WSN-002
"""

from __future__ import annotations

from deerflow_deep_research.domain.synthesis import SynthesisBundleStoreProtocol, SynthesisResult


async def materialize_synthesis(result: SynthesisResult, bundle_store: SynthesisBundleStoreProtocol) -> None:
    """Persist synthesis through the already-selected Bundle store only."""
    if not isinstance(result, SynthesisResult):
        raise TypeError("synthesis_result_required")
    if not isinstance(bundle_store, SynthesisBundleStoreProtocol):
        raise TypeError("synthesis_bundle_required")
    await bundle_store.write_synthesis(result)
