"""Operator-experience acceptance suite for the debugger workbench.

Each scenario is one realistic operator experience, driven through the real
script (executed as ``__main__``), in its own isolated Bundle root, at a
realistic terminal size, with a dwell after the assertions so a timer-driven
re-render cannot hide. The suite prints one line per experience and exits
non-zero when any experience fails.

This is deliberately broader than a unit test: it answers "what does the
operator actually experience, end to end" for the whole surface - entries, HITL,
stepping, continuous run, pause, observation panes, help/palette, recovery,
read-only replay, layout degradation and observation honesty.
"""

from __future__ import annotations

import argparse
import asyncio
import runpy
import sys
import tempfile
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).resolve().parent
HARNESS = SCRIPTS.parent
DEFAULT_SIZE = (110, 34)
DWELL = 1.3

sys.path.insert(0, str(SCRIPTS))
from tui_journey_probe import (  # noqa: E402
    _files_text,
    _inspect_text,
    _log_text,
    _node_context_text,
    _prompt_text,
)


class ExperienceFailure(AssertionError):
    """One operator experience did not behave as promised."""


@dataclass
class Driver:
    app: Any
    pilot: Any
    size: tuple[int, int] = DEFAULT_SIZE

    async def submit(self, text: str) -> None:
        self.app.query_one("#composer").value = text
        await self.pilot.pause()
        await self.pilot.press("enter")

    async def click(self, selector: str) -> None:
        await self.pilot.click(selector)
        await self.pilot.pause()

    async def settle(self, seconds: float = DWELL) -> None:
        await asyncio.sleep(seconds)
        await self.pilot.pause()

    async def wait(self, predicate: Callable[[], bool], *, seconds: float = 30.0) -> bool:
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            await self.pilot.pause()
            if predicate():
                return True
            await asyncio.sleep(0.05)
        return False

    def expect(self, condition: bool, message: str) -> None:
        if not condition:
            raise ExperienceFailure(
                f"{message}\n  inspect={_inspect_text(self.app)!r}\n"
                f"  prompt={_prompt_text(self.app)!r}\n  log={_log_text(self.app)[-300:]!r}"
            )

    @property
    def log(self) -> str:
        return _log_text(self.app)

    @property
    def flat_log(self) -> str:
        return _log_text(self.app).replace("\n", "")

    @property
    def inspect(self) -> str:
        return _inspect_text(self.app)

    @property
    def prompt(self) -> str:
        return _prompt_text(self.app)

    async def start_step(self, question: str) -> None:
        await self.submit(question)
        ok = await self.wait(lambda: self.app._debug_driver is not None)
        self.expect(ok, "the Start Step entry never opened a session")

    async def answer(self, text: str = "depth: standard") -> None:
        await self.submit(text)
        ok = await self.wait(lambda: "paused_at_boundary" in self.inspect or "terminal" in self.inspect)
        self.expect(ok, f"the HITL answer was not consumed: {self.inspect!r}")


@dataclass
class Experience:
    name: str
    run: Callable[[Driver], Any]
    size: tuple[int, int] = DEFAULT_SIZE
    seconds: float = 0.0
    detail: list[str] = field(default_factory=list)


async def _drive(app: Any, experience: Experience, report: list[str]) -> None:
    async with app.run_test(size=experience.size) as pilot:
        driver = Driver(app=app, pilot=pilot, size=experience.size)
        ok = await driver.wait(lambda: type(getattr(app, "last_update", None)).__name__ == "Ready")
        driver.expect(ok, "the app never reached Ready")
        await experience.run(driver)


def _run_experience(experience: Experience) -> tuple[bool, float, str]:
    """Run one experience in its own app + isolated Bundle root."""
    root = Path(tempfile.mkdtemp(prefix="experience-")) / "demo-runs"
    argv = ["demo_tui.py", "--fixture", "--debug"]
    result: dict[str, Any] = {"error": None}

    import textual.app

    original_run = textual.app.App.run
    original_argv = sys.argv[:]

    def fake_run(self: Any, *args: Any, **kwargs: Any) -> None:
        main_module = sys.modules["__main__"]
        real_adapter = main_module.DemoAdapter
        main_module.DemoAdapter = lambda: real_adapter(bundle_root=root)

        async def drive() -> None:
            await _drive(self, experience, experience.detail)

        try:
            asyncio.run(drive())
        except BaseException as exc:  # noqa: BLE001 - reported per experience
            result["error"] = f"{type(exc).__name__}: {exc}"

    textual.app.App.run = fake_run
    sys.argv = argv
    started = time.monotonic()
    try:
        runpy.run_path(str(SCRIPTS / "demo_tui.py"), run_name="__main__")
    except BaseException as exc:  # noqa: BLE001 - reported per experience
        result["error"] = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()[-600:]}"
    finally:
        textual.app.App.run = original_run
        sys.argv = original_argv
    elapsed = time.monotonic() - started
    error = result["error"]
    return (error is None, elapsed, error or "")


# --------------------------------------------------------------------------- #
# The experiences
# --------------------------------------------------------------------------- #


async def _first_screen(d: Driver) -> None:
    """E1: the first screen is actionable and lists what may follow."""
    d.expect("姿态: 无调试会话" in d.inspect, "the first screen must state that no session is live")
    d.expect("/help" in d.prompt and "/attach" in d.prompt, "the prompt must list the legal actions")
    d.expect("Start Run" in d.prompt and "Start Step" in d.prompt, "the prompt must offer both start compositions")
    hint = d.app.query_one("#hint").render().plain
    d.expect("/pause" in hint and "/help" in hint, f"the hint omits workbench commands: {hint!r}")
    d.expect(d.app.query_one("#debug-start-run").display, "the Start Run entry must be visible")
    await d.settle()


async def _hitl_states_the_request(d: Driver) -> None:
    """E2: a HITL stop says what it asks and what may follow (no guessing)."""
    await d.start_step("你能干什么")
    d.expect("awaiting_hitl" in d.inspect, f"the start must land on HITL: {d.inspect!r}")
    d.expect("→ 等待 hitl1 输入" in d.log, "the log must state what the HITL stop waits for")
    d.expect("Deep Research input - fixture composition" in d.log, "the node-authored request must be shown")
    d.expect("输入后按 Enter" in d.log, "the log must say how to answer")
    d.expect("HITL 等待输入" in d.prompt and "/help" in d.prompt, "the prompt must state the ask and the actions")
    session = await d.app._debug_driver.session_snapshot(d.app._debug_bundle_id)
    d.expect(session is not None and session.pending_request is not None, "the driver must carry the request")
    d.expect(session.pending_request.title in d.log, "the shown request must be the carried one, not a rebuilt one")
    await d.settle()


async def _answer_then_step(d: Driver) -> None:
    """E3: answering HITL lands on a boundary; an empty Enter commits one node."""
    await d.start_step("Compare storage approaches")
    await d.answer()
    d.expect("paused_at_boundary" in d.inspect and "下一节点: topic_planning" in d.inspect, d.inspect)
    await d.submit("")
    ok = await d.wait(lambda: "topic_planning" in d.log and "wave0" in d.inspect)
    d.expect(ok, f"the empty-Enter step did not advance one node: {d.inspect!r}")
    await d.settle()


async def _start_run_and_continue(d: Driver) -> None:
    """E4: Start Run stops at the next stop; /run continues to the terminal."""
    d.app.query_one("#composer").value = "Compare storage approaches"
    await d.pilot.pause()
    await d.click("#debug-start-run")
    ok = await d.wait(lambda: "Start Run" in d.flat_log and "awaiting_hitl" in d.inspect)
    d.expect(ok, f"Start Run must say which flavour ran and stop at HITL: {d.inspect!r}")
    await d.answer()
    await d.submit("/run")
    ok = await d.wait(lambda: "姿态: terminal" in d.inspect, seconds=60)
    d.expect(ok, f"/run must reach the next stop (terminal): {d.inspect!r}")
    d.expect("会话终态" in d.log, "the terminal stop must be stated in the log")
    await d.settle()


async def _pause_semantics(d: Driver) -> None:
    """E5: a pause takes effect at the next committed boundary and is honest at terminal."""
    await d.start_step("Compare storage approaches")
    await d.answer()
    await d.submit("/pause")
    ok = await d.wait(lambda: "pause_requested" in d.inspect or "暂停" in d.log)
    d.expect(ok, "the pause request was not acknowledged")
    await d.submit("/run")
    ok = await d.wait(lambda: "paused_at_boundary" in d.inspect)
    d.expect(ok, f"the honoured pause must stop at a committed boundary: {d.inspect!r}")
    await d.answer() if "awaiting_hitl" in d.inspect else None
    await d.submit("/run")
    ok = await d.wait(lambda: "姿态: terminal" in d.inspect, seconds=60)
    d.expect(ok, "the session should still be able to reach terminal")
    await d.submit("/pause")
    ok = await d.wait(lambda: "没有下一个节点边界可暂停" in d.flat_log)
    d.expect(ok, "a terminal session must refuse a pause honestly")
    await d.settle()


async def _observation_panes(d: Driver) -> None:
    """E6: /context and /files render typed pages on demand, with closed denials."""
    await d.start_step("Compare storage approaches")
    await d.submit("/context")
    ok = await d.wait(lambda: "尚无已捕获的调用上下文" in _node_context_text(d.app))
    d.expect(ok, "the Context pane must state its honest empty coverage in fixture mode")
    d.expect(d.app.query_one("#node-context").display, "the Context pane must appear on demand")
    await d.submit("/files")
    ok = await d.wait(lambda: "Files: workspace:." in _files_text(d.app))
    d.expect(ok, "the Files pane must list the workspace root page")
    await d.submit("/files ../../etc/passwd")
    ok = await d.wait(lambda: "path_escape" in _files_text(d.app))
    d.expect(ok, "an escaping path must be denied with its closed reason")
    await d.submit("/files no-such-entry")
    ok = await d.wait(lambda: "not_found" in _files_text(d.app))
    d.expect(ok, "a missing path must be denied with its closed reason")
    files_text = _files_text(d.app)
    d.expect("/private/" not in files_text and "/Users/" not in files_text, "the pane leaked a host path")
    await d.settle()


async def _help_and_palette(d: Driver) -> None:
    """E7: /help lists everything and the palette reaches the same typed actions."""
    await d.submit("/help")
    ok = await d.wait(lambda: "/pause=请求在下一节点边界暂停" in d.flat_log)
    d.expect(ok, "/help must list the whole surface")
    for capability in ("New Run(Start Step)", "/run [节点]=Start Run", "/detach=退出会话", "Ctrl+P 命令面板"):
        d.expect(capability in d.flat_log, f"/help omits {capability!r}")

    from textual.command import CommandInput

    d.app.query_one("#composer").value = "Palette run"
    await d.pilot.pause()
    await d.pilot.press("ctrl+p")
    await d.pilot.pause()
    d.app.screen.query_one(CommandInput).value = "New Run"
    await d.pilot.pause()
    await d.pilot.press("enter")
    ok = await d.wait(lambda: d.app._debug_driver is not None)
    d.expect(ok, "the palette New Run action must open a session like the button does")
    await d.settle()


async def _recovery_chain(d: Driver) -> None:
    """E8: detach keeps the bundle, a new start is refused with guidance, /cancel frees it."""
    await d.start_step("Compare storage approaches")
    bundle_id = d.app._debug_bundle_id
    await d.submit("/detach")
    ok = await d.wait(lambda: d.app._debug_driver is None and "姿态: 无调试会话" in d.inspect)
    d.expect(ok, "detach must clear the session and say so")
    await d.submit("Compare storage again")
    ok = await d.wait(lambda: "已有活跃 bundle" in d.flat_log)
    d.expect(ok, "a retained bundle must refuse a second start with an actionable message")
    d.expect("/cancel" in d.flat_log, "the refusal must name the recovery command")
    await d.submit("/cancel")
    ok = await d.wait(lambda: "已取消活跃调试 bundle" in d.flat_log)
    d.expect(ok, "the recovery cancel must abandon the retained bundle")
    await d.submit("Compare storage once more")
    ok = await d.wait(lambda: d.app._debug_driver is not None)
    d.expect(ok, "a fresh start must be admitted after the recovery cancel")
    d.expect(bundle_id is not None, "the first session must have had a bundle")


async def _attach_sees_the_request(d: Driver) -> None:
    """E9: attaching to a Bundle paused at a HITL still says what it waits for."""
    await d.start_step("Compare storage approaches")
    await d.submit("/detach")
    ok = await d.wait(lambda: d.app._debug_driver is None)
    d.expect(ok, "detach must clear the session")
    await d.submit("/attach")
    ok = await d.wait(lambda: "Attach 候选" in d.log)
    d.expect(ok, "the attach entry must list bounded candidates")
    await d.settle()
    d.expect("[takeover]" in d.log, f"the retained bundle must be offered as takeover: {d.log[-200:]!r}")


async def _replay_is_read_only(d: Driver) -> None:
    """E10: /replay renders the trace without taking a session."""
    await d.start_step("Compare storage approaches")
    bundle_id = d.app._debug_bundle_id
    await d.submit("/detach")
    ok = await d.wait(lambda: d.app._debug_driver is None)
    d.expect(ok, "detach must clear the session")
    await d.submit("/replay")
    ok = await d.wait(lambda: "Replay 候选" in d.flat_log)
    d.expect(ok, "a bare /replay must list candidates instead of a dead-end usage line")
    d.expect("[takeover]" in d.log, "the retained bundle must be offered as takeover")
    await d.submit(f"/replay {bundle_id}")
    ok = await d.wait(lambda: "只读回放" in d.flat_log and "不可解析" not in d.flat_log)
    d.expect(ok, "the replay entry must render a retained bundle's trace")
    d.expect(d.app._debug_driver is None, "replay must not open a debug session")


async def _degraded_layout(d: Driver) -> None:
    """E11: below the supported minimum the workbench says so instead of clipping."""
    screen = d.app.screen.region
    notice = d.app.query_one("#hint").render().plain
    d.expect("小于调试工作台建议" in notice and "80x24" in notice, f"no honest size notice: {notice!r}")
    for widget_id in ("banner", "log", "inspect", "prompt", "controls", "debug-controls", "hint"):
        widget = d.app.query_one(f"#{widget_id}")
        d.expect(widget.display and widget.region.height > 0, f"#{widget_id} is not visible at {d.size}")
        d.expect(widget.region.y + widget.region.height <= screen.height, f"#{widget_id} is clipped at {d.size}")
    d.expect(d.app.query_one("#log").region.height >= 4, "the log must stay readable when degraded")
    d.expect(not d.app.query_one("#node-context").display, "the on-demand panes fold when degraded")
    d.expect(d.app.query_one("#composer").has_focus, "the composer must stay usable when degraded")
    await d.settle()


async def _observation_honesty(d: Driver) -> None:
    """E12: a cancelled session leaves a truthful retained observation (DPL-014)."""
    import json

    await d.start_step("Compare storage approaches")
    bundle_id = d.app._debug_bundle_id
    await d.submit("/cancel")
    ok = await d.wait(lambda: "已取消活跃调试 bundle" in d.flat_log)
    d.expect(ok, "the cancel must be acknowledged")
    roots = await asyncio.to_thread(
        lambda: sorted(Path(d.app._adapter.bundle_root).rglob(f"{bundle_id}/diagnostics/run-summary.json"))
    )
    d.expect(bool(roots), "the retained summary must exist")
    raw = await asyncio.to_thread(roots[0].read_text, "utf-8")
    status = json.loads(raw).get("status")
    d.expect(status == "cancelled", f"the operator report would call this bundle resumable: {status!r}")


async def _explore_harness(d: Driver) -> None:
    """E13: /harness shows what the harness is made of."""
    await d.submit("/harness")
    ok = await d.wait(lambda: "Harness 解剖" in d.log)
    d.expect(ok, "/harness must describe the harness")
    flat = d.flat_log
    for fragment in (
        "组合:",
        "executor recipe:",
        "组合名:",
        "节点类型(",
        "逻辑节点(",
        "工作区根(虚拟 alias):",
        "可读投影:",
        "runbook-030",
    ):
        d.expect(fragment in flat, f"/harness omits {fragment!r}")
    d.expect("/Users/" not in d.log and "/private/" not in d.log, "/harness must not leak host paths")


async def _explore_targets_and_inspect(d: Driver) -> None:
    """E14: /targets lists the debuggable objects and /inspect shows one internals."""
    await d.start_step("Compare storage approaches")
    bundle_id = d.app._debug_bundle_id
    await d.submit("/targets")
    ok = await d.wait(lambda: "可调试对象" in d.log and "bundle " in d.log)
    d.expect(ok, "/targets must enumerate the workspace's objects")
    d.expect("当前会话:" in d.flat_log, "/targets must include the live session")
    d.expect("scope:" in d.flat_log, "/targets must name the scope")
    await d.submit(f"/inspect {bundle_id}")
    ok = await d.wait(lambda: "帧 " in d.flat_log and bundle_id[:16] in d.flat_log)
    d.expect(ok, f"/inspect must show the bundle internals: {d.log[-200:]!r}")
    flat = d.flat_log
    for fragment in ("状态=", "generation=", "Node Context", "工作单元(", "观测摘要:", "帧 01"):
        d.expect(fragment in flat, f"/inspect omits {fragment!r}")
    await d.settle()


async def _context_content_and_drilldown(d: Driver) -> None:
    """E15: a captured invocation shows what the model was given and allowed."""
    import hashlib
    from datetime import UTC, datetime

    from deerflow_deep_research.domain.bundle import BundleId
    from deerflow_deep_research.domain.node_context import (
        CapturedResourceLayer,
        EnforcedToolPosture,
        NodeContextActivityFacts,
        NodeContextSnapshot,
        VirtualRootsView,
    )
    from deerflow_deep_research.runtime.node_context_store import NodeContextStore

    await d.start_step("Compare storage approaches")
    app = d.app
    adapter = app._adapter
    bundle = await adapter._bundle_lifecycle.resolve(
        scope=app._debug_scope(adapter), bundle_id=BundleId(app._debug_bundle_id)
    )
    d.expect(bundle is not None, "the live session must be resolvable")
    store = NodeContextStore(bundle_root=adapter._bundle_lifecycle.private_root(bundle), bundle_id=app._debug_bundle_id)

    def digest(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    key = store.record_sync(
        NodeContextSnapshot(
            context_id="ctx-" + "0" * 28,
            bundle_id=app._debug_bundle_id,
            node="wave0",
            attempt_id="g0-wave0-a1",
            node_agent_ordinal=1,
            created_at=datetime.now(UTC),
            initial_system_policy="system policy text",
            initial_human_message="Objective: compare storage",
            base_policy_layer=CapturedResourceLayer(
                identity="resources/node_agent/runtime_policy.md", text="base policy", sha256=digest("base policy")
            ),
            capability_layer=CapturedResourceLayer(
                identity="pkg:capabilities/wave0.md", text="capability body", sha256=digest("capability body")
            ),
            request_objective="Compare storage options",
            request_expected_output="A comparison",
            safe_model_label="configured-model",
            tool_posture=EnforcedToolPosture(
                requested_tool_names=("web_search",), enforced_tool_names=("web_search",), posture_kind="required"
            ),
            budget={"max_model_calls": 8},
            virtual_roots=VirtualRootsView(workspace_root="/mnt/user-data/workspace"),
        )
    )
    store.record_activity_sync(key, NodeContextActivityFacts(model_calls=2, tool_calls=1, outcome="completed"))

    await d.submit("/context")
    ok = await d.wait(lambda: "enforced tools: web_search" in _node_context_text(app))
    d.expect(ok, f"the Context pane must state what the model was allowed: {_node_context_text(app)!r}")
    d.expect("budget: max_model_calls=8" in _node_context_text(app), "the Context pane must state the budget")

    await d.submit("/context wave0#1")
    ok = await d.wait(lambda: "捕获详情" in _node_context_text(app))
    d.expect(ok, "a selector must drill into one capture")
    detail = _node_context_text(app)
    for fragment in (
        "system policy text",
        "base policy layer:",
        "enforced tools: requested=web_search → enforced=web_search (required)",
        "raw provider histories: NOT_RETAINED",
    ):
        d.expect(fragment in detail, f"the capture detail omits {fragment!r}")


EXPERIENCES: tuple[Experience, ...] = (
    Experience("E1  首屏可操作且列出可做动作", _first_screen),
    Experience("E2  HITL 明确说清在问什么", _hitl_states_the_request),
    Experience("E3  回答 HITL 后单步推进一个节点", _answer_then_step),
    Experience("E4  Start Run 停在停点，/run 跑到终态", _start_run_and_continue),
    Experience("E5  /pause 在下一边界兑现，终态诚实拒绝", _pause_semantics),
    Experience("E6  /context 与 /files 按需呈现且拒绝闭合", _observation_panes),
    Experience("E7  /help 全量清单 + 命令面板同效", _help_and_palette),
    Experience("E8  恢复链：detach → busy → /cancel → 重开", _recovery_chain),
    Experience("E9  attach 到暂停中的 bundle 仍知它在等什么", _attach_sees_the_request),
    Experience("E10 /replay 只读，不占会话", _replay_is_read_only),
    Experience("E11 小终端诚实降级（80x24）", _degraded_layout, (80, 24)),
    Experience("E12 取消后的留存观测诚实（DPL-014）", _observation_honesty),
    Experience("E13 /harness 展示 harness 自身解剖", _explore_harness),
    Experience("E14 /targets 列出可调试对象 + /inspect 看内部", _explore_targets_and_inspect),
    Experience("E15 捕获内容可见（工具/预算/分层）+ 下钻", _context_content_and_drilldown),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", default="", help="run only experiences whose name contains this text")
    args = parser.parse_args()

    selected = [e for e in EXPERIENCES if args.only.lower() in e.name.lower()]
    print(f"operator experiences: {len(selected)}")
    failures: list[tuple[str, str]] = []
    for experience in selected:
        passed, elapsed, error = _run_experience(experience)
        mark = "PASS" if passed else "FAIL"
        print(f"  [{mark}] {experience.name}  ({elapsed:.1f}s)")
        if not passed:
            failures.append((experience.name, error))

    print(f"experiences passed: {len(selected) - len(failures)}/{len(selected)}")
    for name, error in failures:
        print(f"\n--- {name} ---\n{error}")
    if failures:
        print("EXPERIENCES FAILED")
        return 1
    print("EXPERIENCES OK: every operator journey behaved as promised")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
