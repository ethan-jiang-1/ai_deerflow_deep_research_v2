#!/usr/bin/env python3
"""Operator-only Soft Bundle CLI.

This CLI is a thin wrapper around existing Deep Research operator entry points.
It gives each local research run a stateless ``soft_bundle_root`` handle and
records only repository-relative local record locations. It never changes the
product ``deep_research`` tool contract and never treats paths/records as
lifecycle authority.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
RUNS_ROOT = HARNESS / ".deep-research-demo-runs" / "workspace"
DEFAULT_SOFT_BUNDLES_ROOT = RUNS_ROOT / "soft-bundles"

BUNDLE_ID_RE = re.compile(r"^b_[A-Za-z0-9_-]{20,}$")
MANIFEST_NAME = "manifest.json"
BUNDLES_SUBDIR = "bundles"
SCHEMA_VERSION = 1
DEFAULT_QUESTION = "What is the capital of France?"
MODE_QUESTIONS = {
    "001": "What is the capital of France?",
    "002": "What is one bounded fact about grid energy storage?",
}
REQUIRED_TRACE = (
    "bootstrap",
    "hitl1",
    "topic_planning",
    "wave0",
    "wave1",
    "wave2_synthesis",
    "hitl2",
    "readiness",
    "final_delivery",
)


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _to_relative(path: Path) -> str:
    """Return a harness-relative POSIX string for operator output/records."""
    return path.relative_to(HARNESS).as_posix()


def _resolve_soft_root(value: str) -> Path:
    """Resolve a safe repository-relative soft root to an absolute path."""
    if not isinstance(value, str) or not value:
        raise ValueError("soft_bundle_root_invalid")
    p = Path(value)
    if p.is_absolute() or any(part in {"", ".", ".."} for part in p.parts):
        raise ValueError("soft_bundle_root_invalid")
    resolved = (HARNESS / p).resolve()
    if not resolved.is_relative_to(HARNESS.resolve()):
        raise ValueError("soft_bundle_root_outside_repository")
    return resolved


def _generated_root() -> Path:
    now = datetime.now()
    suffix = secrets.token_hex(3)
    name = f"research-{now:%Y%m%d-%H%M}-{suffix}"
    root = DEFAULT_SOFT_BUNDLES_ROOT / name
    if root.exists():
        return _generated_root()
    return root


def _load_manifest(root: Path) -> dict:
    manifest_path = root / MANIFEST_NAME
    try:
        return json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("manifest_invalid") from exc


def _save_manifest(root: Path, manifest: dict) -> None:
    manifest_path = root / MANIFEST_NAME
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


def _require_manifest(root: Path) -> dict:
    if not root.is_dir() or not (root / MANIFEST_NAME).is_file():
        raise ValueError("soft_bundle_root_missing")
    return _load_manifest(root)


def _bundle_record_path(root: Path, bundle_id: str) -> Path:
    return root / BUNDLES_SUBDIR / f"{bundle_id}.json"


def _find_bundle_dir(bundle_id: str) -> Path | None:
    if not RUNS_ROOT.exists():
        return None
    for candidate in RUNS_ROOT.rglob(bundle_id):
        if candidate.is_dir():
            return candidate
    return None


def _latest_bundle_dir() -> Path | None:
    if not RUNS_ROOT.exists():
        return None
    candidates = sorted(
        (p for p in RUNS_ROOT.rglob("b_*") if p.is_dir()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _clean_run_bundles() -> None:
    """Remove prior operator run-bundle content before a fresh control run.

    The Harness-managed ``deep-research`` subtree and scripted-real workspaces
    are removed. Soft bundle records under ``soft-bundles`` are kept.
    """
    research_root = RUNS_ROOT / "deep-research"
    if research_root.exists():
        shutil.rmtree(research_root)
        research_root.mkdir(parents=True, exist_ok=True)
    else:
        research_root.mkdir(parents=True, exist_ok=True)
    scripted_root = RUNS_ROOT / "scripted-real"
    if scripted_root.exists():
        shutil.rmtree(scripted_root)
        scripted_root.mkdir(parents=True, exist_ok=True)
    else:
        scripted_root.mkdir(parents=True, exist_ok=True)


def _run_make(args: list[str], env_extra: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["UV_NO_CACHE"] = "1"
    env.pop("VIRTUAL_ENV", None)
    if env_extra:
        env.update(env_extra)
    print("+", " ".join(args))
    return subprocess.run(args, cwd=str(HARNESS), env=env, text=True, capture_output=True)


def _parse_bundle_id(output: str) -> str | None:
    for line in output.splitlines():
        m = re.search(r"(?:Run Bundle|bundle_id):\s*(b_[A-Za-z0-9_-]{20,})", line)
        if m:
            return m.group(1)
    return None


def _record_bundle(root: Path, manifest: dict, bundle_dir: Path) -> None:
    bundle_id = bundle_dir.name
    if not BUNDLE_ID_RE.fullmatch(bundle_id):
        raise ValueError("bundle_id_invalid")
    record = {
        "schema_version": SCHEMA_VERSION,
        "bundle_id": bundle_id,
        "bundle_local_path": _to_relative(bundle_dir),
        "mode": manifest.get("mode", "001"),
        "question": manifest.get("question", ""),
        "created_at": _now(),
    }
    bundles_dir = root / BUNDLES_SUBDIR
    bundles_dir.mkdir(parents=True, exist_ok=True)
    (_bundle_record_path(root, bundle_id)).write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    manifest["current_bundle_id"] = bundle_id
    manifest["updated_at"] = _now()
    _save_manifest(root, manifest)


def _verify_bundle(bundle_dir: Path, bundle_id: str, mode: str) -> tuple[bool, list[str]]:
    problems: list[str] = []

    state_path = bundle_dir / "state.json"
    if not state_path.exists():
        problems.append("state.json missing")
    else:
        state = json.loads(state_path.read_text())
        if state.get("terminal_status") != "completed":
            problems.append(f"terminal_status={state.get('terminal_status')!r}, expected 'completed'")
        if state.get("phase_status") != "terminal":
            problems.append(f"phase_status={state.get('phase_status')!r}, expected 'terminal'")
        if state.get("phase") != "final_delivery":
            problems.append(f"phase={state.get('phase')!r}, expected 'final_delivery'")
        trace = state.get("execution_trace", [])
        missing = [phase for phase in REQUIRED_TRACE if phase not in trace]
        if missing:
            problems.append(f"execution_trace missing phases: {', '.join(missing)}")

    summary_path = bundle_dir / "diagnostics" / "run-summary.json"
    if mode == "001":
        if not summary_path.exists():
            problems.append("run-summary.json missing")
        else:
            summary = json.loads(summary_path.read_text())
            if summary.get("status") != "completed":
                problems.append(f"summary.status={summary.get('status')!r}, expected 'completed'")
            if summary.get("terminal_outcome") != "completed":
                problems.append(f"summary.terminal_outcome={summary.get('terminal_outcome')!r}, expected 'completed'")
            if summary.get("journal_availability") != "complete":
                problems.append(f"summary.journal_availability={summary.get('journal_availability')!r}, expected 'complete'")

    events_path = bundle_dir / "diagnostics" / "events.jsonl"
    if not events_path.exists():
        problems.append("events.jsonl missing")
    else:
        completed_phases: set[str] = set()
        terminal_ok = False
        for line in events_path.read_text().splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("category") == "node" and event.get("outcome") == "completed" and event.get("phase"):
                completed_phases.add(event["phase"])
            if event.get("category") == "terminal" and event.get("outcome") == "completed" and event.get("phase") == "final_delivery":
                terminal_ok = True
        if not terminal_ok and state_path.exists():
            try:
                state = json.loads(state_path.read_text())
                terminal_ok = state.get("terminal_status") == "completed" and state.get("phase") == "final_delivery"
            except json.JSONDecodeError:
                pass
        missing_events = [phase for phase in REQUIRED_TRACE if phase not in completed_phases]
        if missing_events:
            problems.append(f"events.jsonl missing completed node: {', '.join(missing_events)}")
        if not terminal_ok:
            problems.append("events.jsonl missing terminal completed final_delivery")

    report = bundle_dir / "final" / "report.md"
    if mode == "001" and report.exists():
        problems.append("001 should not publish final/report.md")
    if mode == "002" and not report.exists():
        problems.append("002 should publish final/report.md")

    return (not problems, problems)


def _print_run_summary(bundle_dir: Path, bundle_id: str, mode: str) -> None:
    """Print a human-readable step-by-step run summary after each run."""
    print("\n=== Run Summary ===")
    print("Nodes passed:")

    seen: dict[str, str] = {}
    events_path = bundle_dir / "diagnostics" / "events.jsonl"
    if events_path.exists():
        for line in events_path.read_text().splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("category") == "node" and event.get("outcome") == "completed" and event.get("phase"):
                seen[event["phase"]] = event.get("attempt_id", "?")
    for index, phase in enumerate(REQUIRED_TRACE, start=1):
        if phase in seen:
            print(f"  {index}. {phase} (completed: {seen[phase]})")
        else:
            print(f"  {index}. {phase} (missing)")

    terminal_ok = False
    if events_path.exists():
        for line in events_path.read_text().splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("category") == "terminal" and event.get("outcome") == "completed" and event.get("phase") == "final_delivery":
                terminal_ok = True
                break
    state_path = bundle_dir / "state.json"
    if not terminal_ok and state_path.exists():
        try:
            state = json.loads(state_path.read_text())
            terminal_ok = state.get("terminal_status") == "completed" and state.get("phase") == "final_delivery"
        except json.JSONDecodeError:
            pass
    print(f"Terminal: {'final_delivery -> completed' if terminal_ok else 'final_delivery -> missing'}")

    print("Final result:")
    report = bundle_dir / "final" / "report.md"
    if report.exists():
        print(f"  final/report.md: exists")
        body = report.read_text().strip()
        if body:
            print(body[:2000])
    else:
        print("  final/report.md: not found")

    work_root = bundle_dir / "work"
    if work_root.exists():
        outputs = list(work_root.rglob("outputs/fixture.json"))
        print(f"Work outputs: {len(outputs)} fixture files")
    else:
        print("Work outputs: none")


def cmd_create(args: argparse.Namespace) -> int:
    if args.root:
        root = _resolve_soft_root(args.root)
    else:
        root = _generated_root()
        root.mkdir(parents=True, exist_ok=False)
    if root.exists() and (root / MANIFEST_NAME).is_file():
        manifest = _load_manifest(root)
        print(f"soft_bundle_root={_to_relative(root)}")
        print(f"name={manifest.get('name', '')}")
        return 0
    if root.exists() and any(root.iterdir()):
        print(f"error: root exists but is not a soft bundle directory: {_to_relative(root)}", file=sys.stderr)
        return 2
    root.mkdir(parents=True, exist_ok=True)
    name = args.name or f"research-{datetime.now():%Y%m%d-%H%M}-{secrets.token_hex(3)}"
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "name": name,
        "mode": args.mode,
        "question": MODE_QUESTIONS.get(args.mode, DEFAULT_QUESTION),
        "current_bundle_id": None,
        "created_at": _now(),
        "updated_at": _now(),
    }
    _save_manifest(root, manifest)
    print(f"soft_bundle_root={_to_relative(root)}")
    print(f"name={name}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    root = _resolve_soft_root(args.root)
    manifest = _require_manifest(root)
    if args.mode:
        manifest["mode"] = args.mode
    mode = manifest.get("mode", "001")
    manifest["question"] = MODE_QUESTIONS.get(mode, DEFAULT_QUESTION)
    _save_manifest(root, manifest)

    # Control environment: always start from a clean run-bundle workspace.
    _clean_run_bundles()
    print("cleaned prior run bundles")

    question = manifest.get("question", "")

    if mode == "001":
        make_args = ["make", "demo-scripted", f'DEMO_ARGS=--question "{question}"']
        proc = _run_make(make_args)
        output = (proc.stdout or "") + (proc.stderr or "")
        bundle_id = _parse_bundle_id(output)

        if bundle_id is None:
            # Fallback: deterministic fixture-graph route does not always print a bundle id.
            fallback = ["make", "demo-fixture-graph", f'DEMO_ARGS=--question "{question}"']
            fallback_proc = _run_make(fallback)
            fallback_output = (fallback_proc.stdout or "") + (fallback_proc.stderr or "")
            bundle_id = _parse_bundle_id(fallback_output)
            if bundle_id is None:
                latest = _latest_bundle_dir()
                if latest is None:
                    print("error: could not resolve a valid bundle id after run", file=sys.stderr)
                    return 1
                bundle_id = latest.name

        if proc.returncode != 0 and bundle_id is None:
            print(output, file=sys.stderr)
            return proc.returncode or 1

        bundle_dir = _find_bundle_dir(bundle_id)
        if bundle_dir is None:
            print(f"error: bundle {bundle_id} not found under operator workspace", file=sys.stderr)
            return 1
    elif mode == "002":
        workspace = RUNS_ROOT / "scripted-real" / f"run-{datetime.now():%Y%m%d-%H%M%S}-{secrets.token_hex(3)}"
        make_args = ["make", "debug-scripted-real-workflow", f"DEMO_ARGS=--workspace {workspace}"]
        proc = _run_make(make_args)
        output = (proc.stdout or "") + (proc.stderr or "")
        bundle_id = _parse_bundle_id(output)
        journal_match = re.search(r"event journal:\s*(\S+)", output)
        bundle_dir = Path(journal_match.group(1)).parent.parent if journal_match else None

        if proc.returncode != 0 or bundle_id is None or bundle_dir is None or not bundle_dir.exists():
            print(output, file=sys.stderr)
            return proc.returncode or 1
    else:
        print(f"error: unsupported mode {mode}", file=sys.stderr)
        return 2

    _record_bundle(root, manifest, bundle_dir)
    print(f"bound_bundle_id={bundle_id}")
    print(f"bundle_local_path={_to_relative(bundle_dir)}")

    ok, problems = _verify_bundle(bundle_dir, bundle_id, mode)
    if ok:
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
    _print_run_summary(bundle_dir, bundle_id, mode)
    return 0 if ok else 1


def cmd_clean(args: argparse.Namespace) -> int:
    _clean_run_bundles()
    print("cleaned run bundles")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    root = _resolve_soft_root(args.root)
    manifest = _require_manifest(root)
    bundle_id = manifest.get("current_bundle_id")
    if not bundle_id:
        print("error: current_bundle_id not bound", file=sys.stderr)
        return 1
    bundle_dir = _find_bundle_dir(bundle_id)
    if bundle_dir is None:
        print("error: bundle unavailable", file=sys.stderr)
        return 1
    ok, problems = _verify_bundle(bundle_dir, bundle_id, manifest.get("mode", "001"))
    if ok:
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
    _print_run_summary(bundle_dir, bundle_id, manifest.get("mode", "001"))
    return 0 if ok else 1


def cmd_bind(args: argparse.Namespace) -> int:
    root = _resolve_soft_root(args.root)
    manifest = _require_manifest(root)
    if not BUNDLE_ID_RE.fullmatch(args.bundle_id):
        print("error: invalid bundle_id", file=sys.stderr)
        return 2
    bundle_dir = _find_bundle_dir(args.bundle_id)
    if bundle_dir is None:
        print(f"error: bundle unavailable: {args.bundle_id}", file=sys.stderr)
        return 1
    _record_bundle(root, manifest, bundle_dir)
    print(f"bound_bundle_id={args.bundle_id}")
    print(f"bundle_local_path={_to_relative(bundle_dir)}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root = _resolve_soft_root(args.root)
    manifest = _require_manifest(root)
    print(f"soft_bundle_root={_to_relative(root)}")
    print(f"name={manifest.get('name', '')}")
    print(f"mode={manifest.get('mode', '')}")
    print(f"question={manifest.get('question', '')}")
    print(f"current_bundle_id={manifest.get('current_bundle_id') or '(unbound)'}")
    return 0


def cmd_path(args: argparse.Namespace) -> int:
    root = _resolve_soft_root(args.root)
    manifest = _require_manifest(root)
    bundle_id = manifest.get("current_bundle_id")
    if not bundle_id:
        print("error: current_bundle_id not bound", file=sys.stderr)
        return 1
    bundle_dir = _find_bundle_dir(bundle_id)
    if bundle_dir is None:
        print("error: bundle unavailable", file=sys.stderr)
        return 1
    print(_to_relative(bundle_dir))
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    root = _resolve_soft_root(args.root)
    manifest = _require_manifest(root)
    bundle_id = manifest.get("current_bundle_id")
    if not bundle_id:
        print("error: current_bundle_id not bound", file=sys.stderr)
        return 1
    proc = _run_make(["make", "demo-sessions", f"DEMO_ARGS=inspect {bundle_id}"])
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    return proc.returncode


def cmd_phases(args: argparse.Namespace) -> int:
    root = _resolve_soft_root(args.root)
    manifest = _require_manifest(root)
    bundle_id = manifest.get("current_bundle_id")
    if not bundle_id:
        print("error: current_bundle_id not bound", file=sys.stderr)
        return 1
    bundle_dir = _find_bundle_dir(bundle_id)
    if bundle_dir is None:
        print("error: bundle unavailable", file=sys.stderr)
        return 1
    print(f"\n===== Bundle {bundle_id} 每个环节内容 =====")
    state_path = bundle_dir / "state.json"
    if state_path.exists():
        state = json.loads(state_path.read_text())
        print("\n[state.json]")
        print("  execution_trace:", " -> ".join(state.get("execution_trace", [])))
        print("  phase:", state.get("phase"), "| phase_status:", state.get("phase_status"), "| terminal_status:", state.get("terminal_status"))
    work = bundle_dir / "work"
    if work.exists():
        print("\n[work 输出]")
        for p in sorted(work.rglob("outputs/fixture.json")):
            print(f"\n  --- {p.relative_to(bundle_dir)} ---")
            print("  " + p.read_text().replace("\n", "\n  "))
    report = bundle_dir / "final" / "report.md"
    print("\n[最终产物]")
    print("  final/report.md 存在" if report.exists() else "  final/report.md 不存在")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    parent = _resolve_soft_root(args.under) if args.under else DEFAULT_SOFT_BUNDLES_ROOT
    if not parent.is_dir():
        return 0
    for child in sorted(parent.iterdir()):
        if child.is_dir() and (child / MANIFEST_NAME).is_file():
            print(_to_relative(child))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Operator-only Soft Bundle CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="create a soft bundle root")
    p_create.add_argument("--root", default=None)
    p_create.add_argument("--name", default=None)
    p_create.add_argument("--mode", default="001", choices=["001", "002", "003", "004"])
    p_create.set_defaults(func=cmd_create)

    p_run = sub.add_parser("run", help="run a mode and bind the resulting bundle")
    p_run.add_argument("root")
    p_run.add_argument("--mode", default=None, choices=["001", "002", "003", "004"])
    p_run.set_defaults(func=cmd_run)

    p_bind = sub.add_parser("bind", help="bind an existing bundle id")
    p_bind.add_argument("root")
    p_bind.add_argument("bundle_id")
    p_bind.set_defaults(func=cmd_bind)

    p_clean = sub.add_parser("clean", help="clean prior run bundles")
    p_clean.set_defaults(func=cmd_clean)

    p_verify = sub.add_parser("verify", help="verify the bound bundle and print PASS/FAIL")
    p_verify.add_argument("root")
    p_verify.set_defaults(func=cmd_verify)

    p_status = sub.add_parser("status", help="show soft bundle status")
    p_status.add_argument("root")
    p_status.set_defaults(func=cmd_status)

    p_path = sub.add_parser("path", help="print current bundle local path")
    p_path.add_argument("root")
    p_path.set_defaults(func=cmd_path)

    p_inspect = sub.add_parser("inspect", help="delegate to demo-sessions")
    p_inspect.add_argument("root")
    p_inspect.set_defaults(func=cmd_inspect)

    p_phases = sub.add_parser("phases", help="print per-phase content")
    p_phases.add_argument("root")
    p_phases.set_defaults(func=cmd_phases)

    p_list = sub.add_parser("list", help="list soft bundle roots")
    p_list.add_argument("--under", default=None)
    p_list.set_defaults(func=cmd_list)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
