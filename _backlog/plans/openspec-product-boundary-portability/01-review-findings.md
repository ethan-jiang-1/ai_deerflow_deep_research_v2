# Review 结论

## 1. 原问题不是文件名，而是 owner 混杂

旧 `change-guidance/` 同时包含通用 change practice、agent-workflow policies、Deep Research 路径和
本地 budget。复制到新产品时很难判断哪些应该原样保留，哪些必须改。

## 2. `product/` 应是产品前门，不是第二套 specification

`openspec/product/README.md` 只做产品导向和 owner 路由。Required behavior 留在 specs，pending
behavior 留在 active delta，current facts 留在 code/contracts/tests，精确结构留在
`project-structure.toml`。

## 3. 通用层应按能力分 profile

并非每个项目、每个 Change 都需要 node-agent、human/recovery 或 DeerFlow downstream 规则。因此
core 保持最小，三个 profiles 独立启用，本地 composition 决定实际 policy set。

## 4. Node cognition-versus-code route 是承重契约

旧 `node-edit-map.md` 解决了 Coding Agent 容易“只改 Python”或“什么都改 prompt”的问题。路径可以
退休，但七项语义、顺序和 non-model branch 不能摘要化。

## 5. Harness 必须独立运行

`deep_research_harness/` 是下游应用，不能读取开发治理框架 `openspec/`。治理可以检查应用，应用不能
反向依赖治理。这条边界需要自动化 guard，而不是只写文档。

## 6. README 只做导航，正文不切成碎片

根 README 保持 index；实质规则放在少量、完整、命名清楚的独立文档中。多个 policy identity 可以
由同一完整 profile 文档拥有，不需要每个 identity 一个两三行文件。

## 7. 可移植性用本仓机械证据证明

本 Change 的责任是把源材料整理正确并证明其产品中立、边界完整、可导出。未来其他项目如何采用是
未来工作，不需要在本 Change 中创建 sibling 项目、T0–T4 流程或双仓 archive handshake。
