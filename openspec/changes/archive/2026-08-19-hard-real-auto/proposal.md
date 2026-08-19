# Hard Real-Auto Runs (Mode 004 End-to-End)

## Why

Runbook 004 (real model + real web tools, fully automatic, fixed comparison
question `Compare China and US EV battery market in 2024.`) is the last rung of
the local-demo ladder and is deliberately the hardest: it exists to find defects.
Mode 003 validated the real chain only under a declared `minimal` intent (one
topic, one work unit per wave, two-round wave2 gate). The default product path —
free multi-topic planning, per-topic work units, the default one-round wave2
gate, and the real multi-conclusion final layout — has never been exercised by a
real automatic run. 004 runs that path with zero product pre-changes: defects it
surfaces go through the bug flow with evidence, which is the rung's purpose.

## What Changes

- **Entry intent parameterization (A, operator surface).** `scripts/demo_real.py`
  gains `--profile-intent {minimal,none}` for the embedded-smoke route; the
  current hardcode (`minimal` when `--scripted`, else absent) becomes the default
  `minimal`, so mode 003 behavior is unchanged. `--profile-intent none` starts
  the automatic run WITHOUT an intent declaration — the default product path
  (degraded auto profile, no `single_topic`, free 1–8 topic planning, default
  one-round wave2 gate). The `StartRun.profile_intent` domain contract already
  admits `None`; no product `src/` behavior changes.
- **Mode 004 operator entry (B).** `scripts/soft_bundle.py` mode 004 registers
  the fixed comparison question, delegates to `make demo-real-scripted` with
  `--profile-intent none`, and reuses the record-based bind/inspect/verify
  surface (004 requires `final/report.md`, like 002/003).
- **Runbook and ladder documentation (C).** New
  `_backlog/_local_demo/runbook-004-hard-real-auto.md`; the README ladder's 004
  row is finalized (embedded-smoke entry; the Gateway automatic route is a
  separate product concern outside 001–004).

## Capabilities

### New Capabilities

- `hard-real-auto`: the mode 004 end-to-end acceptance — a default-intent
  (absent declaration) real automatic run on the fixed comparison question
  completes at `final_delivery` with a real `final/report.md` whose content
  covers both comparison subjects; topic breadth is observed and recorded, not
  asserted; the honest-gap degraded-delivery semantics are inherited unchanged.

### Modified Capabilities

- `demo-pipeline`: the embedded-smoke real `--scripted` entry gains an explicit
  `--profile-intent {minimal,none}` selection with `minimal` as the default
  (today's behavior); `none` runs the automatic path without an intent
  declaration. The Gateway rejection of `--scripted` and the TUI minimal
  declaration are unchanged.
- `soft-bundle-session-cli`: mode 004 runs the real-auto embedded-smoke route
  without an intent declaration, records and verifies the bundle, and requires
  `final/report.md` on verify; the record-based inspect delegation covers
  mode 004 like modes 002/003.

## Impact

- `deep_research_harness/scripts/demo_real.py` (CLI flag; embedded-smoke intent
  selection)
- `deep_research_harness/scripts/soft_bundle.py` (MODE_QUESTIONS, mode 004 run
  branch, verify report-required set, inspect delegation set)
- Tests: `tests/integration/test_demo_real.py` (intent flag two-branch, default
  unchanged), `tests/contract/test_soft_bundle_cli.py` (mode 004 bind/verify)
- Docs: `_backlog/_local_demo/runbook-004-hard-real-auto.md` (new),
  `_backlog/_local_demo/README.md` (004 row finalized)
- No product `src/deerflow_deep_research/` behavior changes; no `deerflow/`
  gitlink changes; no gate/domain/node/prompt changes. Known observed input
  asymmetry (comparison-subject seed extraction yields
  `('China', 'US EV battery market in 2024.')` for the fixed question) is
  recorded as an observation point, NOT pre-fixed — evidence-driven bug flow
  only.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/demo_real.py` + `deep_research_harness/scripts/soft_bundle.py` — the operator entry surface that selects and declares (here: declines to declare) the research intent and delegates to the existing embedded-smoke route.
- **Seam classification:** wiring — CLI parameterization and mode delegation only; no model role, prompt, gate, domain contract, or state writer changes.
- **Question:** How does mode 004 run the default product path (no declared intent) end to end on the fixed comparison question so the never-exercised multi-topic real chain is tested and its defects surface, while mode 003's minimal-intent behavior and every product default stay exactly as today?
- **Scope honesty:** mode 004 validates the non-interactive operator path (embedded smoke) under an absent intent declaration; it does not claim coverage of the Gateway interactive path or Gateway-side automation.
- **Necessary adjacent/external contracts:** three named contracts answer bounded questions for this change (details below).
  - `demo-pipeline` (`DPL-003`): the embedded-smoke entry's minimal declaration becomes an explicit default-minimal selection (entry-surface question).
  - `soft-bundle-session-cli` (`SBC-002`, `SBC-004`): mode 004 delegation, verification, and record-based inspection (operator-CLI question).
  - `low-scale-real-auto` (`LSA-001`): read-only parallel — mode 003's declared-minimal acceptance defines the contrast 004 runs without.
- **Evidence seam:** `tests/integration/test_demo_real.py` (flag default = minimal unchanged; `none` omits the declaration), `tests/contract/test_soft_bundle_cli.py` (mode 004 bind/verify); end-to-end: zero-cost 002 regression, 003 contract regression (plus one real 003 rerun at closeout), and one real 004 run (`RESULT: PASS`, real comparative report).
- **Not in scope:** Gateway non-interactive automation; comparison-subject extraction fixes (observe first, bug flow on evidence); any product `src/` node/domain/engine/gate change; `deerflow/` gitlink; bridge hang hardening; readiness/final budget relaxation without observed exhaustion.
- **Triggered review policies:** change-admission

## deerflow boundary

Ordinary downstream work neither modifies nor source-browses the `deerflow/`
gitlink; this change does not own or approve any `deerflow/` boundary work.
