# Accepted-Contract Contradiction Audit

During apply, the active delta named below is the pending owner for behavior it modifies.
The corresponding main-spec wording remains the accepted historical baseline until sync;
it must not be used to restore a second lifecycle authority. Every requirement named in
task 1.6 is accounted for below.

| Accepted requirement(s) with old term/authority | Owning active delta | Apply reading rule | Direct proof |
| --- | --- | --- | --- |
| `DPL-001`, `DPL-004`, `DPL-005`, `DPL-007` | `demo-pipeline` | Canonical Harness root and shared Bundle lifecycle result replace demo-derived id/path/session recovery. | demo adapter and root contract tests |
| `EVH-005`, `EVH-010` | `evaluation-hardening` | Complete verification and ownership scans move to one canonical root; root-sensitive scans must fail closed. | asset/requirement detector tests |
| `NOA-007` | `node-agent-runtime` | Node-agent error/category behavior stays, but the bridge may not select a Bundle/checkpoint/State writer. | node-agent bridge contract |
| `PRS-001`, `PRS-004`, `PRS-005`, `PRS-006`, `PRS-011`, `PRS-014`, `PRS-015` | `project-structure` | `deep_research_harness/` replaces the only active physical root; fixture/evaluation separation remains explicit. | architecture checker and root detector |
| `REC-004`, `REC-005`, `REC-006` | `research-cli-onboarding` | CLI accepts/projects only `bundle_id` from a shared outcome and never an inspection path or recovery identity. | CLI/demo lifecycle tests |
| `RED-002` | `research-demo-tui` | Demo root and `.env` path move; TUI remains a projection only. | demo TUI contract |
| `FCO-001` | `research-fake-cli-onboarding` | Fake onboarding paths move and fixture output cannot create a real control target. | fake CLI/demonstration tests |
| `RER-001`, `RER-002`, `RER-003`, `RER-006`, `RER-007`, `RER-009` | `research-run-experience` | All display facts derive from the typed Bundle result; pending/cache/diagnostic data cannot authorize control. | run-experience contracts |
| `RUS-001`, `RUS-002`, `RUS-003`, `RUS-004`, `RUS-006` | `research-run-session` | Retained manifests/traces/diagnostics become observations only and cannot recover a missing Bundle. | run-session/loss tests |
| `RWB-001`, `RWB-002`, `RWB-003`, `RWB-005`, `RWB-006`, `RWB-007` | `research-local-session-workbench` | Workbench submits only lifecycle-projected Bundle controls and has no broker/index/checkpoint fallback. | workbench contracts/integration |
| `RUI-001`, `RUI-002`, `RUI-003`, `RUI-004`, `RUI-006`, `RUI-007`, `RUI-008`, `RUI-009` | `runtime-integration` | Preserve generic `infra_probe`; Deep Research actions use trusted scope plus Bundle-local State, never a derived research namespace or external checkpointer. | tool/replay/loss tests |
| `REG-004`, `REG-005`, `REG-006`, `REG-007`, `REG-009`, `REG-010`, `REG-011`, `REG-012`, `REG-013`, `REG-014`, `REG-016` | `research-graph-lifecycle` | Bundle-local State replaces external checkpoint authority; `resume` stays correlated and `refine` is separately admitted at a safe point. | state/reducer/lifecycle tests |
| `HIN-001`, `HIN-002`, `HIN-004`, `HIN-005` | `hitl1-node` | Profile, pending correlation, and requests live in the selected Bundle State/content; graph interrupt is delivery only. | HITL1 node/lifecycle tests |
| `WOU-001`, `WOU-003`, `WOU-004`, `WOU-005`, `WOU-006`, `WOU-009` | `work-unit-kernel` | Controller/work/evidence paths resolve only from a runtime-bound Bundle reference and fail on loss. | work-unit containment/loss tests |

## Intentional Unaffected Facts

- The generic `infra_probe` checkpoint namespace remains its own non-Deep-Research
  infrastructure contract. It cannot select or recover a Run Bundle.
- Cognitive Evaluation retains its separate workspace and Bundle contract. It is not a
  candidate in Deep Research scoped discovery.
- Historical archives retain factual old paths and checkpoint topology. They are not
  active command, control, configuration, or specification authority.

## Result

No current accepted requirement remains without an active owning delta or intentional
unaffected rationale. The remaining non-spec terminology mismatch in `CONTEXT.md` and
ADR-0028 is separately tracked in task 1.7; it is not treated as an alternative
lifecycle contract.

## Post-root Re-audit (2026-08-06)

The post-move inventory used `rg -n 'research_id|bundle_directory|deerflow_research/'
deep_research_harness openspec`. There are no matches in Deep Research production,
control, configuration, or current root-consumer paths that make a retired identity,
locator, checkpoint, session, binding, or index authoritative.

The remaining matches are classified as follows:

- `deep_research_harness/docs/release-attestation-2026-07-17.json` and its asset/test
  reader preserve the factual source scope of the historical 2026-07 attestation.
- Current deterministic tests retain retired spellings only as negative rejection,
  historical-attestation, or structural-detector fixtures; none can select, recover,
  or recreate a Run Bundle.
- This active delta and its pre-apply impact inventory quote retired vocabulary to
  prohibit it and preserve the before-state audit; those documents are not runtime
  control surfaces.
- Accepted main specs still contain their pre-sync baseline wording. The active delta
  above is their pending owner until the normal sync/archive step; mass replacement of
  those baselines would incorrectly bypass OpenSpec's delta workflow.
- `openspec/changes/archive/**` remains historical material and is outside current
  control/configuration authority.
