"""Declarative mutations: each entry removes one guarded behavior.

`make mutation-check` applies one entry at a time, runs its selector, and requires
the selector to go red. An entry whose selector stays green means the guard is
decoration, and the lane fails (change `add-evidence-receipts-and-proof-lanes`).
Every entry here was demonstrated by hand while the debugger work landed.
"""

from __future__ import annotations

from dataclasses import dataclass

DRIVER = "src/deerflow_deep_research/runtime/debug_driver.py"
TUI = "scripts/demo_tui.py"
DEMO_CORE = "scripts/_demo_core.py"


@dataclass(frozen=True)
class Mutation:
    id: str
    file: str
    old: str
    new: str
    selector: str
    removes: str


MUTATIONS: tuple[Mutation, ...] = (
    Mutation(
        id="drive-stops-at-hitl",
        file=DRIVER,
        old='            if posture == "awaiting_hitl" and policy.stop_on_hitl:\n                break\n',
        new="",
        selector="tests/integration/test_debug_driver_matrix.py::test_drive_until_stops_at_the_hitl_boundary_once",
        removes="the drive's stop_on_hitl check (it used to re-enter the waiting node 64 times)",
    ),
    Mutation(
        id="hitl-request-is-carried",
        file=DRIVER,
        old='                session["pending_request"] = _pending_request_view(pending)',
        new='                session["pending_request"] = None',
        selector="tests/integration/test_debug_driver_matrix.py::test_hitl_stop_carries_the_node_authored_request",
        removes="carrying the node-authored request into the session snapshot",
    ),
    Mutation(
        id="observations-are-published",
        file=DRIVER,
        old="    if publisher is None:\n        return",
        new="    return",
        selector="tests/integration/test_debug_driver_matrix.py::test_accepted_commands_keep_the_run_summary_truthful",
        removes="publishing the lifecycle observation (BUG-072: the operator report then lies)",
    ),
    Mutation(
        id="hitl-state-is-logged",
        file=TUI,
        old="        if self._last_debug_hint == key:\n            return",
        new="        return",
        selector="tests/integration/test_demo_tui.py::test_hitl_stop_shows_the_request_and_the_legal_actions",
        removes="stating what a HITL stop waits for in the log",
    ),
    Mutation(
        id="start-run-mode-is-forwarded",
        file=TUI,
        old="        await self._debug_start(question, mode=mode)",
        new="        await self._debug_start(question)",
        selector="tests/integration/test_demo_tui.py::test_run_drives_and_pause_requests_a_boundary_stop",
        removes="forwarding Start Run's mode (it silently ran Start Step)",
    ),
    Mutation(
        id="pause-is-honoured",
        file=DRIVER,
        old='            pause_pending = pause_pending or bool(session["pause_requested"])',
        new="            pause_pending = False",
        selector="tests/integration/test_debug_driver_matrix.py::test_a_pending_pause_makes_the_next_drive_advance_one_boundary",
        removes="honouring a pending pause at the next committed boundary",
    ),
    Mutation(
        id="command-inventory-is-complete",
        file="docs/local-operations.md",
        old="| Run the fixture graph without the TUI | `make demo-fixture-graph` |\n",
        new="| Run the fixture graph without the TUI | `make demo-fixture-graph-typo` |\n",
        selector="tests/contract/test_command_inventory_freshness.py",
        removes="the documented-target-is-defined rule (a typo'd inventory entry must be red)",
    ),
    Mutation(
        id="demo-cli-is-hermetic",
        file=DEMO_CORE,
        old=(
            "    override = _nonblank_environment_value(_DEMO_BUNDLE_ROOT_VAR)\n"
            "    return Path(override) if override is not None else agent_root / _DEMO_BUNDLE_ROOT_NAME"
        ),
        new="    return agent_root / _DEMO_BUNDLE_ROOT_NAME",
        selector="tests/integration/test_demo_cli.py",
        removes="the injectable demo Bundle root (the suite then rides the ambient workspace)",
    ),
)
