# TODO: BUG-048 item 7 — state.json / checkpoint self-consistent projection

> 状态: 暂停（未排期） | 优先级: 低 | 更新: 2026-09-12
> 上游: CLS-047（change `fix-003-blocking-bugs-three-changes`）| 下游: 无

## Why

003 bugfix 战役把 BUG-048 的 1–4/6 项修完，第 7 项（`state.json` / checkpoint 的
**自洽投影**）留作 follow-up：投影面当前**没有拥有它的主 spec**，需要一份独立合同先
决定"投影读什么、与 checkpoint 的一致性边界在哪"，才能实现。此前只在 CLS-047 的
关闭摘要里留字，无独立条目。

## 现状对齐

`state.json` 与 checkpoint 都在盘上，但"投影是 checkpoint 的自洽视图"这一主张没有
owner 化的 typed contract；直接补一个投影实现会先于合同，制造第二事实源。

## Current Direction（重启时）

用一份 approved OpenSpec change 先定投影合同：owning spec、读源、一致性不变式、
不一致时的合法处置（拒绝 / 降级披露），再实现。

## Non-Goals

- 不在合同前先写投影实现。
- 不让投影成为 lifecycle 或 checkpoint 的第二 authority。

## Next Step

无（暂停）。重启条件见
[`README.md`](README.md) 的 suspended 索引；先开投影合同的 OpenSpec change。
