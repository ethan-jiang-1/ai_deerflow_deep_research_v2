## 1. Boundary And Structure

- [x] 1.1 Add red contract cases that pin upstream root files as unchanged and require the resolver/tests under `agent/` while allowing profile data only beneath new `profiles/`. (`PRS-007`, `LCP-002`)
- [x] 1.2 Remove the obsolete handoff hook and old agent profile layout; register `agent/scripts/local_profiles.py`, `agent/tests/contract/test_local_profiles.py`, `profiles/README.md`, and `profiles/.gitignore`; render `agent/AGENTS.md`. (`PRS-007`)
- [x] 1.3 Add the new `profiles/` guide and ignore boundary without editing a pre-existing root ignore/documentation surface. (`LCP-001`, `LCP-003`)

## 2. Resolver And Initialization

- [x] 2.1 Write red resolver tests for safe names, project-owned containment, complete/missing/partial pairs, redaction, and root-file preservation. (`LCP-001`, `LCP-004`)
- [x] 2.2 Implement the single resolver with an explicit launcher exec seam, `profiles/<name>/` profile/state paths, documented DeerFlow environment construction, inherited skills-environment removal, and root dotenv selection-key conflict refusal. (`LCP-001`, `LCP-002`, `LCP-003`, `LCP-004`, `LCP-005`)
- [x] 2.3 Add red initialization tests for copying the repository-root pair, independent-snapshot idempotency after root changes, missing root configuration, absent root extensions, partial refusal, and no runtime/database creation. (`LCP-001`, `LCP-003`)
- [x] 2.4 Implement structural initialization with legacy-checkpointer removal and contained absolute SQLite. (`LCP-001`, `LCP-003`)

## 3. Agent Launcher Adapter

- [x] 3.1 Add red validation tests for SQLite and ephemeral-memory state classification, SQLite/path isolation, symlink/path escape rejection, no sandbox/mount isolation claim, and no mutation before a failed preflight. (`LCP-001`, `LCP-003`)
- [x] 3.2 Add safe list/check diagnostics plus red regression cases proving standard environment selection, inherited skills-environment removal, shell-like/expanding root environment refusal, accepted direct literal `export NAME=value` input, each root dotenv selector-key refusal with a keep-secrets-in-`.env` instruction, and no shell hook/source interception. (`LCP-002`, `LCP-004`, `LCP-005`)
- [x] 3.3 Update agent Make command adapters for explicit `profile-setup` through root `make install` then agent operations setup, an `agent/.venv/` preflight before `uv`, list/init/check/dev modes only, locked no-sync ordinary operation, upstream `--dev --skip-install`, dotenv conflict/invalid/unavailable preflight, and profile-agnostic upstream stop. (`LCP-002`, `LCP-005`)

## 4. Documentation And Verification

- [x] 4.1 Document the beginner `profile-setup` (standard root install plus agent operations setup) then init/check/launch workflow, root-upstream ownership boundary, the distinction between root `.env` secrets and profile configuration selection, the SQLite-versus-ephemeral-memory choice, the sandbox/mount non-guarantee, and the shared launcher logs/compatibility-directory boundary. (`LCP-002`, `LCP-003`, `LCP-004`)
- [x] 4.2 Run focused resolver/launcher/governance tests; prove upstream config upgrade affects only the selected ignored profile pair and root `Makefile`, `README*`, `.gitignore`, `scripts/`, `backend/`, and `frontend/` are unchanged. (`PRS-007`, `LCP-001`, `LCP-002`, `LCP-003`, `LCP-004`, `LCP-005`)
- [x] 4.3 Run `cd agent && UV_OFFLINE=1 make verify`, strict OpenSpec validation, and `git diff HEAD --check`; record that Docker, live-model, browser, database-server, and Docker-mount acceptance are not required. (`PRS-007`, `LCP-001`, `LCP-002`, `LCP-003`, `LCP-004`, `LCP-005`)
