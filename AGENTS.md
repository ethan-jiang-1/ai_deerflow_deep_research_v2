# AGENTS.md

本仓库 = **跑在 DeerFlow 之上的 deep research 应用**。它由两层组成，顺序很重要：

```
deep_research_harness/    ★ 你的应用（本仓库的主角，几乎所有工作发生在这里）
deerflow/                 被 leverage 的外部框架（submodule 锁 commit `ceebf97f`，ethan 分支，= 上游 v2.1.0），只用来跑，绝不修改
```

## 你的工作范围（按优先级）

| 目录 | 是什么 | 怎么对待 |
|------|--------|---------|
| `deep_research_harness/` | **你的 deep research runtime 应用**（src/deerflow_deep_research，graph/runtime/agents/engine/domain） | ★ 主角。改代码、写测试、跑它 |
| `openspec/` | 设计规格（specs / changes / governance） | 改设计时在这里写 spec，用 `openspec` CLI |
| `_backlog/` | 任务账本（bugs / plans / todos） | 任务追踪 |

## 框架：只 leverage，不修改

**`deerflow/` 是一个 git submodule（锁在 commit `ceebf97f`，ethan 分支的一个 commit，框架代码等同于上游 v2.1.0 发行版），提供运行环境。** 对它：

- ✅ **用它的 API**——你的应用通过 `import deerflow`（editable 装自 `deerflow/backend/packages/harness`）继承框架能力，有什么用什么。
- ❌ **不要探索 / 修改它的源码**。它是上游镜像，不是你的代码。
- ❌ **不要为了解决问题去翻它内部**——如果某任务要求你读框架源码才能继续，停下来重新界定范围（大概率是你在尝试不该改的东西）。
- 需要理解它内部怎么工作 → 看 `deerflow/AGENTS.md` 与 `deerflow/backend/AGENTS.md`（框架自带的只读指引）。fork 分支携带 `_digest/`、`_faq_on_digested/` 旧研究笔记：只读历史背景，不作为当前理解来源，不要据此推断框架现状。

> 术语提示：本仓库的 `harness` 默认指 `deep_research_harness/`（你的应用）；`deerflow/backend/packages/harness` 是框架包。两者同名——前者是主角，后者是只读背景板。

## 运行方式

```bash
cd deep_research_harness
uv sync                              # 或 python -m venv .venv && pip install -e .
.venv/bin/pip install -e ../deerflow/backend/packages/harness   # editable 装框架
.venv/bin/python -m pytest tests/    # 跑你的测试
```

详细命令见 `deep_research_harness/Makefile` 与 `deep_research_harness/README.md`。

## 可用技能（Coding Agent）

共享的 grillme 技能集（grilling / tdd / code-review / domain-modeling 等）由全局安装提供（`~/.claude/skills/` 与 `~/.agents/skills/`，symlink 到 grillme-skills checkout），本仓库不保存副本。适合本仓的：`grilling`（质疑方案）、`tdd`、`code-review`、`domain-modeling`、`codebase-design`。项目自有的 openspec 技能在 `.agents/skills/`（Codex 通用入口，见 `.openspec-target`）。

## 研发宪章（Development Charter）

三条原则，适用于所有在本仓工作的 coding agent。

### 1) 流程：OpenSpec 是主干，成熟借力是养分

- **契约面 / 行为面变更走 OpenSpec 主干**：`openspec new change` → proposal（含
  Change Focus 卡）→ design / tasks → apply（**红绿测试先行**）→
  `check_project_gate.py --phase plan|closeout` → archive。规范拥有契约；实现追平规范；
  **规范语义的变更需要人拍板**。
- **小改、文档、账本**可走直接提交（本仓有先例），但 ritual 不打折：账本搬迁按
  [`_backlog/README.md`](_backlog/README.md) 的步骤走全（文件、索引、计数三处一致）。
- **所借技术（DeerFlow 等）的成熟工程思想是养分**：读框架自带的只读指引
  `deerflow/AGENTS.md` 与 `deerflow/backend/AGENTS.md`，能借就借；借不够就明说
  "目前借不够"，然后自己探索，而不是把不确定转嫁给用户。
- **刻意接受的分歧就地写明**：一个看似 bug 的行为若决定不修，必须在原位留下
  "有意如此、别再重提"的理由 + 一条锁定它的测试；否则它会被反复重提或悄悄漂移。

### 2) 自主解决：先建回路，再谈结论

- 遇到"坏了 / 不对"：先造**可复现、可红可绿、快**的反馈回路（失败测试 / 差分复现 /
  headless harness），拿到红→绿证据再下结论；**禁止先猜后改**。
- 把"我不知道"变成"我测出来"：能自证的绝不外推；能查规格、文档、账本历史的先查。
- **交付前自证检查单（缺一不许交回，退出码直测、不用管道吞掉）**：
  1) `UV_OFFLINE=1 make verify` = 0；
  2) 交互式 TUI 路径 `make tui-journey` = 0（含**真实停留断言**：≥1.3s 后操作者面板
     仍显示预期状态；与**布局可见性**：常见终端尺寸下面板不越界、composer 可用）；
  3) 治理门 `check_project_gate.py --phase closeout` = 0 且 `check_doc_hygiene.py` 通过；
  4) 自问一句 **"操作者在真实终端尺寸与真实时间流逝下看到的，就是我断言的那个吗？"**
     ——凡只断言内部状态、而不断言可见结果的，**视为未验证**；凡断言快于 UI 自身
     定时器的（例如 1 秒刷新），**视为未验证**；
  5) 环境现场独立性：结论不得依赖某台机器的工作区历史（残留 bundle、缓存、临时目录）。
- **委派是优化，不是复杂度的默认反应**：只有当并行省时、专精、上下文隔离三者之一
  明确超过协调成本时才派 subagent；**输出互相依赖或共享可变状态时硬禁并行**；
  用最少的够用数量，每批重新评估。
- **委派的产出按契约回报**：行动声明附工具回执，交付物给可验证句柄（绝对路径 /
  URL / id / 退出码），失败照实说，验收条件在交接时用代码核过；**无法证明的降级为
  UNVERIFIED，绝不含糊通过**。

### 3) REVIEW 节制：自己能做的 review 自己做

默认**自主 review**：用 `code-review` 技能跑 Standards + Spec 两轴（必要时用
`grilling` 自问），自证通过后直接交付。**只有下列情形才请人介入**：

- 产品方向 / 优先级 / 范围取舍（做什么、先做哪个、值不值得做）；
- 用户保留区：`.agents/skills/`、`.env` 与密钥、gitignored 本地便利件；
- 不可逆或越界：改写历史、push / 发布、删除他人数据、改 `deerflow/`；
- 规范语义的裁决性变更（规范该不该这样写）；
- 用户明确要求 review。

其余（代码质量、命名、测试充分性、文档一致性、bug 定位与修复）→ **自主 review +
自证，直接给结果**，不要求人 review。

## 边界铁律

1. **应用是主角**——所有产出都该服务于 `deep_research_harness/` 的构建。
2. **框架是背景板**——`deerflow/` 只被 import，从不被改。
3. **根目录刻意很小**——如果发现自己在框架内部打转，说明范围错了。
