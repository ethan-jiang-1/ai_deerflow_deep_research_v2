#!/usr/bin/env python3
"""Headless journey harness for the interactive TUI entry points.

Why this exists
---------------
Import-time tests and per-link unit tests cannot see defects that live in *how
the script executes as ``__main__``*: definition/binding order, CLI-to-app
wiring, session routing, and lifecycle admission. Three operator-reported
failures in a row (missing fixture path, debug methods bound after the
``__main__`` guard, a second Enter re-opening a session as ``busy``) were all
invisible to the test suite. This harness executes the real TUI script as
``__main__`` with a headless stand-in for ``App.run``, drives a documented
operator journey with per-step semantic assertions, and prints a transcript.

Rule of use: an agent MUST run this before handing any TUI path to a human.

Usage:
    python scripts/tui_journey_probe.py            # runbook-030 fixture debugger ladder
    python scripts/tui_journey_probe.py --verbose  # also dump panes after a pass
Exit code: 0 when every step passes, 1 at the first failing step with panes.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

HARNESS_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = HARNESS_ROOT / "scripts"

TRANSCRIPT: list[str] = []
VERBOSE = False
PANE = {"log": "", "inspect": ""}


def _log(message: str) -> None:
    TRANSCRIPT.append(message)
    print(message, flush=True)


class StepFailed(AssertionError):
    """A journey step's semantic assertion failed."""


def _require(condition: bool, step: str, detail: str) -> None:
    if not condition:
        raise StepFailed(f"{step}: {detail}")


def _inspect_text(app: Any) -> str:
    from textual.widgets import Static

    return app.query_one("#inspect", Static).render().plain


def _log_text(app: Any) -> str:
    return app._rich_log_text()


def _capture(app: Any) -> None:
    PANE["log"] = _log_text(app)
    PANE["inspect"] = _inspect_text(app)


async def _wait(pilot: Any, predicate: Callable[[], bool], *, deadline_seconds: float = 30.0) -> bool:
    deadline = time.monotonic() + deadline_seconds
    while time.monotonic() < deadline:
        await pilot.pause()
        if predicate():
            return True
        await asyncio.sleep(0.05)
    await pilot.pause()
    return predicate()


async def _submit(app: Any, pilot: Any, text: str) -> None:
    app.query_one("#composer").value = text
    await pilot.pause()
    await pilot.press("enter")
    await pilot.pause()


async def _submit_and_settle(app: Any, pilot: Any, text: str, *, deadline_seconds: float = 30.0) -> bool:
    before = _log_text(app)
    await _submit(app, pilot, text)
    return await _wait(
        pilot,
        lambda: _log_text(app) != before or app._debug_driver is None,
        deadline_seconds=deadline_seconds,
    )


async def _click(app: Any, pilot: Any, selector: str) -> None:
    await pilot.click(selector)
    await pilot.pause()


async def _fixture_debugger_journey(app: Any, pilot: Any) -> None:
    """Drive the runbook-030 debugger ladder with per-step assertions.

    Real driver semantics asserted here (they differ from the first draft of
    runbook-030): a Start Step on a fresh bundle runs to the first interrupt,
    so the operator lands on hitl1's prompt, not on a pre-hitl1 boundary.
    """

    # 1. Ready and the RED-014 three entries -------------------------------
    ok = await _wait(pilot, lambda: type(getattr(app, "last_update", None)).__name__ == "Ready")
    _require(ok, "ready", f"app never reached Ready; inspect={_inspect_text(app)!r}")
    for entry in ("#debug-new-run", "#debug-attach", "#debug-replay"):
        _require(len(app.query(entry)) == 1, "entries", f"workbench entry {entry} is missing")
    _log("  [1] Ready + New Run/Attach/Replay entries .............. ok")

    # 2. New Run button lands on the first interrupt (hitl1) ---------------
    app.query_one("#composer").value = "Compare renewable-energy storage approaches"
    await pilot.pause()
    await _click(app, pilot, "#debug-new-run")
    ok = await _wait(pilot, lambda: app._debug_driver is not None, deadline_seconds=60)
    _require(ok, "start", f"session did not open; log tail:\n{_log_text(app)[-800:]}")
    first_bundle = app._debug_bundle_id
    log = _log_text(app)
    _require("Start Step" in log, "start-log", f"missing Start Step line; log tail:\n{log[-500:]}")
    inspect = _inspect_text(app)
    _require("awaiting_hitl" in inspect, "start-posture", f"expected the hitl1 prompt: {inspect!r}")
    _require("下一节点: hitl1" in inspect, "start-next-node", f"next node not projected: {inspect!r}")
    _log(f"  [2] New Run button -> {first_bundle[:16]}... at hitl1 prompt ... ok")

    # 3. Answer HITL1 ------------------------------------------------------
    await _submit_and_settle(app, pilot, "Use the default profile.")
    ok = await _wait(pilot, lambda: "awaiting_hitl" not in _inspect_text(app), deadline_seconds=60)
    _require(ok, "answer-hitl1", f"HITL1 answer not consumed; inspect={_inspect_text(app)!r}")
    _log("  [3] HITL1 answer consumed (paused at next boundary) ..... ok")

    # 4. Empty Enter advances one boundary ---------------------------------
    before = _log_text(app)
    await _submit(app, pilot, "")
    ok = await _wait(pilot, lambda: _log_text(app) != before, deadline_seconds=60)
    _require(ok, "empty-advance", "an empty Enter did not advance the session")
    _log("  [4] empty Enter advances one boundary ................... ok")

    # 5. Mid-ladder detach preserves the active bundle ---------------------
    await _submit(app, pilot, "/detach")
    ok = await _wait(pilot, lambda: app._debug_driver is None, deadline_seconds=30)
    _require(ok, "detach", "detach did not clear the session")
    _log("  [5] /detach clears the session .......................... ok")

    # 5a. Attach entry (button) reopens the retained bundle ----------------
    app.query_one("#composer").value = first_bundle
    await pilot.pause()
    await _click(app, pilot, "#debug-attach")
    ok = await _wait(pilot, lambda: app._debug_driver is not None, deadline_seconds=60)
    _require(ok, "attach-button", f"Attach button opened no session; log tail:\n{_log_text(app)[-500:]}")
    _require(app._debug_bundle_id == first_bundle, "attach-target", f"attached to {app._debug_bundle_id!r}")
    _require("已附加调试会话" in _log_text(app), "attach-log", "missing attach log line")
    _log(f"  [5a] Attach button reopens {first_bundle[:16]}... ......... ok")

    # 5b. Read-only replay via the slash entry (no session, no lease) ------
    await _submit(app, pilot, "/detach")
    ok = await _wait(pilot, lambda: app._debug_driver is None, deadline_seconds=30)
    _require(ok, "detach-2", "detach did not clear the attached session")
    before = _log_text(app)
    await _submit(app, pilot, f"/replay {first_bundle}")
    ok = await _wait(pilot, lambda: "只读回放（无 lease、不推进）" in _log_text(app), deadline_seconds=60)
    _require(ok, "replay", f"/replay produced no page; log tail:\n{_log_text(app)[-500:]}")
    _require(app._debug_driver is None, "replay-readonly", "replay must not open a debug session")
    replay_log = _log_text(app)[len(before) :]
    _require("bootstrap" in replay_log, "replay-frames", f"replay rendered no frames: {replay_log[-300:]!r}")
    _log(f"  [5b] /replay renders {first_bundle[:16]}... read-only ...... ok")

    # 6. The retained active bundle is refused with an actionable message --
    await _submit(app, pilot, "Compare renewable-energy storage approaches")
    ok = await _wait(pilot, lambda: "开启失败" in _log_text(app), deadline_seconds=60)
    _require(ok, "busy-trap", "a paused bundle did not refuse a second start")
    log = _log_text(app)
    _require("/cancel" in log, "busy-message", "busy denial is not actionable (no /cancel hint)")
    _log("  [6] retained bundle refuses start with /cancel hint ..... ok")

    # 7. /cancel recovers the scope ----------------------------------------
    await _submit(app, pilot, "/cancel")
    ok = await _wait(pilot, lambda: "已取消活跃调试 bundle" in _log_text(app), deadline_seconds=30)
    _require(ok, "cancel", f"/cancel did not cancel; log tail:\n{_log_text(app)[-500:]}")
    _log("  [7] /cancel abandons the retained bundle ................ ok")

    # 8. A fresh session is admitted again ---------------------------------
    await _submit(app, pilot, "Compare renewable-energy storage approaches")
    ok = await _wait(pilot, lambda: app._debug_driver is not None, deadline_seconds=60)
    _require(ok, "restart", f"session did not reopen after /cancel; log tail:\n{_log_text(app)[-500:]}")
    second_bundle = app._debug_bundle_id
    _require(second_bundle != first_bundle, "restart-identity", "reopened the same bundle")
    _log(f"  [8] fresh session after recovery -> {second_bundle[:16]}... ok")

    # 9. Step the ladder to a terminal posture -----------------------------
    ladder_log = _log_text(app)
    steps = 0
    while steps < 30:
        inspect = _inspect_text(app)
        if "terminal" in inspect:
            break
        if "awaiting_hitl" in inspect:
            await _submit_and_settle(app, pilot, "Use the default profile.")
        else:
            await _submit_and_settle(app, pilot, "")
        steps += 1
        inspect = _inspect_text(app)
        _log(f"      ladder {steps:02d}: {inspect}")
        delta = _log_text(app)[len(ladder_log) :]
        _require("开启失败" not in delta, "ladder-busy", f"ladder hit a busy denial at step {steps}")
        if "terminal" not in inspect:
            detail = f"next node missing at step {steps}: {inspect!r}"
            _require("下一节点: —" not in inspect, "ladder-next-node", detail)
    _require(
        "terminal" in _inspect_text(app),
        "ladder-terminal",
        f"ladder did not reach terminal in {steps} steps; inspect={_inspect_text(app)!r}",
    )
    _log(f"  [9] ladder reached terminal in {steps} steps ............ ok")

    # 10. Node Context page ------------------------------------------------
    await _submit(app, pilot, "/context")
    ok = await _wait(pilot, lambda: "Node Context" in _log_text(app), deadline_seconds=30)
    _require(ok, "context", f"/context produced no page; log tail:\n{_log_text(app)[-400:]}")
    _log("  [10] /context renders the Node Context page ............. ok")

    # 11. Clean detach -----------------------------------------------------
    await _submit(app, pilot, "/detach")
    ok = await _wait(pilot, lambda: app._debug_driver is None, deadline_seconds=30)
    _require(ok, "final-detach", "final detach did not clear the session")
    _log("  [11] /detach clears the session ......................... ok")


async def _drive_cancel(app: Any, pilot: Any) -> None:
    """Recovery routine: abandon the workspace's active debug bundle."""
    ok = await _wait(pilot, lambda: type(getattr(app, "last_update", None)).__name__ == "Ready")
    _require(ok, "ready", f"app never reached Ready; inspect={_inspect_text(app)!r}")
    _log("  [1] Ready .............................................. ok")
    await _submit(app, pilot, "/cancel")
    ok = await _wait(
        pilot,
        lambda: "已取消活跃调试 bundle" in _log_text(app) or "没有可取消的活跃调试会话" in _log_text(app),
        deadline_seconds=60,
    )
    _require(ok, "cancel", f"/cancel produced no outcome; log tail:\n{_log_text(app)[-500:]}")
    log = _log_text(app)
    if "已取消活跃调试 bundle" in log:
        line = next(ln for ln in log.splitlines() if "已取消活跃调试 bundle" in ln)
        _log(f"  [2] {line.strip()} ok")
    else:
        _log("  [2] no active debug bundle to cancel .................... ok")


async def _drive(app: Any, routine: Callable[[Any, Any], Any]) -> None:
    async with app.run_test(size=(120, 45)) as pilot:
        try:
            await routine(app, pilot)
        except Exception:
            _capture(app)
            raise
        _capture(app)


def _run_journey(*, isolate: bool, routine: Callable[[Any, Any], Any]) -> list[str]:
    import runpy

    import textual.app

    sys.argv = ["demo_tui.py", "--fixture", "--debug"]
    sys.path.insert(0, str(SCRIPTS))

    isolated_root = Path(tempfile.mkdtemp(prefix="tui-journey-")) / "demo-runs"
    failure: list[str] = []

    def fake_run(self: Any, *args: Any, **kwargs: Any) -> None:
        if isolate:
            # Patch the __main__ namespace's adapter so the run is isolated.
            main_module = sys.modules["__main__"]
            real_adapter = main_module.DemoAdapter
            main_module.DemoAdapter = lambda: real_adapter(bundle_root=isolated_root)

        async def drive() -> None:
            try:
                await _drive(self, routine)
            except Exception as exc:  # noqa: BLE001 - harness reports everything
                failure.append(f"{type(exc).__name__}: {exc}")

        asyncio.run(drive())

    textual.app.App.run = fake_run
    runpy.run_path(str(SCRIPTS / "demo_tui.py"), run_name="__main__")
    return failure


def main() -> int:
    global VERBOSE

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--verbose", action="store_true", help="dump both panes after a passing run")
    parser.add_argument(
        "--cancel-active",
        action="store_true",
        help="recovery mode: cancel the workspace's active debug bundle (no isolation) and exit",
    )
    args = parser.parse_args()
    VERBOSE = args.verbose

    if args.cancel_active:
        _log("TUI journey harness: recovery (cancel the active debug bundle)")
        failure = _run_journey(isolate=False, routine=_drive_cancel)
    else:
        _log("TUI journey harness: fixture debugger ladder (runbook-030)")
        _log("executing scripts/demo_tui.py as __main__ (real entry chain)")
        failure = _run_journey(isolate=True, routine=_fixture_debugger_journey)

    exit_code = 1 if failure else 0
    if exit_code == 0:
        _log("JOURNEY OK: every step passed")
        if VERBOSE:
            _log("--- log pane ---")
            _log(PANE["log"])
            _log("--- inspect pane ---")
            _log(PANE["inspect"])
    else:
        _log("JOURNEY FAILED")
        for message in failure:
            _log(f"FAILURE: {message}")
        _log("--- log pane (tail) ---")
        _log(PANE["log"][-1500:] or "(empty)")
        _log("--- inspect pane ---")
        _log(PANE["inspect"] or "(empty)")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
