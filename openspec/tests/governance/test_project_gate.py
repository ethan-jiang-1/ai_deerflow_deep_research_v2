"""Focused stdlib tests for the OpenSpec root governance gate and the
selected-change scoped modes of the specification/requirement checkers.

Canonical maintained command, from the repository root:

    python3 -m unittest discover -s openspec/tests/governance

No CI or Makefile wiring exists for this suite; it is run by that command.

Most fixtures are built under temp directories and never mutate the
repository. The planted Focus Card negative invokes `check_change_guidance.py`
against an isolated temp copy of the required guidance/product/config/guide
inputs, with a planted active change that lacks a Focus Card; the real
repository is never written. Scripts under test are invoked as subprocesses
exactly like real callers do. The gate is loaded in-process via importlib with
an injected fake runner to prove invocation, explicit cwd, failure naming, and
exit propagation without a native `openspec` CLI.

@impl DRC-010
@impl EVH-005
@impl PRS-009
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GOVERNANCE_DIR = Path(__file__).resolve().parents[2] / "governance"
REPO_ROOT = Path(__file__).resolve().parents[3]
SPECS_CHECKER = GOVERNANCE_DIR / "check_project_specs.py"
REQS_CHECKER = GOVERNANCE_DIR / "check_project_reqs.py"
GATE = GOVERNANCE_DIR / "check_project_gate.py"


def _run(*arguments: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(argument) for argument in arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def _load_gate():
    spec = importlib.util.spec_from_file_location("check_project_gate", GATE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _make_repo(tmp: Path) -> Path:
    """Minimal repo fixture: registry + changes dir + governance checkers."""
    root = tmp / "repo"
    (root / "openspec" / "governance").mkdir(parents=True)
    (root / "openspec" / "changes").mkdir(parents=True)
    (root / "openspec" / "governance" / "req-registry.yaml").write_text(
        "# fixture registry\nEXI-001: execution-intent — Fixture requirement\n",
        encoding="utf-8",
    )
    # Copy the real component scripts so the gate's default inventory resolves.
    for name in (
        "check_project_reqs.py",
        "check_project_specs.py",
        "check_project_architecture.py",
        "check_change_guidance.py",
        "check_project_req_coverage.py",
        "check_harness_dependency_direction.py",
    ):
        source = GOVERNANCE_DIR / name
        if source.is_file():
            (root / "openspec" / "governance" / name).write_text(
                source.read_text(encoding="utf-8"), encoding="utf-8"
            )
    return root


def _write_change(root: Path, name: str, capability: str, header: str | None, title_line: str) -> Path:
    change_dir = root / "openspec" / "changes" / name
    spec_dir = change_dir / "specs" / capability
    spec_dir.mkdir(parents=True)
    spec = spec_dir / "spec.md"
    lines: list[str] = []
    if header is not None:
        lines.append(header)
    lines.append("")
    lines.append("## MODIFIED Requirements")
    lines.append("")
    lines.append(title_line)
    lines.append("")
    lines.append("The system SHALL keep behaving for the fixture. (`FIX-001`)")
    lines.append("")
    lines.append("#### Scenario: Existing scenario survives")
    lines.append("- **WHEN** the fixture runs")
    lines.append("- **THEN** it still behaves")
    spec.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return change_dir


class SpecsSelectedChangeModeTest(unittest.TestCase):
    def test_valid_delta_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            _write_change(root, "valid-change", "demo", "> req: DEM-001", "### Requirement: Demo behaves")
            result = _run(sys.executable, SPECS_CHECKER, root, "--change", "valid-change")
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_header_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            _write_change(root, "no-header", "demo", None, "### Requirement: Demo behaves")
            result = _run(sys.executable, SPECS_CHECKER, root, "--change", "no-header")
            self.assertEqual(result.returncode, 1)
            self.assertIn("Missing > req: header in delta spec", result.stderr)

    def test_title_embedded_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            _write_change(root, "title-id", "demo", "> req: DEM-001", "### Requirement: Demo behaves (DEM-001)")
            result = _run(sys.executable, SPECS_CHECKER, root, "--change", "title-id")
            self.assertEqual(result.returncode, 1)
            self.assertIn("Requirement title embeds a requirement ID", result.stderr)

    def test_missing_selected_change_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            result = _run(sys.executable, SPECS_CHECKER, root, "--change", "absent")
            self.assertEqual(result.returncode, 1)
            self.assertIn("Selected active change missing", result.stderr)

    def test_empty_change_without_specs_dir_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            (root / "openspec" / "changes" / "empty-change").mkdir(parents=True)
            result = _run(sys.executable, SPECS_CHECKER, root, "--change", "empty-change")
            self.assertEqual(result.returncode, 1)
            self.assertIn("has no delta spec files", result.stderr)

    def test_empty_change_with_empty_specs_dir_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            (root / "openspec" / "changes" / "empty-change" / "specs").mkdir(parents=True)
            result = _run(sys.executable, SPECS_CHECKER, root, "--change", "empty-change")
            self.assertEqual(result.returncode, 1)
            self.assertIn("has no delta spec files", result.stderr)

    def test_delta_less_change_with_skip_specs_true_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            change_dir = root / "openspec" / "changes" / "refactor"
            change_dir.mkdir(parents=True)
            (change_dir / ".openspec.yaml").write_text(
                "schema: spec-driven\nskip_specs: true\ncreated: 2026-09-12\n",
                encoding="utf-8",
            )
            result = _run(sys.executable, SPECS_CHECKER, root, "--change", "refactor")
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_delta_less_change_with_skip_specs_false_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            change_dir = root / "openspec" / "changes" / "refactor"
            change_dir.mkdir(parents=True)
            (change_dir / ".openspec.yaml").write_text(
                "schema: spec-driven\nskip_specs: false\n",
                encoding="utf-8",
            )
            result = _run(sys.executable, SPECS_CHECKER, root, "--change", "refactor")
            self.assertEqual(result.returncode, 1)
            self.assertIn("has no delta spec files", result.stderr)

    def test_delta_less_change_with_non_boolean_skip_specs_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            change_dir = root / "openspec" / "changes" / "refactor"
            change_dir.mkdir(parents=True)
            (change_dir / ".openspec.yaml").write_text(
                "schema: spec-driven\nskip_specs: yes\n",
                encoding="utf-8",
            )
            result = _run(sys.executable, SPECS_CHECKER, root, "--change", "refactor")
            self.assertEqual(result.returncode, 1)
            self.assertIn("unhonorable", result.stderr)
            self.assertIn(".openspec.yaml", result.stderr)

    def test_delta_less_change_without_known_schema_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            change_dir = root / "openspec" / "changes" / "refactor"
            change_dir.mkdir(parents=True)
            (change_dir / ".openspec.yaml").write_text("skip_specs: true\n", encoding="utf-8")
            result = _run(sys.executable, SPECS_CHECKER, root, "--change", "refactor")
            self.assertEqual(result.returncode, 1)
            self.assertIn("unhonorable", result.stderr)

    def test_fenced_fake_req_header_does_not_satisfy_req_trace(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            change_dir = root / "openspec" / "changes" / "fenced-only"
            spec_dir = change_dir / "specs" / "demo"
            spec_dir.mkdir(parents=True)
            # The only `> req:` line lives inside a fenced code block; it is
            # not a real declaration and must not satisfy the header rule.
            (spec_dir / "spec.md").write_text(
                "```markdown\n> req: DEM-001\n```\n\n"
                "## MODIFIED Requirements\n\n"
                "### Requirement: Demo behaves\n\nBody.\n",
                encoding="utf-8",
            )
            result = _run(sys.executable, SPECS_CHECKER, root, "--change", "fenced-only")
            self.assertEqual(result.returncode, 1)
            self.assertIn("Missing > req: header in delta spec", result.stderr)

    def test_default_full_mode_still_catches_unrelated_main_spec_violation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            # A healthy selected change does not mask a broken main spec.
            _write_change(root, "valid-change", "demo", "> req: DEM-001", "### Requirement: Demo behaves")
            main_spec = root / "openspec" / "specs" / "demo" / "spec.md"
            main_spec.parent.mkdir(parents=True)
            main_spec.write_text(
                "## Purpose\nFixture purpose.\n## Requirements\n\n### Requirement: Demo\nBody.\n",
                encoding="utf-8",
            )
            selected = _run(sys.executable, SPECS_CHECKER, root, "--change", "valid-change")
            self.assertEqual(selected.returncode, 0, selected.stderr)
            full = _run(sys.executable, SPECS_CHECKER, root)
            self.assertEqual(full.returncode, 1, "full mode must still catch unrelated main-spec drift")


class ReqsPlanningModeTest(unittest.TestCase):
    def test_legal_reservation_prints_and_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            _write_change(root, "new-change", "demo", "> req: DEM-001", "### Requirement: Demo behaves")
            result = _run(sys.executable, REQS_CHECKER, root, "--change", "new-change")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("reservation: DEM-001 (demo)", result.stdout)

    def test_same_capability_registered_is_already_assigned(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            _write_change(root, "uses-existing", "execution-intent", "> req: EXI-001", "### Requirement: Intent")
            result = _run(sys.executable, REQS_CHECKER, root, "--change", "uses-existing")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("already-assigned: EXI-001 (execution-intent)", result.stdout)
            self.assertNotIn("reservation:", result.stdout)

    def test_foreign_owner_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            _write_change(root, "wrong-owner", "other-capability", "> req: EXI-001", "### Requirement: Intent")
            result = _run(sys.executable, REQS_CHECKER, root, "--change", "wrong-owner")
            self.assertEqual(result.returncode, 1)
            self.assertIn("already-assigned ownership violation", result.stderr)
            self.assertIn("EXI-001", result.stderr)

    def test_retired_reuse_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            (root / "openspec" / "governance" / "req-registry.yaml").write_text(
                "OLD-001: demo — Old requirement [DEPRECATED: superseded]\n",
                encoding="utf-8",
            )
            _write_change(root, "reuses-retired", "demo", "> req: OLD-001", "### Requirement: Old behavior")
            result = _run(sys.executable, REQS_CHECKER, root, "--change", "reuses-retired")
            self.assertEqual(result.returncode, 1)
            self.assertIn("reused-retired", result.stderr)

    def test_collision_with_other_active_change_fails_foreign_capability(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            _write_change(root, "change-a", "cap-a", "> req: NEW-001", "### Requirement: A")
            _write_change(root, "change-b", "cap-b", "> req: NEW-001", "### Requirement: B")
            result = _run(sys.executable, REQS_CHECKER, root, "--change", "change-b")
            self.assertEqual(result.returncode, 1)
            self.assertIn("collision", result.stderr)
            self.assertIn("NEW-001", result.stderr)

    def test_collision_with_other_active_change_fails_same_capability(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            # Both deltas declare the same unregistered ID under the SAME
            # capability directory; grouping by capability alone would miss
            # this collision, so the scan must be keyed by (change, capability).
            _write_change(root, "change-a", "demo", "> req: NEW-001", "### Requirement: A")
            _write_change(root, "change-b", "demo", "> req: NEW-001", "### Requirement: B")
            result = _run(sys.executable, REQS_CHECKER, root, "--change", "change-b")
            self.assertEqual(result.returncode, 1)
            self.assertIn("collision", result.stderr)
            self.assertIn("NEW-001", result.stderr)
            self.assertIn("change-a (demo)", result.stderr)

    def test_selected_change_own_declaration_is_not_other_active(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            # Only one active change: its own declaration must be a reservation,
            # never reported as a collision with itself.
            _write_change(root, "solo", "demo", "> req: NEW-001", "### Requirement: Solo")
            result = _run(sys.executable, REQS_CHECKER, root, "--change", "solo")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("reservation: NEW-001 (demo)", result.stdout)

    def test_missing_selected_change_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            result = _run(sys.executable, REQS_CHECKER, root, "--change", "absent")
            self.assertEqual(result.returncode, 1)
            self.assertIn("not found", result.stderr)

    def test_default_full_mode_still_catches_unrelated_drift(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            _write_change(root, "valid-change", "demo", "> req: DEM-001", "### Requirement: Demo behaves")
            # An unrelated main spec header references an unregistered ID.
            main_spec = root / "openspec" / "specs" / "demo" / "spec.md"
            main_spec.parent.mkdir(parents=True)
            main_spec.write_text(
                "> req: GHOST-001\n\n## Purpose\nFixture.\n## Requirements\n\n### Requirement: Demo\nBody.\n",
                encoding="utf-8",
            )
            selected = _run(sys.executable, REQS_CHECKER, root, "--change", "valid-change")
            self.assertEqual(selected.returncode, 0, selected.stderr)
            full = _run(sys.executable, REQS_CHECKER, root)
            self.assertEqual(full.returncode, 1, "full mode must still catch unrelated global drift")


class GateCloseoutTest(unittest.TestCase):
    def test_closeout_runs_all_six_and_propagates_failures_with_explicit_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            gate = _load_gate()
            invoked: list[tuple[list[str], Path | None]] = []

            def fake_runner(arguments, cwd=None):
                invoked.append(([str(argument) for argument in arguments], cwd))
                script = str(arguments[1])
                code = 1 if script.endswith("check_project_architecture.py") else 0
                return code, ""

            code = gate.run_closeout(root, runner=fake_runner)
            self.assertEqual(code, 1)
            names = [arguments[1].split("/")[-1] for arguments, _ in invoked]
            for expected in (
                "check_project_reqs.py",
                "check_project_specs.py",
                "check_project_architecture.py",
                "check_change_guidance.py",
                "check_project_req_coverage.py",
                "check_harness_dependency_direction.py",
            ):
                self.assertIn(expected, names, f"{expected} must be invoked")
            self.assertTrue(
                all(cwd == root for _, cwd in invoked),
                "every closeout subprocess must run with explicit cwd=repo root",
            )

    def test_closeout_last_zero_cannot_mask_earlier_failure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            gate = _load_gate()

            # The LAST component exits 0, but an EARLIER component failed;
            # the aggregate exit code must still be 1.
            def fake_runner_last_zero(arguments, cwd=None):
                script = str(arguments[1])
                return (1 if script.endswith("check_project_specs.py") else 0), ""

            code = gate.run_closeout(root, runner=fake_runner_last_zero)
            self.assertEqual(code, 1)

    def test_closeout_all_zero_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            gate = _load_gate()
            code = gate.run_closeout(root, runner=lambda arguments, cwd=None: (0, ""))
            self.assertEqual(code, 0)

    def test_missing_checker_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            (root / "openspec" / "governance" / "check_change_guidance.py").unlink()
            gate = _load_gate()
            code = gate.run_closeout(root, runner=lambda arguments, cwd=None: (0, ""))
            self.assertEqual(code, 1)

    def test_unreadable_registry_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            registry = root / "openspec" / "governance" / "req-registry.yaml"
            registry.write_text("", encoding="utf-8")
            gate = _load_gate()
            code = gate.run_closeout(root, runner=lambda arguments, cwd=None: (0, ""))
            self.assertEqual(code, 1)

    def test_empty_inventory_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            gate = _load_gate()
            code = gate.run_closeout(root, runner=lambda arguments, cwd=None: (0, ""), checker_names=())
            self.assertEqual(code, 1)

    def test_runner_oserror_fails_closed_with_captured_result(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            gate = _load_gate()
            stdout, stderr = io.StringIO(), io.StringIO()

            def exploding_runner(arguments, cwd=None):
                raise OSError("simulated runner failure")

            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = gate.run_closeout(root, runner=exploding_runner)
            self.assertEqual(code, 1)
            self.assertIn("exit=126", stdout.getvalue())
            self.assertIn("simulated runner failure", stdout.getvalue())

    def test_runner_file_not_found_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            gate = _load_gate()
            stdout, stderr = io.StringIO(), io.StringIO()

            def not_found_runner(arguments, cwd=None):
                raise FileNotFoundError(arguments[0])

            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = gate.run_closeout(root, runner=not_found_runner)
            self.assertEqual(code, 1)
            self.assertIn("exit=127", stdout.getvalue())
            self.assertIn("command not found", stdout.getvalue())


class GatePlanTest(unittest.TestCase):
    def test_plan_sequences_owners_with_change_and_strict_and_explicit_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            gate = _load_gate()
            calls: list[tuple[list[str], Path | None]] = []

            def fake_runner(arguments, cwd=None):
                calls.append(([str(argument) for argument in arguments], cwd))
                return 0, ""

            code = gate.run_plan(root, "demo-change", runner=fake_runner)
            self.assertEqual(code, 0)
            self.assertEqual(len(calls), 4)
            # arguments layout: [python, <script>, ...args] / [openspec, validate, <name>, --strict]
            scripts = [arguments[1].split("/")[-1] for arguments, _ in calls]
            self.assertEqual(
                scripts,
                ["check_change_guidance.py", "check_project_specs.py", "check_project_reqs.py", "validate"],
            )
            self.assertEqual(calls[1][0][-2:], ["--change", "demo-change"])
            self.assertEqual(calls[2][0][-2:], ["--change", "demo-change"])
            self.assertEqual(calls[3][0][-3:], ["validate", "demo-change", "--strict"])
            self.assertTrue(
                all(cwd == root for _, cwd in calls),
                "every plan subprocess must run with explicit cwd=repo root",
            )

    def test_plan_missing_change_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            gate = _load_gate()
            code = gate.run_plan(root, "", runner=lambda arguments, cwd=None: (0, ""))
            self.assertEqual(code, 1)

    def test_plan_failure_propagates(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            gate = _load_gate()

            def fake_runner(arguments, cwd=None):
                script = str(arguments[1])
                code = 1 if script.endswith("check_project_specs.py") else 0
                return code, ""

            code = gate.run_plan(root, "demo-change", runner=fake_runner)
            self.assertEqual(code, 1)

    def test_plan_missing_focus_card_names_owner_and_output(self) -> None:
        # Orchestration propagation test with a SIMULATED owner failure (the
        # injected runner returns the Focus Card failure); the real planted
        # negative against check_change_guidance.py lives in
        # RealChangeGuidancePlantedNegativeTest below.
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            gate = _load_gate()
            stdout, stderr = io.StringIO(), io.StringIO()
            calls: list[tuple[list[str], Path | None]] = []
            focus_failure = (
                "focus.heading_missing: proposal.md has no `## Change Focus` section "
                "(first finding for the planted owner failure)"
            )

            def fake_runner(arguments, cwd=None):
                calls.append(([str(argument) for argument in arguments], cwd))
                script = str(arguments[1])
                if script.endswith("check_change_guidance.py"):
                    return 1, focus_failure
                return 0, ""

            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = gate.run_plan(root, "demo-change", runner=fake_runner)
            self.assertEqual(code, 1)
            # The gate must still run ALL plan owners even when one fails.
            self.assertEqual(len(calls), 4)
            self.assertIn("[change-guidance] exit=1", stdout.getvalue())
            self.assertIn("focus.heading_missing", stdout.getvalue())
            self.assertIn("first finding for the planted owner failure", stdout.getvalue())
            self.assertIn("OpenSpec planning admission failed", stderr.getvalue())

    def test_plan_strict_validation_failure_names_owner_and_output(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td))
            gate = _load_gate()
            stdout, stderr = io.StringIO(), io.StringIO()
            calls: list[tuple[list[str], Path | None]] = []
            strict_failure = (
                "MODIFIED requirement drops a surviving scenario: 'Existing scenario survives' "
                "missing from delta (conceptual dropped-surviving-scenario result)"
            )

            def fake_runner(arguments, cwd=None):
                calls.append(([str(argument) for argument in arguments], cwd))
                if str(arguments[0]) == "openspec":
                    return 1, strict_failure
                return 0, ""

            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = gate.run_plan(root, "demo-change", runner=fake_runner)
            self.assertEqual(code, 1)
            # All four plan owners still run; the failing strict-validation
            # owner is named with its captured output.
            self.assertEqual(len(calls), 4)
            self.assertIn("[strict-validation] exit=1", stdout.getvalue())
            self.assertIn("drops a surviving scenario", stdout.getvalue())
            self.assertIn("OpenSpec planning admission failed", stderr.getvalue())


class RealChangeGuidancePlantedNegativeTest(unittest.TestCase):
    """Real planted negative for a missing Focus Card, fully isolated in temp.

    `check_change_guidance.py` is a whole-tree validator with no isolated
    active-changes mode. This test builds an isolated temp copy of the exact
    real inputs the checker reads (guidance tree, product context, config,
    OpenSpec README, Harness guides/docs, checker + kernel), then plants one
    active change whose proposal lacks `## Change Focus`. The real repository
    is never written. If the real inputs ever drift, the checker fails on the
    real tree first and this test fails loudly rather than hiding that drift.
    """

    PLANTED_NAME = "_zz_governance_test_no_focus_card"
    _FIXTURE_SOURCES = (
        (REPO_ROOT / "openspec" / "change-guidance", "openspec/change-guidance"),
        (REPO_ROOT / "openspec" / "product", "openspec/product"),
        (REPO_ROOT / "openspec" / "README.md", "openspec/README.md"),
        (REPO_ROOT / "openspec" / "config.yaml", "openspec/config.yaml"),
        (
            REPO_ROOT / "openspec" / "governance" / "check_change_guidance.py",
            "openspec/governance/check_change_guidance.py",
        ),
        (
            REPO_ROOT / "openspec" / "governance" / "change_guidance_kernel.py",
            "openspec/governance/change_guidance_kernel.py",
        ),
        (REPO_ROOT / "deep_research_harness" / "AGENTS.md", "deep_research_harness/AGENTS.md"),
        (REPO_ROOT / "deep_research_harness" / "CLAUDE.md", "deep_research_harness/CLAUDE.md"),
        (REPO_ROOT / "deep_research_harness" / "README.md", "deep_research_harness/README.md"),
        (
            REPO_ROOT / "deep_research_harness" / "docs" / "README.md",
            "deep_research_harness/docs/README.md",
        ),
        (
            REPO_ROOT / "deep_research_harness" / "docs" / "runtime-architecture.md",
            "deep_research_harness/docs/runtime-architecture.md",
        ),
        (
            REPO_ROOT / "deep_research_harness" / "docs" / "local-operations.md",
            "deep_research_harness/docs/local-operations.md",
        ),
        (
            REPO_ROOT / "deep_research_harness" / "docs" / "testing-and-evaluation.md",
            "deep_research_harness/docs/testing-and-evaluation.md",
        ),
    )

    def _build_fixture(self, root: Path) -> None:
        for source, relative in self._FIXTURE_SOURCES:
            target = root / relative
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)

    def test_missing_focus_card_fails_real_checker(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            self._build_fixture(root)
            planted = root / "openspec" / "changes" / self.PLANTED_NAME
            planted.mkdir(parents=True)
            (planted / "proposal.md").write_text(
                "# Planted negative\n\nA proposal deliberately lacking `## Change Focus`.\n",
                encoding="utf-8",
            )
            checker = root / "openspec" / "governance" / "check_change_guidance.py"
            result = subprocess.run(
                [sys.executable, str(checker), str(root)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("focus.heading_missing", result.stderr)
            self.assertIn(self.PLANTED_NAME, result.stderr)


class NativeStrictValidationPlantedNegativeTest(unittest.TestCase):
    """Real native `openspec validate --strict` planted negative.

    A MODIFIED delta that drops a surviving scenario is rejected by the
    external CLI (verified against OpenSpec v1.9.0), which names the omitted
    scenario. The fixture is entirely temp-based and deterministic; the native
    CLI owns MODIFIED scenario completeness, and this test does not re-implement
    that rule.
    """

    def test_modified_delta_dropping_surviving_scenario_fails_strict(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            main_spec = root / "openspec" / "specs" / "demo" / "spec.md"
            main_spec.parent.mkdir(parents=True)
            main_spec.write_text(
                "> req: DEM-001\n\n"
                "## Purpose\nDemo fixture.\n\n"
                "## Requirements\n\n"
                "### Requirement: Demo behaves\n"
                "The system SHALL behave. (`DEM-001`)\n\n"
                "#### Scenario: Existing scenario one\n"
                "- **WHEN** the fixture runs\n"
                "- **THEN** it behaves one way\n\n"
                "#### Scenario: Existing scenario two\n"
                "- **WHEN** the fixture runs\n"
                "- **THEN** it behaves another way\n",
                encoding="utf-8",
            )
            change_dir = root / "openspec" / "changes" / "demo-change"
            (change_dir / "specs" / "demo").mkdir(parents=True)
            (change_dir / ".openspec.yaml").write_text(
                "schema: spec-driven\n", encoding="utf-8"
            )
            (change_dir / "proposal.md").write_text(
                "# Demo change\n\nMinimal proposal.\n", encoding="utf-8"
            )
            (change_dir / "design.md").write_text(
                "# Design\n\nMinimal design.\n", encoding="utf-8"
            )
            (change_dir / "tasks.md").write_text("- [ ] implement\n", encoding="utf-8")
            # MODIFIED block keeps only scenario one; scenario two is dropped.
            (change_dir / "specs" / "demo" / "spec.md").write_text(
                "> req: DEM-001\n\n"
                "## MODIFIED Requirements\n\n"
                "### Requirement: Demo behaves\n"
                "The system SHALL behave. (`DEM-001`)\n\n"
                "#### Scenario: Existing scenario one\n"
                "- **WHEN** the fixture runs\n"
                "- **THEN** it behaves one way\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                ["openspec", "validate", "demo-change", "--strict"],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            combined = (result.stdout or "") + (result.stderr or "")
            self.assertIn("Existing scenario two", combined)
            self.assertIn("omits scenario", combined)


if __name__ == "__main__":
    unittest.main()
