# Stage 1 Apply Record - C-001 Real Upstream Topology

> Change: `retire-v1-topology-residue`
> Status: **VERIFIED - A-002 REMAINS DEFERRED**
> Apply-time repository HEAD: `362962a167ca80eb93f08414aa920455732303c6`
> Date: 2026-08-12

## Adjustment C-001

- **Authority owner:** Current topology/execution-route documentation in
  `openspec/config.yaml`, `deep_research_harness/AGENTS.md`, and
  `openspec/agent-charter/charter.md`.
- **Affected paths:** The three authority documents above. The README path correction
  is separately owned by C-003.
- **Before:** Those three documents describe root `backend/` and `frontend/` as the
  DeerFlow upstream mirror/boundary, although the repository contains an upstream
  `deerflow/` gitlink.
- **After:** `deep_research_harness/` is named as the downstream
  product and `deerflow/` as the leveraged upstream gitlink; ordinary downstream work
  neither modifies nor source-browses it.
- **Reason and evidence:** `git ls-files --stage deerflow` records mode `160000` at
  `66b9e7f21212490cf92fafac137542b9deb06615`; `git submodule status -- deerflow`
  reports the same gitlink. Root and nested `--porcelain=v1 --untracked-files=all`
  status were empty at baseline.
- **Main risk:** A textual cleanup could remove a valid dependency, host-interface,
  domain, or legacy-root guard occurrence.
- **Possible side effects:** Readers might infer permission to browse DeerFlow source,
  believe manual evidence is an automatic detector, or receive conflicting answers if
  only part of the explanatory authority changes.
- **Risk controls / stop condition:** Edit only the three target claims atomically;
  retain every non-target occurrence classified below; state both the no-source-browse
  boundary and A-002's deferred detector status. Stop if a code, test, main-spec,
  registry, manifest/TOML, governance executable, or `deerflow/` edit is needed.
- **Verification before apply:** Git metadata listed above; semantic occurrence review
  below; one active OpenSpec change; no baseline worktree edits.
- **Verification after apply:** Scoped diff contains only the approved C-001/C-002
  authority edits plus authorized V-001 format maintenance. `openspec validate
  retire-v1-topology-residue --strict`, `openspec doctor --json`,
  `python3 openspec/governance/check_agent_charter.py .`, `git diff --check`, and all
  local target-document links passed. The exact `make verify` session reached its
  integration stage before the tool output handle was lost; each Makefile test target
  then passed independently: fast 2495, integration/blocking-I/O 241 (4 expected
  skips), workflow 35.
- **Observed side effects:** No runtime, dependency, gitlink, or nested-worktree side
  effect observed within the scoped diff, static checks, or complete Makefile-equivalent
  test evidence. V-001 adds its separately authorized format-only test-file diff.
- **Remaining mismatch / follow-up owner:** A-002 automatic gitlink detector remains
  `DEFERRED-CODE-CHANGE`; it is not owned by this documentation-only change.
- **Authorization and date:** User authorized Stage 1 apply on 2026-08-12.

## Active Non-Archive Occurrence Classification

This is a semantic review, not a token-count target. It excludes archived changes,
the active change artifacts, lockfile entries, and all `deerflow/` content. No listed
retained occurrence is an assertion that root `backend/` or `frontend/` is the current
DeerFlow mirror.

| Path | Term | Classification | Apply disposition |
| --- | --- | --- | --- |
| `deep_research_harness/README.md:56` | `backend` | target obsolete sibling dependency path | C-003 target |
| `deep_research_harness/pyproject.toml:34` | `backend` | retained domain/tool term (`build-backend`) | retain, frozen TOML |
| `deep_research_harness/pyproject.toml:65` | `backend` | retained `deerflow/backend/...` dependency path | retain, frozen TOML |
| `deep_research_harness/docs/local-operations.md:83` | `backend` | retained persistence configuration field (`database.backend`) | retain, outside C-001 allowlist |
| `deep_research_harness/AGENTS.md:5` | `backend` | target root-mirror claim | C-001 target |
| `deep_research_harness/AGENTS.md:5` | `frontend` | target root-mirror claim | C-001 target |
| `openspec/governance/req-registry.yaml:435` | `backend` | retained legacy-root negative guard | retain, frozen registry |
| `openspec/governance/req-registry.yaml:435` | `frontend` | retained legacy-root negative guard | retain, frozen registry |
| `openspec/governance/req-registry.yaml:447` | `backend` | retained legacy-root negative guard | retain, frozen registry |
| `openspec/governance/req-registry.yaml:447` | `frontend` | retained legacy-root negative guard | retain, frozen registry |
| `deep_research_harness/docker/docker-compose.deep-research.yaml:12` | `backend` | retained host-interface path (`backend/Dockerfile`) | retain, frozen deployment config |
| `deep_research_harness/docker/docker-compose.deep-research.yaml:33` | `backend` | retained host-interface working directory | retain, frozen deployment config |
| `openspec/governance/project-structure.toml:16` | `backend` | retained legacy-root negative guard | retain, frozen TOML |
| `openspec/governance/project-structure.toml:16` | `frontend` | retained legacy-root negative guard | retain, frozen TOML |
| `openspec/agent-charter/charter.md:10` | `backend` | target root-boundary description | C-001 target |
| `openspec/agent-charter/charter.md:10` | `frontend` | target root-boundary description | C-001 target |
| `openspec/config.yaml:6` | `backend` | target root-mirror claim | C-001 target |
| `openspec/config.yaml:7` | `frontend` | target root-mirror claim | C-001 target |
| `openspec/config.yaml:63` | `backend` | target obsolete root-boundary proposal rule | C-002 target |
| `openspec/config.yaml:63` | `frontend` | target obsolete root-boundary proposal rule | C-002 target |
| `openspec/config.yaml:82` | `backend` | target obsolete root-cleanliness closeout rule | C-002 target |
| `openspec/config.yaml:82` | `frontend` | target obsolete root-cleanliness closeout rule | C-002 target |
| `openspec/policies/local-context.md:50` | `backend` | retained legacy-root negative guard | retain, outside C-001 allowlist |
| `openspec/policies/local-context.md:50` | `frontend` | retained legacy-root negative guard | retain, outside C-001 allowlist |
| `openspec/specs/deep-research-agent-charter/spec.md:72` | `backend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/deep-research-agent-charter/spec.md:72` | `frontend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/deployment-configuration/spec.md:21` | `backend` | retained domain term (installation environment) | retain, main spec |
| `openspec/specs/deployment-configuration/spec.md:30` | `backend` | retained domain term (caller-quiesced environment) | retain, main spec |
| `openspec/specs/deployment-configuration/spec.md:38` | `backend` | retained host-interface shadow-path term | retain, main spec |
| `openspec/specs/deployment-configuration/spec.md:39` | `backend` | retained host-interface shadow-path term | retain, main spec |
| `openspec/specs/deployment-configuration/spec.md:53` | `backend` | retained host-interface shadow-path term | retain, main spec |
| `openspec/specs/deployment-configuration/spec.md:397` | `backend` | retained persistence domain term | retain, main spec |
| `openspec/specs/deployment-configuration/spec.md:434` | `backend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/deployment-configuration/spec.md:434` | `frontend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/local-configuration-profiles/spec.md:25` | `backend` | retained persistence domain term | retain, main spec |
| `openspec/specs/local-configuration-profiles/spec.md:47` | `backend` | retained persistence domain term | retain, main spec |
| `openspec/specs/local-configuration-profiles/spec.md:159` | `backend` | retained host-interface compatibility path | retain, main spec |
| `openspec/specs/runtime-integration/spec.md:36` | `backend` | retained persistence domain term | retain, main spec |
| `openspec/specs/runtime-integration/spec.md:123` | `backend` | retained persistence domain term | retain, main spec |
| `openspec/specs/project-structure/spec.md:85` | `backend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/project-structure/spec.md:85` | `frontend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/project-structure/spec.md:127` | `backend` | retained structural forbidden-root term | retain, main spec |
| `openspec/specs/project-structure/spec.md:127` | `frontend` | retained structural forbidden-root term | retain, main spec |
| `openspec/specs/project-structure/spec.md:136` | `backend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/project-structure/spec.md:136` | `frontend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/project-structure/spec.md:140` | `backend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/project-structure/spec.md:140` | `frontend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/project-structure/spec.md:144` | `backend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/project-structure/spec.md:144` | `frontend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/project-structure/spec.md:357` | `backend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/project-structure/spec.md:358` | `frontend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/project-structure/spec.md:405` | `backend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/project-structure/spec.md:405` | `frontend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/project-structure/spec.md:426` | `backend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/project-structure/spec.md:426` | `frontend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/demo-pipeline/spec.md:9` | `backend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/demo-pipeline/spec.md:9` | `frontend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/demo-pipeline/spec.md:181` | `backend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/demo-pipeline/spec.md:181` | `frontend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/hitl1-node/spec.md:17` | `backend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/hitl1-node/spec.md:17` | `frontend` | retained legacy-root negative guard | retain, main spec |
| `openspec/specs/evaluation-hardening/spec.md:89` | `backend` | retained repository-root boundary check term | retain, main spec |
| `openspec/specs/evaluation-hardening/spec.md:89` | `frontend` | retained repository-root boundary check term | retain, main spec |
