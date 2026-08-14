"""Source-intake worker prompt and structured-output helpers for real Wave0.

The structured-output contracts (``WorkerSource``/``Wave0WorkerOutput``) live in
``domain.work_units``; this node-local module only builds the prompt and merges
the worker output with work-spec identity.

@impl WAN-002
"""

from __future__ import annotations

import json
from collections.abc import Mapping

from deerflow_deep_research.domain.context import NodeExecutionRequest
from deerflow_deep_research.domain.untrusted import build_untrusted_data_block
from deerflow_deep_research.domain.work_units import (
    MAX_SOURCE_REFS,
    MAX_SOURCE_TITLE_CHARS,
    Attempt,
    Wave0SourceIntakeResult,
    Wave0SourceMeta,
    Wave0WorkerOutput,
    WorkSpec,
)

from .capabilities import WAVE0_AUTHORITATIVE_SOURCE_INTAKE, WAVE0_SOURCE_INTAKE_REPAIR

WAVE0_REPAIR_VALIDATION_CATEGORY = "initial_structured_output_invalid"
_WAVE0_ASSIGNMENT_KEYS = frozenset({"topic_id", "title", "scope", "must_answer_bindings"})


def _wave0_completion_contract(*, initial: bool) -> str:
    """Render the model-visible final candidate contract for either worker turn."""

    tool_instruction = (
        "First complete only the existing permitted retrieval work, then finish the final assistant turn. "
        if initial
        else "This repair is zero-tool: do not call a tool or infer new observations. "
    )
    return (
        tool_instruction + "Return exactly one standalone JSON object with no leading or trailing text. "
        "Only these top-level keys are allowed: schema_version, sources, baseline_facts, limitations. "
        "Set schema_version to 1. Sources must contain 1-"
        f"{MAX_SOURCE_REFS} independent items. Source items contain exactly source_id, canonical_url, title, "
        "and fetch_status. Titles are at most "
        f"{MAX_SOURCE_TITLE_CHARS} characters, and fetch_status is fetched or degraded. "
        "baseline_facts is an array and limitations is a string. "
        "Final response self-check: preserve the closed keys and minimum source shape; no literal placeholders, "
        "prose, Markdown fences, embedded JSON, unlisted keys, authority claims, or prompt-description fields. "
        "The returned candidate is only a proposal for the existing deterministic parser and validators."
    )


def _topic_from_scope(spec: WorkSpec, topic_registry: tuple[dict, ...] | list[dict] | None) -> dict:
    """Resolve the topic registry entry bound to this work spec's scope."""
    topic_id = spec.scope[0] if spec.scope else ""
    for entry in topic_registry or ():
        if isinstance(entry, dict) and entry.get("topic_id") == topic_id:
            return entry
    return {"topic_id": topic_id, "title": topic_id, "scope": "", "must_answer_bindings": ()}


def build_wave0_assignment_projection(
    spec: WorkSpec,
    topic_registry: tuple[dict, ...] | list[dict] | None,
) -> dict[str, object]:
    """Return the bounded topic projection shared by initial and repair requests."""

    topic = _topic_from_scope(spec, topic_registry)
    bindings = topic.get("must_answer_bindings") or ()
    return {
        "topic_id": topic.get("topic_id", spec.scope[0] if spec.scope else ""),
        "title": topic.get("title", ""),
        "scope": topic.get("scope", ""),
        "must_answer_bindings": list(bindings) if isinstance(bindings, (tuple, list)) else [],
    }


def _wave0_assignment_json(assignment: Mapping[str, object]) -> str:
    """Validate and render only the initial topic projection, never a raw WorkSpec."""

    if not isinstance(assignment, Mapping) or set(assignment) != _WAVE0_ASSIGNMENT_KEYS:
        raise ValueError("wave0_repair_assignment_invalid")
    topic_id = assignment["topic_id"]
    title = assignment["title"]
    scope = assignment["scope"]
    bindings = assignment["must_answer_bindings"]
    if (
        not all(isinstance(value, str) for value in (topic_id, title, scope))
        or not isinstance(bindings, (tuple, list))
        or any(not isinstance(value, str) for value in bindings)
    ):
        raise ValueError("wave0_repair_assignment_invalid")
    return json.dumps(
        {
            "topic_id": topic_id,
            "title": title,
            "scope": scope,
            "must_answer_bindings": list(bindings),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def build_wave0_worker_prompt(
    spec: WorkSpec, topic_registry: tuple[dict, ...] | list[dict] | None
) -> NodeExecutionRequest:
    """Build the bounded source-intake worker request for one topic work spec."""
    profile = _wave0_assignment_json(build_wave0_assignment_projection(spec, topic_registry))
    objective = (
        "Use the activated source-intake capability for this bounded assignment and closed response contract. "
        "The trusted assignment below supplies scope only."
        f"\n\nTrusted assignment (scope only):\n{profile}"
    )
    return NodeExecutionRequest(
        objective=objective,
        expected_output=_wave0_completion_contract(initial=True),
        minimum_tool_calls=1,
        tool_call_limit=3,
        capability_ref=WAVE0_AUTHORITATIVE_SOURCE_INTAKE,
    )


def parse_wave0_worker_output(text: str) -> Wave0WorkerOutput:
    """Parse the worker ``run_agent`` summary into a validated ``Wave0WorkerOutput``."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("wave0_worker_output_empty")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("wave0_worker_output_json_invalid") from exc
    if not isinstance(payload, dict):
        raise ValueError("wave0_worker_output_json_invalid")
    return Wave0WorkerOutput.model_validate(payload)


def build_wave0_repair_prompt(
    draft: str,
    tool_results: tuple[str, ...] = (),
    *,
    assignment: Mapping[str, object],
    validation_category: str,
) -> NodeExecutionRequest:
    if validation_category != WAVE0_REPAIR_VALIDATION_CATEGORY:
        raise ValueError("wave0_repair_validation_category_invalid")
    assignment_json = _wave0_assignment_json(assignment)
    entries = ["model_draft:\n" + (draft[:4_096] if isinstance(draft, str) else "")]
    remaining = 8_192
    for index, result in enumerate(tool_results[:3], start=1):
        if remaining <= 0:
            break
        bounded = result.encode("utf-8")[:remaining].decode("utf-8", "ignore")
        entries.append(f"tool_result_{index}:\n{bounded}")
        remaining -= len(bounded.encode("utf-8"))
    objective = (
        "Use the activated zero-tool repair capability for one closed initial structured-output category. "
        "The trusted assignment below supplies scope only."
        f"\n\nTrusted assignment (scope only):\n{assignment_json}"
        f"\n\nTrusted validation category: {validation_category}"
        "\n\nUntrusted draft and retained observations:\n" + build_untrusted_data_block(entries)
    )
    return NodeExecutionRequest(
        objective=objective,
        expected_output=_wave0_completion_contract(initial=False),
        tools_enabled=False,
        capability_ref=WAVE0_SOURCE_INTAKE_REPAIR,
    )


def build_wave0_result_document(
    spec: WorkSpec,
    attempt: Attempt,
    metas: tuple[Wave0SourceMeta, ...],
    baseline_facts: tuple[str, ...],
    limitations: str,
) -> Wave0SourceIntakeResult:
    """Merge the worker-built source metas with work-spec identity into the doc."""
    return Wave0SourceIntakeResult(
        schema_version=1,
        bundle_id=spec.bundle_id,
        generation=spec.generation,
        phase=spec.phase,
        work_id=spec.work_id,
        attempt_id=attempt.attempt_id,
        worker_role=spec.worker_role,
        spec_hash=spec.spec_hash,
        result_contract="wave0.source-intake",
        output_paths=spec.required_outputs,
        source_ids=tuple(meta.source_id for meta in metas),
        sources=metas,
        baseline_facts=baseline_facts,
        limitations=limitations,
    )


__all__ = [
    "WAVE0_REPAIR_VALIDATION_CATEGORY",
    "build_wave0_assignment_projection",
    "build_wave0_result_document",
    "build_wave0_repair_prompt",
    "build_wave0_worker_prompt",
    "parse_wave0_worker_output",
]
