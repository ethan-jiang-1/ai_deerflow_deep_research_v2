"""Recon-chat streaming loop contract (BUG-076).

@impl repair-embedded-tui-first-live-defects
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def _scripts_path():
    """Ensure demo_tui is importable."""
    scripts = str(Path(__file__).resolve().parents[2] / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    return scripts


class _FakeStreamModel:
    """Scripted astream model: one list of chunks per round, capturing messages."""

    def __init__(self, rounds: list[list[SimpleNamespace]]) -> None:
        self._rounds = rounds
        self.messages_by_round: list[list[object]] = []
        self._round = 0

    def astream(self, messages):
        self.messages_by_round.append(list(messages))
        chunks = self._rounds[self._round]
        self._round += 1

        async def _gen():
            for chunk in chunks:
                yield chunk

        return _gen()


def _chunk(content: str = "", tool_calls: list[dict] | None = None) -> SimpleNamespace:
    return SimpleNamespace(content=content, tool_calls=tool_calls)


def _fake_tool(calls: list[dict]):
    def invoke(args):
        calls.append(dict(args))
        return "fake-listing"

    return SimpleNamespace(name="list_workspace", invoke=invoke)


_REAL_CALL = {"name": "list_workspace", "args": {}, "id": "call_00_abc123", "type": "tool_call", "index": 0}
# DeepSeek streams an empty trailing tool_call delta on the SAME index after the
# real one (observed live 2026-09-28); it must not clobber the accumulated call.
_EMPTY_TAIL = {"name": "", "args": {}, "id": None, "type": "tool_call", "index": 0}


@pytest.mark.asyncio
async def test_trailing_empty_tool_delta_does_not_clobber_the_real_call(_scripts_path):
    """BUG-076: the recon chat died with pydantic ValidationError on the first
    tool-calling turn: the empty trailing delta overwrote the real call, and
    ToolMessage(tool_call_id=call.get("id", "")) received None (the key exists).
    """
    from demo_tui import _stream_chat_turn

    tool_calls: list[dict] = []
    tool = _fake_tool(tool_calls)
    model = _FakeStreamModel(
        [
            [_chunk(tool_calls=[_REAL_CALL]), _chunk(tool_calls=[_EMPTY_TAIL])],
            [_chunk("workspace 根下有 logs 与 runs 目录。")],
        ]
    )
    messages = [object(), object()]
    text = await _stream_chat_turn(model, messages, [tool], on_text=lambda _partial: None)

    assert text == "workspace 根下有 logs 与 runs 目录。"
    assert tool_calls == [{}], "the real tool must execute exactly once"
    second_round = model.messages_by_round[1]
    tool_messages = [m for m in second_round if type(m).__name__ == "ToolMessage"]
    assert len(tool_messages) == 1
    assert tool_messages[0].tool_call_id == "call_00_abc123"
    ai_messages = [m for m in second_round if type(m).__name__ == "AIMessage"]
    assert ai_messages[0].tool_calls[0]["name"] == "list_workspace"
    assert ai_messages[0].tool_calls[0]["id"] == "call_00_abc123"


@pytest.mark.asyncio
async def test_plain_text_turn_without_tool_calls(_scripts_path):
    """A no-tool turn streams straight through: no ToolMessage is ever built."""
    from demo_tui import _stream_chat_turn

    model = _FakeStreamModel([[_chunk("你好！"), _chunk("有什么可以帮你看的？")]])
    messages = [object()]
    text = await _stream_chat_turn(model, messages, [], on_text=lambda _partial: None)

    assert text == "你好！有什么可以帮你看的？"
    assert len(model.messages_by_round) == 1
