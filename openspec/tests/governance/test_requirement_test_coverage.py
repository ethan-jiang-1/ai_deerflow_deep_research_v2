"""Requirement-to-collected-test governance checker contracts.

@impl EVH-009
@impl EVH-010
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CHECKER = Path(__file__).resolve().parents[3] / "openspec" / "governance" / "check_project_req_coverage.py"


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(CHECKER), str(root)], capture_output=True, text=True, check=False)


def _project(tmp_path: Path) -> Path:
    _write(
        tmp_path,
        "openspec/governance/req-registry.yaml",
        "ABC-001: example — alpha\nABC-002: example — beta\n",
    )
    _write(tmp_path, "openspec/specs/example/spec.md", "> req: ABC-001, ABC-002\n")
    _write(
        tmp_path,
        "deep_research_harness/tests/unit/test_example.py",
        '"""@impl ABC-001, ABC-002"""\n\ndef test_example():\n    assert True\n',
    )
    return tmp_path


def test_valid_collected_requirement_coverage_passes(tmp_path: Path) -> None:
    result = _run(_project(tmp_path))
    assert result.returncode == 0, result.stderr


def test_openspec_governance_test_counts_as_coverage(tmp_path: Path) -> None:
    root = _project(tmp_path)
    (root / "deep_research_harness/tests/unit/test_example.py").write_text(
        '"""@impl ABC-001"""\n\ndef test_example(): pass\n', encoding="utf-8"
    )
    _write(
        root,
        "openspec/tests/governance/test_example.py",
        '"""@impl ABC-002"""\n\ndef test_example(): pass\n',
    )

    result = _run(root)

    assert result.returncode == 0, result.stderr


def test_unknown_test_requirement_fails(tmp_path: Path) -> None:
    root = _project(tmp_path)
    _write(
        root,
        "deep_research_harness/tests/unit/test_unknown.py",
        '"""@impl XYZ-999"""\n\ndef test_unknown(): pass\n',
    )
    result = _run(root)
    assert result.returncode == 1
    assert "unknown test requirement" in result.stderr
    assert "XYZ-999" in result.stderr


def test_alive_requirement_without_test_fails(tmp_path: Path) -> None:
    root = _project(tmp_path)
    (root / "deep_research_harness/tests/unit/test_example.py").write_text(
        '"""@impl ABC-001"""\n\ndef test_example(): pass\n', encoding="utf-8"
    )
    result = _run(root)
    assert result.returncode == 1
    assert "uncovered requirement" in result.stderr
    assert "ABC-002" in result.stderr


def test_active_delta_requirement_is_pending_and_does_not_require_main_spec_coverage(tmp_path: Path) -> None:
    root = _project(tmp_path)
    _write(
        root,
        "openspec/governance/req-registry.yaml",
        "ABC-001: example — alpha\nABC-002: example — beta\nABC-003: future — future\n",
    )
    _write(root, "openspec/changes/future/specs/future/spec.md", "> req: ABC-003\n")
    (root / "deep_research_harness/tests/unit/test_example.py").write_text(
        '"""@impl ABC-001, ABC-002"""\n\ndef test_example(): pass\n', encoding="utf-8"
    )

    result = _run(root)

    assert result.returncode == 0, result.stderr


def test_active_delta_declaration_does_not_remove_an_alive_requirement_from_coverage(tmp_path: Path) -> None:
    root = _project(tmp_path)
    _write(root, "openspec/changes/modify-example/specs/example/spec.md", "> req: ABC-001\n")
    (root / "deep_research_harness/tests/unit/test_example.py").write_text(
        '"""@impl ABC-002"""\n\ndef test_example(): pass\n', encoding="utf-8"
    )

    result = _run(root)

    assert result.returncode == 1
    assert "uncovered requirement: ABC-001" in result.stderr


def test_package_only_reference_does_not_count(tmp_path: Path) -> None:
    root = _project(tmp_path)
    _write(root, "deep_research_harness/tests/__init__.py", '"""@impl ABC-002"""\n')
    (root / "deep_research_harness/tests/unit/test_example.py").write_text(
        '"""@impl ABC-001"""\n\ndef test_example(): pass\n', encoding="utf-8"
    )
    result = _run(root)
    assert result.returncode == 1
    assert "ABC-002" in result.stderr


def _source(root: Path, content: str, *, name: str = "owned.py") -> None:
    _write(root, f"deep_research_harness/src/deerflow_deep_research/{name}", content)


def test_registered_production_docstrings_and_comments_pass(tmp_path: Path) -> None:
    root = _project(tmp_path)
    _source(
        root,
        '''"""@impl ABC-001"""


class Example:
    """@impl ABC-001"""

    def sync(self):
        """@impl ABC-001"""

    async def async_method(self):
        """@impl ABC-001"""


# @impl ABC-001
value = "ordinary text containing @impl XYZ-999"
''',
    )
    result = _run(root)
    assert result.returncode == 0, result.stderr


def test_unknown_production_annotation_fails_with_relative_location(tmp_path: Path) -> None:
    root = _project(tmp_path)
    _source(root, '"""@impl XYZ-999"""\n')
    result = _run(root)
    assert result.returncode == 1
    assert "unknown production requirement" in result.stderr
    assert "XYZ-999" in result.stderr
    assert "deep_research_harness/src/deerflow_deep_research/owned.py:" in result.stderr


def test_unallocated_harness_requirement_fails_closed(tmp_path: Path) -> None:
    root = _project(tmp_path)
    _write(
        root,
        "openspec/governance/req-registry.yaml",
        "ABC-001: example — alpha\nABC-002: example — beta\nDRH-001: harness — allocated\n",
    )
    _source(root, '"""@impl DRH-999"""\n', name="harness-detector-smoke.py")

    result = _run(root)

    assert result.returncode == 1
    assert "unknown production requirement" in result.stderr
    assert "DRH-999" in result.stderr
    assert "harness-detector-smoke.py" in result.stderr


def test_retired_production_annotation_fails_closed(tmp_path: Path) -> None:
    root = _project(tmp_path)
    _write(
        root,
        "openspec/governance/req-registry.yaml",
        "ABC-001: example — alpha\nABC-002: example — beta [DEPRECATED]\n",
    )
    _source(root, "# @impl ABC-002\n")
    result = _run(root)
    assert result.returncode == 1
    assert "retired production requirement" in result.stderr
    assert "ABC-002" in result.stderr


def test_invalid_production_source_fails_closed_with_relative_location(tmp_path: Path) -> None:
    root = _project(tmp_path)
    path = root / "deep_research_harness/src/deerflow_deep_research/broken.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"value = (\n")
    result = _run(root)
    assert result.returncode == 1
    assert "production source" in result.stderr
    assert "deep_research_harness/src/deerflow_deep_research/broken.py" in result.stderr


def test_invalid_source_encoding_fails_closed(tmp_path: Path) -> None:
    root = _project(tmp_path)
    path = root / "deep_research_harness/src/deerflow_deep_research/encoded.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"# coding: utf-8\n\xff\n")
    result = _run(root)
    assert result.returncode == 1
    assert "production source" in result.stderr
    assert "encoded.py" in result.stderr


def test_canonical_source_smoke_case_cannot_be_mis_scoped(tmp_path: Path) -> None:
    root = _project(tmp_path)
    _source(root, "# @impl XYZ-999\n", name="detector-smoke.py")
    result = _run(root)
    assert result.returncode == 1
    assert "XYZ-999" in result.stderr
    assert "detector-smoke.py" in result.stderr
