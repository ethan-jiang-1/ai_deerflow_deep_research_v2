"""Contract tests for the operator-only Soft Bundle CLI.

@impl SBC-001
@impl SBC-002
@impl SBC-003
@impl SBC-004
@impl SBC-005
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

# soft_bundle imports its sibling _inspect_view; make scripts/ importable here
# the same way test_demo_sessions does.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from deerflow_deep_research.domain.run_observation import RecordBearingLifecycleFact  # noqa: E402
from deerflow_deep_research.runtime.run_observation import RunObservationStore  # noqa: E402
from scripts import soft_bundle  # noqa: E402


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


def test_create_uses_simple_default_question(tmp_path: Path) -> None:
    with _patch_paths(tmp_path):
        code = soft_bundle.cmd_create(_args(root="default-q", name=None, question=None, mode="001"))
        assert code == 0
        manifest = json.loads((tmp_path / "harness/default-q/manifest.json").read_text())
        assert manifest["question"] == soft_bundle.DEFAULT_QUESTION


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
        (root / "manifest.json").write_text(
            json.dumps({"schema_version": 1, "name": "n", "mode": "001", "question": "", "current_bundle_id": None})
        )
        code = soft_bundle.cmd_bind(
            _args(
                root="r", bundle_id=".deep-research-demo-runs/workspace/deep-research/scopes/b_123456789012345678901234"
            )
        )
        assert code == 2


def test_run_parses_bundle_id_and_binds(tmp_path: Path, capsys) -> None:
    with _patch_paths(tmp_path):
        root = tmp_path / "harness" / "r"
        root.mkdir()
        (root / "manifest.json").write_text(
            json.dumps({"schema_version": 1, "name": "n", "mode": "001", "question": "test", "current_bundle_id": None})
        )
        bundle_id = "b_123456789012345678901234"
        bundle_dir = (
            tmp_path
            / "harness"
            / ".deep-research-demo-runs"
            / "workspace"
            / "deep-research"
            / "scopes"
            / "s_test"
            / bundle_id
        )
        bundle_dir.mkdir(parents=True)
        (bundle_dir / "state.json").write_text(json.dumps({"execution_trace": ["bootstrap"], "phase": "x"}))
        fake_make = subprocess.CompletedProcess(args=[], returncode=0, stdout=f"Run Bundle: {bundle_id}\n", stderr="")
        with (
            patch.object(soft_bundle, "_run_make", return_value=fake_make),
            patch.object(soft_bundle, "_clean_run_bundles"),
            patch.object(soft_bundle, "_verify_bundle", return_value=(True, [])),
        ):
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
        bundle_dir = (
            tmp_path
            / "harness"
            / ".deep-research-demo-runs"
            / "workspace"
            / "deep-research"
            / "scopes"
            / "s_test"
            / bundle_id
        )
        bundle_dir.mkdir(parents=True)
        (root / "manifest.json").write_text(
            json.dumps(
                {"schema_version": 1, "name": "n", "mode": "001", "question": "", "current_bundle_id": bundle_id}
            )
        )
        code = soft_bundle.cmd_path(_args(root="r"))
        out = capsys.readouterr().out.strip()
        assert code == 0
        assert not Path(out).is_absolute()
        assert out.startswith(".deep-research-demo-runs/")


def test_inspect_delegates_to_demo_sessions(tmp_path: Path, capsys) -> None:
    with _patch_paths(tmp_path):
        root = tmp_path / "harness" / "r"
        root.mkdir()
        bundle_id = "b_123456789012345678901234"
        (root / "manifest.json").write_text(
            json.dumps(
                {"schema_version": 1, "name": "n", "mode": "001", "question": "", "current_bundle_id": bundle_id}
            )
        )
        captured: list[list[str]] = []
        fake_make = subprocess.CompletedProcess(args=[], returncode=0, stdout=f"Run Bundle: {bundle_id}\n", stderr="")

        def _fake_run_make(args, env_extra=None):
            captured.append(args)
            return fake_make

        with patch.object(soft_bundle, "_run_make", side_effect=_fake_run_make):
            code = soft_bundle.cmd_inspect(_args(root="r"))
        assert code == 0
        assert captured and "demo-sessions" in captured[0]
        assert bundle_id in captured[0][-1]
        assert f"Run Bundle: {bundle_id}" in capsys.readouterr().out


def test_inspect_mode_002_renders_recorded_diagnostics(tmp_path: Path, capsys) -> None:
    with _patch_paths(tmp_path):
        root = tmp_path / "harness" / "r"
        root.mkdir()
        bundle_id = "b_" + "A" * 43
        bundle_dir = (
            tmp_path
            / "harness"
            / ".deep-research-demo-runs"
            / "workspace"
            / "scripted-real"
            / "run-test"
            / "deep-research"
            / "scopes"
            / "s_test"
            / bundle_id
        )
        bundle_dir.mkdir(parents=True)
        asyncio.run(
            RunObservationStore(bundle_root=bundle_dir, bundle_id=bundle_id).publish(
                RecordBearingLifecycleFact(
                    bundle_id=bundle_id,
                    action="status",
                    status="suspended",
                    phase="bootstrap",
                    generation=0,
                    durability="restart_durable",
                )
            )
        )
        (root / "manifest.json").write_text(
            json.dumps(
                {"schema_version": 1, "name": "n", "mode": "002", "question": "", "current_bundle_id": bundle_id}
            )
        )
        code = soft_bundle.cmd_inspect(_args(root="r"))
        out = capsys.readouterr().out
        assert code == 0
        assert "Observed summary: suspended@bootstrap generation 0" in out
        assert "Journal health: complete" in out
        assert "Event Journal is read-only; lifecycle controls remain independent." in out


def test_inspect_mode_002_missing_bundle_is_unavailable(tmp_path: Path, capsys) -> None:
    with _patch_paths(tmp_path):
        root = tmp_path / "harness" / "r"
        root.mkdir()
        bundle_id = "b_" + "A" * 43
        (root / "manifest.json").write_text(
            json.dumps(
                {"schema_version": 1, "name": "n", "mode": "002", "question": "", "current_bundle_id": bundle_id}
            )
        )
        code = soft_bundle.cmd_inspect(_args(root="r"))
        out = capsys.readouterr().out
        assert code == 2
        assert "unavailable for safe inspection" in out


def test_phases_reads_recorded_content(tmp_path: Path, capsys) -> None:
    with _patch_paths(tmp_path):
        root = tmp_path / "harness" / "r"
        root.mkdir()
        bundle_id = "b_123456789012345678901234"
        bundle_dir = (
            tmp_path
            / "harness"
            / ".deep-research-demo-runs"
            / "workspace"
            / "deep-research"
            / "scopes"
            / "s_test"
            / bundle_id
        )
        bundle_dir.mkdir(parents=True)
        (bundle_dir / "state.json").write_text(
            json.dumps(
                {
                    "execution_trace": ["bootstrap", "final_delivery"],
                    "phase": "final_delivery",
                    "phase_status": "terminal",
                    "terminal_status": "completed",
                }
            )
        )
        work = bundle_dir / "work" / "g0_wave0_w0000" / "g0_wave0_w0000_a00" / "outputs"
        work.mkdir(parents=True)
        (work / "fixture.json").write_text(json.dumps({"fixture_marker": "non_research_fixture"}))
        (root / "manifest.json").write_text(
            json.dumps(
                {"schema_version": 1, "name": "n", "mode": "001", "question": "", "current_bundle_id": bundle_id}
            )
        )
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


def test_clean_removes_prior_run_bundles(tmp_path: Path, capsys) -> None:
    with _patch_paths(tmp_path):
        bundle_dir = (
            tmp_path
            / "harness"
            / ".deep-research-demo-runs"
            / "workspace"
            / "deep-research"
            / "scopes"
            / "s_test"
            / "b_123456789012345678901234"
        )
        bundle_dir.mkdir(parents=True)
        (bundle_dir / "state.json").write_text("{}")
        code = soft_bundle.cmd_clean(_args())
        assert code == 0
        assert not bundle_dir.exists()
        assert "cleaned run bundles" in capsys.readouterr().out


def test_run_cleans_prior_bundles_before_make(tmp_path: Path) -> None:
    with _patch_paths(tmp_path):
        root = tmp_path / "harness" / "r"
        root.mkdir()
        (root / "manifest.json").write_text(
            json.dumps({"schema_version": 1, "name": "n", "mode": "001", "question": "", "current_bundle_id": None})
        )
        old_bundle = (
            tmp_path
            / "harness"
            / ".deep-research-demo-runs"
            / "workspace"
            / "deep-research"
            / "scopes"
            / "s_old"
            / "b_123456789012345678901234"
        )
        old_bundle.mkdir(parents=True)
        (old_bundle / "state.json").write_text("{}")
        fake_make = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="Run Bundle: b_223456789012345678901234\n", stderr=""
        )
        new_bundle = (
            tmp_path
            / "harness"
            / ".deep-research-demo-runs"
            / "workspace"
            / "deep-research"
            / "scopes"
            / "s_new"
            / "b_223456789012345678901234"
        )
        with (
            patch.object(soft_bundle, "_run_make", return_value=fake_make),
            patch.object(soft_bundle, "_find_bundle_dir", return_value=new_bundle),
            patch.object(soft_bundle, "_verify_bundle", return_value=(True, [])),
        ):
            code = soft_bundle.cmd_run(_args(root="r", question=None, mode="001"))
        assert code == 0
        assert not old_bundle.exists()


def test_run_mode_002_parses_journal_path_and_binds(tmp_path: Path, capsys) -> None:
    with _patch_paths(tmp_path):
        root = tmp_path / "harness" / "r"
        root.mkdir()
        (root / "manifest.json").write_text(
            json.dumps({"schema_version": 1, "name": "n", "mode": "002", "question": "", "current_bundle_id": None})
        )
        bundle_id = "b_123456789012345678901234"
        bundle_dir = (
            tmp_path
            / "harness"
            / ".deep-research-demo-runs"
            / "workspace"
            / "scripted-real"
            / "run-test"
            / "deep-research"
            / "scopes"
            / "s_test"
            / bundle_id
        )
        bundle_dir.mkdir(parents=True)
        (bundle_dir / "final").mkdir()
        (bundle_dir / "final" / "report.md").write_text("# Report")
        journal = bundle_dir / "diagnostics" / "events.jsonl"
        journal.parent.mkdir()
        journal.write_text("")
        output = f"bundle_id:        {bundle_id}\nevent journal:    {journal}\n"
        fake_make = subprocess.CompletedProcess(args=[], returncode=0, stdout=output, stderr="")
        with (
            patch.object(soft_bundle, "_run_make", return_value=fake_make),
            patch.object(soft_bundle, "_verify_bundle", return_value=(True, [])),
            patch.object(soft_bundle, "_clean_run_bundles"),
        ):
            code = soft_bundle.cmd_run(_args(root="r", question=None, mode="002"))
        assert code == 0
        manifest = json.loads((root / "manifest.json").read_text())
        assert manifest["current_bundle_id"] == bundle_id
        assert "bound_bundle_id=" in capsys.readouterr().out


def test_run_mode_003_binds_the_real_auto_bundle(tmp_path: Path, capsys) -> None:
    """@impl SBC-004"""
    with _patch_paths(tmp_path):
        root = tmp_path / "harness" / "r"
        root.mkdir()
        (root / "manifest.json").write_text(
            json.dumps({"schema_version": 1, "name": "n", "mode": "003", "question": "", "current_bundle_id": None})
        )
        bundle_id = "b_123456789012345678901234"
        bundle_dir = (
            tmp_path
            / "harness"
            / ".deep-research-demo-runs"
            / "workspace"
            / "deep-research"
            / "scopes"
            / "s_test"
            / bundle_id
        )
        bundle_dir.mkdir(parents=True)
        fake_make = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=f"Run Bundle: {bundle_id}\n", stderr=""
        )
        with (
            patch.object(soft_bundle, "_run_make", return_value=fake_make) as fake_make_call,
            patch.object(soft_bundle, "_clean_run_bundles"),
            patch.object(soft_bundle, "_verify_bundle", return_value=(True, [])),
        ):
            code = soft_bundle.cmd_run(_args(root="r", question=None, mode="003"))
            assert code == 0
            assert fake_make_call.call_args.args[0][1] == "demo-real-scripted"
            demo_args = fake_make_call.call_args.args[0][2]
            assert demo_args.startswith('DEMO_ARGS=--question "What is one bounded fact about')
        manifest = json.loads((root / "manifest.json").read_text())
        assert manifest["current_bundle_id"] == bundle_id
        assert manifest["question"] == soft_bundle.MODE_QUESTIONS["003"]
        out = capsys.readouterr().out
        assert "bound_bundle_id=" in out
        assert "RESULT: PASS" in out


def test_inspect_mode_003_renders_recorded_diagnostics(tmp_path: Path, capsys) -> None:
    """@impl SBC-004"""
    with _patch_paths(tmp_path):
        root = tmp_path / "harness" / "r"
        root.mkdir()
        bundle_id = "b_" + "A" * 43
        bundle_dir = (
            tmp_path
            / "harness"
            / ".deep-research-demo-runs"
            / "workspace"
            / "deep-research"
            / "scopes"
            / "s_test"
            / bundle_id
        )
        bundle_dir.mkdir(parents=True)
        asyncio.run(
            RunObservationStore(bundle_root=bundle_dir, bundle_id=bundle_id).publish(
                RecordBearingLifecycleFact(
                    bundle_id=bundle_id,
                    action="status",
                    status="suspended",
                    phase="bootstrap",
                    generation=0,
                    durability="restart_durable",
                )
            )
        )
        (root / "manifest.json").write_text(
            json.dumps(
                {"schema_version": 1, "name": "n", "mode": "003", "question": "", "current_bundle_id": bundle_id}
            )
        )
        code = soft_bundle.cmd_inspect(_args(root="r"))
        out = capsys.readouterr().out
        assert code == 0
        assert "Observed summary: suspended@bootstrap generation 0" in out
        assert "Journal health: complete" in out
        assert "Event Journal is read-only; lifecycle controls remain independent." in out


def test_verify_mode_003_requires_report(tmp_path: Path, capsys) -> None:
    """@impl SBC-004"""
    with _patch_paths(tmp_path):
        root = tmp_path / "harness" / "r"
        root.mkdir()
        bundle_id = "b_123456789012345678901234"
        bundle_dir = (
            tmp_path
            / "harness"
            / ".deep-research-demo-runs"
            / "workspace"
            / "deep-research"
            / "scopes"
            / "s_test"
            / bundle_id
        )
        bundle_dir.mkdir(parents=True)
        (bundle_dir / "state.json").write_text(
            json.dumps(
                {
                    "terminal_status": "completed",
                    "phase_status": "terminal",
                    "phase": "final_delivery",
                    "execution_trace": list(soft_bundle.REQUIRED_TRACE),
                }
            )
        )
        diag = bundle_dir / "diagnostics"
        diag.mkdir()
        events = []
        for phase in soft_bundle.REQUIRED_TRACE:
            events.append({"category": "node", "outcome": "completed", "phase": phase})
        events.append({"category": "terminal", "outcome": "completed", "phase": "final_delivery"})
        (diag / "events.jsonl").write_text("\n".join(json.dumps(e) for e in events) + "\n")
        (root / "manifest.json").write_text(
            json.dumps(
                {"schema_version": 1, "name": "n", "mode": "003", "question": "", "current_bundle_id": bundle_id}
            )
        )
        code = soft_bundle.cmd_verify(_args(root="r"))
        err = capsys.readouterr().err
        assert code == 1
        assert "RESULT: FAIL" in err
        assert "003 should publish final/report.md" in err


def test_verify_reports_pass(tmp_path: Path, capsys) -> None:
    with _patch_paths(tmp_path):
        root = tmp_path / "harness" / "r"
        root.mkdir()
        bundle_id = "b_123456789012345678901234"
        bundle_dir = (
            tmp_path
            / "harness"
            / ".deep-research-demo-runs"
            / "workspace"
            / "deep-research"
            / "scopes"
            / "s_test"
            / bundle_id
        )
        bundle_dir.mkdir(parents=True)
        (bundle_dir / "state.json").write_text(
            json.dumps(
                {
                    "terminal_status": "completed",
                    "phase_status": "terminal",
                    "phase": "final_delivery",
                    "execution_trace": list(soft_bundle.REQUIRED_TRACE),
                }
            )
        )
        diag = bundle_dir / "diagnostics"
        diag.mkdir()
        (diag / "run-summary.json").write_text(
            json.dumps(
                {
                    "status": "completed",
                    "terminal_outcome": "completed",
                    "journal_availability": "complete",
                }
            )
        )
        events = []
        for phase in soft_bundle.REQUIRED_TRACE:
            events.append({"category": "node", "outcome": "completed", "phase": phase})
        events.append({"category": "terminal", "outcome": "completed", "phase": "final_delivery"})
        (diag / "events.jsonl").write_text("\n".join(json.dumps(e) for e in events) + "\n")
        (root / "manifest.json").write_text(
            json.dumps(
                {"schema_version": 1, "name": "n", "mode": "001", "question": "", "current_bundle_id": bundle_id}
            )
        )
        code = soft_bundle.cmd_verify(_args(root="r"))
        out = capsys.readouterr().out
        assert code == 0
        assert "RESULT: PASS" in out


def test_verify_reports_fail(tmp_path: Path, capsys) -> None:
    with _patch_paths(tmp_path):
        root = tmp_path / "harness" / "r"
        root.mkdir()
        bundle_id = "b_123456789012345678901234"
        bundle_dir = (
            tmp_path
            / "harness"
            / ".deep-research-demo-runs"
            / "workspace"
            / "deep-research"
            / "scopes"
            / "s_test"
            / bundle_id
        )
        bundle_dir.mkdir(parents=True)
        (bundle_dir / "state.json").write_text(
            json.dumps(
                {
                    "terminal_status": "blocked",
                    "phase_status": "terminal",
                    "phase": "final_delivery",
                    "execution_trace": list(soft_bundle.REQUIRED_TRACE),
                }
            )
        )
        (root / "manifest.json").write_text(
            json.dumps(
                {"schema_version": 1, "name": "n", "mode": "001", "question": "", "current_bundle_id": bundle_id}
            )
        )
        code = soft_bundle.cmd_verify(_args(root="r"))
        err = capsys.readouterr().err
        assert code == 1
        assert "RESULT: FAIL" in err
