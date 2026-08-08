## Context

The currently observed all-real run is not a malformed lifecycle:

    checkpoint phase: bootstrap
    pending interrupt phase: hitl1
    returned status: suspended
    execution trace: bootstrap

HITL-1 calls interrupt before node_update("hitl1"), so bootstrap is the last
committed phase. PendingResearchInterrupt already contains the fact the user needs:
the graph is waiting for a HITL-1 response. demo_real.py currently rejects that
valid shape because it requires control.phase to equal hitl1 or hitl2. demo_tui.py
instead treats "start" or "no options" as HITL-1. Both are local guesses about a
protocol neither owns.

This is coupled to a second failure: HITL-1 catches bridge/model failures and
converts them to a generic gate_blocked outcome, while the top-level reflected
tool converts unknown exceptions to checkpoint_inconsistent. The user sees a
generic retry sentence, and the operator cannot recover the useful category.
The existing demo adapter then deletes its temporary workspace at process exit.

The design has to correct the interaction contract, not decorate individual
branches of demo_real.py.

## Design Goals

- One cross-entry interpretation of a lifecycle result and a pending human prompt.
- A user can always tell what happened, where it happened, what is known, what to
  do next, and how to cite a safe diagnostic reference.
- No fabricated progress, provider diagnosis, retry guarantee, or durable-session
  claim.
- A small external interface with the wire parsing, correlation, trace validation,
  redaction, failure classification, and input binding hidden behind it.
- No second graph state machine, pending-request copy, phase cursor, or session
  store.
- Compatibility with the existing research bundle model: a run bundle directory is
  the future product session root, but this bounded demo change does not implement
  that future persistence layer.

## Authority Model

    ResearchState + LangGraph pending interrupt
        sole execution-control authority
                    |
                    v
    lifecycle result + human-input artifact
        transport representation
                    |
                    v
    ResearchRunExperience
        safe projection and diagnostics, never graph control
                    |
          ---------------------
          |                   |
          v                   v
        CLI Adapter         TUI Adapter

The existing three authorities do not change:

- ResearchState and the checkpoint interrupt task decide legal phase, transition,
  and pending-input truth.
- The accepted-submission ledger remains evidence truth.
- workspace/deep-research/research_id remains content truth. Its request, work,
  evidence, synthesis, review, final, and diagnostics subtrees are the natural
  future session directory, not an invitation to create a competing state.json.

ResearchRunExperience is deliberately not called ResearchSession. It is a
process-local Module that presents one run and binds user inputs to the existing
graph. It projects durability honestly. The next product-stage plan may make a
run-bundle directory the durable session that survives process boundaries, but
that work must retain the existing checkpoint as control authority.

## The Run-Experience Module

The new runtime-owned ResearchRunExperience Module is the only caller that
understands a reflected lifecycle return. Its Interface is intentionally small:

    preflight() -> ReadinessReport
    handle(intent, observer=None) -> RunUpdate

RunIntent is a closed set: Start(question), Answer(value), Cancel(), and Status().
RunUpdate is a closed set of Ready, Working, AwaitingInput, Terminal, and Fault.
The optional observer receives only the same safe Working and observed-activity
updates that the final caller can render; it is how a CLI/TUI can show elapsed
local liveness without inventing graph progress.

The Module owns:

- construction of the correct start/resume/cancel/status messages and fresh ids;
- lifecycle dispatch through a narrow demo lifecycle adapter;
- parsing Command, ToolMessage, control JSON, and the human-input artifact;
- exact ordered trace-prefix validation, including repeated logical phases;
- control/request id and generation correlation;
- input-mode and advertised-option validation before building a response;
- conversion of known HITL context into a safe semantic prompt;
- source failure classification, redaction, diagnostic-reference issuance, and
  journal publication;
- the difference between local await cancellation and graph-confirmed cancellation.

The CLI and TUI own only terminal rendering, input widgets, accessibility, and
local elapsed-time presentation. Removing the Module would make both adapters
reimplement the same protocol parsing and error behavior, so it has real depth,
leverage, and locality rather than being a forwarding wrapper.

The existing reflected tool invocation is the production-shaped lifecycle
adapter. A deterministic replay adapter is a second concrete adapter for tests.
The two visual surfaces are separate presentation adapters over the same
RunUpdate Interface.

## Pending Interaction Projection

control.phase continues to mean exactly "the last checkpointed logical phase."
It is never rewritten to make a UI look simpler. The public
DeepResearchControlResult gains an optional bounded pending_input projection:

    pending_input:
      schema_version: 1
      request_id: opaque request id
      pending_phase: hitl1 | hitl2
      generation: integer
      mode: text | choice

Only _result_from_snapshot may derive it, and only from the one validated
PendingResearchInterrupt. It excludes suspension cursor, paths, exception data,
full context, and arbitrary state. A suspended status result includes the same
projection, so status is not condemned to report bootstrap while hiding that input
is pending. A suspended Command still carries the existing human_input artifact as
the full graph-owned request. ResearchRunExperience requires exact agreement
between pending_input and that artifact before it emits AwaitingInput.

This resolves the current valid first suspension as:

    completed: bootstrap
    waiting for: research scope and output preferences
    next action: answer the HITL-1 prompt

It does not add pending phase to ResearchState. The interrupt task remains the
only pending-request authority.

## User-Facing States

RunUpdate exposes safe, structured values rather than raw dictionaries:

    RunSnapshot:
      research_id, durability, checkpoint_phase, completed_trace,
      pending_input, elapsed, delivery_mode

    AwaitingInput:
      snapshot, PromptView, trace_delta

    Terminal:
      snapshot, outcome, trace_delta, trace_verified

    Fault:
      snapshot when available, failure, diagnostic_ref

PromptView is graph-owned in meaning and presentation-owned in wording:

- HITL-1 parses only the known versioned brief context. It shows the research goal,
  proposed scope, missing dimensions, allowed values, and a concise answer example.
  A malformed or unknown version produces a safe generic scope request; arbitrary
  context is never printed.
- HITL-2 renders graph-owned choices with stable option ids plus fixed consequence
  explanations. For example, proceed continues with the current plan, rerun starts
  a new generation, repair seeks more evidence, revise_view revisits the synthesis,
  and stop ends the run. The graph still validates the actual option response.

Working means a dispatch was started. It may show elapsed local time and only
observed activity. If the runtime has no stream writer, delivery_mode is
returned_only and the wording is "waiting for the lifecycle result"; it never
claims that a node, model, or web search is progressing. Returned trace entries
remain completed facts, not a progress estimate.

## Failure And Diagnostic Model

The presentation layer must not reverse-engineer exception text. Failures are
classified at the source into a closed RunFailureCode set:

- configuration.model_missing, configuration.web_tool_missing,
  configuration.environment_invalid
- provider.authentication_failed, provider.unavailable, provider.timeout
- tool.unavailable, tool.execution_failed
- input.invalid_response
- persistence.unavailable, checkpoint.inconsistent
- research.blocked
- protocol.invalid_result
- local.interrupted
- internal.unexpected

Each projected failure contains a safe Chinese explanation, phase when known,
certainty (direct or unknown), next action, retryability, and optional opaque
diagnostic_ref. Unknown exceptions map only to internal.unexpected; they must not
be falsely labelled checkpoint_inconsistent. gate_blocked remains the graph route
or terminal status, but carries a compact causal incident when the node had one.

The node-agent bridge maps configuration, provider, tool, timeout, policy, and
structured-output failures into typed safe problems. HITL-1 routes using that
problem rather than catching every exception as None. A terminal blocked state
stores only the current compact incident code, phase, certainty, and diagnostic
reference in the checkpoint so a later status request can explain why the graph
stopped. It stores no raw exception text.

A DemoDiagnosticJournal writes a bounded redacted record outside the disposable
temporary workspace, under a documented local reports directory. A record contains
only its opaque reference, timestamp, action/phase, closed failure code, certainty,
and a non-reversible fingerprint; it never contains provider bodies, exception
messages, model output, user question, URLs, host paths, credentials, or a
suspension cursor. The UI prints the reference and a stable relative location.
For failures before a run exists, it explicitly says no research record was created.
The future run-bundle session plan may relocate the journal into the bundle's
diagnostics subtree; this change must not promise that migration or cross-process
resume.

## Preflight And Command Boundary

Preflight happens before the interactive question prompt or any graph construction.
For the real path it reports, with safe detail:

- whether a supported model configuration is available;
- whether the required web-search credential/tool path is available;
- the selected real or fake mode;
- that the standalone demo is temporary and non-resumable;
- a clear local environment action if the project environment cannot be selected.

The Make target must avoid emitting an unexplained mismatched VIRTUAL_ENV warning
before the application can render preflight. It either deliberately selects the
agent project environment or fails with a clear command-environment explanation.
No preflight performs a model or web request.

## Migration Of Entry Points

demo_real.py:

- runs preflight before reading the question;
- renders RunUpdate state, prompt, failure, safe diagnostic reference, and
  returned trace only;
- has no _suspension, control.phase, Command, trace-prefix, or request-id logic;
- treats Ctrl-C while awaiting dispatch as local.interrupted and does not claim a
  graph cancel.

demo_tui.py:

- builds UI state from RunUpdate rather than question/starting/hitl1/processing/
  hitl2 inference;
- retains appropriate controls and an explicit graph cancel action only when the
  shared state says cancellation is legal;
- renders the same prompt and failure semantics as the CLI.

The fake and scripted routes use the same Module. Scripted automation may still
choose the graph's documented auto policy, but it cannot bypass preflight or
receive an unclassified raw result.

## Verification Strategy

Tests are organized at the responsible seams:

1. Domain/runtime contract tests assert the first real projection shape:
   checkpoint_phase bootstrap plus pending_input hitl1 produces AwaitingInput.
2. A SCRIPTED_REAL_WORKFLOW runs real bootstrap, HITL-1 interrupt/resume,
   checkpointer, and projection with a replay model/bridge. It proves the
   production graph shape rather than hand-writing a favorable result dictionary.
3. Failure-injection tests cover model missing, tool unavailable, timeout,
   structured-output failure, storage failure, malformed wire result, and unknown
   exception. They assert source-to-category mapping and prove sentinel secrets,
   paths, provider text, and user content never appear in RunUpdate, CLI, TUI, or
   journal.
4. CLI and TUI adapter tests consume identical RunUpdate fixtures. They never
   monkeypatch Command parsing in their own module.
5. A bounded credentialed acceptance path exercises a real provider/tool failure
   when available and records only the redacted diagnostic reference and category.
   It supplements, never replaces, deterministic coverage.

## Out Of Scope And Backlog Boundary

This change does not introduce a durable product Session, a run-bundle manifest,
cross-process resume for the standalone demo, persistent report/artifact browsing,
Gateway/Web integration, a streaming timeline, or a full workbench. Those form the
separate deep-research-run-bundle-session-and-workbench backlog plan.

The important constraint is positive, not merely exclusionary: every change here
must make that future model easier. It must never make a CLI-local state machine,
temporary-only storage, or a second phase/status file the de facto session.
