#!/bin/bash
# ============================================================================
#  010 TUI 战役启动器 —— 双击即跑（或终端里 bash RUN-010-TUI.command）
#
#  在【你眼前】的 Terminal 窗口里起 Deep Research TUI：
#    Stage A:  fixture 图（零凭证，已知形状 UI smoke，分钟级）
#    Stage B1: 真实图（真模型 + 真网页，你在 TUI 里做 HITL1 决策；
#              HITL2 是自主 continuation，不需要你）
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
echo "  ${C_GREEN}1${C_OFF}) Stage A  · fixture TUI     零凭证 · 分钟级 · 已知形状 smoke"
echo "  ${C_GREEN}2${C_OFF}) Stage B1 · 真实交互 TUI    真模型+真网页 · 你来做 HITL1 决策"
echo "  ${C_GREEN}q${C_OFF}) 退出"
echo
read -r -p "输入 1 / 2 / q: " choice
case "$choice" in
  1) MODE="fixture" ;;
  2) MODE="real" ;;
  *) echo "再见。"; exit 0 ;;
esac

# --- Stage B1 的应答脚本提示卡（照着抄即可） ----------------------------------
if [ "$MODE" = "real" ]; then
  echo
  echo "${C_YELLOW}─────────────────── 应答脚本（跑的时候照这个抄） ───────────────────────${C_OFF}"
  echo "问题（TUI 下方输入框，原样粘贴后回车）:"
  echo "  ${C_GREEN}What is one bounded fact about China's EV battery market in 2024?${C_OFF}"
  echo
  echo "hitl1（条件式修订——先看初始 proposal 的 depth 字段）:"
  echo "  depth 不是 quick_overview → 输入: ${C_GREEN}depth: quick overview.${C_OFF} 回车"
  echo "  depth 已是 quick_overview → 输入: ${C_GREEN}depth: deep dive.${C_OFF} 回车"
  echo "  修订后的 proposal 达到目标 → 点 ${C_GREEN}Start proposal${C_OFF} 按钮确认"
  echo "  ${C_DIM}（抄下三值留证据: 初始 depth / 你的修订句 / 修订后 depth）${C_OFF}"
  echo
  echo "hitl2 → ${C_GREEN}不需要你${C_OFF}（自主 continuation，自动经过；若停下来等输入=异常，记录它）"
  echo "语言选项 → 本问题不会出现（英文确定性 en；若出现=已知 bug BUG-060，记录即可）"
  echo
  echo "${C_DIM}提示: 全程真模型真网页，几分钟到十几分钟；别合盖/断网。${C_OFF}"
  echo "${C_DIM}      卡死就 Ctrl-C 退出重跑本启动器（旧 bundle 不会自动清理，验收只认本次新增）。${C_OFF}"
  echo "${C_YELLOW}──────────────────────────────────────────────────────────────────────${C_OFF}"
  echo
  read -r -p "按回车打开 TUI（Ctrl-C 可随时退出）..."
fi

# --- exact-bundle 绑定：启动前记录目录集合（仅 Stage B1 产出真实 bundle） ----
BROOT=.deep-research-demo-runs/workspace/deep-research/scopes
BEFORE_LIST=$(ls -d "$BROOT"/*/b_* 2>/dev/null | sort)

# --- 起 TUI（就在这个窗口、你的眼前） ----------------------------------------
if [ "$MODE" = "fixture" ]; then
  make demo-tui-fixture
else
  make demo-tui-embedded-smoke
fi
TUI_EXIT=$?

# ── TUI 退出后：exact-bundle 绑定 + 证据展示（不回退 mtime-latest） ─────────
echo
echo "${C_CYAN}══════════════════ TUI 已退出 (exit=$TUI_EXIT) · 证据收尾 ══════════════════${C_OFF}"
if [ "$MODE" = "real" ]; then
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
else
  echo "${C_DIM}(Stage A fixture 不产出真实 run bundle；交互面结论记入战役记录即可)${C_OFF}"
fi
echo
echo "${C_DIM}完整验收/PASS 判据/报 bug 流程: _backlog/_local_demo/runbook-010-tui-interactive.md${C_OFF}"
read -r -p "按回车关闭本窗口..."
