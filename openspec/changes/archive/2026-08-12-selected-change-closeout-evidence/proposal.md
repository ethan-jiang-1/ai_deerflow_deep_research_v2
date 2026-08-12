## Why

`openspec/guardrails/selected_change_closeout.py` is a bounded local-evidence
guardrail for closing a selected OpenSpec change, but three defects let it violate
its own non-authoritative boundary: a `record-review --output` path only needs to sit
under the change root (so it can overwrite `tasks.md`/`proposal.md`), unchecked-task
parsing accepts any line containing `- [ ]` rather than a real Markdown task item,
and the README mixes a planning-home-root assumption with root-relative examples
without stating that callers must parse the stdout `result` rather than rely on the
shell exit code.

## What Changes

- **Restrict persisted output to a dedicated evidence directory.** `record-review`
  output must resolve below `<active change root>/guardrail-evidence/`, not merely
  below the change root. This closes the overwrite of change artifacts (`tasks.md`,
  `proposal.md`) that the current containment allows.
- **Tighten unchecked-task parsing.** Only real Markdown unchecked task lines
  (a list item beginning `- [ ] `) contribute task labels; lines that merely contain
  the `- [ ]` substring in prose are ignored.
- **Clarify the caller contract in `guardrails/README.md`.** Examples assume the
  planning home as `cwd`; the README states that domain rejections
  (`missing-boundary`, `invalid-review`) are emitted as stdout JSON `result` values
  with exit code 0, so callers must parse `result` rather than rely on the shell exit
  code.
- **Strengthen the approved requirement (SCC-002).** The containment wording in
  `selected-change-closeout-evidence` changes from "below that selected active
  change root" to "within that change's dedicated `guardrail-evidence/` subdirectory".

## Change Focus

- **Primary module / causal owner:** `openspec/guardrails/selected_change_closeout.py` guardrail command, owned by the `selected-change-closeout-evidence` capability.
- **Seam classification:** deterministic-guardrail - repairs the bounded deterministic evidence command's containment, task parsing, and caller contract without changing attestation schema, dispositions, or runtime behavior.
- **Question:** Can `record-review` ever write over a change artifact, and does the caller know it must parse the stdout `result` rather than the shell exit code?
- **Necessary adjacent/external contracts:** `selected-change-closeout-evidence` spec (SCC-002 containment) and `deep_research_harness/tests/contract/test_selected_change_closeout.py` define the observable contract.
- **Evidence seam:** focused contract test for containment, task parsing, and result-parsing, plus the repository governance and deterministic verification gates.
- **Not in scope:** attestation schema, disposition set, boundary/evidence semantics, exit-code changes, runtime/graph/model/provider behavior, and `deerflow/`.
- **Triggered review policies:** change-admission

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `selected-change-closeout-evidence`: SCC-002 persisted-output containment tightened
  to the dedicated `guardrail-evidence/` subdirectory (behavior-level change).

## Impact

- `openspec/guardrails/selected_change_closeout.py` — containment check and task-line
  parser.
- `openspec/guardrails/README.md` — caller contract and examples.
- `deep_research_harness/tests/contract/test_selected_change_closeout.py` — updated
  and added fixtures for the stricter containment and task parser.
- No runtime, graph, model, provider, or `deerflow/` behavior changes.
