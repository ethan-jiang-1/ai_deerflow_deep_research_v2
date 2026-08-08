# Cognitive Evaluations Have Four Honest Outcomes

The Cognitive Evaluation Agent Workflow reports `pass`, `limited`, `inconclusive`, or
`failed` after inspecting an Evaluation Run Bundle. A pass meets the declared cognitive
rubric. A limited result has a declared, inspectable quality or coverage limitation; an
inconclusive result lacks a credible basis for assessment; and a failed result violates a
critical cognitive rubric. Limited and inconclusive results always retain a readable
report and never silently become passing automated tests. Runner execution status remains
separate, so a provider or environment failure is not misreported as a cognitive failure.
