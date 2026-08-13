# Stage 6 Apply Record - D-001 Rubric / Runner Terminology

> Change: `normalize-post-decision-terminology-status`
> Date: 2026-08-13
> Status: **APPLIED AND VERIFIED - ARCHIVE PENDING**

- **Authority owner:** `cognitive-evaluation-suite`; parallel case-corpus boundaries
  remain owned by `evaluation-hardening` and `hitl1-node`. The glossary and ADR 0025
  only explain those contracts.
- **Affected paths:** Exact Cognitive Evaluation Runner, Evaluation Execution Case,
  Evaluation Rubric, and short Rubric explanatory occurrences in `CONTEXT.md`; one new
  current-status/applicability postscript in ADR 0025.
- **Before:** The glossary says the Runner neither reads a quality Rubric nor decides
  cognitive quality, but does not identify the narrow deterministic identity/version
  and unique criterion-ID admission metadata. The Rubric entry says it is read only by
  upper review and not the Runner. ADR 0025 has only its historical body, which says a
  Rubric is not Runner input.
- **After:** Explain that deterministic admission may read only the Case-linked
  Rubric's identity/version and unique criterion-ID set as non-model
  case-control-integrity metadata. The Runner and subject do not interpret those IDs as
  quality. Criterion prose, weights, thresholds, evaluator guidance, cognitive result,
  model-facing quality input, execution-output quality meaning, and Runner quality
  verdicts remain excluded; the Runner reports only `completed` or `failed`. ADR 0025
  receives the same current-applicability distinction without altering historical text.
- **Reason and evidence:** CES requirement `Evaluation cases bind execution inputs` and
  its Runner requirement; Stage 4's actual disposition. The relevant required wording
  was re-read before apply.
- **Main risk:** Metadata wording could be mistaken for permission to pass or interpret
  Rubric content in execution.
- **Possible side effects:** The terms become longer and ADR readers must distinguish a
  historical categorical phrase from the narrowly scoped current postscript.
- **Risk controls / stop condition:** Every changed D-001 sentence names only
  identity/version plus unique criterion IDs and states the excluded content/judgment
  channels. Preserve ADR title/body. Stop if a sentence requires a new behavior,
  implementation assertion, or metadata beyond the named fields.
- **Verification before apply:** Fresh clean worktree and exact before-text baseline;
  the CES/EVH/HITL1 blocks and Stage 4 post-archive disposition were reviewed. The
  concept-map commit has no target overlap.
- **Verification after apply:** Exact occurrence/diff review against CES; strict
  OpenSpec, Charter, Markdown/link, whitespace, and offline deterministic gates;
  record only their stated proof limits.
- **Applied content:** Only the four allowlisted `CONTEXT.md` D-001 occurrences and
  its short Rubric explanatory section now distinguish deterministic identity/version
  and unique criterion-ID metadata from review-only content/judgment. ADR 0025 now has
  a dated current-applicability postscript; its title and historical body are unchanged.
- **Observed side effects:** **None observed within the performed documentation,
  governance, and deterministic checks.** The wording is necessarily longer, but exact
  occurrence review found no copied requirement/task list and no expanded target path.
- **Evidence bound on no observed side effect:** This does not prove reader
  interpretation, live/credentialed evaluation execution, all future paths, or a
  universal runtime absence of prohibited quality input. Stage 4's finite local result
  remains the only bounded current-path evidence.
- **Remaining mismatch / follow-up owner:** No deferred runtime gap was observed by the
  bounded Stage 4 inspection. Any later runtime divergence needs a separately
  authorized code-and-test change.
- **Authorization and date:** User authorized docs-only apply on 2026-08-13; archive
  and commit remain unauthorized.
