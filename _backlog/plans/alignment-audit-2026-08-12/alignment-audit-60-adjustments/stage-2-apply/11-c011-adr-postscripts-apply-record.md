# Adjustment Record - C-011 ADR Status And Applicability Postscripts

- Status: verified
- Authority owner: each linked current owner/route named in the approved design table;
  ADRs retain historical rationale only.
- Affected paths: ADRs 0002, 0003, 0006, 0008, and 0010 only.
- Before (current wording): each ADR contains only its historical title/body, with no
  dated current-status/applicability boundary.
- After (applied adjustment): one uniform dated `2026-08-13` postscript is appended to
  each ADR. It preserves each historical byte prefix and makes only the listed
  current/dormant/planned/non-current sub-decision boundary.
- Reason and evidence: user-approved C-011 review and change design decision 6.
- Main risk: a postscript could be mistaken for rewriting history or deciding A-004.
- Possible side effects: tooling/readers may need to distinguish historical body from
  the postscript; the postscripts add current-owner links to navigate.
- Risk controls / stop condition: append only after recording the exact pre-append byte
  length/SHA-256 below; preserve prefix byte-for-byte. Stop if a prefix differs, an
  existing user append is present, or A-004 semantics are needed.
- Verification before apply: `git diff` is empty for all five ADRs and their baseline
  measurements below were captured.
- Verification after apply: all five recorded byte prefixes SHA-256-match their
  pre-append measurements, and each added suffix begins with the approved dated heading.
  The five designated relative target files exist; 0002's named heading and 0006's
  terminology/status entry also exist.
- Observed side effects (including evidence bound): no historical title/body byte
  changed, as shown by the recorded-prefix checks. The postscript adds documentation
  navigation only; it does not alter runtime authority.
- Remaining mismatch / follow-up owner: Bundle-loss Support Handoff behavior remains
  `reconcile-post-loss-diagnostic-authority`.
- Authorization and date: user authorized Stage 2 apply on 2026-08-13.

## Pre-Append Measurements

| ADR | Bytes | SHA-256 | Approved current-owner/route target |
| --- | ---: | --- | --- |
| 0002 | 738 | `0b017ebbd399e32392b8db4429667bad21b1894673662bd113fd91f70e2b771c` | `../../../openspec/specs/deployment-configuration/spec.md#requirement-dedicated-agent-is-provisioned-in-the-effective-user-scope` |
| 0003 | 504 | `ee0515b5e2cddacde2ea0a93cd43546e4fa6e41a607547a64493819266678e7d` | `../../../openspec/specs/deployment-configuration/spec.md` |
| 0006 | 519 | `9bf8806d572855e2dff8e4e6d090e93026e64f0a5454d5b92ee213dbfcc48404` | `../../CONTEXT.md#support-handoff` terminology/status entry only |
| 0008 | 553 | `9ac764273890f0543b9f5a6d64ff63752d48ffc746a8de31aa6b4e8039941778` | `../../../openspec/specs/deep-research-harness-run-bundles/spec.md` |
| 0010 | 389 | `5da11696063e8654610f31621c77f665f23ee8efa37db7335a336818b68946f1` | `../../../openspec/specs/final-delivery-node/spec.md` |
