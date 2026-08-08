## MODIFIED Requirements

### Requirement: HITL1 integrates into the mixed graph with explicit lifecycle and governance updates

The real HITL1 SHALL replace fake HITL1 in a mixed implementation map when
`bootstrap=real` and `hitl1=real` while later phases remain fake. Selecting
`hitl1=real` without `bootstrap=real` SHALL fail closed during recipe or graph
binding because real HITL1 requires the established request-bundle root for
`profile.json`. The all-fake map SHALL remain unchanged and SHALL complete its
existing E2E lifecycle path without calling `run_agent` or writing request-profile
artifacts.

Real HITL1 SHALL retain the declared `needs_followup -> hitl1` and
`exhausted -> blocked/END` routes; existing `accepted -> topic_planning` and
`cancel -> cancelled/END` routes remain unchanged. Its node-local contracts,
narrow public `interrupt` import exception, registered paths, and declared request
bundle capability remain unchanged. The selected bootstrap/HITL1 real prefix SHALL
report `implementation_mode=mixed`; `full_fake` identifies only an all-fake recipe,
not the absence of a final report. `backend/`, `frontend/`, root config examples,
extensions config, public skills, per-user Agent/SOUL, MCP, ACP, and lead-agent
middleware surfaces SHALL NOT be modified.

#### Scenario: Mixed graph with real HITL1
- **WHEN** the implementation map sets `bootstrap=real`, `hitl1=real`, and every later phase `fake`
- **THEN** the graph compiles, selects both real factories, runs the declared interrupt/resume path, calls the node-agent bridge only within the real HITL1 policy, and reports `implementation_mode=mixed`

#### Scenario: Real HITL1 requires real bootstrap
- **WHEN** the implementation map sets `hitl1=real` but does not set `bootstrap=real`
- **THEN** recipe creation or graph binding fails closed before graph invocation and no node-agent bridge or request-bundle writer is constructed

#### Scenario: Follow-up and blocked routes remain explicit
- **WHEN** the first HITL1 response is incomplete or brief generation exhausts its bounded validation path
- **THEN** the graph follows only `needs_followup -> hitl1` or `exhausted -> blocked/END`, respectively, and does not fall back to fake behavior

#### Scenario: Full-fake graph remains unchanged
- **WHEN** the implementation map sets all phases to `fake`
- **THEN** fake HITL1 presents its fixture request, does not construct a node-agent bridge or request-profile writer, and results report `implementation_mode=full_fake`

#### Scenario: Governance accepts the narrow interrupt boundary
- **WHEN** the architecture checker scans `graph/nodes/hitl1/node.py`
- **THEN** exactly the public `langgraph.types.interrupt` import remains accepted for the HITL node and ordinary node imports remain restricted

#### Scenario: No upstream or UI files are modified
- **WHEN** this change is applied
- **THEN** no file under `backend/` or `frontend/` is changed
