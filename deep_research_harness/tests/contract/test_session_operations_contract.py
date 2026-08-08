"""Contract evidence for direct trusted-scope Run Bundle operations.

@impl RDO-001
@impl RDO-002
@impl RDO-003
@impl RDO-004
@impl RDO-007
"""

from __future__ import annotations

import importlib.util
import inspect

from deerflow_deep_research.domain.lifecycle import BundleControlResult
from deerflow_deep_research.runtime.session_workbench import BundleWorkbench


def test_local_operations_have_no_session_or_broker_contract() -> None:
    """The direct workbench is the only local operation entry point."""

    assert importlib.util.find_spec("deerflow_deep_research.domain.session_operations") is None
    assert importlib.util.find_spec("deerflow_deep_research.runtime.session_operations") is None

    parameters = inspect.signature(BundleWorkbench).parameters
    assert tuple(parameters) == ("lifecycle", "scope", "current_bundle_handle")


def test_shared_lifecycle_result_has_no_legacy_authority_fields() -> None:
    assert "bundle_id" in BundleControlResult.model_fields
    for retired in ("research_id", "session_ref", "checkpoint", "provider", "bundle_directory"):
        assert retired not in BundleControlResult.model_fields
