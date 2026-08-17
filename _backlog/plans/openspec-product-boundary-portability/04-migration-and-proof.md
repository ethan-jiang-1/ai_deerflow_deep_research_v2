# 迁移、兼容、恢复与完成证明

> 角色：source/target 实施顺序、surface cutover、guards、recovery 与 closure 的唯一权威  
> 边界：只改 OpenSpec authoring/governance；不改 runtime，不迁 glossary，不改 `deerflow/`

## 执行原则

- 当前仓库只创建一个 Program Change：`make-openspec-practice-portable`。
- 真实 sibling 优先使用一个 target-native Program Change；若目标治理不支持，则复用已经 active、
  且会按 portable practice 实际执行的真实 changes，或由 target decision owner 批准最小 bounded
  change set；历史 archive 不算 adoption workstream。
- Source Program 用有序 workstreams 隔离 authority seams；workstream 是任务与恢复边界，不是独立
  Change，也不独立 archive。
- 当前 Deep Research behavior、requirement IDs、checker CLI 和 runtime verification 保持不变。
- 新 owner 生效时，同一 Source Change 内更新 current consumers 并退休旧可编辑正文。
- Source Change 在真实 adoption 通过前保持 active；任何跨仓 finding 回到其 owning workstream 修正，
  target 在同一个 adoption change set 中重新验证，不静默 fork，也不因修复轮次增加 Change。
- Source 是 whole-program archive；target adoption change set 在共享 evidence boundary 未闭合前保持 active。

## S0：基线、Consumer Inventory 与 Program Admission

在创建 Source Program Change 前记录：

1. `openspec list --json` 输出，并确认没有重叠 scope 的 active change；
2. 五个 governance checker 的 CLI、0/1 exit contract 与当前 passing baseline；
3. Focus Card、Program Focus、conditional reviews、policy names 和 current fixtures；
4. `change-guidance/`、`config.yaml`、`product/deep-research.md` 的 current inbound links；
5. product exact-member 与 60/80 budget guard；
6. `project-structure`、`deep-research-agent-charter` 和相关 requirement IDs/scenarios；
7. `deep_research_harness/CONTEXT.md` 的 current glossary consumers；
8. `git ls-files --stage deerflow`、submodule status 与 nested worktree cleanliness。

完成条件：每个将被移动的 current entry surface 都有 consumer list、compatibility posture 和 owning
workstream；未知 consumer 不能被“假设不存在”。随后创建 Source Change，其 `## Program Focus`
冻结 S1–S4 的 Candidate / obligation budget、顺序、共享 archive invariant 和 recovery rule。

## S1：Extract Portable Validation Seam

### Authority seam

只把产品中性的 proposal/review grammar 抽到
`governance/change_guidance_kernel.py`。`check_change_guidance.py` 保持当前 CLI，并成为 local wrapper；
现有 Change Guidance prose、paths、policy names 和 member set 在本 workstream 不移动。

### 必须完成

1. 建立 paragraph-level ownership ledger，覆盖 `principles.md`、`change-admission.md`、
   `local-context.md`、全部 conditional review policies 和 `agent-information-map.md`。
2. Pure kernel 只接收显式字符串/结构输入，不遍历 repo、不读取 product/manifest、不执行 commands。
3. Wrapper 继续拥有 current paths、Focus/Program fields、budgets、policy set 和 filesystem checks。
4. Portable validator 移除 Deep Research literals、local paths 与 `DRC/PRS/EVH @impl` IDs。
5. `project-structure.toml` 与 owning project-structure spec 登记新 kernel file；当前 guidance tree 的
   exact members 暂时保持不变。
6. Existing wrapper contract tests 继续从原 CLI 运行；新增 kernel tests 直接调用纯 API。

### Red-before-green

先证明 current implementation 的耦合：

- 中性 project fixture 因 Deep Research path/literal 失败；
- pure grammar 无法脱离 repo filesystem 调用；
- portable source 植入 source requirement ID 时尚不会失败。

再完成 green：

- neutral core fixture 通过；
- current Deep Research fixture 结果不变；
- kernel literal/ID scan 有感知；
- wrapper CLI path、usage 与 0/1 semantics 不变。

### Recovery

若 extraction 改变 current proposal outcome，恢复 wrapper 调用旧 local logic，保留新增 failing fixture
与 finding；不能通过放宽 grammar 让测试变绿。因为本 workstream 不移动 prose，不需要临时 policy path
或 compatibility document。

## S2：Cut Over Kernel、Profiles 与 Local Extensions

### Authority seam

把所有 Change Guidance prose 按
[`02` 文件矩阵](02-boundary-and-file-matrix.md#当前-change-guidance-逐文件处置) 原子迁入：

- `core/`；

- `profiles/workflow-control/`；
- `profiles/node-agent/`；
- `profiles/deerflow-downstream/`；
- `local/`。

### 必须完成

1. Local router 声明 exact enabled profiles、canonical policy names、triggers 与组合规则。
2. 三个 profiles 可独立启用；一个 change 命中多个 profile triggers 时，wrapper 必须要求所有相关
   review records，不能让一个 policy 吞掉另一个。
3. Disabled profile 不出现在可选 policy set，也不产生 proposal field、review table 或 document
   completeness obligation。
4. Deep Research 当前全局 `Seam classification`、Program Focus、operation closeout、module map、
   information-map paths/budgets 保持 local。
5. `openspec/config.yaml` 只组合 rules 与 owner links，不复制 profile 正文或 structure facts。
6. 新增 `portable-change-guidance` capability delta，拥有 portable kernel/profile 的 authoring contract、
   export boundary 与 release criteria；`deep-research-agent-charter` 与 `project-structure` deltas 分别
   拥有 local contributor obligations 和 exact paths/member sets。
7. `project-structure.toml`、`check_change_guidance.py`、focused contract tests、OpenSpec/Harness entry
   documents 和所有 current links 同步 target exact member set。
8. 每个旧 policy path 的 current consumer 原子更新；旧文件在同一 change 删除。
9. Archive 原文保持不变。

### Red-before-green

- core-only fixture 因 current exact policy set 被错误拒绝；
- 两个 profiles 同时触发却只提供一份 review 的 fixture 尚未失败；
- disabled profile policy 尚可被 proposal 选择；
- local Program Focus 被错误纳入 portable export。

Green 后，上述 planted violations 均失败，恢复原 fixture 后重新通过；current Deep Research proposals
继续满足同一 substantive obligations。

### Recovery

若 profile split 破坏 current proposal grammar，保留旧 canonical policy names，通过 wrapper adapter
恢复兼容；不能复制两份 policy prose。若 dependency 设计不闭合，workstream 保持 active，回到 target
profile boundary 修正。

## S3：Product Front Door Cutover

### Authority seam

将 current product navigation entry 从 `product/deep-research.md` 原子迁移到
`product/README.md`；产品语义 owner 不变，glossary 不移动。

### 必须同步

- `openspec/README.md`；
- `openspec/config.yaml`；
- `change-guidance/README.md` 与 local information-map；
- `governance/README.md`；
- `check_change_guidance.py` 的 member/path/budget binding；
- `project-structure.toml` 与 owning project-structure spec；
- deep-research-agent-charter 中拥有 product-entry contract 的 requirement/scenario；
- 所有 current non-archive inbound links 与 negative fixtures。

Cutover 后：

- `product/` exact current member 是 `README.md`；
- 当前 60/80 budget 继续生效；
- README 继续链接 `deep_research_harness/CONTEXT.md`；
- `deep-research.md` 删除，不保留 compatibility copy；
- archive 中历史路径文本不改写，也不被当作 current consumer。

### Red-before-green

- current link 指旧 path 时失败；
- product 目录出现 machine config 或未登记 Markdown member 时失败；
- README 缺 terminology/spec/current-fact/governance owner route 时失败；
- README 越过 hard budget 时失败。

### Recovery

若 current consumer 不能完整枚举，不执行 cutover；继续使用 `deep-research.md` 并修 consumer
inventory。Cutover 已开始后出现漏链，在同一 change forward-fix 或整体恢复旧 path/member guard，
不得保留两个长期入口。

## S4：Candidate Release Gate

Source 在 S1–S3 全部闭合后运行完整 verification、export allowlist 和 digest checks，记录 candidate
commit 与 selected profiles。此时只能声明 `portability candidate`；Source Change 保持 active，不先
archive，也不把尚未被 sibling 采用的 snapshot 写成 portable release。

完成条件：candidate commit 可被 target 固定引用；allowlist、denylist、每个 portable file digest、
source verification 与 planted-negative evidence 完整且可复查。

## T0–T4：真实 Sibling Adoption Change Set

目标仓库创建 `adopt-portable-openspec-practice` change，并严格执行
[`03-adoption-contract.md`](03-adoption-contract.md)。

Source side 只发布固定 revision 和 allowlist，不在当前仓库伪造 sibling runtime。Target 完成：

- byte-identical kernel/selected profiles；
- target-owned product/config/router/wrapper/specs/governance；
- deterministic、node-agent、human/recovery 三个真实 workstreams；
- mechanical fixtures 与 planted negatives；
- `evidence/portable-practice-adoption.md`。

Target adoption boundary 依次完成 T0 foundation、T1 deterministic、T2 node-agent、T3 human/recovery
和 T4 evidence gate。优先在一个 target Program Change 中完成；复用 active changes 或最小拆分时，
T4 evidence 必须给出每个 owning change、commit 与 scope，并证明它实际按 portable practice 执行，
且不得为修复轮次继续增加 Change。完成 T4 后
尚 active 的 target adoption changes 暂不 archive；Source closeout 引用 target repo、commits 与
evidence。Source ratify 前，source 状态保持 “portability candidate”。

### Finding 回流

| Adoption finding | Source 处置 |
| --- | --- |
| 只有改 kernel 才能绑定 product/path | 在 active Source Change 的 owning workstream 修 kernel boundary，发布新 candidate |
| Profile trigger 在 target 不自然 | 在 active Source Change 收窄 trigger 或将规则降为 local；不强迫 target |
| 两项目 structure 不同 | 保持各自 architecture checker，不扩通用 schema |
| 两项目重复同一 local machine fields | 记录为未来最小 binding-schema 候选，不在当前 adoption 临时发明 |
| Target 仍需全仓扫描找 owner | 在 owning Source workstream 修 product/local routing 与 agent-facing evidence |
| Target 复制了 source specs/IDs | Target workstream 失败，在同一个 adoption change set 清理后重跑，不接受 deviation |

## Archive Handshake：Portable Release Closure

只有 T0–T4 无未关闭 kernel/profile finding 时，才把该 source candidate 标记为 V1 portable release。
若 target adoption 触发 source correction，必须：

1. 在仍 active 的 Source Program owning workstream 增补 task 并修正；
2. 重新运行 S1–S4 受影响 guards，发布新 candidate revision/digests；
3. target 在同一 adoption change set 中重新复制而不是手改；
4. 重跑受影响 target workstreams 与 evidence；
5. 重复直到同一 candidate 无未关闭 finding。

通过后，Target 先提交 passing evidence 但保持 active；Source 引用该 target commit/evidence，完成
最终门禁、ratify candidate 并 archive Source Change；Target 再确认所用 candidate 已被 ratify，
strict-validate 并 archive 尚 active 的 adoption changes。

Shared package、generator、architecture schema 或 glossary cutover 不属于本 V1 source/target change set。

## Compatibility Surfaces

| Surface | 等级 | 策略 |
| --- | --- | --- |
| `check_change_guidance.py` command path、arguments、0/1 result | declared project interface | 保持 wrapper 路径与 CLI；内部委托 kernel |
| Focus Card、Program Focus、policy canonical names | agent-facing authoring contract | 保持 current Deep Research grammar；portable baseline更小，由 local wrapper补齐 |
| Conditional review table columns/postures | proposal contract | 迁移路径可变，canonical names/shape 同 change 原子更新 |
| `product/deep-research.md` current path | repository navigation interface | S3 clean cutover，枚举 current consumers，不保留长期 alias |
| Main spec IDs/scenarios、req registry | persisted governance identity | 不改 ID；只在 owning change 更新必要 path requirement |
| `project-structure.toml` | exact structural authority | 继续唯一，不被 product/local schema复制 |
| Archive text | immutable history | 不改写旧路径、术语或 requirement references |
| Runtime behavior/data | out of scope | 无 runtime/data migration |
| `deerflow` gitlink/public API boundary | upstream cross-boundary interface | 指针与 nested worktree不变；不 source-browse 或修改 |

## Guard 与 Planted Negative Matrix

| Boundary | Guard owner / 类型 | Planted negative | 通过证据与 freshness |
| --- | --- | --- | --- |
| Core neutrality | wrapper test + recursive literal/ID scan | Core 加入 `Deep Research`、local path 或 source `@impl` ID | 每次 portable source 变更运行；恢复同 fixture 后通过 |
| Pure validator | kernel unit fixture | Kernel 尝试读取 repo path、执行 shell 或依赖 wrapper global | 每次 kernel API 变更运行 |
| Profile composition | wrapper fixture | 两个 profiles 同时触发却缺少其中一个 review | 每次 profile registry/trigger 变更运行 |
| Profile optionality | core-only fixture | Disabled policy 被 proposal 选择或要求 review | 每次 trigger/profile 变更运行 |
| Review grammar | conditional table fixtures | 缺列、重复表、非法 posture、错误 policy name | 每次 review schema 变更运行 |
| Local composition closure | filesystem fixture | Doc path 越界/缺失、角色重复、enabled profile不完整 | 每次 local binding/entry map 变更运行 |
| Structure single authority | architecture guard + review | Product/local schema 重复 source/test/import/gitlink fields | 每次 product/governance schema 变更运行 |
| Product front door | exact-member/link/budget checks + semantic review | Machine config、未登记 member、owner route缺失、越预算 | 每次 product/entry-doc 变更；review evidence保留在 change |
| Export boundary | allowlist/digest check | Snapshot 包含 denylisted file 或 portable file被 target改写 | 每次 source release与 target adoption |
| Real adoptability | sibling adoption review | 三类 workstream 任一需 fork kernel或复制 source authority | 每个 portable release |
| Upstream scope | gitlink/worktree evidence | Pointer bump 或 nested `deerflow` edit | 每个 source change closeout |

任何 automated guard 都必须展示：安全植入违规时失败，恢复完全相同的 pre-control fixture 后通过。
只有正常路径常绿，不能证明 guard 有感知能力。Semantic authority 判断无法可靠自动化时，使用明确
review event、保留 evidence 和 escalation owner，不伪装成关键词扫描。

## Recovery Closure

| Failure | Detection | Decision / recovery owner | Action | Terminal invariant |
| --- | --- | --- | --- | --- |
| Kernel extraction 改变 current proposal结果 | compatibility fixtures | S1 owner / Program decision owner | 恢复 wrapper旧 composition，保留 failing fixture，重新划 seam | Current grammar恢复，finding 未被吞掉 |
| Profile split 产生双写或 missing owner | link/owner ledger | S2 owner / Program decision owner | 前向收敛到一个 owner；无法收敛则 rollback workstream | 每条 rule 一个 editable owner |
| Product cutover 漏 consumer | link/member checks或review | S3 owner / Program decision owner | 同 Change forward-fix；consumer不可枚举则恢复旧 path | 只有一个 current product entry |
| Target 必须修改 portable file | digest mismatch | Target adoption owner + Source Program owner | Adoption 标记 needs-source-fix；同一 active Source Change 修正并发布新 candidate | Target 无静默 fork，Change budget 不增长 |
| Architecture guard 因通用化被弱化 | current negative fixture | project architecture owner | 回滚抽象；checker继续本地 | Deep Research invariants原样或增强 |
| Guard scope 可被搬文件绕过 | planted escape fixture | guard owner | 扩大 exact scope或拒绝移动；记录 scope decision | 已知违规无法逃逸 |
| Sibling adoption 无法完成 | adoption evidence | target decision authority | reject snapshot或等待 source fix，不宣称 release | Release状态诚实为 candidate/rejected |
| Consumer 或 owner 冲突无法决定 | review finding | Program decision authority | 保持 workstream active并升级决策，不迁移 | Current authority继续唯一有效 |

这些 workstreams 没有 runtime data migration，因此不使用双写、shadow state 或兼容数据副本。文档/path
cutover 采用一次性 current-entry 切换；source control 保存历史。

## Verification

每个 source workstream 从最窄验证开始；S4 与 archive handshake 再运行完整门禁：

```bash
python3 openspec/governance/check_change_guidance.py
python3 openspec/governance/check_project_reqs.py
python3 openspec/governance/check_project_specs.py
python3 openspec/governance/check_project_architecture.py
python3 openspec/governance/check_project_req_coverage.py
openspec validate make-openspec-practice-portable --strict
cd deep_research_harness && UV_OFFLINE=1 make verify
git diff --check
```

Closeout 还记录：

```bash
git status --porcelain=v1 --untracked-files=all
git ls-files --stage deerflow
git submodule status -- deerflow
git -C deerflow status --porcelain=v1 --untracked-files=all
git diff --submodule=short
```

Target adoption 运行自己的 equivalent verification，并在 evidence 中给出 exact commands/results；
不能用 source `make verify` 代替 target proof。

## Deletion Closure

每个 owner/path cutover workstream 必须同时：

1. 枚举 current inbound links、checker constants、spec/registry entries 和 fixtures；
2. 更新所有 current consumers；
3. 删除旧可编辑正文或旧 current entry；
4. 证明 archive 是历史、不是 active consumer；
5. 运行 planted stale-link/duplicate-owner negative；
6. 记录旧入口已退休，不留下无限期 TODO 或兼容 copy。

## 最终关闭门槛

本 plan 只有在以下全部有证据时完成：

- Source S0–S4 tasks 全部完成，Program Change strict-valid、完整验证通过；
- target topology 与 `02` 一致，没有重复 owner；
- export 与 target adoption 完全符合 `03`；
- 每个 guard 有 planted negative 与恢复后 positive；
- current Deep Research proposal grammar、spec IDs、architecture invariants 和 runtime verification 保持；
- `product/README.md` 已切换且 glossary owner 未改变；
- 一个真实 sibling target 在一个共享 adoption evidence boundary 中完成 T0–T4，portable files digest 未变；
- source candidate 被 target 证明并明确 ratify 为 portable release；
- old current paths/duplicate prose 已删除；
- `deerflow` pointer 与 nested worktree 未变；
- Source 只使用一个 Program Change；target 使用获批的最小 change set，且修复轮次没有新增 Change。
