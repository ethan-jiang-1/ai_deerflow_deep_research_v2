# TODO: entry-doc prose + agent search guidance

> 状态: 已完成 | 优先级: 低 | 更新: 2026-09-12
> 上游: 无 | 下游: 无

## Why

一次面向 coding agent 的入口可读性体检发现两处低风险 prose 缺口。按 `_backlog`
纪律「修 prose 走账本、只有新的可机器执行结构才开 change」
（见 [`doc-gate-docs-layer-and-fresh-agent-narrative.md`](../_closed_plans/doc-gate-docs-layer-and-fresh-agent-narrative.md)），
直接修复并在此记录，不开 OpenSpec change。

## 现状对齐

- `deep_research_harness/docs/README.md` 结尾句有重复 `the`，且同一句把
  `../AGENTS.md` 链接写了两次。`check_doc_hygiene.py` 的链接/编码规则对这类
  **语义/措辞**漂移照绿——这是仓库刻意的非机械化边界，不是门禁漏洞。
- `deep_research_harness/AGENTS.md` Boundaries 未提示：`.deep-research-demo-runs/`
  （1986 文件）、`.reports/`（297 文件）、`.venv/`（935M）等生成树虽已在
  `.gitignore`，但裸 `find` / `grep -r` 会下钻（`grep -rl` 命中 5298 文件 vs
  `rg` 494）；专用 glob/grep 工具默认遵守 `.gitignore`，不受影响。

## 落地

- [x] `docs/README.md`：重复 `the` 与重复链接改为单句 path-free 措辞。
- [x] `AGENTS.md` Boundaries：加一行探索指引（用 `rg`，避免 `find`/`grep -r`）。
- [x] `python3 openspec/governance/check_doc_hygiene.py` 与 `--self-test` 均通过。

## Non-Goals

- 不扩 `check_doc_hygiene.py` 的 `ENTRY_DOCS` 范围把根 `README.md`/`CONTEXT*.md` 纳入：
  语义/措辞不可机械化，扩范围属「新建可机器结构」需单独 change，且不服务任何已观察到的漂移。
- 不新增 doubled-word / dangling-prose 检查器（同上，会造永绿假门禁）。
- 不改 `.gitignore`（生成树已正确忽略）。

## Next Step

无。同类文档措辞漂移仍靠 review 纪律，仓库已自觉取舍。
