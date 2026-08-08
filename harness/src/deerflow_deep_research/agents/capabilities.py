"""Trusted loading and validation of package-local node capability policies.

@impl NAC-001
"""

from __future__ import annotations

import importlib.resources
import json
from dataclasses import dataclass
from typing import Any

from deerflow_deep_research.domain.context import NodeAgentCapabilityRef

_HEADER_PREFIX = "<!-- node-agent-capability: "
_HEADER_SUFFIX = " -->"
_MAX_HEADER_BYTES = 4 * 1024
_MAX_BODY_BYTES = 16 * 1024
_METADATA_KEYS = frozenset(
    {
        "schema_version",
        "capability_id",
        "role",
        "method",
        "authority_limit",
        "completion_condition",
        "uncertainty_boundary",
        "tool_posture",
    }
)


class CapabilityResourceError(ValueError):
    """A declared local capability cannot be admitted for rendering."""


@dataclass(frozen=True)
class CapabilityToolPosture:
    kind: str
    allowed_tool_names: frozenset[str] = frozenset()


@dataclass(frozen=True)
class LoadedNodeAgentCapability:
    ref: NodeAgentCapabilityRef
    policy: str
    posture: CapabilityToolPosture


def load_node_agent_capability(ref: NodeAgentCapabilityRef) -> LoadedNodeAgentCapability:
    """Load one exact package resource without accepting caller-provided prompt text."""

    if not isinstance(ref, NodeAgentCapabilityRef):
        raise CapabilityResourceError("capability_ref_invalid")
    try:
        text = importlib.resources.files(ref.package).joinpath(ref.resource).read_text(encoding="utf-8")
    except (ModuleNotFoundError, FileNotFoundError, OSError) as exc:
        raise CapabilityResourceError("capability_resource_missing") from exc
    header, separator, body = text.partition("\n")
    if not separator or len(header.encode("utf-8")) > _MAX_HEADER_BYTES:
        raise CapabilityResourceError("capability_header_invalid")
    if len(body.encode("utf-8")) > _MAX_BODY_BYTES:
        raise CapabilityResourceError("capability_body_oversize")
    metadata = _parse_metadata(header)
    if metadata.get("capability_id") != ref.capability_id:
        raise CapabilityResourceError("capability_id_mismatch")
    return LoadedNodeAgentCapability(ref=ref, policy=body, posture=_parse_posture(metadata["tool_posture"]))


def _parse_metadata(header: str) -> dict[str, Any]:
    if not header.startswith(_HEADER_PREFIX) or not header.endswith(_HEADER_SUFFIX):
        raise CapabilityResourceError("capability_header_invalid")
    try:
        parsed = json.loads(header[len(_HEADER_PREFIX) : -len(_HEADER_SUFFIX)])
    except json.JSONDecodeError as exc:
        raise CapabilityResourceError("capability_header_invalid") from exc
    if not isinstance(parsed, dict) or set(parsed) != _METADATA_KEYS or parsed.get("schema_version") != 1:
        raise CapabilityResourceError("capability_metadata_invalid")
    for key in _METADATA_KEYS - {"schema_version", "tool_posture"}:
        if not isinstance(parsed.get(key), str) or not parsed[key].strip():
            raise CapabilityResourceError("capability_metadata_invalid")
    return parsed


def _parse_posture(value: object) -> CapabilityToolPosture:
    if not isinstance(value, dict) or not isinstance(value.get("kind"), str):
        raise CapabilityResourceError("capability_tool_posture_invalid")
    if value["kind"] == "forbidden" and set(value) == {"kind"}:
        return CapabilityToolPosture(kind="forbidden")
    names = value.get("allowed_tool_names")
    if (
        value["kind"] != "required"
        or set(value) != {"kind", "allowed_tool_names"}
        or not isinstance(names, list)
        or not names
        or any(not isinstance(name, str) or not name for name in names)
        or len(set(names)) != len(names)
        or names != sorted(names)
    ):
        raise CapabilityResourceError("capability_tool_posture_invalid")
    return CapabilityToolPosture(kind="required", allowed_tool_names=frozenset(names))


__all__ = [
    "CapabilityResourceError",
    "CapabilityToolPosture",
    "LoadedNodeAgentCapability",
    "load_node_agent_capability",
]
