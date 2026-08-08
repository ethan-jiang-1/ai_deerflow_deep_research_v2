# Node-Agent Workflow Integrity Policy

> role: review guidance for bounded LLM cognition inside deterministic workflow nodes
> trigger: adding, removing, or materially revising a node's LLM-bearing cognitive role, capability policy, tool posture, output-admission boundary, repair semantics, or model/non-model classification
> authority: guidance only; exact behavior, state writes, routes, tool permissions, and recovery remain in the owning capability specification and executable contracts
> @impl DRC-008

## Rule

Treat a Node Agent as a bounded cognitive worker inside a deterministic workflow,
not as an owner of graph control. When this policy is selected, the proposal must
include one `## Node Agent Review` table. A relevant deterministic surface is
explicitly recorded as `no-agent`; a model-bearing surface is recorded as
`node-agent`. The review exposes the intended handoff for design and review. It
does not create an invocation, prompt, permission, route, state writer, retry, or
result acceptance.

Keep the four owners distinct:

- The graph or node handler owns lifecycle placement, typed state, routes, attempt
  bounds, and artifact promotion.
- The Node Agent answers one bounded cognitive question and returns a candidate.
- The runtime bridge owns configured execution, actual tool availability, sandbox,
  budgets, cancellation, and safe failure projection.
- The parser, evaluator, or materializer owns deterministic validation and whether a
  candidate can affect typed state or an artifact.

## Review Questions

- Is this surface intentionally `node-agent` or `no-agent`, and what bounded
  cognitive question or no-agent rationale makes that classification reviewable?
- Which inputs are trusted assignment/context, and which user, source, tool, or
  model material remains untrusted evidence rather than instruction authority?
- What tool posture is requested, and which runtime policy actually enforces the
  allowed tools, path scope, and budget?
- What typed candidate result is returned, and which deterministic parser,
  evaluator, or materializer admits or rejects it?
- Which owner handles malformed output, tool/provider failure, cancellation, or
  repair, and what is the explicit bound?
- What is the lowest deterministic evidence seam for the handoff? What quality or
  judgment claim still needs scenario or live evaluation instead?

## Configuration Boundary

Root `config.yaml` and local profiles select operator environment such as provider,
available tools, sandbox, and global limits. They do not define a node's cognitive
role, research method, graph route, or product permission. `openspec/config.yaml`
routes a change author to this review; it is not a runtime policy. A prompt or review
record likewise cannot grant execution authority.

## Boundary

This policy cannot infer whether a source change is truly LLM-bearing, judge the
truth of a review row, or replace a capability specification. The owning active
delta, typed request/result contracts, runtime enforcement, node handler, and tests
remain the authority for observable behavior.
