## Context

当前 Harness 的 `bundle_id` 由 `BundleLifecycle.start()` 随机生成，目录布局由 trusted scope 派生，且 `docs/runtime-architecture.md` 明确 typed result 不暴露 host path。本地 operator 已有现成入口：`make demo-scripted`、`make demo-fixture-graph`、`make demo-sessions` 等。soft bundle CLI 需要在这些入口外面加一层无状态 root 句柄，把用户可读的 root 与真实 `bundle_id`、repository-relative 本地记录位置串起来，同时不修改 product `deep_research` 工具 schema。

## Goals / Non-Goals

**Goals:**
- 提供 operator-only CLI：`create / run / bind / status / path / inspect / phases / list`。
- `soft_bundle_root` 作为唯一无状态句柄，不维护全局 `name -> root` 映射。
- 只输出 repository-relative local record location，不输出绝对 host path。
- 所有记录都是 operator 侧观察，绝不作 lifecycle 输入。
- 复用现有 Make target 与 `demo-sessions`，不碰 Harness 核心。

**Non-Goals:**
- 修改 product `deep_research` tool schema 或增加 lifecycle action。
- v2 的 `history` / `use`。
- 003 / 004 真机模式的第一版支持。
- 跨机器、多用户共享。
- 把 soft bundle root 变成 product 公开路径或 lifecycle 身份。

## Decisions

### 1. CLI 是 Harness 外面的薄 wrapper

`scripts/soft_bundle.py` 只做组合与记录：
- `create` 只创建 soft root + `manifest.json`。
- `run` 调用现有 Make target，解析 stdout 中的 `Run Bundle: b_xxx`，拿到合法 `bundle_id` 后再解析 repository-relative 位置。
- `bind` 接受 product 已返回的 `bundle_id`，只做 operator 侧记录。
- `inspect` 委托 `make demo-sessions DEMO_ARGS="inspect <bundle_id>"`。
- `phases` 读取自己记录的 `bundle_local_path` 下的 `state.json`、`work/...` 文件。

备选：直接改 Harness 让 bundle 支持用户命名。被否，因为 `BundleLifecycle` 和 `REG-016` 都明确 bundle 身份不由调用方选择，路径不能成为公开契约。

### 2. 无状态 root，不用全局映射表

每个 soft bundle root 自带 `manifest.json`。`name` 只是备注。后续命令都只收 root，不查注册表。这样 CLI 可替换、可迁移，MD/skill 每步显式携带 root。

### 3. 路径只允许 repository-relative

所有输出和记录都使用 harness-relative 路径，例如 `.deep-research-demo-runs/workspace/deep-research/scopes/<bucket>/<bundle_id>`。`create --root` 只接受 repository 内的安全相对路径，拒绝绝对路径、`..`、`.`、空段以及 repository 外路径。`list` 只扫描 operator soft-bundle 父目录（`.deep-research-demo-runs/workspace/soft-bundles`），不扫描 Harness `deep-research/scopes`。绝对 host path 不出现在 CLI 输出中。

### 4. 生命周期权威保持原样

soft bundle 的 manifest、`bundle_local_path`、`bundle_id` 记录都只是 operator 侧观察。CLI 不把 path 喂给 `start/resume/refine/status/cancel`；`status` 和 lifecycle 的 `status` 不是同一个东西。删除或不可用的 bundle 仍保持 unavailable，不允许通过记录恢复。

### 5. v1 只支持 mode 001

`run --mode 001` 使用 `make demo-scripted`（打印 bundle id），必要时 fallback 到 `demo-fixture-graph` + mtime。003/004 在后续迭代再加，不在本 change。

## Risks / Trade-offs

- [mtime fallback 有并发风险] → 默认优先解析 stdout；mtime 只是 fallback，且本地单机场景足够。
- [path 输出可能被误当成 lifecycle 输入] → spec 明确禁止；CLI 不提供把 path 转成 lifecycle action 的路径。
- [operator CLI 与 product 边界模糊] → 文档和 spec 都标注 operator-only，不注册为 product `deep_research` action。
- [manifest 可能因 bundle 删除而指向不存在路径] → 查询时先验证存在性，失败返回 bounded unavailable，不恢复。
