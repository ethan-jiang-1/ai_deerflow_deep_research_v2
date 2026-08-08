> Implementation status (2026-07-22): `17/17` complete. **All implementation,
> local-profile evidence, and deterministic/governance verification is complete.** The
> change is ready for explicit archive; update this line and the checkboxes if follow-up
> work is added.

## 1. Contracts And Retained Observations

- [x] 1.1 Add red-before-green domain tests for frozen workbench views, bounded timeline entries, metadata-only catalog keys, unavailable projections, and sentinel redaction. (`RWB-001`, `RWB-003`, `RSV-001`, `RSV-003`)
- [x] 1.2 Implement `domain/session_workbench.py` with frozen display/catalog/artifact contracts and `@impl RWB-001` through `RWB-004` / `RSV-001` through `RSV-003`; retain no raw scope, provider, host path, binding, checkpoint, answer, diagnostic body, or arbitrary path field.
- [x] 1.3 Add red-before-green `RunSessionStore` tests for validated bounded trace reads, fixed catalog derivation, no-follow regular-file checks, absent entries, and symlink/nonregular/broader-mode rejection. (`RUS-002`, `RUS-003`, `RSV-001`, `RSV-002`)
- [x] 1.4 Extend the runtime-owned retained-session store with contained read-only timeline/catalog primitives and `@impl RUS-002` / `RUS-003`; preserve legacy inspection output and ensure contained store readers do not independently create a provider, sandbox, graph, or retained root.

## 2. Authorized Workbench Runtime

- [x] 2.1 Add red-before-green runtime tests proving each valid workbench selection calls the existing broker before contained storage, while an unknown catalog key is rejected before broker work; foreign, stale, corrupt, recipe/provider-drifted, and legacy references remain indistinguishable and do not reach contained storage after broker denial. (`RWB-001`, `RDO-004`, `RSV-003`)
- [x] 2.2 Implement `runtime/session_workbench.py` with the fixed-profile `LocalSessionWorkbench` composition and `@impl RWB-001`, `RWB-002`, and `RWB-003`; reuse broker `discover`/`open`/`status`/`resume`/`cancel` rather than constructing an envelope, host, provider, sandbox, or lifecycle action.
- [x] 2.3 Add red-before-green artifact-view tests for unknown-key rejection before broker work, valid-key broker reauthorization, fixed-key-only resolution, metadata-only output, redaction, and no additional provider/sandbox/graph behavior after broker authorization or denial. (`RSV-001`, `RSV-002`, `RSV-003`, `RDO-004`)
- [x] 2.4 Implement the cataloged artifact reader with `@impl RSV-001` through `RSV-003`, including a fixed catalog policy, contained no-follow validation, metadata-only output, and fail-closed unavailable projection.
- [x] 2.5 Add file-SQLite fresh-process lifecycle evidence showing the durable local profile can discover, select, timeline-read, and catalog-read its own session while a foreign/stale reference cannot reveal or mutate it or trigger a retained-path read after broker denial. (`RWB-001`, `RWB-003`, `RSV-003`)

## 3. Local Terminal Workbench

- [x] 3.1 Add pure reducer/presentation tests for discovery, selected session, current broker state, timeline, artifact metadata, unavailable results, and pending-input request-id handling without lifecycle inference. (`RWB-002`, `RWB-003`)
- [x] 3.2 Add the thin `agent/scripts/session_workbench.py` Textual entry and `make -C agent session-workbench` target with `@impl RWB-001` / `RWB-004`; construct only the configured local operation profile and label the surface as non-product.
- [x] 3.3 Implement terminal controls so refresh/open/status/timeline/catalog/metadata remain read-only and answer/cancel delegate only to the broker; prove raw answers never enter argv, manifest, trace, diagnostic, or artifact output. (`RWB-002`, `RWB-003`, `REC-004`)
- [x] 3.4 Add deterministic Textual integration tests for local-profile startup, selection, unavailable/failure rendering, artifact metadata navigation, stale pending response rejection, and duplicate-response/dispatch-lease behavior. (`RWB-001` through `RWB-004`, `REC-003`, `REC-004`)

## 4. Governance, Documentation, And Verification

- [x] 4.1 Register `domain/session_workbench.py`, `runtime/session_workbench.py`, the terminal entry, and focused test paths in project structure; render `agent/AGENTS.md`; add exact requirement/test-evidence claims and known-violation detector smoke coverage. (`PRS-006`, `RWB-001` through `RWB-004`, `RSV-001` through `RSV-003`)
- [x] 4.2 Update `agent/README.md`, `agent/Makefile`, and the session/workbench roadmap with local-workbench launch/use limits, metadata-only catalog policy, product-surface deferral, and the unchanged Gateway/Web boundary. (`REC-003`, `REC-004`, `RWB-004`)
- [x] 4.3 Run profile/config/doctor and durability evidence appropriate to the configured local profile, including `make -C agent profile-preflight`, the safe profile-check/doctor path, `make -C agent test-durability`, and a bounded local workbench smoke; record credentialed-provider evidence only as supplemental or a safe preflight skip.

  Evidence (2026-07-22): `profile-preflight` passed; `profile-check PROFILE=demo`
  accurately reported its ephemeral-memory state and was not used as durable proof;
  `test-durability` passed (`9 passed, 1 skipped`, deferred Postgres only); the
  fresh-process file-SQLite workbench smoke passed (`discover`/`open`/timeline/fixed
  metadata-only catalog plus foreign denial); and `session-workbench --help` exposed no
  caller-selected profile or path authority. Root `make doctor` was run and failed only
  because the existing root `config.yaml` references an unset `TAVILY_API_KEY`; this
  unrelated root configuration gap was left unchanged. No approved credentialed durable
  provider is configured, so live credentialed evidence remains a safe supplemental skip.
- [x] 4.4 Run focused deterministic tests, then `cd agent && UV_OFFLINE=1 make verify`; run strict OpenSpec plus requirement/spec/architecture checks and `git diff HEAD --check`; record baseline/final `git status --porcelain=v1 --untracked-files=all` and confirm `backend/` and `frontend/` remain untouched.

  Evidence (2026-07-22): focused workbench/store/lifecycle suite passed (`37 passed`);
  final `UV_OFFLINE=1 make verify` passed: fast `1612 passed`, integration/blocking-I/O
  `124 passed, 4 skipped` (existing real-Gateway-stack availability skips), and workflow
  `15 passed`. Strict OpenSpec validation, requirements, specs, architecture, and
  `git diff HEAD --check` all passed. The baseline recorded 21 intended changed/untracked
  Change files; final status is rechecked below before archive. `backend/` and
  `frontend/` remain untouched.
