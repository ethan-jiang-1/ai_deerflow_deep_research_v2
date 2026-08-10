> req: WAN-010

## ADDED Requirements

### Requirement: Wave0 records canonical structural validation evidence before candidate admission

When a Wave0 worker's initial result or its existing one zero-tool structural repair
reaches the typed source-intake parser, Wave0 SHALL publish one Journal validation fact
for that stage with its existing work and attempt correlation. A successful parse SHALL
publish an empty code collection. A failed parse SHALL publish only one code from the
closed set `wave0_worker_output_empty`, `wave0_worker_output_json_invalid`, or
`wave0_worker_output_invalid`; it SHALL NOT retain raw JSON, validation messages,
source URLs, tool observations, or exception text.

The initial validation fact SHALL be emitted before the existing repair is invoked. If
the repair result reaches parsing, its validation fact SHALL be retained independently
before the existing structured-output failure path, or as an empty collection on
success. An invocation failure before parser entry retains its existing invocation
fact and does not fabricate a validation result. These facts SHALL not add a repair,
change the one-repair bound, admit a candidate, append a ledger record, alter the
controller/gate route, or change a terminal or lifecycle result. (`WAN-010`)

#### Scenario: Wave0 repair failure retains both parser stages
- **WHEN** an initial Wave0 source-intake result fails parsing and its existing repair
  result also fails parsing
- **THEN** the correlated Journal contains distinct `initial` and `repair` validation
  facts with closed codes before the existing structured-output/controller path runs

#### Scenario: Valid initial Wave0 result retains a successful parser fact
- **WHEN** an initial Wave0 source-intake result parses successfully
- **THEN** the correlated Journal contains one `initial` validation fact with an empty
  code collection, no repair is invoked, and existing candidate admission remains the
  next deterministic boundary

#### Scenario: Pre-parser invocation failure is not relabeled as validation
- **WHEN** the Wave0 bridge invocation fails before it returns a candidate result
- **THEN** Wave0 retains the existing invocation failure behavior and creates no
  fabricated parser validation fact
