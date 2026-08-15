# Historical Parity Report Provenance Comparison

This record closes task 3.1 before the superseded report is removed. It compares
the factual provenance and failure statements in the now-deleted historical parity
report with their retained owners. It does not rewrite any frozen evidence payload.

| Retired report fact group | Retained owner | Retained route | Disposition |
| --- | --- | --- | --- |
| The report is a pre-acceptance 2026-07-17 snapshot, not a current verdict | evaluation-hardening historical baseline | `docs/live-evaluation-baseline-2026-07-17.md` classification and first canary table | Retain as dated, non-blocking observation provenance. |
| The original live result was two passing short prefixes and one Wave0 failure after three bounded attempts, with no accepted record | evaluation-hardening historical baseline | `docs/live-evaluation-baseline-2026-07-17.md` first canary table and provider-only observations | Retain the exact observed failure, token/tool/time data, and its non-release status. |
| The four 2026-07-17 reproducible defects were repaired at deterministic seams | evaluation-hardening regression policy | `docs/regression-descent.md` rows `LIVE-20260717-01` through `LIVE-20260717-04` | Retain each exact collected regression route; the baseline narrates the same four descents. |
| Wave0 model/tool-selection behavior was provider-only and must not be fabricated as deterministic coverage | evaluation-hardening regression policy | `docs/regression-descent.md` row `LIVE-20260717-05` | Retain the bounded live rationale and explicit `provider-only-live` classification. |
| Deterministic proof does not substitute for provider behavior, end-to-end report quality, or a full-real completion | evaluation-hardening historical baseline and regression policy | `docs/live-evaluation-baseline-2026-07-17.md` provider-only and evidence-v1 sections; `docs/regression-descent.md` workflow | Retain the non-overclaim boundary and lowest-seam descent rule. |
| The old report's `NOT READY` and `full-real not executed` statements are historical, not a current release claim | evaluation-hardening historical baseline and accepted attestation | `docs/live-evaluation-baseline-2026-07-17.md`; `docs/release-attestation-2026-07-17.json` | Retain the old partial observation separately from the later accepted run; do not merge epochs. |
| The later full-real normal lifecycle had accepted evidence, final artifacts, citation bindings, contained paths, cleanup, isolated checkpoint, and terminal completion | evaluation-hardening accepted release attestation | `docs/release-attestation-2026-07-17.json` `source_run.hard_invariants` and run counts | Retain the accepted historical run with its source date, hash, and schema. |
| Full-real archive diagnostics were credential-free and raw-host-path-free | evaluation-hardening accepted release attestation | `docs/release-attestation-2026-07-17.json` `attestation_scan` and `source_archive_scan` | Retain the redaction result as the accepted run's own fact. |
| Later provider failures and future repair work require an exact collected regression or an explicit live-only rationale | evaluation-hardening regression policy | `docs/regression-descent.md` table and workflow | Retain current policy without using a historical success to close later discoveries. |
| The imported workflow authority/parity table summarizes current deterministic behavior; it is not an independent provenance or failure record | evaluation-hardening specification and central evidence catalog | `openspec/specs/evaluation-hardening/spec.md`; `tests/assets/evidence.py` | Keep the behavior under its current normative/evidence owners. No consumer needs the retired prose as a separate authority. |

Every retired provenance or failure fact has a retained owner. The report and its
shape-only contract may therefore be removed once a replacement-route assertion
passes and inbound references are absent.
