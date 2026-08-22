"""Contracts for the canonical deterministic verification composition.

@impl EVH-009
@impl EVH-010
@impl DER-004
@impl EVH-032
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
AGENT_ROOT = REPO_ROOT / "deep_research_harness"
MAKEFILE = AGENT_ROOT / "Makefile"


def test_makefile_exposes_exact_non_mutating_verify_composition() -> None:
    text = MAKEFILE.read_text(encoding="utf-8")

    assert re.search(r"^\.PHONY:.*\bverify\b", text, re.MULTILINE)
    assert (
        "install:\n\tenv -u VIRTUAL_ENV uv sync --locked --extra operations --extra demo-tui --extra demo-real" in text
    )
    assert "governance:\n" not in text
    assert "verify: export UV_NO_SYNC := 1" in text
    assert ("verify: lock-check lint test-assets test-fast test-integration test-workflow") in text
    assert not re.search(r"^verify:\n\t", text, re.MULTILINE)
    assert "test-entry-environment-regression" not in re.search(r"^verify:.*$", text, re.MULTILINE).group(0)
    assert ("\t\ttests/assets tests/contract tests/domain tests/engine tests/unit tests/graph tests/eval \\\n") in text
    assert "--durations=20 --junitxml=.reports/test-fast.xml" in text
    assert "PYTEST := python -m pytest" in text
    # Gate lanes default to parallel (-n 4; L2 parallel-safety review complete,
    # see _backlog/plans/test-regression-speedup.md). PYTEST_XDIST is carried by
    # every gate lane via `?=` and may be emptied for serial (`PYTEST_XDIST=`).
    assert "PYTEST_XDIST ?= -n 4" in text
    for lane in ("test:", "test-fast:", "test-integration:", "test-workflow:"):
        body = text.split(lane, 1)[1].split("\n\n", 1)[0]
        assert "uv run $(PYTEST) $(PYTEST_XDIST)" in body
    for target in ("test-intake", "test-retained-observation", "test-work-unit", "test-strict-checkpoint"):
        assert re.search(rf"^{target}:\n\t@started=.* elapsed:", text, re.MULTILINE)
    assert (
        "test-duration-policy:\n"
        "\tuv run python scripts/check_test_durations.py .reports/test-fast.xml "
        "$(if $(PYTEST_XDIST),--parallel)"
    ) in text
    assert ('uv run $(PYTEST) $(PYTEST_XDIST) -m "not (requires_llm or release_e2e or periodic)"') in text
    assert (
        "test-entry-environment-regression:\n"
        "\tmkdir -p .reports\n"
        "\tUV_OFFLINE=1 uv run --no-sync $(PYTEST) \\\n"
        "\t\ttests/scenarios_periodic \\\n"
        '\t\t-m "periodic and not (requires_llm or release_e2e)" \\\n'
        "\t\t--durations=20 --junitxml=.reports/test-entry-environment.xml\n"
        "\tuv run --no-sync python scripts/check_test_durations.py "
        ".reports/test-entry-environment.xml --lane periodic"
    ) in text
