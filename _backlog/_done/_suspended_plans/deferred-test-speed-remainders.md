# TODO: test-speed remainders（CI R1 confirmation / R4 / R5）

> 状态: 暂停（未排期） | 优先级: 低 | 更新: 2026-09-12
> 上游: CLS-052（test-suite-cleanup-and-speed）+ CLS-053 | 下游: 无

## Why

CLS-052 的测试提速收尾时，UI 上还有三项没关闭，只在关闭摘要里留字，无独立条目：

- **CI R1 缓存确认**：`setup-uv` 的 `enable-cache: true` + `prune-cache: false` 已落地，
  但需要**一次真实 CI 首跑**确认缓存命中。首跑被存量 CI 问题挡住（checkout 未拉
  `deerflow` submodule → install 挂，见 CLS-053 L3），用户当时指示"CI 以后再说"。
- **R4 demo_tui 用例数**：慢在驱动开销不是用例数；02x 战役收尾后再评估是否合并。
- **R5 收集优化**：workflow lane 全树收集 3040 个再筛，收益 ~2-3s，已判"不值得"。

## 现状对齐

R1 是唯一"安全且有效"的剩余杠杆（本地已接近收益边界）；R2（拆 4 CI job）、R6
（`make -j verify`）、合并 pytest 调用、`-n auto` 均已有实测**否决/撤回**，不算待办。

## Current Direction（重启时）

先解 CLS-053 的 L3（CI checkout `submodules: recursive`），重开 PR #1 观察 R1 缓存
命中；R4/R5 仅在明确给出性能预算时重估。

## Non-Goals

- 不重开已实测否决的 R2 / R6 / 合并调用 / `-n auto`。
- 不把"测试默认并行"翻案（未经并行安全 review，xdist 保持 opt-in）。

## Next Step

无（暂停）。重启条件：用户重开 CI 话题，或 02x 战役收尾触发 R4 重估。
