> req: WAN-011, WAN-012

## ADDED Requirements

### Requirement: Wave0 worker programs expose one compact final output envelope

The real Wave0 initial source-intake program and its existing one zero-tool structural
repair program SHALL each make the same compact final completion envelope visible to
the model. The initial program SHALL state that it first completes only its existing
permitted retrieval work and then returns exactly one final JSON object, with no
markdown, prose, code fence, explanatory prefix, or trailing text. The repair program
SHALL state the same final JSON-only completion rule while retaining its existing
zero-tool posture.

For either program, the completion envelope SHALL specify a final object containing
exactly `schema_version`, `sources`, `baseline_facts`, and `limitations`.
`schema_version` SHALL be `1`; `sources` SHALL contain at least one source item with
exactly `source_id`, `canonical_url`, `title`, and `fetch_status`; and `fetch_status`
SHALL be either `fetched` or `degraded`. The program SHALL make the existing
source-count, title-length, independent-source, and untrusted-data constraints visible
without representing source metadata as accepted evidence. Before returning the final
response, it SHALL instruct a self-check of the closed key sets, minimum source shape,
and absence of placeholders, prose, fences, authority claims, or prompt-description
fields.

This completion envelope SHALL not alter the existing result schema, parser, source or
artifact validation, source floor, tool window, budget, repair bound, controller retry,
ledger, gate, route, Bundle lifecycle, or terminal outcome. (`WAN-011`)

#### Scenario: Tool-bearing Wave0 worker completes in the closed envelope
- **WHEN** the initial Wave0 worker has completed its existing permitted retrieval
- **THEN** its completion instruction requires one standalone JSON object with only the
  closed Wave0 keys, while the existing parser and deterministic admission path remain
  the only way a returned candidate can affect evidence coverage

#### Scenario: Wave0 repair has the same closed final envelope without a tool
- **WHEN** the existing parser sends an initial Wave0 draft to its one zero-tool repair
- **THEN** the repair receives no added tool or recovery authority and is instructed to
  return only the closed Wave0 JSON envelope before the existing parser and
  non-admission path run

#### Scenario: Prohibited output forms remain explicit without adding a validator
- **WHEN** either Wave0 initial or repair completion envelope is rendered
- **THEN** it explicitly prohibits prose, fences, embedded objects, unlisted keys, and
  literal placeholders without changing which fields the existing parser and
  deterministic validators accept or reject

#### Scenario: Non-standalone final text remains outside the parser contract
- **WHEN** either Wave0 program returns prose, a code fence, or an embedded object
- **THEN** the unchanged standalone-object parser and bounded recovery path reject it
  without accepting a source, appending a ledger record, or widening a retry

### Requirement: Wave0 retains closed response-shape and post-candidate validation evidence

For every Wave0 initial or repair result that reaches the existing candidate parser,
Wave0 SHALL classify the final response as exactly one of `empty`, `prose`, `fenced`,
`embedded_json`, or `json_object` and retain that closed classification on its correlated
Bundle-local Journal validation fact. `empty` means no non-whitespace response;
`fenced` means a response containing a Markdown code fence; `json_object` means the
complete trimmed response is a JSON object; `embedded_json` means a non-standalone
response contains a JSON object; and `prose` covers every other non-empty response.
The classification SHALL be a structural observation only and SHALL not cause parsing,
admission, repair, or routing behavior to differ.

When a parser-accepted Wave0 candidate later fails an existing deterministic
post-candidate submission or artifact validation boundary, Wave0 SHALL retain one
correlated `post_candidate` Journal validation fact containing only that boundary's
existing canonical code collection. It SHALL retain no raw response, draft, prompt,
tool observation, URL, artifact path, validation message, or exception text. A
post-candidate fact SHALL not enter the structural repair request or change the existing
controller retry, ledger, gate, route, terminal, or lifecycle owner. (`WAN-012`)

#### Scenario: A prose response is distinguishable without being retained
- **WHEN** a Wave0 initial or repair result contains only final prose after its model
  turn
- **THEN** the correlated Journal validation fact records `prose` and the existing
  canonical parser code without retaining the response body

#### Scenario: A parser-accepted candidate records a later validation failure safely
- **WHEN** a Wave0 candidate passes parsing but fails deterministic submission or
  artifact validation
- **THEN** the Journal retains one correlated `post_candidate` fact with the existing
  canonical code collection, no repair request receives that code, and no submission is
  published
