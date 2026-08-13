# 60 - Progressive Execution

> 角色: 阶段关卡与 OpenSpec change 编排
> 规则: 一次一个 active change；checkbox 表示本 plan 阶段，不替代 change `tasks.md`

## Stage 0 - Reproducible Inventory

- [ ] 记录新的 clean/tracked Git 快照，并区分本计划文件与用户已有 worktree 内容。
- [ ] 重跑 tracked-file、current term、legacy/compat、entry/config、serializer/export、spec/requirement、
  test selector/registry 扫描。
- [ ] 为 candidate register 每项补 owning spec/IDs、surface grade、static/dynamic consumer、persisted
  data 与外部 unknown。
- [ ] 枚举 current public/operator/evaluation entry surfaces及其用户和唯一责任。
- [ ] 枚举 current persisted schemas/closed enums/config formats与已知 readers/writers。
- [ ] 复核所有已有 negative guards 的 planted/known violation 与最近 freshness。
- [ ] 选择首个 independently replaceable authority cluster；不得以最多命中或最多 LOC 作为理由。

**Gate 0:** 所有高信号候选可分类；首个 change 不依赖未枚举 consumer/data。

## Stage 1 - Canonical Language Decisions

- [ ] 对 Node cognition、Run/Bundle/Observation、fixture composition、entry surfaces、evaluation artifacts
  分别建立 bounded term table。
- [ ] 区分 synonyms 与 genuinely distinct concepts，给每项一个 owner。
- [ ] 对 public/persisted/model-facing rename 决定 cutover，不把它当 private refactor。
- [ ] 把已批准 term 同步计划放入 owning OpenSpec change；不先单独改 glossary。
- [ ] 明确 CONTEXT、ADR、spec、code、test 各自记录角色。

**Gate 1:** current target vocabulary 足以指导代码和 spec，不存在一个词覆盖两个 authority 或两个词
竞争一个 current identity。

## Stage 2 - First Retirement Slice

首选候选顺序由 Stage 0 证据决定；当前建议比较以下最小 slice：

1. legacy node capability binding；
2. phase-agent AI-facing/runtime language；
3. `full_fake` persisted/public compatibility；
4. Run Session / lifecycle-binding capability retirement；
5. entry/config compatibility cluster。

不是固定按此顺序执行。优先选择消费者和数据范围最封闭、能产生净删除且 recovery 完整的一项。

对选中项：

- [ ] 使用 `openspec new change <name>` scaffold；
- [ ] proposal 写一个 primary causal owner、退休对象、净概念变化、相邻契约和 evidence seam；
- [ ] design 完成 surface/cutover/recovery/guard 决策；
- [ ] delta 定义 target behavior 与 old-input disposition；
- [ ] tasks 使用 red-before-green，并包含 consumer/data inventory、old-entry closure、test/registry/docs sync；
- [ ] apply 后运行 focused tests、相关 lanes、governance 和 full deterministic verify；
- [ ] archive 后更新 candidate disposition，再选择下一 slice。

**Gate 2:** target path 唯一，old writer/entry 已关闭，必要兼容 reader有明确期限或已删除，行为与
negative evidence完整。

## Stage 3 - Repeated Vertical Retirement

对剩余 authority clusters 重复 Stage 2。每个 change 必须满足：

- [ ] 不引入永久 alias、dual-write、fallback controller 或第二 source tree；
- [ ] public/persisted break有 decision authority 和 recovery；
- [ ] private code rename与其行为 owner同批完成；
- [ ] test/fixture/evidence metadata随 owning behavior同步减法；
- [ ] main spec/req registry/structure registry/CONTEXT/current docs同步；
- [ ] 记录保留的 historical/negative matches及理由；
- [ ] 记录净概念和表面变化，新 noun/layer必须退休更多歧义或有复核触发。

**Gate 3:** candidate register 不再有可立即执行但未排期的 `retire/rename` 项；剩余
`decision-required` 都有真实外部/产品决策 blocker。

## Stage 4 - Test And Governance Subtraction Review

- [ ] 查找已删 implementation 的 orphan tests、fixtures、selectors、claims、requirements 和 registry rows。
- [ ] 将只保护旧 implementation shape 的测试替换为 target behavior或删除。
- [ ] 验证所有 anti-resurrection guards仍能检测 planted violation，且 scope不能绕过。
- [ ] 处理 suspended/uncollected test assets与空 scaffolding。
- [ ] 复核 Make/CI lanes、test-assets non-empty discovery和requirement coverage。
- [ ] 复核 main capability names、retired IDs、project structure和current docs routes。

**Gate 4:** suite 只保护 current behavior、approved migration/rejection和必要 negative invariants；没有
orphan metadata 或空扫描假绿。

## Stage 5 - Final Re-audit

- [ ] 重跑 Stage 0 扫描并逐条解释 residual current matches。
- [ ] residual allowlist 只包含 historical、approved compatibility input或negative guard；每项有 owner和
  removal/review trigger。
- [ ] 对 current entry/public/persisted surfaces做第二次 consumer/data review。
- [ ] 对 canonical terms做 glossary/spec/code/test cross-check。
- [ ] 记录净删除 files/LOC/tests/claims/spec requirements和净新增概念；数字只作结果，不作成功理由。
- [ ] 记录未运行 live/release/Postgres/real-Gateway evidence及风险。
- [ ] 生成计划 closeout，总结 retained items、rejected candidates、remaining external blockers和下次
  rot-audit trigger。

**Gate 5:** README 的完成定义全部满足，或剩余 blocker被独立 todo/suspended plan 接管且不会让当前
架构保持双入口/双权威。

## 每个 change 的最低验证

从 repo root：

```bash
python3 openspec/governance/check_project_reqs.py .
python3 openspec/governance/check_project_specs.py .
python3 openspec/governance/check_project_architecture.py .
python3 openspec/governance/check_agent_charter.py .
python3 openspec/governance/check_project_req_coverage.py .

cd deep_research_harness
UV_OFFLINE=1 make verify
cd ..

openspec validate <change-name> --strict
openspec doctor --json
git diff HEAD --check
git status --porcelain=v1 --untracked-files=all
git ls-files --stage deerflow
git submodule status -- deerflow
git -C deerflow status --porcelain=v1 --untracked-files=all
git diff --submodule=short
```

具体 change 还必须添加最窄 focused test 和 cutover/negative-control evidence。上述命令不证明 live
behavior、semantic policy applicability、外部消费者迁移或 upstream compatibility。

## 计划状态更新规则

- 本文件只在阶段 gate 或 candidate disposition 变化时更新；
- 逐文件实施进度留在 active change `tasks.md`；
- 一个 change archive 后再勾选对应 gate，不提前批量完成；
- 若发现 load-bearing product decision，保持 open并请求授权，不用 cleanup 假设替代；
- 若某候选确认仍必要，标记 `rejected` 并写 owner/evidence，而不是让它永远停在 pending；
- 全部关闭后，将整个子目录 `git mv` 到 `_backlog/_done/_closed_plans/`，按 backlog 规则分配
  `CLS-038`（或当时 next available ID）并更新三个索引。

