"""Deterministic tests for the composition-alias terminology rule.

Run from the repository root:

    python3 -m unittest discover -s openspec/tests/governance

These fixtures build an isolated temp root and never mutate the repository.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

GOVERNANCE_DIR = Path(__file__).resolve().parents[2] / "governance"
if str(GOVERNANCE_DIR) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_DIR))

from check_project_specs import active_terminology_violations  # noqa: E402


class CompositionAliasRuleTests(unittest.TestCase):
    def _composition_alias_violations(self, body: str) -> list[dict[str, str]]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = root / "openspec" / "specs" / "demo" / "spec.md"
            spec.parent.mkdir(parents=True)
            spec.write_text(body, encoding="utf-8")
            return [
                violation
                for violation in active_terminology_violations(root)
                if violation["rule"] == "compositionAlias"
            ]

    def test_hyphen_and_space_alias_are_flagged(self) -> None:
        self.assertEqual(len(self._composition_alias_violations("The full-fake graph runs.\n")), 1)
        self.assertEqual(len(self._composition_alias_violations("The full fake graph runs.\n")), 1)

    def test_retired_machine_literal_is_not_flagged(self) -> None:
        self.assertEqual(
            self._composition_alias_violations("A State mapping names `full_fake` or unknown.\n"),
            [],
        )

    def test_scenario_heading_is_exempt(self) -> None:
        self.assertEqual(
            self._composition_alias_violations("#### Scenario: Full-fake graph unchanged\n"),
            [],
        )

    def test_scenario_body_is_still_checked(self) -> None:
        body = (
            "#### Scenario: Fixture graph unchanged\n"
            "- **WHEN** the fixture graph runs\n"
            "- **THEN** the full-fake case is gone\n"
        )
        self.assertEqual(len(self._composition_alias_violations(body)), 1)


if __name__ == "__main__":
    unittest.main()
