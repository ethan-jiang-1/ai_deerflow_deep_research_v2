"""Glossary-only record boundary for the current evaluation and Run terms.

@impl NC-C03
@impl EC-C02
@impl OR-C05
@impl EV-C01
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CONTEXT_PATH = REPO_ROOT / "deep_research_harness" / "CONTEXT.md"

_GLOSSARY_RECORDS = (
    "Fixture Composition",
    "Run Bundle",
    "Evaluation Run Workspace",
    "Evaluation Run Bundle",
    "Cognitive Evaluation Review",
    "Node Evaluation Run",
    "Flow Evaluation Run",
)
_REMOVED_TAIL_SECTIONS = (
    "Local-First Deployment",
    "People Initiate Evaluation Review",
    "Reviews Are Separate Immutable Records",
    "Review Records Are Traceable",
    "Rubrics Are Case-Specific Review Authorities",
    "Evaluation Control And Run Data Are Separate",
    "The Cognitive Control Program Is The First Modification Seam",
)


def _glossary_record(text: str, name: str) -> str:
    match = re.search(
        rf"^\*\*{re.escape(name)}\*\*:\n(?P<body>.*?)(?=^\*\*|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None, f"missing canonical glossary record: {name}"
    return match.group(0)


def test_glossary_retains_evaluation_and_product_run_definitions_with_avoid_boundaries() -> None:
    text = CONTEXT_PATH.read_text(encoding="utf-8")

    for name in _GLOSSARY_RECORDS:
        assert "_Avoid_:" in _glossary_record(text, name), f"missing _Avoid_ boundary: {name}"

    review = _glossary_record(text, "Cognitive Evaluation Review")
    assert "Review Record" in review


def test_glossary_excludes_owned_design_and_dormant_status_sections() -> None:
    text = CONTEXT_PATH.read_text(encoding="utf-8")

    for name in _REMOVED_TAIL_SECTIONS:
        assert f"# {name}\n" not in text, f"retired glossary section remains: {name}"
