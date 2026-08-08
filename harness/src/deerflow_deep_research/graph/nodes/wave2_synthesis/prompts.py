"""Wave2 synthesis agent prompt and output parser.

@impl WSN-001
@impl WSN-005
@impl WSN-008
"""

from __future__ import annotations

import json
from collections.abc import Iterable

from deerflow_deep_research.domain.context import NodeExecutionRequest
from deerflow_deep_research.domain.synthesis import SynthesisEvidence, SynthesisResult
from deerflow_deep_research.domain.untrusted import build_untrusted_data_block

from .capabilities import WAVE2_EVIDENCE_SYNTHESIS, WAVE2_EVIDENCE_SYNTHESIS_REPAIR


def _expected_synthesis_output() -> str:
    return json.dumps(
        {
            "instruction": "Return exactly one JSON object and no markdown, prose, or code fences.",
            "schema_version": 1,
            "required_keys": ["schema_version", "findings", "relations", "gaps", "summary"],
            "finding_required_keys": [
                "finding_id",
                "statement",
                "priority",
                "affected_topics",
                "backing_refs",
                "confidence",
                "search_required",
            ],
            "confidence_values": ["high", "medium", "low", "tentative"],
            "relation_required_keys": [
                "relation_id",
                "source_finding",
                "target_finding",
                "relation_type",
            ],
            "relation_type_values": ["supports", "contradicts", "extends", "qualifies"],
            "gap_required_keys": [
                "gap_id",
                "description",
                "priority",
                "affected_topics",
                "search_required",
            ],
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def build_synthesis_prompt(
    topic_registry: Iterable[dict] | None = None,
    wave0_refs: Iterable[str] = (),
    wave1_refs: Iterable[str] = (),
    evidence: Iterable[SynthesisEvidence] = (),
) -> NodeExecutionRequest:
    """Build a bounded synthesis request from accumulated evidence."""
    topics = list(topic_registry or [])
    topic_names = [t.get("title", t.get("topic_id", "")) for t in topics if isinstance(t, dict)]
    evidence_payload = [item.model_dump(mode="json") for item in evidence]
    assignment = json.dumps(
        {
            "accepted_submission_refs": {
                "wave0": sorted(wave0_refs),
                "wave1": sorted(wave1_refs),
            },
            "topics": topic_names[:10],
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    objective = (
        "Use the activated accepted-evidence synthesis capability for this bounded assignment and closed output "
        "contract. The trusted assignment below identifies only graph-assigned topics and accepted submission "
        "references.\n\nTrusted assignment:\n"
        + assignment
        + "\n\nUntrusted accepted evidence:\n"
        + build_untrusted_data_block(
            [json.dumps(evidence_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))]
        )
    )
    return NodeExecutionRequest(
        objective=objective,
        expected_output=_expected_synthesis_output(),
        tools_enabled=False,
        capability_binding="required",
        capability_ref=WAVE2_EVIDENCE_SYNTHESIS,
    )


def parse_synthesis_output(text: str) -> SynthesisResult:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("synthesis_output_empty")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("synthesis_output_json_invalid") from exc
    if not isinstance(payload, dict):
        raise ValueError("synthesis_output_not_object")
    return SynthesisResult.model_validate(payload)


def build_synthesis_repair_prompt(
    draft: str,
    evidence: Iterable[SynthesisEvidence] = (),
    *,
    validation_category: str,
) -> NodeExecutionRequest:
    evidence_payload = [item.model_dump(mode="json") for item in evidence]
    objective = (
        "Use the activated zero-tool structured repair capability for one bounded assignment and closed output "
        "contract. The trusted validation category below is a parser or semantic category only.\n\n"
        f"Trusted validation category: {validation_category}\n\n"
        "Untrusted draft and accepted evidence:\n"
        + build_untrusted_data_block(
            [
                "model_draft:\n" + (draft[:8_192] if isinstance(draft, str) else ""),
                "accepted_evidence:\n"
                + json.dumps(evidence_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
            ]
        )
    )
    return NodeExecutionRequest(
        objective=objective,
        expected_output=_expected_synthesis_output(),
        tools_enabled=False,
        capability_binding="required",
        capability_ref=WAVE2_EVIDENCE_SYNTHESIS_REPAIR,
    )
