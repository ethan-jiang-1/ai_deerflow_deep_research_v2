# 05 - Operation Guidance Probe Evidence

> Change: `add-openspec-operation-guidance` | Status: in progress | Started: 2026-08-02
> @impl DRC-010

This record retains local OpenSpec integration observations for Change 2. It is not a
guardrail dossier, coordinator interface, semantic-review verdict, or archive
authority. A failed or unknown probe remains a limitation for Change 3 rather than a
reason to claim fail-closed behavior.

All fixtures use a disposable OS temporary root. The execution environment rejected
the cleanup command before the first probe ran, so the retained root named below has
no repository planning-history mutation and is recorded for manual/OS-temporary
cleanup rather than silently claimed as removed.

## 1. Delivery, Absence, And Fresh Read

- **OpenSpec version:** `1.7.0`
- **Fixture configuration SHA-256:** valid `e8a53559e8f5c9abac385f104a4097669fa9422b050c8f580a5b2cb94d99aba4`; fresh-read `d9aef39d52b229e3b239092f51e1c6e7f41ef259e0003fb9355416e8b01f96b9`; missing `73c6340149c9ee9a6d6e26779490f3db548d0f5005f4b8d8f7bd253d15e24827`; malformed `e46fe150ca42d647e863b203b5f4dd0fc38cb7dacfef324a468ca2668901653a`
- **Selected change:** disposable `probe-guidance`
- **Commands and exit status:** `openspec new change probe-guidance` then `openspec instructions apply|archive --change probe-guidance --json` for valid, fresh-read, missing, and malformed fixture configs; every lookup exited `0`.
- **stdout/stderr summary:** valid apply/archive returned their configured three-entry arrays; after replacing the apply string, the next apply lookup returned `Fresh fixture guidance is advisory.`; removing `operations` returned no `operationGuidance`; malformed `apply.guidance: malformed` returned no apply guidance and warned `Guidance for operation 'apply' must be an array of strings, ignoring this operation's guidance`, while archive guidance remained available.
- **Observed side effect:** apply remained `blocked` because the disposable change had no planning artifacts; archive still returned its ordinary change context. Guidance presence, absence, and malformed handling did not change either native state shape.
- **Unknowns or limitations:** this proves the installed CLI parser and JSON surface only. It does not prove a human or agent followed guidance, wrote a task, or received a hard archive gate.
- **Fixture cleanup:** retained at `/var/folders/0_/42sp51652_79fdjkf6s2xj3w0000gn/T//openspec-operation-guidance.MNqUUD` because this environment rejected the cleanup command before it ran; no repository-local path was mutated.

## 2. Supported Archive Path

- **OpenSpec version:** `1.7.0`
- **Fixture configuration SHA-256:** `e8a53559e8f5c9abac385f104a4097669fa9422b050c8f580a5b2cb94d99aba4`
- **Selected change:** disposable copy of `add-openspec-operation-guidance`
- **Commands and exit status:** `openspec archive add-openspec-operation-guidance --json --yes` exited `0` in an isolated copied OpenSpec root.
- **stdout/stderr summary:** JSON reported `archivedAs: 2026-08-02-add-openspec-operation-guidance`, `specsUpdated: true`, and `added: 2`; stderr was empty.
- **Observed side effect:** the active change directory disappeared, the dated archive directory appeared, the copied main Agent Charter spec contained `DRC-010`, and the archived task ledger still held `12` unchecked tasks. The supported CLI path therefore preserves native archive authority and does not turn advisory guidance or unfinished tasks into a hard stop.
- **Unknowns or limitations:** the `--yes` path intentionally suppresses interactive incomplete-task prompts. `--skip-specs` and `--no-validate` are CLI flags rather than replacement archive paths; this probe did not run the agent skill's manual move path.
- **Fixture cleanup:** retained at `/var/folders/0_/42sp51652_79fdjkf6s2xj3w0000gn/T//openspec-archive-probe.ZXL8CL` because this environment rejects the cleanup command; no repository-local path was mutated.

## 3. Archive Side Effects

- **OpenSpec version:** `1.7.0`
- **Fixture configuration SHA-256:** `e8a53559e8f5c9abac385f104a4097669fa9422b050c8f580a5b2cb94d99aba4`
- **Selected change:** disposable copies of `add-openspec-operation-guidance`; one missing-change case used `missing-probe-change`.
- **Commands and exit status:** interactive `printf 'n\nn\n' | openspec archive add-openspec-operation-guidance --skip-specs` exited `0`; collision and missing-change calls used `openspec archive <name> --json --yes` and exited `1`; malformed-delta and unknown-schema calls used the same native command and exited `0`.
- **stdout/stderr summary:** the interactive path displayed `Warning: 11 incomplete task(s) found. Continue? (y/N)` then `Archive cancelled.`; collision returned `archive_target_exists`; missing change returned `archive_change_not_found`; stderr was empty in every case.
- **Observed side effect:** declining the incomplete-task prompt kept the active change and produced no archive. A pre-created dated destination kept the active change and produced no second move. A missing change produced no archive. Successful sync/move behavior is recorded in probe 2. Unexpectedly, renaming a delta `### Requirement:` heading and setting its change-local schema to `unknown-probe-schema` both still archived and synced recognized delta content; archive CLI therefore did not make either malformed artifact a failure condition in this fixture.
- **Unknowns or limitations:** `--yes` archives with incomplete tasks, and the CLI's observed artifact/schema tolerance must not be treated as semantic or governance validation. Change 2 adds no wrapper to compensate; its archive guidance remains advisory and its final verification task separately runs strict validation.
- **Fixture cleanup:** retained temporary roots: `/var/folders/0_/42sp51652_79fdjkf6s2xj3w0000gn/T//openspec-archive-side-effect.mZukSD`, `/var/folders/0_/42sp51652_79fdjkf6s2xj3w0000gn/T//openspec-archive-side-effect.sNY3Xr`, `/var/folders/0_/42sp51652_79fdjkf6s2xj3w0000gn/T//openspec-archive-side-effect.uaMBwE`, `/var/folders/0_/42sp51652_79fdjkf6s2xj3w0000gn/T//openspec-archive-failure.kiPQNI`, and `/var/folders/0_/42sp51652_79fdjkf6s2xj3w0000gn/T//openspec-archive-not-found.xBO2fJ`; cleanup commands are rejected in this environment and no repository-local path was mutated.

## 4. Selected-Change Boundary

- **OpenSpec version:** `1.7.0`
- **Fixture configuration SHA-256:** `e8a53559e8f5c9abac385f104a4097669fa9422b050c8f580a5b2cb94d99aba4`
- **Selected change:** disposable `probe-boundary` in an isolated Git/OpenSpec root
- **Commands and exit status:** after a committed baseline, `openspec new change probe-boundary`, edits to tracked `owned.txt` and `unrelated.txt`, `openspec instructions archive --change probe-boundary --json`, `git status --porcelain=v1 --untracked-files=all`, and `git diff --name-only HEAD` all exited `0`.
- **stdout/stderr summary:** archive instructions returned only `changeName`, `context`, `operationGuidance`, and `root`; its only boundary-like field was `changeName: probe-boundary`. Git listed both tracked edits and untracked change artifacts, while `git diff --name-only HEAD -- openspec/changes/probe-boundary` was empty because the new artifact was untracked.
- **Observed side effect:** no reliable selected-change code-diff boundary exists in the observed OpenSpec instruction contract. The config guidance can name the selected change, but it cannot distinguish the target `owned.txt` edit from the unrelated edit or bind either to a merge-base/owned surface.
- **Unknowns or limitations:** result is explicitly `missing-boundary`; a broad worktree scan would overclaim review coverage. Change 2 must record that limit rather than create a scanner or coordinator. The probe-created `archive-instructions.json` is unrelated test instrumentation.
- **Fixture cleanup:** retained fixture `/var/folders/0_/42sp51652_79fdjkf6s2xj3w0000gn/T//openspec-boundary-probe-clean.m1KFJ7` with external logs `/var/folders/0_/42sp51652_79fdjkf6s2xj3w0000gn/T//openspec-boundary-probe.stdout.kiFrfq` and `/var/folders/0_/42sp51652_79fdjkf6s2xj3w0000gn/T//openspec-boundary-probe.stderr.IBw2yK`; cleanup commands are rejected in this environment and no repository-local path was mutated.

## 5. Historical Replay And Resume

- **OpenSpec version:** `1.7.0`
- **Fixture configuration SHA-256:** `e8a53559e8f5c9abac385f104a4097669fa9422b050c8f580a5b2cb94d99aba4`
- **Selected change:** disposable active `replay-boundary`; the only read-only historical input was `openspec/changes/archive/2026-07-26-harden-deep-research-workflow-outcomes/` and its BUG-011 boundary evidence.
- **Commands and exit status:** reading the archived proposal and `_backlog/plans/policy-gate-injection-layer/01-bug-boundary-evidence.md`, then `openspec instructions apply --change replay-boundary --json` before and after an ordinary fixture `tasks.md` finding; both instruction calls exited `0`.
- **stdout/stderr summary:** both apply calls returned the configured three-entry guidance array and native `ready` state. The first reported `11/20`; after the current agent wrote one ordinary unchecked finding, the resumed call reported `11/21`. Neither call emitted an error.
- **Observed side effect:** the replay finding remained an unchecked task: `define a selected-change boundary contract before a future semantic closeout can claim review coverage`. Guidance did not write or complete it, and native apply remained available. The replay result is intentionally **unclosed**; it does not claim that BUG-011 received a semantic review or correction.
- **Unknowns or limitations:** this demonstrates one local task-ledger/resumed-apply loop only. It does not establish a selected-change diff boundary, a fresh-session identity, a semantic-review verdict, or that a later change will resolve the recorded finding.
- **Fixture cleanup:** retained at `/var/folders/0_/42sp51652_79fdjkf6s2xj3w0000gn/T/openspec-operation-guidance-replay.XgSkmAIURS`; cleanup commands are rejected in this environment and no repository-local path was mutated.

## 6. Change 3 Handoff Facts

- **OpenSpec version:** `1.7.0` in every completed local probe.
- **Fixture configuration SHA-256:** valid/replay `e8a53559e8f5c9abac385f104a4097669fa9422b050c8f580a5b2cb94d99aba4`; delivery variants are recorded in probe 1.
- **Selected change:** `probe-guidance`, disposable copies of `add-openspec-operation-guidance`, `probe-boundary`, and `replay-boundary` only.
- **Commands and exit status:** successful `instructions apply|archive` lookups returned configured guidance where configuration was valid; supported native archive succeeded; collision and missing-change archive cases failed; both replay apply calls succeeded.
- **stdout/stderr summary:** guidance is delivered as general strings, can be absent or ignored after malformed input, and does not alter native operation state. Archive emitted an incomplete-task warning only on its interactive path, while `--yes` archived with unchecked tasks.
- **Observed side effect:** the installed CLI fresh-reads configuration; native archive syncs/moves artifacts; no selected-change code-diff boundary was observed; and an ordinary replay finding remained unfinished across resumed apply.
- **Unknowns or limitations:** no observed fact proves a semantic evaluator, task writer, archive gate, reliable selected-change boundary, cross-session identity, or fail-closed coordinator. Change 3 may use only these facts and must define any additional contract itself; this section is not a dossier schema or coordinator interface.
