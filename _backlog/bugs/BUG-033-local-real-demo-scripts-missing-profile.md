# BUG-033: `_backlog/_local_demo` 的真机脚本缺少 `PROFILE`，一跑就报 Usage 错误

> 严重级别: P1 | 发现: 2026-08-17 | 状态: 活跃

## 症状

原 `_backlog/_local_demo/run_real_demo.sh` / `run_real_demo_interactive.sh` 运行时会直接失败：

```bash
make demo-real DEMO_ARGS="--scripted --question \"...\""
# 实际输出：
# test -n "" || { echo "Usage: make demo-real PROFILE=demo"; exit 2; }
# Usage: make demo-real PROFILE=demo
# make: *** [demo-real] Error 2
```

不会进入真实的 Deep Research 流程。

## 根因

Makefile 的 `demo-real` 目标强制要求 `PROFILE` 变量（通常为 `demo`），但这两个本地脚本只传了 `DEMO_ARGS`，没有传 `PROFILE`，因此 `make` 在 `entry-preflight` 之后立即因变量为空退出。

## 复现

```bash
cd _backlog/_local_demo
./run_real_demo.sh 'test'
```

## 修复关联

- 本地已把入口收敛为编号脚本：
  - `run-003-real-auto.sh` → 真机全自动 embedded smoke
  - `run-004-find-bugs.sh` → 真机交互 Gateway，且已带 `PROFILE="${PROFILE:-demo}"`
- 长期：若保留 `_backlog/_local_demo` 脚本，需统一加 `PROFILE` 默认值；或直接废弃旧命名，以 `run-001~004` 为准。
