## 1. Charter principle

- [x] 1.1 Add "Cognitive Programs Are The First Modification Seam" as a numbered
  principle directly after the "8. Operation Guidance Is Advisory" principle in
  `openspec/governance/agent-charter/charter.md` (it becomes principle 9; anchor by
  the preceding principle's title, not by a hard-coded number). Done condition: the
  principle names the two-part node program, states the cognitive control program is
  the first modification seam for a node-behavior symptom, rejects the deterministic
  shell as a substitute repair site, and records that `run_agent` presence is
  current-mechanism evidence, not a node's product identity. The charter's authority
  statement is unchanged.

## 2. Local-context policy seam rule

- [x] 2.1 Add a "Seam classification" subsection to
  `openspec/governance/agent-charter/policies/local-context.md`: a node-behavior
  symptom routes first to the cognitive-program seam; a symptom-to-first-seam table
  covers wrong role/model-visible policy, wrong context/tool posture, malformed or
  misaligned candidate/feedback, unexpected admission, and wrong route/terminal; a
  cognitive-program edit states its cognitive hypothesis and observable result.
  Done condition: policy text present and consistent with the charter principle and
  the DRC-002/DRC-004 delta.
- [x] 2.2 Add the required `Seam classification` field (closed values
  `cognitive-program | human-decision | deterministic-guardrail | wiring`) to the
  policy's Focus Card section. Done condition: field and closed values stated; the
  field value is written bare (no backticks, no punctuation inside the value); the
  policy notes the checker enforces presence, closed-value membership, and a
  non-empty rationale while the policy owns the canonical closed values and the
  substantive cognitive-hypothesis / deterministic-owner requirements.

## 3. Charter checker and contract test

- [x] 3.1 Add `Seam classification` to `FOCUS_FIELDS` in
  `openspec/governance/check_agent_charter.py` and to the mirror set in
  `deep_research_harness/tests/contract/test_agent_charter_governance.py`, and add a
  closed-value membership check plus a non-empty-rationale check for the field
  (mirroring the existing control-placement `Design posture` closed-value
  validation). The test helper `_focus_card` special-cases a valid bare default seam
  value (`deterministic-guardrail`) instead of the generic `fixture` placeholder.
  Done condition: the checker rejects a proposal whose Focus Card omits, leaves
  empty, uses a value outside the closed set for, or supplies no rationale after
  `Seam classification`; the contract test mirrors the extended field set and passes,
  with closed-value rejection and acceptance tests for each seam value.
- [x] 3.2 Add the seam-declaration line to the in-flight
  `openspec/changes/calibrate-real-demo-model-contracts/proposal.md` Focus Card
  (bare value `Seam classification: deterministic-guardrail` with a short rationale
  naming the Journal/attribution evidence and the unchanged deterministic owners). Done
  condition: `openspec change validate --strict` passes for that change and the
  charter checker accepts its Focus Card.

## 4. CONTEXT.md vocabulary and decision

- [x] 4.1 Add six canonical terms to the "Node Agent Control" section of
  `deep_research_harness/CONTEXT.md` (Product Responsibility, Participation Mode,
  Commitment State, Current Operating Mechanism, Current Model-Branch Evidence,
  Seam Classification), each with a one-to-two-sentence definition and `_Avoid_`
  line, without duplicating the existing Deterministic Control Boundary term. Done
  condition: terms follow the file's existing tight-definition format and cluster
  under the existing "Node Agent Control" heading.
- [x] 4.2 Append a decision section "# The Cognitive Control Program Is The First
  Modification Seam" in the file's existing `---\n# <decision>` convention. Done
  condition: the section records the seam-first rule, its ordering, and pointers to
  the archived plan and the local-context policy.

## 5. Focus-gate pointer and authoring route

- [x] 5.1 Add a 2–3 line seam-first pointer inside the focus gate of
  `deep_research_harness/AGENTS.md`, before
  `<!-- END: DEEP-RESEARCH-FOCUS-GATE -->`. Done condition: the file stays under
  the 120-line warning budget; the focus-gate markers, charter link, routing table,
  and context-expansion sentence remain intact (charter checker passes).
- [x] 5.2 Add the seam field to the Focus Card authoring rule in
  `openspec/config.yaml`: both the `## Start A Local Change` step 4 field list in
  `context` and the first `rules:proposal` Focus Card rule. Done condition: the file
  stays under the 180-line reject budget and the existing `config.focus_rule_missing`
  / triggered-policy fragment checks still pass.

## 6. Spec delta

- [x] 6.1 Confirm the MODIFIED DRC-002 (symptom-routing SHALL and scenario) and
  MODIFIED DRC-004 (seam-classification SHALL and scenarios) in
  `openspec/changes/embed-cognitive-seam-first-discipline/specs/deep-research-agent-charter/spec.md`
  carry the full updated requirement blocks. Done condition:
  `openspec change validate --strict` passes and `git diff --check` is clean.

## 7. Verification and stop

- [x] 7.1 Run `make governance` from `deep_research_harness/`, the charter checker
  contract test, `openspec change validate --strict`, and `git diff --check`. Done
  condition: every check attributable to this change passes and results are recorded
  in the closeout; the pre-existing `check_project_reqs` failure (unregistered
  DPL-011/012, NOA-015, REJ-006/007, TOP-009, WAN-010, all from the in-flight
  `calibrate-real-demo-model-contracts` unarchived delta) is recorded as an external
  blocker, not as a failure of this change, and is expected to clear when that change
  archives. **STOP**: do not archive or commit until the user authorizes apply.
