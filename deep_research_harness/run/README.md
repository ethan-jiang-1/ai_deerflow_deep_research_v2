# Run

From `deep_research_harness/`, run `bash run/real-research.sh`. From this directory, run
`bash real-research.sh`. The launcher starts the standalone all-real research CLI from
any working directory.
It defaults to the configured `deepseek-v4-flash` model and a bounded search-provider comparison.

The launcher requires `deep_research_harness/.env` to provide `DEEPSEEK_API_KEY` and `TAVILY_API_KEY`.
Set `DEEP_RESEARCH_QUESTION` to replace the default question, or set `DEERFLOW_DEMO_MODEL` to another configured model name.
