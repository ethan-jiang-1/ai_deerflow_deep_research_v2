"""Deterministic review-catalog generation and freshness checks.

@impl NPC-002
@impl PRS-011
"""

from __future__ import annotations

import os
import socket
from dataclasses import replace
from pathlib import Path

import pytest

from deerflow_deep_research.agents import factory as agent_factory
from deerflow_deep_research.graph.prompt_catalog import prompt_catalog_cases
from deerflow_deep_research.runtime import node_agent_bridge
from scripts import prompt_dump


@pytest.fixture
def catalog_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / ".node-prompt-review"
    monkeypatch.setattr(prompt_dump, "CATALOG_ROOT", root)
    return root


def _tree_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


def test_write_and_check_produce_a_stable_review_catalog(catalog_root: Path) -> None:
    expected = prompt_dump.render_catalog_files()

    assert tuple(expected) == tuple(sorted(expected))
    assert prompt_dump.write_catalog() == tuple(expected)
    assert prompt_dump.check_catalog() == tuple(expected)
    assert _tree_snapshot(catalog_root) == {path: content.encode("utf-8") for path, content in expected.items()}

    index = (catalog_root / "README.md").read_text(encoding="utf-8")
    case = (catalog_root / "hitl1" / "brief.md").read_text(encoding="utf-8")
    assert "generated review artifact" in index.lower()
    assert "not runtime authority" in index.lower()
    assert "## Requested Tool Policy" in case
    assert "runtime-resolved tool inventory" in case
    assert "/Users/" not in case
    assert "TAVILY_API_KEY" not in case


def test_default_catalog_root_is_the_hidden_local_review_workspace() -> None:
    assert prompt_dump.CATALOG_ROOT == prompt_dump.AGENT_ROOT / ".node-prompt-review"


def test_prompt_review_workspace_belongs_to_the_canonical_harness_root() -> None:
    """NPC-002: prompt review is local to the Harness and has no legacy-root alias."""
    assert prompt_dump.AGENT_ROOT.name == "deep_research_harness"


def test_check_missing_local_review_workspace_is_read_only(catalog_root: Path) -> None:
    assert not catalog_root.exists()

    with pytest.raises(prompt_dump.PromptDumpError, match="catalog_missing"):
        prompt_dump.check_catalog()

    assert not catalog_root.exists()


def test_fenced_literal_prompt_uses_a_delimiter_longer_than_its_content() -> None:
    prompt = "first line\n```` literal prompt text\nlast line\n"

    fenced = prompt_dump.fenced_literal_prompt(prompt)

    assert fenced == "`````\n" + prompt + "`````\n"


def test_catalog_refuses_case_paths_that_escape_the_fixed_root(
    catalog_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    unsafe_case = replace(prompt_catalog_cases()[0], case_id="../outside")
    monkeypatch.setattr(prompt_dump, "prompt_catalog_cases", lambda: (unsafe_case,))

    with pytest.raises(prompt_dump.PromptDumpError, match="catalog_path_invalid"):
        prompt_dump.render_catalog_files()

    assert not catalog_root.exists()
    assert not (catalog_root.parent / "outside.md").exists()


def test_check_is_read_only_and_write_only_cleans_obsolete_markdown(catalog_root: Path) -> None:
    prompt_dump.write_catalog()
    stale = catalog_root / "hitl1" / "brief.md"
    stale.write_text("stale generated output\n", encoding="utf-8")
    before_check = _tree_snapshot(catalog_root)

    with pytest.raises(prompt_dump.PromptDumpError, match="catalog_content_stale"):
        prompt_dump.check_catalog()

    assert _tree_snapshot(catalog_root) == before_check
    prompt_dump.write_catalog()
    stale.unlink()

    with pytest.raises(prompt_dump.PromptDumpError, match="catalog_tree_mismatch"):
        prompt_dump.check_catalog()

    prompt_dump.write_catalog()
    obsolete = catalog_root / "obsolete.md"
    obsolete.write_text("obsolete generated output\n", encoding="utf-8")

    with pytest.raises(prompt_dump.PromptDumpError, match="catalog_tree_mismatch"):
        prompt_dump.check_catalog()

    prompt_dump.write_catalog()
    assert not obsolete.exists()
    assert prompt_dump.check_catalog()


def test_check_and_write_refuse_unexpected_non_markdown_and_symlink_paths(
    catalog_root: Path,
) -> None:
    prompt_dump.write_catalog()
    unexpected = catalog_root / "operator-note.txt"
    unexpected.write_text("do not touch\n", encoding="utf-8")

    for operation in (prompt_dump.check_catalog, prompt_dump.write_catalog):
        with pytest.raises(prompt_dump.PromptDumpError, match="catalog_non_markdown_path"):
            operation()
    assert unexpected.read_text(encoding="utf-8") == "do not touch\n"

    unexpected.unlink()
    link = catalog_root / "link.md"
    try:
        os.symlink(catalog_root / "outside.md", link)
    except OSError as exc:
        pytest.skip(f"symlink fixture unavailable: {exc}")

    for operation in (prompt_dump.check_catalog, prompt_dump.write_catalog):
        with pytest.raises(prompt_dump.PromptDumpError, match="catalog_symlink"):
            operation()
    assert link.is_symlink()


def test_generation_does_not_construct_agents_resolve_tools_or_open_network(
    catalog_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("prompt catalog generation must remain pure")

    monkeypatch.setattr(agent_factory, "build_node_agent", forbidden)
    monkeypatch.setattr(node_agent_bridge, "_default_model_resolver", forbidden)
    monkeypatch.setattr(node_agent_bridge, "_default_tools_resolver", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)

    prompt_dump.write_catalog()
    assert prompt_dump.check_catalog()


def test_source_rendering_remains_available_without_a_local_review_workspace(catalog_root: Path) -> None:
    assert not catalog_root.exists()

    expected = prompt_dump.render_catalog_files()

    assert tuple(expected) == tuple(sorted(expected))
    assert not catalog_root.exists()
