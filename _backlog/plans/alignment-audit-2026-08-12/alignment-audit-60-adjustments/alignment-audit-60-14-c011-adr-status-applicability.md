# C-011 - ADR Status And Applicability

> Stage: 2 - `retire-stale-context-concepts`
> 类型: historical status
> 状态: **REVIEW REQUIRED**

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

- [ ] 调整内容准确
- [ ] 风险与副作用已充分披露
- [ ] 批准进入 Stage 2 planning
- [ ] 需要修改或补充，原因：
