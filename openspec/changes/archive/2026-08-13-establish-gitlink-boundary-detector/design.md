## Context

See [proposal.md](proposal.md) for the motivation and Focus Card, and the delta
`project-structure` specification for the behavioral contract. The current architecture
registry describes downstream paths and its checker validates structure/import rules,
but the root `deerflow/` gitlink is only manually observed in closeout records. Current
Git metadata records a stage-zero gitlink at `deerflow` with commit
`66b9e7f21212490cf92fafac137542b9deb06615`; this observation is the initial registry
lock candidate, not a claim about DeerFlow behavior or compatibility.

The existing architecture checker and its focused contract tests are the smallest
responsible deterministic seam. The detector must therefore extend that boundary
rather than create a new archive coordinator, runtime component, or generic submodule
manager.

## Goals / Non-Goals

**Goals:**

- Make the declared upstream path, root index gitlink, nested checked-out commit, and
  nested cleanliness one mechanically checked repository-structure fact.
- Preserve a deliberate, reviewable path for a future upstream bump without allowing a
  detector to mutate or approve it.
- Use hermetic parent/nested Git metadata fixtures and retain the existing live checker
  as the widest deterministic integration proof.

**Non-Goals:**

- Inspect, parse, import, modify, or test DeerFlow source.
- Require an unrelated root worktree to be clean, infer a release/compatibility claim,
  inspect remotes/history/configuration, or manage generic submodules.
- Add archive-blocking behavior, an OpenSpec extension, a runtime safeguard, a new
  command, or an automatic gitlink bump workflow.

## Decisions

### 1. Register one lock under the existing structure authority

Add one `[upstream_gitlink]` registry table with exactly two keys: `path = "deerflow"`
and its full lower-case 40-hex `commit`. The parser will model this as a small immutable
boundary record alongside the existing `StructureManifest`; it will reject an absent
table, an unexpected key, an extra table value, an unnormalized/escaping path, or a
malformed identifier before invoking Git. Static parsing applies in both full and
`--imports-only` modes; metadata validation applies only in full mode.

The corresponding new `PRS-018` ID is allocated in the requirement registry during
apply before it appears in the accepted main spec, code annotations, or evidence
catalog. The active delta may name that pending ID while planning is reviewed.

**Alternative considered:** derive a lock from `.gitmodules`, the nested branch name,
or a Git remote. These are configuration/history facts, can be absent or mutable, and
do not name the exact checkout boundary; they are rejected.

### 2. Check metadata in a closed, ordered sequence

The full architecture checker will validate the boundary after parsing the registry and
before reporting project success. Existing full-check import validation scans only the
registry's legacy `backend`/`frontend` roots, not `deerflow/`; the new boundary adds no
DeerFlow-source traversal. A small helper will use fixed Git argument vectors and the
validated literal repository-relative path, then evaluate these closed conditions in
order:

1. `lstat` confirms the declared path exists as a non-symlink directory.
2. `git -C <root> ls-files --stage -z -- deerflow` yields exactly one entry at stage
   zero with mode `160000` and the expected identifier.
3. `git -C deerflow rev-parse --verify HEAD` resolves exactly the expected identifier.
4. `git -C deerflow status --porcelain=v1 --untracked-files=all` is empty.

Every nonzero exit or unexpected output shape is a distinct closed condition. Every Git
invocation is read-only and bounded to metadata output. The implementation must not
call `git submodule update`, `checkout`, `reset`, `add`, `clean`, `diff` over content,
a recursive file walk, a remote query, a log/history command, or any DeerFlow-source
reader. A focused command-recorder test will assert the evaluator's exact Git vectors.
Diagnostics identify only the boundary condition and declared path; they must not
enumerate nested file names or contents. `--imports-only` parses the static boundary
but does not resolve its filesystem path or invoke Git, preserving its established
isolated import-fixture role.

The root index, rather than the parent repository's committed `HEAD` tree, is the
comparison source because the normal review/apply sequence must be able to validate a
staged intentional pointer+registry update before the final commit. A pointer move
without the matching registry edit, or a matching registry edit without the matching
staged pointer, fails. The checker verifies consistency; OpenSpec review is what
authorizes an intentional bump.

**Alternative considered:** require the parent committed tree to equal the new lock.
That would make the ordinary pre-commit deterministic verification gate fail during a
legitimate reviewed bump. It is rejected.

### 3. Make nested dirtiness a structural gate, not a root-worktree rule

After identity matches, any staged, unstaged, deleted, or untracked nested path causes
a closed failure. This catches local mutations not represented by the parent gitlink
entry. Unrelated files in the parent worktree remain outside this detector: selected
change closeout and ordinary Git review own wider worktree scope.

**Alternative considered:** rely on `git diff --submodule=short` from the parent. Its
summary does not establish the full nested porcelain condition and conflates this
detector with broader change-diff review. It is rejected.

### 5. Keep archive observations supplementary after the detector exists

`openspec/config.yaml` currently routes archive-time root/index/submodule observations
as manual scope and diff evidence. That route remains useful for a human review of the
actual change, but it must no longer say that no automatic protection exists once the
full architecture checker owns the closed metadata validation. The narrow correction
will state that manual observations supplement, rather than replace, the full checker;
neither establishes upstream runtime compatibility or approves an intentional bump.

**Alternative considered:** remove the archive observations after introducing the
detector. The checker deliberately does not review an entire root diff or grant archive
authority, so removing the bounded human scope evidence would leave a separate review
need unmet. It is rejected.

### 4. Use empty-commit temporary Git fixtures

Focused tests will create a temporary parent repository and a temporary nested Git
repository with empty commits, insert a mode-`160000` index entry through Git metadata,
and invoke the existing in-process checker seam. The fixture never copies or reads
DeerFlow files. Bad-boundary cases are the red tests: the current checker accepts them,
so each must first demonstrate that erroneous acceptance. The matching clean case is a
green control. The cases cover bad registry syntax/extra key, ordinary-directory or
symlink placement, missing/non-gitlink/multi-stage root entry, wrong index SHA, nested
`HEAD` drift, metadata-command failure, and nested staged/unstaged/deleted/untracked
dirtiness. An intentional-bump fixture stages a second matching SHA/lock pair without
a parent commit and pairs it with a lock mismatch. Existing test fixtures that construct
minimal structure manifests will gain an explicit valid static boundary or use
`--imports-only`; they may not accidentally bypass the new parser contract.

**Alternative considered:** exercise the real `deerflow/` checkout by changing its
pointer or worktree. It would violate the upstream boundary and risk user state, so it
is rejected.

## Risks / Trade-offs

- [A locally intended upstream bump is initially rejected] -> Require the reviewed
  change to update both the registry lock and root index pointer, document the exact
  pre-commit sequence, and test that matched staged state passes.
- [A focused fixture depends on Git availability/configuration] -> Use only local empty
  repositories, set fixture-local author identity, skip no conditions, and fail with a
  clear test setup error when Git is unavailable; the project already requires Git for
  this repository-level contract.
- [Nested porcelain reports local generated files] -> Treat all nested dirtiness as a
  deliberate closed condition; require cleanup outside the checker rather than hiding
  paths or adding allowlists.
- [The new registry field breaks existing minimal checker fixtures] -> Inventory every
  direct `StructureManifest`/TOML fixture; full-check fixtures create isolated Git
  metadata, whereas import-only fixtures supply a valid static lock without Git.
  Retain dedicated missing/malformed/extra-field rejection tests.
- [Authoring context still denies automatic protection] -> Correct the one archive
  guidance sentence in the same reviewed change, preserving its separate scope/diff and
  compatibility limits.
- [The detector is mistaken for compatibility proof] -> State the metadata-only
  boundary in the spec, registry policy, diagnostics, and task closeout record.

## Migration Plan

1. Obtain separate apply authorization and recapture root/nested Git metadata without
   opening DeerFlow source. Stop on an active overlapping change or unexpected gitlink
   state.
2. Allocate `PRS-018`; add the registry lock and parser model; write the bad-boundary
   red cases before changing the detector.
3. Implement the read-only checker sequence and update all minimal fixtures,
   architecture policy, requirement evidence, and main spec through normal delta sync.
4. Run focused tests, architecture/requirement/Charter/OpenSpec gates, then the full
   deterministic Harness verify gate. Record that the checks do not establish runtime
   compatibility or upstream source conformance.
5. Before archive, rerun root/nested metadata observations and review the exact
   `deerflow` gitlink diff. Roll back by reverting only the registry/checker/evidence
   change; never reset, clean, checkout, or otherwise modify `deerflow/`.
