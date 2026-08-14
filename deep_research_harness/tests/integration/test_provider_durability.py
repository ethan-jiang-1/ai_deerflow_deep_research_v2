"""Generic infrastructure-probe provider durability contracts.

File-backed providers remain restart-durable for ``infra_probe``.  They are
not Deep Research lifecycle storage and cannot reopen a Run Bundle.

@impl RUI-005
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from deerflow_deep_research.domain.lifecycle import ImplementationMode
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.checkpoint import resolve_effective_provider
from deerflow_deep_research.runtime.probe import build_probe_graph_host
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _sqlite_config(db_path: str) -> object:
    return SimpleNamespace(
        checkpointer=None,
        database=SimpleNamespace(backend="sqlite", checkpointer_sqlite_path=db_path, postgres_url=None),
    )


def _memory_config() -> object:
    return SimpleNamespace(checkpointer=None, database=SimpleNamespace(backend="memory"))


def _envelope(tmp_path: Path, app_config: object) -> TrustedRuntimeEnvelope:
    workspace = tmp_path / "workspace"
    uploads = tmp_path / "uploads"
    outputs = tmp_path / "outputs"
    for directory in (workspace, uploads, outputs):
        directory.mkdir(parents=True, exist_ok=True)
    return TrustedRuntimeEnvelope(
        effective_user_id="alice",
        outer_thread_id="thread-1",
        outer_run_id="run-1",
        app_config=app_config,
        workspace_host_path=workspace,
        uploads_host_path=uploads,
        outputs_host_path=outputs,
        workspace_virtual_root="/mnt/user-data/workspace",
        uploads_virtual_root="/mnt/user-data/uploads",
        outputs_virtual_root="/mnt/user-data/outputs",
        parent_sandbox=object(),
        progress=None,
    )


def test_memory_is_same_process() -> None:
    selection = resolve_effective_provider(_memory_config())
    assert selection.kind == "memory"
    assert selection.durability == "same_process"


def test_file_sqlite_is_restart_durable() -> None:
    selection = resolve_effective_provider(_sqlite_config("/tmp/store.db"))
    assert selection.kind == "sqlite"
    assert selection.durability == "restart_durable"


def test_in_memory_sqlite_is_not_restart_durable() -> None:
    selection = resolve_effective_provider(_sqlite_config(":memory:"))
    assert selection.kind == "sqlite"
    assert selection.durability == "same_process"


async def test_file_sqlite_recovers_generic_probe_across_provider_contexts(tmp_path: Path) -> None:
    config = _sqlite_config(str(tmp_path / "store.db"))
    host = build_probe_graph_host(fingerprint_verifier=lambda _app_config: None)
    envelope = _envelope(tmp_path, config)

    first = await host.run_action(action="infra_probe", envelope=envelope, action_input="p1")
    second = await host.run_action(action="infra_probe", envelope=envelope, action_input="p1")

    assert first["previous_visit"] is None
    assert first["current_visit"] == 1
    assert first["durability"] == "restart_durable"
    assert second["previous_visit"] == 1
    assert second["current_visit"] == 2


async def test_file_sqlite_probe_visits_are_isolated_from_bundle_lifecycle(tmp_path: Path) -> None:
    config = _sqlite_config(str(tmp_path / "isolated.db"))
    host = build_probe_graph_host(fingerprint_verifier=lambda _app_config: None)
    envelope = _envelope(tmp_path, config)

    before = await host.run_action(action="infra_probe", envelope=envelope, action_input="p1")
    lifecycle = BundleLifecycle(workspace_host_path=envelope.workspace_host_path)
    bundle = await lifecycle.start(
        scope=("alice", "thread-1"),
        request_text="research question",
        implementation_mode=ImplementationMode.ALL_REAL,
    )
    after = await host.run_action(action="infra_probe", envelope=envelope, action_input="p1")

    assert (await lifecycle.status(scope=("alice", "thread-1"), bundle_id=bundle.bundle_id)).code == "active"
    assert before["previous_visit"] is None and before["current_visit"] == 1
    assert after["previous_visit"] == 1 and after["current_visit"] == 2


def _run_probe_subprocess(db: str, probe_id: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, str(_FIXTURES / "sqlite_probe_subprocess.py"), db, probe_id],
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    return json.loads(completed.stdout.strip())


def test_file_sqlite_probe_survives_a_real_subprocess_restart(tmp_path: Path) -> None:
    db = str(tmp_path / "store.db")
    first = _run_probe_subprocess(db, "p1")
    second = _run_probe_subprocess(db, "p1")

    assert first["previous_visit"] is None
    assert first["current_visit"] == 1
    assert first["durability"] == "restart_durable"
    assert second["previous_visit"] == 1
    assert second["current_visit"] == 2


def test_probe_subprocess_scopes_are_isolated(tmp_path: Path) -> None:
    db = str(tmp_path / "store.db")
    _run_probe_subprocess(db, "p1")
    other = _run_probe_subprocess(db, "p2")

    assert other["previous_visit"] is None
    assert other["current_visit"] == 1
