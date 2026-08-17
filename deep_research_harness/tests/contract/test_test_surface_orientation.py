"""Test-surface orientation documentation contracts.

Contracts derive expected facts from the filesystem, conftest, and marker
registration instead of hardcoding a second catalog.

@impl EVH-009
@impl EVH-031
"""

from __future__ import annotations

from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[2]
DOC = AGENT_ROOT / "docs" / "testing-and-evaluation.md"
CONFTEST = AGENT_ROOT / "tests" / "conftest.py"
TEST_ROOT = AGENT_ROOT / "tests"
FIXTURES = AGENT_ROOT / "tests" / "fixtures"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_taxonomy_documentation_covers_existing_top_level_directories() -> None:
    """The testing doc names every current top-level test directory."""
    doc = _text(DOC)
    existing = sorted(
        entry.name
        for entry in TEST_ROOT.iterdir()
        if entry.is_dir() and not entry.name.startswith(".") and entry.name != "__pycache__"
    )
    missing = [name for name in existing if name not in doc]
    assert not missing, f"test directories missing from the documented taxonomy: {missing}"


def test_network_denial_and_marker_exceptions_are_disclosed() -> None:
    """The doc discloses the autouse network denial and its marker exceptions."""
    doc = _text(DOC)
    conftest = _text(CONFTEST)
    assert "_deny_public_network" in conftest
    assert "requires_llm" in conftest and "release_e2e" in conftest
    assert "network" in doc.lower() or "网络" in doc
    assert "requires_llm" in doc and "release_e2e" in doc


def test_fixtures_helper_status_is_disclosed() -> None:
    """tests/fixtures/ is documented as helpers, and really contains no pytest fixtures."""
    doc = _text(DOC)
    assert "fixtures" in doc.lower() or "Fixtures" in doc
    assert any(word in doc for word in ("helper", "helpers", "不是 pytest fixture"))
    assert not any(_text(path).count("@pytest.fixture") for path in FIXTURES.glob("*.py"))
