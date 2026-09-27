#!/usr/bin/env bash
# Canonical human entry for the Deep Research debugger workbench.
# Presentation-only launcher (RED-013): resolves the harness root, forwards
# explicit intent to the TUI, and never scans the workspace, selects a latest
# bundle, reads checkpoints, or acquires leases. The TUI/lifecycle validates
# every reference.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PYTHON="$HARNESS_ROOT/.venv/bin/python"
if [ ! -x "$PYTHON" ]; then
  PYTHON="$(command -v python3)"
fi

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  cat <<'USAGE'
Deep Research debugger workbench (local Textual TUI)

Usage:
  run/tui-workflow-debugger.sh --fixture          # debugger workbench over the zero-credential fixture graph
  run/tui-workflow-debugger.sh --fixture --debug  # same (the launcher injects --debug for you)
  run/tui-workflow-debugger.sh --embedded-smoke   # plain all-real TUI (no step/continue; debug driver is fixture-only today)
  run/tui-workflow-debugger.sh --attach <id>      # attach the workbench to this exact bundle (implies --fixture --debug)
  run/tui-workflow-debugger.sh --replay <id>      # read-only trace replay for this exact bundle (no lease, no session)
  run/tui-workflow-debugger.sh --help

Workbench entries (all three reach the same typed action):
  New Run button / question + Enter / --fixture      start a session
  Attach button  / /attach <id>    / --attach <id>   reopen a retained bundle
  Replay button  / /replay <id>    / --replay <id>   read-only trace

Equivalent Make commands (run inside deep_research_harness/):
  make tui-debugger DEBUGGER_ARGS="--fixture"  # same debugger workbench
  make demo-tui-fixture                        # plain fixture graph TUI (no debug driver)
  make demo-tui-embedded-smoke                 # plain all-real smoke TUI

All flags are forwarded to the TUI, which validates every reference through
the lifecycle. This launcher never scans the workspace and never touches
lifecycle state.
USAGE
  exit 0
fi

# The fixture composition lives under src_fixtures/ (the Makefile demo targets
# export the same path). Real compositions do not need it and the TUI keeps
# fixture source undiscovered outside fixture runs.
PYTHONPATH="$HARNESS_ROOT/src_fixtures${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONPATH

# RED-013/RED-014: the launcher's fixture entry IS the debugger workbench.
# Inject the composition and debug flags unless the operator supplied them;
# --attach/--replay are workbench entries, so they imply the fixture debugger.
WANTS_FIXTURE=0
HAS_DEBUG=0
WANTS_INTENT=0
for arg in "$@"; do
  case "$arg" in
    --fixture) WANTS_FIXTURE=1 ;;
    --debug) HAS_DEBUG=1 ;;
    --attach|--replay) WANTS_INTENT=1 ;;
  esac
done
if [ "$WANTS_INTENT" = "1" ] && [ "$WANTS_FIXTURE" = "0" ]; then
  set -- "$@" --fixture
  WANTS_FIXTURE=1
fi
if [ "$WANTS_FIXTURE" = "1" ] && [ "$HAS_DEBUG" = "0" ]; then
  set -- "$@" --debug
fi

exec "$PYTHON" "$HARNESS_ROOT/scripts/demo_tui.py" "$@"
