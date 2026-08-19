"""Public non-interactive lifecycle policy contracts.

The policy is evaluated at the reflected tool boundary.  It does not create a
second action-input or checkpoint authority beneath a Run Bundle.

@impl RUO-001
@impl RUO-002
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from langchain_core.messages import AIMessage, HumanMessage

from deerflow_deep_research.runtime.bundle_graph import BundleGraphExecutor
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope
from deerflow_deep_research.tool import run_deep_research


class _FakeAppConfig:
    checkpointer = None
    database = None


class _Adapter:
    def __init__(self, envelope: TrustedRuntimeEnvelope) -> None:
        self.envelope = envelope
        self.initialize_parent_sandbox_values: list[bool] = []

    async def adapt(self, _runtime, *, initialize_parent_sandbox: bool = True) -> TrustedRuntimeEnvelope:
        self.initialize_parent_sandbox_values.append(initialize_parent_sandbox)
        return self.envelope


def _envelope(tmp_path: Path) -> TrustedRuntimeEnvelope:
    workspace = tmp_path / "workspace"
    uploads = tmp_path / "uploads"
    outputs = tmp_path / "outputs"
    for directory in (workspace, uploads, outputs):
        directory.mkdir(parents=True, exist_ok=True)
    return TrustedRuntimeEnvelope(
        effective_user_id="alice",
        outer_thread_id="thread-1",
        outer_run_id="run-1",
        app_config=_FakeAppConfig(),
        workspace_host_path=workspace,
        uploads_host_path=uploads,
        outputs_host_path=outputs,
        workspace_virtual_root="/mnt/user-data/workspace",
        uploads_virtual_root="/mnt/user-data/uploads",
        outputs_virtual_root="/mnt/user-data/outputs",
        parent_sandbox=object(),
    )


def _runtime(*, context: dict[str, object], action: str = "start") -> SimpleNamespace:
    call_id = f"{action}-call"
    user = HumanMessage(content="Research storage", id="human-start")
    control = AIMessage(
        content="",
        tool_calls=[{"name": "deep_research", "args": {"action": action}, "id": call_id}],
    )
    return SimpleNamespace(state={"messages": [user, control]}, context=context, tool_call_id=call_id)


async def test_tool_allows_declared_non_interactive_policy_for_start(tmp_path: Path) -> None:
    """@impl RUI-009"""
    adapter = _Adapter(_envelope(tmp_path))
    result = await run_deep_research(
        action="start",
        probe_id=None,
        runtime=_runtime(
            context={
                "non_interactive": True,
                "non_interactive_policy": {"auto_profile": True, "auto_proceed": True},
            }
        ),
        adapter=adapter,
    )

    assert result["code"] != "interactive_required"
    assert adapter.initialize_parent_sandbox_values == [True]


async def test_tool_allows_declared_minimal_profile_intent_for_start(tmp_path: Path) -> None:
    """@impl RUI-009

    The closed non-interactive policy admits ``profile_intent=minimal``.

    @impl EXI-001
    """
    adapter = _Adapter(_envelope(tmp_path))
    result = await run_deep_research(
        action="start",
        probe_id=None,
        runtime=_runtime(
            context={
                "non_interactive": True,
                "non_interactive_policy": {
                    "auto_profile": True,
                    "auto_proceed": True,
                    "profile_intent": "minimal",
                },
            }
        ),
        adapter=adapter,
    )

    assert result["code"] != "interactive_required"
    assert adapter.initialize_parent_sandbox_values == [True]


async def test_tool_rejects_missing_or_incomplete_non_interactive_policy_before_bundle_publication(
    tmp_path: Path,
) -> None:
    invalid_policies = (
        None,
        {},
        {"auto_profile": True},
        {"auto_proceed": True},
        {"auto_profile": False, "auto_proceed": True},
        {"auto_profile": True, "auto_proceed": False},
        {"auto_profile": 1, "auto_proceed": True},
        {"auto_profile": True, "auto_proceed": "yes"},
        {"auto_profile": True, "auto_proceed": True, "unexpected": True},
        {"auto_profile": True, "auto_proceed": True, "profile_intent": "standard"},
        {"auto_profile": True, "auto_proceed": True, "profile_intent": "minimal", "unexpected": True},
        {"auto_profile": True, "auto_proceed": True, "profile_intent": 1},
        {"auto_profile": True, "auto_proceed": True, "profile_intent": ""},
    )
    for policy in invalid_policies:
        adapter = _Adapter(_envelope(tmp_path))
        context: dict[str, object] = {"non_interactive": True}
        if policy is not None:
            context["non_interactive_policy"] = policy
        result = await run_deep_research(
            action="start",
            probe_id=None,
            runtime=_runtime(context=context),
            adapter=adapter,
        )

        assert result["code"] == "interactive_required"
        assert not list(adapter.envelope.workspace_host_path.rglob("state.json"))


async def test_tool_rejects_the_retired_marker_before_sandbox_or_graph_selection(tmp_path: Path) -> None:
    closed_policy = {"auto_profile": True, "auto_proceed": True}

    def forbidden_graph_executor() -> BundleGraphExecutor:
        raise AssertionError("retired marker must not select a graph executor")

    for action in ("start", "resume", "refine"):
        for context in (
            {"disable_clarification": True, "non_interactive_policy": closed_policy},
            {
                "disable_clarification": True,
                "non_interactive": True,
                "non_interactive_policy": closed_policy,
            },
        ):
            adapter = _Adapter(_envelope(tmp_path))
            result = await run_deep_research(
                action=action,
                probe_id=None,
                runtime=_runtime(context=context, action=action),
                adapter=adapter,
                bundle_graph_executor_factory=forbidden_graph_executor,
            )

            assert result["code"] == "interactive_required"
            assert adapter.initialize_parent_sandbox_values == []
            assert not list(adapter.envelope.workspace_host_path.rglob("state.json"))
