#!/usr/bin/env bash
set -euo pipefail

launcher_directory=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
project_root=$(cd "$launcher_directory/.." && pwd)
# The default question is phrased so the deterministic comparison-intake seed
# (domain/profile.py) extracts a clean subject pair: list separators (commas)
# after the "compare X and Y" pair make the extractor withhold subjects, and
# HITL1 then blocks the auto-policy run before the first model call.
question="${DEEP_RESEARCH_QUESTION:-Compare Tavily and Exa web search services for a China-based SaaS team doing Chinese and English research with official pricing and product documentation and then recommend one provider.}"

export DEERFLOW_DEMO_MODEL=${DEERFLOW_DEMO_MODEL:-deepseek-v4-flash}

cd "$project_root"
make entry-preflight
# Operator entry policy (BUG-032, same as the Makefile's ENTRY_RUN): this
# launcher never installs (`uv run --locked --no-sync`), so the uv cache is
# irrelevant — UV_NO_CACHE=1 keeps it from touching the global cache, which is
# unreadable in sandboxed environments.
exec env -u VIRTUAL_ENV PYTHONDONTWRITEBYTECODE=1 UV_NO_CACHE=${UV_NO_CACHE:-1} uv run --locked --no-sync --env-file .env --extra operations --extra demo-real \
  python scripts/demo_real.py --embedded-smoke --scripted --question "$question"
