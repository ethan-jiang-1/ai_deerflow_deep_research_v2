.PHONY: install entry-preflight verify lock-check format lint test test-fast test-integration test-workflow test-entry-environment-regression test-live test-unit test-contract test-viability test-durability test-blocking-io test-assets test-intake test-retained-observation test-work-unit test-strict-checkpoint test-duration-policy benchmark-fast prompt-dump prompt-dump-check profile-setup profile-preflight profiles profile-init profile-check profile-dev demo demo-scripted demo-fixture-graph demo-real demo-real-embedded-smoke demo-real-scripted demo-tui demo-tui-embedded-smoke demo-tui-fixture demo-tui-real-auto demo-sessions session-workbench debug-scripted-real-workflow soft-bundle

DEMO_ARGS ?=
# Operator demo/session/soft-bundle/profile entry commands default to no uv cache:
# sandboxed environments return EPERM reading the global uv cache and block every
# such command (BUG-032). Override with UV_NO_CACHE=0. Test/install/build targets
# keep normal caching so the offline gate (UV_OFFLINE=1) can still resolve build
# backends from the cache.
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
verify: lock-check lint test-assets test-fast test-integration test-workflow

# Fixed fixture-graph lifecycle demo. Zero API, no Gateway, config.yaml,
# model credentials, network access, or TUI installation needed.
demo: entry-preflight
	PYTHONPATH=src_fake$${PYTHONPATH:+:$$PYTHONPATH} $(ENTRY_RUN) --extra operations python scripts/demo.py $(DEMO_ARGS)

# Non-interactive equivalent used by CI and quick smoke checks.
demo-scripted: entry-preflight
	PYTHONPATH=src_fake$${PYTHONPATH:+:$$PYTHONPATH} $(ENTRY_RUN) --extra operations python scripts/demo.py --scripted $(DEMO_ARGS)

# Explicit deterministic graph-composition verification.
demo-fixture-graph: entry-preflight
	PYTHONPATH=src_fake$${PYTHONPATH:+:$$PYTHONPATH} $(ENTRY_RUN) --extra operations python scripts/demo_fixture_graph.py $(DEMO_ARGS)

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
demo-tui: entry-preflight
	test -n "$(PROFILE)" || { echo "Usage: make demo-tui PROFILE=demo"; exit 2; }
	$(ENTRY_RUN) $(LOCAL_ENV_ARG) --extra operations --extra demo-real --extra demo-tui python scripts/demo_tui.py --profile "$(PROFILE)" $(DEMO_ARGS)

# Explicit direct local graph smoke visualizer without Gateway observation claims.
demo-tui-embedded-smoke: entry-preflight
	$(ENTRY_RUN) $(LOCAL_ENV_ARG) --extra operations --extra demo-real --extra demo-tui python scripts/demo_tui.py --embedded-smoke $(DEMO_ARGS)

# Credential-free Textual fixture-graph route using the same lifecycle presentation shell.
demo-tui-fixture: entry-preflight
	PYTHONPATH=src_fake$${PYTHONPATH:+:$$PYTHONPATH} $(ENTRY_RUN) --extra operations --extra demo-tui python scripts/demo_tui.py --fixture $(DEMO_ARGS)

# 010 auto TUI: embedded real graph that answers HITL1/HITL2 by graph-owned
# policy (scripted start, default product path). The human watches and never
# types. Companion of demo-tui-embedded-smoke (020 manual, same fixed question).
demo-tui-real-auto: entry-preflight
	$(ENTRY_RUN) $(LOCAL_ENV_ARG) --extra operations --extra demo-real --extra demo-tui python scripts/demo_tui.py --embedded-smoke --auto $(DEMO_ARGS)

demo-sessions: entry-preflight
	PYTHONPATH=src_fake$${PYTHONPATH:+:$$PYTHONPATH} $(ENTRY_RUN) --extra operations python scripts/demo_sessions.py $(DEMO_ARGS)

# Operator-only soft bundle CLI. It is a stateless root handle over existing demo
# and session entry points; never a product lifecycle surface.
soft-bundle: entry-preflight
	PYTHONPATH=src_fake$${PYTHONPATH:+:$$PYTHONPATH} $(ENTRY_RUN) python scripts/soft_bundle.py $(DEMO_ARGS)

# Fixed-profile local operator surface. It is not Gateway, Web, upstream Terminal
# Workbench, or a generic recovery client, and accepts no profile/path authority.
session-workbench: entry-preflight
	PYTHONPATH=src_fake$${PYTHONPATH:+:$$PYTHONPATH} $(ENTRY_RUN) --extra operations --extra demo-tui python scripts/session_workbench.py $(DEMO_ARGS)

# Operator-only scripted-real workflow debug: real production adapters, gates,
# ledger, and persistence with a scripted model and scripted web tools. Zero
# .env, zero network, zero credentials, under 10 seconds. Not a demo-real mode.
debug-scripted-real-workflow: entry-preflight
	PYTHONPATH=src_fake$${PYTHONPATH:+:$$PYTHONPATH} $(ENTRY_RUN) --extra operations python scripts/debug_scripted_real_workflow.py $(DEMO_ARGS)

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
		tests/assets tests/contract tests/domain tests/engine tests/unit tests/graph tests/eval \
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
	uv run python scripts/check_test_durations.py .reports/test-fast.xml $(if $(PYTEST_XDIST),--parallel)

# Verify or re-pin the source-controlled eval control digests. Run --check
# before/after any change to a pinned source file (prompts, domain modules);
# re-pin deliberately with the same command after the change is reviewed.
control-digests-check:
	uv run python scripts/regenerate_control_digests.py --check

benchmark-fast:
	uv run python scripts/benchmark_fast.py

# Opt-in local review projection. The deterministic verification gate does not invoke it.
prompt-dump:
	env -u VIRTUAL_ENV uv run python scripts/prompt_dump.py

# Read-only validation of a reviewer-generated local projection.
prompt-dump-check:
	env -u VIRTUAL_ENV uv run python scripts/prompt_dump.py --check

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
	uv run --no-sync python scripts/check_test_durations.py .reports/test-entry-environment.xml --lane periodic

test-live:
	rm -rf .reports/live
	mkdir -p .reports/live
	uv run $(LOCAL_ENV_ARG) python scripts/live_preflight.py --require-web
	LIVE_REPORT_DIR=.reports/live uv run $(LOCAL_ENV_ARG) $(PYTEST) -m "requires_llm and not release_e2e"

test-assets:
	uv run python scripts/check_test_assets.py

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
