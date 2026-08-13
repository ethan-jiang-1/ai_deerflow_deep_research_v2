# Stage 5 Apply - A-004 Full Deterministic Verification

> Change: `reconcile-post-loss-diagnostic-authority`  
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
| Pre-test governance and static checks | Passed. | Project requirement/spec/architecture/Charter checks, `uv lock --check`, Ruff check/format, test-asset coverage, and requirement-to-test coverage all passed. Test assets report 2,771 deterministic tests: fast 2,495, integration 241, workflow 35, live 49. |
| Fast deterministic suite | `2495 passed, 3 deselected`. | Two Pydantic deprecation warnings were emitted. |
| Integration and blocking-I/O suite | `237 passed, 4 skipped, 32 deselected`. | The four skips are `tests/integration/test_gateway_identity.py` cases because the real Gateway app stack is unavailable. Sixteen Pydantic serializer warnings were emitted. |
| Workflow suite | `35 passed, 2785 deselected`. | Forty-two Pydantic serializer warnings were emitted. |

The command ran offline and introduced no source change. It establishes that the
configured deterministic gate passed in this environment, subject to the unavailable
Gateway stack and non-failing Pydantic warnings. It does **not** prove live or
credentialed behavior, physical erasure, absence of residual bytes, every uninspected
or future path, or semantic compatibility beyond the bounded terminal/publication and
inspection evidence in `01-a004-local-conformance-inspection-and-focused-evidence.md`
and `03-a004-synced-required-current-disposition.md`.
