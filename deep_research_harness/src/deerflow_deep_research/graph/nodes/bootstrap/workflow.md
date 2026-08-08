# bootstrap — Bind trusted bootstrap input to the research lifecycle

> Reader interface only. This file is not a runtime resource or configuration.
> Code, typed contracts, approved specifications, and tests remain the authority.
> Participation mode: deterministic control
> Commitment state: intentional controller exclusion
> Current operating mechanism: source-audited bootstrap bundle binding controller
> Primary cognitive/control program surface: trusted request and bundle validation
> Deterministic authority boundary: bootstrap handler writes validated initial state and typed route
> Current model-branch evidence: audit only; no direct branch observed

## Node Identity

Bootstrap is intentionally not a cognitive or human-decision seam: it binds trusted
input before any research program can run.

## From Symptoms

Open `node.py::build_real` and the bootstrap bundle/runtime binding for missing,
mismatched, or unsafe initial state; use `tests/graph/test_bootstrap_node.py` first.

## Three Cross-Module Facts

1. The real factory consumes the trusted bootstrap bundle; fake is zero-I/O fixture behavior.
2. Validation, initial state writes, and lifecycle transitions remain deterministic.
3. A prompt/capability edit cannot repair a trusted-binding or lifecycle symptom.

## Route Facts

The handler returns typed bootstrap outcomes consumed by the graph topology.

## Evaluation and Verification Order

Run bootstrap-focused tests, then topology/implementation tests if the typed outcome
reaches an unexpected graph target.
