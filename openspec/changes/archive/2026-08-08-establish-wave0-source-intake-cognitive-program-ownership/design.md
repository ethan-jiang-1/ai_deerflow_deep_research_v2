## Context

See `proposal.md` for motivation and `specs/wave0-node/spec.md` for the required
behavior. Wave0 already has two required local capability bindings: a required-tool
source-intake worker and a forbidden-tool repairer. The final renderer loads those
resources, but `graph/nodes/wave0/prompts.py` still contains independently sufficient
method text for retrieval, source judgment, untrusted data, limitations, and repair.

The real worker pipeline is deliberately layered:

```text
trusted topic assignment + runtime capability method + closed output contract
                              |
                              v
                    runtime-enforced permitted tools
                              |
                              v
                  untrusted worker candidate / observations
                              |
                  parser -> artifact writer -> submit validator -> ledger
                              |
                     work-unit controller / gate / route
```

Only the upper cognitive-method layer changes. The parser, writer, validator, ledger,
controller, gate, and graph remain distinct deterministic owners.

## Goals / Non-Goals

**Goals:**

- Make each production-loaded Wave0 capability resource sufficient to guide its one
  bounded cognitive task without relying on duplicate prompt-builder procedure.
- Preserve trusted assignment versus untrusted retrieved/draft data boundaries, the
  initial worker's runtime-enforced tool posture, and the repairer's zero-tool posture.
- Establish versioned deterministic evidence for actual resource loading, bounded
  candidate handoff, repair placement, and source-admission non-bypassability.

**Non-Goals:**

- Change `WorkSpec`, worker/result schemas, result contracts, URL/content validation,
  artifact layout, ledger protocol, source floor, retry/gate policy, or graph edges.
- Allow Markdown to choose a configured tool, write files, admit a source, or own
  recovery, lifecycle, or source-quality truth.
- Claim live web/model source judgment quality from fake-capability or deterministic
  cases, or modify Wave1, synthesis, final delivery, `backend/`, or `frontend/`.

## Decisions

### 1. Two local resources are the only reusable cognitive-method owners

Expand `wave0-authoritative-source-intake.md` into the complete bounded method:
interpret the trusted topic assignment as scope, use only available permitted
retrieval, keep retrieved material untrusted, select independent candidate metadata,
record shortfall honestly, self-check candidate/limitation boundaries, and finish with
one closed candidate. Expand `wave0-source-intake-repair.md` into the corresponding
one-repair method: preserve assignment scope, reformat only retained untrusted data,
avoid all evidence invention, self-check the closed candidate, and finish without a
tool.

`prompts.py` will project only per-invocation assignment/output data, bounds, the
closed repair category, and delimited untrusted data. It will not retain a second
description sufficient to determine retrieval judgment, source independence,
uncertainty method, or repair method.

Alternative considered: retain detailed Python prose and use Markdown as a short
policy supplement. Rejected because the production method would have two owners and
the resource version/digest could not identify the actual cognitive procedure.

### 2. Tool authority remains outside the capability

The initial resource can direct the model to use at least one tool that the runtime
makes available, but it cannot name an effective configured subset, grant a tool,
extend the call budget, or choose a filesystem root. `ExecutionPolicy` and the
node-agent bridge remain the enforcement point. The repair resource stays forbidden
from tool use; its input is the bounded observation projection already captured by the
initial attempt.

Alternative considered: encode the tool allowlist or retrieval policy in Markdown as
the operative authority. Rejected because a static capability cannot enforce operator
configuration, sandbox containment, cancellation, or the existing 1--3 call bound.

### 3. Candidate admission and recovery retain their current split

Initial JSON/parser failure is the only event that can enter the existing one-repair
path. The repaired output re-enters the same parser. A post-candidate artifact or
source validation failure remains a submit/controller fact and must not create a
repair invocation. Provider/tool/cancellation failures remain normalized by the
runtime and consumed by the existing work-unit controller.

Alternative considered: let repair see validation codes or source-floor feedback so it
can improve a candidate. Rejected because that makes the repairer a second source
admission/retry controller and risks feeding ledger/lifecycle facts into model control.

### 4. Add a closed Wave0 cognitive-program corpus beside the existing smoke

Add a `wave0-cognitive-program-v1` control suite whose typed `wave0_cognitive_program`
fixture has exact closed case kinds and runtime controls that digest both Wave0
resources and the existing worker schema sources. Its cases cover normal bounded
retrieval handoff, adversarial retrieved instruction, retrieval shortfall, malformed
initial candidate/one repair, and post-candidate validation rejection. Its three
runtime-control names are `source_intake_capability_digest`,
`source_intake_repair_capability_digest`, and `worker_schema_digest`. Each case binds
capability ids, assignment fragments, forbidden effects, and rubric criteria.

The minimal `domain/evaluation.py` / `runtime/evaluation/` extension validates this
fixture, its exact runtime controls, its rubric bindings, and a registered production
scenario subject with fresh scenario dependencies. The deterministic subject uses the
real Wave0 node/controller and real runtime bridge with scripted model/tool adapters.
It proves the production handoff and ownership boundary without invoking a provider or
web API. The existing `test_adversarial_worker_path.py` bridge/ledger/gate seam remains
the direct proof for hostile retrieved text; the new corpus records that scenario under
the same boundary rather than treating an isolated fake result as injection evidence.
The corpus is deliberately absent from the selected-live allowlist, so it
cannot receive a credentialed-live evidence layer. Existing credentialed live
`wave0-worker-v1` evidence remains separate and can report only the evidence it
actually obtained.

Alternative considered: extend the existing one-case Wave0 smoke. Rejected because it
cannot express repair placement, adversarial input, and post-candidate validation as
separate controls, and its `model`/`web` requirements make it unsuitable as the zero-API
regression source.

## Risks / Trade-offs

- [Capability text becomes verbose or repeats output schema] -> Keep schemas, limits,
  delimiters, parsing, and runtime configuration in Python; test that the prompt
  projection contains bounded data rather than a second cognitive procedure.
- [Markdown directs a wider retrieval posture than runtime grants] -> Assert the exact
  resource posture against the existing runtime policy and use a no-permitted-tool
  scripted failure path.
- [Corpus fixture proves only its fake helper] -> Add the minimal closed evaluator
  contract and route every deterministic scenario through the registered production
  Wave0 node subject with fresh dependencies; assert controller/ledger effects, not
  just a rendered string.
- [A repair regression accidentally changes submission recovery] -> Preserve and run
  the post-candidate validation test that observes one initial request and no repair.
- [Live evidence is misreported as deterministic quality] -> Carry existing evidence
  layer/availability semantics forward and reject this corpus at selected-live
  admission; no provider call is part of this change's required verification.

## Migration Plan

1. Add red renderer/projection and real-worker boundary regressions, then expand the
   two capability resources and narrow the prompt builders until they pass.
2. Register and validate the closed Wave0 corpus and run its scripted production-node
   subject with the real bridge and scripted external model/tool adapters.
3. Run focused Wave0/resource/evaluation tests, then the harness deterministic gate
   and strict OpenSpec validation before archive.
4. Rollback is a normal code revert: no state migration, persistent-schema change,
   ledger rewrite, or external API change is introduced.
