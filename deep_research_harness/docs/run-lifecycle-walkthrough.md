# Deep Research Run Lifecycle Walkthrough

> Reader interface only. This file is not a runtime resource or configuration.
> Code, typed contracts, tests, and approved specifications remain the authority.
> Vocabulary source: every bolded term is defined in [`../CONTEXT.md`](../CONTEXT.md);
> this walkthrough only sequences existing terms — it coins none.
> Edge-level truth: [`deep-research-topology.md`](deep-research-topology.md).
> Budget: this file stays under 150 lines; trim narrative before growing it.

This is the story of one Deep Research Run, told in the order a fresh reader meets
the moving parts. Terminal statuses, routes, and node names below are the real ones.

## 1. A run is born

A **Primary User** asks a question. The **Deep Research Harness** creates a fresh
**Run Bundle** — one directory holding that run's **Research State**, evidence,
content, and **Run Event Journal** — identified by an opaque **Run Bundle ID**
(observably shaped like `b_…`, never derived from the conversation). The bundle is
published atomically before anything can discover it; **Run Discovery** later finds
runs only by reading bundle directories, never from a registry or cache. At most one
bundle is active in a trusted scope. The conversation may retain a transient
**Current Bundle Handle**, but the handle cannot prove the bundle exists — only the
filesystem, validated, can.

## 2. Confirmation before work

`bootstrap` binds the request into the bundle, then routes `needs_input` to `hitl1`
when the request is incomplete. `hitl1` runs **Research Confirmation**: a lightweight,
**Model-Led Research Interaction** proposes scope, and the user either accepts or
supplies a **User Decision**. Model interpretations stay advisory until they become an
**Accepted Research Fact**; a bounded preference captured along the way is an
**Accepted Profile Note** — profile content, not a work order. A follow-up question is
answered by a **Correlated Research Response**, which resolves only that one subject.
Routes: `accepted` → `topic_planning`, `needs_followup` → `hitl1`, `cancel` →
cancelled, `exhausted` → blocked.

## 3. Planning and the three waves

`topic_planning` turns accepted facts into a topic registry (route `next`). Then the
research work runs as bounded **LLM-Bearing Node** programs — each a **Node Cognitive
Control Program** (what the model may think and propose) behind a **Deterministic
Control Boundary** (what code admits):

- `wave0` — acquire authoritative-source candidates; workers propose, never admit.
- `wave1` — extract evidence and run read-only critics over accepted records.
- `wave2_synthesis` — synthesize accepted evidence into findings and gaps.

The **evidence ledger** inside the bundle is the accepted-evidence authority; the
waves propose, validators/ledger/gate dispose. `wave0`/`wave1` can route `repair` to
themselves inside a bounded budget; `exhausted` anywhere routes to blocked.

## 4. The evidence loop and the second human stop

If synthesis lacks support, `wave2_synthesis` routes `evidence_needed` to
`targeted_evidence`, which fetches for named gaps and returns (`next`) — the only
cycle between two nodes. When synthesis passes, `hitl2` stops for the user: revise
the view, repair evidence, trigger `rerun` (a new **Refinement Round** over the same
bundle, replanning by depth), `proceed`, `stop`, or `cancel`.

## 5. Readiness and delivery

`readiness` is the last deterministic quality gate — routing `repair_targeted`,
`repair_synthesis`, or `repair_hitl2` back into the loop — and then `final_delivery`
composes the **Final Report Artifact** (`final/report.md`), the readable
**Research Outcome**: answer, evidence and sources, scope and assumptions,
limitations. `pass` routes to the `completed` terminal status. One completed Refinement
Round has ended; earlier materials stay retained for inspection.

## 6. After the terminal boundary: refine

A terminal bundle can be reopened. A text-bearing `refine` performs **Run
Refinement**: **Refinement Admission** stores exactly one pending direction in the
bundle — it never rewrites state under an in-flight writer and never replaces a
pending Correlated Research Response. The pending direction is consumed only at the
next completed terminal boundary; `stopped`, `cancelled`, and `blocked` preserve it.
A textless `refine` against that same `bundle_id` is a **Refinement Continuation**:
it supplies no new text and consumes the stored direction only when the bundle has
full-rerun capacity. An ended bundle that retains no capacity projects `start`
instead. Nothing is ever resumed from conversation memory.

## 7. When a bundle disappears

**Bundle Loss** — external deletion — makes the run permanently unavailable. The
harness does not recreate the bundle, infer its state, or recover it from an
observation; retained journal readers and participant presentation stop working with
it. An **External Run Observation** may outlive the bundle as a non-authoritative
log, but it cannot locate, authorize, or resurrect anything. A fresh `start` remains
legal. Suspension is a different case: a suspended run is a pause awaiting recovery,
not a terminal failure and not Bundle Loss; the supported reattachment presentation
is the demo TUI's startup attach projection (a bounded list of recoverable bundles
with continue/inspect/discard choices), routed through lifecycle actions only.

## 8. Watching it locally

Operator routes (fixture demo, scripted real, TUI, workbench, session inspection) are
indexed in [`../COMMANDS.md`](../COMMANDS.md) with run details in
[`local-operations.md`](local-operations.md). The fixture-graph demo walks this exact
topology end to end with zero credentials.
