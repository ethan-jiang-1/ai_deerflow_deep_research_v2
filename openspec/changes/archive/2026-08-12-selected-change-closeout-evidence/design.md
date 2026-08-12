# Design — Selected Change Closeout Evidence Repair

## Context

See proposal.md — Why for the motivation. The guardrail
`openspec/guardrails/selected_change_closeout.py` enforces a bounded, deterministic,
non-authoritative evidence boundary (SCC-001/002/003). Three defects let the command
overstep that boundary: output containment, unchecked-task parsing, and the caller
contract in `guardrails/README.md`.

The change is behavior-level for SCC-002 (containment), so it must carry a delta spec,
not `skip_specs`.

## Goals / Non-Goals

**Goals:**

- Make a persisted review output resolvable only inside the change's dedicated
  `guardrail-evidence/` subdirectory, so change artifacts (`tasks.md`, `proposal.md`,
  `design.md`) can never be the write target.
- Parse only real Markdown unchecked task lines for `review-required` references.
- State the caller contract precisely in `guardrails/README.md`: examples assume the
  planning home as `cwd`, and domain rejections are stdout JSON `result` values with
  exit code 0 — callers must parse `result`, not the shell exit code.

**Non-Goals:**

- Change the attestation JSON schema, the disposition set
  (`review-required` / `inconclusive`), or the boundary/evidence semantics.
- Change exit codes for `missing-boundary` / `invalid-review`: the process keeps
  returning 0 for these domain rejections; the fix is documentation, not a new
  exit-code contract.
- Touch runtime, graph, model, provider, or `deerflow/` behavior.

## Decisions

### 1. Restrict persisted output to a dedicated evidence directory

`_validate_review` currently rejects an output only when it is not
`is_relative_to(change_root)`. That still permits writing a review record over
`tasks.md`, `proposal.md`, or `design.md`, which the "SHALL NOT rewrite tasks"
boundary forbids. The fix defines `evidence_root = change_root / "guardrail-evidence"`
and rejects any resolved output not `is_relative_to(evidence_root)`, with a new
`invalid-review` condition `output-path-outside-evidence`.

**Alternatives considered:**

- Rejecting only the known artifact filenames was rejected as brittle: it would need
  an ever-growing denylist instead of one structural rule.
- Requiring output under the change root plus "not an artifact" was rejected because
  it re-introduces filename special-casing.

### 2. Parse only true Markdown unchecked task lines

`_unchecked_task_labels` currently accepts any line containing the substring
`- [ ]`. A prose line such as "note the `- [ ]` marker" would become a "task label".
The fix anchors the match to a Markdown list-item unchecked task: a line beginning
(optionally indented) with `-`, `*`, or `+`, then ` [ ] `, then non-empty label. A
compiled regex `^\s*(?:[-*+])\s+\[ \]\s+(.+?)\s*$` yields the exact label.

**Alternatives considered:**

- Keeping the substring test was rejected because it cannot distinguish a real task
  item from prose that happens to contain the marker.

### 3. Document the caller contract (exit code 0)

`missing-boundary` and `invalid-review` are printed as stdout JSON `result` values and
the process returns 0 for both operations. This is intentional: the guardrail is an
evidence helper, and a CLI caller must inspect `result`, never the shell exit code, to
learn whether evidence was established. `guardrails/README.md` is updated to say this
explicitly and to present `verify-boundary` / `record-review` examples from the
planning home as `cwd`, with a note that subdirectory callers must resolve the script
and output paths themselves.

**Alternatives considered:**

- Changing `main()` to exit non-zero on domain rejection was considered and rejected:
  it would silently break the deterministic fixtures' `returncode == 0` contract and
  is a larger behavior change than the reviewed plan asks for. The plan explicitly
  scopes this to documentation.

## Risks / Trade-offs

- [Tightening containment breaks a caller that wrote evidence outside
  `guardrail-evidence/`] → The README and fixtures now use only
  `guardrail-evidence/` paths; a clear `output-path-outside-evidence` condition
  explains the rejection.
- [The stricter task-line regex drops a legitimately formatted task] → The regex
  accepts the standard `- [ ] label` and its `*`/`+` variants; labels are stripped and
  must still exactly match `tasks.md` unchecked labels.
- [Callers still rely on exit code] → README states the exit-code-0 contract twice and
  the fixture asserts `result` values, making the parsing requirement explicit.

## Migration Plan

No data migration or runtime rollback. Apply the delta to the
`selected-change-closeout-evidence` spec, update the code and fixtures together, then
run the focused contract test and the governance gates before archive.

## Open Questions

None. The exit-code decision and containment rule are resolved here and in the spec.
