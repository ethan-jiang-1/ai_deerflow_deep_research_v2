"""Strict-msgpack compatibility for the persisted Deep Research value types.

@impl RUI-008
@impl REG-022
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef, bundle_profile_path
from deerflow_deep_research.domain.state import ContentRef
from deerflow_deep_research.domain.wave1 import Wave1OpenQuestionRef
from deerflow_deep_research.domain.work_units import AttemptStatus
from deerflow_deep_research.runtime.checkpoint import build_deep_research_checkpoint_serde

FIXTURE_SOURCE = Path(__file__).resolve().parents[2] / "src_fake"
BUNDLE = RunBundleRef(
    bundle_id=BundleId("b_" + "A" * 43),
    scope_bucket="s_" + "B" * 43,
)


def test_checkpoint_serde_round_trips_every_persisted_project_type() -> None:
    serde = build_deep_research_checkpoint_serde()
    value = {
        "profile_ref": ContentRef(
            sandbox_path=bundle_profile_path(BUNDLE),
            content_hash="h_" + "B" * 43,
        ),
        "work_status": AttemptStatus.FAILED,
        "wave1_open_questions": (Wave1OpenQuestionRef(question_id="q:w1_oq_1", work_id="g0_wave1_w0000"),),
    }

    decoded = serde.loads_typed(serde.dumps_typed(value))

    assert isinstance(decoded["profile_ref"], ContentRef)
    assert decoded["work_status"] is AttemptStatus.FAILED
    assert isinstance(decoded["wave1_open_questions"][0], Wave1OpenQuestionRef)


def test_strict_msgpack_blocks_an_unregistered_project_type_but_preserves_the_explicit_types() -> None:
    code = """
from deerflow_deep_research.domain.state import ContentRef
from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef, bundle_profile_path
from deerflow_deep_research_fixtures.scenario import FixtureScenario
from deerflow_deep_research.domain.wave1 import Wave1OpenQuestionRef
from deerflow_deep_research.domain.work_units import AttemptStatus
from deerflow_deep_research.runtime.checkpoint import build_deep_research_checkpoint_serde

serde = build_deep_research_checkpoint_serde()
bundle = RunBundleRef(BundleId('b_' + 'A' * 43), 's_' + 'B' * 43)
value = {
    'ref': ContentRef(bundle_profile_path(bundle), 'h_' + 'B' * 43),
    'status': AttemptStatus.FAILED,
    'open_question': Wave1OpenQuestionRef(question_id='q:w1_oq_1', work_id='g0_wave1_w0000'),
}
decoded = serde.loads_typed(serde.dumps_typed(value))
assert isinstance(decoded['ref'], ContentRef)
assert decoded['status'] is AttemptStatus.FAILED
assert isinstance(decoded['open_question'], Wave1OpenQuestionRef)

permissive = __import__('langgraph.checkpoint.serde.jsonplus', fromlist=['JsonPlusSerializer']).JsonPlusSerializer(
    allowed_msgpack_modules=True
)
payload = permissive.dumps_typed({'unknown': FixtureScenario()})
blocked = serde.loads_typed(payload)
assert not isinstance(blocked['unknown'], FixtureScenario)
"""
    existing_pythonpath = os.environ.get("PYTHONPATH")
    result = subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
        env=os.environ
        | {
            "LANGGRAPH_STRICT_MSGPACK": "true",
            "PYTHONPATH": str(FIXTURE_SOURCE) + (os.pathsep + existing_pythonpath if existing_pythonpath else ""),
        },
    )

    assert "Deserializing unregistered type" not in result.stderr
    assert "Blocked deserialization" in result.stderr


@pytest.mark.asyncio
async def test_bundle_graph_checkpoint_opens_with_the_registered_serde(tmp_path: Path) -> None:
    """The Bundle-contained graph store crosses the same explicit boundary."""

    from deerflow_deep_research.domain.state import BundleLocalState
    from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle

    BundleLifecycle(workspace_host_path=tmp_path)._publish_sync(
        BUNDLE, BundleLocalState(bundle_id=BUNDLE.bundle_id, implementation_mode="all_real")
    )
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)

    async with lifecycle.open_graph_checkpoint(BUNDLE) as saver:
        serde = saver.serde
        decoded = serde.loads_typed(
            serde.dumps_typed(
                {
                    "ref": ContentRef(bundle_profile_path(BUNDLE), "h_" + "B" * 43),
                    "open_question": Wave1OpenQuestionRef(question_id="q:w1_oq_1", work_id="g0_wave1_w0000"),
                }
            )
        )

    assert isinstance(decoded["ref"], ContentRef)
    assert isinstance(decoded["open_question"], Wave1OpenQuestionRef)
