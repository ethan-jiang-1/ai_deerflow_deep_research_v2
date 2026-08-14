"""Bounded layout request, admission, and deterministic final rendering."""

from __future__ import annotations

import json
from collections.abc import Iterable

from deerflow_deep_research.domain.context import NodeExecutionRequest
from deerflow_deep_research.domain.publication import FinalDeliveryLayoutCandidate
from deerflow_deep_research.domain.readiness import ReadinessReportPlan
from deerflow_deep_research.domain.synthesis import SynthesisEvidence
from deerflow_deep_research.domain.untrusted import build_untrusted_data_block

from .capabilities import FINAL_DELIVERY_COMPOSER

MAX_FINAL_DELIVERY_EVIDENCE_BYTES = 8_192


def _entry_ids(prefix: str, count: int) -> tuple[str, ...]:
    return tuple(f"{prefix}:{index}" for index in range(count))


def _bounded_evidence(evidence: Iterable[SynthesisEvidence]) -> tuple[dict[str, object], ...]:
    items = tuple(evidence)
    if not items:
        return ()
    remaining = MAX_FINAL_DELIVERY_EVIDENCE_BYTES
    projection: list[dict[str, object]] = []
    for index, item in enumerate(items):
        item_limit = max(0, remaining // (len(items) - index))
        content = item.content.encode("utf-8")[:item_limit].decode("utf-8", "ignore")
        projection.append(
            {
                "submission_ref": item.submission_ref,
                "phase": item.phase,
                "result_contract": item.result_contract,
                "content": content,
                "truncated": item.truncated or len(content.encode("utf-8")) < len(item.content.encode("utf-8")),
            }
        )
        remaining -= len(content.encode("utf-8"))
    return tuple(projection)


def build_final_delivery_request(
    plan: ReadinessReportPlan,
    evidence: tuple[SynthesisEvidence, ...],
) -> NodeExecutionRequest:
    conclusion_ids = _entry_ids("conclusion", len(plan.writable_conclusions))
    uncertainty_ids = _entry_ids("uncertainty", len(plan.mandatory_uncertainties))
    plan_projection = {
        "conclusions": [
            {
                "id": entry_id,
                "question": conclusion.question,
                "conclusion_text": conclusion.conclusion_text,
                "backing_submission_refs": list(conclusion.backing_claim_ids),
            }
            for entry_id, conclusion in zip(conclusion_ids, plan.writable_conclusions, strict=True)
        ],
        "uncertainties": [
            {"id": entry_id, "question": uncertainty.question, "limitation": uncertainty.limitation}
            for entry_id, uncertainty in zip(uncertainty_ids, plan.mandatory_uncertainties, strict=True)
        ],
    }
    objective = (
        "Return a layout for every approved report entry. You may only order the supplied IDs; "
        "do not add prose, claims, citations, routes, or authority fields.\n\nTrusted entry IDs:\n"
        + json.dumps(plan_projection, ensure_ascii=False, separators=(",", ":"))
        + "\n\nAccepted evidence metadata:\n"
        + build_untrusted_data_block(
            [json.dumps(_bounded_evidence(evidence), ensure_ascii=False, sort_keys=True, separators=(",", ":"))]
        )
    )
    expected = json.dumps(
        {
            "instruction": "Return exactly one JSON object and no markdown, prose, or code fences.",
            "schema_version": 1,
            "required_keys": ["schema_version", "conclusion_order", "uncertainty_order"],
            "conclusion_order": list(conclusion_ids),
            "uncertainty_order": list(uncertainty_ids),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return NodeExecutionRequest(
        objective=objective,
        expected_output=expected,
        tools_enabled=False,
        capability_ref=FINAL_DELIVERY_COMPOSER,
    )


def parse_layout_candidate(text: str) -> FinalDeliveryLayoutCandidate:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("final_layout_empty")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("final_layout_json_invalid") from exc
    if not isinstance(payload, dict):
        raise ValueError("final_layout_not_object")
    return FinalDeliveryLayoutCandidate.model_validate(payload)


def admit_layout_candidate(
    candidate: FinalDeliveryLayoutCandidate,
    plan: ReadinessReportPlan,
) -> FinalDeliveryLayoutCandidate:
    if candidate.schema_version != 1:
        raise ValueError("final_layout_schema_unsupported")
    if set(candidate.conclusion_order) != set(_entry_ids("conclusion", len(plan.writable_conclusions))):
        raise ValueError("final_layout_conclusions_invalid")
    if set(candidate.uncertainty_order) != set(_entry_ids("uncertainty", len(plan.mandatory_uncertainties))):
        raise ValueError("final_layout_uncertainties_invalid")
    return candidate


def render_final_artifacts(plan: ReadinessReportPlan, layout: FinalDeliveryLayoutCandidate) -> tuple[bytes, bytes]:
    lines = ["# Deep Research Report", "", "## Findings", ""]
    claims: dict[str, dict[str, list[str]]] = {}
    for entry_id in layout.conclusion_order:
        conclusion = plan.writable_conclusions[int(entry_id.split(":", 1)[1])]
        lines.extend((f"### {conclusion.question}", "", conclusion.conclusion_text, ""))
        claims[entry_id] = {"backing_refs": list(conclusion.backing_claim_ids)}
    lines.extend(("## Uncertainties", ""))
    for entry_id in layout.uncertainty_order:
        uncertainty = plan.mandatory_uncertainties[int(entry_id.split(":", 1)[1])]
        lines.extend((f"### {uncertainty.question}", "", uncertainty.limitation, ""))
    report = "\n".join(lines).encode("utf-8")
    citation_map = json.dumps({"schema_version": 1, "claims": claims}, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return report, citation_map


__all__ = [
    "MAX_FINAL_DELIVERY_EVIDENCE_BYTES",
    "admit_layout_candidate",
    "build_final_delivery_request",
    "parse_layout_candidate",
    "render_final_artifacts",
]
