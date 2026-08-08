# Plan: EVH-024 Credentialed Release Acceptance Diagnosis

> 类型: issue / 诊断 / 测试反馈设计 | 状态: 从 Harness Run Bundle change 拆出，待独立 OpenSpec change | 更新: 2026-08-06

## 背景 / 现状

EVH-024 的 credentialed release selector 是唯一的 full-real public-entry 验收。它覆盖
固定中文请求、模型主导的 HITL1、自然确认、受限的 Python 3.12 来源集、中文报告和引用。
它的 Bundle-authoritative 执行/观察边界已经有确定性测试覆盖，并已随 Harness migration
完成。

最近两次授权运行都在 first_resume:blocked 停止，未产生报告或引用；较晚一次耗时
510.70s。这不是一个适合在普通自动化循环中反复运行的反馈环。当前
UV_OFFLINE=1 make verify 本来就不选择 release lane，且完整确定性验证已通过。

## 决策 / 方案

1. 当前 Harness change 只以确定性证据关闭 EVH-024 的 Bundle-authority 迁移：
   release runner 从 public entry 取得并重新授权选中的 bundle_id，仅从 Bundle-local
   State 与 contained artifacts 观察结果，Bundle 丢失时没有 session/checkpoint/GraphHost/
   workspace fallback。
2. 成功完成真实中文报告与引用的 credentialed execution 是本 issue 的后续人工验收，不是
   当前 structural/lifecycle migration 的归档前置条件。不得把未成功的真实运行标记成通过，
   也不得用 fixture 代替它。
3. 在新的专属 OpenSpec change 形成快速、可复现的诊断环之前，不再为碰碰运气反复执行
   make test-release-e2e。新的真实运行需要单独授权。

## 问题拆分

| 问题 | 正确证据层 | 当前状态 |
| --- | --- | --- |
| release runner 是否绕过 Bundle authority | 确定性 control-plane tests | 已覆盖 |
| 模型/网页调用在哪个阶段违反结构化契约 | 有界、可重放的 provider/phase diagnostic | 缺少快速红绿环 |
| 固定来源集能否产出足够合格的 Wave0/Wave1 证据 | deterministic source-policy and worker-output cases | 部分覆盖，尚未能预测真实模型输出 |
| 一次真实供应商运行能否交付报告和引用 | 手动选择的 full-real acceptance | 尚未通过，不应成为普通 CI |
| make verify 为什么仍偏慢 | JUnit duration profile 和 repository/catalog/process cost | 另见 [2026-08-06-fast-lane-duration-profile.md](2026-08-06-fast-lane-duration-profile.md) |

## 下一 Change 的诊断环

新 change 的第一个任务不是修 prompt 或重跑 release，而是建立以下反馈环：

1. 从现有 redacted release report 提取仅包含 phase、闭合 failure code、结构化响应形状、
   用时和计数的 fixture；绝不保存凭据、原始模型文本、来源 URL/正文或宿主路径。
2. 用该 fixture 在 Wave0/Wave1 adapter/gate 边界创建一个少于 10 秒的确定性红测试。
   它必须能区分 structured_output_invalid、source-floor 不足、tool failure 与未知失败，
   而不是仅断言没有崩溃。
3. 对最小红例子提出并验证排序假设；每次只改变一个变量。只有确定性环变绿后，才申请一次
   新的 credentialed selector。
4. 在真实 selector 中增加或复用有界 phase timing summary，使下一次失败能区分模型、检索、
   图编排和 artifact validation 时间；该 summary 仍不得泄露原始内容。

## 初始假设

1. **结构化输出漂移最可能。** 已观测到额外 fetch_status / baseline_facts 字段；
   若其为主因，重放同一有界响应形状会稳定在 Wave0/Wave1 contract 边界失败。
2. **固定三页来源集与 Wave1 最小新来源数可能不匹配。** 若为主因，使用合规但来源不足的
   deterministic candidate 应在不调用模型时得到相同 blocked category。
3. **单一 selector 同时承担九阶段交付与质量断言，导致故障定位过晚。** 若为主因，phase
   summary 会显示在报告/引用之前已经耗尽；分层 deterministic seam 能把反馈压到秒级。
4. **fast lane 的慢点主要是 catalog、CLI 和全仓库治理扫描，而非测试数量。** 这必须按现有
   duration profile 的 cold/warm 测量验证，不能用删除覆盖来优化。

## 风险 / 取舍

- [误把 deterministic fixture 当真实验收] -> fixture 只作为诊断和回归证据；成功 release
  仍要求一次独立授权的 full-real 运行。
- [为速度删除生命周期/authority 证明] -> 保留最低负责 seam；只移除重复 setup 或把手动验收
  留在手动 lane。
- [再次消耗凭据却没有新信息] -> 没有少于 10 秒的红能力诊断环和单独授权，不运行 selector。
- [增加诊断泄露敏感内容] -> 只记录闭合 code、phase、计数、时长和已批准的响应形状分类。

## 落地关联

该 plan 不授权代码修改或真实运行。后续应创建一个专属 OpenSpec change，例如
diagnose-evh-024-release-acceptance，其 Change Focus 为
deep_research_harness/tests/scenarios/release.py 的 test-only release adapter 与
Wave0/Wave1 的最低负责契约 seam。它必须先实现上述快速红绿环，再决定是否需要 prompt、
source-policy、计时投影或 test-lane 结构调整。
