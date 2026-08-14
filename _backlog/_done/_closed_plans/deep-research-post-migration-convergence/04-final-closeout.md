# 04 - Phase I Final Closeout

> Status: closed on 2026-08-15; archive this record with the parent plan as `CLS-038`.
> Scope: the 54-Candidate post-migration convergence program, executed through eight archived OpenSpec changes (`00`--`07`).
> Evidence anchors: [Candidate Register](03-execution/candidate-register.md), [execution map](03-execution/80-remediation-change-map.md), [execution record](03-execution/99-progressive-execution.md), and the eight `openspec/changes/archive/` directories.

## Terminal Decision

Phase I is complete. All 54 Candidate rows have a final, evidenced disposition and there is no active OpenSpec change.
Forty rows were retired, migrated, renamed, repaired, rejected, or otherwise closed by their owning archived change;
fourteen are intentionally retained current guards or historical records. None remains `ready`, `blocked`, or unknown.

This is not a claim that unregistered external consumers or data do not exist. The authorized outcome is a bounded
clean cutover: current source-controlled surfaces are supported; unknown retained/external inputs are rejected at
their admission boundary unless a future change explicitly inventories and authorizes them.

## Authority And Recovery Review

| Review | Final result | Evidence / recovery boundary |
| --- | --- | --- |
| Authority | Each changed concept has one current owner: required node contract, Run Bundle lifecycle, fixture composition, host configuration, evaluation facade, or persisted-data boundary. No dual writer, entry, or authority is retained. | The `00` program admission guards continue to reject missing owners, open Candidate budgets, and unregistered workstreams. |
| Public and persisted surfaces | Legacy compatibility readers/writers were removed only after owner decisions and matrix-based cutover proof. Unknown old inputs fail closed before write, projection, lifecycle work, or provenance upgrade. | 05--07 archive matrices distinguish supported inventory from planted rejection fixtures; Summary v2 remains current rather than a legacy Journal reader. |
| Recovery | Recovery is bounded to an owner-approved complete local reader hotfix or revert with paired deterministic tests. | No field flag, payload rewrite, synthetic terminal mapping, inferred diagnostic location, or partial compatibility reader is authorized. |
| Retained guards | Guards are current executable behavior, not unfinished cleanup. | Each retained guard has an owning current contract and a known/planted violation: entry rejection, evidence registry/suspension, refinement/workspace drift, live classification, generated projection freshness, or archive/history boundary. |

## Residual Allowlist

The final residual scans found 891 `legacy`/`compat`-class matches and 33 old-term matches. They are not a deletion
backlog. No old-term match appears in production Python. Every remaining match belongs to one of these allowlisted
categories:

| Category | Owner and review/removal trigger |
| --- | --- |
| Current main-spec rejection contracts and approved old-input denials | Capability owner; review when a supported input or public contract is deliberately changed. |
| Focused tests and planted negative controls | Test owner; retain while the current boundary exists, update only with its owning behavior change. |
| Governance, requirement, structure, and evidence registries | Governance owner; review on registry/schema change and remove only through the owning lifecycle. |
| Archived changes, ADRs, audit findings, and closed backlog records | Record owner; evidence-only, revised or removed only through the applicable history policy. |
| Current bounded aliases, normalization, and fallback behavior | Runtime owner; review when its explicit support decision or falsifiable guard changes. |

## Verification And Limits

The repository checks now pass: `openspec doctor --json` is healthy, `openspec validate --specs` reports 47 passed,
and project requirements, specs, architecture, Charter, and requirement-to-test coverage all pass. The eight
archives and their main-spec synchronizations are present; `deerflow` remains clean at gitlink
`66b9e7f21212490cf92fafac137542b9deb06615`.

The last integration lane completed with `239 passed, 4 skipped, 32 deselected`. Full deterministic verification
is evidence-limited by pre-existing test-asset selector findings: three selectors yield five missing-impact or
uncollected messages. `test-fast` has 34 failures and `test-workflow` one failure, all the known
`evaluation_runtime_control_digest_mismatch` baseline. These are not treated as passes and were outside the eight
Candidate scopes; this closeout does not modify their selector registry or digest assets.

Not run: credentialed/live and release lanes, real Gateway, real Demo/TUI provider paths, `requires_llm`, Postgres,
external deployment configuration, external Python consumers, and external retained-data inventories. Their absence
does not create implied support. A future request to support any such surface must enter a new OpenSpec change with
inventory, authority, reader/writer matrix, failure behavior, recovery, and removal trigger.

## Program Accounting

From the parent of the `00` archive (`8661693^`) through the `07` archive (`a8293b6`), the program changed 338
files: 111 added, 204 modified, and 15 deleted, for 13,218 added and 2,784 removed lines. These figures cover code,
tests, current specifications, governance, and archival evidence; they are accounting only, not success criteria.
The material outcome is eight closed changes, five synchronized retained-data-facing main specs in 07, 47 current
main specs validated, 394 registered requirements with 18 explicitly retired, and zero orphan requirements.

No ninth change is admitted. Any later scope is a new request, not unfinished work hidden behind this closed plan.
