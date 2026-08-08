## ADDED Requirements

### Requirement: Retained Wave0 diagnosis preserves closed worker failure classes

The retained event journal and terminal diagnosis projection SHALL carry only the
closed Wave0 worker-failure classification defined by
`deep-research-wave0-worker-failure-classification`.  An `attempt` event SHALL expose
the exact terminal attempt class.  An `exhaustion` event and terminal incident for one
work item SHALL expose that class when all failed attempts agree, otherwise `mixed`.
The terminal incident SHALL retain its existing route failure code and carry this
aggregate in a separate optional diagnosis field. The ordered bounded timeline SHALL
remain available for per-attempt inspection. Legacy
events without a classification SHALL remain an unavailable observation.  No retained
summary, event, inspection, workbench, or CLI projection SHALL expose raw exception
text, traceback, model/tool content, URL, path, prompt, answer, or credential. (`RUS-005`)

#### Scenario: Exhaustion with one cause stays specific
- **WHEN** every failed attempt for a Wave0 work item has the same closed worker class
- **THEN** the attempt timeline, exhaustion event, and terminal incident carry that
  class with the existing diagnostic correlation reference

#### Scenario: Mixed attempts do not invent a root cause
- **WHEN** failed attempts for one Wave0 work item have different closed classes
- **THEN** each attempt event retains its own class while exhaustion and terminal
  diagnosis expose only `mixed`

#### Scenario: Hostile diagnostic content is rejected
- **WHEN** recorder or presentation input includes a raw exception, secret, host path,
  prompt, answer, URL, or provider/tool body alongside a worker category
- **THEN** the unsafe content is rejected or redacted before persistence and no view
  emits it

#### Scenario: Worker category is not a validation code
- **WHEN** an attempt fails with a worker category and has no submission validation
  result
- **THEN** its event stores the class only in a distinct closed worker-category field
  and leaves `validation_code` absent
