#!/usr/bin/env python3
"""Generate or verify the deterministic node-prompt review catalog.

The catalog is a generated review projection. It never drives execution and this
adapter never resolves a model, tool, runtime configuration, or network resource.

@impl NPC-002
@impl NPC-003
@impl PRS-011
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path, PurePosixPath

AGENT_ROOT = Path(__file__).resolve().parents[1]
CATALOG_ROOT = AGENT_ROOT / ".node-prompt-review"
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from deerflow_deep_research.agents.node_cognitive_control_program import (  # noqa: E402
    render_node_cognitive_control_program,
)
from deerflow_deep_research.domain.context import NodeExecutionRequest  # noqa: E402
from deerflow_deep_research.graph.prompt_catalog import PromptCatalogCase, prompt_catalog_cases  # noqa: E402

_BACKTICK_RUN = re.compile(r"`+")


class PromptDumpError(RuntimeError):
    """A bounded catalog-generation or freshness failure."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def fenced_literal_prompt(content: str) -> str:
    """Return literal Markdown whose fence cannot be closed by prompt content."""

    if not isinstance(content, str):
        raise TypeError("prompt_content_invalid")
    longest_backtick_run = max((len(match.group()) for match in _BACKTICK_RUN.finditer(content)), default=0)
    fence = "`" * max(3, longest_backtick_run + 1)
    suffix = "" if content.endswith("\n") else "\n"
    return f"{fence}\n{content}{suffix}{fence}\n"


def _safe_catalog_path(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise PromptDumpError("catalog_path_invalid", "generated relative path must be a contained Markdown path")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or not path.parts
        or any(part in {"", ".", ".."} for part in path.parts)
        or path.suffix != ".md"
    ):
        raise PromptDumpError("catalog_path_invalid", "generated relative path must be a contained Markdown path")
    return path.as_posix()


def _add_file(files: dict[str, str], *, path: str, content: str) -> None:
    safe_path = _safe_catalog_path(path)
    if safe_path in files:
        raise PromptDumpError("catalog_path_duplicate", f"duplicate generated path: {safe_path}")
    if not content.endswith("\n"):
        raise PromptDumpError("catalog_content_invalid", f"generated content must end with a newline: {safe_path}")
    files[safe_path] = content


def _requested_tool_policy(request: NodeExecutionRequest) -> str:
    call_limit = "unbounded by this request" if request.tool_call_limit is None else str(request.tool_call_limit)
    return (
        "## Requested Tool Policy\n\n"
        "This is request policy, not a runtime-resolved tool inventory.\n\n"
        f"- Tools enabled: `{str(request.tools_enabled).lower()}`\n"
        f"- Minimum tool calls: `{request.minimum_tool_calls}`\n"
        f"- Tool-call limit: `{call_limit}`\n"
    )


def _capability_projection(capability: object) -> str:
    ref = capability.ref
    posture = capability.posture
    names = ", ".join(f"`{name}`" for name in sorted(posture.allowed_tool_names)) or "none"
    return (
        "## Node Cognitive Control Program\n\n"
        f"- Capability ID: `{ref.capability_id}`\n"
        f"- Local source: `{ref.package}:{ref.resource}`\n"
        f"- Declared tool posture: `{posture.kind}` ({names})\n\n"
        "## Composition\n\n"
        "1. Base safety policy\n"
        "2. Node-local capability policy\n"
        "3. Trusted assignment and output contract\n"
        "4. Delimited untrusted source/tool data\n\n"
    )


def _render_case(case: PromptCatalogCase) -> str:
    request = case.build_request()
    rendered = render_node_cognitive_control_program(request, attempt_workspace=case.attempt_workspace)
    return (
        f"# Node Prompt: `{case.case_id}`\n\n"
        "> Generated review artifact. It is a deterministic projection, not runtime authority.\n\n"
        "## Case\n\n"
        f"- Node: `{case.node_name}`\n"
        f"- Branch: `{case.branch}`\n"
        f"- Source builder: `{case.builder_id}`\n"
        f"- Variant: `{'repair' if case.is_repair else 'initial'}`\n\n"
        f"{_capability_projection(rendered.capability)}"
        "## Shared System Policy\n\n"
        f"{fenced_literal_prompt(rendered.system_policy)}\n"
        "## Final Human Message\n\n"
        f"{fenced_literal_prompt(rendered.user_message)}\n"
        f"{_requested_tool_policy(request)}"
    )


def _render_index(cases: tuple[PromptCatalogCase, ...]) -> str:
    rows = "\n".join(
        f"| [`{case.case_id}`]({case.output_path}) | `{case.node_name}` | `{case.branch}` | "
        f"`{'repair' if case.is_repair else 'initial'}` |"
        for case in cases
    )
    return (
        "# Node Prompt Review Catalog\n\n"
        "> Generated review artifact. It is a deterministic projection, not runtime authority.\n\n"
        "Each case uses code-owned synthetic fixtures. The individual files show the exact shared "
        "system policy and final human message used for review; requested tool policy is explicitly "
        "not a runtime-resolved tool inventory. Regenerate with `make prompt-dump`; verify without "
        "writing with `make prompt-dump-check`.\n\n"
        "| Case | Node | Branch | Variant |\n"
        "| --- | --- | --- | --- |\n"
        f"{rows}\n"
    )


def render_catalog_files() -> dict[str, str]:
    """Render the complete expected catalog in stable path order without I/O authority."""

    cases = tuple(prompt_catalog_cases())
    if tuple(case.case_id for case in cases) != tuple(sorted(case.case_id for case in cases)):
        raise PromptDumpError("catalog_cases_unsorted", "canonical cases must be ordered by case id")
    files: dict[str, str] = {}
    _add_file(files, path="README.md", content=_render_index(cases))
    for case in cases:
        _add_file(files, path=case.output_path, content=_render_case(case))
    return {path: files[path] for path in sorted(files)}


def _catalog_target(relative_path: str) -> Path:
    safe_path = _safe_catalog_path(relative_path)
    target = CATALOG_ROOT.joinpath(*PurePosixPath(safe_path).parts)
    try:
        target.relative_to(CATALOG_ROOT)
    except ValueError as exc:
        raise PromptDumpError("catalog_path_invalid", "generated path escapes the fixed catalog root") from exc
    return target


def _scan_catalog_tree(root: Path) -> tuple[set[str], set[str]]:
    if root.is_symlink():
        raise PromptDumpError("catalog_symlink", "catalog root must not be a symbolic link")
    if not root.exists():
        raise PromptDumpError("catalog_missing", "catalog root is missing")
    if not root.is_dir():
        raise PromptDumpError("catalog_root_invalid", "catalog root must be a directory")

    files: set[str] = set()
    directories: set[str] = set()

    def visit(directory: Path, prefix: str) -> None:
        try:
            entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
        except OSError as exc:
            raise PromptDumpError("catalog_tree_unreadable", "catalog tree cannot be read") from exc
        for entry in entries:
            relative_path = entry.name if not prefix else f"{prefix}/{entry.name}"
            if entry.is_symlink():
                raise PromptDumpError("catalog_symlink", f"catalog path is a symbolic link: {relative_path}")
            if entry.is_dir(follow_symlinks=False):
                directories.add(relative_path)
                visit(Path(entry.path), relative_path)
            elif entry.is_file(follow_symlinks=False):
                files.add(relative_path)
            else:
                raise PromptDumpError(
                    "catalog_path_invalid",
                    f"catalog path is not a regular file or directory: {relative_path}",
                )

    visit(root, "")
    return files, directories


def _reject_non_markdown_paths(files: set[str]) -> None:
    for relative_path in files:
        if PurePosixPath(relative_path).suffix != ".md":
            raise PromptDumpError("catalog_non_markdown_path", f"unexpected non-Markdown path: {relative_path}")


def _expected_parent_directories(expected_files: dict[str, str]) -> set[str]:
    directories: set[str] = set()
    for relative_path in expected_files:
        parts = PurePosixPath(relative_path).parts[:-1]
        for index in range(1, len(parts) + 1):
            directories.add("/".join(parts[:index]))
    return directories


def check_catalog() -> tuple[str, ...]:
    """Read-only verification that the fixed catalog tree equals deterministic output."""

    expected_files = render_catalog_files()
    actual_files, actual_directories = _scan_catalog_tree(CATALOG_ROOT)
    _reject_non_markdown_paths(actual_files)
    expected_paths = set(expected_files)
    expected_directories = _expected_parent_directories(expected_files)
    if actual_files != expected_paths or actual_directories != expected_directories:
        raise PromptDumpError("catalog_tree_mismatch", "catalog paths do not exactly match generated output")
    for relative_path, content in expected_files.items():
        try:
            actual = _catalog_target(relative_path).read_bytes()
        except OSError as exc:
            raise PromptDumpError("catalog_tree_unreadable", f"catalog file cannot be read: {relative_path}") from exc
        if actual != content.encode("utf-8"):
            raise PromptDumpError("catalog_content_stale", f"catalog file differs: {relative_path}")
    return tuple(expected_files)


def _prune_empty_directories(root: Path) -> None:
    paths = sorted(
        (path for path in root.rglob("*") if path.is_dir() and not path.is_symlink()),
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for path in paths:
        try:
            path.rmdir()
        except OSError:
            continue


def write_catalog() -> tuple[str, ...]:
    """Refresh only the fixed generated Markdown catalog, refusing unsafe paths."""

    expected_files = render_catalog_files()
    if CATALOG_ROOT.is_symlink():
        raise PromptDumpError("catalog_symlink", "catalog root must not be a symbolic link")
    if CATALOG_ROOT.exists():
        actual_files, _ = _scan_catalog_tree(CATALOG_ROOT)
        _reject_non_markdown_paths(actual_files)
        for relative_path in actual_files - set(expected_files):
            _catalog_target(relative_path).unlink()
    else:
        CATALOG_ROOT.mkdir(parents=True)

    for relative_path, content in expected_files.items():
        target = _catalog_target(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            raise PromptDumpError("catalog_symlink", f"catalog path is a symbolic link: {relative_path}")
        target.write_bytes(content.encode("utf-8"))
    _prune_empty_directories(CATALOG_ROOT)
    return check_catalog()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify an existing local review catalog without writing")
    args = parser.parse_args(argv)
    try:
        paths = check_catalog() if args.check else write_catalog()
    except PromptDumpError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    action = "checked" if args.check else "generated"
    print(f"Prompt catalog {action}: {len(paths)} Markdown files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
