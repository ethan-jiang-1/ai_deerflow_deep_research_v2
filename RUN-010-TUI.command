#!/bin/bash
# ============================================================================
#  010 TUI 战役启动器 —— 双击即跑（或终端里 bash RUN-010-TUI.command）
#
#  在【你眼前】的 Terminal 窗口里起 Deep Research TUI：
#    Stage A: fixture 图（零凭证，先摸 TUI 手感，分钟级）
#    Stage B: 真实图（真 DeepSeek + 真 Tavily，你在 TUI 里做 hitl1/hitl2 决策）
#
#  完整操作单: _backlog/_local_demo/runbook-010-tui-interactive.md
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
echo "${C_CYAN}  Deep Research · 010 TUI 交互战役  (runbook-010)${C_OFF}"
echo "${C_CYAN}════════════════════════════════════════════════════════════════════════${C_OFF}"
echo
echo "选一个阶段："
echo "  ${C_GREEN}1${C_OFF}) Stage A · fixture TUI     零凭证 · 分钟级 · 先摸手感"
echo "  ${C_GREEN}2${C_OFF}) Stage B · 真实交互 TUI    真模型+真网页 · 你来做 HITL 决策"
echo "  ${C_GREEN}q${C_OFF}) 退出"
echo
read -r -p "输入 1 / 2 / q: " choice
case "$choice" in
  1) MODE="fixture" ;;
  2) MODE="real" ;;
  *) echo "再见。"; exit 0 ;;
esac

# --- Stage B 的应答脚本提示卡（照着抄即可） ----------------------------------
if [ "$MODE" = "real" ]; then
  echo
  echo "${C_YELLOW}─────────────────── 应答脚本（跑的时候照这个抄） ───────────────────────${C_OFF}"
  echo "问题（TUI 下方输入框，原样粘贴后回车）:"
  echo "  ${C_GREEN}What is one bounded fact about China's EV battery market in 2024?${C_OFF}"
  echo
  echo "hitl1 各轮:"
  echo "  轮1 看到 profile proposal → 输入: ${C_GREEN}depth: quick overview. cost: minimal. time: very quick.${C_OFF} 回车"
  echo "  轮2 若再问 → 输入: ${C_GREEN}looks good, confirm.${C_OFF} 回车"
  echo "  语言选项出现 → 点 ${C_GREEN}Start proposal${C_OFF} 按钮（或输 English 回车）"
  echo "hitl2 决策 → 输入: ${C_GREEN}continue${C_OFF} 回车"
  echo
  echo "${C_DIM}提示: 全程真模型真网页，几分钟到十几分钟；别合盖/断网;${C_OFF}"
  echo "${C_DIM}      卡死就 Ctrl-C 退出，重跑本启动器即可（旧 bundle 自动归档）。${C_OFF}"
  echo "${C_YELLOW}──────────────────────────────────────────────────────────────────────${C_OFF}"
  echo
  read -r -p "按回车打开 TUI（Ctrl-C 可随时退出）..."
fi

# --- 起 TUI（就在这个窗口、你的眼前） ----------------------------------------
if [ "$MODE" = "fixture" ]; then
  make demo-tui-fixture
else
  make demo-tui-embedded-smoke
fi
TUI_EXIT=$?

# ── TUI 退出后：自动展示证据位置（跑完去哪看结果） ──────────────────────────
echo
echo "${C_CYAN}══════════════════ TUI 已退出 (exit=$TUI_EXIT) · 证据收尾 ══════════════════${C_OFF}"
LATEST_BUNDLE=$(ls -td .deep-research-demo-runs/workspace/deep-research/scopes/*/b_* 2>/dev/null | head -1)
if [ -n "$LATEST_BUNDLE" ] && [ -f "$LATEST_BUNDLE/state.json" ]; then
  echo "最新 bundle: ${C_GREEN}$LATEST_BUNDLE${C_OFF}"
  .venv/bin/python - "$LATEST_BUNDLE" <<'PYEOF'
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
r = f"{b}/final/report.md"
if os.path.exists(r):
    print(f"  报告            : {r}")
    print("  ── 报告开头 ──")
    print("\n".join(open(r).read().splitlines()[:12]))
else:
    print("  报告            : (本次未产出 final/report.md)")
PYEOF
else
  echo "${C_DIM}(没找到带 state.json 的 bundle——fixture 短路或启动失败时属正常)${C_OFF}"
fi
echo
echo "${C_DIM}完整验收/报 bug 流程: _backlog/_local_demo/runbook-010-tui-interactive.md${C_OFF}"
read -r -p "按回车关闭本窗口..."
