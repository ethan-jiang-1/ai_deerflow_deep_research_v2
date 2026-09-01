# Handoff: Mode 020 TUI 真人交互战役（= 原 010 手动 TUI）+ change `fix-demo-tui-choice-option`

> 生成: 2026-08-21 | 用途: 战役进行中新会话 pick up 后继续（Stage A/B1 跑次 / 茬处置 / 收口）
> 位置: 本文件在 `_backlog/_local_demo/`；设计文档在 `_backlog/plans/_archive/tui-interactive-campaign-digested.md`（v5，已消化）；
> 进度追踪在 `_backlog/plans/_archive/tui-interactive-campaign-progress-digested.md`；实施载体已归档 `openspec/changes/archive/2026-08-21-fix-demo-tui-choice-option/`
>
> **状态: 🟡 进行中**。已完成：Stage 0 校准（review 全消化）→ Stage A fixture
> smoke（6 bundle 全 completed）→ 两个 change 闭环（`fix-demo-tui-choice-option`
> 修 BUG-060、`add-demo-tui-auto-entry` 修 BUG-061，均已归档）。
> 待办：**Stage B1（你操作 embedded 真跑，战役主体，环境已就绪）**
> →（条件 B2 / 可选 C）→ 收口。

## 目标（一句话）

**在 TUI 里以真人 HITL1 交互跑通一次真实 Deep Research（真实 DeepSeek + 真实
Tavily），并找茬交互认知面**：固定 003 短问题 + 条件式修订应答（初始 depth 是
X 就改 Y）→ 四步证据链（初始 proposal / 修订语句 / 修订后 proposal / 显式确认）
→ exact bundle `terminal_status=completed` + `degraded_profile=false` + 真实
report。HITL2 是自主 continuation **不需要人**。PASS 判据 7 条见 runbook §3.4。

## 实施摘要（已完成部分，均有 commit/归档证据）

- **Stage 0 校准（2026-08-21，commit 前史）**：独立 review 九项事实主张全部
  代码核验成立并消化——plan v4 重写（hitl2 自主性 / CHOICE 拆 B2 / 条件式修订
  证据链 / exact bundle 绑定 / Journal 归因限制 / preflight 三要素）；runbook-010
  与 `RUN-020.command` 重写（合法应答卡 + 启动前后 bundle 目录集合 diff）；
  阶梯表 010 行修正。
- **BUG-060 修复（2026-08-21，commit `cd053d6`）**：change
  `fix-demo-tui-choice-option` 全流程（propose → polish 三 pass → apply TDD →
  归档）。要点：
  - `demo_tui.py`：选项按钮组（`SupportedLanguageOption` 闭集静态生成、按当前
    hitl1 CHOICE 广告切可见性）；按钮点击与 composer **exact-match**（精确等于
    广告 id 如 `zh`）都派发 typed OPTION
    `AnswerRun(value=option_id, response_kind="option", option_id=option_id)`；
    非匹配文本不派发；TEXT 轮与 hitl2 CHOICE 文本转发不变（受保护行为）。
  - 回归：集成 4 用例 + contract 回放 2 用例（派发 seam：typed OPTION → resume；
    text → `input.invalid_response` Fault）。verify 全绿（fast 2641 +
    integration 261 + workflow 35）。
  - RED-009 进主 spec；BUG-060 → `_done/_fixed_bugs/`。
  - **apply 中固化的事实**（后续跑次注意）：hitl2 CHOICE 轮自由文本转发是
    graph 侧校验的既有契约；hitl1 CHOICE 轮的 text 拒绝投影为闭合 Fault
    （`input.invalid_response`），不是 raise。

## 战役跑次战况（append-only，跑了就填）

| 尝试 | 阶段 | bundle / 证据 | 结果 | 判定 |
| --- | --- | --- | --- | --- |
| Stage A（2026-08-21 15:40-16:17，`RUN-020.command` 选 1） | A | fixture scope `s_At5E33X…` 6 个 bundle（15:40/15:55×2/15:59×2/16:17） | 全部 `terminal_status: completed`、`implementation_mode: fixture`；每次 hitl1 完整往返（4 事件）；图走完 final_delivery | ✅ PASS（交互面/启动/退出均正常；Cancel 分支未跑，可选项） |
| Stage B1 第 1 跑（2026-08-30 13:19-13:59，agent 侧全程监控） | B1 | real bundle `b_l_W3Z6jthJlZwk0G9ANJMOzQr-acZEW26q1aHn9teZ4`（exact 绑定：本窗口新增之一，按时间戳区分） | hitl1 交互完整（两轮往返，最终 depth=quick_overview / en / 未降级）→ planning+wave0+wave1 全过、证据 2 条入库（4.4KB submissions）→ **wave2_synthesis 唯一模型调用挂 16m22s 被 `bridge_wall_time` 掐死（provider.timeout），零重试** → readiness `synthesis_findings_unavailable` 终局 blocked | ❌ blocked → **BUG-062**（P1）；hitl2 自主经过✅；四步链三值待用户回报 |
| Stage B1 第 2 跑（2026-08-30 14:10-14:23，**已死**） | B1 | real bundle `b_yFAvXIr8zct6c8sraXXuDcIUhjhtpmA6M-tOJ-0jCeU` | 初始 proposal 即 depth=quick_overview；用户 14:14 输入被 TUI 判"与当前配置一致"（无字段变更）→ 14:18 confirm → topic_planning+wave0 过 → 14:23:45 wave1 model 调用中**网络断，TUI 进程树死亡**；bundle 遗弃为 suspended（journal complete 53 事件），无恢复入口，inspect 拒绝 | ❌ 孤儿 → **BUG-064**；四步链第 2 步存疑（无实际字段修订）+ 三值待用户回报 |
| 清理后 fixture smoke ×2（2026-08-30 16:21、21:51-22:10，scope `s_At5E33X7YKq…`） | — | 4 个 fixture bundle（16:21 ×2 / 22:10 ×2），全部 `terminal_status: completed`、`implementation_mode: fixture`、`final/` 空（预期形态）；日志 tui-97920/36275/36649/38298（各 80B 快跑） | 真实 B1 未跑——**基线因此失效，已重建 =7**（/tmp + .evidence 双份）；第 3 跑验收以 7 为准 | ✅ 无影响，仅基线刷新 |
| B1 第 3 跑 attempt（2026-08-31 02:51，同会话可重触发） | B1 | real bundle `b_Idursp09h6fsm7SZFf0mIyWw0lopw3Y2c-veKcbPnrI`（scope `s_iUfVh9oU…`，terminal=**blocked**） | **hitl1 第一跳（初始 brief/proposal 生成）DeepSeek API 无响应**：provider_sdk_timeout → C1 机制**自动重试 1 次**（Model invocations: 2）→ 仍无响应 → Recovery disposition: exhausted → **干净 handback 回 blocked**，TUI 回侦察模式并给出明确恢复指引 | ❌ blocked（provider 瞬时不可用，非产品缺陷，**不立新 bug**）；**C1 行为当场验证生效**（快失败+闭合诊断 diag_0517f78915cd2d2677e6d81d，对比 BUG-062 挂 16 分钟）；基线重建 **=8**（含本 bundle），重跑后唯一新增即验收对象 |
| B1 第 3 跑 attempt ×2 续挂 + 根因确诊（2026-08-31 02:56-02:57） | B1 | real bundle `b_YoW1-fzJKPEcXDySO5MH-NktSVSyaQc3vrQPQhrRWHg`、`b_kW8IWw9xy-bFWQ_Q_6Ze_vu2G70lHYTYbCTsRDzuCaM`（同 scope，均 terminal=**blocked**，同 hitl1 provider_sdk_timeout 形态） | 用户同会话再触发两次，**同因三连挂**。agent 侧 curl 直探：`https://api.deepseek.com` **TCP 连接超时**（裸连 HTTP 000 / connect 0s；带 key 25s 无响应）——**机器级网络不可达**，与 key/app/操作无关。C1 三次全部按设计快失败+闭合诊断 | ❌ 三连挂同因（网络不可达，等恢复）；**不立新 bug**；C1 连续 3 次实战验证（对比 BUG-062 时代挂 16 分钟）；处置=停手等网络恢复后再触发；基线重建 **=10** |

> Stage A 观察备注：①"没跑出什么"= 预期形态——fixture 图 `final/` 为空
> （不产 report.md），终态只有 "Research complete" + bundle 信息，真实内容
> 属 B1；②每次 run 的 hitl1 首个 attempt 记 `failed` 后 retry completed——
> 这是 journal 对 interrupt 挂起-恢复的记账形态，非故障；③launcher fixture
> 分支提示"不产出真实 run bundle"措辞偏严（fixture bundle 实际写入同一
> demo workspace 的 fixture scope，只是非真实模型 run），不影响绑定逻辑
> （exact-bundle 绑定仅用于 real 模式）。

## 你要做的事（Stage B1，现在）

双击仓库根 **`RUN-020.command`**（或 `bash RUN-020.command`）。启动器自带
应答提示卡 + exact-bundle 绑定（退出后自动打印 terminal/profile/report 开头）。

**操作四步（不需要抄任何数值——三值由 agent 从证据侧自取）**：

1. hitl1 出初始 proposal → 看初始 `depth`：不是 `quick_overview` → 点
   「深度: 快速概览」或输入 `depth: quick overview.`；已是 `quick_overview`
   → 点「深度: 深入」或输入 `depth: deep dive.`（**必然不同于初始值**）；
2. 修订确认行出现 → 点 **Start proposal** 显式确认；
3. hitl2 **别碰**（自主经过），等 Terminal；**只跑这一轮研究**，然后 q 退出
   （多跑一轮 = 多一个 bundle，exact-bundle 会报"证据未绑定"）；
4. 回来口头报一声"跑完了"（有卡顿/报错/怪文案，描述一句即可）。

**三值取证分工（2026-08-31 实测定盘）**：初始 depth + 修订句 =
`logs/tui-<pid>.log`（Phase 4 体验底线：proposal 卡片与交互回显全文落盘，
run 2 冻结日志 tui-78024 实测验证）；修订后 depth = `request/profile.json`
（权威）。`state.json` 的 `admitted_refinement` 为被 admission 的字段变更
佐证（无变更则为 null，如 run 2）。用户口头观察仅作旁证，不再是证据链要件。

## 撞茬处置

- 任何异常：保留现场描述 → 报我登记 `_backlog/bugs/`（下一号 **BUG-066**；
  BUG-062/063/064 均已修复归档 `_done/_fixed_bugs/`，当前无活跃 bug）；
- semantic intake 形状缺陷是预期高危（BUG-058/059 同类：真实模型 vs 确定性
  契约边界）——撞上算产出；
- 收尾纪律同 004：bug 修复走独立 change，战役记录折进 runbook 附录后本文件
  删除。

## 数据清理记录（2026-08-30，用户授权）

老数据 67 → **3 bundles**（基线快照已重建双份，=3）。**保留的证据**：

| 保留物 | 用途 |
| --- | --- |
| `s_WwIyPhgXRkVr6hD6Cvqi…/b_l_W3Z6…`（B1 第 1 跑） | BUG-062（wave2 timeout 零重试）+ BUG-063 证据 |
| `s_WwIyPhgXRkVr6hD6Cvqi…/b_yFAvXIr8…`（B1 第 2 跑） | BUG-064（孤儿 suspended 无恢复入口）证据 |
| `s_WSPqmaB…/b_IzhRp8…`（003 时代 completed all_real） | runbook §3.6 对照 + `verify_b1_pass.py` 可测 |
| `logs/tui-78024.log` | BUG-064 现场（14:23:45 冻结的屏幕记录） |

**第 3 跑的 exact-bundle 验收基线：2026-08-31 复核重建 =8**（清理基线 3 + 清理后
fixture smoke 4 + 第 3 跑 hitl1 blocked 1）——**重跑后唯一新增即本次 bundle**；
同一 TUI 会话除重跑外勿再多跑。
