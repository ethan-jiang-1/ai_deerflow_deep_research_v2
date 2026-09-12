# Deep Research Documentation

This index routes human readers to one focused reference for the **Deep Research
Harness** — a runtime harness on DeerFlow that manages independently deletable Run
Bundles, not a single question-to-report pipeline. It starts after the product entry page
in [`../README.md`](../README.md). It is not a second product overview, runtime
authority, or coding-agent guide.

## Living References

Current behavior, operations, and policy. Kept in sync with the code.

| Question | Focused document |
| --- | --- |
| How do the downstream graph, checkpoint, evidence, sandbox, and public-control boundaries fit together? | [Runtime architecture](runtime-architecture.md) |
| How does one run unfold end to end (lifecycle vocabulary in order)? | [Run lifecycle walkthrough](run-lifecycle-walkthrough.md) |
| How do I run profiles, demos, diagnostics, retained sessions, and the local workbench? | [Local operations](local-operations.md) |
| How are deterministic, live, and release tests selected and interpreted? | [Testing and evaluation](testing-and-evaluation.md) |
| How are live or release defects classified and descended to deterministic regressions? | [Regression descent](regression-descent.md) |
| How do I prepare, run, and review a manually selected cognitive case? | [Cognitive Evaluation Suite](cognitive-evaluation-suite.md) |
| How do I run the local demo ladder end to end (001–004 / 010 / 020 / 030 / 031)? | [Local runbooks](runbooks/README.md) |

## Generated

Derived from the code and mechanically checked for freshness. Do not edit by hand.

- [Logical topology](deep-research-topology.md) — nodes, terminals, and semantic
  edges, rendered by `scripts/render_topology.py` and locked by
  `tests/contract/test_topology_snapshot.py`.

## Frozen Evidence

Point-in-time evidence, valid only as of its stated date and revision. Do not edit it to
track current behavior; cite it as historical proof.

- [Live evaluation baseline (2026-07-17)](evidence/live-evaluation-baseline-2026-07-17.md)
- [Release attestation (2026-07-17)](evidence/release-attestation-2026-07-17.json)

For a code or governance change, start with the application coding boundary in
[`../AGENTS.md`](../AGENTS.md), not this operational documentation set.
