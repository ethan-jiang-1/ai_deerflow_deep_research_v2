"""Cutover guards for graph checkpoints that retained ``repair_counts``.

@impl GAK-004
@impl REG-011
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, fields
from pathlib import Path

import pytest
from langgraph.checkpoint.base import empty_checkpoint
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from deerflow_deep_research.domain.bundle import RunBundleRef
from deerflow_deep_research.domain.failure_codes import FailureCode
from deerflow_deep_research.domain.gate import Failure, GateDefinition, GateRule, PhaseVerdict
from deerflow_deep_research.domain.state import (
    OWNERSHIP_TABLE,
    ResearchGraphState,
    ResearchState,
    validate_research_state,
)
from deerflow_deep_research.engine.gate_kernel import evaluate_gate
from deerflow_deep_research.runtime.bundle_graph import BundleGraphExecutor
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle, BundleLifecycleError
from scripts import retained_run_data_migration as retained_data

FIXTURE = Path(__file__).parents[1] / "fixtures" / "retained_run_data" / "graph_checkpoint_v2_repair_counts.json"
_SCOPE = ("checkpoint-user", "checkpoint-thread")


def _legacy_checkpoint() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


async def _write_legacy_checkpoint(database: Path, bundle: RunBundleRef) -> None:
    database.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = empty_checkpoint()
    checkpoint["channel_values"] = _legacy_checkpoint()
    checkpoint["channel_versions"] = {"repair_counts": "1", "schema_version": "1"}
    config = {"configurable": {"thread_id": bundle.bundle_id.value, "checkpoint_ns": ""}}
    async with AsyncSqliteSaver.from_conn_string(str(database)) as saver:
        await saver.aput(config, checkpoint, {}, checkpoint["channel_versions"])


@dataclass
class _NeverCompileBuilder:
    calls: int = 0

    def compile(self, **_kwargs: object) -> object:
        self.calls += 1
        raise AssertionError("legacy checkpoint reached graph compilation")


@dataclass(frozen=True)
class _NeverCompileRecipe:
    builder: _NeverCompileBuilder


@pytest.mark.asyncio
async def test_unregistered_repair_counts_checkpoint_rejects_before_graph_compile_or_execution(tmp_path: Path) -> None:
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(
        scope=_SCOPE,
        request_text="Cut over a retained checkpoint.",
        implementation_mode="fixture",
    )
    await _write_legacy_checkpoint(lifecycle.private_root(bundle) / "graph.sqlite", bundle)
    state_path = lifecycle.private_root(bundle) / "state.json"
    graph_path = lifecycle.private_root(bundle) / "graph.sqlite"
    before = (state_path.read_bytes(), graph_path.read_bytes())
    builder = _NeverCompileBuilder()
    executor = BundleGraphExecutor(recipe=_NeverCompileRecipe(builder))  # type: ignore[arg-type]

    with pytest.raises(BundleLifecycleError, match="bundle_graph_legacy"):
        await executor.start(
            lifecycle=lifecycle,
            bundle=bundle,
            envelope=object(),
            start_message=object(),  # type: ignore[arg-type]
            tool_call_id="legacy-checkpoint",
        )

    assert builder.calls == 0
    assert (state_path.read_bytes(), graph_path.read_bytes()) == before


def test_registered_checkpoint_migration_writes_reloads_and_replays_current_gate_facts(tmp_path: Path) -> None:
    source_payload = FIXTURE.read_bytes()
    source = retained_data.MigrationSource(
        family="graph_checkpoint",
        schema=2,
        identity="checkpoint-fixture",
        payload=source_payload,
    )
    decoder = getattr(retained_data, "decode_graph_checkpoint", None)
    assert callable(decoder), "offline graph checkpoint decoder is required"
    output_payload = decoder(source)
    record = retained_data.InventoryRecord(
        family=source.family,
        source_schema=source.schema,
        identity=source.identity,
        source_digest=f"sha256:{hashlib.sha256(source.payload).hexdigest()}",
        disposition="migrate",
        output_digest=f"sha256:{hashlib.sha256(output_payload).hexdigest()}",
    )
    inventory = retained_data.RetainedDataInventory(version=1, records=(record,))

    report = retained_data.run_inventory(
        inventory,
        sources=(source,),
        output_directory=tmp_path / "output",
        decode=decoder,
    )
    reloaded = json.loads((tmp_path / "output" / "graph_checkpoint" / "checkpoint-fixture.json").read_text())
    checkpoint = validate_research_state(reloaded)
    replay_gate = GateDefinition(
        phase="wave0",
        rules=(
            GateRule(
                "repairable",
                lambda _state: Failure(FailureCode.WORK_FAILED, "repairable"),
                FailureCode.WORK_FAILED,
            ),
        ),
        route_map={PhaseVerdict.PASS: "pass", PhaseVerdict.REPAIR: "repair", PhaseVerdict.BLOCKED: "exhausted"},
    )
    replay = evaluate_gate(reloaded, "wave0", replay_gate)

    assert report.migrated == 1
    assert reloaded["schema_version"] == 3
    assert "repair_counts" not in reloaded
    assert checkpoint.gate_attempts_by_phase == {"wave0": 2}
    assert checkpoint.repair_budget_by_phase == {"wave0": 1}
    assert replay.attempt == 3
    assert replay.remaining_budget == 0
    assert replay.verdict is PhaseVerdict.REPAIR
    assert replay.route == "repair"


def test_current_graph_state_has_no_repair_counts_alias() -> None:
    """GAK-004: gate facts are the sole repair state after checkpoint cutover."""
    assert "repair_counts" not in ResearchState.__annotations__
    assert "repair_counts" not in {field.name for field in fields(ResearchGraphState)}
    assert "repair_counts" not in {entry.field for entry in OWNERSHIP_TABLE}
