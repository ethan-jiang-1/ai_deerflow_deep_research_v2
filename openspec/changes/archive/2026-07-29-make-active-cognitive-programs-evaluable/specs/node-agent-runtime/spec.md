> req: NOA-012

## ADDED Requirements

### Requirement: Branch review evidence distinguishes requested from enforced execution posture

Runtime review evidence SHALL identify each ledger branch's requested tool window
separately from bridge-enforced capability posture, actual eligible-tool intersection,
and bounded safe failure projection. A real bridge test with fake model/tool bindings
SHALL prove that distinction for the canonical case; a prompt or capability resource
alone SHALL not. It SHALL not change provider, tool, retry, route, checkpoint, or
lifecycle behavior.

#### Scenario: Tool posture is reviewed
- **WHEN** a branch requests a tool posture through local capability composition
- **THEN** deterministic evidence identifies the bridge enforcement seam without claiming that prompt text enforces it
