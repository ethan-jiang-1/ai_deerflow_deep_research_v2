"""Regression proof that the retired session store cannot be imported.

@impl RUS-001
@impl RUS-007
"""

from __future__ import annotations

import importlib.util


def test_retired_run_session_store_has_no_compatibility_module() -> None:
    assert importlib.util.find_spec("deerflow_deep_research.domain.run_session") is None
    assert importlib.util.find_spec("deerflow_deep_research.runtime.run_session") is None
