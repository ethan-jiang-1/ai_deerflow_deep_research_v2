"""Manifest-backed AST import and source-ownership contracts.

@impl PRS-001
@impl PRS-002
@impl PRS-003
@impl PRS-006
@impl PRS-019
@impl FSI-001
@impl FSI-002
@impl FSI-003
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER = REPO_ROOT / "openspec" / "governance" / "check_project_architecture.py"

MANIFEST = """\
schema_version = 1
contract = "project-structure"
requirement_ids = ["PRS-001", "PRS-002", "PRS-003", "PRS-004", "PRS-006", "PRS-018"]

[upstream_gitlink]
path = "deerflow"
commit = "0000000000000000000000000000000000000000"

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
path = "deep_research_harness/src/deerflow_deep_research"
kind = "directory"
owner = "PRS-001"

[[required_paths]]
path = "deep_research_harness/.gitignore"
kind = "file"
owner = "PRS-006"

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

REGISTRY = """\
PRS-001: project-structure - package ownership
PRS-002: project-structure - imports
PRS-003: project-structure - nodes
PRS-004: project-structure - governance
PRS-006: project-structure - ignored local generated paths
PRS-018: project-structure - metadata-only upstream gitlink boundary
"""

VALID_MODULES = {
    "domain/models.py": "from dataclasses import dataclass\nfrom pydantic import BaseModel\n",
    "engine/runner.py": "from deerflow_deep_research.domain import models\n",
    "agents/factory.py": (
        "from deerflow.agents import create_deerflow_agent\n"
        "from langchain_core.tools import BaseTool\n"
        "from deerflow_deep_research.domain import models\n"
    ),
    "graph/builder.py": "from langgraph.graph import StateGraph\nfrom deerflow_deep_research.domain import models\n",
    "graph/components/work_units.py": "from deerflow_deep_research.engine import runner\n",
    "runtime/adapter.py": (
        "from deerflow.tools.types import Runtime\n"
        "from langchain_core.tools import BaseTool\n"
        "from langgraph.runtime import Runtime as LangGraphRuntime\n"
        "from deerflow_deep_research.agents import factory\n"
        "from deerflow_deep_research.domain import models\n"
        "from deerflow_deep_research.graph import builder\n"
    ),
    "graph/nodes/alpha/__init__.py": 'NODE_SPEC = object()\n__all__ = ["NODE_SPEC"]\n',
    "graph/nodes/alpha/contracts.py": "from deerflow_deep_research.domain import models\n",
    "graph/nodes/alpha/node.py": ("from . import contracts\nfrom deerflow_deep_research.engine import runner\n"),
    "graph/nodes/alpha/subgraph.py": (
        "from langgraph.types import Send\nfrom deerflow_deep_research.graph.components import work_units\n"
    ),
    "tool.py": "from deerflow_deep_research import runtime\n",
}

VALID_FIXTURE_MODULES = {
    "__init__.py": "",
    "catalog.py": "from deerflow_deep_research.domain import models\n",
}


def _write(root: Path, relative: str, content: str = "") -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture
def project_root() -> Path:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        _write(root, "openspec/governance/project-structure.toml", MANIFEST)
        _write(root, "openspec/governance/req-registry.yaml", REGISTRY)
        _write(
            root,
            "deep_research_harness/pyproject.toml",
            '[tool.hatch.build.targets.wheel]\npackages = ["src/deerflow_deep_research"]\n',
        )
        _write(
            root,
            "deep_research_harness/.gitignore",
            ".deep-research-demo-runs/\n.reports/\n.pytest_cache/\n.ruff_cache/\n.node-prompt-review/\n",
        )
        source_root = "deep_research_harness/src/deerflow_deep_research"
        for relative, content in VALID_MODULES.items():
            _write(root, f"{source_root}/{relative}", content)
        fixture_root = "deep_research_harness/src_fake/deerflow_deep_research_fixtures"
        for relative, content in VALID_FIXTURE_MODULES.items():
            _write(root, f"{fixture_root}/{relative}", content)
        yield root


def _run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), str(root), "--imports-only"],
        check=False,
        capture_output=True,
        text=True,
    )


def _assert_error(root: Path, code: str) -> None:
    result = _run_checker(root)
    assert result.returncode != 0, result.stdout
    assert code in result.stderr


def test_valid_layer_dependencies_pass(project_root: Path) -> None:
    result = _run_checker(project_root)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    ("relative", "statement"),
    [
        ("domain/reverse.py", "from deerflow_deep_research.runtime import adapter\n"),
        ("engine/reverse.py", "from deerflow_deep_research.agents import factory\n"),
        ("agents/reverse.py", "from deerflow_deep_research.runtime import adapter\n"),
        ("agents/graph_reverse.py", "from deerflow_deep_research.graph import builder\n"),
        ("graph/nodes/alpha/agent_reverse.py", "from deerflow_deep_research.agents import factory\n"),
        ("graph/nodes/alpha/runtime_reverse.py", "from deerflow_deep_research.runtime import adapter\n"),
        ("graph/nodes/alpha/graph_reverse.py", "from deerflow_deep_research.graph import builder\n"),
    ],
)
def test_reverse_dependency_fails(project_root: Path, relative: str, statement: str) -> None:
    _write(project_root, f"deep_research_harness/src/deerflow_deep_research/{relative}", statement)
    _assert_error(project_root, "import.boundary")


def test_sibling_node_import_fails(project_root: Path) -> None:
    _write(
        project_root,
        "deep_research_harness/src/deerflow_deep_research/graph/nodes/beta/node.py",
        "from deerflow_deep_research.graph.nodes.alpha import node\n",
    )
    _assert_error(project_root, "import.sibling")


def test_ordinary_node_module_cannot_import_langgraph(project_root: Path) -> None:
    _write(
        project_root,
        "deep_research_harness/src/deerflow_deep_research/graph/nodes/alpha/node.py",
        "from langgraph.types import Send\n",
    )
    _assert_error(project_root, "import.boundary")


def test_ordinary_node_module_cannot_import_graph_components(project_root: Path) -> None:
    _write(
        project_root,
        "deep_research_harness/src/deerflow_deep_research/graph/nodes/alpha/node.py",
        "from deerflow_deep_research.graph.components import work_units\n",
    )
    _assert_error(project_root, "import.boundary")


def test_real_hitl_node_may_import_only_public_interrupt(project_root: Path) -> None:
    _write(
        project_root,
        "deep_research_harness/src/deerflow_deep_research/graph/nodes/hitl1/__init__.py",
        'NODE_SPEC = object()\n__all__ = ["NODE_SPEC"]\n',
    )
    _write(project_root, "deep_research_harness/src/deerflow_deep_research/graph/nodes/hitl1/contracts.py")
    _write(
        project_root,
        "deep_research_harness/src/deerflow_deep_research/graph/nodes/hitl1/node.py",
        "from langgraph.types import interrupt\n",
    )
    result = _run_checker(project_root)
    assert result.returncode == 0, result.stderr


def test_non_hitl_real_node_cannot_import_interrupt(project_root: Path) -> None:
    _write(
        project_root,
        "deep_research_harness/src/deerflow_deep_research/graph/nodes/alpha/node.py",
        "from langgraph.types import interrupt\n",
    )
    _assert_error(project_root, "import.boundary")


def test_production_fixture_file_is_rejected(project_root: Path) -> None:
    _write(project_root, "deep_research_harness/src/deerflow_deep_research/graph/nodes/alpha/fake.py")
    _assert_error(project_root, "node.fixture_file")


def test_production_source_cannot_import_fixture_package(project_root: Path) -> None:
    _write(
        project_root,
        "deep_research_harness/src/deerflow_deep_research/runtime/fixture_reverse.py",
        "from deerflow_deep_research_fixtures import catalog\n",
    )
    _assert_error(project_root, "import.fixture_reverse")


def test_fixture_source_cannot_import_undeclared_external_package(project_root: Path) -> None:
    _write(
        project_root,
        "deep_research_harness/src_fake/deerflow_deep_research_fixtures/external.py",
        "import requests\n",
    )
    _assert_error(project_root, "import.fixture_external")


def test_fixture_source_cannot_import_an_unregistered_production_module(project_root: Path) -> None:
    _write(
        project_root,
        "deep_research_harness/src_fake/deerflow_deep_research_fixtures/runtime_reverse.py",
        "from deerflow_deep_research.runtime.control import GraphHost\n",
    )
    _assert_error(project_root, "import.fixture_production")


@pytest.mark.parametrize("factory", ["all_real", "create"])
def test_fixture_recipe_factory_allows_only_from_adapters(project_root: Path, factory: str) -> None:
    _write(
        project_root,
        "deep_research_harness/src_fake/deerflow_deep_research_fixtures/catalog.py",
        f"from deerflow_deep_research.runtime.research import ResearchGraphRecipe\nResearchGraphRecipe.{factory}()\n",
    )
    _assert_error(project_root, "fixture.recipe_factory")


def test_fixture_recipe_factory_accepts_from_adapters(project_root: Path) -> None:
    _write(
        project_root,
        "deep_research_harness/src_fake/deerflow_deep_research_fixtures/catalog.py",
        "from deerflow_deep_research.runtime.research import ResearchGraphRecipe\n"
        "ResearchGraphRecipe.from_adapters()\n",
    )
    result = _run_checker(project_root)
    assert result.returncode == 0, result.stderr


def test_raw_provider_classifier_imports_are_limited_to_node_agent_bridge(project_root: Path) -> None:
    _write(
        project_root,
        "deep_research_harness/src/deerflow_deep_research/runtime/node_agent_bridge.py",
        "import httpx\nimport openai\n",
    )

    result = _run_checker(project_root)

    assert result.returncode == 0, result.stderr


def test_raw_provider_classifier_imports_fail_outside_node_agent_bridge(project_root: Path) -> None:
    _write(project_root, "deep_research_harness/src/deerflow_deep_research/runtime/adapter.py", "import httpx\n")

    _assert_error(project_root, "import.external")


def test_gateway_observer_may_import_only_its_public_http_sse_dependencies(project_root: Path) -> None:
    _write(
        project_root,
        "deep_research_harness/src/deerflow_deep_research/runtime/gateway_observer.py",
        "import httpx\nfrom httpx_sse import aconnect_sse\n",
    )

    result = _run_checker(project_root)

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("statement", ["import httpx_sse\n", "from httpx_sse import aconnect_sse\n"])
def test_structured_sse_imports_fail_outside_gateway_observer(project_root: Path, statement: str) -> None:
    _write(project_root, "deep_research_harness/src/deerflow_deep_research/runtime/adapter.py", statement)

    _assert_error(project_root, "import.external")


def test_production_app_import_fails(project_root: Path) -> None:
    _write(
        project_root,
        "deep_research_harness/src/deerflow_deep_research/runtime/app_reverse.py",
        "from app.gateway import app\n",
    )
    _assert_error(project_root, "import.app")


@pytest.mark.parametrize("name", ["utils.py", "helpers.py", "common.py"])
def test_generic_shared_module_fails(project_root: Path, name: str) -> None:
    _write(project_root, f"deep_research_harness/src/deerflow_deep_research/domain/{name}")
    _assert_error(project_root, "module.generic")


@pytest.mark.parametrize("upstream_root", ["backend", "frontend"])
def test_upstream_import_of_downstream_fails(project_root: Path, upstream_root: str) -> None:
    _write(project_root, f"{upstream_root}/rogue.py", "import deerflow_deep_research\n")
    _assert_error(project_root, "source.upstream_import")


def test_manifest_cannot_weaken_domain_boundary(project_root: Path) -> None:
    manifest = project_root / "openspec/governance/project-structure.toml"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace(
            'domain = ["stdlib", "pydantic"]',
            'domain = ["stdlib", "pydantic", "runtime"]',
        ),
        encoding="utf-8",
    )
    _assert_error(project_root, "imports.policy")


def test_manifest_node_shape_requires_real_node_file(project_root: Path) -> None:
    (project_root / "deep_research_harness/src/deerflow_deep_research/graph/nodes/alpha/node.py").unlink()
    _assert_error(project_root, "node.file_missing")


def test_manifest_node_shape_rejects_export_leakage(project_root: Path) -> None:
    _write(
        project_root,
        "deep_research_harness/src/deerflow_deep_research/graph/nodes/alpha/__init__.py",
        'NODE_SPEC = object()\ninternal = object()\n__all__ = ["NODE_SPEC", "internal"]\n',
    )
    _assert_error(project_root, "node.exports")


def test_components_cannot_be_top_level_nodes(project_root: Path) -> None:
    _write(project_root, "deep_research_harness/src/deerflow_deep_research/graph/nodes/components/__init__.py")
    _assert_error(project_root, "node.package_confusion")


def test_whitelisted_namespace_assignment_is_toml_only(project_root: Path) -> None:
    manifest = project_root / "openspec/governance/project-structure.toml"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace(
            'runtime = ["domain", "graph", "agents", "deerflow", "httpx", "httpx_sse", "langchain", '
            '"langgraph", "openai"]',
            'runtime = ["domain", "graph", "agents", "deerflow", "httpx", "httpx_sse", "langchain", '
            '"langgraph", "openai", "pydantic"]',
        ),
        encoding="utf-8",
    )
    result = _run_checker(project_root)
    assert result.returncode == 0, result.stderr


def test_unknown_external_namespace_is_rejected_by_whitelist(project_root: Path) -> None:
    manifest = project_root / "openspec/governance/project-structure.toml"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace(
            'runtime = ["domain", "graph", "agents", "deerflow", "httpx", "httpx_sse", "langchain", '
            '"langgraph", "openai"]',
            'runtime = ["domain", "graph", "agents", "deerflow", "httpx", "httpx_sse", "langchain", '
            '"langgraph", "openai", "bogus_ns"]',
        ),
        encoding="utf-8",
    )
    _assert_error(project_root, "imports.namespace")
