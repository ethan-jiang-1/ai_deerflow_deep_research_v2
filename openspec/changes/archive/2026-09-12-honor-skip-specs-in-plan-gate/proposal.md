## Why

发现 #1（治理工具 bug）：原生 OpenSpec `schemas/spec-driven/schema.yaml` 明确规定，
行为不变的纯重构/tooling/docs 可在 `.openspec.yaml` 设 `skip_specs: true` 以合法地
零 delta，并强调「不要为了通过验证而编造 requirement」；项目自己的
`openspec/governance/architecture-policy.md` 也规定「语义 requirement 变化时才需要
owning delta」。但 `check_project_specs.py --change`（`--phase plan` 的 delta-specs
组件）忽略该标记、对任何零 delta 的 active change 一律 fail closed，使 manifest-only
结构同步（如 `2026-09-12-rename-work-unit-storage-probe`）无法通过 admission——与框架
schema 和项目自身政策冲突。

## What Changes

- `openspec/governance/check_project_specs.py`：`validate_selected_change_delta_specs`
  在零 delta 分支读取 `.openspec.yaml`——
  - `skip_specs: true`（且元数据为合法扁平映射、声明已知 schema、值为布尔真）→ 通过；
  - 标记不可信（非扁平映射 / 未知 schema / `skip_specs` 非布尔）→ fail closed，报
    `selectedChangeSkipSpecsInvalid`；
  - 无标记 → 维持既有 `selectedChangeEmpty` fail closed。
  - 非零 delta 的 change 不受影响，仍照常校验。
- `openspec/tests/governance/test_project_gate.py`：新增 4 个 selected-change 用例
  （marked-pass / false-fail / non-boolean-fail / no-schema-fail），保留既有 2 个
  零 delta fail-closed 用例。
- 无运行时、无 spec、无其他 checker 改动。

## Capabilities

### New Capabilities

（无——纯治理 checker 行为修正。）

### Modified Capabilities

（无。`.openspec.yaml` 声明 `skip_specs: true`。delta 语义未变：语义变化仍需 delta；
本 change 只让 checker 与原生 `skip_specs` 语义及 `architecture-policy.md` 对齐。）

## Impact

- `openspec/governance/check_project_specs.py`（零 delta 分支 + 元数据读取 + 新 check 标签）
- `openspec/tests/governance/test_project_gate.py`（+4 用例）
- 无 `deep_research_harness/src`、无 spec、无 `deerflow/` 改动。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_project_specs.py` ——
  selected-change delta-specs scope 的唯一权威；本 change 修正其对原生 `skip_specs`
  标记的处理。
- **Seam classification:** deterministic-guardrail —— 修正确定性治理检查器的 admission
  规则，使其与框架 schema 和项目政策一致；无认知面、无人工决策面、无运行时行为变化。
- **Question:** 能否让 selected-change delta-specs 检查器认可合法的 `skip_specs: true`
  零 delta 变更，同时仍对不可信标记与无标记零 delta fail closed？
- **Necessary adjacent/external contracts:** `openspec/governance/architecture-policy.md`
  与原生 OpenSpec `spec-driven` schema（`skip_specs` 语义来源，只读）；`check_project_gate.py`
  （`--phase plan` 的 delta-specs 组件调用方，本次不改）；`openspec/tests/governance/test_project_gate.py`
  （确定性证据缝）。
- **Evidence seam:** `python3 -m unittest discover -s openspec/tests/governance` 全绿
  （含新增 4 例）；两个 delta-less active change 的 `--phase plan` exit 0。
- **Not in scope:** 其他五个治理 checker；delta 语义本身（语义变化仍需 delta）；任何
  `deep_research_harness/` 代码；`.openspec.yaml` 的通用 YAML 校验（只解析本仓写出的扁平
  标量元数据，遇嵌套即 fail closed）；`deerflow/`。
- **Triggered review policies:** none: 纯 OpenSpec-only 治理 checker 行为修正，无新运行时路径、无认知面、无 workflow outcome、无 node-agent 面。
