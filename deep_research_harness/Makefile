.PHONY: install governance verify lock-check format lint test test-fast test-integration test-workflow test-live test-unit test-contract test-viability test-durability test-blocking-io test-postgres test-assets test-req-coverage test-intake test-retained-observation test-work-unit test-strict-checkpoint test-duration-policy benchmark-fast prompt-dump prompt-dump-check profile-setup profile-preflight profiles profile-init profile-check profile-dev demo demo-scripted demo-real demo-real-scripted demo-tui demo-tui-fake demo-sessions session-workbench

DEMO_ARGS ?=
LOCAL_ENV_ARG := $(if $(wildcard .env),--env-file .env,)
PYTEST := python -m pytest

install:
	uv sync --locked --extra operations --extra demo-tui

PROFILE_RUN = env -u VIRTUAL_ENV uv run --locked --no-sync --extra operations python scripts/local_profiles.py

profile-setup:
	$(MAKE) -C ../deerflow install
	env -u VIRTUAL_ENV uv sync --locked --extra operations

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

governance:
	python3 ../openspec/governance/check_project_reqs.py ..
	python3 ../openspec/governance/check_project_specs.py ..
	python3 ../openspec/governance/check_project_architecture.py ..
	python3 ../openspec/governance/check_agent_charter.py ..

verify: export UV_NO_SYNC := 1
verify: governance lock-check lint test-assets test-req-coverage test-fast test-integration test-workflow

# Standalone fake lifecycle demo. Zero API, no Gateway, config.yaml,
# model credentials, network access, or TUI installation needed.
demo:
	env -u VIRTUAL_ENV PYTHONPATH=src_fake$${PYTHONPATH:+:$$PYTHONPATH} uv run --extra operations python scripts/demo.py $(DEMO_ARGS)

# Non-interactive equivalent used by CI and quick smoke checks.
demo-scripted:
	env -u VIRTUAL_ENV PYTHONPATH=src_fake$${PYTHONPATH:+:$$PYTHONPATH} uv run --extra operations python scripts/demo.py --scripted $(DEMO_ARGS)

# Real-mode CLI — full 11-phase pipeline with actual LLM + Tavily web tools.
# Requires one model credential plus TAVILY_API_KEY.
demo-real:
	env -u VIRTUAL_ENV uv run $(LOCAL_ENV_ARG) --extra operations --extra demo-real python scripts/demo_real.py $(DEMO_ARGS)

# Non-interactive real-mode for CI (requires credentials).
demo-real-scripted:
	env -u VIRTUAL_ENV uv run $(LOCAL_ENV_ARG) --extra operations --extra demo-real python scripts/demo_real.py --scripted $(DEMO_ARGS)

# Standalone real-mode TUI. Requires model + Tavily credentials.
# This is not the production DeerFlow Terminal Workbench or generic
# human-input integration.
demo-tui:
	env -u VIRTUAL_ENV uv run $(LOCAL_ENV_ARG) --extra operations --extra demo-real --extra demo-tui python scripts/demo_tui.py $(DEMO_ARGS)

# Credential-free Textual route using the same lifecycle presentation shell.
demo-tui-fake:
	env -u VIRTUAL_ENV PYTHONPATH=src_fake$${PYTHONPATH:+:$$PYTHONPATH} uv run --extra operations --extra demo-tui python scripts/demo_tui.py --fake $(DEMO_ARGS)

demo-sessions:
	env -u VIRTUAL_ENV PYTHONPATH=src_fake$${PYTHONPATH:+:$$PYTHONPATH} uv run --extra operations python scripts/demo_sessions.py $(DEMO_ARGS)

# Fixed-profile local operator surface. It is not Gateway, Web, upstream Terminal
# Workbench, or a generic recovery client, and accepts no profile/path authority.
session-workbench: profile-preflight
	env -u VIRTUAL_ENV PYTHONPATH=src_fake$${PYTHONPATH:+:$$PYTHONPATH} uv run --locked --no-sync --extra operations --extra demo-tui python scripts/session_workbench.py $(DEMO_ARGS)

lock-check:
	uv lock --check

format:
	uv run ruff check . --fix
	uv run ruff format .

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run --extra operations --extra demo-tui $(PYTEST) -m "not (requires_llm or release_e2e or postgres)"

test-fast:
	mkdir -p .reports
	uv run --extra operations $(PYTEST) \
		tests/assets tests/contract tests/domain tests/engine tests/unit tests/graph tests/eval \
		-m "not (requires_llm or release_e2e or postgres or workflow)" \
		--durations=20 --junitxml=.reports/test-fast.xml

test-intake:
	@started=$$(date +%s); echo "intake: HITL profile parsing and lifecycle"; uv run --extra operations $(PYTEST) tests/domain/test_profile.py tests/graph/test_hitl1_node.py tests/integration/test_hitl1_lifecycle.py; status=$$?; echo "intake elapsed: $$(( $$(date +%s) - started ))s"; exit $$status

test-retained-observation:
	@started=$$(date +%s); echo "retained-observation: run summary and event journal"; uv run --extra operations $(PYTEST) tests/unit/test_run_session_store.py tests/contract/test_run_session_contract.py; status=$$?; echo "retained-observation elapsed: $$(( $$(date +%s) - started ))s"; exit $$status

test-work-unit:
	@started=$$(date +%s); echo "work-unit: ledger and controller boundaries"; uv run --extra operations $(PYTEST) tests/domain/test_submission_ledger.py tests/graph/test_work_unit_component.py; status=$$?; echo "work-unit elapsed: $$(( $$(date +%s) - started ))s"; exit $$status

test-strict-checkpoint:
	@started=$$(date +%s); echo "strict-checkpoint: msgpack compatibility"; LANGGRAPH_STRICT_MSGPACK=true uv run --extra operations $(PYTEST) tests/unit/test_checkpoint_msgpack.py; status=$$?; echo "strict-checkpoint elapsed: $$(( $$(date +%s) - started ))s"; exit $$status

test-duration-policy:
	uv run --extra operations python scripts/check_test_durations.py .reports/test-fast.xml

benchmark-fast:
	uv run --extra operations python scripts/benchmark_fast.py

# Opt-in local review projection. The deterministic verification gate does not invoke it.
prompt-dump:
	env -u VIRTUAL_ENV uv run --extra operations python scripts/prompt_dump.py

# Read-only validation of a reviewer-generated local projection.
prompt-dump-check:
	env -u VIRTUAL_ENV uv run --extra operations python scripts/prompt_dump.py --check

test-integration:
	uv run --extra operations --extra demo-tui $(PYTEST) \
		tests/integration tests/blocking_io \
		-m "not (requires_llm or release_e2e or postgres or workflow)"

test-workflow:
	uv run --extra operations $(PYTEST) \
		tests \
		-m "workflow and not (requires_llm or release_e2e or postgres)"

test-live:
	rm -rf .reports/live
	mkdir -p .reports/live
	uv run $(LOCAL_ENV_ARG) --extra operations python scripts/live_preflight.py --require-web
	LIVE_REPORT_DIR=.reports/live uv run $(LOCAL_ENV_ARG) --extra operations $(PYTEST) -m "requires_llm and not release_e2e"

test-assets:
	uv run --extra operations python scripts/check_test_assets.py

test-req-coverage:
	python3 ../openspec/governance/check_project_req_coverage.py ..

test-unit:
	uv run --extra operations $(PYTEST) tests/unit

test-contract:
	uv run --extra operations $(PYTEST) tests/contract

test-viability:
	uv run --extra operations $(PYTEST) \
		tests/integration/test_reflected_runtime_viability.py \
		tests/integration/test_cancellation_viability.py

# File-backed SQLite provider-reopen + real subprocess-restart durability.
# Requires no database server and no Docker.
test-durability:
	uv run --extra operations $(PYTEST) tests/integration/test_provider_durability.py

# Deterministic event-loop guard for lifecycle dispatch, nested graph Send
# fan-in, provider cleanup, and outer Command projection.
test-blocking-io:
	uv run --extra operations $(PYTEST) tests/blocking_io

# Postgres durability profile is deferred (see openspec/config.yaml tech-stack
# decisions). This target runs the postgres-marked tests, which skip until a
# later change adds the isolated Postgres test service and Compose profile.
test-postgres:
	uv run --extra operations $(PYTEST) -m postgres
