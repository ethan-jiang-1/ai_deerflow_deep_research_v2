#!/usr/bin/env python3
"""Fail deterministic CI for unwaived slow lane tests.

@impl DER-005
"""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

MAX_FAST_TEST_SECONDS = 5.0
MAX_PERIODIC_TEST_SECONDS = 180.0


@dataclass(frozen=True)
class DurationWaiver:
    selector: str
    reason: str
    owner: str
    expires_on: date


DURATION_WAIVERS: tuple[DurationWaiver, ...] = ()
PERIODIC_DURATION_WAIVERS: tuple[DurationWaiver, ...] = ()


def _selector(case: ET.Element) -> str:
    classname = case.attrib.get("classname", "")
    name = case.attrib.get("name", "")
    return f"{classname}::{name}" if classname else name


def slow_selectors(
    report: Path,
    *,
    now: date,
    max_seconds: float = MAX_FAST_TEST_SECONDS,
    waivers: tuple[DurationWaiver, ...] = DURATION_WAIVERS,
) -> list[str]:
    root = ET.parse(report).getroot()
    valid = {waiver.selector for waiver in waivers if waiver.reason and waiver.owner and waiver.expires_on >= now}
    failures: list[str] = []
    for case in root.iter("testcase"):
        duration = float(case.attrib.get("time", "0"))
        selector = _selector(case)
        if duration > max_seconds and selector not in valid:
            failures.append(f"{selector}={duration:.3f}s")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--lane", choices=("fast", "periodic"), default="fast")
    args = parser.parse_args()
    max_seconds, waivers = (
        (MAX_FAST_TEST_SECONDS, DURATION_WAIVERS)
        if args.lane == "fast"
        else (MAX_PERIODIC_TEST_SECONDS, PERIODIC_DURATION_WAIVERS)
    )
    failures = slow_selectors(
        args.report,
        now=datetime.now(UTC).date(),
        max_seconds=max_seconds,
        waivers=waivers,
    )
    if failures:
        raise SystemExit(f"unwaived {args.lane} test duration: " + ", ".join(failures))
    print(f"{args.lane.title()}-lane duration policy passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
