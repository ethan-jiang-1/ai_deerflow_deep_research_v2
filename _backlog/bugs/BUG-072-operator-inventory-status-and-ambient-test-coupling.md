# BUG-072: 操作员清册把已取消 bundle 报成 resumable + 演示 CLI 测试耦合环境现场

> 严重级别: P2 | 发现: 2026-09-27 | 状态: 活跃

## 症状

两条相关事实（同一现场暴露）：

1. **清册说谎**：把一个已取消的 bundle 报成可恢复。
   ```
   $ make demo-workspace-report
   bundles: 39 (terminal 37, non-terminal 2)
     b_iBO2Tfg5K8z7iNk8ZP…  [resumable (status: suspended)]  120094 bytes
     b_u_t_Vmffz8pfXM6Gc0…  [resumable (status: active)]     118220 bytes
   ```
   而两个 bundle 的 `state.json` 都是 `terminal_status: cancelled`（我随后用
   恢复路径取消的）——清册仍报 non-terminal，会误导操作者（也误导了排查）。

2. **集成测试非密封**：`tests/integration/test_demo_cli.py` 的两个用例直接跑
   `scripts/demo.py`（默认 bundle root = `<harness>/.deep-research-demo-runs`），
   一旦工作区存在任何非终态 bundle（例如操作者停在 HITL 的一次调试会话），
   fixture 运行被生命周期拒为"仍在执行"，测试即 **红**（`git stash` 验证：在
   HEAD 上也红，与当时未提交的改动无关）。取消遗留 bundle 后即恢复绿。

## 根因

1. `scripts/soft_bundle.py::_bundle_status` 只读
   `diagnostics/run-summary.json` 的 `status`——那是**运行期观测快照**，
   `lifecycle.cancel` 不会刷新它；而生命周期的终态事实在 `state.json` 的
   `terminal_status`。清册选择了较弱的投影作为状态来源，于是"取消"对清册不可见。
2. 测试把**环境现场**当作输入：`DemoAdapter()` 默认根固定为 harness 下的
   `.deep-research-demo-runs`，没有可注入的根覆盖，于是同一工作区的历史状态
   （非终态 bundle）决定了测试结果。

## 复现

```bash
cd deep_research_harness
make demo-workspace-report                     # 观察 resumable 行
python3 -c "import json;print(json.load(open('<bundle>/state.json'))['terminal_status'])"
# 二者不一致即命中第 1 条
.venv/bin/python -m pytest tests/integration/test_demo_cli.py -q   # 有非终态 bundle 时红
```

## 修复关联

**第 1 条**（状态来源）：让清册以**生命周期终态事实**为准（`state.json` 的
`terminal_status`），观测快照作回退。注意 DPL-014 的 fail-closed 语义（"run
summary 不可读 ⇒ 永不成为清理候选"）——提升 `state.json` 的优先级会改变
"清理候选"的判定，属契约面语义，**需要先确认 owning spec 的措辞并相应更新**
（走 OpenSpec change，不直接改）。

**第 2 条**（测试密封）：给本地演示适配器一个可注入的 bundle 根
（环境变量，如 `DEERFLOW_DEMO_BUNDLE_ROOT`，默认行为不变），演示 CLI 用例把它
指向 tmp 目录；这同时符合 `docs/testing-and-evaluation.md` 的 Test Hygiene
（不依赖环境现场、不静默依赖工作区历史）。

两条都修完后，第 2 条的密封改动可顺带锁一条回归：在"存在非终态 bundle"的临时
工作区里跑演示 CLI，断言其行为与工作区状态无关。
