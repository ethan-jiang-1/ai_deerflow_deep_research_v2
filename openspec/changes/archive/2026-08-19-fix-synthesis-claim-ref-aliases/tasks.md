# Tasks: fix-synthesis-claim-ref-aliases (BUG-059)

## 1. Claim-id alias projection (red-first)

- [x] 1.1 Add red tests in the wave2 synthesis unit test file (`deep_research_harness/tests/unit/test_wave2_synthesis.py` or the file currently owning `_evidence_aliases`/`_validate_synthesis_semantics` tests): (a) `_evidence_aliases` collects a `claim:w1_c1` id appearing as a `claim_id` key inside evidence JSON and maps it to that evidence's submission ref; (b) `_validate_synthesis_semantics` accepts a finding whose `backing_refs` cite that claim id; (c) a fabricated `claim:w9_missing` id still raises `synthesis_finding_backing_ref_invalid`. Verify with `cd deep_research_harness && UV_OFFLINE=1 .venv/bin/python -m pytest tests/unit -k "alias or claim_ref"`. (`WSN-004`)
- [x] 1.2 Implement in `deep_research_harness/src/deerflow_deep_research/graph/nodes/wave2_synthesis/node.py`: add `claim_id` to the extraction key tuple in `_evidence_aliases` (design D1). Task 1.1 turns green. (`WSN-004`)

## 2. Regression and evidence

- [x] 2.1 Full deterministic gate: `cd deep_research_harness && UV_NO_CACHE=1 make verify` stays green; confirm the diff touches only `wave2_synthesis/node.py` and tests. (`WSN-004`)
- [x] 2.2 Keep `_backlog/bugs/BUG-059-synthesis-claim-ref-alias-blindspot.md` active until the real 004 rerun passes; the rerun itself is owned by change `hard-real-auto` task 4.3. (`WSN-004`)
