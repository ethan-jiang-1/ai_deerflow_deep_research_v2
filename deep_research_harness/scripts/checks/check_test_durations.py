#!/usr/bin/env python3
"""Fail deterministic CI for unwaived slow lane tests.

@impl DER-005
"""

from __future__ import annotations

import argparse
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

MAX_FAST_TEST_SECONDS = 5.0
# xdist 并行档下用例耗时被放大（实测 3.22s→4.90s，~1.5x）；并行报告用独立阈值
# 避免误杀，串行报告仍用 MAX_FAST_TEST_SECONDS。
MAX_FAST_TEST_SECONDS_PARALLEL = 8.0
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
    report_selectors: set[str] = set()
    for case in root.iter("testcase"):
        duration = float(case.attrib.get("time", "0"))
        selector = _selector(case)
        report_selectors.add(selector)
        if duration > max_seconds and selector not in valid:
            failures.append(f"{selector}={duration:.3f}s")
    # 未用即红（DONE-009 停靠项，随第一批真 waiver 落地）：时长会波动，某次跑快不算
    # 未用；只有选择器在报告里根本不存在（测试被改名或删除）时，waiver 才算烂掉。
    dead = sorted(valid - report_selectors)
    failures.extend(f"waiver_selector_unknown:{selector}" for selector in dead)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--lane", choices=("fast", "periodic"), default="fast")
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="report was produced by an xdist run; use the parallel threshold (8s)",
    )
    args = parser.parse_args()
    if args.lane == "fast":
        max_seconds = MAX_FAST_TEST_SECONDS_PARALLEL if args.parallel else MAX_FAST_TEST_SECONDS
        waivers = DURATION_WAIVERS
    else:
        max_seconds, waivers = MAX_PERIODIC_TEST_SECONDS, PERIODIC_DURATION_WAIVERS
    # 机器档位覆盖：CI runner 比本地基准机慢数倍且负载波动，不同测试会轮流贴线，
    # 逐个 waiver 是打地鼠。DURATION_MAX_FAST_SECONDS 只允许放宽（≥ 内建预算），
    # 供 CI 声明自己的机器档；本地不设此变量，内建预算照常严格。
    override = os.environ.get("DURATION_MAX_FAST_SECONDS")
    if override:
        try:
            ceiling = float(override)
        except ValueError as exc:
            raise SystemExit("DURATION_MAX_FAST_SECONDS must be a number") from exc
        if ceiling < max_seconds:
            raise SystemExit("DURATION_MAX_FAST_SECONDS may only loosen the built-in budget")
        max_seconds = ceiling
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
