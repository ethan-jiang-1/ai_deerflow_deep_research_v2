# Progressive Plan: Cognitive-Node-First Agent Loop Governance

> 状态: Complete — Changes 0–11 closed, verified, synchronized, and archived | 更新: 2026-07-30
>
> 本计划取代已归档的 `node-agent-control-flow-readability-progressive-plan.md`
> 的核心取舍：后者只交付了 reader projection，且允许每个 node 使用不同 Markdown
> 形状；本计划要求所有 logical node 使用一个诚实、固定的认知/控制 interface，并把
> capability Markdown、prompt 和受限 agent loop 视为一等程序。
>
> [`wave2-synthesis-compact_v1`](node-agent-control-flow-readability/wave2-synthesis-compact_v1/)
> 是这个 interface 的共同**结构范例**：先辨认智力程序，再从症状进入，随后区分模型可见
> 程序、feedback/candidate、deterministic authority 与 route。它不是要求其他 node 复制
> Wave2 的 prompt、repair 情形或业务事实；各 node 必须用自己的真实 seam 填写同一结构。

## 进度面板 / Roadmap Dashboard

| 总数 | 已关闭 | 当前 | 当前之后 | 下一道门 |
| --- | --- | --- | --- | --- |
| 12 changes（0–11） | 12（0–11） | 计划完成 | 0 | 无；任何后续行为均需新的 Scope Card 与独立授权 |

**计划已到终点**：Changes 0–11 均已完成 implementation、verification、spec sync 和 archive。
HITL2 仍诚实保留为 `conditional/unresolved`；若未来出现已批准的真实产品触发条件，须另起 change。

## 目标

Deep Research 不是一组传统函数之间偶然夹着模型调用的程序。对真正承担判断、规划、检索、
综合或语义解释的节点，主要可调程序是：

```text
trusted assignment
  + model-visible Markdown capability
  + prompt builder / rendered request
  + bounded tools and untrusted observations
  + feedback delivered to the next model turn
        -> Node Agent candidate
        -> deterministic parse / admission / lifecycle control
```

后半段仍然必须由确定性代码拥有 authority：模型不能写 checkpoint、ledger、artifact promotion
或 executable route。但前半段不再是“文档附属物”或最后才看的外部调用；它是认知程序，应该是
质量问题的第一修改 seam。

本计划的成功条件不是增加测试数、也不是把所有控制逻辑交给模型，而是让人和 Coding Agent 在
任意 node package 首屏就能回答：

1. 这个 node 的**产品职责**是什么：它为研究产品解决的具体用户/研究问题是什么？例如 profile
   intake、plan decomposition、evidence sufficiency judgment 或 report composition；不能只写
   “active agent”。
2. 它的**参与模式**是什么：bounded cognitive program、human-decision/authorization，还是
   deterministic controller？这解释应从哪一种程序入手，但不是当前实现的别名。
3. 这个参与模式的**承诺状态**是什么：current accepted、accepted-but-deferred、conditional/
   unresolved，还是 intentional controller exclusion？这防止把 HITL2 的条件性机会伪装成已批准
   体验，也防止把 readiness/final delivery 的已接受 deferred work 忘掉。
4. 它的**当前运行机制**是什么：active model loop、autonomous deterministic continuation、
   deterministic fallback，还是 controller-only？这是可变的、必须由 source audit 证明的事实。
5. 当前 direct `run_agent` discovery 和 Charter 的二元标记证明什么**当前 model-branch evidence**？
   它们只能回答第 4 题，不能替第 1–3 题命名，也不能把 future cognitive/human-decision role
   宣判为永久 `no-agent`。
6. 若模型或人参与，正在解决什么有界认知/决策问题，实际看见哪些 Markdown/prompt/input，能使用
   什么工具，收到什么 feedback？
7. 模型或人只产生什么 candidate/choice，哪个 deterministic owner 决定接纳、恢复、状态 mutation
   和 route？
8. 这个症状首先应调整 capability Markdown、prompt、上下文、工具、feedback、candidate admission、
   human-decision UX，还是 controller/graph？哪个测试或 eval 真正证明该判断？

## Canonical Terms / 规范术语

本计划只使用以下互不替代的术语。`product cognitive role` 是已废弃的简写：它曾把“具体产品
职责”和“参与模式”混为一谈，后续 Scope Card、reader card、proposal、design、spec、task 不得再把
它当字段名。

| Term | Meaning | Fact owner / allowed evidence | Not interchangeable with |
| --- | --- | --- | --- |
| **Product responsibility / 产品职责** | 一个 node 为用户和研究流程承担的具体语义结果；每个 logical node 必须是独立、可读的一句话 | User-approved Scope Card and accepted product/spec history | `run_agent`、agent/controller 标签、prompt 文件名 |
| **Participation mode / 参与模式** | 该职责应由 bounded cognitive program、human decision/authorization 或 deterministic control 哪一种参与方式完成 | Approved product decision; conditional mode must say so | Current mechanism |
| **Commitment state / 承诺状态** | `current accepted`、`accepted-but-deferred`、`conditional/unresolved` 或 `intentional controller exclusion` | Scope Card plus accepted spec/history; `conditional` needs a later user decision | Current source behavior |
| **Current operating mechanism / 当前运行机制** | Source-audited behavior running today | Owning source, typed contract, and lowest responsible deterministic test | Product responsibility, participation mode, commitment |
| **Deterministic authority boundary / 确定性 authority 边界** | Owner that admits candidate/choice and mutates state, artifact, checkpoint, or route | Typed contract/controller/gate/publisher and focused test | Model or UX adapter |
| **Current model-branch evidence / 当前模型分支证据** | Present/absent direct reachable branch and its source; Charter binary, if required, is only this evidence | Discovery plus branch-cohort proof | Product identity, commitment, or authority |

Every canonical table is invalid if it groups multiple logical nodes into one role row, uses a generic
category as a product responsibility, or lets model-branch evidence fill any of the first three
fields.

## 已知缺口

刚完成的 reader-interface rollout 已给六个直接 `run_agent` owner 添加 `workflow.md`，并且
正确保留 deterministic authority。它仍不足以改变日常工程重心：

| 已交付 | 仍缺失 | 后果 |
| --- | --- | --- |
| 每个认知 node 有一份症状导航 | 主规范允许各 node 使用不同文档 shape | Coding Agent 无法从固定界面先识别“这是认知程序” |
| capability 与 prompt 的路径被链接 | Markdown body、prompt builder、feedback、candidate/admission 没有固定成一个 agent-loop interface | 调试会退回 parser/state/gate/route 优先 |
| 每个 `run_agent` owner 有 deterministic workflow coverage | 这些证据主要证明运行时、边界和 failure conformance，不等于认知质量或 prompt/feedback 是否正确 | 大量绿色测试容易掩盖调优方向错误 |
| deterministic admission 不被模型夺权 | 所有 11 个 logical node 没有统一的诚实身份声明 | controller 与 agent 的维护路径混淆 |
| 六个 current `run_agent` owner 被列为 agent | “当前直接模型调用”被误当作“该 node 的产品职责或参与模式” | HITL2、readiness、final delivery 的交互/认知缺口会被错误地永久标记为 `no-agent` |

现有确定性测试不是应被轻率删除的“无用传统程序”：它们守住安全、tool posture、候选接纳、
恢复和 route。问题是测试数量不能作为认知程序正确性的 proxy。今后每个测试必须能说明它证明的是
**认知程序、deterministic guardrail、还是 wiring**；只有前两者共同覆盖一个风险时，才足以关闭
该风险。

2026-07-29 的 source/spec/history investigation 修正了这一计划的初始二分法：

- HITL2 在较早的 change 中曾是真实的 human-decision interrupt；随后因把 `proceed`、`repair`、
  `rerun` 等内部 graph route 暴露给用户造成 P0 UX 问题，当前实现改为 validated autonomous
  `proceed`。这不是“没有交互价值”的结论，而是拒绝把内部 route 菜单当用户体验。当前
  `run_experience` 仍保留 HITL2 choice projection，而 production node 不会发出它；未来只有
  non-inferable preference 或 irreversible authorization 才可用新的 typed contract 恢复人机决策。
- readiness 的当前 critic 明确是 deterministic fallback；主 spec 明确要求未来的 bounded read-only
  agent critic。final delivery 的当前 formatter 也明确是 LLM writer 的 deferred follow-up。
- bootstrap 的 bundle binding 和 rerun 的 scoped invalidation/generation mutation 则是确定性 safety
  seams。把模型塞进它们不会给用户带来认知质量，只会模糊 authority。

因此，本计划以**产品职责**为每个 node 的主身份，再分开记录**参与模式**、**承诺状态**、
**当前运行机制**、**deterministic authority boundary** 与 **current model-branch evidence**。
direct `run_agent` discovery 只能说明当前 loop 是否存在；它不是产品 taxonomy。HITL2 的具体
model-supported UX 仍是需要用户批准的产品决定，不是本次调查替用户作出的实现授权。

## Plan Evolution Checkpoint

- [x] 2026-07-29 -- Reconciled current source, main specs, and HITL2 history: six active direct
  model owners; bootstrap/rerun controller-only; HITL2 autonomous today with a future
  human-decision seam; readiness/final delivery explicitly deferred cognitive roles.
- [x] 2026-07-29 -- Replaced the plan's binary `node-agent`/`no-agent` inventory with an initial
  role-first model. The subsequent adversarial review found that its shorthand still conflated
  product responsibility with participation mode; that distinction is corrected below.
- [x] 2026-07-29 -- Phase 0 source audit confirmed the ordered 11 logical nodes, six current active
  owners, and 16 direct branches: the 18-case topology selection, 19-case owner/local-capability
  selection, separate 44-case capability-cohort selection, and 27-case controller bundle all
  passed. Submitted the Phase 0 Scope Card before proposal creation.
- [x] 2026-07-29 -- User approved `define-cognitive-node-operating-model`; created and polished its
  OpenSpec artifacts. Polish separated the 6-owner and 16-branch proof seams, preserved the
  HITL2/readiness/final-delivery source-vs-spec observations (including final delivery's absent
  current integrity-gate/self-repair path), and passed strict validation. **STOP before apply.**
- [x] 2026-07-29 -- Completed an initial role-first alignment after finding that the active proposal
  foregrounded the Charter binary. This was not an end-to-end readiness certification.
- [x] 2026-07-29 -- Made an initial node-coverage ledger: all 11 nodes require the fixed reader
  interface; nine cognitive/human responsibilities require targeted behavior/experience paths;
  bootstrap and rerun have narrowly justified deterministic-controller exemptions.
- [x] 2026-07-29 -- Hardened the plan after adversarial review: replaced generic role rows with 11
  product responsibilities, added a 16-branch closure ledger, separated conditional commitments,
  split active-branch evaluation from deferred-role dossiers, and added propagation-review gates.
- [x] 2026-07-29 -- User authorized the role-model re-alignment. Rebuilt and independently reviewed
  the active proposal, design, both delta specs, and apply ledger around the product-responsibility-
  first hierarchy; the 18/19/44/27 source evidence bundles and strict OpenSpec validation passed.
  **STOP: fresh authority is still required before apply.**
- [x] 2026-07-29 -- Applied and closed `make-active-cognitive-programs-evaluable`: the 16 active
  direct branches now have exact cognitive-program ledger rows with distinct composition, feedback,
  guardrail/admission, and evaluation-disposition evidence. The completed change introduced
  `cognitive-program-evidence`, synchronized CPE/NAC/NOA/NPC/EVH main specs, passed offline
  verification and strict main-spec validation, and was archived in commit `846c107`. This closes
  evidence reviewability only; it does not claim Wave1 baseline/gate conformance or cognitive
  calibration.
- [x] 2026-07-29 -- User authorized and proposed `repair-wave1-baseline-and-gate-conformance`.
  Its Scope Card keeps Wave1's product responsibility first, identifies the empty top-level Wave0
  baseline and completion-only real gate as source-audited conformance defects, and prohibits a
  new model branch or authority transfer. Proposal, `wave1-node` delta, design, and tasks passed
  strict OpenSpec validation and requirement-ID governance. **STOP before polish/apply.**
- [x] 2026-07-30 -- Applied and closed `repair-wave1-baseline-and-gate-conformance`: Wave1 now
  reconstructs a same-generation Wave0 URL baseline from accepted submissions, rejects invalid
  drafts before persistence, materializes bound SourceDiagnostic and ClaimVerifier review artifacts,
  and evaluates their bounded projection before the deterministic gate routes. The two critic
  branches expand the current direct-branch ledger from 16 to 18 without granting model authority.
  Main specs were synchronized, the change was archived, and offline verification plus strict
  main-spec validation passed in commit `6bb4af4`.
- [x] 2026-07-30 -- Audited and proposed `calibrate-intake-and-planning-cognitive-loops`.
  Its Scope Card keeps HITL1 as the primary causal owner, admits topic planning only through the
  confirmed-profile contract, and scopes quality work to six existing zero-tool branches. The
  proposal, HITL1/topic-planning/evaluation-hardening deltas, design, and tasks separate
  deterministic composition/non-admission proof from optional labeled live judgment evidence.
  Strict OpenSpec validation passed. **STOP before polish/apply.**
- [x] 2026-07-30 -- Applied and closed `calibrate-intake-and-planning-cognitive-loops`: the six
  existing zero-tool HITL1/topic-planning branches now expose calibrated conservative candidate
  policies, retain deterministic admission boundaries, and have a separate twelve-case optional
  live judgment-evaluation corpus. Main specs were synchronized; the change was archived after
  offline verification and strict validation in commit `6a45316`. No credentialed live calibration
  was claimed as required evidence.
- [x] 2026-07-30 -- Audited and proposed `calibrate-evidence-intake-cognitive-loops`: its Scope
  Card keeps Wave0 source intake as the primary causal owner and admits Wave1 only through the
  accepted-baseline/evidence-review contracts. The proposal, Wave0/Wave1/evaluation-hardening
  deltas, design, and tasks separate deterministic composition/non-admission proof from an
  optional twelve-case selected live judgment corpus with strict model/web preflight. Strict
  OpenSpec validation passed. **STOP before polish/apply.**
- [x] 2026-07-30 -- Applied and closed `calibrate-evidence-intake-cognitive-loops`: Wave0 and
  Wave1 now expose calibrated conservative source/evidence candidate policies, bounded repair
  feedback, and a separate twelve-case selected live judgment corpus while deterministic evidence,
  review, gate, and route owners remain unchanged. Main specs were synchronized before archiving;
  offline verification and strict validation passed in commit `e64b83d`. Credentialed live
  evaluation remains explicitly supplemental and was not claimed as completed evidence.
- [x] 2026-07-30 -- Audited and proposed `calibrate-evidence-judgment-cognitive-loops`: its Scope
  Card keeps Wave2 accepted-evidence synthesis as the primary causal owner and admits targeted
  work only through the existing gate-projected gap and assigned-reference contracts. The proposal,
  Wave2/targeted/evaluation-hardening deltas, design, and tasks create a separate twelve-case
  selected live judgment corpus with strict branch-specific model/web preflight, while preserving
  deterministic materialization, ledger, convergence-gate, and route authority. Strict OpenSpec,
  requirement-ID, and main-spec validation passed. **STOP before apply.**
- [x] 2026-07-30 -- Applied and closed `calibrate-evidence-judgment-cognitive-loops`: Wave2 and
  targeted-evidence branches now expose calibrated evidence-judgment policies, a separate
  twelve-case selected live corpus, strict branch-specific preflight, and a closed three-corpus
  report resolver while deterministic materialization, ledger, gate, convergence, and route owners
  remain unchanged. Main specs were synchronized and the change archived in commit `078dde7`.
  Credentialed live calibration was not run because no model or web credential was configured; it
  remains supplemental rather than claimed deterministic evidence.
- [x] 2026-07-30 -- Applied and closed `activate-final-report-composition-loop`: real final
  delivery now invokes one bounded zero-tool layout composer over the immutable readiness plan and
  accepted evidence projection; deterministic admission/rendering preserves exact conclusion,
  uncertainty, and citation bindings while the final gate and publisher retain lifecycle and
  artifact authority. The direct-branch denominator is now twenty. Main specs were synchronized,
  the change was archived, and offline verification plus strict validation passed in commit
  `580efc9`. **STOP before change 11**.
- [x] 2026-07-30 -- Audited and proposed `govern-cognitive-program-evidence`: the proposal,
  design, tasks, and three deltas define an exact 11-node/20-branch evidence board, reconcile
  fulfilled readiness/final-delivery activation projections, and introduce risk-preserving
  consolidation governance with an explicitly empty retirement set. Strict OpenSpec validation
  and `git diff --check` passed. **STOP: polish/apply require separate authorization**.
- [x] 2026-07-30 -- Applied and closed `govern-cognitive-program-evidence`: one test-owned board
  now closes the exact 11-node, 20-branch, and 41-calibration-case denominators; readiness and final
  delivery project their current accepted cognitive programs while HITL2 remains the sole unresolved
  activation dossier. Typed risk-preserving consolidation governance shipped with an empty retirement
  set, and every pre-change selector remains collected. Offline `make verify`, the reader checker,
  selector-superset comparison, strict OpenSpec validation, and `git diff --check` passed; no
  credentialed live/release lane was executed or claimed. The three main specs were synchronized and
  the change was archived at
  `openspec/changes/archive/2026-07-30-govern-cognitive-program-evidence/`.

## Plan Ready-for-Purpose Review

- [x] **Canonical vocabulary:** product responsibility, participation mode, commitment state,
  current operating mechanism, deterministic authority, and model-branch evidence are defined as
  separate facts; retired field names occur only in the deprecation note.
- [x] **11-node closure:** the scope inventory and node completion ledger each have exactly one row
  for every current `LOGICAL_NODES` member, verified by set equality against
  `graph/topology.py`.
- [x] **20-branch closure:** the branch ledger has exactly the source-audited 20 direct branch IDs,
  verified by set equality against `tests/assets/node_agent_capabilities.py`; every row includes
  change 11 final-evidence closure.
- [x] **No false product commitment:** HITL2 is `conditional/unresolved`; readiness and final
  delivery now have current accepted bounded cognitive programs; bootstrap/rerun are intentional
  controller exclusions.
- [x] **No coverage leak:** every named future change has exact node/branch coverage, every ledger
  row names its required changes, and the phase sequence is closed from 0 through 11.
- [x] **Propagation guard:** the mandatory post-polish review checks every artifact, field order,
  authority, audit-only Charter flag, and ledger row before an apply request.
- [x] **Mechanical hygiene:** the evidence/governance implementation, focused reader projections,
  tests, main specs, archive, and this plan are aligned; `backend/` and `frontend/` remain clean,
  strict validation and `git diff --check` pass, and no existing selector was removed or relabeled.
- [x] **OpenSpec alignment:** proposal, design, all three delta specifications, tasks, implementation,
  test evidence, and synchronized main specs use the same closed 11-node/20-branch/41-case model.

## 非谈判原则

- **Markdown capability body 是程序。** 它进入模型可见 policy；修改它与修改 prompt builder
  一样需要明确 cognitive hypothesis、可观察结果和适当 eval。metadata、catalog projection
  和此计划本身不是模型政策。
- **一个 Node Agent 是深模块。** 它以一个小 interface 隐藏模型推理、prompt composition、tool
  interaction 和 structured candidate generation；调用者只依赖 candidate/admission seam，不应
  了解或接管内部推理。
- **候选与 authority 分离。** Node Agent 不能拥有 evidence admission、profile publication、
  checkpoint mutation、retry budget、gate verdict 或 executable route。确定性控制不是次要代码，
  而是认知程序的合法外壳。
- **产品职责先于参与模式，参与模式先于运行机制。** 每个 node 首先以其具体产品职责命名；再说明
  它应由何种参与模式完成、该模式的承诺状态和当前实现。当前运行机制是可替换的 source fact，
  不能反向定义产品身份。
- **条件性不是已批准体验。** HITL2 在出现真实 non-inferable preference 或 irreversible
  authorization 前是 `conditional/unresolved`；它既不能被永久标作 `no-agent`，也不能被写成已有
  human-decision UX。readiness/final delivery 的当前已接纳 cognitive programs 必须继续与它分开标注。
- **`run_agent` 只是当前 model-branch probe。** direct discovery 只证明当前有或没有 active model
  loop；它不能把 specification-deferred cognitive responsibility 或 future human-decision
  responsibility 宣判为永久 `no-agent`。
- **Charter 二元标记只能当审计证据。** 若 Charter review 需要记录 `node-agent`/`no-agent`，它只能
  出现在单独的 current-model-branch evidence appendix，绝不能成为 node title、产品职责、inventory
  的主列、Scope Card 的主张或 reader card 的身份。
- **不伪造 agent，也不掩盖责任状态。** bootstrap 和 rerun 必须清楚标为 intentional controller
  exclusion；readiness 与 final delivery 必须如实标为 current accepted active cognitive programs；
  HITL2 必须如实标为当前 autonomous、条件性 human-decision seam。没有已批准的 model loop 时，
  card 不得虚构 model-visible prompt、tools 或 feedback。
- **11-node 与 20-branch 都是闭合集合。** node ledger 必须恰有 `LOGICAL_NODES` 的 11 个单独行；
  active cognitive program 的 branch ledger 必须恰有当前 source-audited 的 20 个单独行。任何 group
  row、aggregate test 或总数不能替代一个缺失行。
- **固定 shape，内容不固定。** 所有 node 都有同一组 section；每个 section 的事实、症状、
  branch 和验证完全由该 node 的真实 seam 决定。不得复制 Wave2 的具体 repair 语义。
- **测试以主张为单位。** 不以 pytest 总数、行覆盖率或一个 aggregate suite 的绿色状态证明
  cognitive quality。每个认知 branch 应分别有 composition、agent-loop 和必要时 live-eval 证据。
- **先调查再重写行为。** Wave1 的 top-level baseline loading 与 gate conformance 等已知实现/规范
  差异必须进入 owning behavior change，不能借 interface normalisation 隐藏或“顺手修复”。

## Canonical Node Interface

所有 11 个 `graph/topology.py::LOGICAL_NODES` 都 SHALL colocate `workflow.md`。其 authored
Markdown 采用 Wave2 v1 范例的固定**结构语法**，而非复制该范例的内容；标题可翻译，但
section 次序和含义不可省略。每张 card 先声明产品职责，再声明参与模式、承诺状态和当前运行机制，
防止把暂时的 implementation fallback 误读为永久架构：

```markdown
# <Node> — <Product Responsibility>

> Product responsibility: <specific user/research outcome, never a generic category>
> Participation mode: <bounded cognitive program | human decision / authorization | deterministic control>
> Commitment state: <current accepted | accepted-but-deferred | conditional / unresolved | intentional controller exclusion>
> Current operating mechanism (source-audited): <active model loop | autonomous deterministic continuation | deterministic fallback | controller-only>
> Primary cognitive/control program surface: <capability Markdown + prompt builders | human-decision contract | deterministic controller>
> Deterministic authority boundary: <candidate/choice admission and route summary>
> Current model-branch evidence (audit only): <exact reachable direct `run_agent` branch ids | no direct branch observed, with source>

## Node Identity / 节点性质
## From Symptoms / 从症状进入
## Three Cross-Module Facts / 三个跨模块事实
## Route Facts / Route 事实
## Evaluation and Verification Order / 修改后的验证顺序
```

Every card SHALL contain exactly three bounded `Three Cross-Module Facts`; their content is selected
first by product responsibility, then participation mode/commitment state, and then the current
operating mechanism below. A card never manufactures an active model loop just because its product
responsibility is cognitive. Conversely, a missing direct branch never erases a deferred or
conditional responsibility. The canonical card does not display `node-agent`/`no-agent`; a required
Charter binary review is a separate audit appendix.

### Active cognitive participation with an active model loop

`Three Cross-Module Facts` MUST be exactly three bounded facts, in this order:

1. **Cognitive program and model visibility** — bounded question, capability Markdown body,
   prompt builder, trusted assignment, untrusted inputs, requested and runtime-enforced tools.
2. **Bounded agent loop and feedback** — initial call, parser/validator feedback that actually
   reaches a repair/retry turn, delivery gaps, bounds, and the owning recovery layer.
3. **Candidate to deterministic authority** — typed candidate, parser/materializer/controller/
   ledger admission owner, and what the model cannot decide.

`Route Facts` MUST name the semantic edge, route writer, executable edge kind, route consumer,
and target. A node with an unconditional edge says so explicitly; a model result or a handler's
incidental `route` field cannot be represented as route authority.

`From Symptoms` MUST start with cognitive-program symptoms before parser/graph symptoms. At
minimum it covers: wrong role or model-visible policy; wrong context/tool posture; malformed or
misaligned candidate/feedback; unexpected admission; wrong route/terminal result. Every row names
the first `file::symbol` and the narrowest proof or eval seam.

### Accepted cognitive responsibility with deferred model activation

The same headings remain mandatory. `Node Identity` names the existing fallback and the source/spec
that declares the accepted product responsibility. Its three facts cover: (1) the bounded future cognitive
question and current non-model fallback, (2) the required activation interface -- trusted
context, model-visible policy, tool posture, candidate schema, feedback and evaluation -- and
(3) the deterministic materializer/gate/publisher that remains authority. `From Symptoms` starts
with the missing cognitive outcome, then identifies the fallback and the first safe activation
seam. It MUST say that no active prompt/catalog/eval exists yet when none exists.

### Human-decision / authorization participation

The same headings remain mandatory. `Node Identity` says whether the current path is autonomous,
interactive, or dormant, and whether the responsibility is accepted or conditional/unresolved. Its
three facts cover: (1) the trusted research state and the genuine
non-inferable preference or irreversible authorization at issue, (2) the bounded human-facing
brief, recommendation/default, response binding, and optional model-assisted explanation or
free-text interpretation, and (3) the deterministic validation that maps an accepted human choice
to a legal typed candidate/route. The card MUST explicitly reject raw internal route names as UX
and must not give either model or presentation adapter route authority.

### Intentional deterministic-controller participation

The same headings remain mandatory, but `Node Identity` states why a model invocation would be the
wrong seam. Its three facts cover trusted controller inputs, deterministic decision/recovery, and
lifecycle/route authority. The symptom table directs readers to controller seams and explicitly
rejects capability/prompt edits as first changes. A controller-only node can receive an already
validated candidate from an upstream agent or user-decision seam; it does not need to become an
agent to execute it safely.

This gives every graph node a predictable shape while preserving the distinction that prevents
authority leakage.

## Scope Inventory

This inventory is a closed, one-row-per-node product model. `Product responsibility` is the primary
product claim; `participation mode` and `commitment state` explain intended participation; `current
operating mechanism` is a source fact that may change without changing the first three fields.

| Logical node | Product responsibility (primary identity) | Participation mode / commitment state | Current operating mechanism (source-audited) | Deterministic authority and planning consequence |
| --- | --- | --- | --- | --- |
| `bootstrap` | Atomically bind and validate the trusted bootstrap bundle | Deterministic control / intentional controller exclusion | Controller-only | Bundle store/domain contract and node handler own binding, terminal disposition, and state update. |
| `hitl1` | Turn bounded human request/profile material into advisory-brief or semantic-intake candidates | Bounded cognitive program / current accepted | Active model loop; four current branches | HITL1 parser/domain and graph owners admit candidates and publish the profile/route. |
| `topic_planning` | Decompose a confirmed profile into a bounded research-plan candidate | Bounded cognitive program / current accepted | Active model loop; two current branches | Deterministic materializer/controller admits the plan, materializes topics, and writes route. |
| `wave0` | Acquire and evaluate authoritative-source evidence for an assigned work unit | Bounded cognitive program / current accepted | Active model loop; worker and repair branches | Validator/controller and submission ledger admit work-unit candidates and evidence. |
| `wave1` | Extract source-grounded evidence for assigned work and surface bounded repair candidates | Bounded cognitive program / current accepted | Active model loop; worker, repair, SourceDiagnostic, and ClaimVerifier branches | Validator/controller, ledger, critic, and gate retain evidence, admission, and route authority. |
| `wave2_synthesis` | Synthesize accepted evidence into findings, relations, and research gaps | Bounded cognitive program / current accepted | Active model loop; synthesis and repair branches | Node admission writes preview; deterministic gate owns executable route. |
| `targeted_evidence` | Resolve a gate-projected evidence gap through targeted retrieval, diagnosis, or claim verification | Bounded cognitive program / current accepted | Active model loop; four current branches | Worker/repair admission and graph builder retain evidence and executable-edge authority. |
| `hitl2` | Offer a user decision only when a genuine non-inferable preference or irreversible authorization is identified | Human decision / authorization / conditional-unresolved | Autonomous deterministic continuation; validates Wave2 pass and applies `proceed` | Boundary validator/node maps only a valid typed choice to a legal route; no generic internal-route menu. |
| `rerun` | Execute an already validated rerun scope, invalidating projections and advancing generation safely | Deterministic control / intentional controller exclusion | Controller-only | Rerun contract/planner/node own scope validation, invalidation, generation mutation, and route. |
| `readiness` | Judge per-question evidence sufficiency and answerability | Bounded cognitive program / current accepted | Active zero-tool evidence-critic loop | Hard rules and report-plan materializer own verdict admission and route; the critic remains read-only. |
| `final_delivery` | Compose and communicate a report plus citation map from the readiness-bounded plan and accepted evidence | Bounded cognitive program / current accepted | Active zero-tool layout-composition loop | Deterministic layout admission/rendering, integrity gate, and publisher retain validation, exact plan-text/citation binding, publication, terminal status, and route authority. |

The first OpenSpec change must re-run active-branch discovery and separately validate the product
responsibility, participation mode, and commitment evidence above. A direct reachable `run_agent`
branch establishes only the current mechanism. If a Charter review records `node-agent`/`no-agent`, it
is an audit-only present/absent branch flag, never an identity or an admission shortcut. Any difference
is an admission question, not a silent document update or a nonexistent branch added to the prompt
catalog. The row names and order must equal `graph/topology.py::LOGICAL_NODES`; no grouped row is
allowed in this inventory or the node completion ledger.

## Node Change Commitment Ledger

This is the plan's non-optional coverage contract, not a loose list of nodes that happen to be
mentioned elsewhere:

- **11 / 11 logical nodes** must receive the fixed Wave2-shaped `workflow.md` reader interface in
  change 1. The ledger set must equal `LOGICAL_NODES` exactly, with one row per node.
- **9 / 11 nodes** have bounded-cognitive or human-decision participation. Each must receive a
  named intervention **decision** after the required gates: an approved behavior/experience change,
  or a documented, user-accepted no-change decision with causal evidence and retained risk. A
  missing `run_agent` call is never such a decision.
- **2 / 11 nodes** — `bootstrap` and `rerun` — are intentionally excluded only from adding a model
  or human-decision loop. They still receive the reader card, controller evidence, and final
  governance board. Their exemption is a positive safety decision, not an absence of work.
- **20 / 20 current direct model branches** must close their separate branch ledger below. A
  node-level checkbox cannot hide an uncovered repair, diagnostic, or verifier branch.

The checkbox below turns `[x]` only after **all** listed interventions, every owned branch row (when
applicable), and change 11's final evidence-governance board have been applied, verified, and
archived. Completing a reader card, an aggregate test, or one local behavior change alone does not
close a node.

| Node | Product responsibility / participation / commitment | Minimum committed intervention path | Only permitted no-behavior-change disposition | Final status |
| --- | --- | --- | --- | --- |
| `bootstrap` | Bind/validate trusted bootstrap bundle / deterministic control / intentional controller exclusion | Changes 1 and 11 | Its atomic binding has no bounded cognitive question or non-inferable user choice; model participation would blur store/binding/terminal authority | [x] |
| `hitl1` | Produce profile-intake candidates / bounded cognitive program / current accepted | Changes 1, 2, 4, and 11 | Scoped hypothesis/eval proves its capability, prompt, feedback, and admission seams already meet the approved outcome | [x] |
| `topic_planning` | Produce research-plan candidates / bounded cognitive program / current accepted | Changes 1, 2, 4, and 11 | Scoped hypothesis/eval proves its decomposition/repair program already meets the approved outcome | [x] |
| `wave0` | Acquire/evaluate authoritative-source work-unit evidence / bounded cognitive program / current accepted | Changes 1, 2, 5, and 11 | Scoped hypothesis/eval proves its source-selection/feedback program already meets the approved outcome | [x] |
| `wave1` | Extract evidence and surface repair candidates / bounded cognitive program / current accepted | Changes 1, 2, 3, 5, and 11 | Mandatory conformance repair is complete and scoped evaluation proves no further cognitive-program edit is justified | [x] |
| `wave2_synthesis` | Synthesize evidence into findings, relations, and gaps / bounded cognitive program / current accepted | Changes 1, 2, 6, and 11 | Scoped hypothesis/eval proves its synthesis/feedback program already meets the approved outcome | [x] |
| `targeted_evidence` | Resolve a gate-projected evidence gap / bounded cognitive program / current accepted | Changes 1, 2, 6, and 11 | Scoped hypothesis/eval proves its retrieval/critique program already meets the approved outcome | [x] |
| `hitl2` | Conditional user decision for non-inferable preference/authorization / human decision / conditional-unresolved | Changes 1, 3, 8, and 11 | User explicitly decides that no genuine decision trigger exists; autonomous continuation remains the accepted product behavior | [x] |
| `rerun` | Execute validated rerun scope safely / deterministic control / intentional controller exclusion | Changes 1 and 11 | It validates typed scope and performs invalidation/generation mutation; cognition or user choice belongs upstream and would blur lifecycle authority here | [x] |
| `readiness` | Judge answerability/evidence sufficiency / bounded cognitive program / current accepted | Changes 1, 3, 9, and 11 | Change 9's bounded zero-tool critic, deterministic admission, and separately classified answerability evaluation are verified, synced to main specs, and archived; a later product decision is required to supersede this responsibility | [x] |
| `final_delivery` | Compose/communicate report and citation map / bounded cognitive program / current accepted | Changes 1, 3, 10, and 11 | A new user-approved product decision supersedes the active bounded composition responsibility; the deterministic admission/gate/publisher boundary is not an exemption | [x] |

Before any later Scope Card is approved, the ledger must name the node row it closes, its product
responsibility, and whether it is reader-only, active-cognitive, deferred-cognitive,
human-decision, or deterministic-controller work. Before any row becomes `[x]`, a reviewer must
confirm that its product responsibility remained primary and that no current model-branch or Charter
binary flag was used as a substitute for the required proof.

## 20-Branch Evidence Closure Ledger

This is the closed current inventory from `tests/assets/node_agent_capabilities.py`, not a statement
that every later product responsibility already has a model loop. Each row must acquire: model-visible
composition proof; a bounded real-loop/feedback proof; candidate-to-authority proof; deterministic
guardrail proof; and an explicit judgment-eval disposition (`required` or why it is not). The `[x]`
requires changes 2, the owning calibration change where applicable, and change 11; a node aggregate
or another branch's test cannot close it.

| Current direct branch | Capability binding | Owning node responsibility | Branch closure | Status |
| --- | --- | --- | --- | --- |
| `hitl1/brief` | `hitl1-profile-brief` | Profile-intake candidates | Changes 2, 4, 11 | [x] |
| `hitl1/brief-repair` | `hitl1-profile-brief-repair` | Profile-intake candidates | Changes 2, 4, 11 | [x] |
| `hitl1/semantic-intake` | `hitl1-semantic-intake` | Profile-intake candidates | Changes 2, 4, 11 | [x] |
| `hitl1/semantic-intake-repair` | `hitl1-semantic-intake-repair` | Profile-intake candidates | Changes 2, 4, 11 | [x] |
| `topic-planning/plan` | `topic-planning-profile-decomposition` | Research-plan candidates | Changes 2, 4, 11 | [x] |
| `topic-planning/plan-repair` | `topic-planning-plan-repair` | Research-plan candidates | Changes 2, 4, 11 | [x] |
| `readiness/critic` | `readiness-evidence-critic` | Answerability/evidence-sufficiency judgment | Changes 9, 11 | [x] |
| `wave0/worker` | `wave0-authoritative-source-intake` | Authoritative-source evidence | Changes 2, 5, 11 | [x] |
| `wave0/repair` | `wave0-source-intake-repair` | Authoritative-source evidence | Changes 2, 5, 11 | [x] |
| `wave1/worker` | `wave1-evidence-extraction` | Evidence extraction | Changes 2, 3, 5, 11 | [x] |
| `wave1/repair` | `wave1-evidence-extraction-repair` | Evidence extraction | Changes 2, 3, 5, 11 | [x] |
| `wave1/source-diagnostic` | `wave1-source-diagnostic` | Source diagnosis | Changes 3, 5, 11 | [x] |
| `wave1/claim-verifier` | `wave1-claim-verifier` | Claim verification | Changes 3, 5, 11 | [x] |
| `wave2-synthesis/synthesis` | `wave2-evidence-synthesis` | Synthesis and gap formation | Changes 2, 6, 11 | [x] |
| `wave2-synthesis/repair` | `wave2-evidence-synthesis-repair` | Synthesis and gap formation | Changes 2, 6, 11 | [x] |
| `targeted-evidence/worker` | `targeted-gap-evidence-retrieval` | Gate-projected gap resolution | Changes 2, 6, 11 | [x] |
| `targeted-evidence/repair` | `targeted-gap-evidence-repair` | Gate-projected gap resolution | Changes 2, 6, 11 | [x] |
| `targeted-evidence/source-diagnostic` | `targeted-source-diagnostic` | Gate-projected gap resolution | Changes 2, 6, 11 | [x] |
| `targeted-evidence/claim-verifier` | `targeted-claim-verifier` | Gate-projected gap resolution | Changes 2, 6, 11 | [x] |
| `final-delivery/composer` | `final-delivery-composer` | Readiness-bounded report and citation-map composition | Changes 10, 11 | [x] |

If source discovery changes this set, do not edit a row by inference: stop, re-run the source audit,
open a new Scope Card, and reconcile both ledgers before a proposal or apply resumes.

## Mandatory Intervention Protocol

The names below are **proposed change names only**. They do not authorize an
`openspec/changes/<name>` directory, code edits, a spec sync, or an apply. This plan deliberately
does not treat agreement with the broad direction as approval for any individual change.

Every named change follows these non-skippable stops. A later change may never be proposed or
applied while the current one is awaiting a user decision.

1. **Scope stop -- before proposal.** Complete only the prerequisite source audit, then present a
   Scope Card containing: exact change name; **product responsibility first**; participation mode
   and commitment state; bounded cognitive/control problem; source-audited current operating
   mechanism and model-branch evidence; deterministic authority boundary; exact node-ledger row(s)
   and, when active, exact branch-ledger row(s); owned behavior; likely source, spec, test, and
   generated-projection paths; explicit non-goals; dependencies; proof/eval plan; affected Agent
   Charter policies; and unresolved decisions. Stop and wait for the user's explicit approval to
   propose that exact name. Do not create a proposal merely because the audit completed.
2. **Polish stop -- after proposal, before apply.** Once the user has approved proposal creation,
   create the OpenSpec change, run the repository's `polish-openspec-change` workflow, reconcile
   proposal/design/spec/tasks, and present the polished result with every changed scope decision.
   Stop again. "Proposal exists" or "plan looks right" is not authorization to apply.
3. **Semantic propagation review -- after polish, before apply.** Re-read the plan, proposal,
   design, every delta spec, and tasks as a single contract. Produce a small artifact-by-artifact
   matrix proving: (a) product responsibility is first and specific; (b) participation mode and
   commitment state are separate; (c) current mechanism is source-owned; (d) deterministic
   authority is named; (e) `run_agent`/Charter binary occurs only in audit evidence; (f) the
   11-node and applicable 20-branch ledgers have no missing or grouped row; and (g) every proposed
   task closes named rows. Any failed cell returns to the owning artifact; do not call the proposal
   polished or request apply authority until every cell passes.
4. **Apply stop -- explicit implementation authority.** Apply only after the user explicitly tells
   us to apply the named polished change. Keep implementation inside its accepted Scope Card; a new
   behavior, node, runtime surface, or semantic authority requires a fresh Scope Card and another
   stop.
5. **Closure stop -- before the next change.** After implementation, verification, spec sync, and
   archive (when applicable), update this plan's checkboxes with the commit/evidence reference and
   stop. Present the next Scope Card only after the user asks to move forward.

The Scope Card must state the node's product responsibility **before** participation mode, commitment
state, current operating mechanism, and deterministic authority seam. It must distinguish an
active/deferred cognitive-program seam from a human-decision seam and a deterministic-controller
seam. `run_agent` discovery and the Charter `node-agent`/`no-agent` flag may appear only in audit
evidence, never in the Scope Card title or as its role classification. It must also say why a
proposed change belongs there instead of at a parser, fixture, route, or generic runtime helper.
This is the control that keeps the work focused on the agent loop rather than using conventional tests
as a substitute for model-program evidence.

## Named OpenSpec Change Contracts

The following order is intentionally narrow. Each row is an independently reviewable change, not
a phase label that can silently absorb unrelated fixes.

| Order | Proposed OpenSpec change name | Exact coverage | Depends on | May not auto-advance to |
| --- | --- | --- | --- | --- |
| 0 | `define-cognitive-node-operating-model` | 11 node responsibilities; current 16-branch audit | None | Proposal without Scope Card approval |
| 1 | `normalize-cognitive-node-interfaces` | 11 / 11 reader cards | 0 archived | Proposal without a new Scope Card |
| 2 | `make-active-cognitive-programs-evaluable` | 6 active nodes; 16 / 16 current direct branches | 1 archived | Any behavior calibration or deferred-role dossier |
| 3 | `repair-wave1-baseline-and-gate-conformance` | `wave1` worker, repair, and critic branches | 2 archived | Claiming Wave1 loop quality |
| 4 | `calibrate-intake-and-planning-cognitive-loops` | `hitl1`, `topic_planning` | 2 archived | Evidence-intake or judgment cohorts |
| 5 | `calibrate-evidence-intake-cognitive-loops` | `wave0`, `wave1` | 2 and 3 archived | Evidence-judgment cohort |
| 6 | `calibrate-evidence-judgment-cognitive-loops` | `wave2_synthesis`, `targeted_evidence` | 5 archived | Deferred-role dossier or activation |
| 7 | `prepare-deferred-cognitive-and-human-decision-dossiers` | `hitl2`, `readiness`, `final_delivery` | 6 archived | Any HITL2/critic/composer behavior change |
| 8 | `introduce-hitl2-human-decision-experience` | `hitl2` | 6 and 7 archived | Readiness decision/critic activation |
| 9 | `activate-readiness-evidence-critic-loop` | `readiness` | 7 and 8 archived | Final report-composition activation |
| 10 | `activate-final-report-composition-loop` | `final_delivery` | 7 and 9 archived | Test-governance consolidation |
| 11 | `govern-cognitive-program-evidence` | 11 / 11 nodes and 20 / 20 current direct branches | 4, 5, 6, 7, 8, 9, and 10 archived | Any test deletion or next program of work |

### Change 0/11 ✅ 已完成 — `define-cognitive-node-operating-model`

**Owned result.** Establish one canonical vocabulary and one fixed reader interface for all 11
logical nodes. It leads with each node's specific product responsibility, then separately records
participation mode, commitment state, current operating mechanism, deterministic authority, and
current model-branch evidence. Re-run source discovery to measure the six current direct-model-loop
owners and 16 branches; this change must not turn that runtime discovery result into a permanent
product classification.

**Detailed scope.** This is a specification/governance change only. It proposes one new capability
named `cognitive-node-interface`, whose delta defines the product-responsibility-first,
participation-mode, commitment-state, current-mechanism, deterministic-authority, and audit-evidence
fields of the canonical reader interface. It may clarify the coexistence of that new
capability with `openspec/specs/node-agent-reader-interface/spec.md`; it does not revise
`node-agent-capabilities`, HITL2, readiness, final-delivery, or Charter policy behavior. Its
read-only evidence inventory is bounded to `agent/src/deerflow_deep_research/graph/topology.py`,
the 11 packages under `agent/src/deerflow_deep_research/graph/nodes/`, direct reachable
`run_agent` branches, `agent/tests/assets/workflow_nodes.py`,
`agent/tests/contract/test_workflow_node_inventory.py`,
`agent/tests/assets/node_agent_capabilities.py`,
`agent/tests/graph/test_node_agent_capability_cohort.py`,
`agent/tests/domain/test_node_agent_capability.py`,
`agent/tests/graph/test_topology_and_implementation.py`, and the focused current-node tests for
bootstrap, rerun, HITL2, readiness, and final delivery; and the archived HITL2
human-decision/autonomous-continuation changes at
`openspec/changes/archive/2026-07-16-implement-deep-research-hitl2-node/` and
`openspec/changes/archive/2026-07-24-make-hitl2-decisions-agent-led/`.

**Explicit exclusions.** Do not rewrite any `workflow.md` prose yet; do not change capability
Markdown, prompt builders, tools, parser behavior, gate behavior, topology, runtime bridge, or
product-responsibility, participation, commitment, or model-branch evidence merely to make the
inventory pass. Do not reactivate HITL2 input or
create a readiness/final model call in this change. Do not add a source checker or reader task yet:
the 11 cards do not exist until change 1, which owns the non-runtime checker and its focused tests.

**Proof and review.** The topology selection proves the ordered 11-node denominator; the 19-case
inventory/capability selection proves the six current discovered direct-model-loop owners; the
separate 44-case capability-cohort selection validates the exact 16-current-branch denominator;
and the focused 27-case controller bundle proves the current mechanisms of bootstrap, rerun,
HITL2, readiness, and final delivery. Together they must enumerate 11 exact product responsibilities,
participation modes, commitment states, current mechanisms, deterministic authority boundaries, and
16 current direct model branches. The
review must record the HITL2 current/legacy interface drift and the final-delivery
current-code/accepted-integrity-gate drift, then state the precise product questions their future
Scope Cards must settle. The proposal must lead with a **Product Responsibility Review**. It may
append a **Charter Model-Branch Evidence Review** with current-runtime `node-agent`/`no-agent`
flags, but those flags prove only direct-branch presence or absence and may never occupy the primary
classification or role column. The Scope Card selects `change-admission`,
`authority-and-projections`, and `node-agent-workflow-integrity`; it selects neither
`human-interaction-integrity` nor `workflow-outcome-review`, because phase 0 changes no human
interaction, model/tool path, recovery, terminal behavior, or lifecycle projection.

#### Historical initial Scope Card -- 2026-07-29 (proposal created and first-polished; its later role-model re-alignment is recorded below)

- **Exact change name:** `define-cognitive-node-operating-model`.
- **New capability and primary module:** proposed `cognitive-node-interface`; its small external
  interface is the fixed node-local `workflow.md` shape, while its implementation remains authored
  reader projections in phase 1. The new capability hides the 11-node topology and source audit
  behind one uniform reader contract; it is not runtime configuration.
- **Completed re-alignment (after user confirmation):** replaced the
  old generic role field with exact `product responsibility`, `participation mode`, and `commitment
  state`; retain `current operating mechanism`, `primary cognitive/control program surface`,
  deterministic `authority boundary`, and audit-only `current model-branch evidence`; record the
  closed 11-node and 16-branch ledgers; state that a model candidate, human choice, and deterministic
  route writer are distinct seams.
- **Applied planning scope:** proposal/design/tasks and a delta spec for
  `cognitive-node-interface`; a narrow coexistence statement against
  `node-agent-reader-interface`; a primary Product Responsibility Review, a 16-branch closure
  ledger, and a separate audit-only Charter Model-Branch Evidence Review. The plan itself remains the
  audit record, not a runtime authority.
- **Read-only adjacent evidence:** topology; 11 node packages; four focused verification bundles
  (topology denominator, owner/local-capability discovery, sixteen-branch cohort, and current
  controller behavior); existing reader-interface, HITL2, readiness, and final-delivery specs; the
  two named HITL2 archives. Each answers a stated product-responsibility, participation,
  commitment, or current-mechanism fact and does not enter the implementation scope.
- **Out of scope:** all `workflow.md` rewrites, generated/static checks, prompt/capability/tool
  changes, new model calls, HITL2 interrupts, typed state changes, routes, lifecycle, UI adapters,
  test reclassification, and spec synchronization.
- **Proof plan:** retain the topology denominator selection; the passing 19-case inventory/
  capability-contract selection as the lowest deterministic owner-discovery seam; the existing
  44-case capability-cohort selection for the sixteen-branch denominator; and the focused 27-case
  controller bundle for the five non-active current mechanisms. Add no fake behavior test. The
  semantic propagation review checks the 11-node/16-branch audit against source, verifies that
  product responsibility leads every artifact, and verifies that the new projection cannot become a
  second authority.
- **Unresolved decision deliberately retained:** which specific non-inferable preference or
  irreversible authorization should ever make HITL2 interactive, and whether model assistance is
  appropriate. That decision belongs only to change 8, not this proposal.

- [x] Scope Card audited and submitted -- **STOP: wait for approval to propose**.
- [x] User approved this exact name and scope; OpenSpec proposal created.
- [x] First proposal polish completed; its Charter-binary hierarchy was later found incorrect.
- [x] User confirmed the product-responsibility-first OpenSpec artifact revisions; proposal, design,
  both delta specifications, and the apply ledger were rewritten without implementation changes.
- [x] Proposal re-polished and reconciled, including the semantic propagation review, exact 11-node/
  16-branch set checks, strict OpenSpec validation, and the 18/19/44/27 source evidence bundles --
  **STOP: wait for approval to apply**.
- [x] Applied, verified, archived, and this plan updated. The archive-only CNI/NRI delta was carried into Change 1 main specs -- **STOP before change 1**.

### Change 1/11 ✅ 已完成 — `normalize-cognitive-node-interfaces`

**Owned result.** Make every logical node readable in the Wave2-v1 structural shape, without
changing runtime behavior. Every card leads with specific product responsibility, participation mode,
commitment state, and then current mechanism: the six active cards expose their cognitive program
first; bootstrap and rerun expose intentional deterministic-control exclusions; HITL2 exposes its
conditional human-decision opportunity and current autonomous continuation; readiness and final
delivery expose their accepted deferred responsibilities and current fallbacks.

**Detailed scope.** Rewrite the six existing cards at
`graph/nodes/{hitl1,topic_planning,wave0,wave1,wave2_synthesis,targeted_evidence}/workflow.md` and
add cards at `graph/nodes/{bootstrap,hitl2,rerun,readiness,final_delivery}/workflow.md`, all under
`agent/src/deerflow_deep_research/`. Each card starts with product responsibility, participation
mode, commitment state, current operating mechanism, and deterministic authority boundary. Each
currently active card maps its real `node.py`, `prompts.py`, local `capabilities/*.md`, catalog case,
requested/runtime tool posture, feedback recipient, candidate admission owner, route writer,
executable consumer, and narrow proof seam. The HITL2/readiness/final-delivery cards instead link
their current fallback/controller and the spec or historical contract that declares their commitment
state, without inventing a prompt/capability body; `node-agent`/`no-agent` may not appear as card
identity. The change
also owns the static validation and reader-task fixtures/tests accepted in change 0, principally
`agent/tests/assets/workflow_nodes.py`, `agent/tests/contract/test_workflow_node_inventory.py`, and
the focused node-capability contract tests.

**Explicit exclusions.** No capability body, prompt-builder logic, prompt catalog content,
`run_agent` call, tool binding, parser/materializer, ledger/gate, route, checkpoint, or lifecycle
behavior changes. `workflow.md` remains a human/Coding-Agent reader interface and never becomes a
runtime prompt or second semantic authority.

**Proof and review.** One fixed reader task per node must first identify the product outcome at
stake, then find the correct first seam from an active/deferred cognitive symptom, a human-decision
UX symptom, or a deterministic-control symptom, and name a rejected wrong-first edit. The checker
proves exactly 11 cards whose node names match the node ledger and whose product-responsibility
fields are non-generic; it also rejects a grouped row, a missing commitment state, or a Charter flag
in an identity field. Shape/source checks prove only navigation consistency, never cognitive quality
or permanent role classification.

- [x] Scope Card audited and submitted.
- [x] User approved this exact name and scope; OpenSpec proposal created and polished.
- [x] Applied, verified, spec-synced, archived, and this plan updated. Commit `112a2b3` added/revised 11 reader cards, static validation, test evidence, and CNI/NRI/PRS main-spec ownership -- **STOP before change 2**.

### Change 2/11 — `make-active-cognitive-programs-evaluable`

**Owned result.** Turn every one of the 16 current direct model branches into a reviewable cognitive
program with a stable prompt projection, a bounded cognitive hypothesis, and the right mix of
composition, agent-loop, and (when needed) live-eval evidence. This change owns only the six current
active cognitive responsibilities and their exact 16-branch ledger; deferred/conditional activation
dossiers are deliberately isolated in change 7.

**Detailed scope.** The owned program surfaces are
`agent/src/deerflow_deep_research/graph/prompt_catalog.py`,
`agent/scripts/prompt_dump.py`, `agent/node_prompts/`,
`agent/src/deerflow_deep_research/agents/phase_prompt.py`, and
`agent/src/deerflow_deep_research/runtime/node_agent_bridge.py`. The proposal may extend their
focused proof in `agent/tests/graph/test_prompt_catalog.py`,
`agent/tests/graph/test_prompt_dump.py`, `agent/tests/unit/test_phase_prompt.py`,
`agent/tests/unit/test_node_agent_bridge.py`, `agent/tests/assets/workflow_nodes.py`,
`agent/tests/assets/requirement_evidence.py`, and the relevant files under
`agent/tests/scenarios/` and `agent/tests/eval/`. It must give every branch a bounded question,
model-visible trusted/untrusted layers, capability body, requested/enforced tools, candidate
properties, and feedback that a subsequent model turn actually receives. For each of the 16 ledger
rows, it records the exact product responsibility, capability binding, prompt/render seam, feedback
recipient, candidate/authority seam, deterministic guardrail, and whether a judgment eval is
required. The change does not create dossiers for HITL2, readiness, or final delivery.

**Explicit exclusions.** This change does not tune capability language or prompt behavior for
quality, broaden tool authority, change candidate admission, activate HITL2 interaction, or add a
readiness/final model call. The catalog and dump remain projections, not prompt authority. A mocked
JSON parser test cannot be relabeled as an agent-loop or live-eval proof. Deferred/conditional
responsibility dossier work belongs only to change 7.

**Proof and review.** Deterministic cases use the production renderer/bridge to prove composition,
tool bounds, feedback delivery, parsing, and admission for active branches. Scenario/live cases are
added only where a claim depends on model judgment, with an explicit rubric and nondeterministic
boundary. Every 16-branch row must be explicitly closed or remain visibly pending; a node aggregate
cannot stand in for its repair/diagnostic/verifier branches. Existing tests receive a
claim classification (`cognitive-program`, `deterministic-guardrail`, `wiring`, or `obsolete
duplicate`) before any later consolidation decision.

- [x] Scope Card audited and submitted.
- [x] User approved this exact name and scope; OpenSpec proposal created.
- [x] Proposal polished and reconciled; semantic propagation review passed.
- [x] Applied, verified, spec-synced, archived, and this plan updated. Commit `846c107` added the
  16-branch cognitive-program evidence ledger, bridge/composition/feedback evidence, and CPE/NAC/
  NOA/NPC/EVH main-spec ownership -- **STOP before change 3**.

### Change 3/11 — `repair-wave1-baseline-and-gate-conformance`

**Owned result.** Repair the known Wave1 top-level baseline-loading and critic/open-question gate
conformance gap before anyone treats Wave1's model loop as cognitively calibrated.

**Detailed scope.** The initial audit is limited to
`agent/src/deerflow_deep_research/graph/nodes/wave1/node.py`,
`agent/src/deerflow_deep_research/graph/nodes/wave1/prompts.py`,
`agent/src/deerflow_deep_research/graph/nodes/wave1/capabilities/`, and
`agent/src/deerflow_deep_research/engine/gate_fixtures.py`, plus the actual gate owner discovered
from those paths. Likely proof surfaces are `agent/tests/unit/test_wave1_contracts.py`,
`agent/tests/unit/test_wave1_provider_shapes.py`,
`agent/tests/integration/test_wave1_work_units.py`, and the applicable gate/workflow evidence
inventory. The accepted Scope Card must state separately whether the defect is baseline context,
candidate construction, deterministic gate admission, or feedback/recovery wiring.

**Explicit exclusions.** No unrelated Wave0/Wave2/targeted-evidence calibration, no global retry
architecture rewrite, no weakening of critic/open-question gate authority, and no conversion of a
deterministic gate into model authority merely to conceal the discrepancy.

**Proof and review.** Demonstrate the corrected top-level and repair paths with the real owning
node/gate seam, including an adverse case that cannot publish or route through an invalid candidate.
Select `workflow-outcome-review` whenever the audited repair changes feedback, retry, terminal, or
lifecycle behavior. Update Wave1's reader card only to reflect an accepted behavior change.

- [x] Scope Card audited and submitted.
- [x] User approved this exact name and scope; OpenSpec proposal created.
- [x] Proposal polished and reconciled; semantic propagation review passed.
- [x] Applied, verified, spec-synced, archived, and this plan updated. Commit `6bb4af4` repaired
  same-generation baseline reconstruction, pre-persistence Wave1 validation, bounded critic review
  materialization, and deterministic review-projection gate conformance -- **STOP before change 4**.

### Change 4/11 — `calibrate-intake-and-planning-cognitive-loops`

**Owned result.** Improve the cognitive programs that turn human input into a trusted profile and a
research plan: HITL1's profile-brief/semantic-intake/repair branches and topic planning's
decomposition/repair branches.

**Detailed scope.** The candidate program ownership is limited to
`agent/src/deerflow_deep_research/graph/nodes/hitl1/{node.py,prompts.py,capabilities/}` and
`agent/src/deerflow_deep_research/graph/nodes/topic_planning/{node.py,prompts.py,capabilities/}`.
The Scope Card must name the specific capability Markdown, prompt builder, model-visible context,
candidate schema, actual feedback path, and deterministic admission owner before proposing a
wording or tool-posture change. Expected proof surfaces include
`agent/tests/graph/test_hitl1_prompts.py`, `agent/tests/graph/test_hitl1_node.py`,
`agent/tests/graph/test_topic_planning_prompts.py`,
`agent/tests/graph/test_topic_planning_node.py`,
`agent/tests/integration/test_hitl1_lifecycle.py`,
`agent/tests/integration/test_topic_planning_lifecycle.py`, and the scenario/eval cases accepted in
change 2.

**Explicit exclusions.** This change does not activate HITL2 interaction or the readiness/final
deferred roles; those have their own named contracts below. Do not alter bootstrap/rerun, Wave0+
evidence programs, or generic bridge behavior unless the approved audit demonstrates that the
generic bridge, rather than a node-local program, is the causal owner.

**Proof and review.** Each altered branch carries one cognitive hypothesis and its appropriate
composition plus model-judgment evidence. The proposal must separately preserve deterministic
profile/plan admission, checkpoint, and route proof; a more fluent response alone is not success.

- [x] Scope Card audited and submitted.
- [x] User approved this exact name and scope; OpenSpec proposal created.
- [x] Proposal polished and reconciled; semantic propagation review passed.
- [x] Applied, verified, spec-synced, archived, and this plan updated in commit `6a45316` --
  **STOP before change 5**.

### Change 5/11 ✅ 已完成 — `calibrate-evidence-intake-cognitive-loops`

**Owned result.** Improve Wave0 and Wave1's evidence-intake reasoning, source selection, repair
feedback, and candidate boundaries, with Wave1 work permitted only after change 3 is archived.

**Detailed scope.** The candidate program surfaces are
`agent/src/deerflow_deep_research/graph/nodes/wave0/{node.py,prompts.py,capabilities/}` and
`agent/src/deerflow_deep_research/graph/nodes/wave1/{node.py,prompts.py,capabilities/}`, along with
the narrowly identified gate/worker owner required for an accepted candidate. Expected evidence
includes `agent/tests/graph/test_wave0_worker.py`,
`agent/tests/graph/test_wave0_provider_shapes.py`,
`agent/tests/domain/test_wave0_result.py`,
`agent/tests/integration/test_wave0_work_units.py`, the Wave1 tests named in change 3, and focused
scenario/eval cases. The Scope Card must say whether the first seam is capability policy, prompt
composition, retrieval/tool posture, feedback delivery, candidate parsing, or deterministic
admission.

**Explicit exclusions.** Do not recalibrate Wave2 synthesis or targeted retrieval here; do not
relax evidence admission, gate, ledger, checkpoint, or graph-route authority; do not sweep in
unrelated provider-shape cleanup because it happens to share a fixture.

**Proof and review.** Each branch needs a declared evidence-quality hypothesis, a production
agent-loop proof for its model/tool path, and a deterministic guardrail proving invalid evidence
does not gain authority. Live evaluation is required only for a judgment claim that a scripted
loop cannot honestly establish.

- [x] Scope Card audited and submitted.
- [x] User approved this exact name and scope; OpenSpec proposal created.
- [x] Proposal polished and reconciled; semantic propagation review passed.
- [x] Applied, verified offline, spec-synced, archived, and this plan updated in commit `e64b83d`.
  Credentialed live evaluation is supplemental and was not run -- **STOP before change 6**.

### Change 6/11 ✅ 已完成 — `calibrate-evidence-judgment-cognitive-loops`

**Owned result.** Improve Wave2 synthesis and targeted evidence's ability to form useful gaps,
critique accepted evidence, choose bounded retrieval, and return candidates that deterministic
owners may lawfully admit.

**Detailed scope.** Work is limited to
`agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/{node.py,prompts.py,capabilities/}`
and `agent/src/deerflow_deep_research/graph/nodes/targeted_evidence/{node.py,prompts.py,capabilities/}`.
Likely proof surfaces are `agent/tests/graph/test_wave2_synthesis_real.py`,
`agent/tests/graph/test_wave2_provider_shapes.py`,
`agent/tests/graph/test_targeted_evidence_real.py`, the focused bridge tests, and the accepted
scenario/eval corpus. If behavior changes, the two `workflow.md` cards are updated as factual
reader projections in the same change; they remain non-runtime.

**Explicit exclusions.** This change does not activate HITL2 interaction or the readiness/final
deferred roles; their named contracts own those behaviors. Do not transfer gate verdict, ledger
publication, retry budget, checkpoint mutation, or executable route authority to a model; do not
conceal a Wave0/Wave1 intake defect with a Wave2 prompt workaround.

**Proof and review.** Validate the altered synthesis or targeted-retrieval claim with an explicit
rubric, a bounded agent-loop trace, and deterministic admission/route proof. The Scope Card must
identify the evidence cohort dependency it relies on and any residual uncertainty that requires a
live evaluation rather than a fixture.

- [x] Scope Card audited and submitted.
- [x] User approved this exact name and scope; OpenSpec proposal created.
- [x] Proposal polished and reconciled; semantic propagation review passed.
- [x] Applied, verified offline, spec-synced, archived, and this plan updated in commit `078dde7`.
  Credentialed live evaluation was unavailable and remains supplemental -- **STOP before change 7**.

### Change 7/11 ✅ 已完成 — `prepare-deferred-cognitive-and-human-decision-dossiers`

**Owned result.** Prepare three independently reviewable activation dossiers without activating any
runtime behavior: HITL2's **conditional/unresolved** human-decision opportunity, readiness's
**accepted-but-deferred** evidence-sufficiency responsibility, and final delivery's
**accepted-but-deferred** report-composition responsibility. This removes the old error of treating
all three as a generic “non-agent” cohort or treating a dossier as a model-loop implementation.

**Detailed scope.** The change owns the three node rows in the completion ledger and their exact
product-responsibility, participation-mode, commitment-state, current-mechanism, authority, and
activation-proof records. It reads the current node sources, the accepted HITL2/readiness/final
delivery specs, their closest deterministic tests, and the archived HITL2 history. The HITL2 dossier
must state the still-unresolved decision trigger and the user-facing outcome required to resolve it.
The readiness/final dossiers must state the accepted future bounded question, model-visible input
boundary, candidate contract, deterministic admission owner, failure posture, and evaluation
criterion. Each dossier names the next exact change (`8`, `9`, or `10`) but does not create it.

**Explicit exclusions.** No `run_agent` call, prompt, capability Markdown, tool policy, human
interrupt, state/route/lifecycle change, `workflow.md` behavior claim, or classifier update. Do not
turn HITL2's conditional opportunity into an implementation commitment merely because readiness and
final delivery have accepted deferred responsibilities.

**Proof and review.** A dossier is complete only when it passes the semantic propagation review and
has one explicit disposition: `conditional/unresolved` for HITL2 until a user-approved trigger
exists; `accepted-but-deferred` for readiness/final delivery; a named deterministic authority owner;
and a proof/eval plan that cannot be satisfied by the absence of a model branch. The user must see
the three dossiers separately and approve or reject their later behavior Scope Cards separately.

- [x] Scope Card audited and submitted: three separate dossiers only; no runtime activation,
  prompt, capability, tool, state, route, or lifecycle behavior change.
- [x] User authorized this exact name and scope; OpenSpec proposal created.
- [x] Proposal polished and reconciled, including semantic propagation review.
- [x] Applied, verified offline, spec-synced, archived, and this plan updated in commit `2feb709`.
  The three future Scope Cards were separately approved for proposal; no runtime activation occurred.
  **STOP before change 8**.

### Change 8/11 ✅ 已完成 — `introduce-hitl2-human-decision-experience`

**Owned result.** Resolve HITL2's conditional human-decision / authorization responsibility. Only if
the dossier identifies a genuine non-inferable user preference or irreversible authorization and the
user approves it may this change introduce an experience. Otherwise it records the explicit,
user-approved no-change disposition and retains autonomous continuation. Its current autonomous-only
continuation is a source fact, not an identity. An implemented experience must give the user a legible
decision brief and meaningful product choices, never a menu of internal graph route identifiers.
Whether a bounded LLM assists the brief or free-text interpretation is an explicit Scope Card decision,
not an assumption hidden behind the word "agent".

**Detailed scope.** The completed disposition change read the HITL2 control surfaces:
`agent/src/deerflow_deep_research/graph/nodes/hitl2/{node.py,prompts.py,contracts.py}`, the related
typed human-input/lifecycle contracts under `agent/src/deerflow_deep_research/domain/`, and the
graph-owned adapters in `agent/src/deerflow_deep_research/runtime/human_input.py`,
`agent/src/deerflow_deep_research/runtime/run_experience.py`, and the narrowly identified runtime
resume/binding owner. The user approved the no-change disposition: it changed no runtime surface,
but synchronized stale autonomous-continuation wording in `openspec/specs/hitl2-node/spec.md`,
`openspec/specs/research-graph-lifecycle/spec.md`, and registry entry `HIT-002`. An approved future
trigger requires a separate behavior-change proposal to own any runtime delta requirements for
`openspec/specs/hitl2-node/spec.md`, `openspec/specs/human-interaction-contract/spec.md`,
`openspec/specs/research-run-experience/spec.md`, or `openspec/specs/research-graph-lifecycle/spec.md`.
Expected proof started at
`agent/tests/unit/test_hitl2_brief.py`, `agent/tests/unit/test_hitl2_real.py`,
`agent/tests/graph/test_hitl_nodes.py`, `agent/tests/graph/test_research_graph.py`, and the focused
resume/experience tests. The archived July 16 and July 24 HITL2 changes are historical evidence,
not implementation authority.

**Explicit exclusions.** Do not restore an unconditional confirmation screen, expose `proceed`,
`repair`, `rerun`, or `stop` as raw route UX, allow a model/presentation adapter to select a route,
or let a user response bypass request-id binding, typed validation, generation/staleness checks, or
the deterministic route writer. Do not add an LLM solely to make a card look agentic. If the Scope
Card chooses no model support, it must still deliver the bounded human-decision interface honestly.

**Proof and review.** The Scope Card must state the exact non-inferable preference/authorization,
trusted producer, recommendation/default, permitted user-visible actions, response binding,
candidate mapping, and route owner. If it resolves to no change, it records the user decision and why
autonomous continuation is the correct product outcome. A model-assisted variant additionally needs a
capability/prompt, bounded tool posture, a structured candidate, production-loop evidence, and
model-judgment eval; a deterministic variant must not claim those proofs. In either implementation
case, workflow evidence proves a stale, malformed, or unapproved response cannot change lifecycle
state.

- [x] Scope Card audited and submitted as a disposition-only proposal: current source evidence
  identifies no genuine non-inferable preference or irreversible authorization.
- [x] User authorized this exact name and proposal scope; the explicit no-change disposition was
  recorded with the owning specification deltas.
- [x] Proposal polished, reconciled, and strict-validated; the user approved autonomous
  continuation rather than a non-inferable preference or irreversible authorization.
- [x] Applied, verified offline, main specs synchronized, and archived in commit `982dce6`.
  No HITL2 runtime behavior was activated. **STOP before change 9**.

### Change 9/11 — `activate-readiness-evidence-critic-loop`

**Owned result.** Realize readiness's accepted product responsibility as evidence sufficiency / answerability judgment
by replacing its current "all ready" deterministic fallback with the specified bounded read-only
evidence critic. The critic evaluates answerability per must-answer question and returns typed
verdict candidates; hard rules, report-plan materialization, and route selection remain
deterministic.

**Detailed scope.** Primary implementation ownership is
`agent/src/deerflow_deep_research/graph/nodes/readiness/{critic.py,node.py,contracts.py,hard_rules.py,materializer.py}`.
The Scope Card may additionally own the exact local capability/prompt resource it creates and the
shared renderer/bridge only if the audit proves that it is the causal integration seam:
`agent/src/deerflow_deep_research/agents/phase_prompt.py`,
`agent/src/deerflow_deep_research/runtime/node_agent_bridge.py`,
`agent/src/deerflow_deep_research/graph/prompt_catalog.py`, and `agent/scripts/prompt_dump.py`.
Specification scope is `openspec/specs/readiness-node/spec.md`, plus the applicable node-agent and
evaluation specs. Expected proof includes `agent/tests/unit/test_readiness_real.py`, focused
renderer/bridge cases, a real-node scripted agent-loop case, and a bounded scenario/live eval for
answerability judgments that cannot be honestly asserted from fixtures alone.

**Explicit exclusions.** No web/search tools, evidence admission, ledger publication, checkpoint
authority, route authority, HITL2 UX redesign, or final report prose generation. The agent may
recommend `ready_substantive`, `ready_insufficient_judgment`, or `blocked_repair_required`; it may
not promote a conclusion or decide the executable repair edge.

**Proof and review.** Prove model-visible inputs are limited to must-answer questions and accepted
evidence/provenance references, tool policy is zero-web/read-only, invalid outputs fail closed, and
each verdict is materialized by the existing deterministic owner. Include an evaluation rubric for
the distinction between insufficiency and blocked repair. This change triggers
`node-agent-workflow-integrity` and `workflow-outcome-review`.

- [x] Scope Card audited and submitted: one bounded zero-tool critic candidate,
  ledger-derived evidence projection, deterministic admission, and existing repair bounds.
- [x] User authorized this exact name and scope; OpenSpec proposal created.
- [x] Proposal polished and reconciled: ledger projection and structural-read failure,
  per-question admission/retention, readiness-specific bridge policy, capability injection,
  conservative critic failure posture, and evaluation boundaries passed strict OpenSpec,
  diff, and charter checks. **STOP: wait for approval to apply**.
- [x] Applied and offline-verified: real readiness now calls one bounded zero-tool critic through
  its dedicated bridge and declared ledger controller; deterministic admission preserves existing
  hard-rule/materializer/route ownership. The 19-branch evidence ledger adds a separately
  classified supported/insufficient/repair-required judgment corpus. Strict change validation,
  architecture governance, test assets, and `UV_OFFLINE=1 make verify` passed. **STOP: wait for
  sync/archive authorization**.
- [x] Applied, verified offline, synchronized to `readiness-node` and `evaluation-hardening`, and
  archived at `openspec/changes/archive/2026-07-30-activate-readiness-evidence-critic-loop/`.
  Committed as `0254078`. **STOP before change 10**.

### Change 10/11 ✅ 已完成 — `activate-final-report-composition-loop`

**Owned result.** Final delivery's accepted report-composition/communication responsibility now uses
one bounded zero-tool Node Agent to return a typed layout candidate over the immutable readiness
report plan and accepted evidence projection. Deterministic admission and rendering preserve exact
approved conclusion, uncertainty, and citation bindings; final integrity verification, artifact
publication, terminal status, and route remain deterministic.

**Detailed scope.** Primary implementation ownership is
`agent/src/deerflow_deep_research/graph/nodes/final_delivery/{composer.py,node.py,contracts.py,gate.py,capabilities.py}`,
its local `capabilities/composer.md`, and the bounded readiness-plan/evidence store projection. The
change added only the local capability/prompt resource and the renderer/bridge/catalog projection
surfaces required for the genuine composer branch. It modified
`openspec/specs/final-delivery-node/spec.md` and the applicable node-agent/evaluation specs.
Proof starts at `agent/tests/unit/test_final_delivery_real.py` and includes focused
composition, integrity-gate, scripted real-loop, and report-quality scenario/eval cases. The local
`workflow.md` is updated as a factual reader projection of the accepted behavior.

**Explicit exclusions.** No web/search tools, new research/evidence collection, readiness verdict
changes, citation fabrication, direct publication by the model, or model-owned terminal/repair
route. The composer cannot turn a mandatory uncertainty into a conclusion or use evidence outside the
accepted/readiness-bounded inputs.

**Proof and review.** Prove the rendered request contains only the authorized report plan/evidence
layers, layout admission/rendering preserves conclusion/uncertainty bounds, citation-map candidates validate, and the
integrity gate/publisher reject malformed or unsupported output. Report usefulness needs an explicit
human/model-judgment rubric; artifact and lifecycle safety retain deterministic proof. This change
triggers `node-agent-workflow-integrity` and `workflow-outcome-review`.

- [x] Scope Card audited and submitted: one zero-tool report/citation-map candidate,
  readiness-bounded projection, deterministic admission, and existing final gate/publisher
  authority.
- [x] User authorized this exact name and scope; OpenSpec proposal created.
- [x] Proposal polished and reconciled; user separately authorized apply.
- [x] Applied, verified offline, synchronized, and archived at
  `openspec/changes/archive/2026-07-30-activate-final-report-composition-loop/`; committed as
  `580efc9`. **STOP before change 11**.

### Change 11/11 — `govern-cognitive-program-evidence`

**Owned result.** Make cognitive-program evidence reviewable and keep test consolidation tied to
preserved risks rather than to a target test count.

**Detailed scope.** The change owns the evidence inventories and review enforcement around
`agent/tests/assets/workflow_nodes.py`, `agent/tests/assets/requirement_evidence.py`,
`agent/tests/assets/evidence.py`, `agent/tests/scenarios/`, and `agent/tests/eval/`. It may revise
the relevant review-policy documentation under
`openspec/governance/agent-charter/policies/`,
  `openspec/governance/check_agent_charter.py`, and their focused workflow/contract tests. Its
  deliverable is a compact evidence board: product responsibility first, participation mode,
  commitment state, current operating mechanism, deterministic authority, audit-only current
  model-branch evidence, cognitive hypothesis, composition proof, deterministic guardrail, agent-loop
  or human-decision proof, live-eval applicability, known limitation, and the exact selected test/eval
  evidence.

**Explicit exclusions.** No bulk test deletion, marker relabeling, or coverage-count objective.
A test may be removed only in a separately approved, bounded follow-up after the board maps its
risk to an equal-or-stronger retained proof. This change does not alter node prompts, capability
Markdown, tool posture, candidate admission, or graph behavior.

**Proof and review.** The board must close all 11 node rows and all 20 active direct-branch rows;
HITL2, readiness, and final delivery must retain distinct commitment states, and model-branch evidence
may not replace a responsibility row. It must distinguish `cognitive-program`, `human-decision`,
`deterministic-guardrail`, and `wiring` claims. Governance tests must reject an under-specified
prompt/capability proposal, a false active-loop claim, a Charter-binary-as-identity claim, a grouped
ledger row, and invalid evidence mappings. The final review names remaining source/spec/test
discrepancies as future behavior work rather than normalizing them away.

- [x] Scope Card audited: exact 11-node topology, 20-branch catalog/cohort, current
  reader/dossier drift, selected evidence joins, and zero-test-deletion boundary.
- [x] User approved this exact name and scope; OpenSpec proposal, design, three delta specs,
  and tasks created; strict validation passed.
- [x] Proposal polished and reconciled; user separately authorized apply.
- [x] Applied and verified offline; every selector set remains a superset, all three main specs were
  synchronized, and the change was archived at
  `openspec/changes/archive/2026-07-30-govern-cognitive-program-evidence/`. This plan is complete;
  no follow-up change is automatically authorized.

## Evaluation Matrix

| Claim | Correct primary evidence | Insufficient evidence alone |
| --- | --- | --- |
| Capability/prompt body is actually model-visible | Production renderer/bridge composition case plus catalog projection | Markdown file existence or metadata assertion |
| Model sees the right assignment, untrusted data and feedback | Scripted real agent-loop case that asserts ordered requests | Parser unit test or a mocked helper call |
| Model makes a useful cognitive judgment | Bounded scenario/live eval with explicit rubric and failure disposition | Deterministic JSON fixture or aggregate pytest count |
| Product responsibility is stated honestly | User-approved Scope Card plus accepted product/spec/history trace | Direct `run_agent` discovery, a generic category, or a Charter binary flag |
| Participation mode and commitment state are stated honestly | Approved product decision plus current source/spec history | Current mechanism, a reader title, or a future activation dossier |
| Current operating mechanism is stated honestly | Source audit plus focused runtime/controller proof | Product responsibility, participation mode, or a future activation dossier |
| Deferred or conditional responsibility is described honestly before activation | Current fallback plus owning spec/history trace, commitment state, and activation dossier | Absence of a `run_agent` call or a placeholder card |
| Human decision has useful, safe UX | Bound request/response workflow proving meaningful user-visible options, typed binding, and deterministic mapping | Raw graph-route menu, generic confirmation, or a UI snapshot alone |
| Bad candidate cannot gain authority | Parser/materializer/controller/ledger guardrail test | Successful model response or document prose |
| Wrong route/terminal outcome is contained | Gate/wrapper/builder test at the route writer/consumer seam | A model-prompt test |
| Every current direct model branch is closed | One exact branch-ledger row with composition, loop/feedback, authority/guardrail, and eval disposition evidence | Node aggregate test, another branch's proof, or the aggregate count `20` |
| A deterministic-controller responsibility is honestly scoped | Source/spec audit plus controller-only card and controller test | Absence of a capability Markdown file or an audit-only Charter flag |

## Explicit Non-Goals

- Do not let Markdown, prompt catalog, review cards or tests become lifecycle authority.
- Do not replace the bounded Node Agent roles with a giant generic agent abstraction.
- Do not send all graph decisions, retries or evidence admission through a model.
- Do not delete deterministic tests merely because they are not model evaluations.
- Do not claim a fake/scripted test proves live model quality.
- Do not make bootstrap or rerun LLM-bearing only to satisfy a uniform template.
- Do not restore HITL2 as a raw internal-route menu or turn human confirmation into a ritual with no
  real preference/authorization at stake.

## Completion Definition

This plan is complete. All 11 nodes use the canonical interface with exact product responsibility
first; participation mode, commitment state, current operating mechanism, deterministic authority,
and model-branch evidence remain separately auditable; all 11 node-ledger rows and all 20
current-branch rows close through change 11; and every active branch has a reviewable cognitive
program and appropriate evidence. HITL2 remains explicitly `conditional/unresolved`, with the sole
activation dossier requiring a fresh separately approved behavior change if its product precondition
emerges. Readiness and final delivery no longer hide accepted cognitive work behind unexamined
fallbacks, while bootstrap/rerun remain explicit intentional controllers. No Charter
`node-agent`/`no-agent` flag substitutes for product responsibility, participation, or commitment,
and uniform Markdown alone never substitutes for prompt/feedback/evaluation governance.

## Immediate Next Step

**Current next step.** None within this plan. Any HITL2 activation, test retirement, or other
follow-up behavior starts with a fresh Scope Card and separate proposal/apply authorization.
