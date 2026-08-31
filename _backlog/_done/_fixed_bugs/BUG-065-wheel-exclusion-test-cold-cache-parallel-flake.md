# BUG-065: wheel 排除契约测试在全树冷缓存并行首跑下一次性假红（不可稳定复现）

> 严重级别: P2 | 发现: 2026-08-31 | 状态: 已修复（timeout 60s → 300s）
>
> 发现场景: `2026-08-31-doc-gate-docs-layer` change 的 apply 收口（task 4.3 佐证跑），
> 全树并行调用——该调用方式**不是** `make verify` 的任何车道（verify 把测试拆成
> fast/integration/workflow 三条车道分别跑），会踩到的是 `make test`（全树 + `-n 4`）。

## 症状

`cd deep_research_harness && pytest tests -n 4 -m "not (requires_llm or release_e2e or periodic or workflow)"`
（本会话首次全树并行跑，冷缓存）→ **1 failed**：

```
FAILED tests/contract/test_live_architecture_contract.py::test_production_wheel_excludes_fixture_package
2971 passed, 4 skipped, 23 warnings in 31.77s
```

该测试构建生产 wheel 并断言 `src_fake` fixture 包未被包含——fixture 隔离铁律的契约守卫。
单独串行跑约 29s（真实打一次包，是全仓最贵的单测之一）。

## 诊断对照（2026-08-31 当场做了三组负例对照）

| # | 跑法 | 结果 | 用时 |
|---|------|------|------|
| 1 | 全树 `-n 4`（改动在场，冷缓存首跑） | ❌ 1 failed | 31.8s |
| 2 | 同测试**串行**单跑（改动在场） | ✅ 过 | 29.1s（单测） |
| 3 | `git stash -u` 清树后，同命令全树 `-n 4` | ✅ 2972 全过 | 114s |
| 4 | stash pop 改动恢复后，同命令复跑 | ✅ 2972 全过 | 33.5s |

结论：同样的代码、同样的命令，红一次后再不可复现 → flake；改动与打包零交集，
排除因果。附带异常信号：同命令用时在 32s/114s/33s 间大幅波动，支持「负载/竞速」假说。

## 根因（负例控制坐实的失败通路）

`test_production_wheel_excludes_fixture_package` 给 `uv build` 的 `timeout=60`
在「冷/无缓存 + 全树 `-n 4` 满载」下不够：串行冷构建就要 ~29s，4 路负载下隔离
构建环境（hatchling 取材）更容易越过 60s → `subprocess.TimeoutExpired` 假红。

三个静态排除 + 一个直接证明：
- **无并发构建者**：全仓唯一 `uv build` 调用就是本测试 → 同树 build/ 竞态出局；
- **hatchling 后端**：PEP 517 隔离构建，不往源码树写 build/egg-info → 项目树副作用出局；
- **复现率**：修复前同调用 5 次仅首跑（冷缓存）1 红，其后 4 连绿 → 「冷缓存首跑」假说吻合；
- **失败通路直接可达**：临时把 timeout 探针改 1s → 精确复现
  `TimeoutExpired: Command ['uv','build',...] timed out after 1 seconds`（负例控制）。

## 复现

无稳定复现路径（这正是问题）。建议的下一次尝试：连续多次全树 `-n 4` 采样估计
复现率；如再现，先比对 wheel 构建目录是否被并发共享（诊断的第一 suspects）。

## 修复记录（2026-08-31）

落在测试自身机制 → 按拆分原则走 `test:` 提交，不开 change（wheel 排除断言本身
未动，`fixture-source-isolation` 语义无变化、无产品风险）：

- `timeout=60 → 300`，注释锚定 BUG-065 与理由（冷构建 ~29s + 4 路负载；300s
  仍保留上界，真挂死 5 分钟内暴露）；
- 验证：严苛环境（`UV_NO_CACHE=1` 全树 `-n 4`）2972 全过 + 单测串行过 + ruff 绿。

残留不确定性（如实记录）：原始红未能当场捕获断言详情，timeout 是唯一被演示
可达的失败通路而非对当日事件的直接取证；若未来再现红灯且非 TimeoutExpired
形态，重新开账并升级排查（此时才考虑 change 载体）。
