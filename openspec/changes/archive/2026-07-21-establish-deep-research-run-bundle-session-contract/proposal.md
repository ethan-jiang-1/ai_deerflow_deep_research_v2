## Why

The real standalone demo creates a valid research bundle but places it in a
`TemporaryDirectory` that is removed at process exit. Neither the CLI nor the TUI
gives a developer a durable run reference, bundle location, or inspectable trace;
the only persisted local record is a redacted failure-only diagnostic journal. A
developer therefore cannot inspect a normal run without guessing temporary paths or
adding ad hoc logging.

The project already defines the research bundle as the planned session root. This
change establishes the first usable session contract: durable local inspection of a
run and its safe history, without claiming that inspection alone enables resume.

## What Changes

- Add a runtime-owned run-session capability that atomically publishes a bounded
  manifest and redacted lifecycle trace beneath the canonical research bundle. The
  full-fake route receives an explicitly session-metadata-only root; it does not
  pretend that fake graph nodes materialized research content.
- Replace disposable local demo storage with the gitignored project-local root
  `agent/.deep-research-demo-runs/`, with its ignore rule owned by the new
  downstream `agent/.gitignore`. A session is retained only after a record-bearing
  validated lifecycle result supplies research id, status, phase, and generation;
  preflight, denials, malformed results, and status-less errors create no bundle.
- Give shared run updates, the CLI, and the TUI a safe run reference and explicit
  inspectability/durability truth. Developer-facing inspection resolves that
  reference to manifest, trace, artifacts, and diagnostics without printing raw host
  paths in ordinary user-facing output.
- Preserve checkpoint, pending interrupt, and ledger authority: manifest and trace
  are derived views only. This change does not implement automatic cross-process
  resume, a Gateway/Web workbench, multi-user discovery, or a second state store.
- Add deterministic redaction, retention, and production-shaped lifecycle evidence
  for bundle persistence and inspection.

## Capabilities

### New Capabilities

- `research-run-session`: Canonical local run-bundle manifest, redacted lifecycle
  trace, retention, and developer inspection contract (RUS-001 through RUS-003).

### Modified Capabilities

- `demo-pipeline`: Local demos retain inspectable bundles under bounded retention
  instead of deleting all run artifacts on exit (DPL-007).
- `research-cli-onboarding`: CLI surfaces a safe run reference and explicit
  inspection path without exposing host paths or implying resume (REC-004).
- `research-demo-tui`: TUI surfaces the same safe run reference and inspectability
  state as the CLI (RED-005).
- `research-run-experience`: Shared updates carry safe session inspection and
  retention facts without becoming lifecycle control, and post-run diagnostics are
  placed in the retained bundle without fingerprinting raw failure sources
  (RER-003, RER-006).
- `research-graph-lifecycle`: Manifest and trace remain derived projections, never
  a second phase/pending-input/transition authority (REG-014).
- `project-structure`: Run-session domain/runtime modules are registered in the
  canonical downstream structure (PRS-006).

## Impact

- Affected downstream code: `agent/src/deerflow_deep_research/domain/`,
  `runtime/`, the local demo adapter and CLI/TUI presentation scripts, test/evidence
  metadata, architecture registry, and Deep Research documentation.
- New local artifacts: `manifest.json`, `diagnostics/lifecycle.jsonl`, and, when a
  post-bind diagnostic is warranted, `diagnostics/records.jsonl` under
  `agent/.deep-research-demo-runs/workspace/deep-research/<research_id>/`. The local
  root is ignored by downstream-owned `agent/.gitignore`, owner-only, and retained
  under an explicit count, age, and byte policy.
- No files under `backend/` or `frontend/` change. No new Gateway configuration,
  public skill, MCP/ACP, Agent/SOUL, or production Web surface is introduced.
- Selecting, overlaying, or hot-switching DeerFlow `config.yaml` / extensions profiles
  is out of scope; it is a separate startup-orchestration concern.
- Deterministic proof will use local filesystem and replayed external boundaries;
  credentialed acceptance supplements, rather than replaces, that evidence.
