# Design: preserve-failed-run-bundles

## Context

BUG-052：control run 前置清理是 `shutil.rmtree(RUNS_ROOT / "deep-research")`。
排障循环中 run N 的现场在 run N+1 前被毁（run 1–3 的 bundle 因此时丢失）。

## Goals / Non-Goals

- **Goal**：重跑保留最近 3 份失败/历史现场（per 子树名），磁盘有界；发现语义
  零变化。
- **Non-Goal**：不做跨机器归档、不做压缩（本地排障，原始目录即可直读）、不改
  bundle discovery 本体。

## Decisions

### D1. 归档用 `rename` 而非 copy-then-delete

同一文件系统内 `Path.rename` 是原子且 O(1)；copy 双倍 I/O 且中途失败留残骸。
归档路径 `RUNS_ROOT/archive/<name>-<UTC秒-微秒时间戳>`（`YYYYMMDDHHMMSS-µµµµµµ`，
定宽）；UTC 定宽保证字典序即时间序。

### D2. 保留数 N=3，per 子树名独立计数

排障一个 bug 通常只需"上一现场 + 上上一现场"对照；3 份覆盖两轮对照 + 当前。
per-name 计数避免 deep-research（大）与 scripted-real（小）互相挤占。

### D3. 归档目录置于 `archive/` 前缀，天然在 discovery 扫描根之外

discovery 只扫 `deep-research/scopes/...` 等受管子树；`archive/` 是新的兄弟目录，
不匹配任何扫描根，无需改 discovery 代码。测试以"归档后 discovery 行为不变"的
既有测试套全绿来锁定。

### D4. 失败语义：归档失败 → 让异常传播（run 不开始）

归档失败（权限/跨设备）意味着旧现场无法保全，静默继续等于回到 BUG-052。
让异常带着路径信息传播，操作员显式处理。

## Risks / Trade-offs

- [磁盘占用 ×3] → 单次 run 子树 ~几 MB（checkpoint + events），3 份可忽略；
  scripted-real 同理。
- [rename 跨设备失败] → RUNS_ROOT 与 archive 同父目录，同文件系统，构造上
  不可能跨设备。
- [归档时间戳冲突（同微秒双跑）] → 极端场景；`-N` 序号后缀递增直到唯一。

## Migration Plan

无持久化格式变化。旧行为（删除）直接被替换；首次运行时 `archive/` 不存在则
创建。
