"""Pure change-02 checkpoint size bound and content-ref rule.

@impl REG-008
"""

from __future__ import annotations

import pytest

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef, run_bundle_root
from deerflow_deep_research.domain.state import (
    MAX_CHECKPOINT_STATE_BYTES,
    ContentRef,
    ResearchGraphState,
    serialize_research_state,
    validate_research_state,
)

BUNDLE_ID = "b_" + "A" * 43
BUNDLE_ROOT = run_bundle_root(RunBundleRef(bundle_id=BundleId(BUNDLE_ID), scope_bucket="s_" + "B" * 43))


def _base_values(**overrides):
    values: dict = {
        "bundle_id": BUNDLE_ID,
        "outer_thread_id": "thread-1",
        "generation": 0,
    }
    values.update(overrides)
    return values


def test_oversized_serialized_state_is_rejected() -> None:
    values = _base_values(request_text="x" * (MAX_CHECKPOINT_STATE_BYTES + 1))
    with pytest.raises(ValueError, match="state_too_large"):
        serialize_research_state(values)
    with pytest.raises(ValueError, match="state_too_large"):
        validate_research_state(values)


def test_normal_control_state_is_under_the_bound() -> None:
    values = _base_values(request_text="a normal research question")
    assert len(serialize_research_state(values)) <= MAX_CHECKPOINT_STATE_BYTES


def test_content_ref_is_the_only_way_large_content_enters_state() -> None:
    ref = ContentRef(
        sandbox_path=f"{BUNDLE_ROOT}/work/w1/g0-w1-a1/outputs/page.html",
        content_hash="h_" + "B" * 43,
        schema_version=1,
        short_summary="page title",
    )
    assert ref.sandbox_path.startswith(f"{BUNDLE_ROOT}/")


def test_content_ref_rejects_invalid_path() -> None:
    with pytest.raises(ValueError, match="content_ref_path_invalid"):
        ContentRef(sandbox_path="/etc/passwd", content_hash="h_" + "B" * 43)


def test_content_ref_rejects_invalid_hash() -> None:
    with pytest.raises(ValueError, match="content_ref_hash_invalid"):
        ContentRef(
            sandbox_path=f"{BUNDLE_ROOT}/work/w1/g0-w1-a1/outputs/page.html",
            content_hash="not-a-hash",
        )


def test_raw_runtime_authority_cannot_enter_checkpoint() -> None:
    # The frozen dataclass forbids unknown fields, so a TrustedRuntimeEnvelope /
    # AppConfig / handle / credential field is rejected before the checkpoint is built.
    with pytest.raises(TypeError):
        ResearchGraphState(**_base_values(app_config={"db": "secret"}))  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        ResearchGraphState(**_base_values(user_id="alice"))  # type: ignore[call-arg]


def test_wave1_open_question_projection_stays_under_the_checkpoint_bound() -> None:
    """The ids-only projection costs a bounded fraction of the hard state bound."""

    from deerflow_deep_research.domain.wave1 import Wave1OpenQuestionRef

    refs = tuple(
        Wave1OpenQuestionRef(question_id=f"q:w1_{'q' * 60}", work_id="g0_wave1_w00000000")
        for _ in range(64)
    )
    values = _base_values(wave1_open_questions=refs)
    assert len(serialize_research_state(values)) <= MAX_CHECKPOINT_STATE_BYTES
