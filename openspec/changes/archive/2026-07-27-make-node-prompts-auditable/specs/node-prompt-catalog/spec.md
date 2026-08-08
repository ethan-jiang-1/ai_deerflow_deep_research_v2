> req: NPC-001, NPC-002

## ADDED Requirements

### Requirement: Phase-agent prompt rendering has one source-faithful pure seam

The agents layer SHALL expose one pure rendering interface that accepts a validated
`NodeExecutionRequest` and an explicit attempt workspace and returns the exact package
system-policy text plus the exact final human message for a phase-agent invocation.
It SHALL preserve the existing untrusted-artifact projection. It SHALL not import
graph or runtime code, inspect runtime configuration, resolve a model or tool, create
a sandbox, or execute an agent. The runtime bridge SHALL consume that rendering
interface when it constructs its phase-agent messages, so no catalog or adapter
duplicates the final message template. (`NPC-001`)

#### Scenario: Catalog and bridge receive the same final prompt text
- **WHEN** one canonical node request has an objective, expected output, attempt
  workspace, and source artifact references
- **THEN** the catalog renderer and the runtime bridge use the same system policy and
  final human message, including the bounded untrusted-artifact delimiter

#### Scenario: Rendering needs no runtime execution authority
- **WHEN** a prompt-catalog test renders a canonical case
- **THEN** no model, tool resolver, sandbox, provider, lifecycle graph, configuration,
  credential, user input, or external source body is accessed

### Requirement: Node prompts have a complete deterministic review catalog

The graph-owned prompt catalog SHALL define a stable, synthetic case for every
top-level node prompt-builder function in `graph/nodes/**/prompts.py` whose body
directly constructs a `NodeExecutionRequest`. A builder with a `repair_error`
parameter SHALL have both initial and repair cases; a dedicated repair builder SHALL
have its repair case. The catalog generator SHALL render only those cases through the
shared rendering interface and SHALL emit a committed Markdown index and one stable
case file below `agent/node_prompts/`. Each case file SHALL show the stable case
identity, exact system policy, exact final human message, and clearly labelled
requested tool state, minimum calls, and call limit. It SHALL not contain real-user
text, runtime configuration, provider data, credentials, sandbox identity, timestamps,
or a locally resolved tool inventory. (`NPC-002`)

The focused fast deterministic test selection SHALL invoke the same catalog check
adapter against the committed tree, so `UV_OFFLINE=1 make verify` fails on catalog
drift without requiring a separate manually selected command. `make prompt-dump-check`
SHALL remain a convenience wrapper over that check adapter rather than a second
freshness implementation.

#### Scenario: A prompt modification creates a reviewable generated diff
- **WHEN** a node prompt builder or the shared policy changes for a registered
  canonical case
- **THEN** `make prompt-dump` produces a deterministic change below
  `agent/node_prompts/` that displays the new final prompt content

#### Scenario: A stale or omitted case fails deterministically
- **WHEN** a committed case file is stale or a supported direct node prompt-builder
  branch lacks a catalog case
- **THEN** `make prompt-dump-check` and its focused deterministic tests fail without
  invoking a model, tool, or network

#### Scenario: The generated catalog is an exact bounded tree
- **WHEN** an expected generated file is missing, its bytes differ, an obsolete
  generated Markdown file remains, or an unexpected path appears below
  `agent/node_prompts/`
- **THEN** `make prompt-dump-check` fails without writing, and refresh mode writes
  only code-owned expected paths while refusing to traverse or delete an unexpected
  non-Markdown file or symbolic link

#### Scenario: The normal deterministic gate catches catalog drift
- **WHEN** a committed catalog artifact is stale and `UV_OFFLINE=1 make verify` runs
- **THEN** its fast deterministic selection invokes the same catalog check adapter
  and fails without invoking a model, tool, network, or a separate freshness path
