# Runner Cases And Bundles Have Explicit Observations

The Runner accepts only a named, versioned, registered Evaluation Execution Case for a
finite node branch or flow. Each fresh execution records its declared input and control
identity, actual outputs/artifacts, and chronological Observation Trace of logs, events,
tool/model observations, resource use, and diagnostics. The Runner makes a best effort
to retain observations on failure because the node MD control is otherwise a black box;
only the upper review interprets whether those observations are good.
