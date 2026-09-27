# Proposal

## Why

This repository asks for evidence, but three measured failures show that a claim
still travels further than its proof:

1. `tests/integration/test_demo_cli.py` rode the ambient demo workspace, so a
   leftover non-terminal Bundle turned the suite red for reasons unrelated to the
   code - and would have turned it green again by accident (BUG-072).
2. A commit landed with `VERIFY=2` because the commit was chained after the
   verification command; the repository's own contract test then caught a route
   the rewrite had dropped. The claim ("rewrite done") had no receipt for the
   revision that landed.
3. Runbook-031 promised that `/context` shows the captured prompt, runtime MD
   bytes and enforced tools/budget while the pane rendered a summary line - a
   documented promise no assertion pinned, so it drifted.

A fourth instance happened while writing these changes: a proposal line was
edited into a two-line list, the Change Guidance checker rejected it, and the
commit had already been chained after the edit - the same "claim outruns its
proof" pattern, three times in one session.

A receipt is what none of those had: a runner-written record that a named lane
exited zero on a revision that still covers the delivered files.

## What Changes

- **Lane registry (data)**: `openspec/governance/proof-lanes.toml` maps each lane
  to its command, working directory, the file surfaces it covers, and (for
  operator-facing surfaces) the journeys it must include.
- **Receipt runner**: `deep_research_harness/scripts/proof_receipt.py` plus
  `make proof LANE=<lane>` runs the lane, tees the transcript, and records the
  command, exit code, revision, tree cleanliness, tool versions and a digest of
  its own output. `make proof --stale` reports which receipts no longer cover the
  working tree and what to rerun.
- **Mutation lane**: `deep_research_harness/scripts/mutation_check.py` plus a
  declarative `tests/mutations/registry.py` and `make mutation-check` apply each
  registered mutation, assert the named selector goes red, restore the file, and
  exit non-zero when any mutation stays green.
- **Documentation**: the testing document and the local guidance's Delivery Lanes
  bind the lanes to their commands (the guidance principle and table landed
  already with the charter work).

## Order

This change lands before `bind-closeout-to-proof-receipts`: the closeout checker
reads the lane registry and the receipt format defined here, so enforcing receipts
before they can be produced would block every closeout.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- None. This change adds tooling and advisory binding only; making closeout
  require a receipt is a separate change (`bind-closeout-to-proof-receipts`)
  because it modifies the gate composition owned by `project-structure`.

## Impact

- New: `openspec/governance/proof-lanes.toml`,
  `deep_research_harness/scripts/proof_receipt.py`,
  `deep_research_harness/scripts/mutation_check.py`,
  `deep_research_harness/tests/mutations/registry.py`.
- Touched: `deep_research_harness/Makefile` (two targets),
  `deep_research_harness/docs/testing-and-evaluation.md`.
- No runtime, lifecycle, or product behavior changes; receipts and mutations are
  development evidence tooling only.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/`
  gitlink; this change owns no such boundary.

## Change Focus

- **Primary module / causal owner:** the development-evidence tooling of
  `deep_research_harness/` (`scripts/`), which answers "what ran, on which
  revision, and did it pass".
- **Seam classification:** wiring - a runner, a data registry and a mutation
  driver; no authority over runtime behavior, and no gate verdict yet.
- **Question:** How does a claim about this harness become checkable, so that
  "done" always carries the command, exit code and revision that produced it?
- **Necessary adjacent/external contracts:** the lane commands already registered
  in `make verify`, `make tui-journey`, `make debugger-proof`,
  `make tui-experiences`; `openspec/change-guidance/local/deep-research.md`
  Delivery Lanes (the advisory binding); git as the revision authority.
- **Evidence seam:** a self-demonstration - a receipt rejected as stale after a
  touched surface changes, and a mutation that stays green failing the lane -
  plus the three measured failures above reproduced as the lanes' motivation.
- **Not in scope:** the closeout gate composition (`project-structure` PRS-009
  owns it; the follow-up change carries that delta), any runtime or lifecycle
  behavior, and anything under `deerflow/`.
- **Triggered review policies:** none: development tooling and advisory guidance, with no candidate, human judgment, control fact, admission/recovery boundary, node-agent role, or lifecycle output change.
