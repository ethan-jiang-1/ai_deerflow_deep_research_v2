#!/usr/bin/env python3
# check_project_specs.py — 项目级 OpenSpec main specs 结构 + req 追踪检查（只读，不修改）
# Usage: python3 check_project_specs.py [projectRoot] [--change <name>]
#
# 借鉴自 deep-research 的 check-project-specs.mjs，逻辑等价、技术栈换成本仓库的 Python 标准库。
#
# 对齐 @fission-ai/openspec:
#   - openspec/specs/<capability>/spec.md 是 main spec，必须有 ## Purpose 和 ## Requirements
#   - delta headers (## ADDED/MODIFIED/REMOVED/RENAMED Requirements) 只对
#     openspec/changes/<name>/specs/<capability>/spec.md 合法
#   - main spec 的 requirement blocks 只在 ## Requirements 内被 parse/list/show
#
# 默认模式（无 --change）检查 openspec/specs/ 下的 main specs：
#   1. deltaHeaderInMain   — main spec 出现 delta 头 (OpenSpec 结构错误)
#   2. missingPurpose      — 缺少 ## Purpose 节
#   3. missingRequirements — 缺少 ## Requirements 节
#   4. missingReqHeader    — 缺少 > req: 行 (本项目 req-registry.yaml 追踪约定)
#
# --change <name> 模式（selected-change scope）只检查该 active change 的 delta specs，
# 不检查 main specs：
#   5. missingDeltaReqHeader — delta spec 在首个 ## 前缺少声明 owned requirement IDs
#      的 > req: 行
#   6. titleEmbeddedId       — Requirement 标题（### Requirement: ...）内嵌 requirement ID
#
# zero-delta opt-out（对齐原生 OpenSpec schema）：行为不变的纯重构/tooling/docs 可在
# `.openspec.yaml` 设 `skip_specs: true`，此时无 delta spec 合法。标记只有在元数据是
# 合法扁平映射、声明已知 schema、且 skip_specs 为布尔 true 时才被认可；否则 fail closed。
# 这不适用于"无标记却零 delta"的 change——那仍然 fail closed。
#
# 与原 .mjs 的一处有意改进（面向长期）: 当 openspec/specs/ 下尚无任何 spec.md 时，
# 原脚本 exit 1（视为错误）。本仓库从空起步，这里改为 exit 0 + 明确提示——"没有 spec
# 就没有可违反的结构"，避免第一个 change 落地前 `check` 无谓失败。有了 spec 后行为一致。

import argparse
import re
import sys
from pathlib import Path

# Delta headers 只在 openspec/changes/ 合法，不许出现在 openspec/specs/。
DELTA_HEADER_RE = re.compile(r"^##\s+(ADDED|MODIFIED|REMOVED|RENAMED)\s+Requirements\s*$", re.IGNORECASE | re.MULTILINE)
PURPOSE_HEADER_RE = re.compile(r"^##\s+Purpose\s*$", re.IGNORECASE | re.MULTILINE)
REQUIREMENTS_HEADER_RE = re.compile(r"^##\s+Requirements\s*$", re.IGNORECASE | re.MULTILINE)
REQ_TRACE_RE = re.compile(r"^> req:\s*[A-Z]{3}-\d{3}")
REQ_HEADER_RE = re.compile(r"^\s*>\s*req:\s*(.+)$")
ID_SCAN_RE = re.compile(r"[A-Z]{3}-\d{3}")
REQUIREMENT_TITLE_RE = re.compile(r"^###\s+Requirement:\s+(.+)$", re.IGNORECASE)
ID_IN_TEXT_RE = re.compile(r"[A-Z]{3}-\d{3}")
ARCHIVE_PLACEHOLDER_PURPOSE_RE = re.compile(r"^TBD\s*-\s*created by archiving", re.IGNORECASE)
METADATA_LINE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([^#]*?)\s*(?:#.*)?$")
KNOWN_SCHEMAS = frozenset({"spec-driven"})
ACTIVE_TERMINOLOGY_RULES = {
    "numberedChange": re.compile(r"\bchange[- ]?\d+\b", re.IGNORECASE),
    "skeleton": re.compile(r"\bskeleton(?:_state| state)?\b", re.IGNORECASE),
    "phaseRoadmap": re.compile(r"\b(?:later wave|phase-roadmap|remain fake|still fake)\b", re.IGNORECASE),
    "temporaryStandalone": re.compile(r"\btemporary standalone\b", re.IGNORECASE),
    "mislabelledMode": re.compile(r"implementation_mode=full_fake[^\n]*(?:mixed|all.real)", re.IGNORECASE),
}


def strip_fenced_code_blocks(content: str) -> str:
    """把围栏代码块内容替换成空行，保持行号，避免代码示例里的 ## 头被误判。"""
    lines = content.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    output = []
    active = None
    for line in lines:
        m = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if active is None:
            if m:
                active = (m.group(1)[0], len(m.group(1)))
                output.append("")
            else:
                output.append(line)
            continue
        output.append("")
        closing = re.match(r"^\s*(`{3,}|~{3,})\s*$", line)
        if closing and closing.group(1)[0] == active[0] and len(closing.group(1)) >= active[1]:
            active = None
    return "\n".join(output)


def has_req_trace_before_second_heading(content: str) -> bool:
    """`> req:` 行必须出现在首个二级标题之前。

    Fenced code blocks are stripped first, consistent with `_delta_header_ids`:
    a fake `> req:` inside a code fence must never satisfy the header rule.
    """
    seen_first_heading = False
    for line in strip_fenced_code_blocks(content).split("\n"):
        if REQ_TRACE_RE.search(line):
            return not seen_first_heading
        if re.match(r"^##\s+", line):
            seen_first_heading = True
    return False


def _delta_spec_files(change_dir: Path) -> list[Path]:
    """Collect every spec.md under a change's specs/ tree (empty when none)."""
    specs_dir = change_dir / "specs"
    if not specs_dir.is_dir():
        return []
    collected: list[Path] = []
    collect_spec_files(specs_dir, collected)
    return collected


def _skip_specs_marker(change_dir: Path) -> tuple[bool, str | None]:
    """Read the native zero-delta opt-out marker from `.openspec.yaml`.

    Returns ``(honored, invalid_reason)``. The marker is honored only when the
    metadata is a flat top-level mapping that declares a known schema and sets
    ``skip_specs`` to boolean ``true``. A missing key is simply "not marked"
    ``(False, None)``; a present-but-untrustworthy marker is unhonorable and
    fails closed, mirroring native OpenSpec. This intentionally parses only the
    flat scalar metadata this repository writes, and rejects nesting rather than
    guessing.
    """
    metadata = change_dir / ".openspec.yaml"
    if not metadata.is_file():
        return False, None
    try:
        text = metadata.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return False, "change metadata is unreadable"
    fields: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line[:1].isspace():
            return False, "change metadata is not a flat mapping"
        match = METADATA_LINE_RE.match(stripped)
        if not match:
            return False, "change metadata is not a flat mapping"
        key, value = match.group(1), match.group(2).strip()
        if key in fields:
            return False, f"change metadata repeats key '{key}'"
        fields[key] = value
    if fields.get("schema") not in KNOWN_SCHEMAS:
        return False, "change metadata does not declare a known schema"
    if "skip_specs" not in fields:
        return False, None
    value = fields["skip_specs"]
    if value == "true":
        return True, None
    if value == "false":
        return False, None
    return False, "skip_specs is not a boolean"


def _delta_header_ids(content: str) -> set[str]:
    """Requirement IDs declared on `> req:` lines before the first `##` heading."""
    declared: set[str] = set()
    for line in strip_fenced_code_blocks(content).split("\n"):
        if re.match(r"^##\s+", line):
            break
        m = REQ_HEADER_RE.match(line)
        if m:
            declared.update(ID_SCAN_RE.findall(m.group(1)))
    return declared


def _requirement_title_id_violations(content: str) -> list[str]:
    """Requirement titles are stable semantic anchors and SHALL NOT embed IDs."""
    found: list[str] = []
    for line_number, line in enumerate(content.split("\n"), start=1):
        m = REQUIREMENT_TITLE_RE.match(line.strip())
        if not m:
            continue
        embedded = ID_IN_TEXT_RE.findall(m.group(1))
        if embedded:
            found.append(
                f"requirement title embeds requirement ID(s) {', '.join(sorted(set(embedded)))} "
                f"(title is a semantic anchor; IDs live on the `> req:` line)"
            )
    return found


def validate_selected_change_delta_specs(root: Path, change_name: str) -> tuple[list[dict], int]:
    """Selected-change scope: validate one active change's delta specs only.

    Returns (violations, exit_code). Missing or non-active change fails
    closed, and an existing active change with NO delta spec files (or no
    specs/ directory at all) fails closed with `selectedChangeEmpty` — an
    empty scan must not be reported as a pass. A valid `skip_specs: true`
    zero-delta opt-out is the one exception; an unhonorable marker still fails
    closed with `selectedChangeSkipSpecsInvalid`.

    @impl EVH-005
    @impl PRS-009
    """
    change_dir = root / "openspec" / "changes" / change_name
    if not change_dir.is_dir():
        return (
            [{"file": str(change_dir), "check": "selectedChangeMissing",
              "detail": f"active change not found: {change_name}", "line": None}],
            1,
        )
    delta_files = _delta_spec_files(change_dir)
    if not delta_files:
        honored, invalid = _skip_specs_marker(change_dir)
        if honored:
            return [], 0
        if invalid:
            return (
                [{"file": str(change_dir / ".openspec.yaml"), "check": "selectedChangeSkipSpecsInvalid",
                  "detail": (
                      f"active change {change_name} has no delta spec files and its "
                      f"skip_specs marker is unhonorable: {invalid}"
                  ), "line": None}],
                1,
            )
        return (
            [{"file": str(change_dir / "specs"), "check": "selectedChangeEmpty",
              "detail": f"active change {change_name} has no delta spec files (empty scan fails closed)", "line": None}],
            1,
        )
    violations: list[dict] = []
    for file in delta_files:
        content = file.read_text(encoding="utf-8")
        short = str(file).replace(str(root) + "/", "")
        if not has_req_trace_before_second_heading(content):
            violations.append(
                {"file": short, "check": "missingDeltaReqHeader",
                 "detail": "delta spec lacks a > req: <ID> line before its first ## heading", "line": None}
            )
        for detail in _requirement_title_id_violations(content):
            violations.append({"file": short, "check": "titleEmbeddedId", "detail": detail, "line": None})
    return violations, 0


def _validate_main_specs(root: Path) -> int:
    specs_dir = root / "openspec" / "specs"

    if not specs_dir.exists():
        print(f"Specs directory not found: {specs_dir}", file=sys.stderr)
        return 1

    spec_files: list = []
    collect_spec_files(specs_dir, spec_files)

    if not spec_files:
        # 有意改进：空起步不算错误。
        print("No spec.md files yet under openspec/specs — nothing to validate (0 violations).")
        return 0

    violations = []  # {file, check, detail, line?}
    for file in spec_files:
        content = file.read_text(encoding="utf-8")
        structural = strip_fenced_code_blocks(content)
        short = str(file).replace(str(root) + "/", "")

        # 1. deltaHeaderInMain
        dm = DELTA_HEADER_RE.search(structural)
        if dm:
            structural_lines = structural.split("\n")
            line_num = next((i + 1 for i, l in enumerate(structural_lines) if DELTA_HEADER_RE.match(l)), None)
            violations.append({"file": short, "check": "deltaHeaderInMain",
                               "detail": f'main spec 包含 delta 头 "{dm.group(0).strip()}"（delta 头只在 openspec/changes/ 下合法）',
                               "line": line_num})

        # 2. missingPurpose
        if not PURPOSE_HEADER_RE.search(structural):
            violations.append({"file": short, "check": "missingPurpose", "detail": "缺少 ## Purpose 节", "line": None})

        # 3. missingRequirements
        if not REQUIREMENTS_HEADER_RE.search(structural):
            violations.append({"file": short, "check": "missingRequirements", "detail": "缺少 ## Requirements 节", "line": None})

        # 4. missingReqHeader（项目追踪约定，非 OpenSpec 原生字段）
        if not has_req_trace_before_second_heading(structural):
            violations.append({"file": short, "check": "missingReqHeader",
                               "detail": "缺少位于首个二级标题之前的 > req: <ID> 行（本项目 req-registry.yaml 追踪约定）",
                               "line": None})
        elif not purpose_is_current(structural):
            violations.append({"file": short, "check": "placeholderPurpose", "detail": "Purpose 为空或仍是 archive placeholder", "line": None})

    for violation in active_terminology_violations(root):
        violations.append(
            {
                "file": violation["file"],
                "check": "historicalTerminology",
                "detail": violation["rule"],
                "line": int(violation["line"]),
            }
        )

    if violations:
        labels = {
            "deltaHeaderInMain": "Delta header in main spec",
            "missingPurpose": "Missing ## Purpose section",
            "placeholderPurpose": "Empty or placeholder Purpose section",
            "missingRequirements": "Missing ## Requirements section",
            "missingReqHeader": "Missing > req: header",
            "historicalTerminology": "Historical terminology in active authority",
        }
        by_check: dict[str, list] = {}
        for v in violations:
            by_check.setdefault(v["check"], []).append(v)
        for check, items in by_check.items():
            print(f"{labels[check]} ({len(items)}):", file=sys.stderr)
            for item in items:
                loc = f":{item['line']}" if item.get("line") else ""
                print(f"  {item['file']}{loc}", file=sys.stderr)
        print(f"\n{len(violations)} violation(s) in {len(spec_files)} spec files.", file=sys.stderr)
        return 1

    print(f"All project specs valid: {len(spec_files)} main spec files under openspec/specs, 0 violations.")
    return 0


def purpose_is_current(content: str) -> bool:
    """Reject empty and archive-generated Purpose placeholders."""
    match = PURPOSE_HEADER_RE.search(content)
    if match is None:
        return False
    remainder = content[match.end() :]
    body = re.split(r"^##\s+", remainder, maxsplit=1, flags=re.MULTILINE)[0].strip()
    return bool(body) and ARCHIVE_PLACEHOLDER_PURPOSE_RE.match(body) is None


def collect_spec_files(dir_path: Path, sink: list):
    for entry in sorted(dir_path.iterdir(), key=lambda p: p.name):
        if entry.is_dir():
            collect_spec_files(entry, sink)
        elif entry.name == "spec.md":
            sink.append(entry)


def active_terminology_violations(root: Path) -> list[dict[str, str]]:
    """Reject archive-only language from current specification authority."""
    authority_paths = [
        *sorted((root / "openspec" / "specs").rglob("*.md")),
        root / "openspec" / "governance" / "req-registry.yaml",
        root / "deep_research_harness" / "AGENTS.md",
        root / "deep_research_harness" / "README.md",
        root / "deep_research_harness" / "config" / "public-skill" / "deep-research-controller" / "SKILL.md",
        root / "deep_research_harness" / "config" / "agent-template" / "SOUL.md",
    ]
    violations: list[dict[str, str]] = []
    for path in authority_paths:
        if not path.is_file():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for rule, pattern in ACTIVE_TERMINOLOGY_RULES.items():
                if pattern.search(line):
                    violations.append({"file": str(path.relative_to(root)), "rule": rule, "line": str(line_number)})
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        type=Path,
        default=Path("."),
        help="repository root (default: current working directory)",
    )
    parser.add_argument(
        "--change",
        metavar="NAME",
        default=None,
        help="validate only the named active change's delta specs (selected-change scope)",
    )
    args = parser.parse_args()
    root = args.project_root.resolve()

    if args.change is not None:
        violations, _exit = validate_selected_change_delta_specs(root, args.change)
        if violations:
            labels = {
                "selectedChangeMissing": "Selected active change missing",
                "selectedChangeEmpty": "Selected change has no delta spec files",
                "selectedChangeSkipSpecsInvalid": "Selected change skip_specs marker is unhonorable",
                "missingDeltaReqHeader": "Missing > req: header in delta spec",
                "titleEmbeddedId": "Requirement title embeds a requirement ID",
            }
            by_check: dict[str, list] = {}
            for v in violations:
                by_check.setdefault(v["check"], []).append(v)
            for check, items in by_check.items():
                print(f"{labels.get(check, check)} ({len(items)}):", file=sys.stderr)
                for item in items:
                    loc = f":{item['line']}" if item.get("line") else ""
                    print(f"  {item['file']}{loc}", file=sys.stderr)
            print(f"\n{len(violations)} violation(s) in selected change {args.change}.", file=sys.stderr)
            return 1
        print(f"Selected change {args.change} delta specs valid: {len(_delta_spec_files(root / 'openspec' / 'changes' / args.change))} spec file(s), 0 violations.")
        return 0

    return _validate_main_specs(root)


if __name__ == "__main__":
    sys.exit(main())
