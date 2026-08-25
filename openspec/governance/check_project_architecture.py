#!/usr/bin/env python3
"""Validate the permanent project-structure registry without external packages.

@impl PRS-004
@impl PRS-002
@impl PRS-003
@impl PRS-006
@impl PRS-011
@impl PRS-017
@impl PRS-019
@impl PRS-021
@impl FSI-003
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import stat
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

MANIFEST_RELATIVE = PurePosixPath("openspec/governance/project-structure.toml")
INVENTORY_RELATIVE = PurePosixPath("openspec/governance/required-paths.toml")
REGISTRY_RELATIVE = PurePosixPath("openspec/governance/req-registry.yaml")
MAIN_SPEC_RELATIVE = PurePosixPath("openspec/specs/project-structure/spec.md")
UPSTREAM_GITLINK_PATH = PurePosixPath("deerflow")
SPEC_REFERENCE = "> structure: openspec/governance/project-structure.toml"
ID_RE = re.compile(r"^[A-Z]{3}-\d{3}$")
GIT_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
REGISTRY_ID_RE = re.compile(r"^([A-Z]{3}-\d{3}):", re.MULTILINE)
REQ_HEADER_RE = re.compile(r"^> req:\s*(.+)$", re.MULTILINE)
PACKAGE_NAME = "deerflow_deep_research"
FIXTURE_PACKAGE_NAME = "deerflow_deep_research_fixtures"
CANONICAL_HARNESS_ROOT = PurePosixPath("deep_research_harness")
# Import-boundary layers: the six keys of the `[imports]` table. `nodes` is the
# graph-owned node-package import sub-layer, not one of the five ownership layers
# (`runtime`, `domain`, `engine`, `agents`, `graph`).
INTERNAL_LAYERS = {"domain", "engine", "agents", "graph", "nodes", "runtime"}
# Non-weakenable internal-layer import directions, owned by PRS-002. The `[imports]`
# table cannot add an internal layer to a layer that these rules exclude.
REQUIRED_INTERNAL_IMPORT_POLICY = {
    "domain": set(),
    "engine": {"domain"},
    "agents": {"domain"},
    "graph": {"domain", "engine", "nodes"},
    "nodes": {"domain", "engine"},
    "runtime": {"domain", "graph", "agents"},
}
# Closed set of legal external top-level namespaces. External namespaces are
# TOML-authorized per layer; this whitelist only answers "is this external namespace
# real at all". Internal layers are validated separately above.
TOP_LEVEL_NAMESPACE_WHITELIST = {
    "stdlib",
    "pydantic",
    "deerflow",
    "langchain",
    "langgraph",
    "httpx",
    "httpx_sse",
    "openai",
}
REQUIRED_NODE_FILES = {"__init__.py", "node.py", "contracts.py"}
REQUIRED_NODE_FORBIDDEN_FILES = {"fake.py"}


class ContractViolation(Exception):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class RequiredPath:
    path: PurePosixPath
    kind: str
    owner: str


@dataclass(frozen=True)
class UpstreamGitlink:
    path: PurePosixPath
    commit: str


@dataclass(frozen=True)
class StructureManifest:
    requirement_ids: tuple[str, ...]
    guide_path: PurePosixPath
    begin_marker: str
    end_marker: str
    upstream_gitlink: UpstreamGitlink
    source_root: PurePosixPath
    fixture_root: PurePosixPath | None
    fixture_package: str | None
    fixture_production_contracts: tuple[str, ...]
    fixture_external_namespaces: tuple[str, ...]
    fixture_recipe_class: str | None
    fixture_recipe_factories: tuple[str, ...]
    test_root: PurePosixPath
    ownership_layers: tuple[str, ...]
    forbidden_source_roots: tuple[PurePosixPath, ...]
    forbidden_shared_modules: tuple[str, ...]
    ignored_path: PurePosixPath
    ignored_entries: tuple[str, ...]
    required_paths: tuple[RequiredPath, ...]
    imports: dict[str, tuple[str, ...]]
    node_root: PurePosixPath
    node_required_files: tuple[str, ...]
    node_optional_files: tuple[str, ...]
    node_forbidden_files: tuple[str, ...]
    node_public_export: str


def _expect_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractViolation("manifest.schema", f"{label} must be a TOML table")
    return value


def _expect_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractViolation("manifest.schema", f"{label} must be a non-empty string")
    return value


def _expect_string_list(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
        raise ContractViolation("manifest.schema", f"{label} must be a non-empty string array")
    if len(set(value)) != len(value):
        raise ContractViolation("manifest.schema", f"{label} contains duplicates")
    return tuple(value)


def _relative_path(value: Any, label: str) -> PurePosixPath:
    raw = _expect_string(value, label)
    if raw.startswith("/") or PurePosixPath(raw).is_absolute():
        raise ContractViolation("path.absolute", f"{label} must be repository-relative: {raw}")
    if "\\" in raw:
        raise ContractViolation("path.normalization", f"{label} must use POSIX separators: {raw}")
    path = PurePosixPath(raw)
    if ".." in path.parts:
        raise ContractViolation("path.traversal", f"{label} contains parent traversal: {raw}")
    if raw in {"", "."} or path.as_posix() != raw:
        raise ContractViolation("path.normalization", f"{label} is not normalized: {raw}")
    return path


def _registered_ids(root: Path) -> set[str]:
    path = root / REGISTRY_RELATIVE
    if not path.is_file():
        raise ContractViolation("owner.registry_missing", f"requirement registry is missing: {REGISTRY_RELATIVE}")
    return set(REGISTRY_ID_RE.findall(path.read_text(encoding="utf-8")))


def load_manifest(root: Path) -> StructureManifest:
    path = root / MANIFEST_RELATIVE
    if not path.is_file():
        raise ContractViolation("manifest.missing", f"structure registry is missing: {MANIFEST_RELATIVE}")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ContractViolation("manifest.parse", f"cannot parse {MANIFEST_RELATIVE}: {exc}") from exc

    if data.get("schema_version") != 1:
        raise ContractViolation("manifest.schema", "schema_version must be integer 1")
    if data.get("contract") != "project-structure":
        raise ContractViolation("manifest.schema", "contract must be 'project-structure'")

    requirement_ids = _expect_string_list(data.get("requirement_ids"), "requirement_ids")
    if any(not ID_RE.fullmatch(requirement_id) for requirement_id in requirement_ids):
        raise ContractViolation("manifest.schema", "requirement_ids contains an invalid ID")
    registered = _registered_ids(root)
    unknown_requirements = sorted(set(requirement_ids) - registered)
    if unknown_requirements:
        raise ContractViolation(
            "owner.unknown",
            f"unregistered manifest requirement IDs: {', '.join(unknown_requirements)}",
        )

    upstream_gitlink_raw = data.get("upstream_gitlink")
    if not isinstance(upstream_gitlink_raw, dict):
        raise ContractViolation("gitlink.schema", "upstream_gitlink must be a TOML table")
    upstream_gitlink_data = _expect_mapping(upstream_gitlink_raw, "upstream_gitlink")
    if set(upstream_gitlink_data) != {"path", "commit"}:
        raise ContractViolation("gitlink.schema", "upstream_gitlink must contain exactly path and commit")
    upstream_gitlink_path = _relative_path(upstream_gitlink_data.get("path"), "upstream_gitlink.path")
    if upstream_gitlink_path != UPSTREAM_GITLINK_PATH:
        raise ContractViolation("gitlink.path", f"upstream_gitlink.path must be {UPSTREAM_GITLINK_PATH}")
    upstream_gitlink_commit = _expect_string(upstream_gitlink_data.get("commit"), "upstream_gitlink.commit")
    if not GIT_COMMIT_RE.fullmatch(upstream_gitlink_commit):
        raise ContractViolation("gitlink.commit", "upstream_gitlink.commit must be a lower-case 40-hex identifier")
    upstream_gitlink = UpstreamGitlink(path=upstream_gitlink_path, commit=upstream_gitlink_commit)

    package = _expect_mapping(data.get("package"), "package")
    source_root = _relative_path(package.get("source_root"), "package.source_root")
    expected_source_root = CANONICAL_HARNESS_ROOT / "src" / PACKAGE_NAME
    if source_root != expected_source_root:
        raise ContractViolation(
            "source.canonical_root",
            f"package.source_root must be {expected_source_root}",
        )
    fixture_root_raw = package.get("fixture_root")
    fixture_package_raw = package.get("fixture_package")
    fixture_imports_raw = data.get("fixture_imports")
    if fixture_root_raw is None and fixture_package_raw is None:
        fixture_root = None
        fixture_package = None
        if fixture_imports_raw is not None:
            raise ContractViolation("manifest.schema", "fixture_imports requires a registered fixture root")
        fixture_production_contracts: tuple[str, ...] = ()
        fixture_external_namespaces: tuple[str, ...] = ()
        fixture_recipe_class = None
        fixture_recipe_factories: tuple[str, ...] = ()
    elif fixture_root_raw is None or fixture_package_raw is None:
        raise ContractViolation("manifest.schema", "fixture_root and fixture_package must be declared together")
    else:
        fixture_root = _relative_path(fixture_root_raw, "package.fixture_root")
        fixture_package = _expect_string(fixture_package_raw, "package.fixture_package")
        if fixture_package != FIXTURE_PACKAGE_NAME or fixture_root.name != fixture_package:
            raise ContractViolation("manifest.schema", "fixture root must use the registered distinct package name")
        if fixture_root == source_root:
            raise ContractViolation("manifest.schema", "fixture root must differ from production source root")
        expected_fixture_root = source_root.parent.parent / "src_fake" / fixture_package
        if fixture_root != expected_fixture_root:
            raise ContractViolation("manifest.schema", "fixture root must use the registered src_fake location")

        fixture_imports = _expect_mapping(fixture_imports_raw, "fixture_imports")
        fixture_production_contracts = _expect_string_list(
            fixture_imports.get("production_contracts"),
            "fixture_imports.production_contracts",
        )
        if any(
            not contract.startswith(f"{PACKAGE_NAME}.") or len(contract.split(".")) < 3
            for contract in fixture_production_contracts
        ):
            raise ContractViolation(
                "manifest.schema",
                "fixture_imports.production_contracts must name production contract modules",
            )
        fixture_external_namespaces = _expect_string_list(
            fixture_imports.get("external_namespaces"),
            "fixture_imports.external_namespaces",
        )
        if any("." in namespace for namespace in fixture_external_namespaces):
            raise ContractViolation(
                "manifest.schema",
                "fixture_imports.external_namespaces must contain top-level namespaces",
            )
        fixture_recipe_class = _expect_string(fixture_imports.get("recipe_class"), "fixture_imports.recipe_class")
        expected_recipe_class = f"{PACKAGE_NAME}.runtime.research.ResearchGraphRecipe"
        if fixture_recipe_class != expected_recipe_class:
            raise ContractViolation(
                "manifest.schema",
                "fixture_imports.recipe_class must name the documented recipe composition class",
            )
        if fixture_recipe_class in fixture_production_contracts:
            raise ContractViolation(
                "manifest.schema",
                "fixture recipe class must not widen the production-contract import allowlist",
            )
        fixture_recipe_factories = _expect_string_list(
            fixture_imports.get("recipe_factories"),
            "fixture_imports.recipe_factories",
        )
        if fixture_recipe_factories != ("from_adapters",):
            raise ContractViolation(
                "manifest.schema",
                "fixture recipe composition may permit only ResearchGraphRecipe.from_adapters",
            )
    test_root = _relative_path(package.get("test_root"), "package.test_root")
    expected_test_root = CANONICAL_HARNESS_ROOT / "tests"
    if test_root != expected_test_root:
        raise ContractViolation(
            "test.canonical_root",
            f"package.test_root must be {expected_test_root}",
        )
    ownership_layers = _expect_string_list(package.get("ownership_layers"), "package.ownership_layers")
    forbidden_source_roots = tuple(
        _relative_path(item, "package.forbidden_source_roots")
        for item in _expect_string_list(package.get("forbidden_source_roots"), "package.forbidden_source_roots")
    )
    forbidden_shared_modules = _expect_string_list(
        package.get("forbidden_shared_modules"), "package.forbidden_shared_modules"
    )

    ignored_paths = _expect_mapping(data.get("ignored_paths"), "ignored_paths")
    ignored_path = _relative_path(ignored_paths.get("path"), "ignored_paths.path")
    expected_ignored_path = CANONICAL_HARNESS_ROOT / ".gitignore"
    if ignored_path != expected_ignored_path:
        raise ContractViolation(
            "ignore.canonical_root",
            f"ignored_paths.path must be {expected_ignored_path}",
        )
    ignored_entries = _expect_string_list(ignored_paths.get("entries"), "ignored_paths.entries")
    if any(
        not entry.endswith("/")
        or entry.startswith("/")
        or "\\" in entry
        or ".." in PurePosixPath(entry[:-1]).parts
        for entry in ignored_entries
    ):
        raise ContractViolation(
            "manifest.schema",
            "ignored_paths.entries must contain normalized repository-local directory entries",
        )

    inventory_raw = data.get("inventory")
    if not isinstance(inventory_raw, dict):
        raise ContractViolation("inventory.schema", "inventory must be a TOML table")
    inventory_path = _relative_path(inventory_raw.get("path"), "inventory.path")
    if inventory_path != INVENTORY_RELATIVE:
        raise ContractViolation(
            "inventory.path",
            f"inventory.path must be {INVENTORY_RELATIVE.as_posix()}",
        )
    inventory_file = root / INVENTORY_RELATIVE
    if not inventory_file.is_file():
        raise ContractViolation("inventory.missing", f"required-path inventory is missing: {INVENTORY_RELATIVE}")
    try:
        inventory_data = tomllib.loads(inventory_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ContractViolation("inventory.parse", f"cannot parse {INVENTORY_RELATIVE}: {exc}") from exc
    if inventory_data.get("schema_version") != 1:
        raise ContractViolation("inventory.schema", "inventory schema_version must be integer 1")
    if inventory_data.get("contract") != "project-structure-inventory":
        raise ContractViolation(
            "inventory.schema",
            "inventory contract must be 'project-structure-inventory'",
        )
    raw_path_sections = inventory_data.get("paths")
    if not isinstance(raw_path_sections, dict) or not raw_path_sections:
        raise ContractViolation(
            "inventory.schema",
            "inventory must declare a non-empty [paths.<ID>] section table",
        )
    required_paths: list[RequiredPath] = []
    seen_paths: set[PurePosixPath] = set()
    for section_owner in sorted(raw_path_sections):
        if not ID_RE.fullmatch(section_owner):
            raise ContractViolation("inventory.owner", f"inventory section has an invalid owner ID: {section_owner}")
        section = _expect_mapping(raw_path_sections[section_owner], f"paths.{section_owner}")
        for kind, key in (("file", "files"), ("directory", "directories")):
            raw_values = section.get(key)
            if raw_values is None:
                continue
            for item_path_raw in _expect_string_list(raw_values, f"paths.{section_owner}.{key}"):
                item_path = _relative_path(item_path_raw, f"paths.{section_owner}.{key}")
                if item_path in seen_paths:
                    raise ContractViolation("path.duplicate", f"required path appears more than once: {item_path}")
                seen_paths.add(item_path)
                if section_owner not in registered or section_owner not in requirement_ids:
                    raise ContractViolation(
                        "owner.unknown",
                        f"required path {item_path} has unknown owner {section_owner}",
                    )
                if any(item_path == root_path or root_path in item_path.parents for root_path in forbidden_source_roots):
                    raise ContractViolation(
                        "path.forbidden_owner",
                        f"required path is under an upstream root: {item_path}",
                    )
                required_paths.append(RequiredPath(item_path, kind, section_owner))
    if not required_paths:
        raise ContractViolation("manifest.schema", "required_paths must be a non-empty set of inventory entries")
    if not any(item.path == ignored_path and item.kind == "file" for item in required_paths):
        raise ContractViolation(
            "manifest.schema",
            "ignored_paths.path must be registered as a required file",
        )
    if not any(item.path == INVENTORY_RELATIVE and item.kind == "file" for item in required_paths):
        raise ContractViolation(
            "inventory.unregistered",
            "the required-path inventory must be registered as a required file",
        )

    raw_imports = _expect_mapping(data.get("imports"), "imports")
    imports = {name: _expect_string_list(values, f"imports.{name}") for name, values in raw_imports.items()}
    if set(imports) != {"domain", "engine", "agents", "graph", "nodes", "runtime"}:
        raise ContractViolation(
            "manifest.schema",
            "imports must define domain, engine, agents, graph, nodes, and runtime",
        )
    for layer, required_internal in REQUIRED_INTERNAL_IMPORT_POLICY.items():
        internal = set(imports[layer]) & INTERNAL_LAYERS
        if internal != required_internal:
            raise ContractViolation(
                "imports.policy",
                f"imports.{layer} must keep its internal-layer import directions: {sorted(required_internal)}",
            )
        unknown = (set(imports[layer]) - INTERNAL_LAYERS) - TOP_LEVEL_NAMESPACE_WHITELIST
        if unknown:
            raise ContractViolation(
                "imports.namespace",
                f"imports.{layer} names an unknown external namespace: {sorted(unknown)}",
            )

    node_packages = _expect_mapping(data.get("node_packages"), "node_packages")
    node_root = _relative_path(node_packages.get("root"), "node_packages.root")
    node_required_files = _expect_string_list(node_packages.get("required_files"), "node_packages.required_files")
    node_optional_files = _expect_string_list(node_packages.get("optional_files"), "node_packages.optional_files")
    node_forbidden_files = _expect_string_list(node_packages.get("forbidden_files"), "node_packages.forbidden_files")
    if set(node_required_files) != REQUIRED_NODE_FILES:
        raise ContractViolation("manifest.schema", "node_packages.required_files must retain the real-only node grammar")
    if set(node_forbidden_files) != REQUIRED_NODE_FORBIDDEN_FILES:
        raise ContractViolation("manifest.schema", "node_packages.forbidden_files must reject production fake adapters")
    if set(node_required_files) & set(node_optional_files) or set(node_required_files) & set(node_forbidden_files):
        raise ContractViolation("manifest.schema", "node package file categories must not overlap")
    node_public_export = _expect_string(node_packages.get("public_export"), "node_packages.public_export")

    guide = _expect_mapping(data.get("guide"), "guide")
    guide_path = _relative_path(guide.get("path"), "guide.path")
    begin_marker = _expect_string(guide.get("begin_marker"), "guide.begin_marker")
    end_marker = _expect_string(guide.get("end_marker"), "guide.end_marker")
    if begin_marker == end_marker:
        raise ContractViolation("manifest.schema", "guide.begin_marker and guide.end_marker must differ")
    expected_guide_path = CANONICAL_HARNESS_ROOT / "AGENTS.md"
    if guide_path != expected_guide_path:
        raise ContractViolation("manifest.schema", f"guide.path must be {expected_guide_path.as_posix()}")

    return StructureManifest(
        requirement_ids=requirement_ids,
        guide_path=guide_path,
        begin_marker=begin_marker,
        end_marker=end_marker,
        upstream_gitlink=upstream_gitlink,
        source_root=source_root,
        fixture_root=fixture_root,
        fixture_package=fixture_package,
        fixture_production_contracts=fixture_production_contracts,
        fixture_external_namespaces=fixture_external_namespaces,
        fixture_recipe_class=fixture_recipe_class,
        fixture_recipe_factories=fixture_recipe_factories,
        test_root=test_root,
        ownership_layers=ownership_layers,
        forbidden_source_roots=forbidden_source_roots,
        forbidden_shared_modules=forbidden_shared_modules,
        ignored_path=ignored_path,
        ignored_entries=ignored_entries,
        required_paths=tuple(required_paths),
        imports=imports,
        node_root=node_root,
        node_required_files=node_required_files,
        node_optional_files=node_optional_files,
        node_forbidden_files=node_forbidden_files,
        node_public_export=node_public_export,
    )


def _directory_display(path: PurePosixPath) -> str:
    return f"{path.as_posix()}/"


def render_guide_block(manifest: StructureManifest) -> str:
    lines = [
        manifest.begin_marker,
        "## Canonical Structure Locator",
        "",
        "Exact inventory: the structure registry declared by the owning "
        "`project-structure` spec.",
        "",
        f"- Source root: `{_directory_display(manifest.source_root)}`",
        *(
            [f"- Fixture source root: `{_directory_display(manifest.fixture_root)}`"]
            if manifest.fixture_root is not None
            else []
        ),
        f"- Test root: `{_directory_display(manifest.test_root)}`",
        "- Ownership layers: " + ", ".join(f"`{layer}`" for layer in manifest.ownership_layers),
        f"- Node grammar: `{_directory_display(manifest.node_root)}` packages export "
        f"`{manifest.node_public_export}`; see the registry for files",
        "- Validate: repository architecture governance (`check_project_architecture.py`)",
        manifest.end_marker,
    ]
    return "\n".join(lines)


def _validate_guide(root: Path, manifest: StructureManifest) -> None:
    path = root / manifest.guide_path
    if not path.is_file():
        raise ContractViolation("guide.marker_missing", f"module guide is missing: {manifest.guide_path}")
    text = path.read_text(encoding="utf-8")
    begin_count = text.count(manifest.begin_marker)
    end_count = text.count(manifest.end_marker)
    if begin_count == 0 or end_count == 0:
        raise ContractViolation("guide.marker_missing", "module guide lacks the generated structure markers")
    if begin_count != 1 or end_count != 1:
        raise ContractViolation(
            "guide.marker_duplicate",
            "module guide must contain exactly one generated structure block",
        )
    start = text.index(manifest.begin_marker)
    end = text.index(manifest.end_marker, start) + len(manifest.end_marker)
    actual = text[start:end]
    expected = render_guide_block(manifest).rstrip("\n")
    if actual != expected:
        raise ContractViolation("guide.drift", "generated module-guide block does not match the structure registry")


def _validate_spec_authority(root: Path, manifest: StructureManifest) -> None:
    main_spec = root / MAIN_SPEC_RELATIVE
    if main_spec.is_file():
        text = main_spec.read_text(encoding="utf-8")
        reference_count = text.count(SPEC_REFERENCE)
        if reference_count == 0:
            raise ContractViolation("spec.reference_missing", f"active main spec lacks {SPEC_REFERENCE!r}")
        if reference_count != 1:
            raise ContractViolation("spec.reference_ambiguous", "active main spec has duplicate structure references")
        return

    changes_dir = root / "openspec" / "changes"
    active_specs = sorted(changes_dir.glob("*/specs/project-structure/spec.md")) if changes_dir.is_dir() else []
    owning_specs: list[Path] = []
    referenced_specs: list[Path] = []
    for spec_path in active_specs:
        text = spec_path.read_text(encoding="utf-8")
        header = REQ_HEADER_RE.search(text)
        declared = set(re.findall(r"[A-Z]{3}-\d{3}", header.group(1))) if header else set()
        if set(manifest.requirement_ids).issubset(declared):
            owning_specs.append(spec_path)
            if SPEC_REFERENCE in text:
                referenced_specs.append(spec_path)

    if len(referenced_specs) > 1 or len(owning_specs) > 1:
        raise ContractViolation("spec.reference_ambiguous", "more than one active delta claims structural authority")
    if len(referenced_specs) == 1 and len(owning_specs) == 1:
        return
    if owning_specs:
        raise ContractViolation("spec.reference_missing", f"pending owning delta lacks {SPEC_REFERENCE!r}")

    archived_specs = root.glob("openspec/changes/archive/*/specs/project-structure/spec.md")
    if any(SPEC_REFERENCE in path.read_text(encoding="utf-8") for path in archived_specs):
        raise ContractViolation("spec.archived_only", "an archived delta cannot be the active structural authority")
    raise ContractViolation("spec.reference_missing", "no lifecycle-appropriate project-structure spec was found")


def _validate_required_paths(root: Path, manifest: StructureManifest) -> None:
    for item in manifest.required_paths:
        path = root / item.path
        if not path.exists():
            raise ContractViolation("path.missing", f"required {item.kind} is missing: {item.path}")
        if item.kind == "file" and not path.is_file():
            raise ContractViolation("path.kind", f"required file is not a file: {item.path}")
        if item.kind == "directory" and not path.is_dir():
            raise ContractViolation("path.kind", f"required directory is not a directory: {item.path}")


def _validate_ignored_paths(root: Path, manifest: StructureManifest) -> None:
    path = root / manifest.ignored_path
    try:
        actual_entries = tuple(path.read_text(encoding="utf-8").splitlines())
    except (OSError, UnicodeError) as exc:
        raise ContractViolation("ignore.unreadable", f"cannot read ignored-path policy: {manifest.ignored_path}") from exc
    if actual_entries != manifest.ignored_entries:
        raise ContractViolation(
            "ignore.entries",
            f"ignore entries must exactly match the registered policy: {manifest.ignored_path}",
        )


def _validate_single_source_root(root: Path, manifest: StructureManifest) -> None:
    legacy_root = root / "agent"
    if legacy_root.exists() or legacy_root.is_symlink():
        raise ContractViolation(
            "source.compatibility_root",
            "legacy compatibility root is forbidden: agent",
        )

    source_parents = {manifest.source_root.parent: manifest.source_root.name}
    if manifest.fixture_root is not None:
        source_parents[manifest.fixture_root.parent] = manifest.fixture_root.name
    source_container = manifest.source_root.parent.parent
    registered_source_roots = set(source_parents)
    container_path = root / source_container
    if container_path.is_dir():
        for child in container_path.iterdir():
            candidate = PurePosixPath(child.relative_to(root).as_posix())
            if child.is_dir() and child.name.startswith("src") and candidate not in registered_source_roots:
                raise ContractViolation(
                    "source.unregistered_root",
                    f"unregistered Deep Research source root found: {candidate}",
                )
    for source_parent, package_name in source_parents.items():
        parent_path = root / source_parent
        if not parent_path.is_dir():
            continue
        for child in parent_path.iterdir():
            if child.name == "__pycache__" or not child.is_dir() or child.name == package_name:
                continue
            if (child / "__init__.py").is_file():
                raise ContractViolation(
                    "source.unregistered_root",
                    f"unregistered package under source root {source_parent}: {child.name}",
                )

    excluded = {
        PurePosixPath(".git"),
        PurePosixPath(".venv"),
        PurePosixPath("_backlog"),
        manifest.upstream_gitlink.path,
        PurePosixPath("frontend/.next"),
        PurePosixPath("node_modules"),
        PurePosixPath("openspec/changes/archive"),
        manifest.test_root / "fixtures",
    }

    def is_excluded(path: PurePosixPath) -> bool:
        return any(path == prefix or prefix in path.parents for prefix in excluded)

    for current, directories, _files in os.walk(root):
        relative_current = Path(current).relative_to(root)
        current_posix = PurePosixPath(relative_current.as_posix()) if relative_current.parts else PurePosixPath(".")
        directories[:] = [
            directory
            for directory in directories
            if not is_excluded(
                (current_posix / directory) if current_posix != PurePosixPath(".") else PurePosixPath(directory)
            )
        ]
        for directory in directories:
            registered_names = {manifest.source_root.name}
            if manifest.fixture_root is not None:
                registered_names.add(manifest.fixture_root.name)
            if directory not in registered_names:
                continue
            candidate = current_posix / directory if current_posix != PurePosixPath(".") else PurePosixPath(directory)
            if candidate == manifest.source_root or candidate == manifest.fixture_root:
                continue
            raise ContractViolation("source.second_root", f"non-canonical package source root found: {candidate}")


def _run_git_metadata(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(arguments, check=False, capture_output=True, text=True)
    except OSError as exc:
        raise ContractViolation("gitlink.command_unavailable", "cannot execute required upstream gitlink metadata command") from exc


def _validate_upstream_gitlink(root: Path, manifest: StructureManifest) -> None:
    """Validate only the declared gitlink's filesystem and Git metadata.

    @impl PRS-018
    """

    boundary = root / manifest.upstream_gitlink.path
    try:
        boundary_stat = boundary.lstat()
    except OSError as exc:
        raise ContractViolation("gitlink.path_missing", f"cannot inspect upstream gitlink path: {manifest.upstream_gitlink.path}") from exc
    if stat.S_ISLNK(boundary_stat.st_mode):
        raise ContractViolation("gitlink.path_symlink", f"upstream gitlink path is a symlink: {manifest.upstream_gitlink.path}")
    if not stat.S_ISDIR(boundary_stat.st_mode):
        raise ContractViolation("gitlink.path_kind", f"upstream gitlink path is not a directory: {manifest.upstream_gitlink.path}")
    try:
        (boundary / ".git").lstat()
    except OSError as exc:
        raise ContractViolation("gitlink.nested_metadata", "upstream gitlink lacks nested Git metadata") from exc

    index_command = [
        "git",
        "-C",
        str(root),
        "ls-files",
        "--stage",
        "-z",
        "--",
        manifest.upstream_gitlink.path.as_posix(),
    ]
    index_result = _run_git_metadata(index_command)
    if index_result.returncode != 0:
        raise ContractViolation("gitlink.index_query", "cannot inspect upstream gitlink index entry")
    records = [record for record in index_result.stdout.split("\0") if record]
    if len(records) != 1:
        raise ContractViolation("gitlink.index_shape", "upstream gitlink index entry must be exactly one stage-zero record")
    entry_match = re.fullmatch(r"(\d{6}) ([0-9a-f]{40}) (\d)\t(.+)", records[0])
    if entry_match is None:
        raise ContractViolation("gitlink.index_shape", "upstream gitlink index entry is malformed")
    mode, index_commit, stage, index_path = entry_match.groups()
    if index_path != manifest.upstream_gitlink.path.as_posix() or stage != "0":
        raise ContractViolation("gitlink.index_shape", "upstream gitlink index entry must be stage zero at the declared path")
    if mode != "160000":
        raise ContractViolation("gitlink.index_entry", "upstream index entry must have gitlink mode 160000")
    if index_commit != manifest.upstream_gitlink.commit:
        raise ContractViolation("gitlink.index_commit", "upstream gitlink index commit differs from the declared lock")

    nested_root = str(boundary)
    head_command = ["git", "-C", nested_root, "rev-parse", "--verify", "HEAD"]
    head_result = _run_git_metadata(head_command)
    if head_result.returncode != 0:
        raise ContractViolation("gitlink.head_query", "cannot resolve upstream gitlink HEAD")
    head_commit = head_result.stdout.strip()
    if not GIT_COMMIT_RE.fullmatch(head_commit):
        raise ContractViolation("gitlink.head_query", "upstream gitlink HEAD output is malformed")
    if head_commit != manifest.upstream_gitlink.commit:
        raise ContractViolation("gitlink.head_commit", "upstream gitlink HEAD differs from the declared lock")

    status_command = ["git", "-C", nested_root, "status", "--porcelain=v1", "--untracked-files=all"]
    status_result = _run_git_metadata(status_command)
    if status_result.returncode != 0:
        raise ContractViolation("gitlink.status_query", "cannot inspect upstream gitlink cleanliness")
    if status_result.stdout:
        raise ContractViolation("gitlink.status_dirty", "upstream gitlink worktree is not clean")


def _python_files(base: Path) -> list[Path]:
    if not base.is_dir():
        return []
    excluded_names = {".git", ".venv", "venv", "node_modules", ".next", "__pycache__"}
    files: list[Path] = []
    for current, directories, names in os.walk(base):
        directories[:] = sorted(directory for directory in directories if directory not in excluded_names)
        files.extend(Path(current) / name for name in sorted(names) if name.endswith(".py"))
    return files


def _module_parts(source_root: Path, path: Path) -> tuple[str, ...]:
    parts = list(path.relative_to(source_root).with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return tuple(parts)


def _resolved_imports(
    tree: ast.AST,
    module_parts: tuple[str, ...],
    is_package: bool,
    *,
    package_name: str = PACKAGE_NAME,
) -> list[str]:
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
            continue
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.level:
            package_parts = module_parts if is_package else module_parts[:-1]
            ascend = node.level - 1
            if ascend > len(package_parts):
                imports.append("")
                continue
            base_parts = package_parts[: len(package_parts) - ascend]
            module_suffix = tuple(node.module.split(".")) if node.module else ()
            resolved_parts = (package_name, *base_parts, *module_suffix)
        else:
            resolved_parts = tuple(node.module.split(".")) if node.module else ()
        if not resolved_parts:
            imports.append("")
            continue
        for alias in node.names:
            suffix = () if alias.name == "*" else tuple(alias.name.split("."))
            imports.append(".".join((*resolved_parts, *suffix)))
    return imports


def _source_owner(relative: PurePosixPath) -> tuple[str, str | None]:
    parts = relative.parts
    if not parts:
        return "package", None
    if parts[0] == "graph" and len(parts) >= 3 and parts[1] == "nodes":
        return "nodes", parts[2]
    if parts[0] in {"domain", "engine", "agents", "graph", "runtime"}:
        return parts[0], None
    if len(parts) == 1 and parts[0] == "tool.py":
        return "tool", None
    return "package", None


def _target_owner(module_name: str) -> tuple[str | None, str | None]:
    parts = module_name.split(".")
    if not parts or parts[0] != PACKAGE_NAME:
        return None, None
    if len(parts) == 1:
        return "package", None
    if parts[1] == "graph" and len(parts) >= 4 and parts[2] == "nodes":
        return "nodes", parts[3]
    if parts[1] in {"domain", "engine", "agents", "graph", "runtime"}:
        return parts[1], None
    return "package", None


def _external_allowed(
    layer: str,
    module_root: str,
    manifest: StructureManifest,
    relative: PurePosixPath,
) -> bool:
    if module_root in sys.stdlib_module_names or module_root == "__future__":
        return True
    if module_root == "openai":
        return layer == "runtime" and relative == PurePosixPath("runtime/node_agent_bridge.py")
    if module_root == "httpx":
        return layer == "runtime" and relative in {
            PurePosixPath("runtime/node_agent_bridge.py"),
            PurePosixPath("runtime/gateway_observer.py"),
        }
    if module_root == "httpx_sse":
        return layer == "runtime" and relative == PurePosixPath("runtime/gateway_observer.py")
    allowed = set(manifest.imports.get(layer, ())) - INTERNAL_LAYERS - {"stdlib"}
    if layer == "tool":
        allowed = {"langchain", "pydantic"}
    if layer == "package":
        allowed = set()
    return any(module_root == prefix or module_root.startswith(f"{prefix}_") for prefix in allowed)


def _validate_module_imports(
    root: Path,
    source_root: Path,
    path: Path,
    manifest: StructureManifest,
) -> None:
    relative = PurePosixPath(path.relative_to(source_root).as_posix())
    if path.stem in manifest.forbidden_shared_modules:
        raise ContractViolation("module.generic", f"generic shared module is forbidden: {path.relative_to(root)}")
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, UnicodeError, SyntaxError) as exc:
        raise ContractViolation("import.syntax", f"cannot parse {path.relative_to(root)}: {exc}") from exc

    layer, source_node = _source_owner(relative)
    module_parts = _module_parts(source_root, path)
    for imported in _resolved_imports(tree, module_parts, path.name == "__init__.py"):
        if not imported:
            raise ContractViolation("import.boundary", f"invalid relative import in {path.relative_to(root)}")
        module_root = imported.split(".", 1)[0]
        if manifest.fixture_package is not None and module_root == manifest.fixture_package:
            raise ContractViolation(
                "import.fixture_reverse",
                f"production source imports fixture package: {path.relative_to(root)}",
            )
        if module_root == "app":
            raise ContractViolation("import.app", f"production downstream code imports app.*: {path.relative_to(root)}")

        target_layer, target_node = _target_owner(imported)
        if target_layer is None:
            if layer == "nodes" and module_root == "langgraph":
                hitl_interrupt = (
                    source_node in {"hitl1", "hitl2"}
                    and path.name == "node.py"
                    and imported == "langgraph.types.interrupt"
                )
                if path.name != "subgraph.py" and not hitl_interrupt:
                    raise ContractViolation(
                        "import.boundary",
                        "node LangGraph import is outside subgraph/HITL-interrupt exceptions: "
                        f"{path.relative_to(root)}",
                    )
            if not _external_allowed(layer, module_root, manifest, relative):
                raise ContractViolation(
                    "import.external",
                    f"{path.relative_to(root)} imports undeclared external namespace {module_root}",
                )
            continue

        if layer == "nodes" and target_layer == "nodes":
            if target_node != source_node:
                raise ContractViolation(
                    "import.sibling",
                    f"node {source_node} imports sibling node {target_node}: {path.relative_to(root)}",
                )
            continue
        if layer == "nodes" and target_layer == "graph":
            component_prefix = f"{PACKAGE_NAME}.graph.components"
            if path.name == "subgraph.py" and (
                imported == component_prefix or imported.startswith(f"{component_prefix}.")
            ):
                continue
        if target_layer == layer or (layer == "package" and target_layer == "package"):
            continue
        if layer == "tool":
            allowed_internal = {"runtime"}
        elif layer == "package":
            allowed_internal = set()
        else:
            allowed_internal = set(manifest.imports[layer]) & INTERNAL_LAYERS
        if target_layer not in allowed_internal:
            raise ContractViolation(
                "import.boundary",
                f"{layer} module {path.relative_to(root)} imports forbidden {target_layer} module {imported}",
            )


def _validate_upstream_does_not_import_downstream(root: Path, manifest: StructureManifest) -> None:
    for upstream_root in manifest.forbidden_source_roots:
        for path in _python_files(root / upstream_root):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except (OSError, UnicodeError, SyntaxError) as exc:
                raise ContractViolation("import.syntax", f"cannot parse {path.relative_to(root)}: {exc}") from exc
            for node in ast.walk(tree):
                if isinstance(node, ast.Import) and any(
                    alias.name.split(".", 1)[0] == PACKAGE_NAME for alias in node.names
                ):
                    raise ContractViolation(
                        "source.upstream_import",
                        f"upstream module imports downstream package: {path.relative_to(root)}",
                    )
                if isinstance(node, ast.ImportFrom) and (node.module or "").split(".", 1)[0] == PACKAGE_NAME:
                    raise ContractViolation(
                        "source.upstream_import",
                        f"upstream module imports downstream package: {path.relative_to(root)}",
                    )


def _static_all_exports(path: Path) -> list[str] | None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, UnicodeError, SyntaxError) as exc:
        raise ContractViolation("import.syntax", f"cannot parse {path}: {exc}") from exc
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(isinstance(target, ast.Name) and target.id == "__all__" for target in targets):
            continue
        value = node.value
        if not isinstance(value, (ast.List, ast.Tuple)):
            return None
        exports: list[str] = []
        for element in value.elts:
            if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
                return None
            exports.append(element.value)
        return exports
    return None


def _validate_node_packages(root: Path, manifest: StructureManifest) -> None:
    node_root = root / manifest.node_root
    if not node_root.exists():
        return
    if not node_root.is_dir():
        raise ContractViolation("node.root_kind", f"node root is not a directory: {manifest.node_root}")
    reserved = {"components", "topology"}
    for package_root in sorted(path for path in node_root.iterdir() if path.is_dir() and path.name != "__pycache__"):
        relative = package_root.relative_to(root)
        if package_root.name in reserved:
            raise ContractViolation(
                "node.package_confusion",
                f"reusable components/topology cannot be top-level nodes: {relative}",
            )
        missing = sorted(name for name in manifest.node_required_files if not (package_root / name).is_file())
        if missing:
            raise ContractViolation(
                "node.file_missing",
                f"node package {relative} is missing {', '.join(missing)}",
            )
        exports = _static_all_exports(package_root / "__init__.py")
        if exports != [manifest.node_public_export]:
            raise ContractViolation(
                "node.exports",
                f"node package {relative} must export only {manifest.node_public_export}",
            )
        for forbidden_file in manifest.node_forbidden_files:
            if (package_root / forbidden_file).is_file():
                raise ContractViolation(
                    "node.fixture_file",
                    f"production node package contains a fixture adapter: {relative / forbidden_file}",
                )


def _fixture_production_import_is_allowed(imported: str, manifest: StructureManifest) -> bool:
    allowed = (*manifest.fixture_production_contracts, manifest.fixture_recipe_class)
    return any(
        candidate is not None and (imported == candidate or imported.startswith(f"{candidate}."))
        for candidate in allowed
    )


def _validate_fixture_recipe_references(
    root: Path,
    path: Path,
    tree: ast.AST,
    manifest: StructureManifest,
) -> None:
    if manifest.fixture_recipe_class is None:
        return
    recipe_module, recipe_class_name = manifest.fixture_recipe_class.rsplit(".", 1)
    aliases: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or node.level or node.module != recipe_module:
            continue
        aliases.update(alias.asname or alias.name for alias in node.names if alias.name == recipe_class_name)
    if not aliases:
        return

    parents = {
        id(child): parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }
    for node in ast.walk(tree):
        if not isinstance(node, ast.Name) or node.id not in aliases:
            continue
        parent = parents.get(id(node))
        is_allowed_direct_call = (
            isinstance(node.ctx, ast.Load)
            and isinstance(parent, ast.Attribute)
            and parent.value is node
            and parent.attr in manifest.fixture_recipe_factories
            and isinstance(parents.get(id(parent)), ast.Call)
            and parents[id(parent)].func is parent
        )
        if is_allowed_direct_call:
            continue
        factories = ", ".join(manifest.fixture_recipe_factories)
        raise ContractViolation(
            "fixture.recipe_factory",
            f"fixture source may only call {manifest.fixture_recipe_class}.{factories}: {path.relative_to(root)}",
        )


def _validate_fixture_imports(root: Path, manifest: StructureManifest) -> None:
    if manifest.fixture_root is None or manifest.fixture_package is None:
        return
    fixture_root = root / manifest.fixture_root
    if not fixture_root.is_dir():
        raise ContractViolation("path.missing", f"fixture source root is missing: {manifest.fixture_root}")
    for path in _python_files(fixture_root):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, UnicodeError, SyntaxError) as exc:
            raise ContractViolation("import.syntax", f"cannot parse {path.relative_to(root)}: {exc}") from exc
        module_parts = _module_parts(fixture_root, path)
        for imported in _resolved_imports(
            tree,
            module_parts,
            path.name == "__init__.py",
            package_name=manifest.fixture_package,
        ):
            if not imported:
                raise ContractViolation("import.boundary", f"invalid relative import in {path.relative_to(root)}")
            module_root = imported.split(".", 1)[0]
            if module_root == manifest.fixture_package:
                continue
            if module_root == PACKAGE_NAME:
                if _fixture_production_import_is_allowed(imported, manifest):
                    continue
                raise ContractViolation(
                    "import.fixture_production",
                    f"fixture source imports an unregistered production contract {imported}: {path.relative_to(root)}",
                )
            if (
                module_root in sys.stdlib_module_names
                or module_root == "__future__"
                or module_root in manifest.fixture_external_namespaces
            ):
                continue
            raise ContractViolation(
                "import.fixture_external",
                f"fixture source imports undeclared namespace {module_root}: {path.relative_to(root)}",
            )
        _validate_fixture_recipe_references(root, path, tree, manifest)


def _validate_production_wheel(root: Path, manifest: StructureManifest) -> None:
    if manifest.fixture_root is None:
        return
    pyproject = root / manifest.source_root.parent.parent / "pyproject.toml"
    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        packages = data["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"]
    except (KeyError, OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ContractViolation("package.wheel_config", "cannot inspect production wheel package configuration") from exc
    expected = ["src/deerflow_deep_research"]
    if packages != expected:
        raise ContractViolation("package.fixture_included", "production wheel must package only src/deerflow_deep_research")


def validate_imports(root: Path, manifest: StructureManifest) -> None:
    source_root = root / manifest.source_root
    if not source_root.is_dir():
        raise ContractViolation("path.missing", f"source root is missing: {manifest.source_root}")
    for path in _python_files(source_root):
        _validate_module_imports(root, source_root, path, manifest)
    _validate_fixture_imports(root, manifest)
    _validate_production_wheel(root, manifest)
    _validate_upstream_does_not_import_downstream(root, manifest)
    _validate_node_packages(root, manifest)


def validate_project(root: Path, manifest: StructureManifest) -> None:
    _validate_spec_authority(root, manifest)
    _validate_guide(root, manifest)
    _validate_required_paths(root, manifest)
    _validate_ignored_paths(root, manifest)
    _validate_single_source_root(root, manifest)
    validate_imports(root, manifest)
    _validate_upstream_gitlink(root, manifest)


def check_project(root: Path, *, imports_only: bool = False) -> None:
    """Validate one repository through the same seam used by the CLI.

    @impl DER-002
    """
    manifest = load_manifest(root)
    if imports_only:
        validate_imports(root, manifest)
    else:
        validate_project(root, manifest)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument(
        "--imports-only",
        action="store_true",
        help="validate only manifest and Python import contracts",
    )
    parser.add_argument(
        "--render-guide",
        action="store_true",
        help="print the deterministic AGENTS.md structure-locator block",
    )
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    try:
        if args.render_guide:
            manifest = load_manifest(root)
            print(render_guide_block(manifest), end="")
            return 0
        check_project(root, imports_only=args.imports_only)
    except ContractViolation as violation:
        print(f"ERROR [{violation.code}] {violation.detail}", file=sys.stderr)
        return 1
    print(f"Architecture governance passed for {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
