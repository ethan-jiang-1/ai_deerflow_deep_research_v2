# Adjustment Record - C-010.c Dedicated TUI And Local-First Status

- Status: verified
- Authority owner: `deployment-configuration` owns the current Dedicated Agent and
  reflected `deep_research` tool route.
- Affected paths: `deep_research_harness/CONTEXT.md` only.
- Before (current wording): Primary User Interface is planned and Local-First
  Deployment is described as the first product scope for a dedicated TUI.
- After (applied adjustment): the dedicated Primary-User TUI and that Local-First
  product route are `dormant`, while the current Dedicated Agent/reflected-tool route
  remains explicitly current.
- Reason and evidence: user-approved C-010.c disposition; demo TUI and local evaluation
  remain separate contributor/operator surfaces.
- Main risk: dormant may be read as cancellation or may accidentally downgrade current
  demo/evaluation surfaces.
- Possible side effects: readers see current and dormant routes together and must use
  the current-route entry for present operation.
- Risk controls / stop condition: define dormant as historical route without active
  commitment; do not alter demos, evaluation, UI code, or historical ADR body. Stop if
  any runtime behavior or product promise must change.
- Verification before apply: current route requirement and C-010.c review reread.
- Verification after apply: all current glossary and ADR dispositions use `dormant` for
  the historical TUI/Local-First route while retaining the current Dedicated Agent and
  reflected-tool wording; no demo or evaluation surface is relabeled.
- Observed side effects (including evidence bound): none observed in the scoped
  documentation diff. This status does not cancel a future reactivation or alter any UI
  behavior.
- Remaining mismatch / follow-up owner: a future reactivation requires a new product
  change.
- Authorization and date: user authorized Stage 2 apply on 2026-08-13.
