## Context

See proposal.md for the motivation. DRC-006 already requires the human README to be an
early information map with links to the focused documentation. The existing entry table
names commands and recipes but does not state who should choose each surface, what it
actually composes, or what it explicitly is not. The detailed command, authority, and
verification documents already exist and remain their own sources of detail.

## Goals / Non-Goals

**Goals:**

- Make the README's first-scan route selection explicit without changing an existing
  command or runtime contract.
- Preserve one clear path from a selected surface to its current detail owner.
- Make distinctions that already matter operationally and architecturally visible:
  product versus local operator route that is not a versioned product CLI, full fake
  versus fixture graph, visualizer versus a current primary-user TUI, and configured
  fixture workbench versus generic product UI.
- Use focused static documentation and command contracts as deterministic evidence.

**Non-Goals:**

- Add a second command catalog, a lifecycle explanation, a test registry, or an
  authority record to the README.
- Change command wording, recipe selection, provider prerequisites, graph behavior,
  workbench scope, or public-tool authority.
- Move information out of the current focused documents or change their detailed
  procedures.

## Decisions

### A fixed early Entry Surfaces map

Replace the existing entry-point table with one `Entry Surfaces` table near the top of
the README, before the Reading Map. Its stable columns are surface, primary reader/user,
purpose, actual composition, and explicit non-goal. Its six rows are the dedicated Agent
plus reflected tool, standalone operator CLI that is not a versioned product CLI, demo
TUI visualizer that is not a current primary-user TUI, full-fake demos, fixture-graph
verification, and configured-fixture local workbench.

The table is deliberately a selection aid, not a procedure. It names only enough of a
command or surface to identify the route, and sends command execution to local
operations. Retaining a shallow command-only table was rejected because it cannot
express reader, composition, or non-goal distinctions. Moving the map to a new document
was rejected because the README is the existing first human entry point.

### Point to owners instead of copying them

Each row refers readers to the current detail owner: local operations for exact command
use, runtime architecture for composition and authority, and testing/evaluation for
verification meaning. The README retains its existing Reading Map and quick start; it
does not restate those documents' command matrices, lifecycle semantics, or test
selection guidance.

This preserves the agent-information-map policy's reader separation and means a later
change to an operation, architecture, or test contract has one detailed documentation
owner. Embedding all detail in every row was rejected because it would drift from those
owners and exceed the README's routing purpose.

### Static proof at the document seam

Extend the closest existing static documentation contracts to assert the table heading,
columns, required routes, focused-document links, and the terms that prevent the known
surface confusions. Keep the existing command contract as the owner of exact command
spelling. This is deterministic and zero-API; no demo, profile, provider, or live
execution is evidence for a documentation routing claim.

## Risks / Trade-offs

- [A compact table still becomes a hidden command catalog] -> Keep commands as route
  labels and require the local-operations link for exact invocation and prerequisites.
- [A wording edit reclassifies a demo as product behavior] -> Test the explicit
  non-goals and retain the existing command and composition contract tests.
- [The README grows beyond its routing role] -> Preserve the existing early Reading
  Map and enforce the charter's advisory README line-budget signal.
- [Links remain present but route a reader to the wrong detail] -> Assert each question
  type against its named document owner in the focused static test.

## Migration Plan

1. Add focused red documentation assertions that capture the required table grammar,
   named routes, and links.
2. Replace the README table and add concise route links without editing the detailed
   documents' behavior claims.
3. Run the focused governance and command contracts, then the applicable deterministic
   documentation/architecture gates and strict OpenSpec validation.
4. Roll back by reverting the README and its focused assertions; no runtime data,
   configuration, dependency state, or external service migration is involved.
