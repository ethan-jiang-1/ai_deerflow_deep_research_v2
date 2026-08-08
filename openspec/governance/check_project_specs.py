#!/usr/bin/env python3
# check_project_specs.py — 项目级 OpenSpec main specs 结构 + req 追踪检查（只读，不修改）
# Usage: python3 check_project_specs.py [projectRoot]
#
# 借鉴自 deep-research 的 check-project-specs.mjs，逻辑等价、技术栈换成本仓库的 Python 标准库。
#
# 对齐 @fission-ai/openspec:
#   - openspec/specs/<capability>/spec.md 是 main spec，必须有 ## Purpose 和 ## Requirements
#   - delta headers (## ADDED/MODIFIED/REMOVED/RENAMED Requirements) 只对
#     openspec/changes/<name>/specs/<capability>/spec.md 合法
#   - main spec 的 requirement blocks 只在 ## Requirements 内被 parse/list/show
#
# 本脚本不检查 openspec/changes/ 下的 delta spec；那部分交给 OpenSpec validate/archive。
#
# 四项检查:
#   1. deltaHeaderInMain   — main spec 出现 delta 头 (OpenSpec 结构错误)
#   2. missingPurpose      — 缺少 ## Purpose 节
#   3. missingRequirements — 缺少 ## Requirements 节
#   4. missingReqHeader    — 缺少 > req: 行 (本项目 req-registry.yaml 追踪约定)
#
# 与原 .mjs 的一处有意改进（面向长期）: 当 openspec/specs/ 下尚无任何 spec.md 时，
# 原脚本 exit 1（视为错误）。本仓库从空起步，这里改为 exit 0 + 明确提示——"没有 spec
# 就没有可违反的结构"，避免第一个 change 落地前 `check` 无谓失败。有了 spec 后行为一致。

import re
import sys
from pathlib import Path

# Delta headers 只在 openspec/changes/ 合法，不许出现在 openspec/specs/。
DELTA_HEADER_RE = re.compile(r"^##\s+(ADDED|MODIFIED|REMOVED|RENAMED)\s+Requirements\s*$", re.IGNORECASE | re.MULTILINE)
PURPOSE_HEADER_RE = re.compile(r"^##\s+Purpose\s*$", re.IGNORECASE | re.MULTILINE)
REQUIREMENTS_HEADER_RE = re.compile(r"^##\s+Requirements\s*$", re.IGNORECASE | re.MULTILINE)
REQ_TRACE_RE = re.compile(r"^> req:\s*[A-Z]{3}-\d{3}")
ARCHIVE_PLACEHOLDER_PURPOSE_RE = re.compile(r"^TBD\s*-\s*created by archiving", re.IGNORECASE)
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
    """`> req:` 行必须出现在首个二级标题之前。"""
    seen_first_heading = False
    for line in content.split("\n"):
        if REQ_TRACE_RE.search(line):
            return not seen_first_heading
        if re.match(r"^##\s+", line):
            seen_first_heading = True
    return False


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
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
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


if __name__ == "__main__":
    sys.exit(main())
