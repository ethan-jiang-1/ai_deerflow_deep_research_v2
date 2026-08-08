> req: WSN-005

## ADDED Requirements

### Requirement: Wave2 capability admits only assigned accepted-evidence synthesis

The real Wave2 synthesis and structured-repair requests SHALL retain their distinct
forbidden local capabilities. An initial or repaired candidate SHALL derive findings,
relations, and gaps only from the graph-assigned accepted evidence and trusted output
contract. The candidate SHALL not retrieve, add evidence or references, materialize an
artifact, publish a gap projection, or control routing. The existing parser,
materializer, gate preview, and gate SHALL remain the only admission and outcome
owners. (`WSN-005`)

#### Scenario: Assigned evidence bounds a valid synthesis candidate
- **WHEN** a scripted real Wave2 request receives accepted evidence and returns a
  contract-valid finding/gap candidate
- **THEN** deterministic validation admits only backed references, the model sees no
  tool, and the existing materializer and gate derive any artifact or searchable-gap
  projection

#### Scenario: Repair cannot manufacture evidence or routing authority
- **WHEN** an initial Wave2 draft is malformed, gaps-only, or contains an unassigned
  evidence reference
- **THEN** the zero-tool repair receives only the bounded draft, validation facts, and
  assigned evidence; it either produces a contract-valid bounded candidate or follows
  the existing non-publication or exhausted outcome without writing a route or gap
  projection
