"""Bounded configured-Gateway forwarding proof for the withheld candidate path.

This is a marked real-Gateway integration test: it requires the selected
profile-launched direct local Gateway at ``http://127.0.0.1:8001`` plus a real
model credential, and it proves that a predecessor-owned
``deep_research.progress.v1`` event emitted by the reflected ``deep_research``
tool reaches DeerFlow's public SSE ``custom`` channel with matching safe
thread/run/Bundle correlation.

The probe records only redacted evidence, invokes no real entrypoint
presentation callback, and never retains or replays the proof record.

@impl GOO-002
"""

from __future__ import annotations

import asyncio
import json
import urllib.error
import urllib.request
from collections import Counter

import pytest
from langchain_core.messages import HumanMessage

from deerflow_deep_research.runtime.gateway_observer import (
    PUBLIC_GATEWAY_ORIGIN,
    GatewayObserver,
    GatewayObserverError,
    HttpGatewayPublicClient,
)

pytestmark = pytest.mark.requires_llm

GATEWAY_HEALTH_URL = f"{PUBLIC_GATEWAY_ORIGIN}/health"
_DEEP_RESEARCH_QUESTION = (
    "Please do a real deep research comparing DeepSeek vs OpenAI pricing and capabilities, then recommend one provider."
)


def _gateway_available() -> bool:
    try:
        request = urllib.request.Request(GATEWAY_HEALTH_URL, method="GET")
        with urllib.request.urlopen(request, timeout=1.0) as response:
            return 200 <= response.status < 300
    except (OSError, urllib.error.URLError):
        return False


def _redact(value: object, *, keep: int = 6) -> str:
    text = str(value)
    if len(text) <= keep + 1:
        return text
    return f"{text[:keep]}...{text[-4:]}"


def _assert_redacted(candidate: dict[str, object], *, bundle_id: str, outer_run_id: str) -> None:
    """The withheld candidate carries only safe predecessor-approved fields."""

    assert candidate["type"] == "deep_research.progress.v1"
    assert candidate["phase"] in {"bootstrap", "hitl1", "gate", "wave0", "wave1", "wave2", "final_delivery"}
    assert candidate["operation"] in {"node", "gate", "attempt", "submit", "retry", "exhaustion", "validation"}
    assert candidate["outcome"] in {
        "started",
        "completed",
        "failed",
        "rejected",
        "cancelled",
        "stopped",
        "blocked",
        "retrying",
    }
    assert candidate["bundle_id"] == bundle_id
    for key in ("phase", "operation", "outcome"):
        assert " " not in str(candidate[key])
        assert "\n" not in str(candidate[key])
    if "outer_run_id" in candidate:
        assert candidate["outer_run_id"] == outer_run_id


async def _probe_withheld_forwarding() -> tuple[dict[str, object], list[dict[str, object]], str | None]:
    client = HttpGatewayPublicClient()
    withheld: list[dict[str, object]] = []
    observations: list[str] = []
    observer = GatewayObserver(
        client=client,
        transport_observer=lambda observation: observations.append(observation.kind),
        withheld_candidate_observer=withheld.append,
    )
    try:
        result = await asyncio.wait_for(
            observer.dispatch(
                action="start",
                bundle_id=None,
                messages=(HumanMessage(content=_DEEP_RESEARCH_QUESTION),),
            ),
            timeout=600,
        )
    except GatewayObserverError as exc:
        pytest.fail(f"public Gateway turn failed before a typed result: {exc}")
    finally:
        await client.aclose()
    assert isinstance(result, dict), "reflected tool must return the typed lifecycle result dict"
    bundle_id = result.get("bundle_id")
    assert isinstance(bundle_id, str) and bundle_id.startswith("b_"), "typed result must name a Bundle"
    assert result.get("implementation_mode") == "all_real"
    # The public SSE metadata run correlation is the only safe run identity the
    # observer retains; it must match the reflected candidate's outer_run_id.
    return result, withheld, observer.correlation.run_id


def test_gateway_forwarding_proof() -> None:
    """One bounded configured-Gateway integration through the withheld-candidate path.

    Proves a predecessor-owned ``deep_research.progress.v1`` event from the
    reflected tool reaches the public SSE ``custom`` channel with matching safe
    thread/run/Bundle correlation, then leaves the candidate withheld.
    """

    if not _gateway_available():
        pytest.skip(f"selected local Gateway is not reachable at {GATEWAY_HEALTH_URL}")

    result, withheld, outer_run_id = asyncio.run(_probe_withheld_forwarding())

    # The proof is falsifiable: without a matching nested event the candidate
    # stays withheld and this test fails, keeping the Change active for repair.
    assert withheld, (
        "no deep_research.progress.v1 candidate reached the public SSE custom channel; nested forwarding is unproven"
    )
    bundle_id = str(result["bundle_id"])
    for candidate in withheld:
        _assert_redacted(candidate, bundle_id=bundle_id, outer_run_id=outer_run_id or "")

    phases = Counter(str(candidate.get("phase")) for candidate in withheld)
    kinds = Counter(str(candidate.get("operation")) for candidate in withheld)
    print(
        json.dumps(
            {
                "proof": "deep_research.progress.v1 reached public SSE custom channel",
                "bundle_id": _redact(bundle_id),
                "outer_run_id": _redact(outer_run_id) if outer_run_id else None,
                "typed_result": {
                    "action": result.get("action"),
                    "code": result.get("code"),
                    "availability": result.get("availability"),
                    "durability": result.get("durability"),
                },
                "withheld_candidates": len(withheld),
                "phases": dict(phases),
                "operations": dict(kinds),
                "evidence_scope": "redacted, non-retained, no presentation callback invoked",
            },
            indent=2,
        )
    )
