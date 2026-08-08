## Context

The phase-agent runtime currently reads one package Markdown policy and constructs
the user message privately inside `RuntimeNodeAgentBridge`. Node-specific prompt
builders return `NodeExecutionRequest` values from Python. This keeps execution
bounded, but gives reviewers no single, rendered representation of what a node agent
actually receives.

The catalog must not become a second prompt authority. It also cannot invoke a real
agent just to display a prompt: that would require model, tool, sandbox, and runtime
configuration facts which are irrelevant to prompt review and unsafe to encode in
committed output.

## Goals / Non-Goals

**Goals:**

- Render the exact package policy and final human message used for a phase-agent
  invocation from a `NodeExecutionRequest` and a canonical attempt workspace.
- Make every direct node prompt-builder branch that can reach `run_agent` visible as
  a stable Markdown artifact in `agent/node_prompts/`.
- Make prompt diffs reviewable, deterministic, zero-network, and impossible to
  silently stale in the deterministic test gate.
- Keep graph ownership of node-specific case construction and agents ownership of
  final-message rendering, preserving the existing import direction.

**Non-Goals:**

- Do not execute a model, resolve configured tools, create a sandbox, or call a
  lifecycle graph while generating a catalog.
- Do not dump real user questions, research artifacts, configured endpoints,
  credentials, sandbox identifiers, or provider responses.
- Do not add a prompt-editing UI or change a node's research behavior merely to make
  it easier to render.

## Decisions

### 1. Extract one pure final-prompt renderer from the runtime bridge

`agents/` will own a small pure module that turns a validated
`NodeExecutionRequest` plus an explicit attempt workspace string into a frozen
rendered prompt projection: the exact loaded system-policy text and the exact human
message. The bridge will call this module before constructing its ephemeral child
state; the bridge keeps ownership of sandbox/thread metadata, model resolution,
tools, budgets, invocation, and result projection.

The renderer will not import `runtime` or `graph`, inspect configuration, or make an
I/O/provider call beyond the existing package-resource policy read. It will retain the
current untrusted-artifact delimiter behavior. This gives the catalog and the runtime
one seam for prompt text rather than two matching string templates.

Alternative considered: have the dump script call the bridge's private child-state
helper. Rejected because it would expose runtime envelope requirements to a review
tool and preserve a private, hard-to-test formatting seam. Alternative considered:
reconstruct the text in the script. Rejected because it would inevitably drift from
the actual invocation path.

### 2. Keep catalog cases with the graph's prompt builders

`graph/` will own a typed catalog registry of canonical, synthetic cases. Each case
names a stable node and branch, builds a real `NodeExecutionRequest` through the same
public builder used by the node, and supplies only fixed safe values such as a virtual
attempt workspace and artifact references. It will not render the final message or
import the agents layer.

The supported direct-builder inventory is mechanically defined as every top-level
function in `graph/nodes/**/prompts.py` whose body directly constructs a
`NodeExecutionRequest`. The focused discovery test scans that exact inventory and
compares it with the registry. A builder that accepts `repair_error` requires both an
initial and a repair case; a dedicated repair builder requires its repair case. This
is a review-completeness boundary, not runtime discovery or routing authority.

Each case has a stable identity, source builder identity, repair flag, fixed virtual
attempt workspace, and code-owned synthetic fixture. Fixtures use explicit synthetic
markers and never derive a value from the environment, clock, provider, or a run.
The registry covers every direct builder branch that can reach the phase-agent
capability, including normal and repair variants. The graph registry does not render
the final message or import the agents layer.

Alternative considered: put the registry in `agents/`. Rejected because that would
make `agents/` import graph nodes and violate the existing layer direction.

### 3. Generate committed, review-oriented Markdown rather than a runtime record

`scripts/prompt_dump.py` will combine the graph cases and agents renderer. It writes
only below the fixed `agent/node_prompts/` root and produces a small generated index
plus one Markdown file per stable case. Each file will contain:

- a generated-artifact notice and stable case identity;
- the exact shared system policy;
- the exact final user message generated for that case; and
- the request's requested tool state, minimum calls, and call limit, clearly labelled
  as request policy rather than a claim about tools resolved from local configuration.

The command has explicit write and check modes. `make prompt-dump` refreshes the
catalog, while `make prompt-dump-check` is read-only and verifies that the committed
file tree exactly matches current deterministic generation: missing files, changed
bytes, obsolete generated Markdown files, and unexpected paths all fail the check.
The fixed catalog root is wholly generator-owned. Write mode may remove obsolete
generated Markdown files below that root and prune their empty directories, but it
must refuse to traverse or delete an unexpected non-Markdown file or symbolic link.
Generation has no output-root argument, uses sorted case/path order and canonical line
endings, and rejects a generated relative path that would escape the fixed root.
A focused fast-lane test invokes this same check adapter against the committed catalog,
so `UV_OFFLINE=1 make verify` catches prompt drift without a contributor having to
remember a separate target. The Make check target is a convenience wrapper over the
same adapter, not a second freshness implementation.

Each rendered system policy and final user message is enclosed in a Markdown code
fence chosen to be longer than any backtick run in that content, so prompt text stays
literal even when a future prompt itself contains a fence.

The generated Markdown is a projection for review. `runtime_policy.md`, the builder
source, and the runtime bridge remain the sources of truth; generated files never
drive execution.

### 4. Make the catalog a deterministic evidence surface

Focused tests will prove the pure renderer's output, the complete case inventory and
repair coverage, the absence of model/tool/network invocation, byte-for-byte catalog
tree freshness, safe fixture content, and a captured canonical-case bridge equality
with the shared renderer. The test path will carry the new requirement markers and
evidence registration, while the command remains a convenient human review surface.

## Risks / Trade-offs

- [A prompt changes but the catalog lies] -> runtime and generator share one renderer;
  the check target and bridge-conformance test fail on drift.
- [A new branch has no dump] -> the graph-owned registry and source-backed discovery
  test require a case for every direct request builder and both variants of a builder
  with `repair_error`.
- [A catalog leaks user/runtime data] -> cases have only code-owned synthetic values;
  the renderer takes no configuration and the output root is fixed.
- [Reviewers mistake requested tools for configured tools] -> each artifact labels
  the displayed values as request policy and excludes runtime tool resolution.
- [A stale file hides a removed or renamed case] -> check mode compares the complete
  generated tree and write mode removes only obsolete generated Markdown paths.
- [Generated files become noisy] -> stable case ids, deterministic ordering, fixed
  fixtures, and no timestamps, environment values, or model calls are allowed.

## Migration Plan

1. Add the pure renderer and migrate the bridge to consume it without changing the
   existing prompt text.
2. Add graph catalog cases, a captured canonical bridge conformance test,
   generator/check targets, committed Markdown, and focused tests.
3. Register source/test/artifact paths and requirement evidence, then document the
   contributor command.

Rollback removes the new catalog path and restores the bridge's previous private
formatting implementation; no checkpoint, provider configuration, or data migration
is involved.

## Open Questions

None. The catalog uses canonical synthetic fixtures, commits generated Markdown under
`agent/node_prompts/`, and reports requested rather than locally resolved tool policy.
