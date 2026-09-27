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


# 第一批真实 duration waiver（2026-09-28，CI 首次真实运行时落地）：GitHub ubuntu
# runner 比本地基准机慢数倍，这三个子进程/收集密集型测试在 CI 上超并行预算
# （8s），本地均在预算内。按 DONE-009 停靠项的要求，同改动加了"未用即红"防锈。
DURATION_WAIVERS: tuple[DurationWaiver, ...] = (
    DurationWaiver(
        selector="tests.contract.test_asset_checker_contract::test_case_budget_gate_passes_on_current_collection",
        reason="CI runner slowness: collection-heavy test measured 9.2s on ubuntu runners vs in-budget locally",
        owner="ci",
        expires_on=date(2026, 12, 31),
    ),
    DurationWaiver(
        selector="tests.contract.test_test_lane_selection::test_live_tests_are_selected_only_by_the_live_lane",
        reason="CI runner slowness: subprocess-heavy test measured 9.4s on ubuntu runners vs in-budget locally",
        owner="ci",
        expires_on=date(2026, 12, 31),
    ),
    DurationWaiver(
        selector="tests.contract.test_configure::test_cli_read_only_modes_emit_redacted_json_and_runtime_axis_exit_codes",
        reason="CI runner slowness: CLI subprocess test measured 14.0s on ubuntu runners vs in-budget locally",
        owner="ci",
        expires_on=date(2026, 12, 31),
    ),
)
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
