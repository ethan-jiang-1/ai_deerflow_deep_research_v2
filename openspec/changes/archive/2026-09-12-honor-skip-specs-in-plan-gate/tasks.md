# Tasks: honor-skip-specs-in-plan-gate

## 1. 红测护栏（先红后绿）

- [x] 1.1 `openspec/tests/governance/test_project_gate.py` 新增 4 个 selected-change 用例：
      `skip_specs: true` 零 delta 通过；`skip_specs: false`、`skip_specs: yes`、
      缺 schema 均 fail closed。先在未改 checker 前确认 marked-pass 用例红
- [x] 1.2 保留既有 `test_empty_change_without_specs_dir_fails_closed` 与
      `test_empty_change_with_empty_specs_dir_fails_closed`（无标记仍 fail closed）

## 2. checker 修正

- [x] 2.1 `check_project_specs.py` 新增 `_skip_specs_marker(change_dir)`：只解析扁平
      顶层标量元数据；`schema` 必须是已知 schema，`skip_specs` 必须是布尔 `true`；
      缺键 = 未标记，重复键/嵌套/非布尔 = 不可信，均返回结构化原因
- [x] 2.2 `validate_selected_change_delta_specs` 零 delta 分支：honored → 通过；
      invalid → `selectedChangeSkipSpecsInvalid` fail closed；无标记 →
      `selectedChangeEmpty` fail closed；有 delta 的 change 行为不变
- [x] 2.3 `main()` 增加新 check 的标签；模块 docstring 说明 zero-delta opt-out 语义

## 3. 验证与收口

- [x] 3.1 `python3 -m unittest discover -s openspec/tests/governance` 全绿
- [x] 3.2 `--phase plan --change 2026-09-12-rename-work-unit-storage-probe` exit 0
- [x] 3.3 `--phase plan --change 2026-09-12-repair-debug-requirement-evidence` exit 0
- [x] 3.4 `python3 openspec/governance/check_project_gate.py --phase closeout` exit 0（修改后复跑）
- [ ] 3.5 按 openspec-archive-change 流程归档本 change
