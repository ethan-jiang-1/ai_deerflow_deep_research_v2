# hard-real-auto Specification

> req: HRA-001

## Purpose

End-to-end acceptance for mode 004: a fully automatic real run (real model + real web tools, fixed comparison question) started through `soft-bundle run <root> --mode 004` with NO declared research intent (the default product path) completes at `final_delivery` with a real comparative `final/report.md` covering both comparison subjects.

## Requirements

### Requirement: Mode 004 default-intent real-auto runs complete with a real comparative report

A fully automatic real run (real model + real web tools, fixed comparison
question `Compare China and US EV battery market in 2024.`) started through
`soft-bundle run <root> --mode 004` SHALL start the fixed real-auto
embedded-smoke entry WITHOUT declaring a research intent (explicit
`--profile-intent none`), so the run exercises the default product path: topic
planning remains free within the contract's 1–8 topic bound (no `single_topic`
constraint), each wave runs at least one work unit per planned topic, the wave2
gate budget resolves to the default one evidence round, and final delivery uses
the real multi-conclusion layout path. The run SHALL terminate completed at
`final_delivery` and publish `final/report.md` with real comparative content
(backed by real sources, not scripted template sentences) that covers BOTH
comparison subjects (the China and the US EV battery market), plus the
claim-citation map. An honest searchable gap that does not converge within the
default wave2 evidence budget SHALL NOT terminate the run: the first budget
exhaustion degrades to a bounded honest pass and the final report SHALL disclose
every remaining unresolved searchable gap as a mandatory uncertainty; only a
repeated exhaustion after that degradation blocks. Topic breadth SHALL be
observed and recorded from the run's work units (the planner's actual topic
count and scopes), never asserted to a fixed count. The embedded-smoke entry's
absent `--profile-intent` selection SHALL remain `minimal`, so mode 003 behavior
is unchanged. The runbook-004 SHALL document the prerequisites
(`DEEPSEEK_API_KEY`, `TAVILY_API_KEY`, `DEERFLOW_DEMO_MODEL`), the verification
checks, the Ctrl-C-and-retry note for a hung provider, and the honest-gap
degraded-delivery acceptance; it SHALL record the observed comparison-subject
seed extraction for the fixed question as an observation point without
pre-fixing it. (`HRA-001`)

#### Scenario: A real auto run completes with a real comparative report

- **WHEN** a caller runs `soft-bundle run <root> --mode 004` with credentials and
  network available, and the model/tools behave
- **THEN** the run reaches `final_delivery -> completed`, `final/report.md`
  exists with substantive comparative content covering both the China and the US
  EV battery market backed by real source URLs, and the soft-bundle verification
  prints `RESULT: PASS`

#### Scenario: A non-converging honest gap still delivers honestly

- **WHEN** a mode-004 run leaves a searchable gap unresolved after the default
  one evidence round
- **THEN** the first budget exhaustion degrades to a bounded honest pass, the run
  still completes at `final_delivery`, `final/report.md` exists with real
  content, and its uncertainties section discloses the remaining gap rather than
  the run ending blocked without a report; only a repeated exhaustion after that
  degradation blocks

#### Scenario: Default-intent breadth is observed, not asserted

- **WHEN** a mode-004 run (no declared intent) completes
- **THEN** its recorded bundle shows the planner's actual topic decomposition
  with at least one work unit per planned topic per wave, the evidence
  submissions reference real source URLs, and no single-topic breadth is promised

#### Scenario: The embedded-smoke entry default stays minimal

- **WHEN** the embedded-smoke real entry runs `--scripted` without an explicit
  `--profile-intent` selection
- **THEN** the entry declares `profile_intent=minimal` exactly as before (mode
  003 behavior unchanged); mode 004 passes `--profile-intent none` explicitly
