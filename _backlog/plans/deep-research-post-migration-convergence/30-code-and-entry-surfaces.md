# 30 - Code And Entry Surfaces

> 角色: 生产实现、配置、脚本与入口的收敛顺序

## 原则

代码清理从 owning decision 向外推进，不从最大文件或最旧提交开始：

```text
domain meaning / invariant
  -> deterministic engine/admission
  -> cognitive program and agent request
  -> graph composition
  -> runtime/public binding
  -> scripts/config/docs projections
```

跨层变更仍只有一个 primary causal owner。相邻层是明确接口，不借 cleanup 建立 generic shared
helper 或第二个 controller。

## 生产面盘点

### Domain

重点审计：

- deprecated/compat enum 与 default；
- 已无 writer/reader 的 model；
- 一个事实由多个 state/observation/session 类型重复表达；
- 字段仍以旧概念命名但当前语义已改变；
- serialization 是否使 private-looking class 实际成为 persisted promise。

删除条件：所有 constructors、deserializers、reducers、projections 和 persisted fixtures 已处理，且
旧 payload 有明确 rejection/migration 行为。

### Engine

重点审计：

- 只服务退休 route/enum 的 validator/gate；
- duplicated validation 是否因迁移临时并存；
- fallback 是否仍有合法 trigger、bound、terminal disposition；
- negative guard 与 production branch 是否混在同一控制路径。

保留确定性 owner，删除被 target owner 完整取代的 peer controller。不要为了减少文件把独立权威
混进 shared utility。

### Agents / cognitive programs

重点审计：

- `phase agent` 文件、docstring、runtime policy 和 prompt identity；
- legacy capability binding/default；
- capability Markdown、prompt builder、feedback/repair 与 current Node Cognitive Control Contract 是否
  使用同一语言；
- 旧模型策略是否仍能被 runtime loader 选中；
- generated prompt catalog 是否仍包含 retired branch。

AI-facing policy rename 需用 prompt/structured-output/cognitive evaluation evidence，不属于无行为文案改名。

### Graph

重点审计：

- implementation map、recipe mode 与 current public composition；
- retired fake/full-fake route 是否仍可达；
- nodes/components 中只为历史 topology 存在的 adapter/wrapper；
- duplicated route/gate/terminal handling；
- node package public export 和 workflow/capability resource 是否一致。

fixture composition 是确定性证据能力，不因“非生产”自动删除。只删除不再证明 current graph contract
的 fixture branch。

### Runtime

重点审计：

- Bundle lifecycle 与 run observation 是否仍有 session/binding peer authority；
- compatibility readers/writers、provider/checkpoint fallback 和 external observation；
- public `deep_research` tool、Dedicated Agent provisioning、controller skill loading；
- diagnostic/projection 是否复制或推断 lifecycle facts；
- stale path/config handling 和 local profile migration。

运行时是 public/persisted/cross-boundary 风险最高区域。任何删除先完成第 20 章 cutover 记录。

## Entry surface 清单

计划初始至少覆盖：

| Surface | 当前角色假设 | 审计问题 |
| --- | --- | --- |
| reflected `deep_research` tool | current product integration | schema/action/closed result 是否仍含迁移字段或旧 next action |
| Dedicated Agent + public controller skill | current recommended user route | current terminology、tool loading、无第二 authority |
| real demo CLI / launcher | smoke/operator | 是否只暴露 current recipe，命令与配置是否重复 |
| fixture demo / fixture graph | deterministic contributor evidence | 是否仍证明 current composition，旧 `full_fake` 名称是否可退役 |
| standalone demo TUI | operator visualizer | current owner/consumer/CI 是否成立，不冒充 Primary User UI |
| session workbench / inspect commands | operator observation | 是否已完全转为 Bundle/Run Observation 语言，无 binding control |
| cognitive evaluation runner/review | evaluation domain | 与 product Run/Bundle 的命名和 storage boundary 是否清楚 |
| Docker/CI/profile/configure | deployment/automation | old path/config reader 是 migration contract 还是残留 |

## 死代码证据

删除一个 implementation slice 前至少完成：

1. static import/export/call scan；
2. entry/config/registry/serializer/reflection discovery scan；
3. owning spec 和 active delta search；
4. test/eval/fixture consumer scan；
5. public/persisted surface grading；
6. planted deletion or old-entry rejection test；
7. focused tests red-before-green；
8. structure registry 和 package/wheel boundary update。

静态无引用不足以证明动态 resource、reflection、config key 或 persisted enum 可删。

## 分片规则

- 优先选择一个可独立替换的完整 vertical slice；
- 一个 change 不同时清理多个无关术语 cluster；
- private rename 可随 owning behavior change 完成，不单独制造迁移期；
- 大文件只在退役 slice 暴露清楚 owner 时拆分；行数不是拆分理由；
- 每新增一层/类型/adapter 必须写明退休对象，或接受的净增长、owner 与 review trigger；
- 不创建长期 compatibility module、symlink、re-export 或 dual-write 来“安全”完成删除。

## 代码批次完成条件

- target route 是唯一 current writer/entry；
- deleted symbols/files 不在 package exports、reflection、config、registry、docs 或 tests 中残留；
- public/persisted old input 按批准策略 migrate/reject；
- current behavior tests 通过，old-path guard 能检测复活；
- production wheel 不包含 fixture/retired implementation；
- import direction、async blocking-I/O 和 DeerFlow gitlink boundaries 仍通过治理；
- change 记录净增加/删除及尚未退役的 compatibility surface。

