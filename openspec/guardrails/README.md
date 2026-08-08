# Selected Change Closeout Guardrail

`selected_change_closeout.py` records limited, local evidence for an explicitly
declared selected OpenSpec change. It is a standard-library command, not an OpenSpec
operation hook, archive wrapper, semantic reviewer, task writer, or runtime control.

## JSON v1 Contract

Both operations require an attestation JSON file with non-empty fields:

```json
{
  "change_name": "example-change",
  "repository_identity": "/absolute/canonical/repository/root",
  "base_commit": "<commit>",
  "head_commit": "<commit>"
}
```

Run commands from the planning home or a directory below it:

```sh
python3 openspec/guardrails/selected_change_closeout.py verify-boundary \
  --attestation /path/to/attestation.json
```

`verify-boundary` resolves an active change, checks that the declared repository is
the current repository, validates the committed `base..head` ancestry, requires
`HEAD == head`, and requires a clean worktree. A success prints a
`boundary-verified` receipt with exact resolved commits, range, changed-path count,
and SHA-256 of `git diff --binary base head`. It writes nothing. A rejected request
prints `missing-boundary` with a closed condition and no diff or coverage claim.

To retain a local review record, provide the attestation again, a review payload, and
an explicit output below the selected active change root:

```sh
python3 openspec/guardrails/selected_change_closeout.py record-review \
  --attestation /path/to/attestation.json \
  --review /path/to/review.json \
  --output openspec/changes/example-change/guardrail-evidence/review.json
```

The review payload allows only these dispositions:

```json
{
  "disposition": "review-required",
  "task_references": ["Exact unchecked task label"]
}
```

`review-required` references must exactly match current unchecked labels in the
selected change's `tasks.md`. Alternatively, an evidence-limited record is:

```json
{
  "disposition": "inconclusive",
  "evidence_limitation": "A concrete non-empty limitation."
}
```

`record-review` validates the payload and output containment, then re-verifies the
attestation immediately before its only write. It never edits `tasks.md`, invokes or
blocks native `openspec archive`, infers an undeclared worktree boundary, or emits an
approval, clearance, or semantic-pass status. A later session must issue a new
attestation verification; an earlier receipt is inspection evidence only.
