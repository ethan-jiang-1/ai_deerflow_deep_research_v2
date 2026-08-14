> req: NPC-001

## RENAMED Requirements

- FROM: `### Requirement: Phase-agent prompt rendering has one source-faithful pure seam`
- TO: `### Requirement: Node Cognitive Control Program rendering has one source-faithful pure seam`

## MODIFIED Requirements

### Requirement: Node Cognitive Control Program rendering has one source-faithful pure seam

The agents layer SHALL expose one pure renderer for the Node Cognitive Control
Program that accepts one validated request and virtual attempt workspace and
returns exact trusted system-policy text plus the exact final human message for an
LLM-Bearing Node invocation. It SHALL load the base policy and mandatory validated
capability policy from package resources, compose them with the graph-provided
assignment/output contract and delimited untrusted references, and expose the
validated capability projection for review. The node-agent bridge SHALL use this
renderer when it constructs its child messages, so no catalog or adapter duplicates
the final message template. The renderer SHALL reject a missing or invalid request
or capability ref before returning prompt text and SHALL not resolve tools, model,
runtime configuration, or lifecycle authority. (`NPC-001`)

#### Scenario: Direct prompt rendering is deterministic
- **WHEN** a test renders one direct request with a virtual attempt workspace and
  declared capability ref
- **THEN** it receives the same ordered trusted policy, assignment, and delimited
  untrusted-data layers that the runtime bridge will use, without model or tool work

#### Scenario: Capability admission fails before prompt projection
- **WHEN** a request is missing a ref or names an invalid, unknown, or package-
  mismatched local capability
- **THEN** the renderer raises its deterministic admission error and returns no final
  prompt projection, model binding, or tool inventory

#### Scenario: Catalog and bridge receive the same final prompt text
- **WHEN** one canonical node request has an objective, expected output, attempt
  workspace, source artifact references, and declared capability ref
- **THEN** the catalog renderer and node-agent bridge use the same system policy and
  final human message, including the bounded untrusted-artifact delimiter

#### Scenario: Rendering needs no runtime execution authority
- **WHEN** a prompt-catalog test renders a canonical case
- **THEN** no model, tool resolver, sandbox, provider, lifecycle graph,
  configuration, credential, user input, or external source body is accessed
