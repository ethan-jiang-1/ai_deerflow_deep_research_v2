# Adjustment Record - C-010.a Final Report Artifact And Export

- Status: verified
- Authority owner: `final-delivery-node` report publisher/renderer requirements.
- Affected paths: `deep_research_harness/CONTEXT.md` only.
- Before (current wording): `Research Report Export` says a Primary User can reopen,
  copy, or export self-contained Markdown from a retained Run Bundle.
- After (applied adjustment): `Final Report Artifact` retains current
  `final/report.md` as a Bundle artifact and states that its presence does not establish
  a Primary User public reopen/copy/export capability.
- Reason and evidence: final-delivery specification owns report production; no current
  public entry owns report reopen/copy/export.
- Main risk: wording could delete the current artifact or silently create an export
  roadmap promise.
- Possible side effects: the absence of a public report capability is explicit and
  future export needs an independently designed entry, authorization, and retention
  boundary.
- Risk controls / stop condition: retain exact artifact fact; do not call export
  planned or change publisher, Bundle, or public lifecycle API. Stop if a public reader
  contract is needed.
- Verification before apply: final-delivery owner and source term reviewed.
- Verification after apply: scoped diff replaces only the export term with the retained
  artifact fact and does not add a command, reader, or public API.
- Observed side effects (including evidence bound): none observed in the documentation
  diff. The static check does not create or test a public export surface.
- Remaining mismatch / follow-up owner: report access/export is a separate future
  product change if ever approved.
- Authorization and date: user authorized Stage 2 apply on 2026-08-13.
