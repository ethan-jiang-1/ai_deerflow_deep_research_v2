"""Delivery-lane receipts: run a registered lane and record what it proved.

A receipt is runner-written evidence that one lane exited zero on one revision
(change `add-evidence-receipts-and-proof-lanes`). It is invalid on a dirty tree,
stale once a covered surface changes, and never claims a pass for a lane whose
credentials are absent. See `openspec/governance/proof-lanes.toml`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
ROOT = HARNESS.parent
REGISTRY = ROOT / "openspec" / "governance" / "proof-lanes.toml"
PROOF_DIR = ROOT / ".proof"
RECEIPTS = PROOF_DIR / "receipts"
TRANSCRIPTS = PROOF_DIR / "transcripts"
LANE_KEYS = {
    "name",
    "command",
    "cwd",
    "tier",
    "sentinel",
    "surfaces",
    "journeys",
    "requires_credentials",
}
DELIVERABLE_ROOTS = (
    "deep_research_harness/src",
    "deep_research_harness/scripts",
    "deep_research_harness/tests",
    "deep_research_harness/docs",
    "openspec",
    "_backlog",
)


class RegistryError(ValueError):
    """The lane registry is malformed or does not cover the deliverable roots."""


def load_lanes(root: Path = ROOT) -> list[dict]:
    import tomllib

    data = tomllib.loads((root / "openspec" / "governance" / "proof-lanes.toml").read_text(encoding="utf-8"))
    lanes = data.get("lane", [])
    if not isinstance(lanes, list) or not lanes:
        raise RegistryError("registry declares no lanes")
    seen: set[str] = set()
    for lane in lanes:
        unknown = set(lane) - LANE_KEYS
        if unknown:
            raise RegistryError(f"unknown lane key(s): {sorted(unknown)}")
        for required in ("name", "command", "cwd", "sentinel", "surfaces"):
            if not lane.get(required):
                raise RegistryError(f"lane {lane.get('name')!r} is missing {required!r}")
        if lane["name"] in seen:
            raise RegistryError(f"duplicate lane {lane['name']!r}")
        seen.add(lane["name"])
        if lane.get("tier") not in {"fast", "full"}:
            raise RegistryError(f"lane {lane['name']!r} needs tier fast|full")
        if lane.get("journeys") and lane.get("tier") != "full":
            raise RegistryError(f"lane {lane['name']!r} names journeys but is not a full lane")
        if lane.get("requires_credentials") and lane.get("journeys"):
            raise RegistryError(f"lane {lane['name']!r} cannot both require credentials and name journeys")
    return lanes


def surface_files(lane: dict, root: Path = ROOT) -> list[str]:
    import glob as _glob

    paths: list[str] = []
    for pattern in lane["surfaces"]:
        # recursive globbing so a ``/**`` surface matches nested files, not only dirs
        paths.extend(match for match in _glob.glob(pattern, root_dir=root, recursive=True) if (root / match).is_file())
    return sorted(set(paths))


def uncovered_files(lanes: list[dict], root: Path = ROOT) -> list[str]:
    covered: set[str] = set()
    for lane in lanes:
        covered.update(surface_files(lane, root))
    missing: list[str] = []
    for rel_root in DELIVERABLE_ROOTS:
        base = root / rel_root
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.is_file() and not any(part.startswith(".") for part in path.relative_to(root).parts):
                rel = path.relative_to(root).as_posix()
                if rel not in covered:
                    missing.append(rel)
    for name in ("AGENTS.md", "CLAUDE.md"):
        if (root / name).is_file() and name not in covered:
            missing.append(name)
    return missing


def _git(*args: str, root: Path = ROOT) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False).stdout.strip()


def receipt_path(lane: str, root: Path = ROOT) -> Path:
    return root / ".proof" / "receipts" / f"{lane}.json"


def read_receipt(lane: str, root: Path = ROOT) -> dict | None:
    path = receipt_path(lane, root)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def receipt_valid(lane: dict, receipt: dict | None, *, root: Path = ROOT, head: str | None = None) -> tuple[bool, str]:
    if receipt is None:
        return False, "no receipt"
    if receipt.get("status") != "valid":
        return False, f"receipt status {receipt.get('status')!r} is not a pass"
    if receipt.get("exit_code") != 0:
        return False, f"exit code {receipt.get('exit_code')}"
    if receipt.get("dirty"):
        return False, "recorded on a dirty tree"
    head = head or _git("rev-parse", "HEAD", root=root)
    revision = receipt.get("revision")
    if not revision:
        return False, "no recorded revision"
    # Against the working tree, not revision..HEAD: an uncommitted edit to a covered
    # surface must invalidate the receipt too (found by touching a covered file).
    changed = _git("diff", "--name-only", revision, "--", *lane["surfaces"], root=root)
    if changed:
        return False, f"covered surface changed since the receipt: {changed.splitlines()[0]}"
    transcript = receipt.get("transcript")
    digest = receipt.get("transcript_sha256")
    if not transcript or not (root / transcript).is_file():
        return False, "transcript missing"
    actual = hashlib.sha256((root / transcript).read_bytes()).hexdigest()
    if actual != digest:
        return False, "transcript digest mismatch"
    if lane["sentinel"] not in (root / transcript).read_text(encoding="utf-8", errors="replace"):
        return False, f"sentinel {lane['sentinel']!r} absent from the transcript"
    return True, "valid"


def _version(command: list[str]) -> str:
    run = subprocess.run(command, capture_output=True, text=True, check=False)
    return (run.stdout or run.stderr).strip().splitlines()[0] if (run.stdout or run.stderr) else "unknown"


def run_lane(lane: dict, *, root: Path = ROOT, credentials_present: bool = True) -> dict:
    dirty = bool(_git("status", "--porcelain", root=root))
    revision = _git("rev-parse", "HEAD", root=root)
    started = datetime.now(UTC).isoformat()
    clock = time.monotonic()
    transcript = f".proof/transcripts/{lane['name']}-{revision[:12]}-{int(time.time())}.log"
    target = root / transcript
    target.parent.mkdir(parents=True, exist_ok=True)
    if lane.get("requires_credentials") and not credentials_present:
        # A boundary is recorded, never a pass.
        target.write_text("unverified: credentials absent\n", encoding="utf-8")
        receipt = _receipt(
            lane, revision, dirty, started, clock, target, transcript, exit_code=None, status="unverified"
        )
        _store(lane, receipt, root)
        return receipt
    run = subprocess.run(
        lane["command"], shell=True, cwd=root / lane["cwd"], capture_output=True, text=True, check=False
    )
    body = (run.stdout or "") + (run.stderr or "")
    target.write_text(body, encoding="utf-8")
    status = "valid" if run.returncode == 0 and not dirty else "provisional"
    receipt = _receipt(
        lane, revision, dirty, started, clock, target, transcript, exit_code=run.returncode, status=status
    )
    _store(lane, receipt, root)
    return receipt


def _receipt(lane, revision, dirty, started, clock, target, transcript, *, exit_code, status) -> dict:
    return {
        "lane": lane["name"],
        "command": lane["command"],
        "cwd": lane["cwd"],
        "exit_code": exit_code,
        "status": status,
        "revision": revision,
        "dirty": dirty,
        "started": started,
        "finished": datetime.now(UTC).isoformat(),
        "duration_s": round(time.monotonic() - clock, 2),
        "python": sys.version.split()[0],
        "uv": _version(["uv", "--version"]),
        "openspec": _version(["openspec", "--version"]),
        "transcript": transcript,
        "transcript_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "sentinel": lane["sentinel"],
        "sentinel_observed": lane["sentinel"] in target.read_text(encoding="utf-8", errors="replace"),
        "journeys": lane.get("journeys", []),
    }


def _store(lane: dict, receipt: dict, root: Path) -> None:
    path = receipt_path(lane["name"], root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _lane(lanes: list[dict], name: str) -> dict:
    for lane in lanes:
        if lane["name"] == name:
            return lane
    raise RegistryError(f"unknown lane {name!r}; registered: {', '.join(item['name'] for item in lanes)}")


def self_test(root: Path = ROOT) -> int:
    """Planted violations: each rule must fail, and the real tree must pass."""
    import tempfile

    failures: list[str] = []
    lanes = load_lanes(root)
    if uncovered_files(lanes, root):
        failures.append(f"real tree has uncovered files: {uncovered_files(lanes, root)[:3]}")
    bad = [
        (
            "unknown key",
            {"name": "x", "command": "true", "cwd": ".", "tier": "fast", "sentinel": "s", "surfaces": ["a"], "junk": 1},
        ),
        (
            "empty surfaces",
            {"name": "x", "command": "true", "cwd": ".", "tier": "fast", "sentinel": "s", "surfaces": []},
        ),
        ("missing sentinel", {"name": "x", "command": "true", "cwd": ".", "tier": "fast", "surfaces": ["a"]}),
        (
            "journeys on a fast lane",
            {
                "name": "x",
                "command": "true",
                "cwd": ".",
                "tier": "fast",
                "sentinel": "s",
                "surfaces": ["a"],
                "journeys": ["E1"],
            },
        ),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        (tmp_root / "openspec" / "governance").mkdir(parents=True)
        for label, lane in bad:
            (tmp_root / "openspec" / "governance" / "proof-lanes.toml").write_text(
                "[[lane]]\n" + "\n".join(f"{k} = {json.dumps(v)}" for k, v in lane.items()) + "\n",
                encoding="utf-8",
            )
            try:
                load_lanes(tmp_root)
            except RegistryError:
                continue
            failures.append(f"registry accepted a planted violation: {label}")
    verify = _lane(lanes, "verify")
    ok, _ = receipt_valid(
        verify,
        {
            "status": "valid",
            "exit_code": 0,
            "dirty": False,
            "revision": "0" * 40,
            "transcript": "none",
            "transcript_sha256": "x",
        },
    )
    if ok:
        failures.append("an empty receipt was accepted")
    for failure in failures:
        print(f"self-test FAILED: {failure}")
    if failures:
        print("proof-receipt self-test: FAILED")
        return 1
    print(f"proof-receipt self-test: OK ({len(lanes)} lanes, surface map total)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    run = sub.add_parser("run")
    run.add_argument("--lane", required=True)
    run.add_argument("--credentials-present", default="", help="set to 'no' to record a credential boundary")
    verify = sub.add_parser("verify")
    verify.add_argument("--lane")
    verify.add_argument("--stale", action="store_true")
    export = sub.add_parser("export")
    export.add_argument("--lane", required=True)
    sub.add_parser("self-test")
    args = parser.parse_args()

    if args.action == "self-test":
        return self_test()
    lanes = load_lanes()
    if args.action == "run":
        receipt = run_lane(_lane(lanes, args.lane), credentials_present=args.credentials_present != "no")
        for key in ("lane", "status", "exit_code", "revision", "duration_s"):
            print(f"{key}: {receipt[key]}")
        return 0 if receipt["status"] in {"valid", "unverified"} else 1
    if args.action == "export":
        path = receipt_path(args.lane)
        print(path.read_text(encoding="utf-8") if path.is_file() else f"no receipt for {args.lane}")
        return 0
    selected = [_lane(lanes, args.lane)] if args.lane else lanes
    failed = False
    for lane in selected:
        ok, reason = receipt_valid(lane, read_receipt(lane["name"]))
        print(
            f"{'OK   ' if ok else 'STALE'} {lane['name']}: {reason}"
            + ("" if ok else f" -> rerun: make proof LANE={lane['name']}")
        )
        failed = failed or not ok
    if failed and not args.stale:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
