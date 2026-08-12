# C-011 - ADR Status And Applicability

> Stage: 2 - `retire-stale-context-concepts`
> 类型: historical status
> 状态: **REVIEWED - PLANNING ONLY**

## 调整内容到底是什么

为 ADR 0002、0003、0006、0008、0010 增加一致的 status 和 current applicability note，
区分历史决定、当前仍适用原则、planned capability 与 dormant surface。

## 主要风险

事后元数据可能被理解为篡改历史，或让 ADR status 越权定义 runtime；粗暴整篇标废弃也会
伤及仍有效的子决定。

## 可能副作用

工具或读者可能不认识新增状态；一个 ADR 可能同时含 dormant surface 与 current
principle，需要更细的 applicability 描述。

## 控制与停止条件

- 先采用最小统一 schema。
- 正文保持历史原样，每个 applicability claim 链接 current owner。
- 与 A-004 相交部分继续 quarantine；若 status 必须改写行为本身，停止。

## 审阅结论

- [x] 调整内容准确：2026-08-12，只为 ADR 0002、0003、0006、0008、0010 添加统一的
  后记型 status/applicability note；标题和历史正文逐字保留。0002/0003/0006/0010 按子决定
  区分 current、dormant、planned 或 non-current；0008 的 dedicated-TUI Local-First 路线
  为 `dormant`，但现有 Bundle lifecycle/isolation 不受影响。
- [x] 风险与副作用已充分披露：不使用全局 obsolete 标签，不让注记越权定义 runtime；每个
  applicability claim 都链接现行 owner，Support Handoff 的 Bundle-loss retention 保持 A-004
  quarantine。
- [x] 批准进入 Stage 2 planning（不包含创建 OpenSpec change 或 apply 授权）
- [ ] 需要修改或补充，原因：
