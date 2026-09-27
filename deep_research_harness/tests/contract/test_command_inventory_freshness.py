"""Command-inventory freshness tripwire.

A Makefile target that reaches neither `COMMANDS.md` nor `docs/local-operations.md`
is invisible to an agent reading the repository, and the earlier evidence-lane work
showed how easily that happens (three new targets landed with no inventory entry until
a human noticed). This tripwire makes the omission red instead of silent.

Internal targets are waived by an explicit, reviewable list; a waiver whose target no
longer exists also fails, so the list cannot rot.

@impl PRS-009
"""

from __future__ import annotations

import re
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = AGENT_ROOT / "Makefile"
INVENTORY = AGENT_ROOT / "COMMANDS.md"
OPERATIONS = AGENT_ROOT / "docs" / "local-operations.md"

# Internal targets: lane members selected by the lane expressions, and contributor
# tooling that is not an entry point. Anything else must be documented.
WAIVER_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"^test-.*$", "internal lane member, selected by the lane expressions in the Makefile"),
)

WAIVERS: dict[str, str] = {
    "benchmark-fast": "contributor performance smoke, not a gate or entry point",
    "control-digests-check": "governance digest check, invoked by its own lane",
    "prompt-dump": "contributor prompt inspection (see the prompt-catalog guidance)",
    "prompt-dump-check": "contributor prompt-inspection drift check",
}


def _targets() -> list[str]:
    text = MAKEFILE.read_text(encoding="utf-8")
    return sorted({match.group(1) for match in re.finditer(r"^([a-zA-Z][a-zA-Z0-9_-]*):(?!=)", text, re.MULTILINE)})


def _documented(target: str) -> bool:
    return any(f"make {target}" in path.read_text(encoding="utf-8") for path in (INVENTORY, OPERATIONS))


def test_every_user_visible_target_reaches_a_command_inventory() -> None:
    """Every Makefile target is either documented or explicitly waived with a reason."""
    undocumented = [
        target
        for target in _targets()
        if not _documented(target)
        and target not in WAIVERS
        and not any(re.match(pattern, target) for pattern, _ in WAIVER_PATTERNS)
    ]
    assert not undocumented, (
        "these targets reach no command inventory (add them to COMMANDS.md or "
        f"docs/local-operations.md, or waive them with a reason): {undocumented}"
    )


def test_documented_targets_are_defined() -> None:
    """A documented `make <target>` that the Makefile does not define must be red.

    This is the deterministic form of a transient seen while hand-mutating the
    Makefile: contract tests dry-run documented targets with check=True, so a
    documented-but-missing target fails them with 'No rule to make target'.
    """
    text = "\n".join(path.read_text(encoding="utf-8") for path in (INVENTORY, OPERATIONS))
    # `make LANE=x` / `make PROFILE=demo` are variable assignments, not targets.
    mentioned = set(re.findall(r"make ([a-zA-Z][a-zA-Z0-9_-]*)(?![=a-zA-Z0-9_-])", text))
    defined = set(_targets())
    missing = sorted(name for name in mentioned if name not in defined)
    assert not missing, f"the command inventories document targets the Makefile does not define: {missing}"


def test_waiver_entries_still_exist_and_stay_justified() -> None:
    """A waiver for a target that no longer exists, or that is now documented, must fail."""
    targets = set(_targets())
    stale = [target for target in WAIVERS if target not in targets]
    assert not stale, f"waivers name targets that no longer exist: {stale}"
    for target, reason in WAIVERS.items():
        if _documented(target):
            continue
        assert reason.strip(), f"waiver for {target!r} needs a reason"
    for pattern, reason in WAIVER_PATTERNS:
        assert reason.strip(), f"pattern waiver {pattern!r} needs a reason"
        assert any(re.match(pattern, target) for target in targets), (
            f"pattern waiver {pattern!r} matches no target any more"
        )
