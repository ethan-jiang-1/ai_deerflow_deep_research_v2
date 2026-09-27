"""Standalone fixture terminal demo smoke contract.

@impl DPL-002
@impl FCO-002
@impl RER-003
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SOURCE = AGENT_ROOT / "src_fixtures"


def _fixture_environment(bundle_root: Path) -> dict[str, str]:
    """Child environment pinned to its own demo workspace (BUG-072).

    The suite used to run the CLI against the ambient harness workspace, so a
    leftover non-terminal bundle there made these tests fail red for reasons that
    had nothing to do with the code under test.
    """
    existing_pythonpath = os.environ.get("PYTHONPATH")
    return os.environ | {
        "LANGGRAPH_STRICT_MSGPACK": "true",
        "DEERFLOW_DEMO_BUNDLE_ROOT": str(bundle_root),
        "PYTHONPATH": str(FIXTURE_SOURCE) + (os.pathsep + existing_pythonpath if existing_pythonpath else ""),
    }


def _ambient_bundle_dirs() -> set[str]:
    root = AGENT_ROOT / ".deep-research-demo-runs"
    if not root.is_dir():
        return set()
    return {path.name for path in root.rglob("b_*") if path.is_dir()}


def test_scripted_demo_traverses_scope_input_and_autonomous_terminal_fixture(tmp_path: Path) -> None:
    ambient_before = _ambient_bundle_dirs()
    bundle_root = tmp_path / "demo-runs"
    result = subprocess.run(
        [sys.executable, str(AGENT_ROOT / "scripts/demo.py"), "--scripted"],
        cwd=AGENT_ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
        env=_fixture_environment(bundle_root),
    )
    # Hermetic: the run lands in its own root and never touches the ambient one.
    assert any(path.is_dir() for path in bundle_root.rglob("b_*")), "the run ignored its injected root"
    assert _ambient_bundle_dirs() == ambient_before, "the suite wrote into the ambient demo workspace"

    output = result.stdout
    # The fixture graph proves the deterministic execution path through final delivery.
    assert "正在等待生命周期返回结果" in output
    assert "Run Bundle: b_" in output
    assert "确认研究配置" in output
    assert "输入选项 ID:" not in output
    assert "主题规划" in output
    assert "自主决策" in output
    assert "报告生成" in output
    # Terminal completion
    assert "terminal: completed" in output
    assert "Fixture-graph demo complete." in output
    assert "Blocked deserialization" not in result.stderr


def test_interactive_demo_completes_after_scope_without_a_hitl2_choice(tmp_path: Path) -> None:
    """The fixed fixture graph uses the deterministic autonomous terminal route."""
    rendered_choice = "proceed: 按当前研究计划继续。"
    bundle_root = tmp_path / "demo-runs"
    result = subprocess.run(
        [sys.executable, str(AGENT_ROOT / "scripts/demo.py")],
        cwd=AGENT_ROOT,
        check=False,
        capture_output=True,
        input="Use broad public sources\n",
        text=True,
        timeout=30,
        env=_fixture_environment(bundle_root),
    )

    output = result.stdout
    assert result.returncode == 0, result.stderr
    assert "输入选项 ID:" not in output
    assert rendered_choice not in output
    assert output.count("确认研究配置") == 1
    assert "terminal: completed" in output
