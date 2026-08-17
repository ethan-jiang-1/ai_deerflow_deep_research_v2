# OpenSpec 产品边界与可移植性文档集

本目录只解释当前仓库如何把 OpenSpec practice 分成 portable、project-local 和 product 三层。

| 文件 | 职责 |
| --- | --- |
| [主计划](../openspec-product-boundary-portability.md) | 最终目标、结构、边界和完成标准 |
| [`01-review-findings.md`](01-review-findings.md) | 为什么需要这次收拢 |
| [`02-boundary-and-file-matrix.md`](02-boundary-and-file-matrix.md) | 每类内容和文件的唯一 owner |
| [`04-migration-and-proof.md`](04-migration-and-proof.md) | 迁移顺序、负向证明和验证命令 |

阅读顺序：主计划 → `02` → `04`；需要理解取舍时再读 `01`。

本方案不要求另一个仓库、不创建第二个 Change，也不把未来采用情况当作当前 Change 的完成条件。
