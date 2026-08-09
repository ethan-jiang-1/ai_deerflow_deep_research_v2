#!/usr/bin/env bash
set -euo pipefail

launcher_directory=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
project_root=$(cd "$launcher_directory/.." && pwd)
question="${DEEP_RESEARCH_QUESTION:-Compare Tavily and Exa for a China-based SaaS team that needs Chinese and English web research. Use official pricing and product documentation, then recommend one provider.}"

export DEERFLOW_DEMO_MODEL=${DEERFLOW_DEMO_MODEL:-deepseek-v4-flash}

cd "$project_root"
make entry-preflight
exec env -u VIRTUAL_ENV PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync --env-file .env --extra operations --extra demo-real \
  python scripts/demo_real.py --scripted --question "$question"
