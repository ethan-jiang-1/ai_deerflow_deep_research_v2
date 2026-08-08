# research-session-artifact-view Specification

> req: RSV-001, RSV-002, RSV-003, RSV-004

## Purpose

Provide a fixed, metadata-only view of broker-authorized retained session artifacts
without recursive discovery, artifact bodies, or artifact-derived control.
## Requirements

### Requirement: Run Bundle artifact catalog is fixed and observation-only

The runtime SHALL expose a workbench artifact catalog only after the shared Bundle
lifecycle boundary validates one selected available Run Bundle for the current trusted
scope. The initial catalog SHALL map fixed keys only to contained
`request/marker.json`, `request/profile.json`, `diagnostics/lifecycle.jsonl`, and
`diagnostics/records.jsonl` references when each validated file exists. It SHALL omit
absent entries, never recursively enumerate a Bundle, and never infer report, work,
evidence, cache, dynamic, or final artifact paths. Catalog metadata SHALL omit host
paths, lifecycle internals, provider details, raw diagnostic bodies, Bundle-local State
payloads, and checkpoint data. (`RSV-001`)

#### Scenario: Absent future report is not fabricated into the catalog
- **WHEN** an available Bundle has no validated producer-owned final report artifact
- **THEN** its catalog contains no report entry and the workbench does not infer one from Bundle layout or filename discovery

### Requirement: Artifact metadata access is reauthorized, contained, and bounded

The runtime SHALL reject an unknown catalog key before Bundle work. For a valid key, it
SHALL resolve the selected Bundle through the shared trusted-scope lifecycle result,
then map that key internally to one fixed relative path. Only after an available result
may it validate every component with no-follow contained owner-only regular-file checks
and classify fixed metadata. That contained reader SHALL return no artifact body in this
change and SHALL not open an external provider, acquire a sandbox, invoke a graph, or
turn an artifact view into Run discovery/control. `diagnostics/lifecycle.jsonl` is
consumed only by the dedicated bounded timeline mapper. (`RSV-002`)

#### Scenario: Unsafe artifact has no metadata detail
- **WHEN** a cataloged artifact is a symlink, nonregular file, or broader-mode file
- **THEN** the workbench returns bounded unavailable output without reading its body or following an external path

### Requirement: Artifact access fails closed without widening Bundle existence

Unknown catalog keys, unknown or foreign Bundle ids, unavailable Bundles, missing
contained observations, and authorization failures SHALL produce the same bounded
unavailable artifact result. An unknown key SHALL stop before lifecycle resolution. For
a valid key, an unavailable lifecycle result SHALL stop retained-path, external-provider,
sandbox, and graph work. The view SHALL not disclose whether a selected path or Bundle
exists. (`RSV-003`)

#### Scenario: Foreign artifact request cannot distinguish a Bundle
- **WHEN** a caller selects an unknown or foreign opaque Bundle id with a recognized catalog key
- **THEN** the result is indistinguishable from an unavailable artifact and performs no contained-path, provider, sandbox, or graph work

### Requirement: Run Bundle artifact views are reauthorized observations, not Run discovery

An artifact view SHALL expose only fixed, contained, bounded metadata or content that
the selected available Run Bundle authorizes. It SHALL take a validated `bundle_id`
through the shared lifecycle result/operation contract and SHALL not accept a session
reference, raw path, or artifact-derived lifecycle identity. An unavailable Bundle
shall remain unavailable even if a historical artifact reference or retained manifest
still exists. (`RSV-004`)

#### Scenario: Artifact record cannot reopen a deleted Bundle
- **WHEN** a historical artifact view references a Bundle that has been deleted
- **THEN** the view returns the bounded unavailable outcome and does not reconstruct a Bundle, State, or session operation
