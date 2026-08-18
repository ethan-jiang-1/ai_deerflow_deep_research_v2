# Plan: Soft Bundle Session CLI（无状态 root 句柄）

> 类型: 设计 | 更新: 2026-08-17 | 状态: 最终共识

## 背景

- Deep Research Harness 的真实 Run Bundle id 是 `b_<random>`，不透明、随机、不可读。
- 本地跑完后必须靠 `find ... -name 'b_*'` 找最新 bundle，才能继续 inspect / phases。
- MD 或 skill 无法在运行前先要一个稳定句柄，也无法在运行后稳定地查回目录、日志、内容。
- 需要一个新的句柄：**soft bundle root**。
- 001~004 作为流程测试，必须使用固定研究问题（control environment），难度递增，便于对照和找 bug；不开放自定义问题。

## 现实约束（研究结论）

- `BundleLifecycle.start()` 只接受 trusted scope + request text；`bundle_id` 由 `new_bundle_id()` 随机生成，不由调用方选择。
- Bundle 目录由 `scope_bucket(effective_user_id, outer_thread_id)` 派生，布局私有：
  `.deep-research-demo-runs/workspace/deep-research/scopes/<bucket>/<bundle_id>/`
- `docs/runtime-architecture.md` 明确：typed result 只暴露 bounded `bundle_id`，不暴露 host path；不接受 caller-selected identity 或 filesystem root。
- 现有 spec 的历史原因：绝对 host path 不稳定、不安全、会泄漏机器信息；path 一旦成为 lifecycle 输入，就会绕过 Bundle-loss / scope 隔离防线。
- 但 spec 允许 operator 侧输出 **repository-relative local record location**（例如 `.deep-research-demo-runs/workspace/...`），不允许绝对 host path。
- 因此不改 product `deep_research` 工具 schema，不给它加 `create <name>` / root 参数。
- operator 层已有现成入口，soft bundle CLI 只做这些入口外面的薄 wrapper：
  - `make demo-scripted`：打印 `Run Bundle: b_xxx`
  - `make demo-fixture-graph`：001 最简图验证
  - `make debug-scripted-real-workflow`：打印 `bundle_id` 和 event journal 路径
  - `make demo-real-embedded-smoke`
  - `make demo-real PROFILE=demo`
  - `make demo-sessions DEMO_ARGS="inspect <bundle_id>"`：查节点日志

## 最终方案

### 核心概念

| 概念 | 含义 | 是否路由 |
| --- | --- | --- |
| `soft_bundle_root` | 一个安全目录路径，指向一个 soft bundle 的根 | **是，唯一句柄** |
| `bundle name` | 备注名字，写在 root 内的 `manifest.json` | 否，只给人看 |
| `bundle_id` | 某一次真实运行的 `b_xxx` | 否，只记录在 root 内 |
| `bundle_local_path` | 真实 Run Bundle 的 **repository-relative 本地记录位置** | 否，operator 侧记录，绝不作 lifecycle 输入 |

### 命令面（v1）

```text
soft-bundle create [--root <path>] [--name <name>] [--question <q>] [--mode <mode>]
soft-bundle run     <soft_bundle_root> [--question <q>] [--mode <mode>]
soft-bundle bind    <soft_bundle_root> <bundle_id>
soft-bundle status  <soft_bundle_root>
soft-bundle path    <soft_bundle_root>
soft-bundle inspect <soft_bundle_root>
soft-bundle phases  <soft_bundle_root>
soft-bundle list    [--under <parent_dir>]
```

规则：

- 所有后续命令只收 `soft_bundle_root`，不查全局映射表。
- `create` 返回 `soft_bundle_root` 和 `name`；MD/skill 保存 root 继续后续步骤。
- `name` 不参与路由；`manifest.json` 自描述。
- `create` 幂等：root 已存在且含合法 `manifest.json` 时，返回现有 root；root 已存在但不是 soft bundle 目录时，直接失败。
- `path` 只打印 repository-relative local record location，不打印绝对 host path；该输出是 operator 复盘信息，**不能喂回 `start/resume/refine/status/cancel`**。

### 默认 root

代码已经定义（`scripts/_demo_core.py`）：

```text
_DEMO_BUNDLE_ROOT_NAME = ".deep-research-demo-runs"
root      = deep_research_harness/.deep-research-demo-runs
workspace = deep_research_harness/.deep-research-demo-runs/workspace
```

规则：

- 所有路径都按 **harness-relative** 处理，基准目录是 `deep_research_harness/`。
- `create --root <path>`：用户给路径则用用户路径；只接受安全相对路径。
- `create` 不给 root：用默认 workspace root 作为父目录，生成
  `.deep-research-demo-runs/workspace/soft-bundles/<generated>/`
  并返回完整 `soft_bundle_root`。

### 目录与 manifest

```text
<soft_bundle_root>/
  manifest.json
  bundles/
    <bundle_id>.json
```

`manifest.json`：

```json
{
  "schema_version": 1,
  "name": "我的电池研究",
  "mode": "001",
  "question": "...",
  "current_bundle_id": "b_xxx",
  "created_at": "...",
  "updated_at": "..."
}
```

`bundles/<bundle_id>.json`：

```json
{
  "schema_version": 1,
  "bundle_id": "b_xxx",
  "bundle_local_path": ".deep-research-demo-runs/workspace/deep-research/scopes/<bucket>/<bundle_id>",
  "mode": "001",
  "question": "...",
  "created_at": "..."
}
```

### 为什么无全局映射

- root 本身就是路径，见到 root 即可直接操作，无状态、可替换、可迁移。
- MD/skill 每步显式携带 root，系统不需要“记住” name。
- `name` 只是 `manifest.json` 里的备注，不参与路由。

## 落地

### 第一版原型：`_backlog/_local_demo/soft_bundle.py`

- `create`：只创建 soft root + `manifest.json`，不调用 Harness。
- `run`：
  - mode 001：调用 `make demo-scripted`，从 stdout 解析 `Run Bundle: b_xxx`；失败时退回 `demo-fixture-graph` + mtime fallback。
  - 拿到合法 `bundle_id` **之后**，才在 `.deep-research-demo-runs/workspace/deep-research/scopes/` 下解析它的 repository-relative 位置，写 `bundles/<bundle_id>.json`，并更新 manifest 的 `current_bundle_id`。扫描只用于 operator 记录，不用于“发现/选择”bundle。
- `bind <root> <bundle_id>`：skill 从 product `deep_research` 结果里拿到 `bundle_id`，交给 CLI；CLI 只负责解析并记录 repository-relative 位置。
- `inspect`：委托 `make demo-sessions DEMO_ARGS="inspect <bundle_id>"`。
- `phases`：读取 CLI 自己记录的 `bundle_local_path` 下的 `state.json`、`work/...` 文件。
- `path`：只打印 `bundle_local_path`（repository-relative），不打印绝对 host path。
- 不改 `src/deerflow_deep_research/` 下的 product 代码。

### OpenSpec 落地

- 原型验证通过后，开 `openspec/changes/<change>`，spec 对象是 operator CLI，不是 product lifecycle。
- Spec 写死边界：soft bundle root 是 operator 命名空间，不是 Harness 的 public path 或 lifecycle 输入。
- Spec 必须对齐现有 `RDO / RWB / REC / RSV / REG-016`：只输出 repository-relative local record location，不输出绝对 host path；拿到 `bundle_id` 后才解析本地位置；任何 path/记录都不能作为 lifecycle authority。
- 将来若要让 skill 原生控制，把该 CLI 注册成 skill 可调用的本地命令/tool；skill 自己保存 `soft_bundle_root`，再拿 product 返回的 `bundle_id` 交给 CLI。
