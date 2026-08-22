#!/bin/bash
# ============================================================================
#  020 手动 TUI 启动器 —— 双击即跑（或终端里 bash RUN-020.command）
#
#  在【你眼前】的 Terminal 窗口里起真实交互 TUI：
#    真模型 + 真网页，你在 TUI 里做 HITL1 决策；
#    HITL2 是自主 continuation，不需要你。
#
#  完整操作单: _backlog/_local_demo/runbook-020-tui-manual.md
# ============================================================================

# --- 定位仓库（双击打开时 cwd 是 home，必须自己 cd） -----------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HARNESS="$SCRIPT_DIR/deep_research_harness"
cd "$HARNESS" || { echo "找不到 deep_research_harness/：$HARNESS"; read -r -p "按回车关闭..."; exit 1; }

# --- PATH 兜底（双击的 Terminal 可能没有 ~/.local/bin，uv 在那里） ----------
export PATH="$HOME/.local/bin:$PATH"

# --- 颜色 ------------------------------------------------------------------
C_CYAN=$'\033[36m'; C_YELLOW=$'\033[33m'; C_GREEN=$'\033[32m'; C_RED=$'\033[31m'; C_DIM=$'\033[2m'; C_OFF=$'\033[0m'

clear
echo "${C_CYAN}════════════════════════════════════════════════════════════════════════${C_OFF}"
echo "${C_CYAN}  Deep Research · 020 手动 TUI 交互（runbook-020）${C_OFF}"
echo "${C_CYAN}════════════════════════════════════════════════════════════════════════${C_OFF}"
echo
echo "直接进入真实交互 TUI（真模型+真网页，你来做 HITL1 决策）。"
echo "${C_DIM}注: 曾有的 Stage A（fixture UI smoke）已移除——010 已覆盖 TUI 通路验证，"
echo "     启动器不再提供；如需单独跑 fixture smoke 用 make demo-tui-fixture。${C_OFF}"

# --- 应答脚本提示卡（照着抄即可） ------------------------------------------
echo
echo "${C_YELLOW}─────────────────── 应答脚本（跑的时候照这个抄） ───────────────────────${C_OFF}"
echo "侦察模式（TUI 启动后不直接跑；研究结束后也会回到这里）:"
echo "  看环境/workspace/之前跑过什么 → 输入: ${C_GREEN}环境${C_OFF} 或 ${C_GREEN}env${C_OFF}（显示 workspace 路径与结构）"
echo "  随便聊 → 直接输入任何内容（真模型低成本回应）"
echo
echo "启动正式 Deep Research（按钮或整句触发语）:"
echo "  点 ${C_GREEN}Start Deep Research${C_OFF} 按钮，或输入: ${C_GREEN}开始 Deep Research${C_OFF}（或 ${C_GREEN}start deep research${C_OFF}）"
echo "  → 触发后自动跑固定问题: What is one bounded fact about China's EV battery market in 2024?"
echo
echo "hitl1（条件式修订——先看初始 proposal 的 depth 字段）:"
echo "  depth 不是 quick_overview → 点「深度: 快速概览」按钮或输入: ${C_GREEN}depth: quick overview.${C_OFF}"
echo "  depth 已是 quick_overview → 点「深度: 深入」按钮或输入: ${C_GREEN}depth: deep dive.${C_OFF}"
echo "  修订后的 proposal 达到目标 → 点 ${C_GREEN}Start proposal${C_OFF} 按钮确认"
echo "  ${C_DIM}（hitl1 有快捷修订按钮；每次输入会回显并显示「已按你的输入修订…」确认行；抄下三值留证据: 初始 depth / 你的修订句 / 修订后 depth）${C_OFF}"
echo
echo "hitl2 → ${C_GREEN}不需要你${C_OFF}（自主 continuation，自动经过；若停下来等输入=异常，记录它）"
echo "语言选项 → 本问题不会出现（英文确定性 en；若出现=已知 bug BUG-060，记录即可）"
echo
echo "${C_DIM}提示: 全程真模型真网页，几分钟到十几分钟；别合盖/断网。${C_OFF}"
echo "${C_DIM}      卡死就 Ctrl-C 退出重跑本启动器（旧 bundle 不会自动清理，验收只认本次新增）。${C_OFF}"
echo "${C_YELLOW}──────────────────────────────────────────────────────────────────────${C_OFF}"
echo
read -r -p "按回车打开 TUI（Ctrl-C 可随时退出）..."

# --- exact-bundle 绑定：启动前记录目录集合（真实 run 产出 bundle） ----------
BROOT=.deep-research-demo-runs/workspace/deep-research/scopes
BEFORE_LIST=$(ls -d "$BROOT"/*/b_* 2>/dev/null | sort)

# --- 起 TUI（就在这个窗口、你的眼前） ----------------------------------------
make demo-tui-embedded-smoke
TUI_EXIT=$?

# ── TUI 退出后：exact-bundle 绑定 + 证据展示（不回退 mtime-latest） ─────────
echo
echo "${C_CYAN}══════════════════ TUI 已退出 (exit=$TUI_EXIT) · 证据收尾 ══════════════════${C_OFF}"
AFTER_LIST=$(ls -d "$BROOT"/*/b_* 2>/dev/null | sort)
NEW_LIST=$(comm -13 <(echo "$BEFORE_LIST") <(echo "$AFTER_LIST"))
  NEW_COUNT=$(echo "$NEW_LIST" | grep -c . || true)
  if [ "$NEW_COUNT" -ne 1 ]; then
    echo "${C_RED}证据未绑定：本次新增 bundle 数 = $NEW_COUNT${C_OFF}"
    echo "${C_DIM}（0 个 = 启动/preflight 失败或没起 run；多个 = 并发写入。不得拿历史 bundle 冒充本次证据。）${C_OFF}"
  else
    BUNDLE=$(echo "$NEW_LIST")
    echo "本次 bundle（唯一新增）: ${C_GREEN}$BUNDLE${C_OFF}"
    if [ -f "$BUNDLE/state.json" ]; then
      .venv/bin/python - "$BUNDLE" <<'PYEOF'
import json, sys
b = sys.argv[1]
try:
    s = json.load(open(f"{b}/state.json"))
    print(f"  terminal_status : {s.get('terminal_status')}")
    prof = {k: s.get(k) for k in ("research_depth","cost_tolerance","time_budget","output_language","degraded_profile")}
    print(f"  profile         : {prof}")
except Exception as e:
    print(f"  (state.json 读取: {e})")
import os
for label, p in (("request/profile.json", f"{b}/request/profile.json"),):
    print(f"  {label:16s}: {'OK' if os.path.exists(p) else '(缺失)'}")
r = f"{b}/final/report.md"
if os.path.exists(r):
    print(f"  报告            : {r}")
    print("  ── 报告开头 ──")
    print("\n".join(open(r).read().splitlines()[:12]))
else:
    print("  报告            : (本次未产出 final/report.md)")
PYEOF
    else
      echo "${C_DIM}(bundle 无 state.json——启动后早期失败，按 runbook §6 处理)${C_OFF}"
    fi
  fi
echo
echo "${C_DIM}完整验收/PASS 判据/报 bug 流程: _backlog/_local_demo/runbook-020-tui-manual.md${C_OFF}"
read -r -p "按回车关闭本窗口..."
