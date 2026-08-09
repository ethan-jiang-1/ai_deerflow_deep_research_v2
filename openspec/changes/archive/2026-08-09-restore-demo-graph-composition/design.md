## Context

See [proposal.md](proposal.md) for the motivation. The current shared transport
accepts an adapter and a generic host, then calls `run_deep_research()` without a
`BundleGraphExecutor`. The generic host is used by `tool.py` only for a non-lifecycle
`infra_probe`; a lifecycle call without an executor instead reaches the approved
full-fake fallback in `BundleControl`. The all-real recipe factory exists but real CLI
and TUI entries do not connect it to lifecycle dispatch. The current full-fake commands
use the same presentation-oriented shell, so a repair must make the graph-backed
contract explicit without silently changing their deterministic operator contract.

The trusted executor constructor is already a downstream runtime-composition seam:
the reflected public tool does not expose recipe or checkpoint selection. This change
uses that seam from the demo composition root only. It does not inspect or change
DeerFlow implementation code.

## Goals / Non-Goals

**Goals:**

- Make real CLI and default TUI dispatch an all-real `BundleGraphExecutor` through
  one shared demo runtime factory.
- Add a fixed `fixture_graph` verification composition and surface it only through
  `make demo-fixture-graph`.
- Make missing or mismatched graph composition fail before any result can be presented
  as completed research.
- Preserve the exact zero-credential full-fake command contracts and prove the
  distinction with deterministic tests.

**Non-Goals:**

- Adding caller-controlled recipe, executor, checkpoint, graph-route, provider, or
  recovery inputs.
- Making the fixture-graph route a product entry, a replacement for full-fake, or a
  session-recovery mechanism.
- Changing graph topology, public reflected-tool behavior, provider retry semantics,
  or any upstream DeerFlow, `backend/`, or `frontend/` source.

## Decisions

### One opaque graph-backed demo runtime

Introduce a small internal `build_demo_runtime(mode, adapter)` boundary in
`scripts/_demo_core.py`. It accepts only the local fixed modes `real` and
`fixture_graph`, selects the corresponding existing recipe factory, and creates the
matching `BundleGraphExecutor`. The all-real mode supplies the existing demo-local
node-agent bridge through the recipe factory; fixture-graph mode requires no bridge
and loads the complete fixture catalog with fixture source already enabled by the
command target.

The returned runtime binding owns the executor and the lifecycle transport binding;
entry adapters receive the finished binding rather than individual recipe or executor
parts. This keeps construction authority at the demo runtime boundary and lets both
real adapters share it.

Alternatives rejected:

- Letting CLI flags or TUI constructor parameters choose recipe/checkpoint/executor:
  this would widen presentation authority and diverge from the public tool boundary.
- Having each entry construct a recipe and executor: this duplicates a security and
  compatibility decision and permits drift.
- Omitting the executor and accepting the existing `BundleControl` full-fake fallback:
  it proves no graph lifecycle composition.

### Selected mode is a persisted Bundle fact

When graph-backed runtime construction starts a Bundle, it passes the selected recipe's
existing `implementation_mode` into the Bundle lifecycle's authoritative state and all
later control-result projections read it from that state. The fixture-graph verification
route therefore returns `fixture`; real entries return `all_real`. Existing retained
states and the separately explicit full-fake path preserve the current default of
`all_real` rather than being reinterpreted or exposed as a mode selector.

This is a projection correction, not a new public control. CLI/TUI arguments and the
reflected public tool continue to have no recipe, executor, checkpoint, or mode-label
input. It also makes mode truth restart-durable for a graph-backed Bundle rather than
depending on the entry process that first created it.

### Separate graph lifecycle from infra probe and full-fake paths

Tighten the graph-backed `DemoLifecycleTransport` binding so graph lifecycle dispatch
always forwards its owned executor to `run_deep_research()`. A binding lacking that
executor raises a bounded local startup failure before dispatch. Rename or otherwise
isolate the current generic host construction as an `infra_probe`-only seam; it has no
role in real or fixture-graph lifecycle construction. This prevents graph-backed
entries from invoking `run_deep_research()` without an executor and thereby reaching
the existing full-fake fallback.

Keep the full-fake command path as a separately explicit compatibility route. Its
fixed host/transport arrangement may be represented by a dedicated full-fake factory,
but it must not use the graph-backed runtime mode or be documented as fixture-graph
verification. This is a composition refactor behind the existing command behavior,
not a silent semantic migration of `make demo`, `make demo-scripted`, or
`make demo-tui-fake`.

### Fixed entry routing and truthful command text

`demo_real.py` and the default `demo_tui.py` startup create an adapter after their
existing readiness checks and obtain the `real` runtime binding from the shared
factory. A new dedicated fixture-graph entry uses `fixture_graph`; its Make target
adds `src_fake` only to its child process. The new command has no mode selector.

The new entry `--help` and the concise README command map call it a verification
route. Existing full-fake help and command names retain their zero-credential,
non-research language. The broader entry-surface documentation remains Stage 5 work.

### Completion remains graph-owned

The adapter continues to render only `ResearchRunExperience` updates. It never treats
the `BundleControl` full-fake fallback as a graph-backed completion. A deterministic
fixture-graph composition test must traverse the actual demo transport with concrete
recipe/executor objects and prove that the Bundle checkpoint, returned trace, and
fixture final-delivery gate establish terminal success. The fixture adapter remains
isolated from publication and final-delivery read capabilities, so this verification
does not create or claim report artifacts; its checkpointed final-delivery gate pass,
completed terminal state, and trace are the required deterministic evidence. The
all-real entries are tested for fixed composition and executor handoff; a credentialed
all-real execution is optional rather than being simulated by replacing its external
adapters. Missing delivery evidence or an executor construction failure remains a typed
non-completed/fault path with the existing legal next-action projection.

### Evidence layers

Use the smallest seam that detects composition loss first:

1. Demo-core tests observe the fixed recipe and executor selected for each
   graph-backed mode, verify dispatch receives that executor, and verify the selected
   mode is projected from the created Bundle.
2. Real CLI and default TUI adapter tests prove both invoke the shared runtime rather
   than dispatching without an executor, and verify fail-closed startup behavior.
3. A subprocess test proves `make demo-fixture-graph` reaches fixture graph
   composition while current full-fake commands preserve their output and exit
   contract.
4. A fixture-graph lifecycle test verifies actual graph trace, checkpointed
   final-delivery gate pass, and completed terminal fact through the production demo
   transport. It does not require fixture report publication or widen fixture
   capabilities. A bounded credentialed all-real smoke may supplement this evidence
   but cannot replace it.

## Risks / Trade-offs

- [The full-fake compatibility implementation still shares presentation utilities]
  -> Keep its construction explicit and retain existing command-process tests before
  and after the refactor.
- [Fixture source is missing in an ordinary real process] -> The fixture-graph target
  alone enables it for its child process; the runtime fails boundedly if that verified
  entry precondition is absent.
- [A selected fixture recipe is projected as all-real] -> Persist mode at Bundle
  creation and test the returned terminal result plus a later status/reprojection;
  existing Bundle state retains its default for backward compatibility.
- [A deterministic test could misrepresent an all-real run by replacing its external
  adapters] -> Keep all-real evidence at fixed composition and executor handoff; use
  the complete fixture graph for deterministic lifecycle evidence, and reserve
  all-real execution for an explicit credentialed smoke.
- [A real provider run is nondeterministic or costly] -> Keep it optional and bounded;
  deterministic composition evidence remains the acceptance gate.

## Migration Plan

1. Add red composition tests around the current missing-executor path into the
   full-fake fallback and record the existing full-fake process baseline.
2. Land the shared runtime binding and switch only graph-backed real CLI/TUI starts to
   it; add the new fixture-graph command without changing existing full-fake names.
3. Update command help and the concise README map, then run focused process and
   fixture-graph lifecycle tests before the deterministic project gate.
4. Rollback removes the new verification target and runtime binding changes together;
   it never rewrites retained Bundles, graph checkpoints, or public-tool inputs.
