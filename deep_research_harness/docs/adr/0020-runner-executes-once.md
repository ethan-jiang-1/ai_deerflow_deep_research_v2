# Runner Executes Once

The Cognitive Evaluation Runner performs one declared node or flow execution in one new
isolated workspace. It reports only `completed` or `failed`, retaining the failure reason
and any collected material without making a recovery decision. It has no retry loop,
attempt hierarchy, or resume behavior. A caller that wants another try invokes the Runner
again, producing a separate Bundle; production-node recovery remains production behavior.
