> req: RDO-005

## ADDED Requirements

### Requirement: Authorized broker resume preserves typed advertised responses

The local authorized session broker SHALL accept one frozen typed resume response
contract, not only a free-text answer. It SHALL project only the pending request's bounded
advertised action ids to the owner-visible session view and pass a response unchanged to
the existing generic human-input verifier under the namespace lock. The broker SHALL not
interpret localized phrases, infer actions from text, expand the public Deep Research tool
schema, or use session manifest/trace facts as action authority. Existing text and HITL2
choice resumes retain their behavior. (`RDO-005`)

#### Scenario: Brokered acceptance is revalidated under lock
- **WHEN** an authorized workbench submits typed `accept_suggestion` for the currently projected HITL1 request
- **THEN** broker resume preserves request/message correlation and generic advertised-action validation decides whether it reaches HITL1

#### Scenario: Broker cannot turn text into an action
- **WHEN** a local caller sends ordinary text equal to an action id or an action absent from its pending projection
- **THEN** broker returns the existing unavailable/invalid outcome without graph mutation or action inference
