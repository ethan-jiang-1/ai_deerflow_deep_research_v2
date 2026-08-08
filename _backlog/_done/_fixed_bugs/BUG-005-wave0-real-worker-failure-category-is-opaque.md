# BUG-005: Real Wave0 worker failure remains category-opaque after safe observability

> Severity: P1 | Found: 2026-07-22 | Status: Fixed in code; live root cause remains unconfirmed

## Evidence

Credentialed scripted real reproduction retained this safe run:

```text
run: r_e8w-cpL9Juk5Q2JEM7Dsv47hZefpnbRaxYtY9MxN6aI
bundle: 202607221650_r_e8w-cpL9Juk5Q2JEM7Dsv47hZefpnbRaxYtY9MxN6aI
summary: blocked@wave0
summary diagnostic: diag_019a959fa066d7fd07183ec7
journal: complete, sequence 1-34
```

The safe timeline proves one `g0_wave0_w0000` work item exhausted three attempts:

- attempts `a00` and `a01` each completed two model/tool boundaries, then emitted
  `attempt: worker.failed` and `exhaustion: work.failed`;
- attempt `a02` emitted `model_tool.started`, then `attempt: worker.failed` and
  `exhaustion: work.failed` without a matching completion event;
- terminal lifecycle is `blocked@wave0` with `research.blocked`.

No raw exception, prompt, provider/model/tool body, URL, path, or credential was
retained. This is correct redaction behavior, but the current closed category does not
distinguish provider failure, tool failure, structured-output parse failure, or source
validation failure.

## Scope

The retained summary/event journal and `inspect` behavior are working for this run; do
not reopen BUG-002 for presentation work. The remaining defect is the Wave0 worker's
safe failure classification at the node-agent/result-parser boundary.

## Resolution

`classify-deep-research-wave0-worker-failures` now preserves the redaction boundary
while recording closed per-attempt categories, an honest exhausted-work aggregate, and
the same diagnosis through retained inspection and terminal presentation. Deterministic
coverage distinguishes node-agent/tool, structured-output, and typed validation paths.

This does **not** identify a provider or Tavily root cause for the captured run. A new
credentialed reproduction is required before opening a provider/tool remediation.
