# TODO: A-002 gitlink boundary detector

> 状态: 待设计 | 优先级: 高 | 更新: 2026-08-13
> 上游: Stage 7 final alignment audit | 下游: future governance/archive evidence

## Why

The current archive protocol records `deerflow/` gitlink and nested-worktree state
manually. `openspec/config.yaml` explicitly says that this is evidence, not automatic
protection. A later change can therefore alter the pointer or nested worktree without a
dedicated deterministic failure.

## 现状对齐

`deerflow/` is an upstream submodule at the repository root. Downstream work must not
modify or source-browse it. The expected detector's job is only to reject an unapproved
gitlink pointer/worktree change according to a declared boundary; it must not inspect
or alter DeerFlow source.

## Current Direction

Create one separately authorized OpenSpec change whose primary owner is the lowest
responsible repository-governance/check boundary. Start with a red deterministic test
for an altered gitlink pointer and a dirty nested worktree fixture or equivalent Git
metadata simulation. Then add the smallest detector and wire it only into the intended
governance/closeout command.

## Design Questions

- Which committed range or declared baseline owns the allowed gitlink pointer?
- Can the detector test Git metadata safely without initializing or modifying DeerFlow?
- Should nested-worktree dirtiness fail all checks or only archive/closeout checks?
- How should intentional upstream bumps be explicitly admitted?

## Non-Goals

- Do not modify or source-browse `deerflow/`.
- Do not treat a detector as proof of runtime compatibility with DeerFlow.
- Do not combine this work with unrelated topology prose or application behavior.

## Next Step

Open a bounded governance OpenSpec proposal with a red-before-green detector seam and
an explicit permitted-baseline contract.
