# Real Smoke Test Completes A Bounded Research Outcome

`real-research.sh` is an operator-facing smoke test, not the Primary User product
interface. A passing run uses real model and web integrations, automatically follows
bounded default decisions for a fixed, cost-controlled question, and produces a
readable final report. Preflight success, a retained run record, or partial graph
progress alone do not pass the smoke test; expected transient external failures may
use bounded retry and otherwise must leave the Smoke Test Operator an actionable
diagnostic.
