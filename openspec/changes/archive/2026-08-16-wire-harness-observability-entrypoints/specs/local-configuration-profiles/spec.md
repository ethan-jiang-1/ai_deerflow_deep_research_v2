> req: LCP-004, LCP-005

## MODIFIED Requirements

### Requirement: Profile observability is safe and restart-honest

Agent profile list/check/launch output SHALL identify only a safe profile label,
readiness, either isolated local SQLite or ephemeral memory state, and restart-required
state. It SHALL not expose raw configurations, environment values, secrets, mounts,
connection strings, parser/provider detail, or arbitrary host paths. Profile selection
starts a fresh process and creates no graph, lifecycle, checkpoint, ledger,
sandbox-content, run-session, Agent, skill, MCP, or ACP authority. (`LCP-004`,
`LCP-005`)

Before a profile advertises the Gateway observer, trace-correlated logging, Console,
or durable run-history observation, its deterministic check SHALL verify all of the
following documented restart-scoped prerequisites: JSON logging enhancement is
enabled; the supported run-history backend is durable for the claimed local mode; the
public Deep Research skill/Agent entry is ready; and the selected Gateway health
endpoint `http://127.0.0.1:8001/health` is reachable. A missing or incompatible
prerequisite SHALL fail before an observer turn. The profile SHALL not patch
configuration, fall back to memory while claiming history, accept a caller-selected
origin or the Nginx `:2026` proxy endpoint, or imply that the observer can recover a
Deep Research Run.

The public-entry prerequisite SHALL call the existing project-owned
`configure.execute_configuration` in `check` mode with only the selected profile's
validated launch environment. It SHALL accept the result only when
`runtime_config_ready` is true and `entry_status` is exactly `ready`; `unknown` and
`not_ready` are safe preflight failures. This check SHALL not invoke configuration
apply/rollback, submit credentials, or probe an authenticated Agent API. (`LCP-004`,
`LCP-005`)

Preparation SHALL use the repository root `config.yaml` as the sole current local
`config_version` baseline and require the selected profile configuration to have the
same version before backend synchronization or Harness installation. This SHALL be a
current-development consistency check only, not a backward- or forward-compatibility
policy. The static `deerflow/config.example.yaml` SHALL not select, override, or judge
the local baseline. A missing, malformed, or unequal version SHALL fail with a
redacted preparation diagnostic before commands run, without a DeerFlow upgrade,
runtime root-config fallback, or manual editable-install bypass.

For profile launch only, one exception to the normal no-host-path diagnostic rule is
permitted: the absolute owner-only path of the newly created process-scoped rotating
`stderr` capture below
`deep_research_harness/.deep-research-demo-runs/logs/`. The launcher SHALL print that
path before provider work, preserve the unchanged Gateway stack's normal `stderr`, and
disclose no other new host path. The file remains outside sandbox-mapped workspace,
Bundle directories, and profile configuration/state roots and cannot become a replay,
selection, recovery, or lifecycle surface. (`LCP-004`, `LCP-005`)

#### Scenario: Diagnostics remain redacted and authority-neutral
- **WHEN** a profile contains sentinel paths, credentials, or malformed provider
  details
- **THEN** normal diagnostics expose only safe profile facts and neither create nor
  interpret a downstream runtime authority

#### Scenario: Gateway observer claim is preflighted
- **WHEN** an operator selects a profile for the real CLI/TUI Gateway observer
- **THEN** profile check verifies JSON trace logging, durable history, public entry,
  and Gateway health before a turn, and a failed check names only the safe corrective
  action without starting an observer or creating a Run

#### Scenario: Unknown public entry is not treated as ready
- **WHEN** profile-scoped `configure.py` check returns `entry_status=unknown` or
  `not_ready`, or reports runtime configuration not ready
- **THEN** Gateway observer readiness fails before a public request without mutating
  configuration, submitting credentials, or probing an authenticated Agent API

#### Scenario: Current local configuration is the only preparation version authority
- **WHEN** the selected profile and root `config.yaml` have matching current
  `config_version` values while the static upstream example has another value
- **THEN** preparation accepts the current local configuration and does not treat the
  static example as a compatibility baseline

#### Scenario: Selected profile differs from the current local configuration
- **WHEN** the selected profile has a missing, malformed, or unequal
  `config_version` relative to the root `config.yaml`
- **THEN** preparation fails before synchronization or installation with a redacted
  diagnostic and does not upgrade DeerFlow or switch the running profile to root
  configuration

#### Scenario: Local capture path is the sole permitted host-path disclosure
- **WHEN** a valid local profile launches its Gateway process capture
- **THEN** it prints only that invocation's absolute owner-only log path under the
  declared demo-log root, while all other profile diagnostics retain their existing
  path and secret redaction rules

#### Scenario: Ephemeral profile cannot advertise durable history
- **WHEN** a profile uses memory database/history state
- **THEN** it may retain its existing ephemeral profile classification but cannot pass
  Gateway observer readiness or claim Console/run-history durability
