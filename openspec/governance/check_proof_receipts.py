"""Closeout proof-receipt checker.

For the selected change, find the delivery lanes whose declared surfaces the change
touched and require a runner-produced receipt for each: exit zero, recorded on a
clean tree, a revision whose diff to the delivered revision is empty for those
surfaces, a transcript whose digest matches, and that lane's success sentinel in
the transcript text. A caller-declared claim never satisfies this.

The lane registry lives with the application (`deep_research_harness/proof-lanes.toml`)
because the application must not depend on this tree; governance reading the
application is the allowed direction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "deep_research_harness" / "proof-lanes.toml"
PROOF = REPO / ".proof"
MODE_DEFAULT = "warn"


class ReceiptError(ValueError):
    """The receipt set does not cover the delivered revision."""


def _git(*args: str, root: Path = REPO) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False).stdout.strip()


def load_lanes(path: Path = REGISTRY) -> list[dict]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    lanes = data.get("lane", [])
    if not isinstance(lanes, list) or not lanes:
        raise ReceiptError("lane registry declares no lanes")
    return lanes


def _expand(pattern: str) -> list[str]:
    return [pattern, pattern[:-3] + "/**/*"] if pattern.endswith("/**") else [pattern]


def matches(lane: dict, path: str) -> bool:
    import fnmatch

    return any(fnmatch.fnmatch(path, pat) for pattern in lane["surfaces"] for pat in _expand(pattern))


def touched_files(attestation: dict, *, root: Path = REPO) -> list[str]:
    base, head = attestation["base_commit"], attestation["head_commit"]
    files = _git("diff", "--name-only", f"{base}..{head}", root=root).splitlines()
    return [line for line in files if line.strip()]


def required_lanes(lanes: list[dict], touched: list[str]) -> dict[str, list[str]]:
    required: dict[str, list[str]] = {}
    for lane in lanes:
        hits = [path for path in touched if matches(lane, path)]
        if hits:
            required[lane["name"]] = hits
    return required


def receipt_problems(lane: dict, touched: list[str], head: str, root: Path = REPO) -> list[str]:
    path = root / ".proof" / "receipts" / f"{lane['name']}.json"
    if not path.is_file():
        return [f"no receipt for lane {lane['name']!r}"]
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return [f"receipt for lane {lane['name']!r} is unreadable"]
    problems: list[str] = []
    if receipt.get("status") != "valid":
        problems.append(f"status {receipt.get('status')!r}")
    if receipt.get("exit_code") != 0:
        problems.append(f"exit code {receipt.get('exit_code')}")
    if receipt.get("dirty"):
        problems.append("recorded on a dirty tree")
    revision = receipt.get("revision")
    if not revision:
        problems.append("no recorded revision")
    elif not _git("rev-parse", "--verify", "--quiet", f"{revision}^{{commit}}", root=root):
        # Fail closed: an unknown revision must never read as "nothing changed".
        problems.append(f"unknown recorded revision {revision[:12]}")
    else:
        changed = _git("diff", "--name-only", f"{revision}..{head}", "--", *lane["surfaces"], root=root).splitlines()
        if changed:
            problems.append(f"{len(changed)} covered surface(s) changed after the receipt")
    transcript = receipt.get("transcript")
    if not transcript or not (root / transcript).is_file():
        problems.append("transcript missing")
    else:
        actual = hashlib.sha256((root / transcript).read_bytes()).hexdigest()
        if actual != receipt.get("transcript_sha256"):
            problems.append("transcript digest mismatch")
        elif lane["sentinel"] not in (root / transcript).read_text(encoding="utf-8", errors="replace"):
            problems.append(f"sentinel {lane['sentinel']!r} absent from the transcript")
    return problems


def evaluate(attestation: dict, *, root: Path = REPO) -> list[str]:
    lanes = load_lanes(root / "deep_research_harness" / "proof-lanes.toml")
    touched = touched_files(attestation, root=root)
    head = attestation["head_commit"]
    lines: list[str] = []
    for name, hits in required_lanes(lanes, touched).items():
        lane = next(item for item in lanes if item["name"] == name)
        problems = receipt_problems(lane, hits, head, root)
        if problems:
            lines.append(f"{name}: unmet ({'; '.join(problems)}) - touched {hits[0]} -> rerun: make proof LANE={name}")
    return lines


def self_test() -> int:
    """Planted violations: every rule must fail, and a fresh receipt must pass."""
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "deep_research_harness").mkdir(parents=True)
        (root / ".proof" / "receipts").mkdir(parents=True)
        (root / ".proof" / "transcripts").mkdir(parents=True)
        (root / "deep_research_harness" / "proof-lanes.toml").write_text(
            'version = 1\n[[lane]]\nname = "demo"\ncommand = "true"\ncwd = "."\ntier = "fast"\n'
            'sentinel = "DEMO OK"\nsurfaces = ["deep_research_harness/src/**"]\n',
            encoding="utf-8",
        )
        # A real (temporary) git repository: the checker's staleness rule is a git rule.
        (root / "deep_research_harness" / "src").mkdir(parents=True)
        (root / "deep_research_harness" / "src" / "x.py").write_text("x = 1\n", encoding="utf-8")
        for command in (
            ("init", "-q"),
            ("add", "-A"),
            ("-c", "user.email=proof@example.invalid", "-c", "user.name=proof", "commit", "-q", "-m", "seed"),
        ):
            _git(*command, root=root)
        head = _git("rev-parse", "HEAD", root=root)
        transcript = root / ".proof" / "transcripts" / "demo.log"
        transcript.write_text("DEMO OK\n", encoding="utf-8")
        digest = hashlib.sha256(transcript.read_bytes()).hexdigest()

        def write(**overrides) -> None:
            receipt = {
                "lane": "demo",
                "status": "valid",
                "exit_code": 0,
                "dirty": False,
                "revision": head,
                "transcript": ".proof/transcripts/demo.log",
                "transcript_sha256": digest,
            }
            receipt.update(overrides)
            (root / ".proof" / "receipts" / "demo.json").write_text(json.dumps(receipt), encoding="utf-8")

        lane = load_lanes(root / "deep_research_harness" / "proof-lanes.toml")[0]
        write()
        if receipt_problems(lane, ["deep_research_harness/src/x.py"], head, root):
            failures.append("a fresh receipt was rejected")
        for label, overrides in (
            ("red exit code", {"exit_code": 1}),
            ("dirty tree", {"dirty": True}),
            ("stale revision", {"revision": "0" * 40}),
            ("digest mismatch", {"transcript_sha256": "0" * 64}),
            ("provisional status", {"status": "provisional"}),
        ):
            write(**overrides)
            if not receipt_problems(lane, ["deep_research_harness/src/x.py"], head, root):
                failures.append(f"accepted a planted violation: {label}")
        transcript.write_text("nothing here\n", encoding="utf-8")
        write()
        if not receipt_problems(lane, ["deep_research_harness/src/x.py"], head, root):
            failures.append("accepted a transcript without the sentinel")
        (root / ".proof" / "receipts" / "demo.json").unlink()
        if not receipt_problems(lane, ["deep_research_harness/src/x.py"], head, root):
            failures.append("accepted a missing receipt")
    for failure in failures:
        print(f"self-test FAILED: {failure}")
    if failures:
        print("proof-receipts checker self-test: FAILED")
        return 1
    print("proof-receipts checker self-test: OK (fresh receipt passes; five planted violations fail)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attestation", default="", help="selected-change attestation (base_commit/head_commit)")
    parser.add_argument("--mode", choices=("warn", "enforce"), default=MODE_DEFAULT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.attestation:
        print(f"proof receipts: no selected change (mode={args.mode})")
        return 0
    attestation_path = Path(args.attestation)
    if not attestation_path.is_file():
        print(f"proof receipts: no attestation at {attestation_path} (mode={args.mode})")
        return 0
    attestation = json.loads(attestation_path.read_text(encoding="utf-8"))
    if Path(str(attestation.get("repository_identity", REPO))).resolve() != REPO.resolve():
        print(f"proof receipts: attestation names another repository (mode={args.mode})")
        return 0
    lines = evaluate(attestation)
    for line in lines:
        print(f"[{args.mode}] {line}")
    if not lines:
        print(f"proof receipts: every required lane has a fresh receipt (mode={args.mode})")
        return 0
    if args.mode == "enforce":
        print(f"proof receipts: {len(lines)} lane(s) unmet (mode=enforce)")
        return 1
    print(f"proof receipts: {len(lines)} lane(s) would fail in enforce mode (mode=warn)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
