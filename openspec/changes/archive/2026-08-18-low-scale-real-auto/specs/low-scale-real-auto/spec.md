## ADDED Requirements

### Requirement: Mode 003 real-auto runs complete with a real report

A fully automatic real run (real model + real web tools, fixed bounded question)
started through `soft-bundle run <root> --mode 003` SHALL declare
`profile_intent=minimal` at the entry, so the run exercises the real product path
under the minimal intent: the topic planner is required to emit exactly one topic
(`single_topic`), wave0 and wave1 each run exactly one work unit, wave2
cross-synthesis operates on one topic, and the wave2 gate budget resolves to two
evidence rounds. The run SHALL terminate completed at `final_delivery` and
publish `final/report.md` with real content (backed by real sources, not scripted
template sentences), plus the claim-citation map. The runbook-003 SHALL document
the prerequisites (`DEEPSEEK_API_KEY`, `TAVILY_API_KEY`, `DEERFLOW_DEMO_MODEL`)
and the verification checks, including the Ctrl-C-and-retry note for a hung
provider. Runs without the declared intent do not promise single-topic breadth.
(`LSA-001`)

#### Scenario: A real auto run completes with a real report
- **WHEN** a caller runs `soft-bundle run <root> --mode 003` with credentials and
  network available, and the model/tools behave
- **THEN** the run reaches `final_delivery -> completed`, `final/report.md` exists
  with substantive content, and the soft-bundle verification prints
  `RESULT: PASS`

#### Scenario: The declared-minimal real auto run keeps wave breadth at one
- **WHEN** a mode-003 run (declared minimal intent) completes
- **THEN** its recorded bundle contains exactly one wave0 work unit and one wave1
  work unit, and the evidence submissions reference real source URLs

#### Scenario: Runs without the declared intent do not promise single-topic breadth
- **WHEN** a run does not declare `profile_intent=minimal`
- **THEN** no single-topic or two-round-gate behavior is promised by this change
