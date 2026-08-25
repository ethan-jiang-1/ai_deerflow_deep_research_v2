# Tasks: split-project-structure-manifest

## 1. 清单生成与等价对拍

- [x] 1.1 写等价对拍脚本（stdlib、一次性，放 `openspec/governance/` 临时路径）：从当前扁平 `[[required_paths]]` 导出 (path, kind, owner) 全集；从 `required-paths.toml` 的 `[paths.<ID>]` 段展开同一集合，断言两者完全一致。对新清单缺失运行必红。验证：`python3 <脚本>` 对新清单缺失报红
- [x] 1.2 用 1.1 从当前扁平清单机械生成 `openspec/governance/required-paths.toml`（`[paths.<PRS-ID>]` 分组、段内路径字典序、`files`/`directories` 分列）。验证：1.1 对拍零差异

## 2. Checker 与清单切换（原子步骤，fixture 先行）

- [x] 2.1 red-green 先写新格式的确定性负例（`openspec/tests/governance/` 或既有架构夹具）：缺 `[inventory]` 表 / inventory path 不匹配常量 / 段键非法（非 `^[A-Z]{3}-\d{3}$`）/ owner 未知 / `required-paths.toml` 未登记为 required file / 删除已登记文件 → 各自非零并点名规则（对新 checker 红）。验证：`python3 -m unittest discover -s openspec/tests/governance`
- [x] 2.2 改造 `openspec/governance/check_project_architecture.py`：新增 `INVENTORY_RELATIVE = PurePosixPath("openspec/governance/required-paths.toml")`；`load_manifest` 解析契约文件后校验 `[inventory]` 表（`path == INVENTORY_RELATIVE`、`schema_version == 1`、`contract == "project-structure-inventory"`）；解析清单文件，按文件内段序 + 段内 files-then-directories 展开为 `list[RequiredPath]`；复用既有全部校验（`_relative_path` 规范化/禁 `..`/禁绝对路径、路径去重、kind ∈ {file,directory}、owner ∈ requirement_ids ∧ registered、禁 upstream root、非空、`ignored_paths.path` 已登记）。验证：2.1 全绿 + 最小「契约+清单」fixture 全量校验绿
- [x] 2.3 与 2.2 同一提交切换真实清单：从 `openspec/governance/project-structure.toml` 移除全部 `[[required_paths]]`，新增 `[inventory]` 表；确认 `project-structure.toml` 与 `required-paths.toml` 均登记为 required file（owner PRS-004）。验证：`python3 openspec/governance/check_project_architecture.py` 对真实仓库绿

## 3. 瘦身验证与措辞同步

- [x] 3.1 验证瘦身效果与 AGENTS.md 生成块不变：契约文件 `project-structure.toml` ≤ ~80 行；清单文件 `required-paths.toml` ≤ ~400 行；`--render-guide` 输出与现有生成块逐字节一致（`_validate_guide` 绿）。验证：`wc -l` 两文件 + `check_project_architecture.py` 绿
- [x] 3.2 同步指向「单一 project-structure.toml 精确清单」的散文为「project-structure manifest = 契约文件 + 清单文件」：`openspec/governance/architecture-policy.md`（authority 表 + Synchronized Changes 第 2 步）、`openspec/config.yaml`（第 18 行）、`openspec/README.md`（第 17 行）、`openspec/change-guidance/README.md`（第 33 行）、`openspec/change-guidance/local/deep-research.md`（第 39 行）、`openspec/governance/README.md`（nav 表增补清单文件行）。验证：`grep -rn "project-structure.toml" openspec/ --include="*.md" --include="*.yaml"` 走查无过时断言
- [x] 3.3 测试夹具扫描：grep 全仓对 `project-structure.toml` 的拷贝/构造点，逐一核对是否需增补 `required-paths.toml`（当前 `openspec/tests/governance/test_project_gate.py` 用 fake runner、不构造 manifest，`deep_research_harness/tests/` 无 manifest 引用——预计无需改动；若有构造点则同步增补）。验证：`grep -rn "project-structure.toml" --include="*.py" .` 走查 + `python3 -m unittest discover -s openspec/tests/governance`

## 4. 验证与收尾

- [x] 4.1 六个 component checker 全绿：`check_project_architecture.py`、`check_project_reqs.py`、`check_project_specs.py`、`check_change_guidance.py`、`check_project_req_coverage.py`、`check_harness_dependency_direction.py`（repo 根逐条跑，退出码直测）。验证：每条 `echo $?` = 0
- [x] 4.2 聚合 gate 与 Harness 验证：`python3 openspec/governance/check_project_gate.py --phase closeout` 绿；`cd deep_research_harness && UV_OFFLINE=1 make verify` 独立绿（Harness 不读 OpenSpec）。验证：两命令退出码 = 0
- [x] 4.3 严格校验与 diff 卫生：`openspec validate split-project-structure-manifest --strict` 绿；`git diff HEAD --check` 无输出。验证：两命令退出码 = 0
- [x] 4.4 记录 scope/diff 证据：`git status --porcelain=v1 --untracked-files=all`、`git ls-files --stage deerflow`、`git submodule status -- deerflow`、`git -C deerflow status --porcelain=v1 --untracked-files=all`、`git diff --submodule=short` 存档于 change 的 evidence/；确认 `deerflow` 指针 hash 仍为 `66b9e7f2…`。验证：指针与 nested worktree 未变
