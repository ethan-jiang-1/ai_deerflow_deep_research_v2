# 迁移与验证

## 迁移顺序

1. 抽取纯 `change_guidance_kernel.py`，保留本地 wrapper CLI；
2. 建立 paragraph/rule ownership ledger；
3. 原子切换 core、三个 profiles 和 local composition；
4. 迁移完整 node-agent authoring gate；
5. 将产品前门切换到 `product/README.md`；
6. 移走 Harness 中的 OpenSpec governance tests 和引用；
7. 删除旧 policy/product/closeout 路径；
8. 生成 portable snapshot manifest 和 digests；
9. 完成 closeout review 并 archive 同一个 Change。

## 必须保持

- Deep Research proposal grammar、requirement IDs 和 checker CLI；
- Harness runtime、prompts 和应用行为；
- `deep_research_harness/CONTEXT.md` 的 glossary authority；
- `project-structure.toml` 的精确结构 authority；
- `deerflow/` 只读、public-API-only 边界。

## 负向证明

| 边界 | Planted negative |
| --- | --- |
| Portable neutrality | 加入产品名、本地路径或 source requirement ID |
| Pure validator | 尝试读取 filesystem、执行 command 或 import wrapper |
| Profile composition | 启用缺失 profile、选择 disabled policy、漏掉并行 review |
| Node authoring gate | 删除、降级或错序七项语义，或为 non-model work 伪造 prompt |
| Product front door | 保留旧链接、增加额外 member、遗漏 owner route、超 budget |
| Dependency direction | Harness 文档、Makefile、test 或 asset 引用 `openspec/` |
| Single owner | 留下旧 policy tree、重复正文或 compatibility copy |
| Snapshot | 加入 denylisted path、broken link 或篡改任一 digest |

## 最终验证

```bash
python3 openspec/governance/check_harness_dependency_direction.py
python3 openspec/governance/check_change_guidance.py
python3 openspec/governance/check_project_reqs.py
python3 openspec/governance/check_project_specs.py
python3 openspec/governance/check_project_architecture.py
python3 openspec/governance/check_project_req_coverage.py
openspec validate make-openspec-practice-portable --strict
python3 openspec/governance/portable_change_guidance_export.py \
  openspec/changes/make-openspec-practice-portable/evidence/portability-candidate.json
cd deep_research_harness && UV_OFFLINE=1 make verify
git diff --check
```

完成标准：上述验证通过、旧入口已删除、每类内容只有一个 owner、Harness 不依赖 OpenSpec、portable
snapshot 只含 allowlist 文件。无需另一个仓库或另一个 Change。
