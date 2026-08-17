# BUG-032: uv 缓存读取 `Operation not permitted` 导致 `make demo-scripted` 等本地命令直接挂

> 严重级别: P1 | 发现: 2026-08-17 | 状态: 已修复

## 症状

在受限/沙箱环境中运行：

```bash
cd deep_research_harness
make demo-scripted
```

会立即失败：

```
error: failed to open file `/Users/bowhead/.cache/uv/sdists-v9/.git`: Operation not permitted (os error 1)
make: *** [demo-scripted] Error 2
```

同样的错误也会影响 `make demo-fixture-graph`、`make demo-sessions`、`make demo-real-embedded-smoke` 等所有走 `uv run --locked --no-sync` 的本地命令。

## 根因

`uv` 默认读取全局缓存 `/Users/bowhead/.cache/uv`。在沙箱/受限权限环境下，uv 访问缓存里的哨兵文件 `sdists-v9/.git` 时被系统返回 `EPERM`（不是 `EACCES`）。普通 `cat`/`open` 读同一文件正常，说明是 uv 对该路径的访问模式与沙箱规则冲突，而不是文件权限本身的问题。

本机绕过方式已验证：

```bash
UV_NO_CACHE=1 make demo-scripted
```

或

```bash
export UV_NO_CACHE=1
make demo-scripted
```

## 复现

```bash
cd deep_research_harness
make demo-scripted
# 期望：fixture demo 跑通
# 实际：uv 缓存 EPERM 直接退出
```

## 修复关联

- 短期：本地脚本统一加 `export UV_NO_CACHE=1`（已在 `_backlog/_local_demo/*.sh` 处理）。
- 长期：评估 Makefile 是否默认加 `UV_NO_CACHE=1`，或修复 uv 缓存目录在沙箱中的访问问题。

> 修复: 已修复（`fix-local-demo-tooling`：Makefile 默认 `export UV_NO_CACHE=1`，可 `UV_NO_CACHE=0` 覆盖）。
