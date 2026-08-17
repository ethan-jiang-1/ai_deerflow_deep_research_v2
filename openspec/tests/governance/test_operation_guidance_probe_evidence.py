"""Durable evidence contract for the bounded OpenSpec operation probes.

@impl DRC-010
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_PATH = (
    REPO_ROOT / "_backlog/_done/_closed_plans/policy-gate-injection-layer/05-operation-guidance-probe-evidence.md"
)
PROBE_HEADINGS = (
    "## 1. Delivery, Absence, And Fresh Read",
    "## 2. Supported Archive Path",
    "## 3. Archive Side Effects",
    "## 4. Selected-Change Boundary",
    "## 5. Historical Replay And Resume",
    "## 6. Change 3 Handoff Facts",
)
REQUIRED_METADATA = (
    "- **OpenSpec version:**",
    "- **Fixture configuration SHA-256:**",
    "- **Selected change:**",
    "- **Commands and exit status:**",
    "- **stdout/stderr summary:**",
    "- **Observed side effect:**",
    "- **Unknowns or limitations:**",
)


def test_operation_guidance_probe_evidence_has_complete_per_probe_metadata() -> None:
    assert EVIDENCE_PATH.is_file(), EVIDENCE_PATH
    text = EVIDENCE_PATH.read_text(encoding="utf-8")

    for index, heading in enumerate(PROBE_HEADINGS):
        assert heading in text
        start = text.index(heading)
        end = text.index(PROBE_HEADINGS[index + 1], start) if index + 1 < len(PROBE_HEADINGS) else len(text)
        record = text[start:end]
        for metadata in REQUIRED_METADATA:
            assert metadata in record, f"{heading} is missing {metadata}"
