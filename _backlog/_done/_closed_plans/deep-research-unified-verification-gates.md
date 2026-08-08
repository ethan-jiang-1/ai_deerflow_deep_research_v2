# Plan: Deep Research Unified Verification Gates

> 类型: 治理/流程 | 更新: 2026-07-19 | 状态: distilled successor，待立 change
> 采用阶段: 单人、本地优先；多人协作与远端自动化后续再议
> 来源: `deep-research-spec-gates-and-coverage.md` 的未完成有效部分
> 建议 change: `consolidate-deep-research-verification-gates`

## 背景 / 当前状态

旧 plan 提出的 requirement-test coverage 和证据治理已经由
`evaluation-hardening` 落地并加强：

- 三个 root OpenSpec governance checker 已稳定运行；
- `check_project_req_coverage.py` 检查 alive requirement 的测试背书；
- `check_test_assets.py` 进一步只认可实际 collected deterministic selector 所在
  模块的 `@impl`，并校验 evidence claims、scenario、incident、provider-shape 和
  focused selections；
- PR CI 固定运行 lock、lint、assets、requirement coverage，以及互斥且完整的
  fast/integration/workflow deterministic lanes。

剩余问题已经收敛为验证入口的一致性，而不是重新建设测试治理：

1. 本地、现有 workflow 定义和 OpenSpec archive tasks 仍分别维护命令清单，没有一个
   canonical executable target；
2. 现有 workflow 定义没有显式运行三个 root governance checker；这些 workflow
   当前不是本 change 的运行基础设施或完成依据；
3. `openspec/config.yaml` 的 archive hard done-conditions 只列三个 root checker，
   没有绑定完整 agent deterministic gate；
4. `agent/src/**/*.py` 中已有大量 `@impl`，但未知或 retired ID 不会被机械拒绝；
5. `openspec/governance/req-registry.yaml.tmp` 是失去权威意义的 tracked 临时文件。

## 决策 / 方案

### 1. 一个 canonical `make verify`

在 `agent/Makefile` 增加 `verify` 和薄的 `governance` target。`verify` 固定按现有
零凭据 PR 范围执行：

1. `governance`：三个 root checker；
2. `lock-check`；
3. `lint`；
4. `test-assets`；
5. `test-req-coverage`；
6. `test-fast`；
7. `test-integration`；
8. `test-workflow`。

`test-integration` 已覆盖 `tests/integration` 与 `tests/blocking_io`，包括当前
SQLite durability、viability 和 blocking-I/O 资产；`verify` 不再重复运行它们的
子集 target。该 target 不读取凭据，不运行 Postgres、live 或 release。

### 2. 本地 archive 使用权威入口，现有 workflow 仅做声明式对齐

- `openspec/config.yaml` 的 hard done-conditions 改为要求
  `cd agent && make verify`，不再复制一份易缩水的命令清单；
- `.github/workflows/agent-tests.yml` 与 `agent-release-e2e.yml` 的 deterministic job
  声明式复用 `make verify`，为以后启用远端 CI 时避免另一份命令清单；
- 本 change 只通过本地 contract test 锁定两个 workflow 定义引用 canonical target，
  并锁定 `verify` 的精确 prerequisite 集合。它不要求 GitHub Actions 实际运行，
  不配置 runner、分支保护、required checks、密钥或团队审批。

### 3. 校验 production `@impl` 引用

扩展 `check_project_req_coverage.py`：

- 保留现有测试侧 alive requirement coverage 行为；
- 扫描 `agent/src/**/*.py` 中出现的 `@impl` ID，包括模块 docstring 和行内注释；
- 未登记或 registry 中标为 `[DEPRECATED]` 的 source `@impl` 使 checker 失败，并
  报告 ID 与文件；
- 不要求每个 alive requirement 都必须有 production source 标注，source 标注仍是
  implementation ownership，不替代 collected test evidence。

为 unknown source ID、retired source ID、合法 source ID 和现有测试 coverage 行为保留
最小正反 fixture。

### 4. 删除过期临时 registry

删除 tracked `openspec/governance/req-registry.yaml.tmp`。唯一 registry 继续是
`req-registry.yaml`；不建立第二份 catalog 或同步机制。

## 验收

- `cd agent && make verify` 在无模型、无外网凭据环境全绿；
- OpenSpec archive hard done-condition 只引用本地 canonical target；
- 两个现有 workflow 的 deterministic job 定义引用 canonical target，且该声明由本地
  contract test 校验；远端 workflow 运行状态不属于验收；
- 从 `verify` prerequisites 删除任一 gate 时 contract test 失败；
- 添加 `@impl XYZ-999` 或 retired ID 到临时 source fixture 时 coverage checker 失败；
- 当前 source/test `@impl`、90 个 evidence claims 和 deterministic lane partition 全绿；
- `git ls-files openspec/governance/req-registry.yaml.tmp` 返回空。

## Non-Goals

- 不创建 `GATES.md` 或 `run_gates.sh`，避免与 spec、policy、Makefile 和 CI 重复；
- 不新增测试框架、coverage 百分比或第二份 requirement-to-test catalog；
- 不把 doctor、configure、infra probe、Postgres、live 或 release 放入无凭据 PR gate；
- 不建设或启用远端 CI，不配置 runner、branch protection、required checks、secrets、
  团队审批或发布自动化；多人协作治理留待项目进入相应阶段后另立 change；
- 不建立通用 backend/frontend diff gate；protected-boundary 比较继续由具体 downstream
  change 按 apply base 执行；
- 不改变现有 test-evidence authority、asset classes、authenticity 或 selector 语义。

## 风险 / 取舍

- **[风险] 未来启用远端 CI 后，单一 step 的日志分段较粗。** -> Make 会打印每个
  prerequisite 的命令与失败 target；当前阶段只保证 workflow 定义不会另建清单，
  不把远端运行体验提前纳入本 change。
- **[风险] 全量 `verify` 让文档 change 也跑 deterministic suite。** -> 这是 archive
  hard done-condition 的有意单机成本，只在归档前承担；credentialed lanes 仍排除。
- **[风险] source 注释扫描误读示例文本。** -> 只扫描 `agent/src/**/*.py` 的
  `@impl` payload，并用 registry 语法解析，不扫描文档或 archived artifacts。

## 落地关联

下一步通过 OpenSpec proposal 创建 `consolidate-deep-research-verification-gates`。
实现只涉及治理脚本、Makefile、现有 workflow 定义、contract tests、OpenSpec authoring
guidance 和删除失效临时文件；不建设远端 CI，不修改 Deep Research runtime behavior。
