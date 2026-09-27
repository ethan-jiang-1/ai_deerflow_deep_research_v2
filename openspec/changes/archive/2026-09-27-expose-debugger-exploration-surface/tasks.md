# Tasks

## 1. Exploration surface (RED-014)

- [x] 1.1 `/harness` reports the composition, recipe revision, compatibility fingerprint, per-node kinds, prerequisites, logical ladder, trusted roots and readable projections. Verify: experience E13 asserts each fragment. ✓
- [x] 1.2 `/targets` inventories every Bundle with status/phase/frames/generation and attach posture plus the live session, and `/inspect <id>` shows state, frames and typed work-unit records. Verify: experience E14. ✓
- [x] 1.3 A bare `/replay` lists bounded candidates with postures instead of a usage line, and the no-session prompt lists both start compositions and the id-taking entries. Verify: experience E10 and E1. ✓

## 2. Captured context is readable (RED-014)

- [x] 2.1 `/context` lists each captured invocation with model/tool counts, enforced tools, budget and mounts. Verify: the workbench test asserts the enforcement facts; experience E15. ✓
- [x] 2.2 `/context <node>#<n>` drills into one invocation: objective, expected output, initial policy and human message, layer identities/hashes/sizes **and bounded content excerpts**, requested versus enforced tools, budget, output schema, roots, mounts, activity, coverage strip and the NOT RETAINED label. Verify: the workbench test asserts the detail fragments; experience E15. ✓

## 3. One-command evidence

- [x] 3.1 `make tui-experiences` runs the fifteen-journey suite and `make debugger-proof` runs the five-lane chain. Verify: `make debugger-proof` exits 0 with every lane green. ✓

## 4. Gates

- [x] 4.1 Run the plan gate for this change, then `--phase closeout`, `UV_OFFLINE=1 make verify`, `make tui-journey`, `make debugger-proof`, `openspec validate --strict`, `git diff HEAD --check` and `check_doc_hygiene.py`, measuring every exit code directly. Verify: every measured exit code is 0. ✓
