"""Deterministic contracts for the permanent project-structure governance gate.

@impl PRS-004
@impl PRS-001
@impl PRS-006
@impl PRS-009
@impl PRS-011
@impl PRS-017
@impl PRS-018
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
CHECKER = REPO_ROOT / "openspec" / "governance" / "check_project_architecture.py"
MANIFEST_PATH = Path("openspec/governance/project-structure.toml")
ACTIVE_SPEC_PATH = Path("openspec/changes/change-00/specs/project-structure/spec.md")
MAIN_SPEC_PATH = Path("openspec/specs/project-structure/spec.md")
ARCHIVED_SPEC_PATH = Path("openspec/changes/archive/change-00/specs/project-structure/spec.md")
GUIDE_PATH = Path("deep_research_harness/AGENTS.md")
BEGIN_MARKER = "<!-- BEGIN GENERATED: PROJECT-STRUCTURE -->"
END_MARKER = "<!-- END GENERATED: PROJECT-STRUCTURE -->"
NODE_ROOT = "deep_research_harness/src/deerflow_deep_research/graph/nodes"


def test_canonical_harness_root_is_the_only_tracked_downstream_root() -> None:
    """PRS-017: structural consumers have one canonical Harness root."""
    assert (REPO_ROOT / "deep_research_harness").is_dir()
    assert not (REPO_ROOT / "deerflow_research").exists()


VALID_MANIFEST = """\
schema_version = 1
contract = "project-structure"
requirement_ids = ["PRS-001", "PRS-002", "PRS-003", "PRS-004", "PRS-006", "PRS-009", "PRS-011", "PRS-018"]

[upstream_gitlink]
path = "deerflow"
commit = "0000000000000000000000000000000000000000"

[package]
source_root = "deep_research_harness/src/deerflow_deep_research"
fixture_root = "deep_research_harness/src_fake/deerflow_deep_research_fixtures"
fixture_package = "deerflow_deep_research_fixtures"
test_root = "deep_research_harness/tests"
ownership_layers = ["runtime", "domain", "engine", "agents", "graph"]
forbidden_source_roots = ["backend", "frontend"]
forbidden_shared_modules = ["utils", "helpers", "common"]

[fixture_imports]
production_contracts = ["deerflow_deep_research.domain.models"]
external_namespaces = ["pydantic", "langgraph"]
recipe_class = "deerflow_deep_research.runtime.research.ResearchGraphRecipe"
recipe_factories = ["from_adapters"]

[ignored_paths]
path = "deep_research_harness/.gitignore"
entries = [".deep-research-demo-runs/", ".reports/", ".pytest_cache/", ".ruff_cache/", ".node-prompt-review/"]

[[required_paths]]
path = "deep_research_harness/pyproject.toml"
kind = "file"
owner = "PRS-001"

[[required_paths]]
path = "deep_research_harness/src/deerflow_deep_research"
kind = "directory"
owner = "PRS-001"

[[required_paths]]
path = "deep_research_harness/src_fake/deerflow_deep_research_fixtures"
kind = "directory"
owner = "PRS-001"

[[required_paths]]
path = "deep_research_harness/tests"
kind = "directory"
owner = "PRS-001"

[[required_paths]]
path = "deep_research_harness/.gitignore"
kind = "file"
owner = "PRS-006"

[[required_paths]]
path = "deep_research_harness/docs"
kind = "directory"
owner = "PRS-009"

[[required_paths]]
path = "deep_research_harness/docs/README.md"
kind = "file"
owner = "PRS-009"

[[required_paths]]
path = "deep_research_harness/docs/runtime-architecture.md"
kind = "file"
owner = "PRS-009"

[[required_paths]]
path = "deep_research_harness/docs/local-operations.md"
kind = "file"
owner = "PRS-009"

[[required_paths]]
path = "deep_research_harness/docs/testing-and-evaluation.md"
kind = "file"
owner = "PRS-009"

[[required_paths]]
path = "openspec/governance/test-evidence-policy.md"
kind = "file"
owner = "PRS-004"

[[required_paths]]
path = "openspec/README.md"
kind = "file"
owner = "PRS-009"

[[required_paths]]
path = "openspec/product"
kind = "directory"
owner = "PRS-009"

[[required_paths]]
path = "openspec/product/README.md"
kind = "file"
owner = "PRS-009"

[[required_paths]]
path = "openspec/change-guidance"
kind = "directory"
owner = "PRS-009"

[[required_paths]]
path = "openspec/change-guidance/README.md"
kind = "file"
owner = "PRS-009"

[[required_paths]]
path = "openspec/change-guidance/core/change-practice.md"
kind = "file"
owner = "PRS-009"

[[required_paths]]
path = "openspec/change-guidance/profiles/node-agent/node-agent.md"
kind = "file"
owner = "PRS-009"

[[required_paths]]
path = "openspec/change-guidance/local"
kind = "directory"
owner = "PRS-009"

[[required_paths]]
path = "openspec/governance/selected-change-closeout.md"
kind = "file"
owner = "PRS-009"

[[required_paths]]
path = "openspec/governance/selected-change-closeout.py"
kind = "file"
owner = "PRS-009"

[imports]
domain = ["stdlib", "pydantic"]
engine = ["domain"]
agents = ["domain", "deerflow", "langchain"]
graph = ["domain", "engine", "nodes", "langgraph"]
nodes = ["domain", "engine", "langgraph"]
runtime = ["domain", "graph", "agents", "deerflow", "httpx", "httpx_sse", "langchain", "langgraph", "openai"]

[node_packages]
root = "deep_research_harness/src/deerflow_deep_research/graph/nodes"
required_files = ["__init__.py", "node.py", "contracts.py"]
optional_files = ["subgraph.py"]
forbidden_files = ["fake.py"]
public_export = "NODE_SPEC"
"""

SPEC_TEXT = """\
> req: PRS-001, PRS-002, PRS-003, PRS-004, PRS-006, PRS-009, PRS-011, PRS-018
> structure: openspec/governance/project-structure.toml

## ADDED Requirements

### Requirement: Structural authority survives change archival
The owning spec normatively identifies the permanent structure registry.
"""

MAIN_SPEC_TEXT = SPEC_TEXT.replace("## ADDED Requirements", "## Purpose\n\nFixture.\n\n## Requirements")

REGISTRY_TEXT = """\
prefixes:
  PRS: project-structure

PRS-001: project-structure - package ownership
PRS-002: project-structure - imports
PRS-003: project-structure - node surface
PRS-004: project-structure - durable authority
PRS-006: project-structure - ignored local generated paths
PRS-009: project-structure - Deep Research charter and human documentation
PRS-011: project-structure - prompt catalog structure
PRS-018: project-structure - metadata-only upstream gitlink boundary
"""

def _write(root: Path, relative_path: Path | str, content: str = "") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _replace(root: Path, relative_path: Path | str, old: str, new: str) -> None:
    path = root / relative_path
    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


def _git(root: Path, *arguments: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=False,
        capture_output=True,
        input=input_text,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"temporary Git fixture command failed: {result.stderr}")
    return result


def _configure_temporary_git_repository(root: Path) -> None:
    _git(root, "config", "user.name", "architecture-fixture")
    _git(root, "config", "user.email", "architecture-fixture@example.invalid")


def _initialize_gitlink_fixture(root: Path) -> str:
    _git(root, "init", "--quiet")
    _configure_temporary_git_repository(root)
    _git(root, "commit", "--allow-empty", "--quiet", "-m", "parent fixture")

    nested = root / "deerflow"
    nested.mkdir()
    _git(nested, "init", "--quiet")
    _configure_temporary_git_repository(nested)
    _git(nested, "commit", "--allow-empty", "--quiet", "-m", "nested fixture")
    commit = _git(nested, "rev-parse", "--verify", "HEAD").stdout.strip()
    _stage_gitlink(root, commit)
    return commit


def _stage_gitlink(root: Path, commit: str, *, mode: str = "160000") -> None:
    _git(root, "update-index", "--add", "--cacheinfo", f"{mode},{commit},deerflow")


def _set_gitlink_lock(root: Path, commit: str) -> None:
    manifest_path = root / MANIFEST_PATH
    manifest = manifest_path.read_text(encoding="utf-8")
    start = manifest.index('commit = "', manifest.index("[upstream_gitlink]"))
    end = manifest.index("\n", start)
    manifest_path.write_text(manifest[:start] + f'commit = "{commit}"' + manifest[end:], encoding="utf-8")


def _commit_nested_probe(root: Path) -> str:
    nested = root / "deerflow"
    (nested / "boundary-probe.txt").write_text("clean\n", encoding="utf-8")
    _git(nested, "add", "boundary-probe.txt")
    _git(nested, "commit", "--quiet", "-m", "tracked probe")
    commit = _git(nested, "rev-parse", "--verify", "HEAD").stdout.strip()
    _stage_gitlink(root, commit)
    _set_gitlink_lock(root, commit)
    return commit


class ArchitectureGovernanceContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary.name)
        _write(self.root, MANIFEST_PATH, VALID_MANIFEST)
        _write(self.root, "openspec/governance/req-registry.yaml", REGISTRY_TEXT)
        _write(self.root, "openspec/governance/test-evidence-policy.md", "# Test Evidence Governance Policy\n")
        _write(self.root, "openspec/README.md", "# OpenSpec\n")
        _write(self.root, "openspec/product/README.md", "# Product Context\n")
        _write(self.root, "openspec/change-guidance/README.md", "# Change Guidance\n")
        _write(self.root, "openspec/change-guidance/core/change-practice.md", "# Principles\n")
        _write(self.root, "openspec/change-guidance/profiles/node-agent/node-agent.md", "# Node Agent Gate\n")
        (self.root / "openspec/change-guidance/local").mkdir()
        _write(self.root, "openspec/governance/selected-change-closeout.md", "# Closeout Evidence\n")
        _write(
            self.root,
            "openspec/governance/selected-change-closeout.py",
            "#!/usr/bin/env python3\n",
        )
        _write(self.root, ACTIVE_SPEC_PATH, SPEC_TEXT)
        _write(self.root, GUIDE_PATH, "# Application-Owned Agent Guide\n")
        _write(
            self.root,
            "deep_research_harness/pyproject.toml",
            '[project]\nname = "fixture"\n\n'
            "[tool.hatch.build.targets.wheel]\n"
            'packages = ["src/deerflow_deep_research"]\n',
        )
        (self.root / "deep_research_harness/src/deerflow_deep_research").mkdir(parents=True)
        _write(self.root, "deep_research_harness/src_fake/deerflow_deep_research_fixtures/__init__.py")
        (self.root / "deep_research_harness/tests").mkdir(parents=True)
        _write(
            self.root,
            "deep_research_harness/.gitignore",
            ".deep-research-demo-runs/\n.reports/\n.pytest_cache/\n.ruff_cache/\n.node-prompt-review/\n",
        )
        _write(self.root, "deep_research_harness/docs/README.md", "# Documentation\n")
        _write(self.root, "deep_research_harness/docs/runtime-architecture.md", "# Runtime architecture\n")
        _write(self.root, "deep_research_harness/docs/local-operations.md", "# Local operations\n")
        _write(self.root, "deep_research_harness/docs/testing-and-evaluation.md", "# Testing and evaluation\n")
        self.gitlink_commit = _initialize_gitlink_fixture(self.root)
        _set_gitlink_lock(self.root, self.gitlink_commit)

    def tearDown(self) -> None:
        self._temporary.cleanup()

    def run_checker(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECKER), str(self.root)],
            check=False,
            capture_output=True,
            text=True,
        )

    def assert_checker_error(self, code: str) -> None:
        result = self.run_checker()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(code, result.stderr)

    def test_valid_pending_project_passes(self) -> None:
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("architecture governance passed", result.stdout.lower())

    def test_missing_gitlink_lock_fails(self) -> None:
        manifest_path = self.root / MANIFEST_PATH
        manifest = manifest_path.read_text(encoding="utf-8")
        start = manifest.index("[upstream_gitlink]")
        end = manifest.index("\n\n", start)
        manifest_path.write_text(manifest[:start] + manifest[end + 2 :], encoding="utf-8")

        self.assert_checker_error("gitlink.schema")

    def test_gitlink_lock_rejects_extra_field(self) -> None:
        _replace(
            self.root,
            MANIFEST_PATH,
            f'commit = "{self.gitlink_commit}"',
            f'commit = "{self.gitlink_commit}"\nbranch = "main"',
        )

        self.assert_checker_error("gitlink.schema")

    def test_gitlink_lock_rejects_malformed_commit(self) -> None:
        _set_gitlink_lock(self.root, "not-a-git-commit")

        self.assert_checker_error("gitlink.commit")

    def test_gitlink_lock_rejects_noncanonical_path(self) -> None:
        _replace(self.root, MANIFEST_PATH, 'path = "deerflow"', 'path = "./deerflow"')

        self.assert_checker_error("path.normalization")

    def test_gitlink_boundary_rejects_symlink(self) -> None:
        nested = self.root / "deerflow"
        shutil.rmtree(nested)
        target = self.root / "ordinary-boundary"
        target.mkdir()
        nested.symlink_to(target, target_is_directory=True)

        self.assert_checker_error("gitlink.path_symlink")

    def test_gitlink_boundary_rejects_missing_index_entry(self) -> None:
        _git(self.root, "update-index", "--force-remove", "deerflow")

        self.assert_checker_error("gitlink.index_shape")

    def test_gitlink_boundary_rejects_non_gitlink_index_entry(self) -> None:
        _stage_gitlink(self.root, self.gitlink_commit, mode="100644")

        self.assert_checker_error("gitlink.index_entry")

    def test_gitlink_boundary_rejects_alternate_stage_entries(self) -> None:
        _git(
            self.root,
            "update-index",
            "--index-info",
            input_text=(
                f"0 {'0' * 40}\tdeerflow\n"
                f"160000 {self.gitlink_commit} 1\tdeerflow\n"
                f"160000 {self.gitlink_commit} 2\tdeerflow\n"
            ),
        )

        self.assert_checker_error("gitlink.index_shape")

    def test_gitlink_boundary_rejects_index_commit_mismatch(self) -> None:
        _stage_gitlink(self.root, "f" * 40)

        self.assert_checker_error("gitlink.index_commit")

    def test_gitlink_boundary_rejects_nested_head_mismatch(self) -> None:
        _git(self.root / "deerflow", "commit", "--allow-empty", "--quiet", "-m", "head drift")

        self.assert_checker_error("gitlink.head_commit")

    def test_gitlink_boundary_rejects_metadata_query_failure(self) -> None:
        shutil.rmtree(self.root / "deerflow" / ".git")
        (self.root / "deerflow" / ".git").write_text("gitdir: missing-metadata\n", encoding="utf-8")

        self.assert_checker_error("gitlink.head_query")

    def test_gitlink_boundary_rejects_ordinary_directory_without_git_metadata(self) -> None:
        nested = self.root / "deerflow"
        shutil.rmtree(nested / ".git")

        self.assert_checker_error("gitlink.nested_metadata")

    def test_gitlink_boundary_rejects_staged_nested_change(self) -> None:
        _commit_nested_probe(self.root)
        nested = self.root / "deerflow"
        (nested / "boundary-probe.txt").write_text("staged\n", encoding="utf-8")
        _git(nested, "add", "boundary-probe.txt")

        self.assert_checker_error("gitlink.status_dirty")

    def test_gitlink_boundary_rejects_unstaged_nested_change(self) -> None:
        _commit_nested_probe(self.root)
        (self.root / "deerflow" / "boundary-probe.txt").write_text("unstaged\n", encoding="utf-8")

        self.assert_checker_error("gitlink.status_dirty")

    def test_gitlink_boundary_rejects_deleted_nested_change(self) -> None:
        _commit_nested_probe(self.root)
        (self.root / "deerflow" / "boundary-probe.txt").unlink()

        self.assert_checker_error("gitlink.status_dirty")

    def test_gitlink_boundary_rejects_untracked_nested_change(self) -> None:
        nested = self.root / "deerflow"
        (nested / "untracked-probe.txt").write_text("untracked\n", encoding="utf-8")

        self.assert_checker_error("gitlink.status_dirty")

    def test_matching_staged_gitlink_bump_passes_before_parent_commit(self) -> None:
        nested = self.root / "deerflow"
        _git(nested, "commit", "--allow-empty", "--quiet", "-m", "intentional bump")
        bumped_commit = _git(nested, "rev-parse", "--verify", "HEAD").stdout.strip()
        _stage_gitlink(self.root, bumped_commit)
        _set_gitlink_lock(self.root, bumped_commit)

        result = self.run_checker()

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_staged_gitlink_bump_rejects_mismatched_lock(self) -> None:
        nested = self.root / "deerflow"
        _git(nested, "commit", "--allow-empty", "--quiet", "-m", "unmatched bump")
        bumped_commit = _git(nested, "rev-parse", "--verify", "HEAD").stdout.strip()
        _stage_gitlink(self.root, bumped_commit)

        self.assert_checker_error("gitlink.index_commit")

    def test_structure_scan_does_not_descend_into_declared_gitlink(self) -> None:
        nested = self.root / "deerflow"
        _write(nested, "deerflow_deep_research/__init__.py")
        _git(nested, "add", "deerflow_deep_research/__init__.py")
        _git(nested, "commit", "--quiet", "-m", "upstream-shaped fixture")
        nested_commit = _git(nested, "rev-parse", "--verify", "HEAD").stdout.strip()
        _stage_gitlink(self.root, nested_commit)
        _set_gitlink_lock(self.root, nested_commit)

        result = self.run_checker()

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_gitlink_checker_uses_only_fixed_read_only_metadata_commands(self) -> None:
        import importlib

        checker = importlib.import_module("openspec.governance.check_project_architecture")
        manifest = checker.load_manifest(self.root)
        expected_commands = [
            ["git", "-C", str(self.root), "ls-files", "--stage", "-z", "--", "deerflow"],
            ["git", "-C", str(self.root / "deerflow"), "rev-parse", "--verify", "HEAD"],
            [
                "git",
                "-C",
                str(self.root / "deerflow"),
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
            ],
        ]
        responses = [
            subprocess.CompletedProcess(
                expected_commands[0],
                0,
                stdout=f"160000 {self.gitlink_commit} 0\tdeerflow\0",
                stderr="",
            ),
            subprocess.CompletedProcess(expected_commands[1], 0, stdout=f"{self.gitlink_commit}\n", stderr=""),
            subprocess.CompletedProcess(expected_commands[2], 0, stdout="", stderr=""),
        ]

        with patch.object(checker.subprocess, "run", side_effect=responses) as run:
            checker._validate_upstream_gitlink(self.root, manifest)

        self.assertEqual([call.args[0] for call in run.call_args_list], expected_commands)

    def test_gitlink_checker_rejects_malformed_metadata_output(self) -> None:
        import importlib

        checker = importlib.import_module("openspec.governance.check_project_architecture")
        manifest = checker.load_manifest(self.root)

        with patch.object(
            checker.subprocess,
            "run",
            return_value=subprocess.CompletedProcess([], 0, stdout="not an index record\0", stderr=""),
        ):
            with self.assertRaises(checker.ContractViolation) as raised:
                checker._validate_upstream_gitlink(self.root, manifest)
        self.assertEqual(raised.exception.code, "gitlink.index_shape")

    def test_gitlink_checker_rejects_unavailable_metadata_command(self) -> None:
        import importlib

        checker = importlib.import_module("openspec.governance.check_project_architecture")
        manifest = checker.load_manifest(self.root)

        with patch.object(checker.subprocess, "run", side_effect=OSError("unavailable")):
            with self.assertRaises(checker.ContractViolation) as raised:
                checker._validate_upstream_gitlink(self.root, manifest)
        self.assertEqual(raised.exception.code, "gitlink.command_unavailable")

    def test_imports_only_does_not_issue_gitlink_metadata_queries(self) -> None:
        import importlib

        checker = importlib.import_module("openspec.governance.check_project_architecture")

        with patch.object(checker, "_run_git_metadata") as run:
            checker.check_project(self.root, imports_only=True)

        run.assert_not_called()

    def test_missing_manifest_fails(self) -> None:
        (self.root / MANIFEST_PATH).unlink()
        self.assert_checker_error("manifest.missing")

    def test_malformed_manifest_fails(self) -> None:
        _write(self.root, MANIFEST_PATH, "schema_version = [")
        self.assert_checker_error("manifest.parse")

    def test_fixture_registration_requires_root_and_package_together(self) -> None:
        _replace(
            self.root,
            MANIFEST_PATH,
            'fixture_package = "deerflow_deep_research_fixtures"\n',
            "",
        )
        self.assert_checker_error("manifest.schema")

    def test_fixture_registration_requires_the_distinct_package_name(self) -> None:
        _replace(
            self.root,
            MANIFEST_PATH,
            'fixture_package = "deerflow_deep_research_fixtures"',
            'fixture_package = "deerflow_deep_research"',
        )
        self.assert_checker_error("manifest.schema")

    def test_fixture_registration_requires_the_registered_src_fake_root(self) -> None:
        _replace(
            self.root,
            MANIFEST_PATH,
            'fixture_root = "deep_research_harness/src_fake/deerflow_deep_research_fixtures"',
            'fixture_root = "deep_research_harness/alternate/deerflow_deep_research_fixtures"',
        )
        self.assert_checker_error("manifest.schema")

    def test_former_harness_root_is_rejected_before_path_validation(self) -> None:
        _replace(
            self.root,
            MANIFEST_PATH,
            'source_root = "deep_research_harness/src/deerflow_deep_research"',
            'source_root = "deerflow_research/src/deerflow_deep_research"',
        )

        self.assert_checker_error("source.canonical_root")

    def test_fixture_registration_requires_an_import_allowlist(self) -> None:
        manifest_path = self.root / MANIFEST_PATH
        manifest = manifest_path.read_text(encoding="utf-8")
        start = manifest.index("[fixture_imports]")
        end = manifest.index("[[required_paths]]", start)
        manifest_path.write_text(manifest[:start] + manifest[end:], encoding="utf-8")
        self.assert_checker_error("manifest.schema")

    def test_missing_registered_fixture_root_fails(self) -> None:
        shutil.rmtree(self.root / "deep_research_harness/src_fake/deerflow_deep_research_fixtures")
        self.assert_checker_error("path.missing")

    def test_absolute_path_fails(self) -> None:
        _replace(
            self.root,
            MANIFEST_PATH,
            'path = "deep_research_harness/pyproject.toml"',
            'path = "/deep_research_harness/pyproject.toml"',
        )
        self.assert_checker_error("path.absolute")

    def test_traversing_path_fails(self) -> None:
        _replace(
            self.root,
            MANIFEST_PATH,
            'path = "deep_research_harness/pyproject.toml"',
            'path = "deep_research_harness/../pyproject.toml"',
        )
        self.assert_checker_error("path.traversal")

    def test_duplicate_path_fails(self) -> None:
        duplicate = """\

[[required_paths]]
path = "deep_research_harness/pyproject.toml"
kind = "file"
owner = "PRS-001"
"""
        _write(self.root, MANIFEST_PATH, VALID_MANIFEST + duplicate)
        self.assert_checker_error("path.duplicate")

    def test_unknown_requirement_owner_fails(self) -> None:
        _replace(self.root, MANIFEST_PATH, 'owner = "PRS-001"', 'owner = "PRS-999"')
        self.assert_checker_error("owner.unknown")

    def test_forbidden_upstream_ownership_fails(self) -> None:
        _replace(
            self.root,
            MANIFEST_PATH,
            'path = "deep_research_harness/pyproject.toml"',
            'path = "backend/deep-research.py"',
        )
        _write(self.root, "backend/deep-research.py")
        self.assert_checker_error("path.forbidden_owner")

    def test_missing_owning_spec_reference_fails(self) -> None:
        _replace(self.root, ACTIVE_SPEC_PATH, "> structure: openspec/governance/project-structure.toml\n", "")
        self.assert_checker_error("spec.reference_missing")

    def test_ambiguous_pending_owning_specs_fail(self) -> None:
        _write(self.root, "openspec/changes/change-other/specs/project-structure/spec.md", SPEC_TEXT)
        self.assert_checker_error("spec.reference_ambiguous")

    def test_archived_delta_cannot_be_pending_authority(self) -> None:
        _write(self.root, ARCHIVED_SPEC_PATH, SPEC_TEXT)
        shutil.rmtree(self.root / "openspec/changes/change-00")
        self.assert_checker_error("spec.archived_only")

    def test_archived_delta_cannot_replace_existing_main_spec(self) -> None:
        _write(self.root, ARCHIVED_SPEC_PATH, SPEC_TEXT)
        _write(self.root, MAIN_SPEC_PATH, MAIN_SPEC_TEXT.replace("> structure:", "> historical-structure:"))
        shutil.rmtree(self.root / "openspec/changes/change-00")
        self.assert_checker_error("spec.reference_missing")

    def test_second_source_root_fails(self) -> None:
        _write(self.root, "rogue/deerflow_deep_research/__init__.py")
        self.assert_checker_error("source.second_root")

    def test_unregistered_source_root_fails(self) -> None:
        _write(self.root, "deep_research_harness/src_experimental/rogue.py")
        self.assert_checker_error("source.unregistered_root")

    def test_legacy_compatibility_root_fails(self) -> None:
        (self.root / "agent").mkdir()
        self.assert_checker_error("source.compatibility_root")

    def test_missing_required_path_fails(self) -> None:
        (self.root / "deep_research_harness/pyproject.toml").unlink()
        self.assert_checker_error("path.missing")

    def test_prompt_review_ignore_entries_are_required(self) -> None:
        _write(self.root, "deep_research_harness/.gitignore", ".deep-research-demo-runs/\n")

        self.assert_checker_error("ignore.entries")

    def test_registered_local_workbench_path_is_detected_when_removed(self) -> None:
        """The structural registry keeps a workbench adapter from becoming orphaned."""
        workbench = "deep_research_harness/scripts/session_workbench.py"
        required = f'''\

[[required_paths]]
path = "{workbench}"
kind = "file"
owner = "PRS-001"
'''
        _write(self.root, workbench, "# thin adapter\n")
        _write(self.root, MANIFEST_PATH, VALID_MANIFEST + required)
        (self.root / workbench).unlink()

        self.assert_checker_error("path.missing")

    def test_registered_human_documentation_path_is_detected_when_removed(self) -> None:
        documentation = self.root / "deep_research_harness/docs/testing-and-evaluation.md"
        documentation.unlink()

        result = self.run_checker()

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("path.missing", result.stderr)
        self.assertIn("deep_research_harness/docs/testing-and-evaluation.md", result.stderr)

    def test_registered_product_context_path_is_detected_when_removed(self) -> None:
        product_document = self.root / "openspec/product/README.md"
        product_document.unlink()

        result = self.run_checker()

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("path.missing", result.stderr)
        self.assertIn("openspec/product/README.md", result.stderr)

    def test_direct_provider_classifier_imports_are_limited_to_the_raw_binding(self) -> None:
        _write(
            self.root,
            "deep_research_harness/src/deerflow_deep_research/runtime/node_agent_bridge.py",
            "import httpx\nimport openai\n",
        )

        result = self.run_checker()

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_direct_provider_classifier_imports_are_rejected_outside_the_raw_binding(self) -> None:
        _write(
            self.root,
            "deep_research_harness/src/deerflow_deep_research/runtime/run_experience.py",
            "import httpx\n",
        )

        self.assert_checker_error("import.external")

    def test_tool_module_cannot_import_domain_contracts(self) -> None:
        _write(
            self.root,
            "deep_research_harness/src/deerflow_deep_research/tool.py",
            "from deerflow_deep_research.domain.lifecycle import LifecycleAction\n",
        )

        self.assert_checker_error("import.boundary")


if __name__ == "__main__":
    unittest.main()
