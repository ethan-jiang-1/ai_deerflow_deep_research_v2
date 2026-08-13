# Stage 4 Apply - A-003 Full Deterministic Verification

> Change: `reconcile-evaluation-rubric-authority`
> Date: 2026-08-13
> Task: 4.2
> Status: **PASSED WITH EXPECTED SKIPS AND STATED EVIDENCE BOUNDARY**

Command:

```bash
cd deep_research_harness && UV_OFFLINE=1 make verify
```

Result: exit status `0`.

| Verification layer | Result | Notes |
| --- | --- | --- |
| Pre-test governance and static checks | Passed. | Project requirement/spec/architecture/Charter checks, `uv lock --check`, Ruff check/format, test-asset coverage, and requirement-to-test coverage all passed. |
| Fast deterministic suite | `2495 passed, 3 deselected`. | Two Pydantic deprecation warnings were emitted. |
| Integration and blocking-I/O suite | `237 passed, 4 skipped, 32 deselected`. | The four skips are `tests/integration/test_gateway_identity.py` cases whose real Gateway app stack is unavailable. Sixteen Pydantic serializer warnings were emitted. |
| Workflow suite | `35 passed, 2785 deselected`. | Forty-two Pydantic serializer warnings were emitted. |

The command ran offline and made no source change. It establishes that the repository's
configured deterministic gate passed in this environment, subject to the stated Gateway
absence and non-failing Pydantic warnings. It does **not** independently prove that the
three synced requirements are semantically compatible, that a non-Wave2 model handoff
has been observed, or that live/credentialed behavior excludes Rubric-derived quality
semantics. Those remain bounded by the manual handoff evidence recorded in
`01-a003-handoff-inspection-and-focused-evidence.md` and the required/current
disposition in `04-a003-synced-required-current-disposition.md`.
