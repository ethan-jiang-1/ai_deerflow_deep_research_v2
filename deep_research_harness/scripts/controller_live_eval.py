#!/usr/bin/env python3
"""Manual selected-live runner for the controller direction-loop case.

Builds the real lead-agent composition home (real model endpoint; the API key
comes from the named environment variable and never enters a committed file),
wires the controller live subject, and invokes the selected-live entrypoint
once or as the case's declared repetition series. Manual operations only -
not collected by pytest or routine CI; see docs/cognitive-evaluation-suite.md.

Run from deep_research_harness/ with the environment prepared (make install)
and .env present:

    .venv/bin/python scripts/controller_live_eval.py --mode single
    .venv/bin/python scripts/controller_live_eval.py --mode series
"""

from __future__ import annotations

import argparse
import asyncio
import os
import shutil
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
CONFIGURE_PATH = REPO / "scripts" / "configure.py"
HOME_ROOT = REPO / ".reports" / "controller-live-home"
DEFAULT_MODEL = "deepseek-v4-flash"
PROVIDER = "deepseek"
BASE_URL = "https://api.deepseek.com"


def _load_env() -> None:
    from dotenv import load_dotenv

    load_dotenv(REPO / ".env")


def _import_configure() -> Any:
    import importlib.util

    spec = importlib.util.spec_from_file_location("controller_live_configure", CONFIGURE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _config_text(*, skills_root: Path, model: str, api_key: str) -> str:
    return f"""\
config_version: 19
models:
  - name: {model}
    display_name: Controller live evaluation model
    use: langchain_openai:ChatOpenAI
    model: {model}
    api_key: {api_key}
    base_url: {BASE_URL}
sandbox:
  use: deerflow.sandbox.local:LocalSandboxProvider
tool_groups:
  - name: file:read
tools:
  - name: read_file
    group: file:read
    use: deerflow.sandbox.tools:read_file_tool
skills:
  path: {skills_root}
  container_path: /mnt/skills
  deferred_discovery: false
title:
  enabled: false
memory:
  enabled: false
loop_detection:
  enabled: false
safety_finish_reason:
  enabled: false
read_before_write:
  enabled: false
token_usage:
  enabled: false
agents_api:
  enabled: false
"""


def build_home(*, model: str, api_key: str) -> Any:
    """Materialize the isolated real-model DeerFlow home (mirrors the activation fixture)."""

    if HOME_ROOT.exists():
        shutil.rmtree(HOME_ROOT)
    root = HOME_ROOT
    (root / "backend").mkdir(parents=True)
    skills_root = root / "skills"
    (skills_root / "public").mkdir(parents=True)
    (skills_root / "custom").mkdir(parents=True)
    config_path = root / "config.yaml"
    extensions_path = root / "extensions_config.json"
    home = root / ".deer-flow"
    config_path.write_text(_config_text(skills_root=skills_root, model=model, api_key=api_key), encoding="utf-8")
    extensions_path.write_text('{"mcpServers": {}, "skills": {}}\n', encoding="utf-8")
    env = {
        "DEER_FLOW_CONFIG_PATH": str(config_path),
        "DEER_FLOW_EXTENSIONS_CONFIG_PATH": str(extensions_path),
        "DEER_FLOW_SKILLS_PATH": str(skills_root),
        "DEER_FLOW_HOME": str(home),
        "DEER_FLOW_AUTH_DISABLED": "1",
    }
    os.environ.update(env)
    configured = _import_configure().execute_configuration(root, env, mode="apply", online_detector=lambda: False)
    assert configured.entry_status == "ready", "controller live home configuration failed"
    assert (skills_root / "public" / "deep-research-controller" / "SKILL.md").is_file()

    from deerflow.config import paths as paths_module
    from deerflow.config.app_config import AppConfig, reset_app_config, set_app_config
    from deerflow.config.extensions_config import reset_extensions_config
    from deerflow.sandbox.sandbox_provider import reset_sandbox_provider
    from deerflow.skills.storage import reset_skill_storage

    reset_app_config()
    reset_extensions_config()
    reset_skill_storage()
    reset_sandbox_provider()
    paths_module._paths = None
    app_config = AppConfig.from_file(str(config_path))
    set_app_config(app_config)
    return app_config


async def _run(*, case_id: str, mode: str, price_in: float | None, price_out: float | None) -> int:
    from unittest.mock import patch

    from deerflow_deep_research import tool as public_tool
    from deerflow_deep_research.runtime.evaluation import (
        CaseRegistry,
        CognitiveEvaluationRunner,
        load_case_registry,
        run_selected_live_case,
        run_selected_live_case_series,
    )

    registry = load_case_registry()
    case = registry.resolve(case_id=case_id, version="v1")
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        print("live_model_credentials_missing: DEEPSEEK_API_KEY is not set", file=sys.stderr)
        return 2
    model = os.environ.get("DEERFLOW_DEMO_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    app_config = build_home(model=model, api_key=api_key)
    if case.subject == "public_controller":
        from deerflow_deep_research.runtime.evaluation.controller_live import _control_factory, controller_live_subject

        def control_override(state: str, calls: list) -> Any:
            return patch.object(public_tool, "BundleControl", _control_factory(state, calls))

        subject = controller_live_subject(
            app_config=app_config,
            provider=PROVIDER,
            model=model,
            control_override=control_override,
            price_input_per_mtok=price_in,
            price_output_per_mtok=price_out,
        )
    elif case.subject == "topic_planning":
        from deerflow_deep_research.graph.nodes.topic_planning import NODE_SPEC
        from deerflow_deep_research.runtime.evaluation.topic_planning_live import topic_planning_live_subject

        subject = topic_planning_live_subject(
            node_spec=NODE_SPEC,
            app_config=app_config,
            provider=PROVIDER,
            model=model,
            price_input_per_mtok=price_in,
            price_output_per_mtok=price_out,
        )
    else:
        print(f"evaluation_subject_unavailable: {case.subject}", file=sys.stderr)
        return 2
    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((case,)),
        runs_root=REPO / "evals" / "runs",
        subjects={case.subject: subject},
        available_services=frozenset({"model"}),
    )
    if mode == "series":
        results = await run_selected_live_case_series(runner=runner, case_id=case_id, version="v1", environ=os.environ)
    else:
        results = (await run_selected_live_case(runner=runner, case_id=case_id, version="v1", environ=os.environ),)
    for result in results:
        manifest_path = result.bundle_path / "manifest.json"
        print(f"execution {result.execution_id} status={result.status.value} bundle={result.bundle_path}")
        if manifest_path.is_file():
            import json

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            revision = str(manifest.get("code_revision", ""))[:12]
            print(f"  code_revision={revision} evidence_layer={manifest['evidence_layer']}")
        resources_path = result.bundle_path / "resources.json"
        if resources_path.is_file():
            import json

            resources = json.loads(resources_path.read_text(encoding="utf-8"))
            print(
                f"  model={resources.get('model')} calls={resources.get('model_calls')} "
                f"tokens={resources.get('input_tokens')}in/{resources.get('output_tokens')}out "
                f"cost_usd={resources.get('cost_usd')}"
            )
    return 0 if all(r.status.value == "completed" for r in results) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", default="public-controller-direction-loop", help="registered case id")
    parser.add_argument("--mode", choices=("single", "series"), default="single")
    parser.add_argument("--price-in", type=float, default=None, help="input price per million tokens")
    parser.add_argument("--price-out", type=float, default=None, help="output price per million tokens")
    args = parser.parse_args()
    _load_env()
    return asyncio.run(_run(case_id=args.case, mode=args.mode, price_in=args.price_in, price_out=args.price_out))


if __name__ == "__main__":
    raise SystemExit(main())
