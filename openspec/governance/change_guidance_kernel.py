"""Pure validation primitives for portable OpenSpec Change Guidance.

The module accepts explicit strings and schemas only. It performs no repository,
filesystem, process, environment, product, or wrapper discovery.

@impl PCG-001 PCG-002 PCG-003 PCG-004
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    detail: str


@dataclass(frozen=True)
class ReviewSchema:
    heading: str
    columns: tuple[str, ...]
    classifications: frozenset[str] = frozenset()
    classification_column: int | None = None


@dataclass(frozen=True)
class ProfileSchema:
    name: str
    policies: frozenset[str]
    reviews: Mapping[str, ReviewSchema]


@dataclass(frozen=True)
class CompositionSchema:
    enabled_profiles: tuple[ProfileSchema, ...]
    local_policies: frozenset[str] = frozenset()

    @property
    def policies(self) -> frozenset[str]:
        return frozenset().union(self.local_policies, *(profile.policies for profile in self.enabled_profiles))

    @property
    def reviews(self) -> Mapping[str, ReviewSchema]:
        return {
            policy: review
            for profile in self.enabled_profiles
            for policy, review in profile.reviews.items()
        }


def field_value(section: str, field: str) -> str | None:
    match = re.search(
        rf"^- \*\*{re.escape(field)}:\*\*[ \t]*(?P<value>\S[^\n]*)$",
        section,
        flags=re.MULTILINE,
    )
    return match.group("value").strip() if match else None


def missing_fields(section: str, fields: Sequence[str]) -> tuple[str, ...]:
    return tuple(field for field in fields if field_value(section, field) is None)


def comma_separated_values(value: str, pattern: str | None = None) -> tuple[str, ...] | None:
    values = tuple(item.strip() for item in value.split(","))
    if not values or any(not item for item in values) or len(values) != len(set(values)):
        return None
    if pattern is not None and any(re.fullmatch(pattern, item) is None for item in values):
        return None
    return values


def selected_policies(value: str, composition: CompositionSchema) -> tuple[str, ...] | None:
    if value.startswith("none:") and value.removeprefix("none:").strip():
        return ()
    policies = comma_separated_values(value)
    if policies is None or any(policy not in composition.policies for policy in policies):
        return None
    return policies


def table_cells(line: str) -> tuple[str, ...] | None:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return None
    return tuple(cell.strip() for cell in stripped[1:-1].split("|"))


def validate_review_table(section: str, schema: ReviewSchema) -> tuple[ValidationIssue, ...]:
    tables: list[list[tuple[str, ...]]] = []
    current: list[tuple[str, ...]] = []
    for line in section.splitlines():
        cells = table_cells(line)
        if cells is None:
            if current:
                tables.append(current)
                current = []
        else:
            current.append(cells)
    if current:
        tables.append(current)
    if len(tables) != 1 or len(tables[0]) < 3:
        return (ValidationIssue("review.table_shape", f"{schema.heading} needs exactly one complete table"),)
    table = tables[0]
    if table[0] != schema.columns or any(re.fullmatch(r":?-{3,}:?", cell) is None for cell in table[1]):
        return (ValidationIssue("review.table_header", f"{schema.heading} has an invalid header"),)
    for row in table[2:]:
        if len(row) != len(schema.columns) or any(not cell for cell in row):
            return (ValidationIssue("review.table_row", f"{schema.heading} has an incomplete row"),)
        if schema.classification_column is not None and row[schema.classification_column] not in schema.classifications:
            return (ValidationIssue("review.classification", f"{schema.heading} has an unsupported classification"),)
    return ()


def neutrality_issues(texts: Mapping[str, str], forbidden_patterns: Sequence[str]) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    for relative_path, content in texts.items():
        for pattern in forbidden_patterns:
            match = re.search(pattern, content, flags=re.IGNORECASE)
            if match is not None:
                issues.append(
                    ValidationIssue(
                        "portable.neutrality",
                        f"{relative_path} contains forbidden portable binding {match.group(0)!r}",
                    )
                )
    return tuple(issues)


def profile_completeness_issues(
    selected: Sequence[str],
    composition: CompositionSchema,
    review_sections: Mapping[str, str],
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    for policy in selected:
        if policy not in composition.policies:
            issues.append(ValidationIssue("profile.policy_unknown", f"policy {policy!r} is not enabled"))
            continue
        review = composition.reviews.get(policy)
        if review is not None:
            section = review_sections.get(policy)
            if section is None:
                issues.append(ValidationIssue("profile.review_missing", f"policy {policy!r} needs {review.heading}"))
            else:
                issues.extend(validate_review_table(section, review))
    return tuple(issues)
