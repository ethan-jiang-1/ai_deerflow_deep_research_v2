.PHONY: install entry-preflight verify lock-check format lint test test-fast test-integration test-workflow test-entry-environment-regression test-live test-unit test-contract test-viability test-durability test-blocking-io test-assets test-intake test-retained-observation test-work-unit test-strict-checkpoint test-duration-policy test-changed benchmark-fast prompt-dump prompt-dump-check profile-setup profile-preflight profiles profile-init profile-check profile-dev demo demo-scripted demo-fixture-graph demo-real demo-real-embedded-smoke demo-real-scripted demo-tui demo-tui-embedded-smoke demo-tui-fixture demo-tui-real-auto demo-sessions session-workbench debug-scripted-real-workflow soft-bundle demo-workspace-report demo-clean tui-experiences debugger-proof

DEMO_ARGS ?=
# BUG-032 conclusion: sandboxed environments (DSH workspace-write) EPERM on the
# global uv cache (~/.cache/uv), so EVERY uv invocation in this Makefile uses the
# git-ignored workspace-local .uv-cache instead — installs, lock checks, lint,
# tests, and the wheel-build contract test. The global cache is never read or
# written. On a fresh clone (cold .uv-cache) warm it once online:
#   UV_CACHE_DIR=$PWD/.uv-cache uv build --wheel --out-dir /tmp/warmup
# Operator entry commands additionally set UV_NO_CACHE=1 (their `uv run
# --locked --no-sync` never installs, so the cache is irrelevant to them).
# Override with UV_NO_CACHE=0 if a cache-enabled entry run is wanted.
export UV_CACHE_DIR := $(CURDIR)/.uv-cache
UV_NO_CACHE ?= 1
# Real demo targets default to the standard demo profile so runbook/script callers
# that pass only DEMO_ARGS still launch; an explicitly empty PROFILE= is rejected.
PROFILE ?= demo
LOCAL_ENV_ARG := $(if $(wildcard .env),--env-file .env,)
PYTEST := python -m pytest
# 默认并行（-n 4；CLS-052 第三轮 L2 review 完成：静态扫描无共享状态风险，
# 两次 -n 4 全绿。实测 -n 4 三 lane 均优于串行；-n auto 在 8 核机上对
# workflow lane 过订阅更慢，故用固定 -n 4 而非 auto）。需要串行时显式
# `make verify PYTEST_XDIST=`（空）。
PYTEST_XDIST ?= -n 4
ENTRY_RUN = PYTHONDONTWRITEBYTECODE=1 env -u VIRTUAL_ENV UV_NO_CACHE=$(UV_NO_CACHE) uv run --locked --no-sync
ENTRY_REQUIRED_DISTRIBUTIONS = python-dotenv ruamel.yaml textual tavily-python
ENTRY_SETUP_MESSAGE = Command environment is not prepared. Run 'make install' from deep_research_harness/.

install:
	env -u VIRTUAL_ENV uv sync --locked --extra operations --extra demo-tui --extra demo-real

entry-preflight:
	@test -x .venv/bin/python && .venv/bin/python -c 'from importlib.metadata import version; [version(name) for name in "$(ENTRY_REQUIRED_DISTRIBUTIONS)".split()]' >/dev/null 2>&1 || { echo "$(ENTRY_SETUP_MESSAGE)"; exit 2; }

PROFILE_RUN = PYTHONDONTWRITEBYTECODE=1 env -u VIRTUAL_ENV UV_NO_CACHE=$(UV_NO_CACHE) uv run --locked --no-sync --extra operations python scripts/local_profiles.py

profile-setup:
	$(MAKE) -C ../deerflow install
	$(MAKE) install

profile-preflight:
	@test -d .venv || { echo "Profile setup is required. Run 'make profile-setup' from deep_research_harness/."; exit 2; }

profiles: profile-preflight
	$(PROFILE_RUN) list

profile-init: profile-preflight
	test -n "$(PROFILE)" || { echo "Usage: make profile-init PROFILE=demo"; exit 2; }
	$(PROFILE_RUN) init "$(PROFILE)"

profile-check: profile-preflight
	test -n "$(PROFILE)" || { echo "Usage: make profile-check PROFILE=demo"; exit 2; }
	$(PROFILE_RUN) check "$(PROFILE)"

profile-dev: profile-preflight
	test -n "$(PROFILE)" || { echo "Usage: make profile-dev PROFILE=demo"; exit 2; }
	$(PROFILE_RUN) launch "$(PROFILE)"

verify: export UV_NO_SYNC := 1
# The wheel-build contract test resolves its hatchling backend from the
# workspace-local UV_CACHE_DIR exported above; it works offline once that
# cache is warm (see the warm-up note at the top of this file).
verify: lock-check lint test-assets test-fast test-integration test-workflow

# Fixed fixture-graph lifecycle demo. Zero API, no Gateway, config.yaml,
# model credentials, network access, or TUI installation needed.
demo: entry-preflight
	PYTHONPATH=src_fixtures$${PYTHONPATH:+:$$PYTHONPATH} $(ENTRY_RUN) --extra operations python scripts/demo.py $(DEMO_ARGS)

# Non-interactive equivalent used by CI and quick smoke checks.
demo-scripted: entry-preflight
	PYTHONPATH=src_fixtures$${PYTHONPATH:+:$$PYTHONPATH} $(ENTRY_RUN) --extra operations python scripts/demo.py --scripted $(DEMO_ARGS)

# Explicit deterministic graph-composition verification.
demo-fixture-graph: entry-preflight
	PYTHONPATH=src_fixtures$${PYTHONPATH:+:$$PYTHONPATH} $(ENTRY_RUN) --extra operations python scripts/demo_fixture_graph.py $(DEMO_ARGS)

# Default real CLI: selected local Gateway observer. The launched profile owns provider credentials.
demo-real: entry-preflight
	test -n "$(PROFILE)" || { echo "Usage: make demo-real PROFILE=demo"; exit 2; }
	$(ENTRY_RUN) $(LOCAL_ENV_ARG) --extra operations --extra demo-real python scripts/demo_real.py --profile "$(PROFILE)" $(DEMO_ARGS)

# Explicit direct local graph smoke route. It makes no Gateway history, trace, liveness, or forwarding claim.
demo-real-embedded-smoke: entry-preflight
	$(ENTRY_RUN) $(LOCAL_ENV_ARG) --extra operations --extra demo-real python scripts/demo_real.py --embedded-smoke $(DEMO_ARGS)

# Explicit non-interactive embedded smoke route; retained for local calibration only.
demo-real-scripted: entry-preflight
	$(ENTRY_RUN) $(LOCAL_ENV_ARG) --extra operations --extra demo-real python scripts/demo_real.py --embedded-smoke --scripted $(DEMO_ARGS)

# Default real TUI: selected local Gateway observer. This is not the production Terminal Workbench.
# Canonical debugger workbench entry (thin wrapper over the TUI entry; RED-013).
tui-debugger:
	./run/tui-workflow-debugger.sh $(DEBUGGER_ARGS)

# Headless self-verification harness for the interactive TUI entry chain.
# Executes the real script as __main__ (PYTHONPATH stripped) and drives the
# runbook-030 debugger ladder with per-step semantic assertions. Agents MUST
# run this before handing any TUI path to an operator; it is also wired into
# `make verify`. JOURNEY_ARGS="--cancel-active" abandons a leftover active
# debug bundle (recovery after an interrupted session).
tui-experiences:
	@env -u PYTHONPATH $(ENTRY_RUN) --extra operations --extra demo-tui python scripts/tui_experience_suite.py $(EXPERIENCE_ARGS)

debugger-proof:
	@echo "== 1/5 driver matrix (closed commands, lease, stop policy, pending request) =="
	@env -u PYTHONPATH $(ENTRY_RUN) --extra operations --extra demo-tui python -m pytest tests/integration/test_debug_driver_matrix.py -q
	@echo "== 2/5 debugger entry contract (launcher, PYTHONPATH seam, harness subprocess) =="
	@env -u PYTHONPATH $(ENTRY_RUN) --extra operations --extra demo-tui python -m pytest tests/integration/test_debugger_entry.py -q
	@echo "== 3/5 workbench tests (UX, layout tiers, panes, palette) =="
	@env -u PYTHONPATH $(ENTRY_RUN) --extra operations --extra demo-tui python -m pytest tests/integration/test_demo_tui.py -q
	@echo "== 4/5 operator journey harness (real script as __main__, dwell at every checkpoint) =="
	@env -u PYTHONPATH $(ENTRY_RUN) --extra operations --extra demo-tui python scripts/tui_journey_probe.py
	@echo "== 5/5 operator experience suite (15 end-to-end journeys) =="
	@env -u PYTHONPATH $(ENTRY_RUN) --extra operations --extra demo-tui python scripts/tui_experience_suite.py
	@echo "debugger-proof: every lane exited 0"

tui-journey:
	env -u PYTHONPATH $(ENTRY_RUN) --extra operations --extra demo-tui python scripts/tui_journey_probe.py $(JOURNEY_ARGS)

demo-tui: entry-preflight
	test -n "$(PROFILE)" || { echo "Usage: make demo-tui PROFILE=demo"; exit 2; }
	$(ENTRY_RUN) $(LOCAL_ENV_ARG) --extra operations --extra demo-real --extra demo-tui python scripts/demo_tui.py --profile "$(PROFILE)" $(DEMO_ARGS)

# Explicit direct local graph smoke visualizer without Gateway observation claims.
demo-tui-embedded-smoke: entry-preflight
	$(ENTRY_RUN) $(LOCAL_ENV_ARG) --extra operations --extra demo-real --extra demo-tui python scripts/demo_tui.py --embedded-smoke $(DEMO_ARGS)

# Credential-free Textual fixture-graph route using the same lifecycle presentation shell.
demo-tui-fixture: entry-preflight
	PYTHONPATH=src_fixtures$${PYTHONPATH:+:$$PYTHONPATH} $(ENTRY_RUN) --extra operations --extra demo-tui python scripts/demo_tui.py --fixture $(DEMO_ARGS)

# 010 auto TUI: embedded real graph that answers HITL1/HITL2 by graph-owned
# policy (scripted start, default product path). The human watches and never
# types. Companion of demo-tui-embedded-smoke (020 manual, same fixed question).
demo-tui-real-auto: entry-preflight
	$(ENTRY_RUN) $(LOCAL_ENV_ARG) --extra operations --extra demo-real --extra demo-tui python scripts/demo_tui.py --embedded-smoke --auto $(DEMO_ARGS)

demo-sessions: entry-preflight
	PYTHONPATH=src_fixtures$${PYTHONPATH:+:$$PYTHONPATH} $(ENTRY_RUN) --extra operations python scripts/demo_sessions.py $(DEMO_ARGS)

# Operator-only soft bundle CLI. It is a stateless root handle over existing demo
# and session entry points; never a product lifecycle surface.
soft-bundle: entry-preflight
	PYTHONPATH=src_fixtures$${PYTHONPATH:+:$$PYTHONPATH} $(ENTRY_RUN) python scripts/soft_bundle.py $(DEMO_ARGS)

# Read-only demo workspace inventory (bundles, lifecycle status, sizes; operator
# view, not a lifecycle authority; DPL-014).
demo-workspace-report: entry-preflight
	PYTHONPATH=src_fixtures$${PYTHONPATH:+:$$PYTHONPATH} $(ENTRY_RUN) python scripts/soft_bundle.py workspace-report

# Guarded demo workspace cleanup: dry-run by default; CONFIRM=1 deletes only
# terminal bundles (never non-terminal/resumable ones); `DEMO_ARGS="--logs"`
# also cleans the logs subtree under the same confirmation gate.
demo-clean: entry-preflight
	PYTHONPATH=src_fixtures$${PYTHONPATH:+:$$PYTHONPATH} $(ENTRY_RUN) python scripts/soft_bundle.py workspace-clean $(DEMO_ARGS)

# Fixed-profile local operator surface. It is not Gateway, Web, upstream Terminal
# Workbench, or a generic recovery client, and accepts no profile/path authority.
session-workbench: entry-preflight
	PYTHONPATH=src_fixtures$${PYTHONPATH:+:$$PYTHONPATH} $(ENTRY_RUN) --extra operations --extra demo-tui python scripts/session_workbench.py $(DEMO_ARGS)

# Operator-only scripted-real workflow debug: real production adapters, gates,
# ledger, and persistence with a scripted model and scripted web tools. Zero
# .env, zero network, zero credentials, under 10 seconds. Not a demo-real mode.
debug-scripted-real-workflow: entry-preflight
	PYTHONPATH=src_fixtures$${PYTHONPATH:+:$$PYTHONPATH} $(ENTRY_RUN) --extra operations python scripts/debug_scripted_real_workflow.py $(DEMO_ARGS)

lock-check:
	uv lock --check

format:
	uv run ruff check . --fix
	uv run ruff format .

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run $(PYTEST) $(PYTEST_XDIST) -m "not (requires_llm or release_e2e or periodic)"

test-fast:
	mkdir -p .reports
	uv run $(PYTEST) $(PYTEST_XDIST) \
		tests/contract tests/domain tests/engine tests/unit tests/graph tests/eval \
		-m "not (requires_llm or release_e2e or periodic or workflow)" \
		--durations=20 --junitxml=.reports/test-fast.xml

test-intake:
	@started=$$(date +%s); echo "intake: HITL profile parsing and lifecycle"; uv run $(PYTEST) tests/domain/test_profile.py tests/graph/test_hitl1_node.py tests/integration/test_hitl1_lifecycle.py; status=$$?; echo "intake elapsed: $$(( $$(date +%s) - started ))s"; exit $$status

test-retained-observation:
	@started=$$(date +%s); echo "retained-observation: run summary and event journal"; uv run $(PYTEST) tests/unit/test_run_session_store.py tests/contract/test_run_session_contract.py; status=$$?; echo "retained-observation elapsed: $$(( $$(date +%s) - started ))s"; exit $$status

test-work-unit:
	@started=$$(date +%s); echo "work-unit: ledger and controller boundaries"; uv run $(PYTEST) tests/domain/test_submission_ledger.py tests/graph/test_work_unit_component.py; status=$$?; echo "work-unit elapsed: $$(( $$(date +%s) - started ))s"; exit $$status

test-strict-checkpoint:
	@started=$$(date +%s); echo "strict-checkpoint: serde and current-only checkpoint admission"; LANGGRAPH_STRICT_MSGPACK=true uv run $(PYTEST) tests/unit/test_checkpoint_msgpack.py tests/unit/test_retained_checkpoint_cutover.py tests/unit/test_state_contracts.py tests/unit/test_bundle_graph_journal.py tests/engine/test_gate_kernel.py; status=$$?; echo "strict-checkpoint elapsed: $$(( $$(date +%s) - started ))s"; exit $$status

test-duration-policy:
	uv run python scripts/checks/check_test_durations.py .reports/test-fast.xml $(if $(PYTEST_XDIST),--parallel)

# Local iteration speed-up (L8): run only tests touched by the working-tree diff,
# optionally plus the previously failed set. NOT part of verify/CI — the gate
# stays the full lane selection. Usage: `make test-changed` or
# `make test-changed ARGS="--last-failed --base HEAD~1"`.
test-changed:
	uv run python scripts/checks/test_changed.py $(ARGS)

# Verify or re-pin the source-controlled eval control digests. Run --check
# before/after any change to a pinned source file (prompts, domain modules);
# re-pin deliberately with the same command after the change is reviewed.
control-digests-check:
	uv run python scripts/checks/regenerate_control_digests.py --check

benchmark-fast:
	uv run python scripts/checks/benchmark_fast.py

# Opt-in local review projection. The deterministic verification gate does not invoke it.
prompt-dump:
	env -u VIRTUAL_ENV uv run python scripts/checks/prompt_dump.py

# Read-only validation of a reviewer-generated local projection.
prompt-dump-check:
	env -u VIRTUAL_ENV uv run python scripts/checks/prompt_dump.py --check

test-integration:
	uv run $(PYTEST) $(PYTEST_XDIST) \
		tests/integration tests/blocking_io \
		-m "not (requires_llm or release_e2e or periodic or workflow)"

test-workflow:
	uv run $(PYTEST) $(PYTEST_XDIST) \
		tests \
		-m "workflow and not (requires_llm or release_e2e or periodic)"

# Maintained clean-copy public-entry evidence. It intentionally stays outside the
# rapid verify aggregate because each scenario creates and installs a full copy.
test-entry-environment-regression:
	mkdir -p .reports
	UV_OFFLINE=1 uv run --no-sync $(PYTEST) \
		tests/scenarios_periodic \
		-m "periodic and not (requires_llm or release_e2e)" \
		--durations=20 --junitxml=.reports/test-entry-environment.xml
	uv run --no-sync python scripts/checks/check_test_durations.py .reports/test-entry-environment.xml --lane periodic

test-live:
	rm -rf .reports/live
	mkdir -p .reports/live
	uv run $(LOCAL_ENV_ARG) python scripts/live_preflight.py --require-web
	LIVE_REPORT_DIR=.reports/live uv run $(LOCAL_ENV_ARG) $(PYTEST) -m "requires_llm and not release_e2e"

test-assets:
	uv run python scripts/checks/check_test_assets.py

test-unit:
	uv run $(PYTEST) tests/unit

test-contract:
	uv run $(PYTEST) tests/contract

test-viability:
	uv run $(PYTEST) \
		tests/integration/test_reflected_runtime_viability.py \
		tests/integration/test_cancellation_viability.py

# File-backed SQLite provider-reopen + real subprocess-restart durability.
# Requires no database server and no Docker.
test-durability:
	uv run $(PYTEST) tests/integration/test_provider_durability.py

# Deterministic event-loop guard for lifecycle dispatch, nested graph Send
# fan-in, provider cleanup, and outer Command projection.
test-blocking-io:
	uv run $(PYTEST) tests/blocking_io
