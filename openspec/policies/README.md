# OpenSpec External Policies

> scope: recurring cross-change design review guidance
> authority: guidance only; never runtime control, permission, or current-state truth
> @impl DRC-009

This directory holds a small number of OpenSpec policies whose design questions span
more than one local governance route. They guide proposal authors and reviewers. The
Deep Research Agent Charter remains the local routing home; its deterministic checker
validates declared record shape only; approved specifications, code, and tests retain
authority over behavior and current facts.

## Available Policies

| Policy | Read when | Does not create |
|---|---|---|
| [control placement](control-placement.md) | A change moves a candidate, human judgment, control fact, or deterministic admission/recovery boundary | A runtime gate, state write, permission, retry, lifecycle action, or model role |

## Boundary

These policies do not introduce a second Agent Charter or a runtime enforcement
family. They do not infer policy applicability, approve a proposal, or replace an
owning capability specification. V2 `add-cross-session-cognitive-guardrails` remains
deferred: this directory contains no guardrail runner, dossier, hook, semantic
evaluator, or cross-session workflow.
