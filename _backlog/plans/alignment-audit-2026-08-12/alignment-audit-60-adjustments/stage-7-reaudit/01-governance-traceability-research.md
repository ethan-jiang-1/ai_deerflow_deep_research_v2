# Stage 7 Research - Governance, Topology, And Traceability

> Date: 2026-08-13
> HEAD: `198cf290146b4308e7a8da432d28abd46aca51d1`
> Scope: current, non-archive primary sources for A-001, A-002, A-008, and A-009.
> Method: read repository-owned authority, checker, test, and Git metadata only. No
> DeerFlow source was opened; no code, spec, configuration, governance executable, or
> progressive ledger was changed by this research record.

## Baseline

| Observation | Result | Proof limit |
| --- | --- | --- |
| Active OpenSpec changes | `openspec list --json` returned `changes: []`. | A later concurrent change can alter this baseline. |
| Gitlink index | `git ls-files --stage deerflow` returned mode `160000` at `66b9e7f21212490cf92fafac137542b9deb06615`. | This is Git metadata, not an inspection of host source. |
| Gitlink and nested worktree | `git submodule status -- deerflow` showed the same pointer; `git -C deerflow status --short` was empty. | This is a point-in-time manual observation. |
| Root diff/status | Root `git status --short` and `git diff --submodule=short` were empty before this evidence file was written. | It does not automatically protect a later pointer or nested-worktree change. |

## A-001 - Current Topology Authority

### Evidence

- Repository-root [AGENTS.md](/Users/bowhead/ai_deerflow_deep_research_v2/AGENTS.md:3) names the two layers as `deep_research_harness/` and the `deerflow/` submodule; its boundary rules prohibit modifying the framework at [line 20](/Users/bowhead/ai_deerflow_deep_research_v2/AGENTS.md:20).
- [openspec/config.yaml](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/config.yaml:6) identifies `deep_research_harness/` as the downstream product and `deerflow/` as its upstream gitlink, and prohibits ordinary modification or source browsing at [lines 7-10](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/config.yaml:7).
- The local contributor guide repeats the same boundary at [deep_research_harness/AGENTS.md:3](/Users/bowhead/ai_deerflow_deep_research_v2/deep_research_harness/AGENTS.md:3), while the active structural main spec defines `deep_research_harness/` as the canonical downstream root at [project-structure/spec.md:66](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/specs/project-structure/spec.md:66).
- The editable dependency path is current and concrete: [deep_research_harness/README.md:55](/Users/bowhead/ai_deerflow_deep_research_v2/deep_research_harness/README.md:55) points to `../deerflow/backend/packages/harness`.
- Remaining `backend`/`frontend` language in [deployment-configuration/spec.md:427](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/specs/deployment-configuration/spec.md:427) is a negative guard against changes under upstream directories, not a claim that root `backend/` or `frontend/` is the upstream checkout. The prior re-audit recorded this distinction as N-001 at [Stage 3 ledger](/Users/bowhead/ai_deerflow_deep_research_v2/_backlog/plans/alignment-audit-2026-08-12/alignment-audit-60-adjustments/stage-3-reaudit/03-reduced-mismatch-ledger-and-next-gate.md:25).

### Conclusion

**Resolved within A-001's historical-topology scope.** Current authority consistently
describes the real `deerflow/` gitlink and the `deep_research_harness/` downstream
root. Valid negative guards mentioning `backend`/`frontend` are not evidence of a
return to the retired root-mirror model and must not be bulk-renamed.

### Follow-up Risk And Side Effect

No A-001 follow-up is proposed. A future wording change that indiscriminately removes
`backend` or `frontend` would risk weakening valid placement/deployment constraints or
misdescribing actual public host paths. Its likely side effect is loss of a useful drift
guard, rather than an improvement in topology truth.

## A-002 - Gitlink Detection And Protection

### Evidence

- The OpenSpec archive rule requires explicit Git status, index, submodule, nested worktree, and submodule-diff observations at [openspec/config.yaml:81](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/config.yaml:81). The same rule expressly states at [line 83](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/config.yaml:83) that these are **manual** scope/diff evidence, "not automatic detection or protection."
- The structural registry's upstream roots remain `backend` and `frontend` at [project-structure.toml:10](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/governance/project-structure.toml:10) and [line 16](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/governance/project-structure.toml:16). The architecture checker iterates only those configured roots for upstream-import validation at [check_project_architecture.py:714](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/governance/check_project_architecture.py:714); its helper returns no files for a non-directory at [lines 541-549](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/governance/check_project_architecture.py:541).
- The checked current repository-owned checker/guardrail/test sources contain no registered automatic gitlink pointer or nested-worktree detector. The one Git-using closeout guardrail verifies caller-declared committed ranges only, not a gitlink policy, as stated in [selected_change_closeout.py:1](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/guardrails/selected_change_closeout.py:1) and implemented as generic repository/diff checks at [lines 101-150](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/guardrails/selected_change_closeout.py:101).

### Conclusion

**Open: `DEFERRED-CODE-CHANGE`.** The baseline Git metadata is clean, and the authoring
route now describes the real boundary honestly. Neither fact creates an automatic
detector or protection mechanism. This confirms the Stage 7 condition at [progressive
plan:556](/Users/bowhead/ai_deerflow_deep_research_v2/_backlog/plans/alignment-audit-2026-08-12/alignment-audit-60-progressive-execution-plan.md:556).

### Follow-up Risk And Side Effect

A detector would require a separately authorized code/governance/test change. It would
need to distinguish an intended gitlink pointer update, an uninitialized submodule,
and an unauthorized nested-worktree modification without reading DeerFlow source.
Risks are false failures in partial checkouts and false assurance if the detector checks
only the root pointer. Likely side effects are additional Git/submodule availability
requirements and a slower or more environment-sensitive verification gate. Manual
evidence must remain explicitly bounded until such a change is implemented and tested.

## A-008 - Policy Cardinality

### Evidence

- The current routing behavior is plural where triggers are plural: the Charter entry says to select every canonical policy whose trigger applies at [agent-charter/README.md:13](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/agent-charter/README.md:13) through [line 20](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/agent-charter/README.md:20), while retaining one primary causal owner.
- The authoring context requires canonical comma-separated policy names at [openspec/config.yaml:46](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/config.yaml:46) through [line 50](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/config.yaml:50). The active Charter main spec makes that a normative plural list at [deep-research-agent-charter/spec.md:419](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/specs/deep-research-agent-charter/spec.md:419) through [line 436](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/specs/deep-research-agent-charter/spec.md:436).
- The deterministic checker parses a comma-separated list at [check_agent_charter.py:586](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/governance/check_agent_charter.py:586) through [line 633](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/governance/check_agent_charter.py:633), and the spec requires independently selected review records at [deep-research-agent-charter/spec.md:464](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/specs/deep-research-agent-charter/spec.md:464).
- However, [openspec/policies/README.md:6](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/policies/README.md:6) still tells contributors to select "one relevant policy," and the normative DRC-001 requirement repeats that at [deep-research-agent-charter/spec.md:10](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/specs/deep-research-agent-charter/spec.md:10) through [line 20](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/specs/deep-research-agent-charter/spec.md:20).

### Conclusion

**Open current mismatch, recorded as N-002; A-008 is not fully resolved.** A contributor
can mechanically declare multiple triggered policies today, but two current guidance/
normative surfaces tell that contributor to choose one. The Stage 3 ledger already
classified the authoring risk and required a separate bounded change at [lines
18-19](/Users/bowhead/ai_deerflow_deep_research_v2/_backlog/plans/alignment-audit-2026-08-12/alignment-audit-60-adjustments/stage-3-reaudit/03-reduced-mismatch-ledger-and-next-gate.md:18)
and [line 26](/Users/bowhead/ai_deerflow_deep_research_v2/_backlog/plans/alignment-audit-2026-08-12/alignment-audit-60-adjustments/stage-3-reaudit/03-reduced-mismatch-ledger-and-next-gate.md:26).

### Follow-up Risk And Side Effect

A small policy-routing OpenSpec change should align the singular wording with the
already-enforced plural behavior while preserving one primary causal owner. It must
review all affected spec, entry, config, and checker contracts together; changing only
the README would leave the normative contradiction. The risk is over-selection of
irrelevant policies and extra review tables; the counter-risk of no change is
under-selection of genuinely triggered reviews. Its observable side effect would be
additional conditional review records for multi-trigger changes, not runtime behavior.

## A-009 - Traceability Scope

### Evidence

- The requirement-coverage checker gathers `@impl` IDs from docstrings of files with test functions at [check_project_req_coverage.py:39](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/governance/check_project_req_coverage.py:39) through [line 70](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/governance/check_project_req_coverage.py:70), then fails only when an active main-spec ID has no such test reference at [lines 138-153](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/governance/check_project_req_coverage.py:138). It does not associate a requirement with an assertion, scenario outcome, or semantic equivalence rule.
- The active evaluation specification distinguishes ownership annotations from test-selector proof: existing `@impl` annotations identify implementation surfaces, while central evidence claims own selector proof at [evaluation-hardening/spec.md:98](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/specs/evaluation-hardening/spec.md:98) through [line 100](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/specs/evaluation-hardening/spec.md:100). It also deliberately avoids a second exhaustive test catalog for ordinary collected tests.
- `RequirementImpact` metadata gives selected requirements a requirement, owning contract, seam, selector, and risk at [requirement_evidence.py:42](/Users/bowhead/ai_deerflow_deep_research_v2/deep_research_harness/tests/assets/requirement_evidence.py:42) through [line 50](/Users/bowhead/ai_deerflow_deep_research_v2/deep_research_harness/tests/assets/requirement_evidence.py:50), but its validator checks only the supplied entries at [lines 1442-1487](/Users/bowhead/ai_deerflow_deep_research_v2/deep_research_harness/tests/assets/requirement_evidence.py:1442). It does not require an entry for every active requirement.
- The richer evidence validator requires every alive ID to appear in deterministic `@impl` metadata, then applies claim-class requirements only to explicitly listed policy rules at [requirement_evidence.py:1606](/Users/bowhead/ai_deerflow_deep_research_v2/deep_research_harness/tests/assets/requirement_evidence.py:1606) through [line 1644](/Users/bowhead/ai_deerflow_deep_research_v2/deep_research_harness/tests/assets/requirement_evidence.py:1644).

### Conclusion

**Open: `OPTIONAL-HARDENING`.** Current green coverage proves an ID-level relationship:
every active main requirement has at least one `@impl` reference in a test docstring,
and selected risk areas have richer typed evidence. It does **not** prove that every
requirement's semantic assertions, scenario outcomes, and implementation behavior are
equivalent. This is a proof-strength limit, not evidence that requirements are missing
or unimplemented. It matches the Stage 7 constraint at [progressive
plan:558](/Users/bowhead/ai_deerflow_deep_research_v2/_backlog/plans/alignment-audit-2026-08-12/alignment-audit-60-progressive-execution-plan.md:558).

### Follow-up Risk And Side Effect

A stronger mapping must be a separately authorized, bounded code/evidence change. A
pragmatic initial scope would map changed or highest-risk requirements to named
assertion/scenario evidence rather than impose a second exhaustive catalog. The risk is
turning static prose or metadata into a false semantic proof, or creating a costly
duplicated inventory that drifts from tests. Likely side effects are added test-writing
and maintenance burden, more stringent review of assertion intent, and potentially
slower validation. It must continue to distinguish test selection, behavioral evidence,
and provider-dependent/live quality claims.

## Authority And Proof Boundary

The authority ladder is explicit: active main specs own normative semantics;
`project-structure.toml` owns exact enumerable structure; contract tests/checkers own
mechanical enforcement; archived artifacts are historical only
([architecture-policy.md:7](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/governance/architecture-policy.md:7)
through [line 21](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/governance/architecture-policy.md:21)).
The test-evidence policy makes the analogous distinction between active semantics,
enumerable metadata, and executable evidence, and says static metadata is not a proxy
for behavioral proof ([test-evidence-policy.md:7](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/governance/test-evidence-policy.md:7)
through [line 23](/Users/bowhead/ai_deerflow_deep_research_v2/openspec/governance/test-evidence-policy.md:23)).

Accordingly, this report establishes only the four conclusions above. It does not prove
future worktree cleanliness, live/provider behavior, hidden semantic equivalence, or
the correctness of an unimplemented detector. It also does not create a backlog item,
authorize a change, or modify the Stage 7 progressive ledger.
