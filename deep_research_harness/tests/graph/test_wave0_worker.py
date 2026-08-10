"""Wave0 worker prompt, structured output, and intent materialization.

@impl WAN-001
@impl WAN-002
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef, run_bundle_root
from deerflow_deep_research.domain.work_units import (
    Attempt,
    Wave0SourceMeta,
    Wave0WorkerOutput,
    WorkerSource,
    WorkSpec,
    compute_work_spec_hash,
)
from deerflow_deep_research.graph.nodes.wave0.prompts import (
    WAVE0_REPAIR_VALIDATION_CATEGORY,
    build_wave0_assignment_projection,
    build_wave0_repair_prompt,
    build_wave0_result_document,
    build_wave0_worker_prompt,
    parse_wave0_worker_output,
)
from deerflow_deep_research.graph.nodes.wave0.subgraph import _canonical_validation_code, materialize_wave0_intents

BUNDLE = RunBundleRef(
    bundle_id=BundleId("b_" + "A" * 43),
    scope_bucket="s_" + "B" * 43,
)
BUNDLE_ID = BUNDLE.bundle_id.value
BUNDLE_ROOT = run_bundle_root(BUNDLE)
WORK_ID = "g0_wave0_w0000"
ATTEMPT_ID = "g0_wave0_w0000_a00"
NOW = datetime(2026, 7, 14, tzinfo=UTC)


def _topic(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "topic_id": "batteries",
        "slug": "batteries",
        "title": "Grid-scale batteries",
        "scope": "Grid battery economics",
        "must_answer_bindings": ["Q1"],
        "search_dimensions": [],
        "exclusions": [],
    }
    payload.update(overrides)
    return payload


def _spec(**overrides: object) -> WorkSpec:
    payload: dict[str, object] = {
        "schema_version": 1,
        "bundle_id": BUNDLE_ID,
        "generation": 0,
        "phase": "wave0",
        "work_id": WORK_ID,
        "work_ordinal": 0,
        "worker_role": "wave0_intake",
        "scope": ("batteries",),
        "result_contract": "wave0.source-intake",
        "result_schema_version": 1,
        "required_outputs": (),
    }
    payload.update(overrides)
    payload["spec_hash"] = compute_work_spec_hash(payload)
    return WorkSpec.model_validate(payload)


def _attempt(spec: WorkSpec) -> Attempt:
    return Attempt.model_validate(
        {
            "schema_version": 1,
            "bundle_id": spec.bundle_id,
            "generation": spec.generation,
            "phase": spec.phase,
            "work_id": spec.work_id,
            "attempt_id": ATTEMPT_ID,
            "attempt_ordinal": 0,
            "spec_hash": spec.spec_hash,
            "status": "running",
            "created_at": NOW,
            "started_at": NOW,
            "expires_at": None,
            "terminal_at": None,
            "terminal_code": None,
        }
    )


def _worker_source(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "source_id": "source:1",
        "canonical_url": "https://example.com/path",
        "title": "Example",
        "fetch_status": "fetched",
    }
    payload.update(overrides)
    return payload


def test_materialize_wave0_intents_one_per_topic_and_rejects_empty() -> None:
    intents = materialize_wave0_intents((_topic(), _topic(topic_id="solar")))
    assert [intent.scope[0] for intent in intents] == ["batteries", "solar"]
    assert all(intent.worker_role == "wave0_intake" for intent in intents)
    assert all(intent.result_contract == "wave0.source-intake" for intent in intents)

    with pytest.raises(ValueError, match="topic_registry_empty"):
        materialize_wave0_intents(())
    with pytest.raises(ValueError, match="topic_registry_empty"):
        materialize_wave0_intents(None)


def test_build_wave0_worker_prompt_carries_topic_constraints() -> None:
    """@impl WAN-009"""
    request = build_wave0_worker_prompt(_spec(), (_topic(),))
    assert "Grid-scale batteries" in request.objective
    assert "Q1" in request.objective
    assert "Trusted assignment (scope only)" in request.objective
    assert "activated source-intake capability" in request.objective
    assert "MUST call at least one available web search or fetch tool" not in request.objective
    assert "assignment-relevant, independent source candidates" not in request.objective
    assert "honest limitation" not in request.objective
    assert request.minimum_tool_calls == 1
    assert request.tool_call_limit == 3
    assert "Return exactly one JSON object" in request.expected_output
    assert '"schema_version":1,"sources":[' in request.expected_output
    assert all(field in request.expected_output for field in WorkerSource.model_fields)
    assert "content_ref" not in request.objective
    assert "content_hash" not in request.objective
    assert "byte_count" not in request.objective


def test_wave0_worker_expected_output_is_a_response_shape_not_a_schema_descriptor() -> None:
    request = build_wave0_worker_prompt(_spec(), (_topic(),))

    assert '"schema_version":1,"sources":[' in request.expected_output
    assert "Return exactly one JSON object" in request.expected_output
    for forbidden in (
        '"instruction"',
        '"required_keys"',
        '"source_required_keys"',
        '"bounds"',
        '"claims"',
        '"questions"',
    ):
        assert forbidden not in request.expected_output


def test_parse_wave0_worker_output_round_trip_and_rejects_invalid() -> None:
    payload = json.dumps(
        {"schema_version": 1, "sources": [_worker_source()], "baseline_facts": ["fact"], "limitations": ""}
    )
    parsed = parse_wave0_worker_output(payload)
    assert isinstance(parsed, Wave0WorkerOutput)
    assert parsed.sources[0].fetch_status == "fetched"

    with pytest.raises(ValueError, match="wave0_worker_output_json_invalid"):
        parse_wave0_worker_output("not json")
    with pytest.raises(ValueError, match="wave0_worker_output_empty"):
        parse_wave0_worker_output("   ")
    with pytest.raises(ValidationError):
        parse_wave0_worker_output(json.dumps({"schema_version": 1, "sources": []}))


@pytest.mark.parametrize(
    ("candidate", "expected_code"),
    [
        pytest.param("   ", "wave0_worker_output_empty", id="empty"),
        pytest.param("not json", "wave0_worker_output_json_invalid", id="json-invalid"),
        pytest.param(
            json.dumps({"schema_version": 1, "sources": []}),
            "wave0_worker_output_invalid",
            id="shape-invalid",
        ),
    ],
)
def test_wave0_parser_failure_is_mapped_to_a_closed_journal_code(candidate: str, expected_code: str) -> None:
    """@impl WAN-010"""

    with pytest.raises(ValueError) as error:
        parse_wave0_worker_output(candidate)

    assert _canonical_validation_code(error.value) == expected_code


def test_wave0_repair_prompt_carries_bounded_tool_results_as_untrusted_data() -> None:
    """@impl WAN-009"""
    assignment = build_wave0_assignment_projection(
        _spec(),
        (_topic(work_id="raw-work-id-must-not-render", attempt_id="raw-attempt-id-must-not-render"),),
    )
    request = build_wave0_repair_prompt(
        "draft prose",
        ('[{"url":"https://example.com/source","title":"Source"}]',),
        assignment=assignment,
        validation_category=WAVE0_REPAIR_VALIDATION_CATEGORY,
    )
    assert request.tools_enabled is False
    assert "<untrusted-source-data>" in request.objective
    assert "https://example.com/source" in request.objective
    trusted, untrusted = request.objective.split("<untrusted-source-data>", maxsplit=1)
    assert "Grid-scale batteries" in trusted
    assert WAVE0_REPAIR_VALIDATION_CATEGORY in trusted
    assert "raw-work-id-must-not-render" not in request.objective
    assert "raw-attempt-id-must-not-render" not in request.objective
    assert "model_draft:\ndraft prose" in untrusted
    assert "topic projection" not in untrusted
    assert "closed initial structured-output category" in request.objective
    assert "activated zero-tool repair capability" in request.objective
    assert "cannot supply a source, URL, title, fact, fetch outcome, or limitation" not in request.objective
    assert "Return JSON only" not in request.objective


def test_wave0_repair_prompt_rejects_raw_or_open_repair_context() -> None:
    with pytest.raises(ValueError, match="wave0_repair_assignment_invalid"):
        build_wave0_repair_prompt(
            "draft",
            assignment={"work_id": WORK_ID},
            validation_category=WAVE0_REPAIR_VALIDATION_CATEGORY,
        )
    with pytest.raises(ValueError, match="wave0_repair_validation_category_invalid"):
        build_wave0_repair_prompt(
            "draft",
            assignment=build_wave0_assignment_projection(_spec(), (_topic(),)),
            validation_category="submission_validation_failed",
        )


def test_worker_source_canonicalizes_untrusted_model_url() -> None:
    source = WorkerSource.model_validate(_worker_source(canonical_url="HTTPS://Example.com:443/path/#frag"))

    assert source.canonical_url == "https://example.com/path"


@pytest.mark.parametrize(
    "alias",
    ["available", "accessible", "retrieved", "success", "available_via_search"],
)
def test_worker_source_normalizes_fetched_status_aliases(alias: str) -> None:
    source = WorkerSource.model_validate(_worker_source(fetch_status=alias))

    assert source.fetch_status == "fetched"


@pytest.mark.parametrize(
    "alias",
    ["unavailable", "unreachable", "failed", "paywalled", "not_fetched", "unverified"],
)
def test_worker_source_normalizes_degraded_status_aliases(alias: str) -> None:
    source = WorkerSource.model_validate(_worker_source(fetch_status=alias))

    assert source.fetch_status == "degraded"


def test_worker_source_rejects_unknown_fetch_status() -> None:
    with pytest.raises(ValidationError, match="fetch_status"):
        WorkerSource.model_validate(_worker_source(fetch_status="maybe"))


def test_wave0_worker_output_normalizes_bounded_limitations_list() -> None:
    output = parse_wave0_worker_output(
        json.dumps(
            {
                "schema_version": 1,
                "sources": [_worker_source()],
                "limitations": ["Search snippets only", "No full-text fetch"],
            }
        )
    )

    assert output.limitations == "Search snippets only; No full-text fetch"


def test_wave0_worker_output_keeps_valid_sources_and_records_dropped_items() -> None:
    output = parse_wave0_worker_output(
        json.dumps(
            {
                "schema_version": 1,
                "sources": [
                    _worker_source(source_id="source:valid"),
                    _worker_source(source_id="source:bad-url", canonical_url="not-a-url"),
                    _worker_source(source_id="source:bad-status", fetch_status="maybe"),
                ],
                "limitations": "Search-only evidence",
            }
        )
    )

    assert tuple(source.source_id for source in output.sources) == ("source:valid",)
    assert output.limitations == "Search-only evidence; Dropped 2 invalid source records."


def test_build_wave0_result_document_merges_identity_and_sources() -> None:
    spec = _spec()
    attempt = _attempt(spec)
    output = parse_wave0_worker_output(
        json.dumps({"schema_version": 1, "sources": [_worker_source()], "baseline_facts": ["fact"], "limitations": ""})
    )
    metas = tuple(
        Wave0SourceMeta(
            source_id=source.source_id,
            canonical_url=source.canonical_url,
            title=source.title,
            content_ref=f"{BUNDLE_ROOT}/work/{WORK_ID}/{ATTEMPT_ID}/cache/source-0.json",
            fetch_status=source.fetch_status,
        )
        for source in output.sources
    )
    doc = build_wave0_result_document(spec, attempt, metas, output.baseline_facts, output.limitations)
    assert doc.bundle_id == spec.bundle_id
    assert doc.work_id == spec.work_id
    assert doc.attempt_id == attempt.attempt_id
    assert doc.result_contract == "wave0.source-intake"
    assert doc.source_ids == ("source:1",)
    assert doc.sources[0].title == "Example"
