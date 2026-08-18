"""Frozen targeted-evidence worker and result-document contracts.

@impl TEL-002
"""

from __future__ import annotations

import re
from typing import Annotated, Any, Literal
from urllib.parse import urlsplit

from pydantic import Field, model_validator

from deerflow_deep_research.domain.lifecycle import LogicalPhase
from deerflow_deep_research.domain.work_units import (
    BUNDLE_ID_RE,
    CONTENT_HASH_RE,
    MAX_REQUIRED_OUTPUTS,
    MAX_SOURCE_REFS,
    SOURCE_ID_RE,
    WORKER_ROLE_RE,
    _FrozenModel,
    canonicalize_source_url,
)


def _derive_targeted_source_id(canonical_url: str) -> str:
    """Deterministic provider-shape source id derived from the canonical URL.

    Follows the existing ``source:w1_<slug>`` scoped-id convention so a provider
    that emits only ``url`` still yields a stable, contract-conforming id.
    """
    parts = urlsplit(canonical_url)
    base = (parts.hostname or "") + parts.path
    slug = re.sub(r"[^a-zA-Z0-9_.:-]+", "_", base).strip("_.:-")[:64]
    if not slug:
        raise ValueError("source_id_invalid")
    return f"source:te_{slug}"


class TargetedWorkerSource(_FrozenModel):
    source_id: str = Field(pattern=SOURCE_ID_RE.pattern)
    canonical_url: str = Field(min_length=1, max_length=2048)
    title: str = Field(min_length=1, max_length=512)

    @model_validator(mode="before")
    @classmethod
    def normalize_provider_shape(cls, value: Any) -> Any:
        """Map the provider source shape onto the typed contract.

        ``url`` becomes the canonical URL, ``source_id`` is derived when the
        provider omits it, and provider-only fields (``observed_relevance``,
        ``snippet``) are absorbed rather than rejected.
        """
        if not isinstance(value, dict):
            return value
        payload = dict(value)
        for absorbed in ("observed_relevance", "snippet"):
            payload.pop(absorbed, None)
        raw_url = payload.pop("url", None)
        if "canonical_url" not in payload:
            if not isinstance(raw_url, str):
                return payload
            payload["canonical_url"] = canonicalize_source_url(raw_url)
        if "source_id" not in payload:
            payload["source_id"] = _derive_targeted_source_id(payload["canonical_url"])
        return payload

    @model_validator(mode="after")
    def require_canonical_url(self) -> TargetedWorkerSource:
        if canonicalize_source_url(self.canonical_url) != self.canonical_url:
            raise ValueError("canonical_url_not_canonical")
        return self


class TargetedWorkerOutput(_FrozenModel):
    schema_version: Literal[1]
    gap_id: str = Field(min_length=1, max_length=128)
    gap_status: Literal["resolved", "deferred", "unresolved"]
    sources: Annotated[tuple[TargetedWorkerSource, ...], Field(max_length=MAX_SOURCE_REFS)] = ()
    limitations: str = Field(default="", max_length=2000)


class TargetedSourceMeta(_FrozenModel):
    source_id: str = Field(pattern=SOURCE_ID_RE.pattern)
    canonical_url: str = Field(min_length=1, max_length=2048)
    title: str = Field(min_length=1, max_length=512)
    content_ref: str


class TargetedSourceIntakeResult(_FrozenModel):
    schema_version: Literal[1]
    bundle_id: str = Field(pattern=BUNDLE_ID_RE.pattern)
    generation: int = Field(ge=0, le=2)
    phase: Literal[LogicalPhase.TARGETED_EVIDENCE]
    work_id: str
    attempt_id: str
    worker_role: str = Field(pattern=WORKER_ROLE_RE.pattern)
    spec_hash: str = Field(pattern=CONTENT_HASH_RE.pattern)
    result_contract: Literal["targeted.source-intake"]
    output_paths: Annotated[tuple[str, ...], Field(max_length=MAX_REQUIRED_OUTPUTS)] = ()
    source_ids: Annotated[tuple[str, ...], Field(max_length=MAX_SOURCE_REFS)] = ()
    sources: Annotated[tuple[TargetedSourceMeta, ...], Field(max_length=MAX_SOURCE_REFS)] = ()
    gap_id: str = Field(min_length=1, max_length=128)
    gap_status: Literal["resolved", "deferred", "unresolved"]
    limitations: str = Field(default="", max_length=2000)

    @model_validator(mode="after")
    def validate_identity_and_sources(self) -> TargetedSourceIntakeResult:
        if not self.attempt_id.startswith(f"{self.work_id}_a"):
            raise ValueError("attempt_id_identity_mismatch")
        if tuple(source.source_id for source in self.sources) != self.source_ids:
            raise ValueError("source_ids_mismatch")
        return self
