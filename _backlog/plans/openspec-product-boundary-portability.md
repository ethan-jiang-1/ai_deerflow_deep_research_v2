# OpenSpec 产品边界与可移植性最终方案

> 状态：已由 `make-openspec-practice-portable` 实施并验证
> 范围：只重构本仓库 `openspec/` 的 authoring / governance practice

## 初心

让 OpenSpec 实践更容易迁移到不同产品：

- Deep Research 特有内容尽量集中在 `openspec/product/` 和本地 composition；
- `openspec/change-guidance/core/` 与 `profiles/` 保持产品无关；
- 不同产品采用时主要替换产品入口、本地路径、policy 组合和本地 authority；
- 不要求本 Change 创建或修改另一个项目；
- 不修改 Deep Research runtime，也不读取或修改 `deerflow/`。

## 最终结构

```text
openspec/
├── product/
│   └── README.md
├── change-guidance/
│   ├── README.md
│   ├── core/change-practice.md
│   ├── profiles/workflow-control/workflow-control.md
│   ├── profiles/node-agent/node-agent.md
│   ├── profiles/deerflow-downstream/deerflow-downstream.md
│   └── local/deep-research.md
└── governance/
    ├── change_guidance_kernel.py
    ├── check_change_guidance.py
    └── portable_change_guidance_export.py
```

## 边界

### Portable

- `core/change-practice.md`：owner、scope、authority、evidence、change admission；
- `workflow-control`：状态、失败、恢复、人类决定与 control placement；
- `node-agent`：LLM node 的 cognition-versus-code authoring gate；
- `deerflow-downstream`：只使用上游 public API 的 downstream 边界；
- `change_guidance_kernel.py`：不依赖仓库状态的纯 grammar validator。

### Project Local

- `product/README.md`：Deep Research 产品入口和 owner 路由；
- `change-guidance/local/deep-research.md`：本地 paths、budgets、Program Focus、information map；
- `config.yaml`、checker wrapper、structure registry、specs 和 requirement IDs；
- `deep_research_harness/AGENTS.md`：应用自己的完整 coding route。

## Node-Edit-Map 核心保留

文件名不是 authority，但以下七项必须显著且完整：

1. 四类 seam：`cognitive-program`、`deterministic-guardrail`、`human-decision`、`wiring`；
2. cognitive control contract；
3. prompt 与 trusted/untrusted context；
4. structured candidate、feedback、bounded repair、stop condition；
5. deterministic proof 与 cognitive evaluation；
6. deterministic handoff owners；
7. 明确的 non-model branch。

它们现在同时存在于 portable node-agent profile 和 Harness 自有 coding guide，并由 planted-negative
tests 防止省略、降级或错序。

## 依赖方向

```text
openspec/  ──检查/约束──▶  deep_research_harness/
deep_research_harness/  ──不得依赖──▶  openspec/
```

Harness 不读取、导入、执行或链接 `openspec/`；OpenSpec governance tests 位于
`openspec/tests/governance/`。

## 完成证明

- portable allowlist 只包含 core、所选 profiles 和纯 kernel；
- product/local/spec/change/archive/test/evidence material 被 denylist 排除；
- 每个 portable file 记录 SHA-256；
- 产品/path/source-ID literals、broken links 和 digest tampering 会失败；
- `product/README.md` 是唯一产品前门；
- 旧 policy 路径和 `product/deep-research.md` 已退休；
- OpenSpec governance、strict Change validation、Harness verify 和 diff checks 通过。

## 文档

- [Review 结论](openspec-product-boundary-portability/01-review-findings.md)
- [边界与文件矩阵](openspec-product-boundary-portability/02-boundary-and-file-matrix.md)
- [迁移与验证](openspec-product-boundary-portability/04-migration-and-proof.md)
