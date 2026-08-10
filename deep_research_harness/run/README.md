# Run

From `deep_research_harness/`, run `bash run/real-research.sh`. From this directory, run
`bash real-research.sh`. The launcher starts the standalone all-real research CLI from
any working directory. It exports one explicit selector: callers can supply
`DEERFLOW_DEMO_MODEL`, or the launcher deliberately exports its configured
`deepseek-v4-flash` policy before composing the real demo.

The launcher requires `deep_research_harness/.env` to provide `DEEPSEEK_API_KEY` and `TAVILY_API_KEY`.
Set `DEEP_RESEARCH_QUESTION` to replace the default question, or set `DEERFLOW_DEMO_MODEL` to another configured model name.

## Bounded Real-Demo Calibration

Use the direct scripted demo from `deep_research_harness/` when collecting bounded
profile-comparison evidence, so each candidate is explicit:

```bash
DEERFLOW_DEMO_MODEL=<profile> make demo-real-scripted
make demo-sessions DEMO_ARGS="inspect <bundle-id>"
```

The fixed scripted question starts a fresh Run Bundle. Inspect only the resulting
Bundle through the read-only command and compare redacted profile identity/revision,
phase, failure category, budget-stop reason, and validation codes. Repeat manually for
another explicitly selected profile; do not use the launcher policy as a hidden
calibration selector.

The resulting evidence does not qualify a model and does not select or change a
default model. It does not modify prompts, budgets, recovery, or lifecycle controls.
