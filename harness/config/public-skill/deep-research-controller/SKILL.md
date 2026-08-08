---
name: deep-research-controller
description: Route multi-source research requests through DeerFlow's all-real Deep Research lifecycle.
---

# Deep Research Controller

This is an all-real research lifecycle. Every result retains
`implementation_mode=all_real`. Treat typed results as the source of truth. A blocked
or unavailable result is incomplete research: report its code directly and never
fabricate findings, evidence, reports, progress, access, authorization, or completion.

Use this workflow after loading it for an ordinary relevant turn. It proposes one
candidate lifecycle action; tool schema, trusted runtime context, and Bundle-local
lifecycle State decide whether that action is allowed.

## 1. Establish the current subject

Read the latest user turn together with the visible typed Deep Research result. Identify
whether there is a currently displayed pending input and which opaque `bundle_id` the
result names. A Run Bundle is the durable record for one research run. Do not recover an
old run from conversation memory, infer an id, or treat ordinary conversation text as a
hidden command.

If a visible pending input asks the user for a response, first decide whether the new
turn directly answers that exact subject. Keep the response in the user message; never
copy it into tool arguments. An independent direction can coexist with a pending input,
but it must be clearly a request to change the research run rather than an answer to the
pending subject.

## 2. Classify intent

Choose one intent only after applying these decision criteria:

| Intent | Choose it only when the user clearly means | Candidate action |
| --- | --- | --- |
| new research request | a new qualifying multi-source research task, not a follow-up about an existing Bundle | `start` |
| correlated pending answer | an answer to the exact visible pending input | `resume` |
| independent same-Run direction | a bounded instruction that changes the focus, scope, comparison, or priority of the selected current run | text-bearing `refine` |
| status request | an inspection request without a requested change | `status` |
| explicit cancellation | an unambiguous request to stop the selected run | `cancel` |

Words such as "note", "remember", "adjust", "fix", or criticism do not choose an
intent by themselves. Do not infer cancellation from dissatisfaction. If the current
subject, intended effect, or target is unclear, ask one clarification and make no
Deep Research lifecycle call in that turn. For an unrelated request, handle it outside
this lifecycle rather than attaching it to a Bundle.

## 3. Select the legal target

For a new research request, use `start` without choosing an id or copying the question
into arguments. For an existing run, use only the opaque `bundle_id` supplied by a
current typed result or an explicitly named available target; never guess a target from a
Handle, a title, a past conversation, or discovery. A correlated answer belongs only to
the selected current pending subject.

An available ended Bundle always needs an explicit `bundle_id`. If a result is
unavailable, do not try to recover it; follow `legal_next_action`, normally a fresh
independent `start`. If an ended result has `legal_next_action="start"`, capacity is
exhausted: do not propose either form of `refine`, even when its refinement projection
shows a retained pending direction.

## 4. Make one exclusive lifecycle call

After selecting one clear intent and legal target, issue exactly one `deep_research`
call in a later assistant turn. There must be no sibling tool call in that turn.

- New request: `deep_research(action="start")`.
- Correlated pending answer: `deep_research(action="resume", bundle_id=...)`; the
  answer remains in the user message.
- Independent direction: `deep_research(action="refine", bundle_id=...,
  refinement="...")`. The text must be the user's clear bounded direction, not a
  reconstructed hidden instruction.
- Inspection: `deep_research(action="status", bundle_id=...)`.
- Explicit stop: `deep_research(action="cancel", bundle_id=...)`.

Never place two Deep Research calls in one assistant turn or pair one with file, search,
or any other tool. Do not make a tool call after ambiguity, for a profile-note request
alone, or merely because an earlier result mentions an ended Bundle.

## 5. Explain the typed result

Explain the returned `code`, the selected Bundle's refinement projection, and
`legal_next_action` separately. The action code describes the submitted request; the
refinement projection describes the Bundle after that request.

- `refinement_pending` means the direction is stored for a legal later boundary. It is
  not proof that planning or findings changed.
- `refinement_applied` means the selected direction's next round committed. It is not a
  claim that the research itself is complete.
- `refinement_conflict` means this submitted direction did not replace the existing
  one. Explain the projection and its legal next action instead of calling it success.
- A suspended result preserves its visible pending input; invite the matching response
  only when that is the legal next action. For blocked, cancelled, stopped, exhausted,
  or unavailable outcomes, state the returned disposition plainly and do not invent a
  retry or recovery path.

When `legal_next_action` is `status`, offer inspection. When it is `resume`, keep the
current subject visible. When it is `refine`, first apply the terminal-pending rule
below. When it is `start`, offer only a fresh independent research request.

## Ambiguity and profile notes

After Research Confirmation, `custom_notes`, `scope_boundaries`, and the accepted
profile remain canonical profile content. Without a clear independent same-Run direction,
do not call `deep_research` or promise a profile write for a request to save or edit one
of those notes. Ask whether the user instead intends a bounded direction; only their
clarified direction may use ordinary text-bearing `refine`.

Do not turn a pending answer into a direction, do not turn criticism into a stop, and do
not turn an ambiguous terminal follow-up into a continuation. Ask one clarification
before any lifecycle call whenever more than one classification is plausible.

## Terminal pending direction

When a current typed result shows an available terminal Bundle with a pending refinement
projection and `legal_next_action="refine"`, do not continue it automatically. Use the
textless continuation form only after the user explicitly asks to continue that queued
direction. Send that exact `bundle_id` and omit `refinement`. Do not reproduce or infer
the stored direction text, use a Handle, or convert a new text-bearing direction into a
continuation.

Stopped, cancelled, and blocked outcomes keep the same rule: they never silently restart
research. A new text-bearing direction remains a normal direction submission, subject to
the returned result and runtime validation. An exhausted terminal result with
`legal_next_action="start"` never permits a continuation.

## Positive examples

- "Research how the policy changed across primary sources" is a new research request:
  make the exclusive `start` call.
- A visible question asks for the intended audience and the user supplies that audience:
  make the exclusive `resume` call; do not put the response in arguments.
- "For this run, compare the regional regulator guidance first" is an independent
  same-Run direction: make one text-bearing `refine` call for the selected Bundle.
- A typed terminal result shows a queued direction and the user says "continue that
  queued direction": make one textless `refine` call with the returned `bundle_id`.
- "What is the current research status?" is a status request: make one `status` call.

## Negative examples

- "Please note this" is ambiguous without a clear effect: ask one clarification; do
  not call the lifecycle.
- "Save this as a profile note" after confirmation is not a hidden write path: do not
  call the lifecycle or promise a profile write.
- "This direction is not useful" is not explicit cancellation. Clarify the desired
  change or stop request before acting.
- A terminal result whose legal next action is `start` is not refinable. Do not submit a
  direction or continuation to that Bundle.
- A deleted or unavailable Bundle is not recoverable. Do not infer a replacement id;
  offer a fresh independent start when the returned legal action allows it.
