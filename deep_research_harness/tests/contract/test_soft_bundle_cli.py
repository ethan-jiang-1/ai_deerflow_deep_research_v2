"""Contract tests for the operator-only Soft Bundle CLI.

@impl SBC-001
@impl SBC-002
@impl SBC-003
@impl SBC-004
@impl SBC-005
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts import soft_bundle


def _args(**kwargs: object) -> SimpleNamespace:
    return SimpleNamespace(**kwargs)


def _patch_paths(tmp_path: Path):
    harness = tmp_path / "harness"
    harness.mkdir()
    runs = harness / ".deep-research-demo-runs" / "workspace"
    runs.mkdir(parents=True)
    soft_root = runs / "soft-bundles"
    soft_root.mkdir(parents=True)
    return patch.multiple(
        soft_bundle,
        HARNESS=harness,
        RUNS_ROOT=runs,
        DEFAULT_SOFT_BUNDLES_ROOT=soft_root,
    )


def test_create_is_idempotent(tmp_path: Path, capsys) -> None:
    with _patch_paths(tmp_path):
        first = soft_bundle.cmd_create(_args(root="demo", name="demo-name", question="q", mode="001"))
        out1 = capsys.readouterr().out
        second = soft_bundle.cmd_create(_args(root="demo", name="other", question="q", mode="001"))
        out2 = capsys.readouterr().out
        assert first == 0
        assert second == 0
        assert "soft_bundle_root=demo" in out1
        assert "soft_bundle_root=demo" in out2
        manifest = json.loads((tmp_path / "harness/demo/manifest.json").read_text())
        assert manifest["name"] == "demo-name"


def test_create_rejects_non_soft_bundle_directory(tmp_path: Path, capsys) -> None:
    with _patch_paths(tmp_path):
        bad = tmp_path / "harness" / "bad"
        bad.mkdir()
        (bad / "sentinel.txt").write_text("x")
        code = soft_bundle.cmd_create(_args(root="bad", name="n", question="q", mode="001"))
        assert code == 2
        assert "not a soft bundle directory" in capsys.readouterr().err


def test_bind_rejects_path_as_bundle_selector(tmp_path: Path) -> None:
    with _patch_paths(tmp_path):
        root = tmp_path / "harness" / "r"
        root.mkdir()
        (root / "manifest.json").write_text(json.dumps({"schema_version": 1, "name": "n", "mode": "001", "question": "", "current_bundle_id": None}))
        code = soft_bundle.cmd_bind(_args(root="r", bundle_id=".deep-research-demo-runs/workspace/deep-research/scopes/b_123456789012345678901234"))
        assert code == 2


def test_run_parses_bundle_id_and_binds(tmp_path: Path, capsys) -> None:
    with _patch_paths(tmp_path):
        root = tmp_path / "harness" / "r"
        root.mkdir()
        (root / "manifest.json").write_text(json.dumps({"schema_version": 1, "name": "n", "mode": "001", "question": "test", "current_bundle_id": None}))
        bundle_id = "b_123456789012345678901234"
        bundle_dir = tmp_path / "harness" / ".deep-research-demo-runs" / "workspace" / "deep-research" / "scopes" / "s_test" / bundle_id
        bundle_dir.mkdir(parents=True)
        (bundle_dir / "state.json").write_text(json.dumps({"execution_trace": ["bootstrap"], "phase": "x"}))
        fake_make = subprocess.CompletedProcess(args=[], returncode=0, stdout=f"Run Bundle: {bundle_id}\n", stderr="")
        with patch.object(soft_bundle, "_run_make", return_value=fake_make):
            code = soft_bundle.cmd_run(_args(root="r", question=None, mode="001"))
        assert code == 0
        manifest = json.loads((root / "manifest.json").read_text())
        assert manifest["current_bundle_id"] == bundle_id
        record = json.loads((root / "bundles" / f"{bundle_id}.json").read_text())
        assert record["bundle_local_path"].startswith(".deep-research-demo-runs/")
        assert "bound_bundle_id=" in capsys.readouterr().out


def test_path_prints_repository_relative_only(tmp_path: Path, capsys) -> None:
    with _patch_paths(tmp_path):
        root = tmp_path / "harness" / "r"
        root.mkdir()
        bundle_id = "b_123456789012345678901234"
        bundle_dir = tmp_path / "harness" / ".deep-research-demo-runs" / "workspace" / "deep-research" / "scopes" / "s_test" / bundle_id
        bundle_dir.mkdir(parents=True)
        (root / "manifest.json").write_text(json.dumps({"schema_version": 1, "name": "n", "mode": "001", "question": "", "current_bundle_id": bundle_id}))
        code = soft_bundle.cmd_path(_args(root="r"))
        out = capsys.readouterr().out.strip()
        assert code == 0
        assert not Path(out).is_absolute()
        assert out.startswith(".deep-research-demo-runs/")


def test_inspect_delegates_to_demo_sessions(tmp_path: Path) -> None:
    with _patch_paths(tmp_path):
        root = tmp_path / "harness" / "r"
        root.mkdir()
        bundle_id = "b_123456789012345678901234"
        (root / "manifest.json").write_text(json.dumps({"schema_version": 1, "name": "n", "mode": "001", "question": "", "current_bundle_id": bundle_id}))
        captured: list[list[str]] = []
        fake_make = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

        def _fake_run_make(args, env_extra=None):
            captured.append(args)
            return fake_make

        with patch.object(soft_bundle, "_run_make", side_effect=_fake_run_make):
            code = soft_bundle.cmd_inspect(_args(root="r"))
        assert code == 0
        assert captured and "demo-sessions" in captured[0]
        assert bundle_id in captured[0][-1]


def test_phases_reads_recorded_content(tmp_path: Path, capsys) -> None:
    with _patch_paths(tmp_path):
        root = tmp_path / "harness" / "r"
        root.mkdir()
        bundle_id = "b_123456789012345678901234"
        bundle_dir = tmp_path / "harness" / ".deep-research-demo-runs" / "workspace" / "deep-research" / "scopes" / "s_test" / bundle_id
        bundle_dir.mkdir(parents=True)
        (bundle_dir / "state.json").write_text(json.dumps({"execution_trace": ["bootstrap", "final_delivery"], "phase": "final_delivery", "phase_status": "terminal", "terminal_status": "completed"}))
        work = bundle_dir / "work" / "g0_wave0_w0000" / "g0_wave0_w0000_a00" / "outputs"
        work.mkdir(parents=True)
        (work / "fixture.json").write_text(json.dumps({"fixture_marker": "non_research_fixture"}))
        (root / "manifest.json").write_text(json.dumps({"schema_version": 1, "name": "n", "mode": "001", "question": "", "current_bundle_id": bundle_id}))
        code = soft_bundle.cmd_phases(_args(root="r"))
        out = capsys.readouterr().out
        assert code == 0
        assert "bootstrap -> final_delivery" in out
        assert "non_research_fixture" in out


def test_list_scans_only_soft_bundle_parent(tmp_path: Path, capsys) -> None:
    with _patch_paths(tmp_path):
        parent = tmp_path / "harness" / ".deep-research-demo-runs" / "workspace" / "soft-bundles"
        (parent / "a").mkdir()
        (parent / "a" / "manifest.json").write_text(json.dumps({"schema_version": 1}))
        (parent / "b").mkdir()
        (parent / "b" / "other.txt").write_text("x")
        code = soft_bundle.cmd_list(_args(under=None))
        out = capsys.readouterr().out
        assert code == 0
        assert ".deep-research-demo-runs/workspace/soft-bundles/a" in out
        assert "soft-bundles/b" not in out
