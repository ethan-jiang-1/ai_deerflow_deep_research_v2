# Periodic Scenarios

This directory contains maintained deterministic, credential-free public-entry
regressions whose clean-copy environment setup is intentionally too expensive for
the rapid pull-request gate. Run them locally with
`UV_OFFLINE=1 make test-entry-environment-regression` from
`deep_research_harness/`; the `Deep Research Entry Environment Regression` workflow
runs the same target for its declared entry-environment path surface, daily, and on
manual dispatch.

All scenarios here carry the registered `periodic` marker and must not carry
`requires_llm` or `release_e2e`. They remain supported-contract evidence and are
collected by `make test-assets`; `make test`, `make verify`, fast, integration, and
workflow targets exclude them.

This is not `tests/scenarios_suspended/`: suspended scenarios are credentialed
release diagnostics with no active supported-contract execution path and require an
approved reactivation change. Periodic scenarios are maintained evidence with a
low-frequency execution path.
