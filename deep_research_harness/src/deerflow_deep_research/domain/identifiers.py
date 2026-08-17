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
from enum import StrEnum


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

BUNDLE_ID_PATTERN = r"^b_[A-Za-z0-9_-]{43}$"
BUNDLE_ID_RE = re.compile(BUNDLE_ID_PATTERN)
CONTENT_HASH_RE = re.compile(r"^h_[A-Za-z0-9_-]{43}$")
SANDBOX_PATH_RE = re.compile(r"^workspace/deep-research/scopes/s_[A-Za-z0-9_-]{43}/b_[A-Za-z0-9_-]{43}/.+$")

__all__ = [
    "BUNDLE_ID_PATTERN",
    "BUNDLE_ID_RE",
    "CONTENT_HASH_RE",
    "LOGICAL_PHASE_NAMES",
    "LogicalPhase",
    "SANDBOX_PATH_RE",
]
