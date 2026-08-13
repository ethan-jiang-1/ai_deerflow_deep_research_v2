# Stage 1 Apply Record - V-001 Verification Format Maintenance

> Change: `retire-v1-topology-residue`
> Type: `VERIFICATION-UNBLOCKING FORMAT-ONLY EXCEPTION`
> Status: **VERIFIED - FORMAT-ONLY EXCEPTION CLOSED**
> Date: 2026-08-13

## Adjustment V-001

- **Authority owner:** The configured Ruff formatter and the repository's existing
  `make verify` lint gate.
- **Affected path:** `deep_research_harness/tests/contract/test_selected_change_closeout.py`.
- **Before:** Ruff rejects one implicit adjacent-literal expression in
  `test_record_review_ignores_prose_containing_checkbox_marker`, even though Python
  already concatenates the two literals into one `write_text()` string.
- **After:** Let the configured Ruff formatter replace those two source literals with
  its one-line equivalent. The resulting string is exactly
  `"## Tasks\\n\\n- [ ] Real work item\\n\\nProse that mentions the `- [ ]` marker is not a task.\\n"`.
- **Reason and evidence:** `UV_OFFLINE=1 make verify` previously stopped only at this
  formatter complaint after all earlier governance, lock, and Ruff-check stages passed.
  `UV_OFFLINE=1 uv run ruff format --diff` proposes exactly this one expression rewrite.
- **Main risk:** A formatting exception could be used to smuggle in a test semantic
  change or silently broaden the documentation-only Stage 1 scope.
- **Possible side effects:** The test file becomes an additional changed path, which
  makes the Stage 1 diff no longer documentation-only in a literal sense; a future
  reader could mistake this as permission to alter closeout behavior.
- **Risk controls / stop condition:** Run only the configured formatter against the
  one named file; inspect that the diff is exactly the recorded adjacent-literal
  rewrite; run its focused test and the full gate; stop if any other file, assertion,
  fixture value, behavior, or `deerflow/` path is proposed.
- **Verification before apply:** Focused Ruff diff proves exactly one source expression
  changes; current file has no user or Stage 1 diff.
- **Verification after apply:** `UV_OFFLINE=1 uv run ruff format --check` reports the
  file already formatted; `UV_OFFLINE=1 uv run ruff check` passes; focused pytest
  reports `15 passed`; the inspected Git diff is exactly 1 insertion and 2 deletions
  joining the recorded literals. The original `make verify` session reached integration
  before its tool output handle was lost; all of its Makefile targets subsequently
  passed with recorded JUnit evidence: fast 2495, integration/blocking-I/O 241
  (4 expected skips), workflow 35.
- **Observed side effects:** The expected sole test-file formatting diff is present. No
  assertion, fixture value, behavior, `deerflow/`, dependency, or runtime side effect
  was observed within the focused checks, exact diff review, or full verification
  evidence.
- **Remaining mismatch / follow-up owner:** A-002 remains `DEFERRED-CODE-CHANGE`;
  V-001 provides no gitlink detector or closeout authority.
- **Authorization and date:** User authorization to continue, interpreted and recorded
  as V-001-specific authorization on 2026-08-13 after the exact formatter diff was
  disclosed.
