"""Red tests for the bootstrap marker contract, store protocol, and binding validation.

@impl BON-001
@impl BON-002
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from deerflow_deep_research.domain.bootstrap import (
    BOOTSTRAP_MARKER_SCHEMA_VERSION,
    BootstrapBundleStoreProtocol,
    BootstrapMarker,
    validate_bootstrap_binding,
)
from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef, bundle_marker_path
from deerflow_deep_research.domain.failure_codes import FailureCode
from deerflow_deep_research.domain.state import BUNDLE_STATE_SCHEMA_VERSION, BundleLocalState

_DIGEST = "d_" + "b" * 43
_MID = "human-start"
_BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "a" * 43), scope_bucket="s_" + "c" * 43)


def _marker(
    *,
    bundle_id: BundleId = _BUNDLE.bundle_id,
    start_message_id: str = _MID,
    request_digest: str = _DIGEST,
    state_schema_version: int = BUNDLE_STATE_SCHEMA_VERSION,
) -> BootstrapMarker:
    return BootstrapMarker(
        bundle_id=bundle_id,
        start_message_id=start_message_id,
        request_digest=request_digest,
        state_schema_version=state_schema_version,
    )


def _bundle_state(**overrides: object) -> BundleLocalState:
    values: dict[str, object] = {
        "bundle_id": _BUNDLE.bundle_id,
        "implementation_mode": "all_real",
        "start_message_id": _MID,
        "start_request_digest": _DIGEST,
        "schema_version": BUNDLE_STATE_SCHEMA_VERSION,
    }
    values.update(overrides)
    return BundleLocalState(**values)  # type: ignore[arg-type]


class TestBootstrapMarker:
    def test_valid_marker_is_frozen_and_extra_forbid(self) -> None:
        marker = _marker()
        assert marker.schema_version == BOOTSTRAP_MARKER_SCHEMA_VERSION == 1
        with pytest.raises(ValidationError):
            marker.bundle_id = BundleId("b_" + "x" * 43)  # type: ignore[misc]
        with pytest.raises(ValidationError):
            BootstrapMarker.model_validate(
                {
                    "bundle_id": _BUNDLE.bundle_id.value,
                    "start_message_id": _MID,
                    "request_digest": _DIGEST,
                    "state_schema_version": BUNDLE_STATE_SCHEMA_VERSION,
                    "extra": "unwanted",
                }
            )

    @pytest.mark.parametrize(
        "field,value",
        [
            ("bundle_id", "not_a_bundle_id"),
            ("bundle_id", "b_short"),
            ("request_digest", "not_a_digest"),
            ("request_digest", "d_short"),
            ("start_message_id", ""),
            ("state_schema_version", 0),
            ("state_schema_version", 100),
        ],
    )
    def test_invalid_fields_are_rejected(self, field: str, value: object) -> None:
        with pytest.raises(ValidationError):
            _marker(**{field: value})

    def test_unsupported_marker_schema_version_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            BootstrapMarker.model_validate(
                {
                    "schema_version": 2,
                    "bundle_id": _BUNDLE.bundle_id.value,
                    "start_message_id": _MID,
                    "request_digest": _DIGEST,
                    "state_schema_version": BUNDLE_STATE_SCHEMA_VERSION,
                }
            )

    def test_canonical_json_round_trip_is_stable(self) -> None:
        marker = _marker()
        encoded = marker.canonical_json()
        assert isinstance(encoded, bytes)
        # Canonical: sorted keys, compact separators.
        assert encoded == json.dumps(
            {
                "schema_version": 1,
                "bundle_id": _BUNDLE.bundle_id.value,
                "start_message_id": _MID,
                "request_digest": _DIGEST,
                "state_schema_version": BUNDLE_STATE_SCHEMA_VERSION,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        assert BootstrapMarker.from_canonical_json(encoded) == marker
        assert BootstrapMarker.from_canonical_json(encoded.decode("utf-8")) == marker

    @pytest.mark.parametrize("payload", ["not json", "{", "[]", "42"])
    def test_invalid_canonical_json_is_rejected(self, payload: str) -> None:
        with pytest.raises(ValueError, match="marker_json_invalid"):
            BootstrapMarker.from_canonical_json(payload)


class TestBootstrapBundleStoreProtocol:
    def test_implementer_is_recognized(self) -> None:
        class _Store:
            async def establish_bundle(self, marker: BootstrapMarker) -> None: ...

            async def read_marker(self) -> BootstrapMarker | None: ...

            async def read_bundle_state(self) -> BundleLocalState: ...

        assert isinstance(_Store(), BootstrapBundleStoreProtocol)

    def test_non_implementer_is_rejected(self) -> None:
        class _NotAStore:
            async def establish_bundle(self, marker: BootstrapMarker) -> None: ...

        assert not isinstance(_NotAStore(), BootstrapBundleStoreProtocol)


class TestValidateBootstrapBinding:
    def test_bound_marker_returns_none(self) -> None:
        assert validate_bootstrap_binding(_marker(), _bundle_state()) is None

    @pytest.mark.parametrize(
        "field,checkpoint_value",
        [
            ("bundle_id", BundleId("b_" + "z" * 43)),
            ("start_message_id", "human-other"),
            ("start_request_digest", "d_" + "z" * 43),
        ],
    )
    def test_identity_mismatch_is_failure(self, field: str, checkpoint_value: object) -> None:
        failure = validate_bootstrap_binding(_marker(), _bundle_state(**{field: checkpoint_value}))
        assert failure is not None
        assert failure.code is FailureCode.IDENTITY_MISMATCH

    def test_state_schema_version_mismatch_is_failure(self) -> None:
        failure = validate_bootstrap_binding(
            _marker(state_schema_version=BUNDLE_STATE_SCHEMA_VERSION + 1),
            _bundle_state(),
        )
        assert failure is not None
        assert failure.code is FailureCode.SCHEMA_VERSION_UNSUPPORTED

    def test_non_marker_raises_type_error(self) -> None:
        with pytest.raises(TypeError):
            validate_bootstrap_binding("not a marker", _bundle_state())  # type: ignore[arg-type]

    def test_legacy_checkpoint_mapping_is_not_a_binding_source(self) -> None:
        with pytest.raises(TypeError, match="bundle_state_required"):
            validate_bootstrap_binding(_marker(), {"bundle_id": "r_" + "a" * 43})  # type: ignore[arg-type]


class TestMarkerPath:
    def test_marker_path_is_under_request_subtree(self) -> None:
        assert bundle_marker_path(_BUNDLE).endswith(f"/{_BUNDLE.bundle_id.value}/request/marker.json")
