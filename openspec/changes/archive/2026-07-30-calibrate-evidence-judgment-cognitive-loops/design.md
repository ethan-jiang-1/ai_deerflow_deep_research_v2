## Context

Wave2 already turns graph-assigned accepted evidence into a zero-tool `SynthesisResult`, then a
deterministic validator/materializer/preview/gate pipeline decides persistence and searchable-gap
routing. Targeted evidence consumes only the gate-owned gap-id projection: its worker has exactly
one retrieval, while its repair and two critics are zero-tool candidate paths with existing
validator, controller, materializer, ledger, and convergence-gate owners. See `proposal.md` for
motivation and the three delta specifications for the required observable behavior.

The prior two calibration changes establish a typed optional evidence-v1 rubric result and two
separate twelve-case corpus indexes. This change must preserve those identities and extend report
resolution as a closed three-corpus union; a deterministic fixture is conformance evidence, never
evidence-judgment quality evidence.

## Goals / Non-Goals

**Goals:**

- Make the six existing Wave2/targeted branch policies and their bounded feedback explicit and
  independently reviewable.
- Add deterministic composition/non-admission proof and a selected, branch-appropriate live
  judgment runner for a third twelve-case corpus.
- Preserve the existing deterministic authority and recovery boundaries end to end.

**Non-Goals:**

- No new model branch, tool, capability identifier, provider configuration, graph topology, or
  production retry/convergence rule.
- No change to evidence or artifact schemas, accepted-record semantics, checkpoint fields, ledger
  mutation, gate predicates, or executable routes.
- No live execution in default verification and no alteration of the previous calibration corpora or
  canonical canaries.

## Decisions

### 1. Calibrate all six existing policy surfaces without granting candidate authority

The implementation will revise only the two Wave2 and four targeted capability Markdown bodies and
their prompt builders. Wave2 will express supported finding/relation criteria, uncertainty, honest
gaps, and candidate-gap versus deterministic projection boundaries. Targeted policy will express
one-gap identity, observed provenance, uncertainty, honest non-resolution, and review-only verdict
boundaries. Typed candidates do not gain quality, acceptance, artifact, gate, or route fields.

Alternative considered: add model-authored confidence or acceptability fields to decide whether an
artifact or targeted round proceeds. Rejected because validator/materializer/controller/gate seams
already own those decisions and a calibration label is not lifecycle input.

### 2. Preserve narrow repair and critic input boundaries

Wave2 repair will reuse the bounded accepted-evidence subset of its initial request plus only its
invalid draft and closed parser/semantic failure facts. Targeted repair will retain its
assigned gap, retained observations, bounded draft, and existing closed validation metadata. The
two targeted critics retain assigned references and delimited untrusted material. Raw exceptions,
checkpoint state, artifact paths, ledger data, gate state, routes, and post-candidate controller
validation remain outside these requests.

Alternative considered: pass raw exception strings or later work-unit validation failures to repair.
Rejected because they are unbounded or controller-owned feedback and would create an unreviewed
second recovery seam.

### 3. Add a separate third corpus and resolve optional reports through a closed union

The test-owned corpus will have exactly one normal and one highest-risk case for each of the six
branches. It stays separate from the existing intake/planning and evidence-intake collections so
their fixed denominators and tool-posture facts remain auditable. Evidence-v1 report validation will
resolve a present rubric result only through the closed union of the three corpus indexes, require
global case-id uniqueness, and validate the resolved branch/criterion tuple. Reports without a
rubric remain backward-readable.

Alternative considered: append cases to an earlier corpus or infer the owner from a case-id prefix.
Rejected because either approach weakens exact collection identity and makes an unrecognized report
look valid.

### 4. Use the branch-appropriate real dependency seam only for selected judgment evidence

Focused deterministic cases will assert prompt rendering, trusted/untrusted boundaries, tool
posture, bounded repair/review inputs, and non-admission at each real node/subgraph seam. Selected
live targeted-worker cases use a real model-and-web bridge after strict model/web preflight and
retain exactly-one tool bounds. Selected Wave2, repair, and critic cases use real model-only bridge
execution after strict model preflight. The production parser is a hard invariant before rubric
evaluation; live results have one outer attempt and cannot invoke production recovery, mutate state,
or expand canonical canaries.

Alternative considered: score fake capability outputs or run a full pipeline. Rejected because fake
results cannot establish model judgment, and a full-pipeline run obscures the branch being assessed.

### 5. Retain the existing recovery and publication owners

Wave2 retains exactly one zero-tool repair before its existing non-publication/exhaustion path.
Targeted worker retains its existing one repair; later work-unit failures, retry allocation, and
convergence decisions stay with their present controller and gate. Targeted critic dispatch currently
propagates invocation, parser, or validation failure from its direct call boundary; this change does
not add suppression, a retry guarantee, a terminal projection, or route authority. Live rubric
failures are test-owned reports and cannot become gate or route input.

Alternative considered: use rubric `limited` or critic prose to schedule another retrieval. Rejected
because that transfers non-deterministic evaluation into production convergence authority.

## Risks / Trade-offs

- [Live model/web variability or missing credentials] -> strict branch-specific preflight, one outer
  attempt, explicit bounds, redacted diagnostics, and a supplemental typed disposition.
- [Richer synthesis policy is mistaken for a route decision] -> retain explicit candidate versus
  materializer/preview/gate language and test that invalid candidates produce no projection.
- [Targeted repair leaks untrusted or controller data] -> keep closed validation metadata separate
  from the untrusted draft; exclude raw errors and post-candidate controller failures.
- [Third corpus accidentally changes previous calibration governance] -> assert all three exact
  collection identities, global uniqueness, closed resolution, and unchanged canonical canaries.
- [Critic prose is mistaken for evidence or a convergence verdict] -> retain assigned-reference
  materialization checks and prove malformed/out-of-scope candidates publish no authority.

## Migration Plan

1. Verify the existing `WSN-006`, `TEL-006`, and `EVH-020` registry reservations, then add failing
   deterministic branch, report-resolver, and corpus-governance tests.
2. Revise only the six local capability/prompt surfaces and the established Wave2/targeted repair or
   critic invocation seams needed to carry bounded feedback; regenerate the prompt catalog.
3. Add focused real-node fake-capability and evidence-governance tests, then run the offline
   verification target.
4. Run selected live calibration only when required credentials are configured; record each bounded
   supplemental disposition without production mutation or canonical-canary changes.
5. Roll back by reverting policy and calibration/evidence assets together. No stored-data migration
   or compatibility bridge is required.
