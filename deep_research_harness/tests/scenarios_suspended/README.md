# Suspended Scenarios

`test_evh_024_release_acceptance.py` is retained diagnostic material for the credentialed
full-real EVH-024 selector. It is collectable by pytest under this suspended directory
but is excluded from every deterministic and live lane by its declared
`requires_llm`/`release_e2e` markers, and has no Make or CI execution path.

Do not reactivate or run it ad hoc. Follow
`_backlog/_done/_suspended_plans/evh-024-release-acceptance-diagnosis.md`: a new
approved OpenSpec change must first establish a deterministic diagnostic loop that
completes in less than ten seconds before any credentialed execution is authorized.
