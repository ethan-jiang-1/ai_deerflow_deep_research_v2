# Design: doc-gate-docs-layer

## Context

`check_doc_hygiene.py`（PRS-020）已有三条规则：ADR index ↔ 目录、entry-chain 相对链接、
UTF-8/尾换行；范围常量 `ENTRY_DOCS` 刻意只含 6 个入口文件（preceding change 的
design Decision 5）。`deep_research_harness/docs/` 的 37 个 markdown 不在扫描内。该盲区
被 `54886b8` 击中：删 OpenSpec 链接时留下悬空 prose 片段，gate 照绿，人工评审才捞出。
2026-08-31 对全部 37 个文件实测三条规则：全绿——扩围是零破坏收紧。

## Goals / Non-Goals

**Goals:**

- 把**既有**相对链接规则与 UTF-8/尾换行规则应用到 docs 层（`docs/*.md` + `docs/adr/*.md`），
  `--self-test` 负例控制同步覆盖新范围。
- 保持 PRS-020 全部既有边界承诺不变：自包含、非六 component 聚合、不接 `make verify`。

**Non-Goals:**

- 不做悬空 prose 片段检测——语义判断不可机械化，宁缺毋假。
- 不动 ADR index 规则的语义（仍只校验 `docs/adr` 索引↔目录一致性）。
- 不做 line budget（`check_change_guidance.py` 已拥有）。
- 不新增文件、不新增结构路径、不改 `project-structure.toml`、不动 `architecture-policy.md`。
- 不接 `make verify`、不改 `check_project_gate.py`、不动 `deerflow/`。

## Decisions

1. **MODIFIED PRS-020，不新增 requirement。** 扩围改变的是同一 checker 的规则范围，
   owner 与登记路径都不变；新增 PRS-022 会制造两个 requirement 共有一份 checker 的归属
   模糊。*Alternative（新增 PRS-022「docs 层覆盖」）rejected：同 owner 同文件拆两个
   requirement 只增加登记簿噪音。*
2. **扫描范围用显式枚举常量，glob 只做完整性守卫。** 沿用 `ENTRY_DOCS` 的先例：新增
   `DOC_LAYER_DOCS`（`docs/*.md` 顶层 + `docs/adr/*.md`），由脚本内构造；扫描走常量，
   review diff 一眼可核。枚举的已知弱点是「新增文件忘登记 → 静默欠覆盖」，故补一条
   **范围完整性守卫**：glob `docs/**/*.md` 全集与常量求差，多出的未登记文档即退出
   非零并点名——漂移从静默变成响亮失败，与本仓 fail-closed 哲学一致，delta spec 的
   「unregistered docs-layer markdown is rejected」scenario 即它的契约。
   *Alternative（`docs/**/*.md` 运行时 glob 直接作扫描源）rejected：扫描面随工作树
   静默变化，且排除规则（非 markdown、未来可能的新子目录）会散落成隐式逻辑。*
3. **规则复用，不复制实现。** docs 层文档走与 entry-chain 相同的链接解析与
   UTF-8/换行检查函数；新增的只是「范围 → 规则」的映射（docs 层不适用 ADR index 规则）。
   *Alternative（为 docs 层复制一套检查函数）rejected：两份实现必然漂移。*
4. **`--self-test` 扩展而非重建。** 在既有干净 fixture / 植根违规模式上，为 docs 层范围
   补三个植根违规（坏链接、非 UTF-8、缺尾换行）并断言各自非零；原 entry-chain fixtures
   原样保留。真实树走查（植入 → 红 → 还原）作为 apply 期的第二重负例证据。
5. **registry 描述行同步放 apply。** `req-registry.yaml` 的 PRS-020 描述行还写着
   「broken entry-chain relative links」；扩围后由 apply 任务改为覆盖两个范围的措辞
   （planning 不动 registry，沿 CLS-056 以来「apply 正式登记」的惯例）。

## Risks / Trade-offs

- **[误伤生成文件]** `docs/deep-research-topology.md` 是生成物。→ 实测已绿；且它由
  `render_topology.py` 生成 markdown，编码/链接规则与生成器兼容；若未来生成器产出坏
  链接，gate 红是对的（生成器该修）。
- **[范围枚举漂移]** docs 树新增文件而常量未更新时，旧设计会静默欠覆盖。→ 范围完整性
  守卫把这种状态变成非零退出并点名文件；「范围即代码」降级为 review 习惯，不再承担
  正确性义务。
- **[self-test fixture 膨胀]** → 每规则一个最小 fixture，沿用既有模式，不引入 fixture 框架。
- **[与 change-guidance 的边界]** line budget 仍归 `check_change_guidance.py`；本 change
  不重复其义务。
