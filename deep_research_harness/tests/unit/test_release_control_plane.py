"""Full-real release acceptance control-plane contracts.

@impl EVH-004
@impl EVH-005
@impl EVH-009
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import types
from dataclasses import fields
from pathlib import Path

import pytest

import tests.scenarios.release as release_scenario
from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef
from deerflow_deep_research.domain.state import BundleLocalState
from deerflow_deep_research.domain.wave1 import (
    Wave1SemanticViolation,
    Wave1WorkerOutput,
    Wave1WorkerSource,
    validate_wave1_worker_output,
)
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from tests.scenarios.release import (
    RELEASE_SCENARIO,
    ReleaseAcceptanceFailure,
    ReleaseAttempt,
    ReleaseBundleExecutionAdapter,
    ReleaseOutcome,
    ReleasePreflightError,
    ReleaseRunner,
    _citation_source_evidence,
    _release_control_failure_code,
    _release_source_urls_by_policy,
    _selected_bundle_id,
    new_release_invocation,
    preflight_release_environment,
)

_RELEASE_SOURCE_URLS = (
    "https://docs.python.org/3.12/whatsnew/3.12.html",
    "https://docs.python.org/3.12/library/venv.html",
    "https://docs.python.org/3.12/library/removed.html",
)


def _wave1_output(source_urls: tuple[str, ...] | frozenset[str]) -> Wave1WorkerOutput:
    ordered_urls = tuple(source_urls)
    return Wave1WorkerOutput(
        schema_version=1,
        sources=tuple(
            Wave1WorkerSource(
                source_id=f"source:wave1_{index}",
                canonical_url=url,
                title=f"Source {index}",
            )
            for index, url in enumerate(ordered_urls)
        ),
    )


def _stub_tavily_search(monkeypatch: pytest.MonkeyPatch, results: list[dict[str, str]]):
    class FakeTavilyClient:
        calls: list[tuple[str, int]] = []

        def __init__(self, *, api_key: str) -> None:
            self.api_key = api_key

        def search(self, query: str, *, max_results: int) -> dict[str, object]:
            type(self).calls.append((query, max_results))
            return {"results": results}

    module = types.ModuleType("tavily")
    module.TavilyClient = FakeTavilyClient
    monkeypatch.setitem(sys.modules, "tavily", module)
    return FakeTavilyClient


def test_release_preflight_requires_explicit_confirmation() -> None:
    with pytest.raises(ReleasePreflightError, match="release_confirmation_missing") as caught:
        preflight_release_environment(environ={})

    assert caught.value.code == "release_confirmation_missing"


def test_release_preflight_requires_model_and_web_configuration() -> None:
    with pytest.raises(ReleasePreflightError, match="live_model_credentials_missing"):
        preflight_release_environment(environ={"RELEASE_E2E_CONFIRM": "1"})

    environment = preflight_release_environment(
        environ={
            "RELEASE_E2E_CONFIRM": "1",
            "OPENAI_API_KEY": "model-secret",
            "TAVILY_API_KEY": "web-secret",
        }
    )
    assert environment.model_provider == "openai"
    assert environment.web_provider == "tavily"


def test_release_preflight_cli_fails_without_confirmation_or_credentials() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/release_preflight.py"],
        capture_output=True,
        check=False,
        env={"PATH": os.environ.get("PATH", ""), "RELEASE_DISABLE_DOTENV": "1"},
        text=True,
    )

    assert result.returncode == 1
    assert "release_confirmation_missing" in result.stderr


def test_release_preflight_remains_available_without_an_execution_target() -> None:
    makefile = Path("Makefile").read_text(encoding="utf-8")

    assert "test-release-e2e" not in makefile
    assert Path("scripts/release_preflight.py").is_file()


def test_release_invocations_never_reuse_trusted_runtime_identity() -> None:
    first = new_release_invocation()
    second = new_release_invocation()

    assert first.thread_id != second.thread_id
    assert first.run_id != second.run_id
    assert first.user_id == second.user_id == "release-e2e"


def test_release_accepts_only_a_valid_public_bundle_result() -> None:
    bundle_id = f"b_{'a' * 43}"

    assert _selected_bundle_id({"bundle_id": bundle_id}) == bundle_id
    assert _selected_bundle_id({"bundle_id": "not-a-bundle"}) is None
    assert _selected_bundle_id({}) is None


def test_release_failure_code_exposes_only_bounded_terminal_classification() -> None:
    control = {
        "code": "blocked",
        "terminal_incident": {"phase": "wave0", "code": "output.structured_invalid"},
    }

    assert _release_control_failure_code("first_resume", control) == (
        "first_resume:blocked:wave0:output.structured_invalid"
    )
    assert (
        _release_control_failure_code(
            "first_resume",
            {"code": "blocked", "terminal_incident": {"phase": "wave1", "code": "research.blocked"}},
        )
        == "first_resume:blocked:wave1:research.blocked"
    )
    assert (
        _release_control_failure_code(
            "first_resume",
            {"code": "blocked", "terminal_incident": {"phase": "../../private", "code": "secret=value"}},
        )
        == "first_resume:blocked"
    )


def test_release_runner_has_no_legacy_graph_or_path_observation_fallback() -> None:
    source = Path("tests/scenarios/release.py").read_text(encoding="utf-8")

    for retired_token in (
        "_".join(("research", "id")),
        "bundle" + "_directory",
        "Graph" + "Host",
        "check" + "point",
    ):
        assert retired_token not in source


async def test_release_bundle_adapter_reauthorizes_the_public_id_before_observing_artifacts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """@impl EVH-024"""
    invocation = new_release_invocation()
    bundle_id = BundleId(f"b_{'a' * 43}")
    bundle = RunBundleRef(bundle_id=bundle_id, scope_bucket=f"s_{'b' * 43}")
    state = BundleLocalState(bundle_id=bundle_id)
    records = (types.SimpleNamespace(record_hash="ref:contained"),)
    lifecycle_calls: list[object] = []
    store_calls: list[object] = []

    class FakeLifecycle:
        def __init__(self, *, workspace_host_path) -> None:
            lifecycle_calls.append(workspace_host_path)

        async def resolve(self, *, scope, bundle_id):
            assert scope == (invocation.user_id, invocation.thread_id)
            assert bundle_id == bundle.bundle_id
            return bundle

        async def read_state(self, selected_bundle):
            assert selected_bundle == bundle
            return state

    class FakeStore:
        def __init__(self, selected_bundle) -> None:
            self.bundle = selected_bundle

        @classmethod
        async def create(cls, envelope, *, bundle):
            assert envelope is transport.envelope
            store_calls.append(bundle)
            return cls(bundle)

        async def load_records(self):
            return records

        async def observe_final_artifacts(self):
            return (b"# Report\n", b'{"claims":{}}')

    transport = types.SimpleNamespace(envelope=types.SimpleNamespace(workspace_host_path=tmp_path))
    monkeypatch.setattr(release_scenario, "BundleLifecycle", FakeLifecycle)
    monkeypatch.setattr(release_scenario, "WorkUnitStore", FakeStore)

    observation = await ReleaseBundleExecutionAdapter(
        adapter=transport,
        graph_executor=object(),
        invocation=invocation,
    ).observe(bundle_id=bundle_id.value)

    assert observation is not None
    assert observation.state is state
    assert observation.records == records
    assert observation.final_artifacts == (b"# Report\n", b'{"claims":{}}')
    assert lifecycle_calls == [tmp_path]
    assert store_calls == [bundle]


async def test_release_bundle_adapter_fails_on_bundle_loss_before_any_store_observation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """@impl EVH-024"""
    invocation = new_release_invocation()
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(
        scope=(invocation.user_id, invocation.thread_id),
        request_text="Release observation must not recover a missing Bundle.",
    )
    shutil.rmtree(lifecycle.private_root(bundle))
    store_calls: list[object] = []

    class ForbiddenStore:
        @classmethod
        async def create(cls, _envelope, *, bundle):
            store_calls.append(bundle)
            raise AssertionError("lost Bundle must fail before contained-store access")

    transport = types.SimpleNamespace(envelope=types.SimpleNamespace(workspace_host_path=tmp_path))
    monkeypatch.setattr(release_scenario, "WorkUnitStore", ForbiddenStore)

    observation = await ReleaseBundleExecutionAdapter(
        adapter=transport,
        graph_executor=object(),
        invocation=invocation,
    ).observe(bundle_id=bundle.bundle_id.value)

    assert observation is None
    assert store_calls == []


def test_release_scenario_requires_normal_path_without_conditional_rerun_branches() -> None:
    assert RELEASE_SCENARIO.expected_trace == (
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


def test_release_scenario_owns_the_model_led_chinese_confirmation_transcript() -> None:
    """@impl EVH-024"""
    assert RELEASE_SCENARIO.request_text == (
        "请只使用 Python 官方文档，用中文为一个现有 Python Web 服务写一份升级到 Python 3.12 前的检查清单："
        "列出三项最重要的兼容性或运行时变化，并为每项给出具体来源链接。"
    )
    assert RELEASE_SCENARIO.confirmation_text == "确认"
    assert RELEASE_SCENARIO.declared_source_urls == _RELEASE_SOURCE_URLS
    assert all("profile" not in field.name for field in fields(RELEASE_SCENARIO))


async def test_release_web_adapter_normalizes_the_declared_sources_and_restricts_its_query(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl EVH-024"""
    from tests.scenarios.canaries import _LiveWebSearch

    client = _stub_tavily_search(
        monkeypatch,
        [
            {
                "title": "What's New in Python 3.12",
                "url": "HTTPS://DOCS.PYTHON.ORG:443/3.12/whatsnew/3.12.html#overview",
                "content": "release notes",
            },
            {
                "title": "venv",
                "url": "https://docs.python.org/3.12/library/venv.html/",
                "content": "virtual environments",
            },
            {
                "title": "Removed Modules",
                "url": "https://docs.python.org/3.12/library/removed.html#removed",
                "content": "removed modules",
            },
        ],
    )

    response = await _LiveWebSearch("test-key", allowed_source_urls=_RELEASE_SOURCE_URLS).search(
        "Python 3.12 upgrade checklist"
    )

    assert client.calls == [("Python 3.12 upgrade checklist site:docs.python.org/3.12", 3)]
    assert json.loads(response) == [
        {
            "title": "What's New in Python 3.12",
            "url": _RELEASE_SOURCE_URLS[0],
            "snippet": "release notes",
        },
        {"title": "venv", "url": _RELEASE_SOURCE_URLS[1], "snippet": "virtual environments"},
        {"title": "Removed Modules", "url": _RELEASE_SOURCE_URLS[2], "snippet": "removed modules"},
    ]


async def test_release_web_adapter_fails_closed_when_no_declared_search_result_remains(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl EVH-024"""
    from tests.scenarios.canaries import _LiveWebSearch

    _stub_tavily_search(
        monkeypatch,
        [
            {
                "title": "Outside source",
                "url": "https://example.com/python-3-12",
                "content": "untrusted source",
            }
        ],
    )

    adapter = _LiveWebSearch("test-key", allowed_source_urls=_RELEASE_SOURCE_URLS)

    async def fetch_declared_sources() -> list[dict[str, str]]:
        return []

    monkeypatch.setattr(adapter, "_fetch_declared_sources", fetch_declared_sources)
    with pytest.raises(ValueError, match="release_source_set_empty"):
        await adapter.search("Python 3.12 upgrade checklist")


async def test_release_web_adapter_discards_out_of_set_results_when_declared_results_exist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl EVH-024"""
    from tests.scenarios.canaries import _LiveWebSearch

    _stub_tavily_search(
        monkeypatch,
        [
            {
                "title": "venv",
                "url": "https://docs.python.org/3.12/library/venv.html#creating-virtual-environments",
                "content": "virtual environments",
            },
            {
                "title": "Outside source",
                "url": "https://example.com/python-3-12",
                "content": "untrusted source",
            },
        ],
    )

    response = await _LiveWebSearch("test-key", allowed_source_urls=_RELEASE_SOURCE_URLS).search(
        "Python 3.12 upgrade checklist"
    )

    assert json.loads(response) == [
        {
            "title": "venv",
            "url": _RELEASE_SOURCE_URLS[1],
            "snippet": "virtual environments",
        }
    ]


async def test_release_web_adapter_fetches_declared_sources_when_search_index_misses_them(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl EVH-024"""
    from tests.scenarios.canaries import _LiveWebSearch

    _stub_tavily_search(
        monkeypatch,
        [
            {
                "title": "Current documentation",
                "url": "https://docs.python.org/3/whatsnew/3.12.html",
                "content": "unversioned index result",
            }
        ],
    )
    adapter = _LiveWebSearch("test-key", allowed_source_urls=_RELEASE_SOURCE_URLS)

    async def fetch_declared_sources() -> list[dict[str, str]]:
        return [
            {
                "title": "What's New in Python 3.12",
                "url": _RELEASE_SOURCE_URLS[0],
                "snippet": "versioned source body",
            }
        ]

    monkeypatch.setattr(adapter, "_fetch_declared_sources", fetch_declared_sources)
    response = await adapter.search("Python 3.12 compatibility")

    assert json.loads(response) == [
        {
            "title": "What's New in Python 3.12",
            "url": _RELEASE_SOURCE_URLS[0],
            "snippet": "versioned source body",
        }
    ]


async def test_release_web_adapter_completes_only_the_declared_phase_view(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl EVH-024"""
    from tests.scenarios.canaries import _LiveWebSearch

    wave1_urls = frozenset(_RELEASE_SOURCE_URLS[1:])
    _stub_tavily_search(
        monkeypatch,
        [
            {
                "title": "venv",
                "url": _RELEASE_SOURCE_URLS[1],
                "content": "virtual environments",
            }
        ],
    )
    adapter = _LiveWebSearch("test-key", allowed_source_urls=_RELEASE_SOURCE_URLS)
    fetched_views: list[frozenset[str]] = []

    async def fetch_declared_sources(source_urls: frozenset[str]) -> list[dict[str, str]]:
        fetched_views.append(source_urls)
        return [
            {
                "title": "Removed Modules",
                "url": _RELEASE_SOURCE_URLS[2],
                "snippet": "removed modules",
            }
        ]

    monkeypatch.setattr(adapter, "_fetch_declared_sources", fetch_declared_sources)
    response = await adapter.search(
        "Python 3.12 upgrade checklist",
        allowed_source_urls=wave1_urls,
        require_complete_source_view=True,
    )

    assert fetched_views == [frozenset({_RELEASE_SOURCE_URLS[2]})]
    assert {item["url"] for item in json.loads(response)} == set(wave1_urls)
    assert _RELEASE_SOURCE_URLS[0] not in response


async def test_release_web_adapter_fails_closed_when_a_phase_view_stays_incomplete(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl EVH-024"""
    from tests.scenarios.canaries import _LiveWebSearch

    wave1_urls = frozenset(_RELEASE_SOURCE_URLS[1:])
    _stub_tavily_search(
        monkeypatch,
        [
            {
                "title": "venv",
                "url": _RELEASE_SOURCE_URLS[1],
                "content": "virtual environments",
            }
        ],
    )
    adapter = _LiveWebSearch("test-key", allowed_source_urls=_RELEASE_SOURCE_URLS)

    async def fetch_declared_sources(source_urls: frozenset[str]) -> list[dict[str, str]]:
        assert source_urls == frozenset({_RELEASE_SOURCE_URLS[2]})
        return []

    monkeypatch.setattr(adapter, "_fetch_declared_sources", fetch_declared_sources)
    with pytest.raises(ValueError, match="release_source_view_incomplete"):
        await adapter.search(
            "Python 3.12 upgrade checklist",
            allowed_source_urls=wave1_urls,
            require_complete_source_view=True,
        )


def test_release_source_partition_preserves_wave1_two_new_source_floor() -> None:
    """@impl EVH-024"""
    views = _release_source_urls_by_policy(RELEASE_SCENARIO)

    assert views == {
        "wave0-source-intake": frozenset({_RELEASE_SOURCE_URLS[0]}),
        "wave1-evidence-extraction": frozenset(_RELEASE_SOURCE_URLS[1:]),
    }
    assert validate_wave1_worker_output(
        _wave1_output(views["wave1-evidence-extraction"]),
        wave0_urls=views["wave0-source-intake"],
    ) == frozenset(_RELEASE_SOURCE_URLS[1:])


def test_release_source_partition_does_not_weaken_the_old_wave1_collision_guard() -> None:
    """@impl EVH-024"""
    with pytest.raises(Wave1SemanticViolation, match="wave1_new_source_floor_not_met"):
        validate_wave1_worker_output(
            _wave1_output(_RELEASE_SOURCE_URLS),
            wave0_urls=_RELEASE_SOURCE_URLS[:2],
        )


def test_release_citation_evidence_fails_closed_for_an_accepted_out_of_set_final_source() -> None:
    """@impl EVH-024"""
    evidence = _citation_source_evidence(
        accepted_submission_refs=("ref:outside",),
        citation_bindings={"claim-1": ("ref:outside",)},
        records=(
            types.SimpleNamespace(
                record_hash="ref:outside",
                source_refs=(types.SimpleNamespace(canonical_url="https://example.com/python-3-12"),),
            ),
        ),
        declared_source_urls=_RELEASE_SOURCE_URLS,
    )

    assert evidence.declared_source_set_only is False
    assert evidence.distinct_source_count == 1


async def test_release_runner_reports_bounded_visible_retry_and_required_terminal_artifacts() -> None:
    invocation = new_release_invocation()
    attempts = iter(
        (
            ReleaseAttempt(outcome=None, error_code="provider_timeout", wall_time_seconds=1.0),
            ReleaseAttempt(
                outcome=ReleaseOutcome(
                    invocation=invocation,
                    bundle_id=f"b_{'a' * 43}",
                    terminal_status="completed",
                    lifecycle_trace=RELEASE_SCENARIO.expected_trace,
                    accepted_submission_refs=("ref:source-one", "ref:source-two", "ref:source-three"),
                    artifacts=("final/report.md", "final/claim-citation-map.json"),
                    citation_bindings={
                        "claim-1": ("ref:source-one",),
                        "claim-2": ("ref:source-two",),
                        "claim-3": ("ref:source-three",),
                    },
                    confirmation_traversed=True,
                    report_nonempty=True,
                    report_contains_chinese=True,
                    declared_source_set_id="python-docs-3.12",
                    declared_source_set_only=True,
                    distinct_source_count=2,
                    contained=True,
                    cleaned_up=True,
                ),
                error_code=None,
                wall_time_seconds=2.0,
                response_shapes=(
                    {
                        "content_chars": 42,
                        "content_kind": "json_object",
                        "json_keys": ["summary"],
                        "tool_names": [],
                    },
                ),
            ),
        )
    )

    async def execute(_scenario, selected_invocation):
        assert selected_invocation == invocation
        return next(attempts)

    report = await ReleaseRunner(executor=execute, max_attempts=2).run(RELEASE_SCENARIO, invocation)

    assert report.attempt_count == 2
    assert report.retry_count == 1
    assert [attempt.error_code for attempt in report.attempts] == ["provider_timeout", None]
    assert report.attempts[1].response_shapes[0]["content_kind"] == "json_object"
    assert report.outcome_summary == {
        "terminal_status": "completed",
        "lifecycle_trace": RELEASE_SCENARIO.expected_trace,
        "accepted_count": 3,
        "artifacts": ("final/report.md", "final/claim-citation-map.json"),
        "citation_claim_count": 3,
        "citation_ref_count": 3,
        "confirmation_traversed": True,
        "report_nonempty": True,
        "report_contains_chinese": True,
        "declared_source_set_id": "python-docs-3.12",
        "declared_source_set_only": True,
        "distinct_source_count": 2,
        "contained": True,
        "cleaned_up": True,
    }
    assert report.hard_invariants == {
        "terminal_completed": True,
        "lifecycle_trace_complete": True,
        "accepted_evidence_present": True,
        "report_artifacts_present": True,
        "citation_bindings_valid": True,
        "paths_contained": True,
        "cleanup_complete": True,
        "bundle_result_bound": True,
        "confirmation_traversed": True,
        "report_nonempty": True,
        "report_contains_chinese": True,
        "minimum_cited_claims": True,
        "declared_source_set_only": True,
        "minimum_distinct_sources": True,
    }


async def test_release_runner_reports_the_complete_model_led_smoke_evidence() -> None:
    """@impl EVH-024"""
    invocation = new_release_invocation()

    async def execute(_scenario, selected_invocation):
        assert selected_invocation == invocation
        return ReleaseAttempt(
            outcome=ReleaseOutcome(
                invocation=invocation,
                bundle_id=f"b_{'a' * 43}",
                terminal_status="completed",
                lifecycle_trace=RELEASE_SCENARIO.expected_trace,
                accepted_submission_refs=("ref:source-one", "ref:source-two", "ref:source-three"),
                artifacts=("final/report.md", "final/claim-citation-map.json"),
                citation_bindings={
                    "claim-1": ("ref:source-one",),
                    "claim-2": ("ref:source-two",),
                    "claim-3": ("ref:source-three",),
                },
                confirmation_traversed=True,
                report_nonempty=True,
                report_contains_chinese=True,
                declared_source_set_id="python-docs-3.12",
                declared_source_set_only=True,
                distinct_source_count=2,
                contained=True,
                cleaned_up=True,
            ),
            error_code=None,
            wall_time_seconds=1.0,
        )

    report = await ReleaseRunner(executor=execute, max_attempts=1).run(RELEASE_SCENARIO, invocation)

    assert report.hard_invariants == {
        "terminal_completed": True,
        "lifecycle_trace_complete": True,
        "accepted_evidence_present": True,
        "report_artifacts_present": True,
        "citation_bindings_valid": True,
        "paths_contained": True,
        "cleanup_complete": True,
        "bundle_result_bound": True,
        "confirmation_traversed": True,
        "report_nonempty": True,
        "report_contains_chinese": True,
        "minimum_cited_claims": True,
        "declared_source_set_only": True,
        "minimum_distinct_sources": True,
    }
    assert report.outcome_summary is not None
    assert report.outcome_summary["declared_source_set_id"] == "python-docs-3.12"
    assert report.outcome_summary["distinct_source_count"] == 2
    assert "https://" not in json.dumps(report.to_dict())


async def test_release_runner_rejects_claims_without_backing_references() -> None:
    """@impl EVH-024"""
    invocation = new_release_invocation()

    async def execute(_scenario, _invocation):
        return ReleaseAttempt(
            outcome=ReleaseOutcome(
                invocation=invocation,
                bundle_id=f"b_{'a' * 43}",
                terminal_status="completed",
                lifecycle_trace=RELEASE_SCENARIO.expected_trace,
                accepted_submission_refs=("ref:source-one", "ref:source-two", "ref:source-three"),
                artifacts=("final/report.md", "final/claim-citation-map.json"),
                citation_bindings={"claim-1": (), "claim-2": (), "claim-3": ()},
                confirmation_traversed=True,
                report_nonempty=True,
                report_contains_chinese=True,
                declared_source_set_id="python-docs-3.12",
                declared_source_set_only=True,
                distinct_source_count=2,
                contained=True,
                cleaned_up=True,
            ),
            error_code=None,
            wall_time_seconds=1.0,
        )

    with pytest.raises(ReleaseAcceptanceFailure, match="citation_bindings_valid|minimum_cited_claims") as caught:
        await ReleaseRunner(executor=execute, max_attempts=1).run(RELEASE_SCENARIO, invocation)

    assert caught.value.report.hard_invariants["citation_bindings_valid"] is False
    assert caught.value.report.hard_invariants["minimum_cited_claims"] is False


async def test_release_runner_rejects_bypassed_confirmation() -> None:
    """@impl EVH-024"""
    invocation = new_release_invocation()

    async def execute(_scenario, _invocation):
        return ReleaseAttempt(
            outcome=ReleaseOutcome(
                invocation=invocation,
                bundle_id=f"b_{'a' * 43}",
                terminal_status="completed",
                lifecycle_trace=RELEASE_SCENARIO.expected_trace,
                accepted_submission_refs=("ref:source-one", "ref:source-two", "ref:source-three"),
                artifacts=("final/report.md", "final/claim-citation-map.json"),
                citation_bindings={
                    "claim-1": ("ref:source-one",),
                    "claim-2": ("ref:source-two",),
                    "claim-3": ("ref:source-three",),
                },
                confirmation_traversed=False,
                report_nonempty=True,
                report_contains_chinese=True,
                declared_source_set_id="python-docs-3.12",
                declared_source_set_only=True,
                distinct_source_count=2,
                contained=True,
                cleaned_up=True,
            ),
            error_code=None,
            wall_time_seconds=1.0,
        )

    with pytest.raises(ReleaseAcceptanceFailure, match="confirmation_traversed") as caught:
        await ReleaseRunner(executor=execute, max_attempts=1).run(RELEASE_SCENARIO, invocation)

    assert caught.value.report.hard_invariants["confirmation_traversed"] is False


async def test_release_trace_accepts_consecutive_visible_internal_retries() -> None:
    invocation = new_release_invocation()
    trace_with_retries = (
        "bootstrap",
        "hitl1",
        "topic_planning",
        "wave0",
        "wave0",
        "wave0",
        "wave1",
        "wave2_synthesis",
        "hitl2",
        "readiness",
        "final_delivery",
    )

    async def execute(_scenario, _invocation):
        return ReleaseAttempt(
            outcome=ReleaseOutcome(
                invocation=invocation,
                bundle_id=f"b_{'a' * 43}",
                terminal_status="completed",
                lifecycle_trace=trace_with_retries,
                accepted_submission_refs=("ref:source-one", "ref:source-two", "ref:source-three"),
                artifacts=("final/report.md", "final/claim-citation-map.json"),
                citation_bindings={
                    "claim-1": ("ref:source-one",),
                    "claim-2": ("ref:source-two",),
                    "claim-3": ("ref:source-three",),
                },
                confirmation_traversed=True,
                report_nonempty=True,
                report_contains_chinese=True,
                declared_source_set_id="python-docs-3.12",
                declared_source_set_only=True,
                distinct_source_count=2,
                contained=True,
                cleaned_up=True,
            ),
            error_code=None,
            wall_time_seconds=1.0,
        )

    report = await ReleaseRunner(executor=execute, max_attempts=1).run(RELEASE_SCENARIO, invocation)

    assert report.hard_invariants["lifecycle_trace_complete"] is True
    assert report.outcome_summary is not None
    assert report.outcome_summary["lifecycle_trace"] == trace_with_retries


async def test_release_trace_rejects_more_than_three_consecutive_phase_visits() -> None:
    invocation = new_release_invocation()
    excessive_trace = (*RELEASE_SCENARIO.expected_trace[:3], *("wave0",) * 4, *RELEASE_SCENARIO.expected_trace[4:])

    async def execute(_scenario, _invocation):
        return ReleaseAttempt(
            outcome=ReleaseOutcome(
                invocation=invocation,
                bundle_id=f"b_{'a' * 43}",
                terminal_status="completed",
                lifecycle_trace=excessive_trace,
                accepted_submission_refs=("ref:source-one", "ref:source-two", "ref:source-three"),
                artifacts=("final/report.md", "final/claim-citation-map.json"),
                citation_bindings={
                    "claim-1": ("ref:source-one",),
                    "claim-2": ("ref:source-two",),
                    "claim-3": ("ref:source-three",),
                },
                confirmation_traversed=True,
                report_nonempty=True,
                report_contains_chinese=True,
                declared_source_set_id="python-docs-3.12",
                declared_source_set_only=True,
                distinct_source_count=2,
                contained=True,
                cleaned_up=True,
            ),
            error_code=None,
            wall_time_seconds=1.0,
        )

    with pytest.raises(ReleaseAcceptanceFailure) as caught:
        await ReleaseRunner(executor=execute, max_attempts=1).run(RELEASE_SCENARIO, invocation)

    assert caught.value.report.hard_invariants["lifecycle_trace_complete"] is False


async def test_release_runner_rejects_missing_artifacts_with_stable_identity() -> None:
    invocation = new_release_invocation()

    async def execute(_scenario, _invocation):
        return ReleaseAttempt(
            outcome=ReleaseOutcome(
                invocation=invocation,
                bundle_id=f"b_{'a' * 43}",
                terminal_status="completed",
                lifecycle_trace=RELEASE_SCENARIO.expected_trace,
                accepted_submission_refs=("ref:source-one", "ref:source-two", "ref:source-three"),
                artifacts=("final/report.md",),
                citation_bindings={
                    "claim-1": ("ref:source-one",),
                    "claim-2": ("ref:source-two",),
                    "claim-3": ("ref:source-three",),
                },
                confirmation_traversed=True,
                report_nonempty=True,
                report_contains_chinese=True,
                declared_source_set_id="python-docs-3.12",
                declared_source_set_only=True,
                distinct_source_count=2,
                contained=True,
                cleaned_up=True,
            ),
            error_code=None,
            wall_time_seconds=1.0,
        )

    with pytest.raises(
        ReleaseAcceptanceFailure,
        match=f"scenario={RELEASE_SCENARIO.scenario_id} lane=release authenticity=full_real_pipeline",
    ) as caught:
        await ReleaseRunner(executor=execute, max_attempts=1).run(RELEASE_SCENARIO, invocation)

    assert caught.value.report.hard_invariants["report_artifacts_present"] is False
