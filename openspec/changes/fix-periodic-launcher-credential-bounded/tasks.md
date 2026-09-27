# Tasks

## 1. Red (already demonstrated — record it)

- [x] 1.1 Red evidence exists and is cited: the scenario fails at the
      launcher stage on every credential-free machine — CI run 36354099368
      (readiness reports `尚未找到可用的模型配置` where the test asserts
      `本地前提检查已就绪`) and the 2026-09-28 local run (fails the same
      way). The failing stage is documented in BUG-074.

## 2. Fix the launcher stage (Option B, after the fake-credential experiment rejected Option A)

- [x] 2.1 Experiment measured and rejected: injected fake credentials let
      readiness pass but drove `topic_planning` into a REAL model call
      (HTTP 401, `provider.authentication_failed`) — the ready-then-blocked
      journey is unsatisfiable offline; recorded in design.md.
- [x] 2.2 Replace the unsatisfiable assertions with the honest not-ready
      journey: model configuration not ready with remediation guidance, the
      ready summary ABSENT, non-zero exit, credential names never echoed.
- [x] 2.3 Local run boundary recorded (see evidence/local-environment-note.md):
      the heavy launcher-chain scenario hangs non-deterministically under this
      DSH sandbox (four different hang points across seven probes; once the
      chain completed far enough to prove the assertions' target output), while
      the file's sibling scenario passes locally in 19s. Local green for this
      scenario is UNVERIFIABLE here; CI is the acceptance environment (task 3.4).

## 3. Lane and gates

- [x] 3.1 Periodic lane target cannot run to completion under this sandbox
      (same non-deterministic hang); the sibling scenario passes locally and
      the fixed scenario's assertions match the CI-proven not-ready output
      byte for byte. Lane acceptance moves to CI (3.4).
- [x] 3.2 Full gates: `UV_OFFLINE=1 make verify`, closeout gate, governance
      suite, doc hygiene, dependency direction — all zero; commit.
- [x] 3.3 Close BUG-074: move the card to `_done/_fixed_bugs/`, update the
      three indexes, and note the fix in the card.
- [x] 3.4 Push and watch the entry-environment CI workflow — its first green
      run in history is this change's acceptance.
