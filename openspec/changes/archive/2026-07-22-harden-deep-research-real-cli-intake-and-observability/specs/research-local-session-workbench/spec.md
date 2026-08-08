> req: RWB-005, RWB-006

## ADDED Requirements

### Requirement: Workbench renders authorized retained diagnosis observations

After existing broker authorization succeeds, the local workbench SHALL render only
validated retained diagnosis summary and bounded event observations. It SHALL identify
terminal/suspended status, committed phase, durability, safe category/reference, and
correlated attempt categories. It SHALL not render raw diagnostic/event bodies, create an
arbitrary file browser, derive lifecycle authority, or resume a same-process session from
retained observations. (`RWB-005`)

#### Scenario: Operator can distinguish terminal history from pending operation
- **WHEN** an authorized selected session has a retained `blocked@wave0` summary
- **THEN** workbench renders the terminal diagnosis and disables answer/resume controls rather than presenting it as a live pending session

#### Scenario: Unavailable diagnosis remains bounded
- **WHEN** summary or events validation fails after broker authorization
- **THEN** workbench keeps the broker-derived session view and renders diagnosis unavailable without exposing raw stored bytes or invoking graph/provider work

### Requirement: Workbench renders and submits only projected typed input actions

The local workbench SHALL render a control only for a bounded action id explicitly
projected from the current authorized pending input, and SHALL submit that action through
the existing broker typed resume seam. It SHALL never map a free-text field value to an
action, synthesize an action from a proposal, or retain a submitted response body in a
session observation. The control remains unavailable for stale, absent, or non-HITL1
pending input and the broker/generic verifier remain final authority. (`RWB-006`)

#### Scenario: Workbench exposes a verified acceptance control
- **WHEN** the authorized current HITL1 pending input advertises `accept_suggestion`
- **THEN** the workbench renders an explicit acceptance control that sends the typed action with the projected request id

#### Scenario: Stale action is unavailable
- **WHEN** the pending request changes, becomes terminal, or does not advertise an action
- **THEN** the workbench does not render or dispatch an acceptance control
