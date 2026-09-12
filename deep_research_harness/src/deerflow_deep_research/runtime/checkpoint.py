"""Resolve the effective generic checkpoint provider and probe namespace.

@impl RUI-005
@impl RUI-003
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Literal
from urllib.parse import parse_qs, urlsplit

ProviderKind = Literal["memory", "sqlite", "postgres"]
ProviderSource = Literal["database", "default"]
Durability = Literal["same_process", "restart_durable", "unavailable"]

# Infrastructure-probe checkpoint topology/namespace. It remains independent from
# the Bundle lifecycle, so provider rows can never become Run State.
INFRA_PROBE_GRAPH = "infra-probe"
INFRA_PROBE_GRAPH_VERSION = "v1"
INFRA_PROBE_CHECKPOINT_NS = f"{INFRA_PROBE_GRAPH}/{INFRA_PROBE_GRAPH_VERSION}"
_INFRA_PROBE_DIGEST_DOMAIN = "deep-research/infra-probe"
_INFRA_PROBE_KEY_SCHEMA = 1
SUPPORTED_PROBE_KEY_SCHEMAS = frozenset({_INFRA_PROBE_KEY_SCHEMA})


class CheckpointNamespaceError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"[{code}] {detail}")
        self.code = code
        self.detail = detail


class ProviderConfigurationError(ValueError):
    """Reject a retired provider input without exposing its configuration."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class ProviderSelection:
    """One effective provider selection without owning its resource lifecycle."""

    kind: ProviderKind
    source: ProviderSource
    connection: str | None
    durability: Durability
    issue: str | None = None


def _sqlite_is_memory(connection: str) -> bool:
    normalized = connection.strip()
    if normalized == ":memory:":
        return True
    parsed = urlsplit(normalized)
    if parsed.scheme.lower() != "file":
        return False
    return parse_qs(parsed.query).get("mode", [""])[-1].lower() == "memory" or parsed.path == ":memory:"


def _selection(
    *,
    kind: ProviderKind,
    source: ProviderSource,
    connection: str | None,
) -> ProviderSelection:
    if kind == "memory":
        return ProviderSelection(kind, source, None, "same_process")
    if kind == "postgres":
        normalized = connection.strip() if connection else ""
        if not normalized:
            return ProviderSelection(kind, source, None, "unavailable", "postgres_connection_missing")
        return ProviderSelection(kind, source, normalized, "restart_durable")
    normalized = connection or "store.db"
    durability: Durability = "same_process" if _sqlite_is_memory(normalized) else "restart_durable"
    return ProviderSelection(kind, source, normalized, durability)


def validate_provider_configuration(app_config: object) -> None:
    """Reject retired local provider input before classification or factory use."""

    if getattr(app_config, "checkpointer", None) is not None:
        raise ProviderConfigurationError("legacy_checkpointer_unsupported")


def resolve_effective_provider(app_config) -> ProviderSelection:
    """Classify only the supported database input without opening a provider."""

    validate_provider_configuration(app_config)

    database = getattr(app_config, "database", None)
    if database is None:
        return ProviderSelection("memory", "default", None, "same_process")
    if database.backend == "memory":
        return ProviderSelection("memory", "database", None, "same_process")
    if database.backend == "sqlite":
        return _selection(
            kind="sqlite",
            source="database",
            connection=database.checkpointer_sqlite_path,
        )
    return _selection(
        kind="postgres",
        source="database",
        connection=database.postgres_url,
    )


def _enforce_serialized_checkpoint_bound(payload: bytes) -> None:
    """Reject a serialized checkpoint or write that crosses the hard size bound.

    The bound is measured on the bytes the saver would persist, which is robust for
    every payload the shared serde sees — including framework values such as
    ``Send`` in an agent graph — so it never misjudges a non-Deep-Research state.
    Deep Research's canonical state measure is enforced separately at the node
    update, read admission, and offline migration seams.

    @impl REG-008
    """

    from deerflow_deep_research.domain.state import MAX_CHECKPOINT_STATE_BYTES, CheckpointStateBoundExceeded

    if len(payload) > MAX_CHECKPOINT_STATE_BYTES:
        raise CheckpointStateBoundExceeded()


def build_deep_research_checkpoint_serde():
    """Return the smallest explicit LangGraph msgpack compatibility boundary.

    Deep Research checkpoints intentionally persist only these three project
    value types (``ContentRef`` including its ``AttemptStatus`` alias usage,
    and the wave1 open-question projection). All other project types remain
    blocked in strict msgpack mode. Every write also crosses the hard
    whole-state size bound before any bytes reach the store.

    @impl REG-008
    @impl REG-022
    """
    from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

    class _BoundedCheckpointSerde(JsonPlusSerializer):
        def dumps_typed(self, obj: Any) -> tuple[str, bytes]:
            type_, payload = super().dumps_typed(obj)
            _enforce_serialized_checkpoint_bound(payload)
            return type_, payload

    return _BoundedCheckpointSerde(
        allowed_msgpack_modules={
            ("deerflow_deep_research.domain.state", "ContentRef"),
            ("deerflow_deep_research.domain.work_units", "AttemptStatus"),
            ("deerflow_deep_research.domain.wave1", "Wave1OpenQuestionRef"),
        }
    )


def validate_probe_key_schema(schema_version: int) -> int:
    """Reject an unsupported probe checkpoint-key schema version, fail closed."""
    if schema_version not in SUPPORTED_PROBE_KEY_SCHEMAS:
        raise CheckpointNamespaceError("schema_unsupported", "unsupported probe checkpoint-key schema version")
    return schema_version


def _length_prefixed(value: str) -> bytes:
    encoded = value.encode("utf-8")
    return len(encoded).to_bytes(8, "big") + encoded


def derive_probe_thread_key(
    *,
    effective_user_id: str,
    outer_thread_id: str,
    probe_id: str,
) -> str:
    """Derive the internal probe checkpoint thread key.

    The key is a domain-prefixed full SHA-256 digest over a versioned,
    length-prefixed canonical tuple of trusted scope plus the opaque probe id.
    Length prefixing removes delimiter ambiguity so distinct scopes cannot
    collide; the digest is an internal key that is never accepted from a caller.
    """
    for label, value in (
        ("effective_user_id", effective_user_id),
        ("outer_thread_id", outer_thread_id),
        ("probe_id", probe_id),
    ):
        if not isinstance(value, str) or not value:
            raise CheckpointNamespaceError("scope_invalid", f"{label} must be a non-empty string")
    payload = b"".join(
        (
            validate_probe_key_schema(_INFRA_PROBE_KEY_SCHEMA).to_bytes(2, "big"),
            _length_prefixed(_INFRA_PROBE_DIGEST_DOMAIN),
            _length_prefixed(effective_user_id),
            _length_prefixed(outer_thread_id),
            _length_prefixed(probe_id),
        )
    )
    digest = hashlib.sha256(payload).hexdigest()
    return f"{_INFRA_PROBE_DIGEST_DOMAIN}:{digest}"


__all__ = [
    "INFRA_PROBE_CHECKPOINT_NS",
    "INFRA_PROBE_GRAPH",
    "INFRA_PROBE_GRAPH_VERSION",
    "SUPPORTED_PROBE_KEY_SCHEMAS",
    "CheckpointNamespaceError",
    "ProviderConfigurationError",
    "Durability",
    "ProviderKind",
    "ProviderSelection",
    "ProviderSource",
    "derive_probe_thread_key",
    "resolve_effective_provider",
    "validate_provider_configuration",
    "validate_probe_key_schema",
    "build_deep_research_checkpoint_serde",
]
