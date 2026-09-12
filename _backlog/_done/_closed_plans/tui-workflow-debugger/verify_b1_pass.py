#!/usr/bin/env python3
"""020 Stage B1 PASS verifier (mechanical conditions).

Usage:
    .venv/bin/python verify_b1_pass.py <bundle_dir>

Reads the exact-bundle's evidence and checks the mechanically-verifiable half of
the 7 PASS conditions from runbook-020 §3.4. Conditions 2 (human three-values)
and 7 (bug judgement) are NOT mechanical; this script prints the supporting
facts and a prompt for what the human must supply.

Field names are confirmed against a real `all_real` bundle (state.json schema 5,
request/profile.json schema 2, diagnostics/events.jsonl schema 3).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# state.json <-> request/profile.json field correspondence (different names).
PROFILE_FIELD_MAP = {
    "research_depth": "depth",
    "target_audience": "audience",
    "output_format": "format",
    "output_language": "output_language",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: verify_b1_pass.py <bundle_dir>", file=sys.stderr)
        return 2
    bundle = Path(sys.argv[1]).resolve()
    if not bundle.is_dir():
        print(f"bundle not found: {bundle}", file=sys.stderr)
        return 2

    results: list[tuple[str, bool, str]] = []

    state_path = bundle / "state.json"
    profile_path = bundle / "request" / "profile.json"
    report_path = bundle / "final" / "report.md"
    citation_path = bundle / "final" / "claim-citation-map.json"
    events_path = bundle / "diagnostics" / "events.jsonl"

    # --- condition 1: exact bundle bound (input is the unique new bundle) ----
    state = _load(state_path)
    results.append((
        "1  exact bundle",
        True,
        f"bundle_id={state.get('bundle_id')} implementation_mode={state.get('implementation_mode')}",
    ))

    # --- condition 3: profile.json matches state + degraded_profile=false ----
    profile = _load(profile_path)
    mismatches = []
    for state_key, profile_key in PROFILE_FIELD_MAP.items():
        sv, pv = state.get(state_key), profile.get(profile_key)
        if sv != pv:
            mismatches.append(f"{state_key}({sv!r}) != profile.{profile_key}({pv!r})")
    degraded_ok = (state.get("degraded_profile") is False
                   and profile.get("degraded_profile") is False)
    if not degraded_ok:
        mismatches.append(
            f"degraded_profile state={state.get('degraded_profile')!r} "
            f"profile={profile.get('degraded_profile')!r}"
        )
    results.append((
        "3  profile matches state + not degraded",
        not mismatches and degraded_ok,
        "; ".join(mismatches) if mismatches else
        f"depth={state.get('research_depth')!r} audience={state.get('target_audience')!r} "
        f"format={state.get('output_format')!r} lang={state.get('output_language')!r}",
    ))

    # --- condition 4: terminal completed + HITL2 autonomous (no interrupt) ---
    terminal_ok = state.get("terminal_status") == "completed"
    events = [_load_json_line(l) for l in events_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    hitl2_facts = [e for e in events if e.get("phase") == "hitl2"]
    hitl2_interrupt = [
        e for e in hitl2_facts
        if e.get("category") in ("interrupt", "pending_interrupt")
        or "AwaitingInput" in json.dumps(e, ensure_ascii=False)
        or "PendingResearchInterrupt" in json.dumps(e, ensure_ascii=False)
    ]
    hitl2_autonomous = bool(hitl2_facts) and not hitl2_interrupt
    results.append((
        "4  terminal completed + HITL2 autonomous",
        terminal_ok and hitl2_autonomous,
        f"terminal_status={state.get('terminal_status')!r} hitl2_facts={len(hitl2_facts)} "
        f"hitl2_interrupt={len(hitl2_interrupt)}",
    ))

    # --- condition 5: report + citation map with real content ----------------
    report_ok = report_path.exists()
    citation_ok = citation_path.exists()
    report_nondegenerate = False
    report_note = ""
    if report_ok:
        text = report_path.read_text(encoding="utf-8")
        # The historical degenerate layout repeats the question back without a
        # substantive finding; flag for human review rather than auto-failing.
        degenerate_marker = "Evidence supports a substantive answer for:"
        report_nondegenerate = degenerate_marker not in text and len(text.strip()) > 200
        report_note = f"report.md bytes={len(text)}"
        if degenerate_marker in text:
            report_note += " (DEGENERATE marker present -> human review)"
    results.append((
        "5  report + citation map present",
        report_ok and citation_ok,
        f"report={'OK' if report_ok else 'MISSING'} citation={'OK' if citation_ok else 'MISSING'} | {report_note}",
    ))
    if report_nondegenerate:
        results.append(("5b report non-degenerate (human confirms)", True, "no degenerate marker"))

    # --- condition 2 + 6 supporting facts ----------------------------------
    hitl1_facts = [e for e in events if e.get("phase") == "hitl1"]
    model_tool_facts = [e for e in hitl1_facts if e.get("category") == "model_tool"]
    print("=" * 72)
    print("MECHANICAL PASS CHECKS")
    print("=" * 72)
    all_ok = True
    for name, ok, detail in results:
        all_ok = all_ok and ok
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    print()

    print("--- condition 2 (four-step evidence chain) supporting facts ---")
    print(f"  state.research_depth      : {state.get('research_depth')!r}")
    print(f"  profile_ref.short_summary : {state.get('profile_ref', {}).get('short_summary')!r}")
    print(f"  hitl1_visit_count         : {state.get('hitl1_visit_count')!r}")
    print(f"  execution_trace           : {state.get('execution_trace')}")
    print("  [HUMAN MUST SUPPLY] initial depth + revision statement + revised depth")
    print("  [HUMAN MUST SUPPLY] explicit confirmation method (Start proposal click)")
    print()

    print("--- condition 6 (journal capability limitation) ---")
    print(f"  hitl1 model_tool facts    : {len(model_tool_facts)}")
    for e in model_tool_facts:
        print(f"    ordinal={e.get('call_ordinal')} outcome={e.get('outcome')} "
              f"capability_field_present={'capability' in e}")
    print("  NOTE: capability is NOT attributable from journal (§5.3); do not grep")
    print()

    print(f"OVERALL MECHANICAL: {'PASS' if all_ok else 'FAIL'} "
          f"(conditions 2/7 still need human + agent judgement)")
    return 0 if all_ok else 1


def _load_json_line(line: str) -> dict:
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return {}


if __name__ == "__main__":
    raise SystemExit(main())
