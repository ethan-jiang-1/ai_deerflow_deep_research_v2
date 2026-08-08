> req: RSV-001, RSV-002, RSV-003

## ADDED Requirements

### Requirement: Session artifact catalog is fixed and observation-only

The runtime SHALL expose a workbench artifact catalog only after broker authorization
of one selected durable local session. The initial catalog SHALL map fixed keys only
to contained `request/marker.json`, `request/profile.json`,
`diagnostics/lifecycle.jsonl`, and `diagnostics/records.jsonl` references when each
validated file exists. It SHALL omit absent entries, never recursively enumerate a
bundle, and never infer report, work, evidence, cache, dynamic, or final artifact
paths. Catalog metadata SHALL omit host paths, binding internals, provider details,
raw diagnostic bodies, and checkpoint data. (`RSV-001`)

#### Scenario: Absent future report is not fabricated into the catalog
- **WHEN** a retained session has no validated producer-owned final report artifact
- **THEN** its catalog contains no report entry and the workbench does not infer one
  from bundle layout or filename discovery

### Requirement: Artifact metadata access is reauthorized, contained, and bounded

The runtime SHALL reject an unknown catalog key before broker work. For a valid key, it
SHALL reauthorize the selected session through the existing broker, which may use its
established checkpoint-provider verification, then map that key internally to one fixed
relative path. Only after an available broker projection may it validate every component
with no-follow contained owner-only regular-file checks and classify fixed metadata.
That contained reader SHALL return no artifact body in this change and SHALL not open an
additional provider, acquire a sandbox, or invoke a graph. `diagnostics/lifecycle.jsonl`
is consumed only by the dedicated bounded timeline mapper, and every catalog entry
remains metadata-only. It SHALL not offer an arbitrary path, recursive listing, raw
download, active-content rendering, or artifact-derived control input. (`RSV-002`)

#### Scenario: Unsafe artifact has no metadata detail
- **WHEN** a cataloged artifact is a symlink, nonregular file, or broader-mode file
- **THEN** the workbench returns bounded unavailable output without reading its body or
  following an external path

### Requirement: Artifact access fails closed without widening session existence

Unknown catalog keys, unknown or foreign session references, unavailable bindings,
missing retained observations, and authorization failures SHALL produce the same
bounded unavailable artifact result. An unknown key SHALL stop before broker work. For a
valid key, the workbench SHALL use the existing broker as the only authorization path;
if that broker returns unavailable, the workbench SHALL not read a retained path, acquire
a sandbox, invoke a graph node, create a retained-root object, or perform additional
provider work. It SHALL not disclose whether a selected path or session exists.
(`RSV-003`)

#### Scenario: Foreign artifact request cannot distinguish a session
- **WHEN** a caller selects an unknown or foreign opaque session reference with a
  recognized catalog key
- **THEN** the result is indistinguishable from an unavailable artifact; after its
  broker call it performs no retained-path, additional-provider, sandbox, or graph work
