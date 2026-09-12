"""Canonical identifier constants for the Deep Research runtime.

This module is the single source of truth for the runtime identifier shapes
(bundle ids, content hashes, sandbox-path references) and the logical phase
name list. Every other module imports from here instead of redefining the
same regex or phase list.

@impl WOU-001
@impl WOU-002
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from enum import StrEnum
from types import MappingProxyType


class LogicalPhase(StrEnum):
    BOOTSTRAP = "bootstrap"
    HITL1 = "hitl1"
    TOPIC_PLANNING = "topic_planning"
    WAVE0 = "wave0"
    WAVE1 = "wave1"
    WAVE2_SYNTHESIS = "wave2_synthesis"
    TARGETED_EVIDENCE = "targeted_evidence"
    HITL2 = "hitl2"
    RERUN = "rerun"
    READINESS = "readiness"
    FINAL_DELIVERY = "final_delivery"


# The one authoritative phase-name list, derived from the enum so the enum
# remains the single authority for both the names and their order.
LOGICAL_PHASE_NAMES = tuple(member.value for member in LogicalPhase)

# The one authoritative one-line human summary per logical node. Node package
# workflow.md H1 titles are projections of these summaries; tests pin the
# projection. This mapping is a generated-doc input only — never runtime
# authority for graph composition, lifecycle, or admission.
_LOGICAL_NODE_SUMMARY_TEXT: Mapping[LogicalPhase, str] = {
    LogicalPhase.BOOTSTRAP: "Bind trusted bootstrap input to the research lifecycle",
    LogicalPhase.HITL1: "Turn a human request into an approved research profile",
    LogicalPhase.TOPIC_PLANNING: "Decompose a confirmed profile into a research-plan candidate",
    LogicalPhase.WAVE0: "Acquire authoritative-source evidence for assigned work",
    LogicalPhase.WAVE1: "Extract source-grounded evidence and bounded repair candidates",
    LogicalPhase.WAVE2_SYNTHESIS: "Synthesize accepted evidence into findings and research gaps",
    LogicalPhase.TARGETED_EVIDENCE: "Resolve a gate-projected evidence gap",
    LogicalPhase.HITL2: "Resolve a conditional research decision before delivery",
    LogicalPhase.RERUN: "Apply a validated rerun scope to research control",
    LogicalPhase.READINESS: "Judge per-question evidence sufficiency and answerability",
    LogicalPhase.FINAL_DELIVERY: "Compose and communicate a report from accepted research state",
}

if set(_LOGICAL_NODE_SUMMARY_TEXT) != set(LogicalPhase) or any(
    not summary.strip() for summary in _LOGICAL_NODE_SUMMARY_TEXT.values()
):
    raise ValueError("logical_node_summaries_incomplete")

LOGICAL_NODE_SUMMARIES: Mapping[LogicalPhase, str] = MappingProxyType(_LOGICAL_NODE_SUMMARY_TEXT)

BUNDLE_ID_PATTERN = r"^b_[A-Za-z0-9_-]{43}$"
BUNDLE_ID_RE = re.compile(BUNDLE_ID_PATTERN)
CONTENT_HASH_RE = re.compile(r"^h_[A-Za-z0-9_-]{43}$")
SANDBOX_PATH_RE = re.compile(r"^workspace/deep-research/scopes/s_[A-Za-z0-9_-]{43}/b_[A-Za-z0-9_-]{43}/.+$")

__all__ = [
    "BUNDLE_ID_PATTERN",
    "BUNDLE_ID_RE",
    "CONTENT_HASH_RE",
    "LOGICAL_NODE_SUMMARIES",
    "LOGICAL_PHASE_NAMES",
    "LogicalPhase",
    "SANDBOX_PATH_RE",
]
