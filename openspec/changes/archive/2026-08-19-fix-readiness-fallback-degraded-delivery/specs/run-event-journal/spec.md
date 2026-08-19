# run-event-journal Delta

> req: REJ-010

## ADDED Requirements

### Requirement: Visit decision facts carry closed routing attribution

The Event Journal SHALL retain the readiness visit-decision fact and the
targeted-evidence drained no-op fact defined by their owning capabilities, each as a
node-level fact whose attribution fields are closed enumerations: the readiness fact
carries the written route (`pass` | `repair_targeted` | `exhausted`), a non-negative
blocked-verdict count, at most one pass-guard flag (`wave2_degraded` |
`no_declared_gap_work` | `fallback_projection`), and, only on an `exhausted` route,
that visit's closed structural failure codes; the targeted-evidence fact carries the
closed `drained_no_op` reason and a zero gap count. These fields SHALL NOT be derived
from or retain raw exception detail, critic output, prompt text, evidence content, or
any non-closed value, SHALL be absent when their owning condition does not hold, and
SHALL NOT change invocation outcomes, failure categories, budget decisions, routing,
or terminal classification.

#### Scenario: A readiness visit fact is retrievable with closed attribution
- **WHEN** a readiness visit completes and its journal fact is inspected
- **THEN** the fact exposes only the closed route, blocked count, optional single
  pass-guard flag, and — on `exhausted` — the closed structural failure codes, with no
  critic or evidence content

#### Scenario: A drained targeted-evidence visit fact is distinguishable from work
- **WHEN** a gap-less targeted-evidence visit and a gap-dispatching visit are both
  journaled in one run
- **THEN** only the gap-less visit's fact carries `drained_no_op` with gap count `0`,
  and the dispatching visit's facts carry no such reason

#### Scenario: Decision facts never alter control outcomes
- **WHEN** the journal records readiness visit decision facts and targeted-evidence
  no-op facts
- **THEN** invocation outcomes, failure categories, budget decisions, routing, and
  terminal classification are identical to a run where the facts are not recorded
