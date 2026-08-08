> req: BON-006

## ADDED Requirements

### Requirement: Bootstrap establishes the checkpoint-selected canonical bundle root

Real bootstrap SHALL establish and validate the marker beneath the controller-owned
canonical `bundle_directory`, not by recomputing a root from `research_id`. For new runs
the locator is the trusted `YYYYMMDDHHMM_r_<research-id>` value checkpointed before graph
entry; for a compatible old checkpoint without it bootstrap SHALL use only legacy
`r_<research-id>`. Bootstrap SHALL reject malformed locators, symlinks, cross-research
markers, and a marker whose root name does not match the selected locator before routing.
It SHALL not migrate or copy a legacy root, and `research_id` remains the marker's sole
identity binding. (`BON-006`)

#### Scenario: Bootstrap writes under the selected new locator
- **WHEN** a fresh state selects `202607220359_r_abc`
- **THEN** bootstrap atomically creates `workspace/deep-research/202607220359_r_abc/request/marker.json` and binds marker research id `r_abc`

#### Scenario: Legacy state does not get renamed
- **WHEN** an old compatible checkpoint lacks a locator and contains a valid `r_abc` root
- **THEN** bootstrap resumes against that root without creating a timestamped sibling or changing checkpoint identity
