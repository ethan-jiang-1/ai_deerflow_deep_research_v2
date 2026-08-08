"""Pure Bootstrap marker contract, store protocol, and Bundle-State binding validation.

@impl BON-001
@impl BON-002

The Harness publishes a Run Bundle and its initial Bundle-local State before Bootstrap
runs. Bootstrap establishes only contained request content, including an optional
schema/version marker bound to that already-published State. This module owns the frozen
marker contract, the runtime-checkable store protocol the node consumes, and pure binding
validation that reuses gate-kernel ``FailureCode`` values. It performs no I/O or mutation.
"""

from __future__ import annotations

import json
from typing import Literal, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from deerflow_deep_research.domain.bundle import BundleId
from deerflow_deep_research.domain.failure_codes import FailureCode
from deerflow_deep_research.domain.gate import Failure
from deerflow_deep_research.domain.state import BundleLocalState

BOOTSTRAP_MARKER_SCHEMA_VERSION = 1


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class BootstrapMarker(_FrozenModel):
    """Versioned contained marker bound to one published Bundle-local State.

    ``schema_version`` is the marker format version. ``state_schema_version`` records
    the Bundle-local State schema version under which the marker was established. The
    marker is request content, never a lifecycle root, selector, or recovery source.
    """

    schema_version: Literal[BOOTSTRAP_MARKER_SCHEMA_VERSION] = BOOTSTRAP_MARKER_SCHEMA_VERSION
    bundle_id: BundleId
    start_message_id: str = Field(min_length=1, max_length=256)
    request_digest: str = Field(pattern=r"^d_[A-Za-z0-9_-]{43}$")
    state_schema_version: int = Field(ge=1, le=99)

    @field_validator("bundle_id", mode="before")
    @classmethod
    def validate_bundle_id(cls, value: object) -> BundleId:
        if isinstance(value, BundleId):
            return value
        return BundleId(value)  # type: ignore[arg-type]

    @field_serializer("bundle_id")
    def serialize_bundle_id(self, value: BundleId) -> str:
        return value.value

    @classmethod
    def from_bundle_state(cls, state: BundleLocalState) -> BootstrapMarker:
        """Build the only legal marker from an already-published Bundle State."""
        if not isinstance(state, BundleLocalState):
            raise TypeError("bundle_state_required")
        if state.start_message_id is None or state.start_request_digest is None:
            raise ValueError("bootstrap_state_incomplete")
        return cls(
            bundle_id=state.bundle_id,
            start_message_id=state.start_message_id,
            request_digest=state.start_request_digest,
            state_schema_version=state.schema_version,
        )

    def canonical_json(self) -> bytes:
        return json.dumps(
            self.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

    @classmethod
    def from_canonical_json(cls, data: bytes | str) -> BootstrapMarker:
        if isinstance(data, str):
            raw = data
        elif isinstance(data, (bytes, bytearray)):
            raw = data.decode("utf-8")
        else:
            raise ValueError("marker_json_invalid")
        try:
            payload = json.loads(raw)
        except ValueError as exc:
            raise ValueError("marker_json_invalid") from exc
        if not isinstance(payload, dict):
            raise ValueError("marker_json_invalid")
        return cls.model_validate(payload)


@runtime_checkable
class BootstrapBundleStoreProtocol(Protocol):
    """Runtime-owned capability for one preselected Bundle's bootstrap content."""

    async def establish_bundle(self, marker: BootstrapMarker) -> None: ...

    async def read_marker(self) -> BootstrapMarker | None: ...

    async def read_bundle_state(self) -> BundleLocalState: ...


def validate_bootstrap_binding(
    marker: BootstrapMarker,
    state: BundleLocalState,
) -> Failure | None:
    """Return a typed ``Failure`` if *marker* is not bound to *state*, else ``None``.

    Pure: performs no I/O or mutation. It compares the marker's opaque Bundle identity,
    start-message correlation, request digest, and State schema version directly against
    the selected Bundle-local State. Legacy checkpoint mappings are not binding inputs.
    """
    if not isinstance(marker, BootstrapMarker):
        raise TypeError("marker_required")
    if not isinstance(state, BundleLocalState):
        raise TypeError("bundle_state_required")
    if marker.bundle_id != state.bundle_id:
        return Failure(
            code=FailureCode.IDENTITY_MISMATCH,
            rule_name="bootstrap_binding",
            description="bundle_id mismatch",
        )
    if marker.start_message_id != state.start_message_id:
        return Failure(
            code=FailureCode.IDENTITY_MISMATCH,
            rule_name="bootstrap_binding",
            description="start_message_id mismatch",
        )
    if marker.request_digest != state.start_request_digest:
        return Failure(
            code=FailureCode.IDENTITY_MISMATCH,
            rule_name="bootstrap_binding",
            description="request_digest mismatch",
        )
    if marker.state_schema_version != state.schema_version:
        return Failure(
            code=FailureCode.SCHEMA_VERSION_UNSUPPORTED,
            rule_name="bootstrap_binding",
            description="state_schema_version mismatch",
        )
    return None


__all__ = [
    "BOOTSTRAP_MARKER_SCHEMA_VERSION",
    "BootstrapBundleStoreProtocol",
    "BootstrapMarker",
    "validate_bootstrap_binding",
]
