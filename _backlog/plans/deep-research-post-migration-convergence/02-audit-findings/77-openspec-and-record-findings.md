# 77 - OpenSpec And Record Findings

> 取证基线: 2026-08-13 @ `c92ed9d028ab6ac1bb144adba62c02ba94cc2f2b`
> 应用/spec 行为基线: `5bb41c16a45ff3caae6e5b1e900610c91bf68336`
> 范围: current main specs、registries、CONTEXT/ADR/docs、generated projections、agent/CI delivery routes
> 历史边界: `openspec/changes/archive/` 与 `_backlog/_done/` 只作证据，不做全文术语清洗

## Record authority map

| Record | Role | Current fact authority |
| --- | --- | --- |
| main capability spec | required behavior | capability owner after archive/sync |
| active delta | pending behavior | one selected OpenSpec change；当前为零 |
| `req-registry.yaml` | stable ID/status registry | requirement governance |
| `project-structure.toml` | exact structural inventory | architecture governance |
| product `CONTEXT.md` | ubiquitous language | glossary only，当前尾部越界见 NC-C03 |
| ADR | immutable historical decision/reason | status/supersession，不是 current behavior |
| README/docs index | navigation/current support projection | linked owner，不复制 authority |
| generated topology/agent locator | derived projection | generator/registry |
| archive/_done | historical evidence | never pending/current authority |

## Finding OR-01: Clean clone 已丢失仓库承诺的 CI workflow

commit `5bb41c1` 删除 tracked `.github/workflows/agent-tests.yml` 与
`agent-live-evaluation.yml`，并把整个 `.github/` 加入 `.gitignore`。本机仍留有 ignored copies，因此当前
working tree上的 tests看似可通过；但 `git ls-files .github/workflows` 为零，clean clone不会获得它们。

这不是可选 editor tooling。current testing guide正向声明 deterministic PR/push workflow和 manual live
workflow；至少五个 contract tests直接读取这两个路径并验证 lane/suspension/verification behavior。clean
clone因此既没有 promised automation，也会在相关 tests读取文件时失败。当前 checker只验证文件内容/存在，
没有验证 required delivery artifact被 Git tracked，导致 ignored local copy掩盖结构漂移。

修复必须优先于 cleanup implementation：恢复明确批准的 workflow为 tracked delivery artifacts，缩小
`.gitignore`，并增加 trackedness negative guard。不能仅修改 tests跳过文件，也不能把 local copy当恢复证据。

## Finding OR-02: Clean clone 也丢失了 current docs 声明的项目 OpenSpec skills

同一 commit删除 `.agents/skills/.openspec-target`、六个 OpenSpec workflow skills与 polish skill，再忽略
整个 `.agents/`。root README和 AGENTS仍声明“项目自有 OpenSpec skills在 `.agents/skills/`，见
`.openspec-target`”；本机 ignored copies存在，所以当前 agent环境可发现它们，但 clean clone中
`git ls-files .agents/skills` 为零，root `.openspec-target` 也不存在。

这里要区分两类 skill：global/shared skills可 machine-local；项目自有 OpenSpec workflow携带本仓 planning
boundary、store/root routing和 apply/archive行为，docs已把它们当 repository entry。若决定它们应随仓库
交付，就恢复 tracked files并登记结构；若产品决定改为外部安装，则必须提供可复现 installer/version source，
并同步 README/AGENTS。当前状态是两种 authority都没有，不能标 `historical`。

## Finding OR-03: Main specs/requirement registry mechanically clean，但若干 capability owner 已漂移

当前 49 个 capability spec、393 registered IDs、0 active changes通过既有 checker；这证明格式、ID和
coverage joins自洽。它不推翻 findings中已取证的语义漂移：node capability spec写迁移时间层、Run Session/
lifecycle-binding capability仍引用退役 owner、fixture/full-fake requirements把 fallback写成 current长期行为。

这些不能做一次 specs rewrite。每个 owner-local change需保留 never-reuse registry规则：语义连续可迁名，
语义已终止则 retire ID并由 target owner分配新 ID；negative invariant归 current boundary，而不是永久保留
空壳 capability。

## Finding OR-04: `project-structure.toml` 有一项可删 scaffold，也缺两类 delivery artifact

TA-C02已证明 `tests/e2e` required directory只维持空 `.gitkeep`，可随 structure delta删除。相反，registry
没有登记 root CI workflows或 project-owned agent skills；ignored-path allowlist还明确包含整个 `.agents/`，
使 checker无法发现 skills从版本控制消失。`.github/` 虽未列入 registry allowlist，却也没有 required-path/
trackedness guard。

目标不是把所有 dot-directory纳入结构表，而是只登记被 current docs/tests承诺的具体 delivery artifacts，
并让 checker验证它们存在且 tracked。local caches/editor settings仍可 ignored。

## Finding OR-05: Product `CONTEXT.md` 尾部是重复 design records，ADR 本体应保留

product glossary在 language definitions后复制“People Initiate Evaluation Review”等六段 architecture
statements；对应 ADR 0022-0026与 specs已经拥有这些事实。NC-C03给出逐段迁移条件。另一个 dormant
`Local-First Deployment` term由 ADR 0002/0008保存历史，current glossary不应继续把它作为状态账本。

ADR 0007已标 `superseded by ADR-0028`；0002/0003/0006/0008/0010明确写 non-current/dormant scope。没有
current docs把这些历史 ADR当 runtime behavior authority，故不应删除/改写其历史名。当前缺少统一 ADR index
不自动构成新结构需求；README/docs未把读者路由进这些 old ADR，direct link与 status已足以消歧。

## Finding OR-06: Current docs 路由大体正确，只有 superseded DPT report 可减

root/product README、docs index把 current product/operator/testing/evaluation routes分开。dated live baseline
和 release attestation以有日期、有限证据导航；regression descent是 current policy。TA-C05证明 superseded
DPT report无 current route，只有 shape-only test保护，可在证据对照后删除。

文档清理应保持 index角色：不把 Candidate结论复制进 product docs，不把 dated artifact冒充 freshness，
也不因 old term residual批量改 history。

## Finding OR-07: Generated topology/agent locator 有 current regeneration guard，应保留

`docs/deep-research-topology.md` 由 `render_topology_snapshot()`生成，contract test逐字比较；prompt catalog也
有 fixed-root generator/check。`deep_research_harness/AGENTS.md` 的结构 locator由 registry checker验证，
archive不能替代 current structure authority。这些是可证伪 projections，不是手工重复文档。

删除生成物会失去 review surface；手改则建立第二 authority。只有 owning graph/registry change时同步
regenerate并运行 planted stale-output tests。

## Finding OR-08: Archive 与 `_done` 的 historical boundary 正确，不做全库旧词清洗

spec/architecture checkers明确排除 archived delta作为 current terminology authority，同时拒绝 archive-only
spec替代 main spec。tests还直接引用少数 `_done` / suspended diagnosis作为历史 evidence。当前没有证据要求
重写历史正文；只需在 current inbound link损坏或历史文件冒充 current authority时修 route。

## 最终审计 Candidate

### OR-C01 - Restore tracked CI workflow delivery before cleanup implementation

- **证据**: `5bb41c1` deletion；`.github/` ignore；zero tracked workflow files；current docs与 contract tests正向
  依赖；ignored local copies掩盖 clean-clone failure。
- **当前 owner**: 无可交付 owner；machine-local residue暂时满足 path readers。
- **目标 owner**: repository-tracked CI workflows，Test/Evidence Owner负责 deterministic/manual-live lane contract。
- **Disposition**: `repair`，P0 blocker。
- **迁移条件**: 从最后 tracked revision与 current Make/docs/spec核对 workflow内容；决定 exact supported lanes。
- **删除条件**: 不适用；恢复项只有在 docs/spec/tests/hosting automation共同明确退役后才能另审计。
- **保留负向护栏**: clean clone trackedness check；deterministic PR/push lane；live manual-only；release E2E仍 suspended。
- **OpenSpec change slice**: `restore-repository-automation-delivery`，必须是首个 implementation change。

### OR-C02 - Resolve and restore reproducible project OpenSpec skill delivery

- **证据**: README/AGENTS positive route；zero tracked `.agents/skills`；missing referenced root target；ignored local
  copies与 prior tracked revision。
- **当前 owner**: ambiguous machine-local copies；docs错误声称 repository ownership。
- **目标 owner**: Repository Governance Owner选择 tracked project skills，或 versioned external installer/source。
- **Disposition**: `repair / product decision`，不得静默维持现状。
- **迁移条件**: 确认 skills是否项目特有、期望 agent clients和更新路线；消除 `.openspec-target` 路径歧义。
- **删除条件**: 若选择外部 owner，repo docs不再声称项目自有且 clean setup可复现；若选择 repo owner则不删除。
- **保留负向护栏**: clean clone discovery；planning-only/propose boundary；apply/archive分离；nearest OpenSpec root。
- **OpenSpec change slice**: `restore-repository-automation-delivery`；repository-vs-external owner是该 change 的
  admission decision，不另造未编排的实施 change，且不得在开始其他 cleanup前长期搁置。

### OR-C03 - Converge owner-drifted capabilities through owner-local changes

- **证据**: NC/RS/FM findings与 current specs/registry/checker结果。
- **当前 owner**: mechanically valid但语义漂移的 capability names/requirements。
- **目标 owner**: Node Cognition、Bundle/Journal、fixture composition各自 current capability。
- **Disposition**: `migrate/rename/retire` per NC-C01/RS-C01..C03/FM-C01..C04。
- **迁移条件**: each change maps old requirements/IDs/consumers/evidence to one target owner。
- **删除条件**: old capability directory无 current behavior/consumer；retired IDs保留占位且 never reused。
- **保留负向护栏**: checker/coverage不缩 scope；anti-resurrection requirements归 target owner。
- **OpenSpec change slice**: 不建 spec-cleanup mega-change；follow [80 - Remediation Change Map](../03-execution/80-remediation-change-map.md) owner slices。

### OR-C04 - Correct the structural registry in both directions

- **证据**: empty `tests/e2e` positive entry；workflows/skills absent from required tracked inventory；broad ignored path。
- **当前 owner**: project-structure registry/checker。
- **目标 owner**: exact current delivery artifacts only；local-only directories remain explicitly excluded。
- **Disposition**: `migrate`。
- **迁移条件**: OR-C01/C02 delivery decision；TA-C02 empty scaffold approval；add trackedness sensitivity test。
- **删除条件**: `tests/e2e` entry removed with directory；no promised delivery artifact can be replaced by ignored copy。
- **保留负向护栏**: gitlink/import/node package/generated locator rules unchanged；exception baseline shrink-only。
- **OpenSpec change slice**: OR-C01 structure delta first；TA-C02 later `subtract-empty-test-scaffolding`。

### OR-C05 - Restore product CONTEXT to glossary-only scope without rewriting ADR history

- **证据**: duplicated tail statements map to ADR 0022-0026/specs；dormant term maps to ADR 0002/0008；ADR statuses clear。
- **当前 owner**: glossary plus duplicated design records。
- **目标 owner**: glossary owns definitions only；ADR/spec own decisions/requirements。
- **Disposition**: `migrate then delete duplicated/dormant glossary content`; ADR `historical keep`。
- **迁移条件**: per-paragraph owner/link check；canonical term table；current docs retain necessary navigation。
- **删除条件**: no unique domain definition lost；glossary contains no design/status ledger；ADRs unchanged except routing if needed。
- **保留负向护栏**: canonical evaluation distinctions remain；superseded/dormant status discoverable；no fourth term registry。
- **OpenSpec change slice**: `restore-product-glossary-ownership`，结合 NC-C03/EC-C02/EV-C01。

### OR-C06 - Keep current indexes and historical evidence; delete only the grounded DPT duplicate

- **证据**: docs routes；TA-C05..C07 evidence comparison。
- **当前 owner**: current navigation + frozen evidence epochs + regression policy；DPT report is superseded duplicate。
- **目标 owner**: unchanged current index/evidence owners after DPT subtraction。
- **Disposition**: indexes/baseline/attestation/policy `keep/historical`; DPT `migrate then delete`。
- **迁移条件**: compare unique DPT provenance before deletion；do not copy verdict prose。
- **删除条件**: TA-C05 exact closure; no broken current links/tests。
- **保留负向护栏**: dated evidence never proves freshness；attestation immutable；regression descent remains current。
- **OpenSpec change slice**: `retire-superseded-dpt-report`。

### OR-C07 - Retain generated projections and their freshness guards

- **证据**: topology/prompt generators、exact comparison tests、architecture locator renderer。
- **当前 owner**: graph/prompt/structure source + generators。
- **目标 owner**: 不变。
- **Disposition**: `retain guard/projection`。
- **迁移条件**: no standalone cleanup。
- **删除条件**: only with replacement review route and equal stale/unsafe-path detection。
- **保留负向护栏**: generated content cannot drive runtime；stale/extra/missing output fails；paths remain contained。
- **OpenSpec change slice**: none; mandatory verification for owning graph/structure changes。

### OR-C08 - Preserve archive and completed-backlog history as evidence-only

- **证据**: checker exclusions/anti-substitution tests；current historical references。
- **当前 owner**: source-control history and archive/backlog lifecycle。
- **目标 owner**: 不变。
- **Disposition**: `historical`。
- **迁移条件**: none; current links may be repaired without rewriting facts。
- **删除条件**: outside this plan; requires explicit retention policy and inbound evidence migration。
- **保留负向护栏**: archive never pending authority；historical old terms excluded from residual current drift scan。
- **OpenSpec change slice**: none。
