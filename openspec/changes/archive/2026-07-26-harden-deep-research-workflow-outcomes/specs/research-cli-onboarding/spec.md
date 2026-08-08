## ADDED Requirements

### Requirement: Real CLI renders direct-phase workflow incidents without collapsing them

The standalone real CLI SHALL render a terminal direct-phase workflow incident using
only the shared run update's safe category, phase, observed recovery disposition,
diagnostic reference, durability truth, and legal next action. It SHALL distinguish a
known provider timeout/unavailable incident from generic blocked, structured-output
exhaustion, and unknown local failure without displaying raw provider or exception
content.

#### Scenario: BUG-010 is reported as a bounded topic-planning timeout
- **WHEN** real topic planning exhausts its configured provider-recovery policy
- **THEN** the CLI identifies `provider.timeout` and `topic_planning`, reports the
  observed bounded recovery, prints only the legal next action, and preserves a safe
  diagnostic reference rather than saying only that research was blocked
