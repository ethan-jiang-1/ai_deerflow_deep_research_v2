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
  run/tui-workflow-debugger.sh                    # start the debugger TUI (choose composition inside)
  run/tui-workflow-debugger.sh --fixture          # zero-credential fixture graph
  run/tui-workflow-debugger.sh --embedded-smoke   # local all-real smoke route
  run/tui-workflow-debugger.sh --attach <id>      # attach to this exact bundle (lifecycle-validated)
  run/tui-workflow-debugger.sh --replay <id>      # read-only replay for this exact bundle
  run/tui-workflow-debugger.sh --help

Equivalent Make commands (run inside deep_research_harness/):
  make demo-tui                # default TUI
  make demo-tui-fixture        # fixture graph TUI
  make demo-tui-embedded-smoke # all-real smoke TUI

All flags are forwarded verbatim to the TUI, which validates every reference
through the lifecycle. This launcher never scans the workspace and never
touches lifecycle state.
USAGE
  exit 0
fi

exec "$PYTHON" "$HARNESS_ROOT/scripts/demo_tui.py" "$@"
