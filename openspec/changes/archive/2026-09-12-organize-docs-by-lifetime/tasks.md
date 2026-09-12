# Tasks: organize-docs-by-lifetime

## 1. 冻结证据隔离

- [x] 1.1 `git mv docs/live-evaluation-baseline-2026-07-17.md docs/evidence/`
- [x] 1.2 `git mv docs/release-attestation-2026-07-17.json docs/evidence/`
- [x] 1.3 明确**不**移动 `regression-descent.md`（活策略/台账），在 README 归入 Living

## 2. 索引与链接

- [x] 2.1 重写 `docs/README.md`：Living References / Generated / Frozen Evidence 三块，
      补上缺失的 `run-lifecycle-walkthrough.md`
- [x] 2.2 `docs/testing-and-evaluation.md` 的 attestation 链接改指 `evidence/`
- [x] 2.3 `docs/adr/README.md` 0005 索引句去掉 TUI 机制残留
- [x] 2.4 冻结件正文不改写；其内部非链接文字引用保持不变

## 3. 治理与证据缝同步

- [x] 3.1 `check_doc_hygiene.py` `DOC_LAYER_DOCS` 同步 evidence/ 新路径（注册范围不可缩水），
      更新 docstring 与自测 fixture 路径
- [x] 3.2 `tests/contract/test_release_attestation.py` attestation 路径常量同步
- [x] 3.3 `tests/contract/test_release_evidence_provenance.py` BASELINE/ATTESTATION 同步，
      REGRESSION_DESCENT 保持 `docs/regression-descent.md`
- [x] 3.4 `test_regression_descent.py` / `test_topology_snapshot.py` 无需改动，确认仍绿

## 4. 验证与收口

- [x] 4.1 `python3 openspec/governance/check_doc_hygiene.py --self-test` exit 0
- [x] 4.2 `python3 openspec/governance/check_doc_hygiene.py` exit 0
- [x] 4.3 四个 contract 测试通过
- [x] 4.4 `check_project_gate.py --phase plan --change 2026-09-12-organize-docs-by-lifetime` exit 0
- [x] 4.5 `UV_OFFLINE=1 make verify` exit 0
- [x] 4.6 按 openspec-archive-change 流程归档本 change
