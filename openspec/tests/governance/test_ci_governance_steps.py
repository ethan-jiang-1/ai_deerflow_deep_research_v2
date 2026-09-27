"""The deterministic CI workflow carries the governance-side obligations.

Three facts live here because only this workflow can own them:

- The governance checkers live outside the harness tree, so ``make verify``
  can never lint them: the verify gate stays application-independent
  (PRS-020) and no harness file may even name an ``openspec/`` path
  (dependency direction). The workflow is the only host for this lint.
- The workflow also runs the governance unittest suite, so both governance
  surfaces it touches — the linted scripts and the suite itself — must
  select it through the path filters.
- The suite invocation must match the command the suite docstrings
  document, without ``-t .``: the governance suite is a plain directory,
  not a package, and unittest discovery with a distinct top-level
  directory raises ``ImportError: Start directory is not importable``
  (verified on Python 3.12.10 and 3.13.5). The ``-t .`` form therefore
  never executed a single test, which is how a red suite stayed unnoticed.

Two divergences are pinned here on purpose, so they cannot rot silently:

- ``ruff check --isolated`` — the governance lint uses ruff's own default
  rule set, self-contained. It must not pick up the harness
  ``pyproject.toml`` implicitly through the working directory, and adopting
  the harness rule set (E/F/I/UP/B/ASYNC at line length 120) would be a
  cosmetic campaign over gate-critical parsers, not this obligation.
- Path filters select exactly ``openspec/governance/**`` and
  ``openspec/tests/governance/**``, not all of ``openspec/**`` — spec and
  document edits must not spin the full harness suite.
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "agent-tests.yml"


class CiGovernanceStepsTests(unittest.TestCase):
    def test_both_path_filters_select_the_governance_surfaces(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        for filter_line in (
            '      - "openspec/governance/**"',
            '      - "openspec/tests/governance/**"',
        ):
            self.assertEqual(
                workflow.count(filter_line),
                2,
                f"pull_request and push must both select {filter_line}",
            )

    def test_governance_lint_step_is_self_contained_and_installed(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "UV_CACHE_DIR=$PWD/.uv-cache UV_OFFLINE=1 uv run ruff check --isolated ../openspec/governance/",
            workflow,
            "the workflow must lint the governance scripts with ruff's isolated "
            "default rule set, not an implicitly discovered harness configuration",
        )
        self.assertLess(
            workflow.index("make install"),
            workflow.index("uv run ruff check --isolated"),
            "the governance lint runs through the installed environment, so it must follow make install",
        )

    def test_governance_suite_runs_the_documented_discover_command(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "python3 -m unittest discover -s openspec/tests/governance -q",
            workflow,
            "the workflow must run the governance suite with the command its "
            "docstrings document",
        )
        self.assertNotIn(
            "-s openspec/tests/governance -t",
            workflow,
            "discovery with a distinct top-level directory cannot import the "
            "governance suite (not a package); the -t form never ran a test",
        )


if __name__ == "__main__":
    unittest.main()
