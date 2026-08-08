"""Deterministic contracts for the permanent project-structure governance gate.

@impl PRS-004
@impl PRS-001
@impl PRS-006
@impl PRS-011
@impl PRS-017
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
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
requirement_ids = ["PRS-001", "PRS-002", "PRS-003", "PRS-004", "PRS-006", "PRS-009", "PRS-011"]

[guide]
path = "deep_research_harness/AGENTS.md"
begin_marker = "<!-- BEGIN GENERATED: PROJECT-STRUCTURE -->"
end_marker = "<!-- END GENERATED: PROJECT-STRUCTURE -->"

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

[imports]
domain = ["stdlib", "pydantic"]
engine = ["domain"]
agents = ["domain", "deerflow", "langchain"]
graph = ["domain", "engine", "nodes", "langgraph"]
nodes = ["domain", "engine", "langgraph"]
runtime = ["domain", "graph", "agents", "deerflow", "httpx", "langchain", "langgraph", "openai"]

[node_packages]
root = "deep_research_harness/src/deerflow_deep_research/graph/nodes"
required_files = ["__init__.py", "node.py", "contracts.py"]
optional_files = ["subgraph.py"]
forbidden_files = ["fake.py"]
public_export = "NODE_SPEC"
"""

SPEC_TEXT = """\
> req: PRS-001, PRS-002, PRS-003, PRS-004, PRS-006, PRS-009, PRS-011
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
"""

VALID_GENERATED_BLOCK = f"""\
<!-- BEGIN GENERATED: PROJECT-STRUCTURE -->
## Canonical Structure Locator

Exact inventory: `openspec/governance/project-structure.toml`

- Source root: `deep_research_harness/src/deerflow_deep_research/`
- Fixture source root: `deep_research_harness/src_fake/deerflow_deep_research_fixtures/`
- Test root: `deep_research_harness/tests/`
- Ownership layers: `runtime`, `domain`, `engine`, `agents`, `graph`
- Node grammar: `{NODE_ROOT}/` packages export `NODE_SPEC`; see the registry for files
- Validate: `python3 openspec/governance/check_project_architecture.py`
<!-- END GENERATED: PROJECT-STRUCTURE -->
"""


def _write(root: Path, relative_path: Path | str, content: str = "") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _replace(root: Path, relative_path: Path | str, old: str, new: str) -> None:
    path = root / relative_path
    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


class ArchitectureGovernanceContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary.name)
        _write(self.root, MANIFEST_PATH, VALID_MANIFEST)
        _write(self.root, "openspec/governance/req-registry.yaml", REGISTRY_TEXT)
        _write(self.root, "openspec/governance/test-evidence-policy.md", "# Test Evidence Governance Policy\n")
        _write(self.root, ACTIVE_SPEC_PATH, SPEC_TEXT)
        _write(self.root, GUIDE_PATH, f"# Agent Guide\n\n{VALID_GENERATED_BLOCK}\nOperational text.\n")
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

    def test_missing_guide_markers_fail(self) -> None:
        _write(self.root, GUIDE_PATH, "# Agent Guide\n")
        self.assert_checker_error("guide.marker_missing")

    def test_duplicate_guide_markers_fail(self) -> None:
        _write(self.root, GUIDE_PATH, f"{VALID_GENERATED_BLOCK}\n{VALID_GENERATED_BLOCK}")
        self.assert_checker_error("guide.marker_duplicate")

    def test_stale_generated_guide_block_fails(self) -> None:
        _replace(self.root, GUIDE_PATH, "Ownership layers:", "Old ownership layers:")
        self.assert_checker_error("guide.drift")

    def test_generated_guide_block_is_a_locator_not_an_inventory(self) -> None:
        self.assertNotIn("deep_research_harness/pyproject.toml", VALID_GENERATED_BLOCK)
        self.assertIn("Exact inventory:", VALID_GENERATED_BLOCK)
        self.assertIn("Fixture source root:", VALID_GENERATED_BLOCK)
        self.assertIn("Validate:", VALID_GENERATED_BLOCK)

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
