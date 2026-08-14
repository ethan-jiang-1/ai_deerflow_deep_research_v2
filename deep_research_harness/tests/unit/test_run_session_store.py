"""Regression proof that the retired session store cannot be imported.

@impl DRH-006
@impl PRS-006
@impl RUI-003
"""

from __future__ import annotations

import importlib.util

import pytest

_RETIRED_RUN_SESSION_MODULES = (
    "deerflow_deep_research.domain.run_session",
    "deerflow_deep_research.runtime.run_session",
)


def _assert_retired_run_session_modules_absent(find_spec: object) -> None:
    assert callable(find_spec)
    for module_name in _RETIRED_RUN_SESSION_MODULES:
        assert find_spec(module_name) is None


def test_retired_run_session_store_has_no_compatibility_module() -> None:
    _assert_retired_run_session_modules_absent(importlib.util.find_spec)


def test_retired_run_session_guard_rejects_a_planted_import() -> None:
    with pytest.raises(AssertionError):
        _assert_retired_run_session_modules_absent(
            lambda module_name: object() if module_name == _RETIRED_RUN_SESSION_MODULES[0] else None
        )
