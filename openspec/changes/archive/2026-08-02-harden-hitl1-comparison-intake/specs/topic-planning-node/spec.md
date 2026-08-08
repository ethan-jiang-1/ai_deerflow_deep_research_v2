## ADDED Requirements

### Requirement: Topic planning consumes confirmed comparison and language constraints directly

When a confirmed HITL1 profile contains comparison subjects and request/output-language
facts, real topic planning SHALL read those typed facts from checkpoint profile fields
and include them in both its initial and structured-repair assignments. It SHALL use
the accepted output/interaction language for planning communication and shall preserve
the exact two comparison subjects as scope constraints. It SHALL NOT derive, translate,
substitute, or infer a comparison pair or language from `request_text`,
`must_answer_questions`, request-bundle content, or prior model prose.

#### Scenario: Confirmed Chinese comparison reaches planning unchanged
- **WHEN** HITL1 accepts a Chinese profile comparing lithium-ion batteries with
  vanadium redox flow batteries
- **THEN** topic planning receives the exact typed pair and Chinese language preference
  in its bounded checkpoint-derived prompt input

#### Scenario: Planner cannot fill an absent comparison fact
- **WHEN** a checkpoint profile lacks a required comparison pair
- **THEN** topic planning is not reached through the accepted HITL1 route and cannot
  invent a pair from the request text
