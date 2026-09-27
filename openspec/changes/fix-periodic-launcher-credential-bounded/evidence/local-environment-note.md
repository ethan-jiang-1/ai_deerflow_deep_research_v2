# Local environment note — why the fixed scenario is verified on CI, not here

Seven probes on 2026-09-28, each replicating the scenario's launcher stage in
a fresh copied project (install 2s, hermetic config, empty test-owned `.env`,
credential-scrubbed child environment):

| probe | result |
| --- | --- |
| full test (original, pre-fix) | subprocess timeout at 180s |
| full test (Option A, fake creds) | completed; readiness ready; real model call → HTTP 401 (this measured evidence rejected Option A) |
| launcher, 60s, buffered | timeout, stdout empty (block-buffered loss), stderr carried the app's logger line — the app runs |
| launcher, 60s, unbuffered | readiness reported READY, run proceeded, hung waiting on the lifecycle |
| launcher, env dumped at exec point | launcher env contains ONLY the selector (zero credentials); timeout reproduced |
| launcher, readiness instrumented in the copy | timeout with no output at all |
| launcher, exact repeat of the READY probe | timeout with no output at all — not even the banner |

The chain hangs at four different points across identical runs; process
inspection is blocked in this sandbox (`ps: Operation not permitted`); this
environment has a known history of sandbox denials on shared caches
(`~/.cache/uv` EPERM, BUG-032). One run reaching "ready" with a
credential-free environment contradicts the resolver's code path and could
not be reproduced — attributed to the same non-deterministic mediation.

What IS verified locally: the file's sibling scenario
(`test_missing_or_incomplete_entry_environment_stops_before_an_adapter`)
passes in 19s; lint and format pass on the fix; the full verify gate (which
excludes the periodic lane by design) passes. The fixed assertions match the
CI-proven not-ready output byte for byte (CI run 36354099368 logs show
`尚未找到可用的模型配置` with the remediation guidance, exactly what the
scenario now asserts).

Verdict: local green for this scenario is **UNVERIFIABLE under this sandbox**;
the change's acceptance is the entry-environment CI workflow's first green
run (task 3.4).
