"""Read-side trace replay spike (zero-contract): bundle dir -> per-node cards.

Replays one run bundle's persisted superstep checkpoints into per-node boundary
cards. Strictly read-only: opens ``graph.sqlite`` in ro mode and never invokes
a node. Precedent: ``verify_b1_pass.py`` (campaign evidence tool).

Usage:
    .venv/bin/python scripts/tui_trace.py <bundle_dir> [--json]
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from deerflow_deep_research.runtime.checkpoint import build_deep_research_checkpoint_serde
from deerflow_deep_research.runtime.research import ResearchGraphRecipe


async def _replay(bundle: Path) -> dict:
    db = bundle / "graph.sqlite"
    if not db.is_file():
        raise SystemExit(f"no graph.sqlite under {bundle}")
    bundle_id = bundle.name

    import aiosqlite

    conn = await aiosqlite.connect(f"file:{db}?mode=ro", uri=True)
    try:
        saver = AsyncSqliteSaver(conn)
        saver.serde = build_deep_research_checkpoint_serde()
        graph = ResearchGraphRecipe.all_real().builder.compile(checkpointer=saver)
        config = {"configurable": {"thread_id": bundle_id, "checkpoint_ns": ""}}
        snaps = [snap async for snap in graph.aget_state_history(config)]
    finally:
        await conn.close()
    snaps.reverse()  # oldest first

    cards: list[dict] = []
    prev_values: dict | None = None
    for index, snap in enumerate(snaps):
        meta = dict(snap.metadata or {})
        writes = meta.get("writes")
        values = dict(snap.values or {})
        changed = []
        if prev_values is not None:
            changed = [key for key in values if prev_values.get(key) != values.get(key)]
        trace = values.get("execution_trace") or ()
        cards.append(
            {
                "seq": index,
                "step": meta.get("step"),
                "source": meta.get("source"),
                "created_at": getattr(snap, "created_at", None),
                "writes_nodes": sorted(writes) if isinstance(writes, dict) else writes,
                "next": list(snap.next or ()),
                "phase": values.get("phase"),
                "route": values.get("route"),
                "terminal_status": values.get("terminal_status"),
                "trace_tail": list(trace[-3:]),
                "changed_keys": changed,
            }
        )
        prev_values = values

    events_path = bundle / "diagnostics" / "events.jsonl"
    events_count = 0
    first_event_keys: list[str] = []
    if events_path.is_file():
        lines = events_path.read_text(encoding="utf-8").splitlines()
        events_count = len(lines)
        if lines:
            first_event_keys = sorted(json.loads(lines[0]))

    return {
        "bundle_id": bundle_id,
        "supersteps": len(snaps),
        "terminal": snaps[-1].values.get("terminal_status") if snaps else None,
        "cards": cards,
        "events_count": events_count,
        "first_event_keys": first_event_keys,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay one run bundle as per-node cards (read-only).")
    parser.add_argument("bundle", type=Path, help="Run bundle directory containing graph.sqlite")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text cards")
    args = parser.parse_args()

    payload = asyncio.run(_replay(args.bundle))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        return
    print(
        f"bundle={payload['bundle_id']} supersteps={payload['supersteps']} "
        f"terminal={payload['terminal']} events={payload['events_count']}"
    )
    for card in payload["cards"]:
        print(
            f"[{card['seq']:02d}] step={card['step']} src={card['source']} "
            f"writes={card['writes_nodes']} next={card['next']} "
            f"phase={card['phase']} route={card['route']} term={card['terminal_status']} "
            f"ts={card['created_at']} trace={card['trace_tail']}"
        )
        if card["changed_keys"]:
            print(f"     Δ {','.join(card['changed_keys'][:10])}{'…' if len(card['changed_keys']) > 10 else ''}")


if __name__ == "__main__":
    main()
