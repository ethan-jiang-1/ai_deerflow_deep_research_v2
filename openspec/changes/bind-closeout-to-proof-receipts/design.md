# Design

## Context

`selected-change-closeout.py` already defines the attestation contract this
checker needs: `{change_name, repository_identity, base_commit, head_commit}`,
verified against the current repository and the committed ancestry. The
companion change defines the lane registry and the receipt format. The aggregate
in `check_project_gate.py` is orchestration-only and preserves each component's
exit code, so a new component must be a standalone script with its own tests.

## Goals / Non-Goals

**Goals:** a closeout verdict that cannot be satisfied by prose, and a checker
whose inputs are already-defined contracts. **Non-Goals:** no runtime behavior, no
change to what the other five components check, and no judgement about whether a
lane is *sufficient* (that stays a reviewed registry decision).

## Decisions

1. **Touched files come from the existing attestation, not from a new rule.** The
   checker takes `--attestation <path>` with the `selected-change-closeout.py`
   contract and computes `git diff --name-only <base_commit>..<head_commit>`.
   Inventing a second base/head rule would let the two disagree. Without an
   attestation, or with no active change, the checker exits zero and prints
   `no selected change` - it never guesses a range.
2. **Required lanes are the intersection of touched files and registered
   surfaces.** The registry's surface globs are authoritative; the checker prints
   the surfaces it matched so a too-narrow declaration is visible rather than
   silently lenient.
3. **A receipt is valid only if five facts hold**: recorded exit code zero; the
   recording tree was clean; `git diff <receipt revision>..<head_commit> --
   <surfaces>` is empty; the transcript file exists with the recorded SHA-256; and
   the transcript text contains the lane's registered success sentinel. Each
   failure prints its own reason and the exact `make proof LANE=<lane>` rerun.
4. **Warn and enforce are explicit modes.** `--mode warn` (the default for the
   measured window) prints every unmet requirement and exits zero;
   `--mode enforce` exits non-zero. The printed line always names the mode, so a
   warn-only run can never be read as an enforced verdict. Task 3.2 flips the
   aggregate's invocation after the measurement.
5. **Credential-gated lanes never yield a valid receipt.** A lane registered with
   `requires_credentials` produces an `unverified` record; the checker reports it
   as a known boundary instead of a failure, and the change must state that
   boundary in its tasks.
6. **The aggregate stays orchestration-only.** The checker owns its rules and
   tests; `check_project_gate.py` only adds it to the registered component set and
   preserves its exit code.

## Risks / Trade-offs

- [A change could register a new lane and declare too few surfaces to avoid
  receipts] → the registry is a reviewed artifact in the same change, and the
  checker prints the surfaces it used.
- [Warn-only mode could linger and never be flipped] → task 3.2 is explicit, and
  the printed mode makes a lingering warn visible in every closeout transcript.
- [Attestation ranges could be stale] → `verify-boundary` already validates the
  committed ancestry; the checker re-reads the attestation rather than caching it.
