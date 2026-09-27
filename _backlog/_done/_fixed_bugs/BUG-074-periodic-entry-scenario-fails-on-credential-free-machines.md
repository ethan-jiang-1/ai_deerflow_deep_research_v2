# BUG-074: periodic 入口环境场景在无凭据机器上必然失败(含 CI)

> 严重级别: P2 | 发现: 2026-09-28(CI 首次真实运行) | 状态: 已修复(2026-09-28,change `fix-periodic-launcher-credential-bounded`)

## 症状

`tests/scenarios_periodic/test_local_entry_environment.py::test_prepared_entries_preserve_dependency_state_and_keep_launcher_credential_bounded`
在 GitHub Actions(CI run 36354296668)与本机(2026-09-28 实测,236s 超时/断言失败)都失败。
`agent-entry-environment-regression.yml` 工作流的**全部历史运行均为失败**——此测试在无凭据环境从未通过。

CI 失败形态:launcher(`run/real-research.sh`)输出 `尚未找到可用的模型配置`,而测试断言
`本地前提检查已就绪`;本机形态:入口子进程超时。

## 根因(2026-09-28 分析)

测试自相矛盾:

1. `_child_environment` 从子进程环境里**清除全部凭据变量**
   (`CHILD_SECRET_KEYS = DEEPSEEK/ANTHROPIC/OPENAI/TAVILY_API_KEY`)——"credential bounded" 的本意;
2. launcher 阶段还写入**空的测试自有 .env**,明确阻断开发者凭据文件;
3. 但断言要求 readiness 的 `本地前提检查已就绪`——而 `_demo_core.resolve_real_demo_model_profile`
   要求环境里**同时**有模型选择器变量与非空凭据变量才判"模型就绪"。

三者不可能同时成立:凭据被 1 与 2 双重清除后,模型就绪永假,断言必然失败。
该测试只能在其编写时的某种旧 readiness 语义(或未清凭据的旧帮手)下通过。

## 影响

- `agent-entry-environment-regression.yml`(每日 + 手动)自创建以来全红;
- EVH-005 声明 periodic lane "credential-free",此测试违反其所在 lane 的自身要求。

## 修复(2026-09-28)

采用方案 B(诚实断言 not-ready 旅程)。方案 A(注入假凭据)被实测否决:假钥匙让就绪通过后,
`--embedded-smoke --scripted` 的自动建档自动确认、topic_planning 真打了 api.deepseek.com
(HTTP 401, provider.authentication_failed)——"就绪→blocked"旅程无法离线展开,属有凭据的手动 lane。
方案 B 断言:就绪诚实不就绪(尚未找到可用的模型配置 + 下一步指引)、就绪摘要不存在、
非零退出、凭据变量名不泄漏。本地边界如实记录(change 的 evidence/local-environment-note.md:
DSH 沙箱下重路径非确定性挂起,7 轮探针 4 个挂点);验收 = CI——**entry-environment workflow
于 2026-09-28 取得史上首个绿灯**(此前全部历史运行均失败)。

## 原始修复方向记录(已被上述实测取代)

- 方案 A:测试为 launcher 阶段**显式注入有界假凭据**(与测试名 keep_launcher_credential_bounded
  的本意一致:注入假值,断言就绪 + research.blocked + 凭据名不泄漏);
- 方案 B:断言改为"凭据缺失时 readiness 诚实不就绪 + blocked",匹配现行语义;
- 两案都须先核对 `real-research.sh` 在 ready 与 blocked 两个分支的真实输出契约,并加红测。

## 备注

发现于 2026-09-28 的扫尾审计推送:CI 首次真实运行暴露两层历史死因(子模块未检出——已修
2c1231b;此测试——本卡)。同批落地的 duration waiver 与防锈见
`scripts/checks/check_test_durations.py` 与 DONE-009 的停靠项记录。
