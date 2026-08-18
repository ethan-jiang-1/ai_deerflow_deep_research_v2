## MODIFIED Requirements

### Requirement: Authorized local discovery projects bounded Bundle facts

The runtime SHALL provide local discovery only through the same trusted-scope Bundle
lifecycle resolver as the public tool. It SHALL validate a Current Bundle Handle or scan
only actual Bundle directories and Bundle-local State beneath the current trusted scope;
it SHALL not use an owner/profile index, retained manifest, raw path, or another
principal/profile's data. It SHALL discover no more than the one legal active Bundle and
shall return bounded active/ended/unavailable/ambiguous facts without creating,
repairing, or pruning a Bundle. (`RDO-001`)

The operator soft-bundle control entry's fresh-run preparation SHALL preserve failed-run
forensics: an existing managed run subtree (`deep-research`, `scripted-real`) SHALL be
moved into a timestamped archive directory under the runs root's `archive/` area rather
than deleted, keeping the most recent three archives per subtree name and pruning older
ones; the fresh empty subtree is recreated afterwards. Archived subtrees SHALL sit
outside the discovery scan roots so bundle discovery semantics are unchanged, and the
archive step SHALL emit one grep-able line naming the archive location.

#### Scenario: Foreign and unknown Bundles are indistinguishable
- **WHEN** discovery or open receives a foreign, unknown, corrupt, or deleted opaque Bundle id
- **THEN** it returns the same bounded unavailable or denied projection without a path, owner, provider, or existence hint

#### Scenario: A rerun archives instead of destroying the prior run tree
- **WHEN** the operator starts a fresh control run and the managed run subtree contains
  a prior (possibly failed) run's bundles
- **THEN** the subtree's prior content is moved into a timestamped archive directory
  beneath `archive/`, the fresh empty subtree is recreated, and the prior run's state,
  events, and bundle content remain inspectable at the archive location

#### Scenario: Archive retention stays bounded
- **WHEN** archiving would create the fourth archive for the same subtree name
- **THEN** the oldest archive for that name is deleted, keeping exactly the three most
  recent archives

#### Scenario: Archived trees are not discovered as bundles
- **WHEN** bundle discovery scans the trusted scope after archiving
- **THEN** archived subtrees are outside the scan roots and produce no bundle facts
