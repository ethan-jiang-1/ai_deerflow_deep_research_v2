---
status: superseded by ADR-0028
---

# Primary User Research Sessions Are Durable

This decision previously made a Durable Research Session the cross-restart lifecycle
authority. ADR-0028 replaces that model: an available Run Bundle and its contained
Research State are the durable authority for one Deep Research Run, while the Harness
has no independent session registry. Same-process retained records remain appropriate
for CLI smoke tests but do not satisfy the product requirement for retained Run Bundles.
