#!/usr/bin/env bash
# Canonical human entry for the Deep Research debugger workbench.
# Presentation-only launcher (RED-013): resolves the harness root, forwards
# explicit intent to the TUI, and never scans the workspace, selects a latest
# bundle, reads checkpoints, or acquires leases. The TUI/lifecycle validates
# every reference.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# DEBUGGER_PYTHON is a test seam: it lets a regression test observe the exact
# argv this launcher forwards without launching the TUI. Unset in normal use.
if [ -n "${DEBUGGER_PYTHON:-}" ]; then
  PYTHON="$DEBUGGER_PYTHON"
else
  PYTHON="$HARNESS_ROOT/.venv/bin/python"
  if [ ! -x "$PYTHON" ]; then
    PYTHON="$(command -v python3)"
  fi
fi

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  cat <<'USAGE'
Deep Research debugger workbench (local Textual TUI)

Usage:
  run/tui-workflow-debugger.sh                    # composition chooser (interactive) / fixture default (non-interactive)
  run/tui-workflow-debugger.sh --fixture          # debugger over the zero-credential fixture graph
  run/tui-workflow-debugger.sh --embedded-smoke   # debugger over the ALL-REAL graph (needs .env credentials + network)
  run/tui-workflow-debugger.sh --attach <id>      # attach the workbench to this exact bundle (fixture by default)
  run/tui-workflow-debugger.sh --replay <id>      # read-only trace replay for this exact bundle (no lease, no session)
  run/tui-workflow-debugger.sh --help

Every composition below starts the DEBUGGER: the launcher injects --debug for
the chosen composition, so step/continue, /context, /files, /attach and
/replay are available over fixture or all-real graphs alike.

Environment (non-interactive composition selection):
  DEBUGGER_COMPOSITION=fixture|embedded-smoke|gateway   explicit composition (default: fixture)
  DEBUGGER_PROFILE=<name>                               required by the gateway composition

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

# RED-013 composition chooser. A bare invocation must not fall through to
# Gateway mode with no profile: interactive callers get a menu, non-interactive
# callers take the documented default (the fixture debugger, zero credentials)
# without reading stdin, and DEBUGGER_COMPOSITION selects explicitly for scripts.
CHOOSE_FIXTURE=0
COMPOSITION="${DEBUGGER_COMPOSITION:-}"
if [ "$#" -eq 0 ]; then
  if [ -t 0 ]; then
    cat <<'MENU'
Select a debugger composition:
  1) fixture debugger  (zero credentials, recommended)
  2) embedded smoke    (ALL-REAL graph: real model + web tools)
  3) gateway observer  (needs a ready local profile: DEBUGGER_PROFILE=<name>)
MENU
    read -r -p "Choice [1]: " composition_choice
    case "${composition_choice:-1}" in
      2) COMPOSITION="embedded-smoke" ;;
      3) COMPOSITION="gateway" ;;
      *) COMPOSITION="fixture" ;;
    esac
  elif [ -z "$COMPOSITION" ]; then
    # Non-interactive caller with no explicit choice: documented default.
    COMPOSITION="fixture"
  fi
fi
case "$COMPOSITION" in
  "")
    # Explicit composition flags were supplied; leave the argv untouched.
    ;;
  fixture)
    CHOOSE_FIXTURE=1
    ;;
  embedded|embedded-smoke)
    set -- "$@" --embedded-smoke
    ;;
  gateway|profile)
    if [ -z "${DEBUGGER_PROFILE:-}" ]; then
      echo "gateway composition needs DEBUGGER_PROFILE=<name> (or pass --profile <name>)" >&2
      exit 2
    fi
    set -- "$@" --profile "$DEBUGGER_PROFILE"
    ;;
  *)
    echo "unknown DEBUGGER_COMPOSITION: $COMPOSITION (expected fixture, embedded-smoke, or gateway)" >&2
    exit 2
    ;;
esac

# RED-013/RED-014: this launcher IS the debugger, over whichever composition the
# operator chose. Inject the composition default and --debug unless supplied;
# --attach/--replay are workbench entries and default to the fixture debugger.
# Both `--attach <id>` and argparse's `--attach=<id>` spellings count.
WANTS_FIXTURE="$CHOOSE_FIXTURE"
WANTS_DEBUGGER="$CHOOSE_FIXTURE"
HAS_FIXTURE=0
HAS_EMBEDDED=0
HAS_DEBUG=0
WANTS_INTENT=0
for arg in "$@"; do
  case "$arg" in
    --fixture) HAS_FIXTURE=1; WANTS_FIXTURE=1; WANTS_DEBUGGER=1 ;;
    --embedded-smoke) HAS_EMBEDDED=1; WANTS_DEBUGGER=1 ;;
    --debug) HAS_DEBUG=1 ;;
    --attach|--attach=*|--replay|--replay=*) WANTS_INTENT=1 ;;
  esac
done
if [ "$WANTS_INTENT" = "1" ] && [ "$HAS_FIXTURE" = "0" ] && [ "$HAS_EMBEDDED" = "0" ]; then
  WANTS_FIXTURE=1
  WANTS_DEBUGGER=1
fi
if [ "$WANTS_FIXTURE" = "1" ] && [ "$HAS_FIXTURE" = "0" ]; then
  set -- "$@" --fixture
fi
if [ "$WANTS_DEBUGGER" = "1" ] && [ "$HAS_DEBUG" = "0" ]; then
  set -- "$@" --debug
fi
# The fixture composition lives under src_fixtures/ and is enabled ONLY for the
# fixture entry (the Makefile demo-tui-fixture target does the same). Real
# compositions must never discover fixture source; the TUI also self-enables it
# in fixture mode, so this is the caller-side half of that contract.
if [ "$WANTS_FIXTURE" = "1" ]; then
  PYTHONPATH="$HARNESS_ROOT/src_fixtures${PYTHONPATH:+:$PYTHONPATH}"
  export PYTHONPATH
fi

exec "$PYTHON" "$HARNESS_ROOT/scripts/demo_tui.py" "$@"
