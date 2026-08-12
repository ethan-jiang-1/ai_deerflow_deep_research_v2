# C-004 - Separate The Three Workspace/Bundle Concepts

> Stage: 2 - `retire-stale-context-concepts`
> 类型: `UNAMBIGUOUS-RETIRE`
> 状态: **REVIEWED - PLANNING ONLY; NOT AUTHORIZED FOR APPLY**

## 调整内容到底是什么

修正 `deep_research_harness/CONTEXT.md` 将三个不同所有者的概念混为一个 `workspace`
或 `Bundle` 的问题：

- **DeerFlow host workspace** 是 DeerFlow 提供的文件系统工作区；Deep Research 不拥有
  它，但在其中存放自己的资料。
- **Deep Research Run Bundle** 是 Deep Research 为一轮研究持久保存的文件系统容器，位于
  host workspace 的 `deep-research/scopes/<scope>/<bundle-id>/`。其中的
  `Bundle-local Research State` 才是该 Run 生命周期的唯一权威状态；Bundle 本身还容纳
  请求、工作产物、证据、报告和诊断。
- **Evaluation Run Workspace** 是 Cognitive Evaluation Runner 在
  `evals/runs/<execution-id>/workspace/` 创建的私有执行目录。它既不是 DeerFlow host
  workspace，也不是 Deep Research Run Bundle 的父目录或生命周期 authority。相同
  execution root 下的 `bundle/` 是它的同级、不可变 Evaluation Run Bundle。

目标 glossary 只保留以上稳定的所有权和边界事实；不把它写成目录布局手册，也不改变
现有目录布局、storage 或 runtime contract。

## 主要风险

- 只改一处会使 glossary、Evaluation spec 和说明文档对 Evaluation workspace 的语义不一致。
- 把路径讲得过细会使 glossary 随内部目录重构而漂移；讲得过少又会失去“为何不可混用”的
  execution isolation 与 owner 信息。
- 改名而不全量同步会打断读者对既有 `Evaluation Run Workspace` 术语的映射。

## 可能副作用

- 读者会看到 `workspace` 仍分别用于 DeerFlow host 和 evaluation runner，必须依赖
  `host` / `Evaluation Run` 前缀判断 owner。
- 过去依据“workspace contains Bundle”理解评估路径的读者，需要改以 owning runtime/spec
  了解真实 layout。
- 复审可能发现其他将 Evaluation Bundle 当成主产品 Run Bundle、或将 evaluation workspace
  当作 host workspace 的残留；这些必须单独登记，不能自动扩入本项。

## 控制与停止条件

- 只处理 evaluation vocabulary；不改变 Runner、`evals/runs/`、主产品 Run Bundle、
  DeerFlow host workspace 或任何 lifecycle 行为。
- OpenSpec change 中先确认三个 owner 的词汇定义，再同步 prose；不扫描 DeerFlow 源码。
- 与 `cognitive-evaluation-suite`、`deep-research-harness-run-bundles` 的 main specs
  交叉核对，不能为术语整齐而改变 required behavior。
- 新发现先登记，不自动扩入 change；若诚实定义需要变更 runtime layout 或术语重命名涉及
  未审的 API/test 范围，停止并转为独立 code work。

## 审阅结论

- [x] 调整内容准确：2026-08-12，已确认 Run Bundle 是 host workspace 中的持久容器，
  `Bundle-local Research State` 是其内部 lifecycle authority；evaluation workspace 是独立
  的 Runner-owned 目录。
- [x] 风险与副作用已充分披露
- [x] 批准进入 Stage 2 planning（不包含创建 OpenSpec change 或 apply 授权）
- [ ] 需要修改或补充，原因：
