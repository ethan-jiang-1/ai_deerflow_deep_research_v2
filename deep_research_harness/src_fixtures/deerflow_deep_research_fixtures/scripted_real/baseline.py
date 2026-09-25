"""Fixed narrow baseline scripts for the scripted-real workflow debug command.

Pure data only: this module imports no production or fixture runtime authority,
so the fixture production-contract allowlist stays untouched. The operator
launcher (`scripts/debug_scripted_real_workflow.py`) owns the composition that
feeds these scripts into the all-real production control path.

Placeholders rendered against the trusted prompt assignment at call time:

- ``{{first_submission_ref}}``: first ``"submission_ref":"…"`` token
- ``{{wave0_first_ref}}``: first ref inside the prompt's ``"wave0":[…]`` array
- ``{{conclusion_ids}}`` / ``{{uncertainty_ids}}``: JSON arrays of the plan entry
  ids supplied in the composer prompt
"""

from __future__ import annotations

# Fixed research question and HITL1 auto-confirmation text.
BASELINE_QUESTION = "What is one bounded fact about grid energy storage?"
BASELINE_CONFIRMATION = "确认"

# Scripted model responses with fixed usage accounting (BudgetMiddleware
# requires total/output token metadata on every response).
MODEL_INPUT_TOKENS = 10
MODEL_OUTPUT_TOKENS = 5
MODEL_TOTAL_TOKENS = MODEL_INPUT_TOKENS + MODEL_OUTPUT_TOKENS

# Tool-call template marker: "TOOL_CALL:<name>" emits one scripted tool call.
MODEL_SCRIPT: tuple[str, ...] = (
    # hitl1 structured brief (one zero-tool call).
    '{"schema_version": 2, "brief_summary": "One bounded primary-source fact on grid energy storage economics.", '
    '"depth": "quick_overview", "audience": "domain_expert", "format": "annotated_bibliography", '
    '"cost_tolerance": "minimal", "time_budget": "very_quick", '
    '"must_answer": ["What evidence supports the answer?"], '
    '"scope_boundaries": "One narrow public-source topic.", "custom_notes": "Scripted-real workflow baseline.", '
    '"comparison_required": false, "comparison_subjects": null, "request_language": "en", "output_language": "en"}',
    # topic planning (one topic covering the must-answer question).
    '{"schema_version": 1, "topics": [{"title": "Primary evidence", '
    '"scope": "One authoritative source answering the scripted question", '
    '"must_answer_bindings": ["What evidence supports the answer?"], '
    '"search_dimensions": ["official source"], "exclusions": []}]}',
    # wave0 worker: one retrieval, then the intake candidate.
    "TOOL_CALL:web_search",
    '{"schema_version": 1, "sources": [{"source_id": "source:canary", '
    '"canonical_url": "https://example.invalid/canary", "title": "Canary primary source", '
    '"fetch_status": "fetched"}], "baseline_facts": [], "limitations": ""}',
    # wave1 worker: one retrieval, then extraction with >=2 new sources beyond baseline.
    "TOOL_CALL:web_search",
    '{"schema_version": 1, "sources": ['
    '{"source_id": "source:w1-extra-a", "canonical_url": "https://example.invalid/extra-a", '
    '"title": "Extra canary source A"}, '
    '{"source_id": "source:w1-extra-b", "canonical_url": "https://example.invalid/extra-b", '
    '"title": "Extra canary source B"}], '
    '"source_ids": ["source:w1-extra-a", "source:w1-extra-b"], '
    '"claims": [{"claim_id": "storage-economics", "statement": "Storage duration changes project economics.", '
    '"support_refs": ["source:w1-extra-a"], "counter_refs": ["source:w1-extra-b"]}], "open_questions": []}',
    # wave1 source-diagnostic critic (closed enums per the production contract).
    '{"schema_version": 1, "source_ids": ["source:w1-extra-a", "source:w1-extra-b"], "sources": ['
    '{"source_id": "source:w1-extra-a", "trust_tier": "medium", "materiality": "primary", '
    '"marketing_risk": false, "cross_verification_need": true}, '
    '{"source_id": "source:w1-extra-b", "trust_tier": "low", "materiality": "secondary", '
    '"marketing_risk": false, "cross_verification_need": true}]}',
    # wave1 claim-verifier critic aligned with the extraction's claim ids.
    '{"schema_version": 1, "claims": [{"claim_id": "claim:w1_storage-economics", "verdict": "supported", '
    '"support_refs": ["source:w1-extra-a"], "counter_refs": ["source:w1-extra-b"], '
    '"reason": "One bounded authoritative source supports the claim."}]}',
    # wave2 synthesis: one finding backed by an accepted submission ref, no searchable gaps.
    '{"schema_version": 1, "findings": [{"finding_id": "finding:storage-economics", '
    '"statement": "Storage duration changes project economics.", "priority": 1, '
    '"affected_topics": ["primary-evidence"], "backing_refs": ["{{wave0_first_ref}}"], '
    '"confidence": "high", "search_required": false}], "relations": [], "gaps": [], '
    '"summary": "One backed finding from accepted evidence."}',
    # readiness critic: every assigned question ready with accepted submission refs.
    '{"schema_version": 1, "per_question": [{"question": "What evidence supports the answer?", '
    '"verdict": "ready_substantive", "backing_claim_ids": ["{{first_submission_ref}}"], "limitation_note": ""}], '
    '"overall_limitations": [], "synthesis_flaws": [], "contradiction_ids": []}',
    # final-delivery composer: raw arrays containing only the plan entry ids.
    '{"schema_version": 1, "conclusion_order": {{conclusion_ids}}, "uncertainty_order": {{uncertainty_ids}}}',
)

# Scripted web tools: exactly the baseline budget; any surplus call exhausts the
# queue and fails the run loudly.
WEB_SEARCH_RESPONSES: tuple[str, ...] = (
    '{"url": "https://example.invalid/canary", "content": "Canary primary source content."}',
    '{"url": "https://example.invalid/extra-a", "content": "Extra canary source content."}',
)
WEB_FETCH_RESPONSES: tuple[str, ...] = ()

# Declared per-wave budget for the baseline run (SCR-002).
EXPECTED_MODEL_CALLS = 11
EXPECTED_WEB_SEARCH_CALLS = 2
EXPECTED_WEB_FETCH_CALLS = 0

# Repair/targeted named case (BUG-028 + BUG-029): one targeted_search Wave1 question
# survives an invalid source-diagnostic critic, re-dispatches through the wave1
# repair loop, projects the handoff, becomes one searchable synthesis gap, runs one
# targeted-evidence round, and exhausts to the bounded blocked terminal.
REPAIR_TARGETED_SCRIPT: tuple[str, ...] = (
    # hitl1 structured brief (one zero-tool call).
    '{"schema_version": 2, "brief_summary": "One bounded primary-source fact on grid energy storage economics.", '
    '"depth": "quick_overview", "audience": "domain_expert", "format": "annotated_bibliography", '
    '"cost_tolerance": "minimal", "time_budget": "very_quick", '
    '"must_answer": ["What evidence supports the answer?"], '
    '"scope_boundaries": "One narrow public-source topic.", "custom_notes": "Scripted-real repair/targeted case.", '
    '"comparison_required": false, "comparison_subjects": null, "request_language": "en", "output_language": "en"}',
    # topic planning (one topic covering the must-answer question).
    '{"schema_version": 1, "topics": [{"title": "Primary evidence", '
    '"scope": "One authoritative source answering the scripted question", '
    '"must_answer_bindings": ["What evidence supports the answer?"], '
    '"search_dimensions": ["official source"], "exclusions": []}]}',
    # wave0 worker: one retrieval, then the intake candidate.
    "TOOL_CALL:web_search",
    '{"schema_version": 1, "sources": [{"source_id": "source:canary", '
    '"canonical_url": "https://example.invalid/canary", "title": "Canary primary source", '
    '"fetch_status": "fetched"}], "baseline_facts": [], "limitations": ""}',
    # wave1 worker #1: extraction that leaves one targeted_search open question.
    "TOOL_CALL:web_search",
    '{"schema_version": 1, "sources": ['
    '{"source_id": "source:w1-extra-a", "canonical_url": "https://example.invalid/extra-a", '
    '"title": "Extra canary source A"}, '
    '{"source_id": "source:w1-extra-b", "canonical_url": "https://example.invalid/extra-b", '
    '"title": "Extra canary source B"}], '
    '"source_ids": ["source:w1-extra-a", "source:w1-extra-b"], '
    '"claims": [{"claim_id": "storage-economics", "statement": "Storage duration changes project economics.", '
    '"support_refs": ["source:w1-extra-a"], "counter_refs": ["source:w1-extra-b"]}], '
    '"open_questions": [{"question_id": "q:w1_more-evidence", '
    '"question": "Which deployment context has the lower operating cost?", "state": "targeted_search"}]}',
    # wave1 source-diagnostic critic #1: invalid contract output (BUG-029 path).
    "not-json",
    # wave1 claim-verifier critic #1: valid for worker #1's claim.
    '{"schema_version": 1, "claims": [{"claim_id": "claim:w1_storage-economics", "verdict": "supported", '
    '"support_refs": ["source:w1-extra-a"], "counter_refs": ["source:w1-extra-b"], '
    '"reason": "One bounded authoritative source supports the claim."}]}',
    # wave1 repair visit: worker #2 re-extracts the same sources with no open question.
    "TOOL_CALL:web_search",
    '{"schema_version": 1, "sources": ['
    '{"source_id": "source:w1-extra-a", "canonical_url": "https://example.invalid/extra-a", '
    '"title": "Extra canary source A"}, '
    '{"source_id": "source:w1-extra-b", "canonical_url": "https://example.invalid/extra-b", '
    '"title": "Extra canary source B"}], '
    '"source_ids": ["source:w1-extra-a", "source:w1-extra-b"], '
    '"claims": [{"claim_id": "storage-economics", "statement": "Storage duration changes project economics.", '
    '"support_refs": ["source:w1-extra-a"], "counter_refs": ["source:w1-extra-b"]}], "open_questions": []}',
    # re-dispatched critics for worker #2 (the repair visit's view covers only the new work).
    '{"schema_version": 1, "source_ids": ["source:w1-extra-a", "source:w1-extra-b"], "sources": ['
    '{"source_id": "source:w1-extra-a", "trust_tier": "medium", "materiality": "primary", '
    '"marketing_risk": false, "cross_verification_need": true}, '
    '{"source_id": "source:w1-extra-b", "trust_tier": "low", "materiality": "secondary", '
    '"marketing_risk": false, "cross_verification_need": true}]}',
    '{"schema_version": 1, "claims": [{"claim_id": "claim:w1_storage-economics", "verdict": "supported", '
    '"support_refs": ["source:w1-extra-a"], "counter_refs": ["source:w1-extra-b"], '
    '"reason": "One bounded authoritative source supports the claim."}]}',
    # wave2 synthesis #1: one searchable gap referencing the projected question.
    '{"schema_version": 1, "findings": [{"finding_id": "finding:storage-economics", '
    '"statement": "Storage duration changes project economics.", "priority": 1, '
    '"affected_topics": ["primary-evidence"], "backing_refs": ["{{wave0_first_ref}}"], '
    '"confidence": "high", "search_required": false}], "relations": [], '
    '"gaps": [{"gap_id": "gap:storage-cost", '
    '"description": "Which deployment context has the lower operating cost?", "priority": 1, '
    '"affected_topics": ["primary-evidence"], "search_required": true, '
    '"source_questions": ["q:w1_d30ccbed_more-evidence"]}], '
    '"summary": "One backed finding with one searchable gap."}',
    # targeted worker: one retrieval, then an honest unresolved same-gap intake.
    "TOOL_CALL:web_search",
    '{"schema_version": 1, "gap_id": "gap:storage-cost", "gap_status": "unresolved", '
    '"sources": [{"source_id": "source:targeted", "canonical_url": "https://example.invalid/targeted", '
    '"title": "Targeted evidence"}], "limitations": "The scripted targeted search stays unresolved."}',
    # wave2 synthesis #2: the gap remains searchable, so the wave2 gate exhausts.
    '{"schema_version": 1, "findings": [{"finding_id": "finding:storage-economics", '
    '"statement": "Storage duration changes project economics.", "priority": 1, '
    '"affected_topics": ["primary-evidence"], "backing_refs": ["{{wave0_first_ref}}"], '
    '"confidence": "high", "search_required": false}], "relations": [], '
    '"gaps": [{"gap_id": "gap:storage-cost", '
    '"description": "Which deployment context has the lower operating cost?", "priority": 1, '
    '"affected_topics": ["primary-evidence"], "search_required": true, '
    '"source_questions": ["q:w1_d30ccbed_more-evidence"]}], '
    '"summary": "The searchable gap remains after one targeted round."}',
)

REPAIR_TARGETED_SEARCH_RESPONSES: tuple[str, ...] = (
    '{"url": "https://example.invalid/canary", "content": "Canary primary source content."}',
    '{"url": "https://example.invalid/extra-a", "content": "Extra canary source content A."}',
    '{"url": "https://example.invalid/extra-b", "content": "Extra canary source content B."}',
    '{"url": "https://example.invalid/targeted", "content": "Targeted search content."}',
)
REPAIR_TARGETED_FETCH_RESPONSES: tuple[str, ...] = ()

EXPECTED_REPAIR_TARGETED_MODEL_CALLS = 16
EXPECTED_REPAIR_TARGETED_SEARCH_CALLS = 4
EXPECTED_REPAIR_TARGETED_FETCH_CALLS = 0

__all__ = [
    "BASELINE_CONFIRMATION",
    "BASELINE_QUESTION",
    "EXPECTED_MODEL_CALLS",
    "EXPECTED_REPAIR_TARGETED_FETCH_CALLS",
    "EXPECTED_REPAIR_TARGETED_MODEL_CALLS",
    "EXPECTED_REPAIR_TARGETED_SEARCH_CALLS",
    "EXPECTED_WEB_FETCH_CALLS",
    "EXPECTED_WEB_SEARCH_CALLS",
    "MODEL_INPUT_TOKENS",
    "MODEL_OUTPUT_TOKENS",
    "MODEL_SCRIPT",
    "MODEL_TOTAL_TOKENS",
    "REPAIR_TARGETED_FETCH_RESPONSES",
    "REPAIR_TARGETED_SCRIPT",
    "REPAIR_TARGETED_SEARCH_RESPONSES",
    "WEB_FETCH_RESPONSES",
    "WEB_SEARCH_RESPONSES",
]
