#!/usr/bin/env python3
"""Fail deterministic CI for unwaived slow fast-lane tests.

@impl DER-005
"""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

MAX_FAST_TEST_SECONDS = 5.0


@dataclass(frozen=True)
class DurationWaiver:
    selector: str
    reason: str
    owner: str
    expires_on: date


DURATION_WAIVERS: tuple[DurationWaiver, ...] = ()


def _selector(case: ET.Element) -> str:
    classname = case.attrib.get("classname", "")
    name = case.attrib.get("name", "")
    return f"{classname}::{name}" if classname else name


def slow_selectors(report: Path, *, now: date, waivers: tuple[DurationWaiver, ...] = DURATION_WAIVERS) -> list[str]:
    root = ET.parse(report).getroot()
    valid = {waiver.selector for waiver in waivers if waiver.reason and waiver.owner and waiver.expires_on >= now}
    failures: list[str] = []
    for case in root.iter("testcase"):
        duration = float(case.attrib.get("time", "0"))
        selector = _selector(case)
        if duration > MAX_FAST_TEST_SECONDS and selector not in valid:
            failures.append(f"{selector}={duration:.3f}s")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    failures = slow_selectors(args.report, now=datetime.now(UTC).date())
    if failures:
        raise SystemExit("unwaived fast test duration: " + ", ".join(failures))
    print("Fast-lane duration policy passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
