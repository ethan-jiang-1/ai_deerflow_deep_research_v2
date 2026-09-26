"""The declared upstream gitlink lock and the app-side pin never drift apart.

@impl PRS-018

The submodule commit is declared twice on purpose: the governance registry
(``openspec/governance/project-structure.toml``) owns the repository-level fact
and the harness contract test owns the code-level mirror
(``CURRENT_DEERFLOW_PIN``). The v2.1.0 upgrade updated one side and not the
other, which left the architecture gate red while every routine lane stayed
green. This test fails the deterministic suite the moment the two anchors
disagree again.
"""

from __future__ import annotations

import re
import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY = REPO_ROOT / "openspec/governance/project-structure.toml"
PIN_TEST = REPO_ROOT / "deep_research_harness/tests/contract/test_deerflow_public_api.py"

_GITLINK_COMMIT_RE = re.compile(r'^commit\s*=\s*"([0-9a-f]{40})"\s*$', re.MULTILINE)
_PIN_RE = re.compile(r'^CURRENT_DEERFLOW_PIN\s*=\s*"([0-9a-f]{40})"\s*$', re.MULTILINE)


class UpstreamPinAgreementTest(unittest.TestCase):
    def test_declared_gitlink_lock_equals_the_code_side_pin(self) -> None:
        manifest = tomllib.loads(REGISTRY.read_text(encoding="utf-8"))
        declared = manifest["upstream_gitlink"]["commit"]

        pin_match = _PIN_RE.search(PIN_TEST.read_text(encoding="utf-8"))
        self.assertIsNotNone(pin_match, "CURRENT_DEERFLOW_PIN not found in the harness contract test")
        pinned = pin_match.group(1)

        raw = REGISTRY.read_text(encoding="utf-8")
        lock_match = _GITLINK_COMMIT_RE.search(raw)
        self.assertIsNotNone(lock_match, "gitlink commit line not found in the structure registry")

        self.assertEqual(
            declared,
            pinned,
            "upstream gitlink lock and CURRENT_DEERFLOW_PIN disagree; "
            "update both sides in the same change so the architecture gate stays green",
        )


if __name__ == "__main__":
    unittest.main()
