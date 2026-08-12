# Stage 1 Apply Record - C-003 Editable Harness Path

> Change: `retire-v1-topology-residue`
> Status: **VERIFIED**
> Apply-time repository HEAD: `362962a167ca80eb93f08414aa920455732303c6`
> Date: 2026-08-12

## Adjustment C-003

- **Authority owner:** `deep_research_harness/README.md` Quick Start requirements
  text.
- **Affected paths:** `deep_research_harness/README.md` only.
- **Before:** The repository-root Quick Start named the nonexistent sibling path
  `../backend/packages/harness`.
- **After:** It names `../deerflow/backend/packages/harness`, matching the current
  repository topology while retaining the existing repository-root command context.
- **Reason and evidence:** The directory exists. `deep_research_harness/pyproject.toml`
  has `deerflow-harness = { path = "../deerflow/backend/packages/harness", editable =
  true }`; `deep_research_harness/uv.lock` records the same editable source.
- **Main risk:** A path-only correction could still be unusable if its command context
  differs, or it could accidentally imply a new installation route.
- **Possible side effects:** Environments still using a V1 external `../backend/`
  layout no longer match the documented support path. The valid `backend` component of
  the new gitlink-relative path must not be mistaken for residue in later cleanup.
- **Risk controls / stop condition:** Preserve the nearby wording that commands run
  from the repository root; change no dependency metadata or lockfile; stop if the
  README, pyproject, and lockfile disagree.
- **Verification before apply:** The README's existing Quick Start says to run from the
  repository root. The target directory exists, while both dependency authorities name
  the corrected editable path.
- **Verification after apply:** README text was compared with the unchanged pyproject
  and lockfile entries, all of which name `../deerflow/backend/packages/harness`.
  The local target directory exists. Changed-document link inspection, strict
  OpenSpec/doctor/Charter checks, `git diff --check`, and the Makefile-equivalent full
  verification evidence all passed. No metadata file was changed.
- **Observed side effects:** No runtime behavior or dependency resolution changed. No
  documentation side effect was observed in the direct path comparison or verification
  evidence.
- **Remaining mismatch / follow-up owner:** None within C-003's documentation scope.
  A V1-layout environment is outside the current checkout's supported topology.
- **Authorization and date:** User authorized Stage 1 apply on 2026-08-12.
