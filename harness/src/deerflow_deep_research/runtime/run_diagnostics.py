"""Bounded redacted diagnostics for the standalone run experience.

@impl RER-003
@impl REG-013
@impl PRS-005
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from deerflow_deep_research.domain.run_experience import FailureCertainty, RunFailureCode
from deerflow_deep_research.domain.run_observation import ProviderTimeoutOrigin

DEFAULT_DEMO_DIAGNOSTIC_RELATIVE_PATH = (
    Path("deep_research_harness") / ".reports" / "deep-research-diagnostics" / "records.jsonl"
)
_MODULE_ROOT = Path(__file__).resolve().parents[3]
MAX_DIAGNOSTIC_RECORDS = 200
_DIAGNOSTIC_REFERENCE_RE = re.compile(r"^diag_[A-Za-z0-9_-]{8,64}$")
_TIMEOUT_ORIGINS = frozenset({"bridge_wall_time_budget", "provider_sdk_timeout"})


class DemoDiagnosticJournal:
    """Write compact support records outside a temporary demo workspace."""

    def __init__(
        self,
        *,
        path: Path | None = None,
        max_records: int = MAX_DIAGNOSTIC_RECORDS,
    ) -> None:
        # Diagnostics belong to the downstream project even when `make -C deep_research_harness`
        # or another launcher preserves the monorepo working directory.
        self._path = path or _MODULE_ROOT / ".reports" / "deep-research-diagnostics" / "records.jsonl"
        self._max_records = max_records

    @property
    def relative_location(self) -> str:
        return str(DEFAULT_DEMO_DIAGNOSTIC_RELATIVE_PATH)

    def publish(
        self,
        *,
        action: str,
        phase: str | None,
        code: RunFailureCode,
        certainty: FailureCertainty,
        fingerprint_source: Any = None,
        reference: str | None = None,
        recovery_trigger_timeout_origin: ProviderTimeoutOrigin | None = None,
        final_timeout_origin: ProviderTimeoutOrigin | None = None,
    ) -> str | None:
        """Persist a non-reversible fingerprint without retaining raw failure data."""
        try:
            if reference is not None and _DIAGNOSTIC_REFERENCE_RE.fullmatch(reference) is None:
                return None
            if (
                recovery_trigger_timeout_origin is not None and recovery_trigger_timeout_origin not in _TIMEOUT_ORIGINS
            ) or (final_timeout_origin is not None and final_timeout_origin not in _TIMEOUT_ORIGINS):
                return None
            reference = reference or f"diag_{secrets.token_urlsafe(18)}"
            fingerprint = self._fingerprint(
                action=action,
                phase=phase,
                code=code,
                certainty=certainty,
                source=fingerprint_source,
            )
            record = {
                "reference": reference,
                "time": datetime.now(UTC).isoformat(),
                "action": action,
                "phase": phase,
                "category": code.value,
                "certainty": certainty.value,
                "fingerprint": fingerprint,
            }
            if recovery_trigger_timeout_origin is not None:
                record["recovery_trigger_timeout_origin"] = recovery_trigger_timeout_origin
            if final_timeout_origin is not None:
                record["final_timeout_origin"] = final_timeout_origin
            self._path.parent.mkdir(parents=True, exist_ok=True)
            prior = self._read_tail()
            encoded = json.dumps(record, sort_keys=True, separators=(",", ":"))
            self._path.write_text("\n".join((*prior, encoded, "")), encoding="utf-8")
            return reference
        except OSError:
            return None

    def _read_tail(self) -> tuple[str, ...]:
        try:
            lines = self._path.read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            return ()
        except OSError:
            return ()
        return tuple(lines[-(self._max_records - 1) :])

    @staticmethod
    def _fingerprint(
        *,
        action: str,
        phase: str | None,
        code: RunFailureCode,
        certainty: FailureCertainty,
        source: Any,
    ) -> str:
        # Raw exception/message/prompt/provider values are not safe fingerprint input.
        # ``source`` remains accepted for compatibility but is deliberately ignored.
        del source
        payload = "\x1f".join((action, phase or "", code.value, certainty.value)).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


__all__ = [
    "DEFAULT_DEMO_DIAGNOSTIC_RELATIVE_PATH",
    "DemoDiagnosticJournal",
    "MAX_DIAGNOSTIC_RECORDS",
]
