# Adjustment Record - C-005.b Archived Change Dependency

- Status: verified
- Authority owner: `openspec/policies/local-context.md` for current seam routing.
- Affected paths: `deep_research_harness/CONTEXT.md` only.
- Before (current wording): the cognitive-control paragraph says its discipline comes
  from the archived `node-agent-cognitive-loop-governance-progressive-plan`.
- After (applied adjustment): the paragraph retains the seam-first discipline and
  current `local-context` policy link without presenting an archived change as current
  authority.
- Reason and evidence: C-005.b approved separating historical provenance from current
  rule ownership; the extant policy is the current route.
- Main risk: retiring the citation could erase the actual seam rule or modify history.
- Possible side effects: historical provenance is no longer named in the glossary and
  must be found through archive/ADR/Git history instead.
- Risk controls / stop condition: alter only the current sentence; do not edit archived
  material. Stop if no current owner can be named.
- Verification before apply: current policy target exists and source paragraph was read.
- Verification after apply: scoped diff removes only the archived change citation; the
  relative `local-context` policy target remains present.
- Observed side effects (including evidence bound): none observed in the current
  glossary and link check. Historical provenance remains available only through its
  unchanged history, which this static review does not exhaustively catalog.
- Remaining mismatch / follow-up owner: none within this occurrence; historical archive
  remains intentionally unchanged.
- Authorization and date: user authorized Stage 2 apply on 2026-08-13.
