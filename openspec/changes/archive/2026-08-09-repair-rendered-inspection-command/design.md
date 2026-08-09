## Context

See [proposal.md](proposal.md) for the motivation. The canonical command is already
rendered by `_terminal_failure_presentation.inspection_command()` and owned by
`REC-005`/`REC-006`, but `demo_sessions.py` accepts only `bundle_id`. The command
therefore fails during argument parsing, before the existing read-only
`RunObservationStore.inspect()` boundary can provide its typed result.

The observation store deliberately cannot identify a Bundle path, trusted scope, or
lifecycle operation. Its inspection result is the authority for safe available and
unavailable observation facts; this change must not introduce an alternate store,
Bundle resolver, or recovery controller.

## Goals / Non-Goals

**Goals:**

- Make the renderer's exact `inspect <bundle-id>` grammar executable from the Harness
  root.
- Preserve bounded safe output and zero/nonzero disposition for the existing typed
  inspection result.
- Prove the public command with an isolated process seam instead of a renderer-only
  string assertion.

**Non-Goals:**

- Supporting both the old and canonical spellings.
- Adding an arbitrary observation root, path, profile, session reference, or Bundle
  selector to the command interface.
- Adding observation discovery, lifecycle controls, graph execution, provider calls,
  retries, or cross-process recovery.

## Decisions

### One literal read-only subcommand

The parser will expose exactly one required `inspect` subcommand with one opaque
`bundle_id` argument. `run()` continues to call only `RunObservationStore.inspect()`
with that parsed id, then renders the existing typed result. The old single positional
form is intentionally rejected.

Using a subcommand rather than silently accepting both forms makes the command copied
from a CLI/TUI receipt, command help, README, and local operations one stable contract.
It also prevents a parser alias from becoming a second compatibility surface with
different future semantics.

Alternatives rejected:

- Accept both `inspect <bundle-id>` and `<bundle-id>`: preserves the ambiguity that
  caused documentation, renderer, and parser drift.
- Accept a generic verb or an arbitrary path/profile switch: widens the operator
  surface and risks turning read-only observation into a Bundle locator.

### Retain typed observation ownership

Argument parsing admits only command shape; it does not decide whether a Bundle or
observation exists. `RunObservationStore.inspect()` remains the sole owner of invalid,
missing, unavailable, corrupt, and available facts. The entry maps its existing typed
result to safe rendered text and exit zero for available versus bounded nonzero for all
other states.

No parser branch may invoke a Bundle workbench, graph, provider, sandbox, or lifecycle
method. The legal disposition for unavailable inspection remains unavailable; no local
retry, resume, or replacement Run is claimed by this command.

### Evidence crosses the actual command boundary

Focused tests will cover parser grammar, typed read-only results, and an inspect-only
store spy. A subprocess test will then publish one unique bounded observation through
`RunObservationStore`, invoke the renderer's exact Make command from
`deep_research_harness/`, and assert its safe available output and success status. It
will also exercise invalid, missing, and corrupt observations as bounded nonzero results.

The child process authenticates the command boundary, output, and exit disposition; it
does not by itself prove the absence of every forbidden call. The focused store spy is
the deterministic authority-boundary proof that the entry dispatches only `inspect()`.

The current `standalone-inspection-command-execution` test-evidence claim incorrectly
names a direct `run()` test. Apply will retarget that claim to the new subprocess test,
retain a separate direct-projection claim for the focused test that existing
requirement-impact metadata names, and add the matching documentation claim/impacts for
the exact README and local-operations contract. No unrelated test registry entries
change.

The test records its exact test-owned record root from the store after publishing and
removes only that record in a `finally` block. It must not reproduce the private storage
key, scan, remove, or alter the diagnostic root or any other project record. This reaches
the lowest deterministic process seam without introducing a test-only command option or
modifying the actual inspection authority.

## Risks / Trade-offs

- [Existing users may have used the undocumented one-argument form] -> Reject it
  deliberately, with `--help` exposing the canonical grammar, so all published
  surfaces stay compatible with rendered CLI/TUI output.
- [A subprocess fixture could leave diagnostics in the project root] -> Use a unique
  test-owned Bundle id and store-derived record-level cleanup in `finally`; never
  reproduce the private key or remove the diagnostic root or unrelated records.
- [A process test could overclaim absence of forbidden calls] -> Use it only for the
  command/output/exit boundary and retain a focused inspect-only store spy for dispatch
  authority.

## Migration Plan

1. Add a failing Harness-root process regression for the currently rendered command
   and focused parser/read-only cases.
2. Implement the one-subcommand grammar, then align help and operator documents.
3. Run focused tests and the deterministic project gate; rollback restores the prior
   parser and documentation together, with no persisted Bundle or observation schema
   migration.
