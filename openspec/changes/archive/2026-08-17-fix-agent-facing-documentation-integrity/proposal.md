## Why

Agent-facing navigation and operator documentation contain stale paths and command
examples that send a contributor to a missing DeerFlow digest, a retired repository
root, or an invocation that omits the required profile. The deterministic gate is now
green, so this is the next low-risk way to remove recurring contributor friction without
changing the downstream runtime or the upstream `deerflow/` gitlink.

## What Changes

- Correct root and backlog references to the checked-out repository layout and the
  existing read-only DeerFlow guide surfaces; state that the old digest notes are not
  distributed with this submodule.
- Correct `demo-real` and `demo-real-scripted` examples so they match the supported
  Makefile entry semantics and the local-operations reference.
- Document the existing test taxonomy, deterministic public-network denial and its
  explicit marker exceptions, and the helper-module meaning of `tests/fixtures/`.
- Add focused documentation contracts and a path/reference audit that fail on the
  repaired stale references without turning documentation into a second runtime
  authority.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- None. This change corrects navigation and explanatory material only; it does not
  change a supported runtime, lifecycle, or test-selection behavior.

## Impact

- Root `AGENTS.md`, root and Harness READMEs, `_backlog/README.md`,
  `openspec/README.md`, and `docs/testing-and-evaluation.md`.
- Focused documentation and command contracts under `deep_research_harness/tests/`.
- No runtime source, dependencies, credentials, network behavior, or DeerFlow source.

## Change Focus

- **Primary module / causal owner:** documentation and command navigation at repository and Harness entry surfaces, which own contributor routing but not runtime behavior.
- **Seam classification:** wiring — corrects references and command examples while preserving the existing Makefile, pytest, and runtime contracts.
- **Question:** How can a new contributor or coding agent discover valid framework context, local entry commands, and test-surface boundaries without following stale paths or inferring unsupported behavior?
- **Necessary adjacent/external contracts:** `deep_research_harness/Makefile` and `docs/local-operations.md` establish existing command semantics; `tests/conftest.py` establishes the current deterministic network boundary; `deerflow/AGENTS.md` and `deerflow/backend/AGENTS.md` are the available read-only framework orientation surfaces. This change only documents those facts.
- **Evidence seam:** focused documentation contracts verify literal commands, real relative-path targets, taxonomy/marker disclosures, and absence of the identified stale references; `make governance` remains the structural documentation check.
- **Not in scope:** changing Make targets, pytest marker behavior, test-directory layout, framework source or documentation, runtime CLI behavior, or restoring a digest directory.
- **Triggered review policies:** change-admission
