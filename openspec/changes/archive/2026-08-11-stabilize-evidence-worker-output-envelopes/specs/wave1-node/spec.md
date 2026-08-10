> req: WON-011, WON-012

## ADDED Requirements

### Requirement: Wave1 worker programs expose one compact final output envelope

The real Wave1 initial evidence-extraction program and its existing one zero-tool
structural-repair program SHALL each make the same compact final completion envelope
visible to the model. The initial program SHALL state that it first completes exactly
its existing permitted retrieval work and then returns exactly one final JSON object,
with no markdown, prose, code fence, explanatory prefix, or trailing text. The repair
program SHALL state the same final JSON-only completion rule while retaining its
existing zero-tool posture.

For either program, the completion envelope SHALL specify a final object containing
exactly `schema_version`, `sources`, `claims`, and `open_questions`.
`schema_version` SHALL be `1`; `sources` SHALL contain at least two distinct URLs that
are new relative to the assigned Wave0 baseline, and each source item SHALL contain
exactly `source_id`, `canonical_url`, and `title`. Claims and open questions SHALL
retain their existing closed item shapes and reference constraints. Before returning
the final response, the program SHALL instruct a self-check of the closed key sets,
minimum new-source shape, baseline-newness constraint, and absence of placeholders,
prose, fences, authority claims, or prompt-description fields.

This completion envelope SHALL not alter the existing result schema, parser, local
semantic validation, provenance or new-source floors, submission validation, tool
window, budget, repair bound, controller retry, ledger, critics, gate, route, Bundle
lifecycle, or terminal outcome. (`WON-011`)

#### Scenario: Tool-bearing Wave1 worker completes in the closed envelope
- **WHEN** the initial Wave1 worker has completed its existing permitted retrieval
- **THEN** its completion instruction requires one standalone JSON object with only the
  closed Wave1 keys, while the existing parser, local semantic validator, and
  deterministic admission path remain the only way a returned candidate can affect
  evidence coverage

#### Scenario: Wave1 repair has the same closed final envelope without a tool
- **WHEN** the existing Wave1 parser or local semantic validator sends an initial draft
  to its one zero-tool repair
- **THEN** the repair receives no added tool or recovery authority and is instructed to
  return only the closed Wave1 JSON envelope before the existing parser, local
  validator, and non-admission path run

#### Scenario: Prohibited output forms remain explicit without adding a validator
- **WHEN** either Wave1 initial or repair completion envelope is rendered
- **THEN** it explicitly prohibits prose, fences, embedded objects, unlisted keys,
  literal placeholders, and baseline URLs represented as new evidence without changing
  which fields the existing parser and deterministic validators accept or reject

#### Scenario: Non-standalone or baseline-duplicate output remains non-admissible
- **WHEN** either Wave1 program returns prose, a code fence, an embedded object, or a
  candidate whose claimed new-source floor is supplied by an assigned baseline URL
- **THEN** the unchanged parser or local semantic validator rejects it through the
  current bounded path without accepting evidence or widening a retry

### Requirement: Wave1 retains closed response-shape and post-candidate validation evidence

For every Wave1 initial or repair result that reaches the existing parser or local
pre-persistence validation boundary, Wave1 SHALL classify the final response as exactly
one of `empty`, `prose`, `fenced`, `embedded_json`, or `json_object` and retain that
closed classification on its correlated Bundle-local Journal validation fact. `empty`
means no non-whitespace response; `fenced` means a response containing a Markdown code
fence; `json_object` means the complete trimmed response is a JSON object;
`embedded_json` means a non-standalone response contains a JSON object; and `prose`
covers every other non-empty response. The classification SHALL be a structural
observation only and SHALL not cause parsing, semantic validation, admission, repair,
or routing behavior to differ.

When a parser- and locally-valid Wave1 candidate later fails an existing deterministic
post-candidate submission or artifact validation boundary, Wave1 SHALL retain one
correlated `post_candidate` Journal validation fact containing only that boundary's
existing canonical code collection. It SHALL retain no raw response, draft, prompt,
tool observation, URL, artifact path, validation message, or exception text. A
post-candidate fact SHALL not enter the structural repair request or change the existing
controller retry, ledger, critic, gate, route, terminal, or lifecycle owner. (`WON-012`)

#### Scenario: A final prose response is distinguishable without being retained
- **WHEN** a Wave1 initial or repair result contains final prose after its model turn
- **THEN** the correlated Journal validation fact records `prose` and the existing
  canonical parser code without retaining the response body

#### Scenario: A parser-accepted candidate records a later validation failure safely
- **WHEN** a Wave1 candidate passes parsing and local semantic validation but fails
  deterministic submission or artifact validation
- **THEN** the Journal retains one correlated `post_candidate` fact with the existing
  canonical code collection, no repair request receives that code, and no submission is
  published
