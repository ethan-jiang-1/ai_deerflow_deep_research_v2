"""Real DeerFlow proof for ordinary public-controller skill loading.

@impl DEC-003
@impl DEC-004
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import Runnable

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIGURE_PATH = REPO_ROOT / "deep_research_harness" / "scripts" / "configure.py"
SKILL_SOURCE = REPO_ROOT / "deep_research_harness" / "config" / "public-skill" / "deep-research-controller" / "SKILL.md"
SKILL_CONTAINER_PATH = "/mnt/skills/public/deep-research-controller/SKILL.md"


class _ScriptedExternalModel(FakeMessagesListChatModel):
    """The only scripted boundary: successive responses from the external model."""

    def bind_tools(self, tools: Any, *, tool_choice: Any = None, **kwargs: Any) -> Runnable:  # type: ignore[override]
        return self


def _configure_module():
    spec = importlib.util.spec_from_file_location("ordinary_controller_configure", CONFIGURE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _config_text(*, skills_root: Path, deferred_discovery: bool) -> str:
    return f"""\
config_version: 19
models:
  - name: ordinary-loader-test-model
    display_name: Ordinary loader test model
    use: langchain_openai:ChatOpenAI
    model: gpt-4o-mini
    api_key: test-only-key
sandbox:
  use: deerflow.sandbox.local:LocalSandboxProvider
tool_groups:
  - name: file:read
tools:
  - name: read_file
    group: file:read
    use: deerflow.sandbox.tools:read_file_tool
skills:
  path: {skills_root}
  container_path: /mnt/skills
  deferred_discovery: {str(deferred_discovery).lower()}
title:
  enabled: false
memory:
  enabled: false
loop_detection:
  enabled: false
safety_finish_reason:
  enabled: false
read_before_write:
  enabled: false
token_usage:
  enabled: false
agents_api:
  enabled: false
"""


@pytest.fixture
def configured_deerflow_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Materialize the committed skill and Agent into an isolated DeerFlow home."""

    def build(*, deferred_discovery: bool) -> Any:
        root = tmp_path / ("deferred" if deferred_discovery else "direct")
        root.mkdir()
        (root / "backend").mkdir()
        skills_root = root / "skills"
        (skills_root / "public").mkdir(parents=True)
        (skills_root / "custom").mkdir(parents=True)
        config_path = root / "config.yaml"
        extensions_path = root / "extensions_config.json"
        home = root / ".deer-flow"
        config_path.write_text(
            _config_text(skills_root=skills_root, deferred_discovery=deferred_discovery),
            encoding="utf-8",
        )
        extensions_path.write_text('{"mcpServers": {}, "skills": {}}\n', encoding="utf-8")
        env = {
            "DEER_FLOW_CONFIG_PATH": str(config_path),
            "DEER_FLOW_EXTENSIONS_CONFIG_PATH": str(extensions_path),
            "DEER_FLOW_SKILLS_PATH": str(skills_root),
            "DEER_FLOW_HOME": str(home),
            "DEER_FLOW_AUTH_DISABLED": "1",
        }

        configured = _configure_module().execute_configuration(
            root,
            env,
            mode="apply",
            online_detector=lambda: False,
        )
        assert configured.entry_status == "ready"
        assert (home / "users/default/agents/deep-research/config.yaml").is_file()
        assert (skills_root / "public/deep-research-controller/SKILL.md").is_file()

        for key, value in env.items():
            monkeypatch.setenv(key, value)

        # Reset process caches at their real configuration boundary. Runtime tools
        # remain the production objects resolved from the materialized config.
        from deerflow.config import paths as paths_module
        from deerflow.config.app_config import AppConfig, reset_app_config, set_app_config
        from deerflow.config.extensions_config import reset_extensions_config
        from deerflow.sandbox.sandbox_provider import reset_sandbox_provider
        from deerflow.skills.storage import reset_skill_storage

        reset_app_config()
        reset_extensions_config()
        reset_skill_storage()
        reset_sandbox_provider()
        monkeypatch.setattr(paths_module, "_paths", None)
        app_config = AppConfig.from_file(str(config_path))
        set_app_config(app_config)
        from deerflow_deep_research.runtime.startup_snapshot import capture_startup_fingerprint

        monkeypatch.setenv(
            "DEER_FLOW_DEEP_RESEARCH_STARTUP_FINGERPRINT",
            capture_startup_fingerprint(app_config, worker_value=None),
        )
        return app_config

    yield build

    from deerflow.config.app_config import reset_app_config
    from deerflow.config.extensions_config import reset_extensions_config
    from deerflow.sandbox.sandbox_provider import reset_sandbox_provider
    from deerflow.skills.storage import reset_skill_storage

    reset_app_config()
    reset_extensions_config()
    reset_skill_storage()
    reset_sandbox_provider()


def _tool_call(name: str, args: dict[str, Any], identifier: str) -> AIMessage:
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": identifier, "type": "tool_call"}])


def _run_ordinary_turn(
    *,
    app_config: Any,
    responses: list[AIMessage],
    recursion_limit: int = 24,
    messages: list[BaseMessage] | None = None,
    thread_id: str = "ordinary-loader-thread",
    run_id: str = "ordinary-loader-run",
) -> dict[str, Any]:
    """Run one actual lead-agent turn with only its external model responses scripted."""

    from deerflow.agents.lead_agent import agent as lead_agent_module

    model = _ScriptedExternalModel(responses=responses)
    turn_messages = (
        messages
        if messages is not None
        else [HumanMessage(content="Please investigate the policy evidence for this research question.")]
    )
    factory_config = {
        "configurable": {
            "agent_name": "deep-research",
            "user_id": "default",
            "thinking_enabled": False,
            "subagent_enabled": False,
        }
    }
    invoke_config = {
        "configurable": {
            "thread_id": thread_id,
            "run_id": run_id,
            "user_id": "default",
        },
        "recursion_limit": recursion_limit,
    }
    runtime_context = {
        "thread_id": thread_id,
        "run_id": run_id,
        "user_id": "default",
        "app_config": app_config,
    }
    with patch.object(lead_agent_module, "create_chat_model", return_value=model):
        agent = lead_agent_module._make_lead_agent(factory_config, app_config=app_config)
        return agent.invoke(
            {"messages": turn_messages},
            invoke_config,
            context=runtime_context,
        )


def _tool_message(messages: list[BaseMessage], tool_call_id: str) -> ToolMessage:
    return next(
        message for message in messages if isinstance(message, ToolMessage) and message.tool_call_id == tool_call_id
    )


def _ordinary_loader_indexes(messages: list[BaseMessage]) -> tuple[int, int] | None:
    """Return real canonical-read/control positions, or reject shortcut transcripts."""

    read_index: int | None = None
    control_index: int | None = None
    for index, message in enumerate(messages):
        if not isinstance(message, AIMessage):
            continue
        tool_calls = message.tool_calls or []
        if len(tool_calls) == 1 and tool_calls[0].get("name") == "read_file":
            if tool_calls[0].get("args", {}).get("path") == SKILL_CONTAINER_PATH:
                read_index = index
        if len(tool_calls) == 1 and tool_calls[0].get("name") == "deep_research":
            control_index = index
    if read_index is None or control_index is None or read_index >= control_index:
        return None
    return read_index, control_index


def _assert_ordinary_loader_handoff(
    result: dict[str, Any],
    *,
    expect_deferred: bool,
    read_file_output_max_chars: int,
) -> None:
    messages = list(result["messages"])
    positions = _ordinary_loader_indexes(messages)
    assert positions is not None, "ordinary evidence requires canonical read_file before the exclusive lifecycle call"
    read_index, control_index = positions
    read_message = messages[read_index]
    assert isinstance(read_message, AIMessage)
    read_call = read_message.tool_calls[0]
    read_result = _tool_message(messages, str(read_call["id"]))
    expected_digest = hashlib.sha256(SKILL_SOURCE.read_bytes()).hexdigest()
    actual_content = read_result.content if isinstance(read_result.content, str) else ""
    assert hashlib.sha256(actual_content.encode("utf-8")).hexdigest() == expected_digest
    assert read_file_output_max_chars == 0 or len(actual_content) <= read_file_output_max_chars
    assert read_result.additional_kwargs.get("skill_context_entry", {}).get("path") == SKILL_CONTAINER_PATH
    assert [entry["path"] for entry in result["skill_context"]] == [SKILL_CONTAINER_PATH]

    control_message = messages[control_index]
    assert isinstance(control_message, AIMessage)
    assert len(control_message.tool_calls) == 1
    assert control_message.tool_calls[0]["name"] == "deep_research"
    assert control_message.tool_calls[0]["args"] == {"action": "status"}
    _tool_message(messages, str(control_message.tool_calls[0]["id"]))

    describe_indexes = [
        index
        for index, message in enumerate(messages)
        if isinstance(message, AIMessage)
        and any(call.get("name") == "describe_skill" for call in message.tool_calls or [])
    ]
    if expect_deferred:
        assert len(describe_indexes) == 1
        assert describe_indexes[0] < read_index
    else:
        assert describe_indexes == []


def test_non_slash_discovery_reads_committed_controller_before_exclusive_lifecycle_call(
    configured_deerflow_home,
) -> None:
    app_config = configured_deerflow_home(deferred_discovery=False)

    result = _run_ordinary_turn(
        app_config=app_config,
        responses=[
            _tool_call(
                "read_file",
                {"description": "Load the controller workflow", "path": SKILL_CONTAINER_PATH},
                "read-controller",
            ),
            _tool_call("deep_research", {"action": "status"}, "read-status"),
            AIMessage(content="The lifecycle response is available."),
        ],
    )

    _assert_ordinary_loader_handoff(
        result,
        expect_deferred=False,
        read_file_output_max_chars=app_config.sandbox.read_file_output_max_chars,
    )


def test_deferred_non_slash_discovery_still_reads_committed_controller_before_lifecycle_call(
    configured_deerflow_home,
) -> None:
    app_config = configured_deerflow_home(deferred_discovery=True)

    result = _run_ordinary_turn(
        app_config=app_config,
        responses=[
            _tool_call("describe_skill", {"name": "select:deep-research-controller"}, "describe-controller"),
            _tool_call(
                "read_file",
                {"description": "Load the returned controller workflow", "path": SKILL_CONTAINER_PATH},
                "read-controller",
            ),
            _tool_call("deep_research", {"action": "status"}, "read-status"),
            AIMessage(content="The lifecycle response is available."),
        ],
        recursion_limit=26,
    )

    _assert_ordinary_loader_handoff(
        result,
        expect_deferred=True,
        read_file_output_max_chars=app_config.sandbox.read_file_output_max_chars,
    )


def test_ordinary_loader_evidence_rejects_prompt_copy_slash_and_prewritten_control_shortcuts() -> None:
    control = _tool_call("deep_research", {"action": "status"}, "prewritten-control")
    shortcut_transcripts = (
        [SystemMessage(content=SKILL_SOURCE.read_text(encoding="utf-8")), control],
        [HumanMessage(content="/deep-research-controller investigate this"), control],
        [control],
    )

    assert all(_ordinary_loader_indexes(list(messages)) is None for messages in shortcut_transcripts)
