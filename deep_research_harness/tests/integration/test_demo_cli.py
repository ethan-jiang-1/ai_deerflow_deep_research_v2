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
FIXTURE_SOURCE = AGENT_ROOT / "src_fake"


def _fixture_environment() -> dict[str, str]:
    existing_pythonpath = os.environ.get("PYTHONPATH")
    return os.environ | {
        "LANGGRAPH_STRICT_MSGPACK": "true",
        "PYTHONPATH": str(FIXTURE_SOURCE) + (os.pathsep + existing_pythonpath if existing_pythonpath else ""),
    }


def test_scripted_demo_traverses_scope_input_and_autonomous_terminal_fixture() -> None:
    result = subprocess.run(
        [sys.executable, str(AGENT_ROOT / "scripts/demo.py"), "--scripted"],
        cwd=AGENT_ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
        env=_fixture_environment(),
    )

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


def test_interactive_demo_completes_after_scope_without_a_hitl2_choice() -> None:
    """The fixed fixture graph uses the deterministic autonomous terminal route."""
    rendered_choice = "proceed: 按当前研究计划继续。"
    result = subprocess.run(
        [sys.executable, str(AGENT_ROOT / "scripts/demo.py")],
        cwd=AGENT_ROOT,
        check=False,
        capture_output=True,
        input="Use broad public sources\n",
        text=True,
        timeout=30,
        env=_fixture_environment(),
    )

    output = result.stdout
    assert result.returncode == 0, result.stderr
    assert "输入选项 ID:" not in output
    assert rendered_choice not in output
    assert output.count("确认研究配置") == 1
    assert "terminal: completed" in output
