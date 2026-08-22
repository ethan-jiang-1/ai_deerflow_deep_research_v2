#!/usr/bin/env python3
"""Validate incident mappings against the deterministic pytest collection.

@impl EVH-006
@impl EVH-009
@impl WFO-002
@impl CPE-004
@impl EVH-017
@impl EVH-023
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from deerflow_deep_research.graph.registry import load_research_node_specs  # noqa: E402
from deerflow_deep_research.graph.topology import LOGICAL_NODES  # noqa: E402
from scripts.check_node_workflows import (  # noqa: E402
    WorkflowReaderError,
    load_reader_inventory,
)
from tests.assets.cognitive_program_board import (  # noqa: E402
    COGNITIVE_PROGRAM_BOARD,
    CognitiveProgramBoardError,
    CognitiveProgramEvidenceBoard,
    validate_cognitive_program_board,
)
from tests.assets.evidence import (  # noqa: E402
    EVIDENCE_CLAIMS,
    EvidenceClaimError,
    FocusedSelection,
    TestEvidenceClaim,
    claim_index,
    validate_claim_selections,
    validate_inventory_claim_references,
)
from tests.assets.fault_matrix import CRITICAL_FAULTS, FaultMatrixError, validate_fault_matrix  # noqa: E402
from tests.assets.inventory import INCIDENTS, CoverageError, validate_incident_coverage  # noqa: E402
from tests.assets.node_agent_capabilities import (  # noqa: E402
    COHORT_EVIDENCE,
    CapabilityEvidenceRow,
    validate_cohort_evidence,
)
from tests.assets.node_conformance import (  # noqa: E402
    NODE_CONFORMANCE,
    NodeConformance,
    NodeConformanceError,
    validate_node_conformance,
)
from tests.assets.provider_shapes import (  # noqa: E402
    LIVE_DISCOVERY_DISPOSITIONS,
    RELEASE_DISCOVERY_DISPOSITIONS_01_14,
    RELEASE_DISCOVERY_DISPOSITIONS_15_25,
    load_provider_shape_archive,
    validate_provider_shape_catalog,
)
from tests.assets.requirement_evidence import (  # noqa: E402
    CONSOLIDATION_DECISIONS,
    REQUIREMENT_EVIDENCE_POLICY,
    REQUIREMENT_IMPACTS,
    ConsolidationDecision,
    RequirementEvidenceError,
    RequirementImpact,
    collected_deterministic_impl_ids,
    validate_consolidation_decisions,
    validate_requirement_evidence,
    validate_requirement_impacts,
)
from tests.assets.selection import (  # noqa: E402
    DETERMINISTIC_EXCLUDE,
    FAST_EXPRESSION,
    FAST_PATHS,
    INTEGRATION_EXPRESSION,
    INTEGRATION_PATHS,
    LIVE_EXPRESSION,
    LIVE_PATHS,
    PERIODIC_EXPRESSION,
    PERIODIC_PATHS,
    WORKFLOW_EXPRESSION,
    WORKFLOW_PATHS,
)
from tests.assets.workflow_nodes import (  # noqa: E402
    MODEL_WORKFLOW_COVERAGE,
    ModelWorkflowCoverage,
    WorkflowCoverageError,
    discover_run_agent_owners,
    validate_model_workflow_coverage,
)
from tests.scenarios.canaries import LIVE_CANARIES  # noqa: E402
from tests.scenarios.evidence_intake_calibration import (  # noqa: E402
    EVIDENCE_INTAKE_CALIBRATION_CASES,
    validate_evidence_intake_calibration_cases,
)
from tests.scenarios.evidence_judgment_calibration import (  # noqa: E402
    EVIDENCE_JUDGMENT_CALIBRATION_CASES,
    validate_evidence_judgment_calibration_cases,
)
from tests.scenarios.final_composition_calibration import (  # noqa: E402
    FINAL_COMPOSITION_CALIBRATION_CASES,
    validate_final_composition_calibration_cases,
)
from tests.scenarios.governance import ScenarioGovernanceError, validate_real_scenario_catalog  # noqa: E402
from tests.scenarios.intake_planning_calibration import (  # noqa: E402
    CALIBRATION_CASES,
    validate_calibration_cases,
)
from tests.scenarios.replays import (  # noqa: E402
    FIRST_WAVE_CASES,
    FIRST_WAVE_FAMILIES,
    REQUIRED_FIRST_WAVE_FAMILY_IDS,
)

NODE_ROOT = AGENT_ROOT / "src/deerflow_deep_research/graph/nodes"
PROVIDER_SHAPE_ROOT = AGENT_ROOT / "tests/fixtures/provider_shapes"
PROVIDER_DISCOVERY_IDS = {
    *(f"LIVE-20260717-{index:02d}" for index in range(1, 7)),
    *(f"RELEASE-20260717-{index:02d}" for index in range(1, 26)),
}
PROVIDER_DISCOVERY_DISPOSITIONS = (
    *LIVE_DISCOVERY_DISPOSITIONS,
    *RELEASE_DISCOVERY_DISPOSITIONS_01_14,
    *RELEASE_DISCOVERY_DISPOSITIONS_15_25,
)
DEFAULT_COLLECTION_COMMAND = (sys.executable,)
CATALOG_SCRIPT = AGENT_ROOT / "scripts" / "collect_test_catalog.py"

# Suite-level case budget: the deterministic gate must not grow without review.
# Baselines are the measured 2026-08-22 counts (fast=2648, integration=304,
# workflow=35, live=50, periodic=2, deterministic total=2987) plus headroom for
# bounded, evidence-backed additions. Crossing a budget without a current waiver
# fails `make test-assets`/CI so test bloat is an explicit, reviewed decision
# instead of an unnoticed accumulation.
CASE_BUDGETS: tuple[tuple[FocusedSelection, int], ...] = (
    (FocusedSelection.FAST, 2900),
    (FocusedSelection.INTEGRATION, 400),
    (FocusedSelection.WORKFLOW, 60),
    (FocusedSelection.LIVE, 80),
    (FocusedSelection.PERIODIC, 10),
)
DETERMINISTIC_TOTAL_BUDGET = 3300

_CATALOG_CACHE: dict[tuple[Path, tuple[str, ...]], tuple[tuple[str, frozenset[str]], ...]] = {}
_DIRECT_COLLECTION_CACHE: dict[tuple[Path, tuple[str, ...], str, tuple[str, ...], bool], frozenset[str]] = {}
# Cross-process disk cache for the whole-tree catalog: make verify runs four
# pytest processes (fast/integration/workflow/test-assets), each of which would
# otherwise re-run a ~3-4s `pytest --collect-only` subprocess for the same tree.
# The cache is keyed by a fingerprint of test-relevant sources so it self-invalidates
# on any source change; written atomically so concurrent processes never read a
# partial file. Cleared by reset_collection_cache() so cache-behavior contract
# tests keep forcing a fresh subprocess.
CATALOG_CACHE_PATH = AGENT_ROOT / ".reports" / "catalog-cache.json"
_CATALOG_FINGERPRINT_ROOTS = (
    AGENT_ROOT / "tests",
    AGENT_ROOT / "scripts",
    AGENT_ROOT / "src",
    AGENT_ROOT / "pyproject.toml",
)
CALIBRATION_REGISTRIES = (
    CALIBRATION_CASES,
    EVIDENCE_INTAKE_CALIBRATION_CASES,
    EVIDENCE_JUDGMENT_CALIBRATION_CASES,
    FINAL_COMPOSITION_CALIBRATION_CASES,
)


def _catalog_fingerprint() -> str:
    """Cheap content fingerprint of everything that can change the catalog."""
    digest = hashlib.sha256()
    for root in _CATALOG_FINGERPRINT_ROOTS:
        if root.is_dir():
            files = sorted(p for p in root.rglob("*.py") if p.is_file())
        elif root.is_file():
            files = [root]
        else:
            continue
        for path in files:
            try:
                stat = path.stat()
            except OSError:
                continue
            digest.update(f"{path.relative_to(AGENT_ROOT)}\0{stat.st_mtime_ns}\0{stat.st_size}\0".encode())
    return digest.hexdigest()


def _read_catalog_cache() -> tuple[tuple[str, frozenset[str]], ...] | None:
    """Return the disk catalog when it matches the current tree fingerprint."""
    try:
        payload = json.loads(CATALOG_CACHE_PATH.read_text(encoding="utf-8"))
        if payload.get("fingerprint") != _catalog_fingerprint():
            return None
        entries = payload.get("entries")
        if not isinstance(entries, list):
            return None
        catalog = tuple(
            (entry["nodeid"], frozenset(entry["markers"]))
            for entry in entries
            if isinstance(entry, dict)
            and isinstance(entry.get("nodeid"), str)
            and isinstance(entry.get("markers"), list)
            and all(isinstance(marker, str) for marker in entry["markers"])
        )
        return catalog or None
    except (OSError, ValueError, TypeError, KeyError):
        return None


def _write_catalog_cache(catalog: tuple[tuple[str, frozenset[str]], ...]) -> None:
    """Atomically persist the catalog for other pytest processes."""
    try:
        CATALOG_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "fingerprint": _catalog_fingerprint(),
            "entries": [{"nodeid": nodeid, "markers": sorted(markers)} for nodeid, markers in catalog],
        }
        tmp_path = CATALOG_CACHE_PATH.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        tmp_path.replace(CATALOG_CACHE_PATH)
    except OSError:
        pass


class CognitiveEvidenceGateError(ValueError):
    pass


@dataclass(frozen=True)
class CaseBudgetWaiver:
    """Authorized lane/count overage for a bounded period (like DurationWaiver)."""

    lane: FocusedSelection | None  # None = deterministic total
    reason: str
    owner: str
    expires_on: date


CASE_BUDGET_WAIVERS: tuple[CaseBudgetWaiver, ...] = ()


def validate_case_budgets(
    focused: Mapping[FocusedSelection, set[str]],
    deterministic_total: int,
    *,
    now: date,
    waivers: tuple[CaseBudgetWaiver, ...] = CASE_BUDGET_WAIVERS,
) -> None:
    """Fail the asset gate when a lane (or the deterministic total) exceeds its
    unwaived case budget. Lanes not listed in CASE_BUDGETS are not bounded."""
    valid = {waiver.lane for waiver in waivers if waiver.reason and waiver.owner and waiver.expires_on >= now}
    failures: list[str] = []
    for selection, budget in CASE_BUDGETS:
        count = len(focused.get(selection, ()))
        if count > budget and selection not in valid:
            failures.append(f"{selection.value}={count} > budget {budget}")
    if deterministic_total > DETERMINISTIC_TOTAL_BUDGET and None not in valid:
        failures.append(f"deterministic-total={deterministic_total} > budget {DETERMINISTIC_TOTAL_BUDGET}")
    if failures:
        raise CoverageError("unwaived case budget overrun: " + ", ".join(failures))


def reset_collection_cache() -> None:
    """Clear successful selector collections for a test-owned process."""
    _CATALOG_CACHE.clear()
    _DIRECT_COLLECTION_CACHE.clear()
    try:
        CATALOG_CACHE_PATH.unlink(missing_ok=True)
    except OSError:
        pass


def _catalog_for_project(*, agent_root: Path, command: tuple[str, ...]) -> tuple[tuple[str, frozenset[str]], ...]:
    key = (agent_root.resolve(), command)
    cached = _CATALOG_CACHE.get(key)
    if cached is not None:
        return cached
    if agent_root.resolve() == AGENT_ROOT and command == DEFAULT_COLLECTION_COMMAND:
        disk_cached = _read_catalog_cache()
        if disk_cached is not None:
            _CATALOG_CACHE[key] = disk_cached
            return disk_cached
    with tempfile.TemporaryDirectory(prefix="deep-research-test-catalog-") as directory:
        output_path = Path(directory) / "catalog.json"
        result = subprocess.run(
            [*command, str(CATALOG_SCRIPT), "--output", str(output_path)],
            cwd=agent_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0 or not output_path.is_file():
            raise CoverageError(f"project pytest collection failed:\n{result.stderr or result.stdout}")
        try:
            raw_entries = json.loads(output_path.read_text(encoding="utf-8"))
            catalog = tuple(
                (entry["nodeid"], frozenset(entry["markers"]))
                for entry in raw_entries
                if isinstance(entry, dict)
                and isinstance(entry.get("nodeid"), str)
                and isinstance(entry.get("markers"), list)
                and all(isinstance(marker, str) for marker in entry["markers"])
            )
        except (OSError, ValueError, TypeError, KeyError) as exc:
            raise CoverageError(f"project pytest catalog invalid: {exc}") from exc
    if not catalog:
        raise CoverageError("project pytest catalog returned no selectors")
    if agent_root.resolve() == AGENT_ROOT and command == DEFAULT_COLLECTION_COMMAND:
        _write_catalog_cache(catalog)
    _CATALOG_CACHE[key] = catalog
    return catalog


def _matches_marker_expression(markers: frozenset[str], expression: str) -> bool:
    tokens = expression.replace("(", " ( ").replace(")", " ) ").split()
    index = 0

    def parse_or() -> bool:
        nonlocal index
        value = parse_and()
        while index < len(tokens) and tokens[index] == "or":
            index += 1
            right = parse_and()
            value = value or right
        return value

    def parse_and() -> bool:
        nonlocal index
        value = parse_term()
        while index < len(tokens) and tokens[index] == "and":
            index += 1
            right = parse_term()
            value = value and right
        return value

    def parse_term() -> bool:
        nonlocal index
        if index >= len(tokens):
            raise CoverageError(f"marker expression invalid: {expression}")
        token = tokens[index]
        index += 1
        if token == "not":
            return not parse_term()
        if token == "(":
            value = parse_or()
            if index >= len(tokens) or tokens[index] != ")":
                raise CoverageError(f"marker expression invalid: {expression}")
            index += 1
            return value
        if token in {"and", "or", ")"}:
            raise CoverageError(f"marker expression invalid: {expression}")
        return token in markers

    value = parse_or()
    if index != len(tokens):
        raise CoverageError(f"marker expression invalid: {expression}")
    return value


def _matches_paths(nodeid: str, paths: tuple[str, ...]) -> bool:
    return any(nodeid == path or nodeid.startswith(f"{path}/") for path in paths)


def collect_pytest_selectors(
    *,
    paths: tuple[str, ...],
    expression: str,
    label: str,
    agent_root: Path = AGENT_ROOT,
    command: tuple[str, ...] = DEFAULT_COLLECTION_COMMAND,
    allow_empty: bool = False,
) -> set[str]:
    if agent_root.resolve() == AGENT_ROOT and command == DEFAULT_COLLECTION_COMMAND:
        selectors = {
            nodeid
            for nodeid, markers in _catalog_for_project(agent_root=agent_root, command=command)
            if _matches_paths(nodeid, paths) and _matches_marker_expression(markers, expression)
        }
        if not selectors and not allow_empty:
            raise CoverageError(f"{label} pytest collection returned no selectors")
        return selectors

    key = (agent_root.resolve(), paths, expression, command, allow_empty)
    cached = _DIRECT_COLLECTION_CACHE.get(key)
    if cached is not None:
        return set(cached)
    result = subprocess.run(
        [
            *command,
            "--collect-only",
            "-q",
            *paths,
            "-m",
            expression,
        ],
        cwd=agent_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 and not (allow_empty and result.returncode == 5):
        raise CoverageError(f"{label} pytest collection failed:\n{result.stderr or result.stdout}")
    selectors = {line.strip() for line in result.stdout.splitlines() if "::" in line and not line.startswith("=")}
    if not selectors and not allow_empty:
        raise CoverageError(f"{label} pytest collection returned no selectors")
    _DIRECT_COLLECTION_CACHE[key] = frozenset(selectors)
    return set(selectors)


def collect_deterministic_selectors(agent_root: Path = AGENT_ROOT) -> set[str]:
    return collect_pytest_selectors(
        paths=("tests",),
        expression=f"not ({DETERMINISTIC_EXCLUDE})",
        label="deterministic aggregate",
        agent_root=agent_root,
    )


def validate_cognitive_evidence_gate(
    *,
    board: CognitiveProgramEvidenceBoard,
    logical_nodes: tuple[str, ...],
    reader_records: tuple[object, ...],
    cohort_rows: tuple[CapabilityEvidenceRow, ...],
    workflow_coverage: tuple[ModelWorkflowCoverage, ...],
    node_conformance: tuple[NodeConformance, ...],
    claims: Mapping[str, TestEvidenceClaim],
    requirement_impacts: tuple[RequirementImpact, ...],
    calibration_registries: tuple[tuple[object, ...], ...],
    consolidation_decisions: tuple[ConsolidationDecision, ...],
    collected_selectors: set[str],
) -> None:
    """Run the complete offline cognitive-evidence joins over injected owners."""

    if len(calibration_registries) != 4:
        raise CognitiveEvidenceGateError("calibration registry invalid: expected four owning registries")
    intake_planning, evidence_intake, evidence_judgment, final_composition = calibration_registries
    try:
        validate_calibration_cases(intake_planning)  # type: ignore[arg-type]
        validate_evidence_intake_calibration_cases(evidence_intake)  # type: ignore[arg-type]
        validate_evidence_judgment_calibration_cases(evidence_judgment)  # type: ignore[arg-type]
        validate_final_composition_calibration_cases(final_composition)  # type: ignore[arg-type]
    except ValueError as exc:
        raise CognitiveEvidenceGateError(f"calibration registry invalid: {exc}") from exc

    validate_cognitive_program_board(
        board,
        logical_nodes=logical_nodes,
        reader_records=reader_records,
        cohort_rows=cohort_rows,
        workflow_coverage=workflow_coverage,
        node_conformance=node_conformance,
        claims=claims,
        requirement_impacts=requirement_impacts,
        calibration_cases=tuple(case for registry in calibration_registries for case in registry),
        collected_selectors=collected_selectors,
    )
    validate_consolidation_decisions(
        consolidation_decisions,
        claims=tuple(claims.values()),
        requirement_impacts=requirement_impacts,
        collected_selectors=collected_selectors,
    )


def main() -> int:
    try:
        collected = collect_deterministic_selectors()
        focused = {
            FocusedSelection.FAST: collect_pytest_selectors(
                paths=FAST_PATHS,
                expression=FAST_EXPRESSION,
                label="fast",
            ),
            FocusedSelection.INTEGRATION: collect_pytest_selectors(
                paths=INTEGRATION_PATHS,
                expression=INTEGRATION_EXPRESSION,
                label="integration",
            ),
            FocusedSelection.WORKFLOW: collect_pytest_selectors(
                paths=WORKFLOW_PATHS,
                expression=WORKFLOW_EXPRESSION,
                label="workflow",
            ),
            FocusedSelection.LIVE: collect_pytest_selectors(
                paths=LIVE_PATHS,
                expression=LIVE_EXPRESSION,
                label="live",
            ),
            FocusedSelection.PERIODIC: collect_pytest_selectors(
                paths=PERIODIC_PATHS,
                expression=PERIODIC_EXPRESSION,
                label="periodic",
            ),
        }
        claims = claim_index(EVIDENCE_CLAIMS)
        validate_claim_selections(EVIDENCE_CLAIMS, focused_selectors=focused)
        validate_case_budgets(
            focused,
            deterministic_total=len(collected),
            now=datetime.now(UTC).date(),
        )
        deterministic_impl_ids = collected_deterministic_impl_ids(AGENT_ROOT, collected)
        declared_requirement_ids = {
            *(requirement_id for claim in EVIDENCE_CLAIMS for requirement_id in claim.requirement_ids),
            *(impact.requirement_id for impact in REQUIREMENT_IMPACTS),
            *(rule.requirement_id for rule in REQUIREMENT_EVIDENCE_POLICY),
            *deterministic_impl_ids,
        }
        validate_requirement_evidence(
            policy=REQUIREMENT_EVIDENCE_POLICY,
            claims=EVIDENCE_CLAIMS,
            alive_requirement_ids=deterministic_impl_ids,
            known_requirement_ids=declared_requirement_ids,
            deterministic_impl_ids=deterministic_impl_ids,
            collected_selectors=set().union(*focused.values()),
        )
        validate_requirement_impacts(
            REQUIREMENT_IMPACTS,
            claims=EVIDENCE_CLAIMS,
            known_requirement_ids=declared_requirement_ids,
            collected_selectors=set().union(*focused.values()),
        )
        validate_inventory_claim_references(
            (
                *((f"incident:{entry.incident_id}", entry.claim_ids) for entry in INCIDENTS),
                *(
                    (f"node:{entry.logical_name}", (entry.success_claim_id, entry.risk_claim_id))
                    for entry in NODE_CONFORMANCE
                ),
                *((f"fault:{entry.fault.value}", (entry.claim_id,)) for entry in CRITICAL_FAULTS),
                *((f"workflow:{entry.logical_name}", entry.referenced_claim_ids) for entry in MODEL_WORKFLOW_COVERAGE),
            ),
            claims=claims,
        )
        validate_cohort_evidence(
            COHORT_EVIDENCE,
            claims,
            collected_selectors=set().union(*focused.values()),
        )
        validate_cognitive_evidence_gate(
            board=COGNITIVE_PROGRAM_BOARD,
            logical_nodes=LOGICAL_NODES,
            reader_records=load_reader_inventory(AGENT_ROOT.parent),
            cohort_rows=COHORT_EVIDENCE,
            workflow_coverage=MODEL_WORKFLOW_COVERAGE,
            node_conformance=NODE_CONFORMANCE,
            claims=claims,
            requirement_impacts=REQUIREMENT_IMPACTS,
            calibration_registries=CALIBRATION_REGISTRIES,
            consolidation_decisions=CONSOLIDATION_DECISIONS,
            collected_selectors=set().union(*focused.values()),
        )
        validate_incident_coverage(INCIDENTS, claims, collected, excluded_selectors=set())
        validate_node_conformance(
            NODE_CONFORMANCE,
            claims,
            collected,
            registered_names=set(load_research_node_specs()),
        )
        validate_fault_matrix(CRITICAL_FAULTS, claims, collected)
        validate_model_workflow_coverage(
            MODEL_WORKFLOW_COVERAGE,
            claims=claims,
            discovered_owners=discover_run_agent_owners(NODE_ROOT),
            focused_selectors=focused,
        )
        validate_real_scenario_catalog(
            FIRST_WAVE_FAMILIES,
            FIRST_WAVE_CASES,
            EVIDENCE_CLAIMS,
            deterministic_selectors=collected,
            workflow_selectors=focused[FocusedSelection.WORKFLOW],
            required_family_ids=REQUIRED_FIRST_WAVE_FAMILY_IDS,
        )
        try:
            validate_provider_shape_catalog(
                PROVIDER_DISCOVERY_DISPOSITIONS,
                cases=load_provider_shape_archive(PROVIDER_SHAPE_ROOT),
                required_discovery_ids=PROVIDER_DISCOVERY_IDS,
                claims=claims,
                collected_selectors=set().union(*focused.values()),
                live_case_ids={case.scenario_id for case in LIVE_CANARIES},
            )
        except ValueError as exc:
            raise CoverageError(f"provider-shape catalog invalid: {exc}") from exc
    except (
        CoverageError,
        CognitiveEvidenceGateError,
        CognitiveProgramBoardError,
        EvidenceClaimError,
        FaultMatrixError,
        NodeConformanceError,
        ScenarioGovernanceError,
        RequirementEvidenceError,
        WorkflowCoverageError,
        WorkflowReaderError,
    ) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(
        f"Test asset coverage passed: {len(INCIDENTS)} incidents, "
        f"{len(NODE_CONFORMANCE)} real nodes, {len(CRITICAL_FAULTS)} critical faults, "
        f"{len(MODEL_WORKFLOW_COVERAGE)} model-workflow nodes, "
        f"{len(EVIDENCE_CLAIMS)} central claims, {len(collected)} deterministic tests; "
        + ", ".join(f"{selection.value}={len(focused[selection])}" for selection in FocusedSelection)
        + "."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
