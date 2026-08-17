"""Pure portable Change Guidance contracts.

@impl PCG-001
@impl PCG-002
@impl PCG-003
@impl PCG-004
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
KERNEL_PATH = REPO_ROOT / "openspec" / "governance" / "change_guidance_kernel.py"
SPEC = importlib.util.spec_from_file_location("change_guidance_kernel", KERNEL_PATH)
assert SPEC is not None and SPEC.loader is not None
kernel = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = kernel
SPEC.loader.exec_module(kernel)


def _review(heading: str, columns: tuple[str, ...]) -> str:
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    row = "| " + " | ".join("value" for _ in columns) + " |"
    return f"## {heading}\n\n{header}\n{separator}\n{row}\n"


def test_kernel_uses_explicit_inputs_without_repository_state() -> None:
    section = "- **Owner:** portable owner\n- **Evidence:** direct fixture\n"
    assert kernel.missing_fields(section, ("Owner", "Evidence")) == ()
    assert kernel.field_value(section, "Owner") == "portable owner"
    assert kernel.comma_separated_values("alpha, beta", r"[a-z]+") == ("alpha", "beta")


def test_core_only_composition_has_no_profile_obligations() -> None:
    composition = kernel.CompositionSchema(enabled_profiles=())
    assert composition.policies == frozenset()
    assert kernel.profile_completeness_issues((), composition, {}) == ()


def test_enabled_profiles_compose_all_review_obligations() -> None:
    columns = ("Fact", "Owner")
    control = kernel.ReviewSchema("Control Review", columns)
    node = kernel.ReviewSchema("Node Review", columns)
    composition = kernel.CompositionSchema(
        enabled_profiles=(
            kernel.ProfileSchema("workflow-control", frozenset({"control"}), {"control": control}),
            kernel.ProfileSchema("node-agent", frozenset({"node"}), {"node": node}),
        )
    )
    issues = kernel.profile_completeness_issues(
        ("control", "node"),
        composition,
        {"control": _review("Control Review", columns)},
    )
    assert [issue.code for issue in issues] == ["profile.review_missing"]


def test_disabled_and_unknown_policies_fail_closed() -> None:
    composition = kernel.CompositionSchema(enabled_profiles=())
    assert kernel.selected_policies("node-agent", composition) is None
    assert kernel.profile_completeness_issues(("node-agent",), composition, {})[0].code == "profile.policy_unknown"


def test_review_table_rejects_incomplete_shape_and_classification() -> None:
    schema = kernel.ReviewSchema(
        "Node Review",
        ("Surface", "Classification"),
        frozenset({"node-agent", "no-agent"}),
        1,
    )
    invalid = "| Surface | Classification |\n| --- | --- |\n| fixture | unknown |\n"
    assert kernel.validate_review_table(invalid, schema)[0].code == "review.classification"


def test_neutrality_scan_detects_source_product_path_and_requirement_id() -> None:
    forbidden = (r"Deep Research", r"deep_research_harness/", r"\b(?:DRC|PRS|PCG)-\d{3}\b")
    clean = {"core/change-practice.md": "One owner and one evidence seam."}
    assert kernel.neutrality_issues(clean, forbidden) == ()
    for planted in ("Deep Research", "deep_research_harness/", "DRC-012"):
        issues = kernel.neutrality_issues({"core/change-practice.md": planted}, forbidden)
        assert issues and issues[0].code == "portable.neutrality"
