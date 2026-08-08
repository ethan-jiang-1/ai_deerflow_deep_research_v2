## Why

BUG-007 is a P0 workflow failure: HITL2 asks a user to choose graph-control routes
without giving them the evidence, judgement, or authority needed to make that
choice. The system must perform the research judgement it can derive from validated
state and interrupt only for a genuine user preference or authorization decision.

## What Changes

- Replace unconditional HITL2 route selection with an agent-led, deterministic
  continuation at the already-validated Wave2-to-readiness boundary. The policy
  validates that boundary and applies its sole ordinary route without creating a
  second routing authority.
- Make the full-fake lifecycle automatically take its labelled fixture route rather
  than ask a user to judge nonexistent research output.
- Remove real-mode HITL2 interaction in this change. A future non-inferable user
  preference or irreversible authorization needs its own typed state contract and
  OpenSpec change; it must not be represented by the legacy graph-route menu.
- Remove the readiness hard check that treats a consumed HITL2 response as research
  quality evidence. A valid autonomous continuation must not be blocked merely
  because it did not manufacture a human confirmation.
- Make standalone CLI/TUI render autonomous decisions as progress and ordinary
  completion, not as a menu of internal graph routes. Replace copy-hostile command
  examples with commands safe to paste into interactive zsh.
- Add deterministic lowest-seam regressions proving that ordinary validated states
  do not interrupt and that every remaining human decision has actionable context.

## Capabilities

### New Capabilities

- `agent-led-research-decisions`: Bounded autonomous HITL2 continuation at the
  validated Wave2 boundary, with no human-decision fallback in this change.
- `research-fake-cli-onboarding`: Paste-safe first-run instructions and a
  no-route-selection fake CLI lifecycle.

### Modified Capabilities

- `hitl2-node`: HITL2 changes from an unconditional human choice to validated
  policy-led continuation with no current interrupt path.
- `demo-pipeline`: Full-fake demos stop requiring users to choose internal control
  routes, and standalone presentation distinguishes autonomous actions from input.
- `research-demo-tui`: The fake TUI follows the autonomous fixture route rather than
  presenting a decision menu for nonexistent findings.
- `readiness-node`: Readiness no longer mistakes obsolete HITL2 confirmation for a
  structural research-quality precondition.

## Impact

- Affected downstream surfaces: HITL2 node contracts/prompt policy, graph lifecycle
  state projection, fake and real standalone adapters, TUI, tests, test-evidence
  metadata, and `agent/README.md`.
- No backend, frontend, Gateway configuration, model provider, web-search provider,
  checkpoint schema, or dependency change is proposed. No files under `backend/` or
  `frontend/` will be modified.
- Real decisions remain graph-owned. A deterministic policy may select only existing
  routes from validated state; it does not fabricate findings, change gate authority,
  or turn fake output into research.
