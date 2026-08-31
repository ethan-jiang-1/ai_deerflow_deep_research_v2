#!/usr/bin/env python3
"""Collect Deep Research test node ids and inherited marker names once."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest


class CatalogPlugin:
    def __init__(self) -> None:
        self.entries: list[dict[str, object]] = []

    def pytest_collection_finish(self, session: pytest.Session) -> None:
        self.entries = [
            {"nodeid": item.nodeid, "markers": sorted({marker.name for marker in item.iter_markers()})}
            for item in session.items
        ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    plugin = CatalogPlugin()
    exit_code = pytest.main(["--collect-only", "-q", "tests"], plugins=(plugin,))
    if exit_code == pytest.ExitCode.OK:
        args.output.write_text(json.dumps(plugin.entries, separators=(",", ":")), encoding="utf-8")
    return int(exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
