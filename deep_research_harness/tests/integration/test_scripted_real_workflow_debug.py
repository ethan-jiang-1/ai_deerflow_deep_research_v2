"""Scripted-real three-wave action proof against the production control path.

The external model's responses are scripted; every production node adapter,
prompt, parser, work-unit ledger, gate, route, and persistence path is real.
A passed case therefore proves each real Wave0/Wave1/Wave2 action actually
occurred under a fixed narrow budget — not model judgment, web availability,
or live provider behavior.

@impl SCR-002
@impl SCR-003
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

import pytest


@pytest.fixture
def _scripts_path() -> str:
    scripts = str(Path(__file__).resolve().parents[2] / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    return scripts


def _await(coro: object) -> object:
    return asyncio.run(coro)  # type: ignore[arg-type]


def test_scripted_real_baseline_proves_every_wave_action(tmp_path: Path, _scripts_path: str) -> None:
    """SCR-002/SCR-003: the fixed baseline drives and proves one bounded action per wave.

    @impl SCR-006
    """

    from debug_scripted_real_workflow import ScriptedRealRun, run_scripted_real_workflow

    started_at = time.monotonic()
    result = _await(run_scripted_real_workflow(workspace=tmp_path, run_id="proof-baseline"))
    assert isinstance(result, ScriptedRealRun)
    elapsed = time.monotonic() - started_at

    # Per-wave counters exactly match the declared baseline budget.
    assert result.model_calls == 11, f"expected 11 model calls, saw {result.model_calls}: {result.consumed}"
    assert result.web_search_calls == 2, f"expected 2 web_search calls, saw {result.web_search_calls}"
    assert result.web_fetch_calls == 0, f"expected 0 web_fetch calls, saw {result.web_fetch_calls}"

    # Terminal projection is a real completed research run that never entered
    # the targeted-evidence or rerun branches.
    assert result.terminal_status == "completed"
    for phase in (
        "hitl1",
        "topic_planning",
        "wave0",
        "wave1",
        "wave2_synthesis",
        "hitl2",
        "readiness",
        "final_delivery",
    ):
        assert phase in result.execution_trace, f"{phase} missing from {result.execution_trace}"
    assert "targeted_evidence" not in result.execution_trace
    assert "rerun" not in result.execution_trace

    # Durable evidence: accepted work-unit records, both Wave1 critic review
    # artifacts, a published report and citation-map pair with a backed claim.
    assert result.record_count >= 2, f"expected at least 2 accepted records, saw {result.record_count}"
    assert {"source-diagnostic.json", "claim-verifier.json"} <= set(result.wave1_review_artifacts), (
        result.wave1_review_artifacts
    )
    assert result.final_artifacts_published
    assert result.backed_claim_count >= 1, "no citation claim with a backing reference"

    # SCR-006: the terminal observation is published into the bundle journal, so a
    # read-only inspection reports the completed terminal summary.
    from deerflow_deep_research.runtime.run_observation import RunObservationStore

    bundle_dir = Path(result.journal_path).parent.parent
    inspection = _await(
        RunObservationStore(bundle_root=bundle_dir, bundle_id=result.bundle_id).inspect(bundle_id=result.bundle_id)
    )
    assert inspection.summary is not None
    assert inspection.summary.status == "completed"
    assert inspection.summary.phase == "final_delivery"
    assert inspection.summary.terminal_outcome == "completed"
    assert any(event.category.value == "terminal" for event in inspection.events)

    # The baseline wall-time contract: a timeout is a test failure, not a skip.
    assert elapsed < 10.0, f"wall time {elapsed:.2f}s exceeded the 10s contract"


def test_scripted_real_repair_targeted_named_case_proves_the_bounded_loop(tmp_path: Path, _scripts_path: str) -> None:
    """BUG-028/BUG-029 named case: question handoff, critic fact, bounded blocked terminal."""

    import json

    from debug_scripted_real_workflow import ScriptedRealRun, run_scripted_real_workflow

    started_at = time.monotonic()
    result = _await(
        run_scripted_real_workflow(workspace=tmp_path, run_id="proof-repair-targeted", scenario="repair-targeted")
    )
    assert isinstance(result, ScriptedRealRun)
    elapsed = time.monotonic() - started_at

    assert result.model_calls == 16, f"expected 17 model calls, saw {result.model_calls}: {result.consumed}"
    assert result.web_search_calls == 4, f"expected 4 web_search calls, saw {result.web_search_calls}"
    assert result.web_fetch_calls == 0
    assert result.terminal_status == "blocked"
    trace = result.execution_trace
    assert "targeted_evidence" in trace, trace
    assert trace[-1] == "wave2_synthesis", trace
    assert "rerun" not in trace
    assert result.record_count >= 4, f"expected >=4 accepted records, saw {result.record_count}"

    events = [
        json.loads(line) for line in Path(result.journal_path).read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    critic_facts = [
        event
        for event in events
        if event.get("category") == "validation"
        and event.get("critic_kind") == "source_diagnostic"
        and "wave1_source_diagnostic_output_json_invalid" in event.get("validation_codes", ())
    ]
    assert critic_facts, "no journal fact for the invalid source-diagnostic critic"

    assert elapsed < 10.0, f"wall time {elapsed:.2f}s exceeded the 10s contract"


def test_scripted_real_readiness_cap_trip_degrades_to_completed_delivery(
    tmp_path: Path,
    _scripts_path: str,
) -> None:
    """@impl REA-008 REJ-010

    The BUG-057 bridge cap failure still delivers.

    The tiered-budget bridge (d772aba) accepts the already-generated critic
    output degraded instead of killing the run, so the readiness critic's
    output is used and delivery completes through the real composer.
    """

    import json

    from debug_scripted_real_workflow import ScriptedRealRun, run_scripted_real_workflow

    result = _await(
        run_scripted_real_workflow(
            workspace=tmp_path,
            run_id="proof-readiness-cap-trip",
            scenario="readiness-cap-trip",
        )
    )
    assert isinstance(result, ScriptedRealRun)
    assert result.terminal_status == "completed"
    assert result.final_artifacts_published
    assert result.backed_claim_count >= 1
    assert "targeted_evidence" not in result.execution_trace

    events = [
        json.loads(line) for line in Path(result.journal_path).read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    # The cap trip degrades: the critic output rides through, the run passes
    # readiness with a real (not conservative-fallback) candidate, and delivery
    # completes. The pre-tiered-budget kill path (budget.exhausted journal
    # event, readiness_critic_fallback.execution_failed) must not reappear.
    assert not any(
        event.get("phase") == "readiness" and event.get("failure_category") == "budget.exhausted" for event in events
    )
    assert not any(str(event.get("failure_category", "")).startswith("readiness_critic_fallback") for event in events)
    assert any(
        event.get("readiness_route") == "pass"
        and event.get("readiness_blocked_count") == 0
        and event.get("readiness_pass_guard") is None
        for event in events
    )
