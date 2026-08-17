"""Trusted public-action dispatch over Bundle-local lifecycle State.

This module deliberately has no GraphHost, session, binding, checkpoint-provider, or
path input.  It turns a trusted runtime envelope plus action-valid input into either a
shared typed Bundle result or the bounded HITL suspension delivery command.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from langchain_core.messages import HumanMessage

from deerflow_deep_research.domain.bundle import BundleId
from deerflow_deep_research.domain.identifiers import BUNDLE_ID_PATTERN  # re-exported for the tool layer
from deerflow_deep_research.domain.lifecycle import (
    AcceptedHumanResponse,
    BundleAvailability,
    BundleControlResult,
    Durability,
    InfrastructureResultCode,
    LegalNextAction,
    LifecycleAction,
    RefinementAdmissionDisposition,
    RefinementOperation,
    ResponseKind,
    ResultCode,
    text_only_content,
)
from deerflow_deep_research.runtime.bundle_lifecycle import (
    BundleAlreadyActive,
    BundleLifecycle,
    BundleLifecycleError,
    CurrentBundleHandle,
)
from deerflow_deep_research.runtime.human_input import HumanInputError, SelectedStartMessage
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope

if TYPE_CHECKING:
    from deerflow_deep_research.runtime.bundle_graph import BundleGraphExecutor
    from deerflow_deep_research.runtime.non_interactive import StartActionInput


class BundleControl:
    """One runtime-owned controller for the five public Bundle lifecycle actions."""

    def __init__(
        self,
        *,
        lifecycle: BundleLifecycle,
        graph_executor: BundleGraphExecutor | None = None,
        graph_executor_factory: Callable[[], BundleGraphExecutor] | None = None,
    ) -> None:
        if graph_executor is not None and graph_executor_factory is not None:
            raise ValueError("graph_executor_composition_ambiguous")
        self._lifecycle = lifecycle
        self._graph_executor = graph_executor
        self._graph_executor_factory = graph_executor_factory

    @staticmethod
    def action_from_wire(value: str) -> LifecycleAction | None:
        """Convert a prevalidated public action without exposing domain contracts to the tool."""

        try:
            return LifecycleAction(value)
        except ValueError:
            return None

    @staticmethod
    def _trusted_log_correlation(
        envelope: Any | None,
        *,
        scope: tuple[str, str],
    ) -> tuple[str | None, str | None]:
        """Expose current trusted correlation to lifecycle logging only."""

        if not isinstance(envelope, TrustedRuntimeEnvelope):
            return None, None
        if envelope.effective_user_id != scope[0] or envelope.outer_thread_id != scope[1]:
            return None, None
        return envelope.outer_thread_id, envelope.outer_run_id

    @staticmethod
    def unavailable_wire_result(*, action: LifecycleAction, code: str) -> dict[str, Any]:
        """Project a bounded lifecycle denial from a trusted runtime boundary."""

        try:
            result_code: ResultCode | InfrastructureResultCode = ResultCode(code)
        except ValueError:
            try:
                result_code = InfrastructureResultCode(code)
            except ValueError:
                result_code = InfrastructureResultCode.RUNTIME_CONTEXT_REQUIRED
        return BundleControl._unavailable(action=action, code=result_code)

    async def dispatch(
        self,
        *,
        action: LifecycleAction,
        effective_user_id: str,
        outer_thread_id: str,
        messages: Sequence[Any],
        tool_call_id: str,
        bundle_id: str | None = None,
        refinement: str | None = None,
        handle: CurrentBundleHandle | None = None,
        start_message: SelectedStartMessage | None = None,
        envelope: Any | None = None,
        start_input: StartActionInput | None = None,
    ) -> Any:
        scope = (effective_user_id, outer_thread_id)
        log_outer_thread_id, log_outer_run_id = self._trusted_log_correlation(envelope, scope=scope)
        try:
            target = self._bundle_id(bundle_id)
        except ValueError:
            return self._unavailable(action=action)
        if action is LifecycleAction.START:
            return await self._start(
                scope=scope,
                tool_call_id=tool_call_id,
                start_message=start_message,
                envelope=envelope,
                start_input=start_input,
                log_outer_thread_id=log_outer_thread_id,
                log_outer_run_id=log_outer_run_id,
            )
        if action is LifecycleAction.STATUS:
            return (await self._lifecycle.status(scope=scope, bundle_id=target, handle=handle)).model_dump(
                mode="json", exclude_none=True
            )
        if action is LifecycleAction.CANCEL:
            return await self._cancel(
                scope=scope,
                bundle_id=target,
                handle=handle,
                log_outer_thread_id=log_outer_thread_id,
                log_outer_run_id=log_outer_run_id,
            )
        if action is LifecycleAction.RESUME:
            return await self._resume(
                scope=scope,
                bundle_id=target,
                handle=handle,
                messages=messages,
                envelope=envelope,
                tool_call_id=tool_call_id,
            )
        if action is LifecycleAction.REFINE:
            return await self._refine(
                scope=scope,
                bundle_id=target,
                handle=handle,
                refinement=refinement,
                operation_key=tool_call_id,
                envelope=envelope,
            )
        return self._unavailable(action=action)

    async def _start(
        self,
        *,
        scope: tuple[str, str],
        tool_call_id: str,
        start_message: SelectedStartMessage | None,
        envelope: Any | None,
        start_input: StartActionInput | None,
        log_outer_thread_id: str | None,
        log_outer_run_id: str | None,
    ) -> Any:
        if start_message is None:
            return self._unavailable(action=LifecycleAction.START, code=ResultCode.START_MESSAGE_INVALID)
        if envelope is None:
            return self._unavailable(action=LifecycleAction.START)
        try:
            executor = self._checked_graph_executor()
        except (RuntimeError, ValueError):
            return self._unavailable(action=LifecycleAction.START)
        try:
            bundle = await self._lifecycle.start(
                scope=scope,
                request_text=start_message.text,
                start_message_id=start_message.message_id,
                implementation_mode=executor.implementation_mode,
                log_outer_thread_id=log_outer_thread_id,
                log_outer_run_id=log_outer_run_id,
            )
        except BundleAlreadyActive as exc:
            try:
                state = await self._lifecycle.read_state(exc.bundle)
            except BundleLifecycleError:
                return self._unavailable(action=LifecycleAction.START)
            same_start = (
                state.start_message_id == start_message.message_id
                and state.start_request_digest == self._lifecycle.request_digest(start_message.text)
            )
            result = self._lifecycle.result_for_state(
                action=LifecycleAction.START,
                bundle=exc.bundle,
                state=state,
                code=None if same_start else ResultCode.ACTIVE_BUNDLE_EXISTS,
            )
            if same_start and state.pending_request_id is not None and state.pending_cursor is not None:
                try:
                    return await executor.reproject(
                        lifecycle=self._lifecycle,
                        bundle=exc.bundle,
                        action=LifecycleAction.START,
                        tool_call_id=tool_call_id,
                    )
                except BundleLifecycleError:
                    return self._unavailable(action=LifecycleAction.START)
                except ValueError:
                    return self._unavailable(action=LifecycleAction.START)
            return result.model_dump(mode="json", exclude_none=True)
        except BundleLifecycleError:
            return self._unavailable(action=LifecycleAction.START)

        try:
            return await executor.start(
                bundle=bundle,
                lifecycle=self._lifecycle,
                envelope=envelope,
                start_message=start_message,
                tool_call_id=tool_call_id,
                start_input=start_input,
            )
        except (BundleLifecycleError, ValueError):
            return self._unavailable(action=LifecycleAction.START)

    async def _resume(
        self,
        *,
        scope: tuple[str, str],
        bundle_id: BundleId | None,
        handle: CurrentBundleHandle | None,
        messages: Sequence[Any],
        envelope: Any | None,
        tool_call_id: str,
    ) -> dict[str, Any]:
        bundle = await self._lifecycle.resolve(scope=scope, bundle_id=bundle_id, handle=handle)
        if bundle is None:
            return self._unavailable(action=LifecycleAction.RESUME)
        if envelope is None:
            return self._unavailable(action=LifecycleAction.RESUME)
        try:
            executor = self._checked_graph_executor()
        except (RuntimeError, ValueError):
            return self._unavailable(action=LifecycleAction.RESUME)
        try:
            state = await self._lifecycle.read_state(bundle)
            if not state.is_active:
                return self._lifecycle.result_for_state(
                    action=LifecycleAction.RESUME,
                    bundle=bundle,
                    state=state,
                ).model_dump(mode="json", exclude_none=True)
            response = self._response_from_messages(messages=messages, state=state)
            return await executor.resume(
                lifecycle=self._lifecycle,
                bundle=bundle,
                envelope=envelope,
                response=response,
                tool_call_id=tool_call_id,
            )
        except BundleLifecycleError as exc:
            if exc.code == "response_mismatch":
                try:
                    current = await self._lifecycle.read_state(bundle)
                except BundleLifecycleError:
                    return self._unavailable(action=LifecycleAction.RESUME)
                return self._lifecycle.result_for_state(
                    action=LifecycleAction.RESUME,
                    bundle=bundle,
                    state=current,
                    code=ResultCode.RESPONSE_MISMATCH,
                ).model_dump(mode="json", exclude_none=True)
            return self._unavailable(action=LifecycleAction.RESUME)
        except HumanInputError as exc:
            try:
                current = await self._lifecycle.read_state(bundle)
            except BundleLifecycleError:
                return self._unavailable(action=LifecycleAction.RESUME)
            return self._lifecycle.result_for_state(
                action=LifecycleAction.RESUME,
                bundle=bundle,
                state=current,
                code=(ResultCode.RESPONSE_MISMATCH if exc.code == "response_mismatch" else ResultCode.RESPONSE_INVALID),
            ).model_dump(mode="json", exclude_none=True)

    async def _cancel(
        self,
        *,
        scope: tuple[str, str],
        bundle_id: BundleId | None,
        handle: CurrentBundleHandle | None,
        log_outer_thread_id: str | None,
        log_outer_run_id: str | None,
    ) -> dict[str, Any]:
        bundle = await self._lifecycle.resolve(scope=scope, bundle_id=bundle_id, handle=handle)
        if bundle is None:
            return self._unavailable(action=LifecycleAction.CANCEL)
        try:
            state = await self._lifecycle.cancel(
                scope=scope,
                bundle_id=bundle.bundle_id,
                log_outer_thread_id=log_outer_thread_id,
                log_outer_run_id=log_outer_run_id,
            )
            return self._lifecycle.result_for_state(
                action=LifecycleAction.CANCEL,
                bundle=bundle,
                state=state,
            ).model_dump(mode="json", exclude_none=True)
        except BundleLifecycleError:
            return self._unavailable(action=LifecycleAction.CANCEL)

    async def _refine(
        self,
        *,
        scope: tuple[str, str],
        bundle_id: BundleId | None,
        handle: CurrentBundleHandle | None,
        refinement: str | None,
        operation_key: str,
        envelope: Any | None,
    ) -> dict[str, Any]:
        try:
            recovered = await self._recover_textless_post_commit_task(
                scope=scope,
                bundle_id=bundle_id,
                envelope=envelope,
            )
            if recovered is not None:
                return recovered
            admission = await self._lifecycle.admit_refinement(
                scope=scope,
                text=refinement,
                operation_key=operation_key if refinement is not None else None,
                bundle_id=bundle_id,
                handle=handle,
            )
            # Resolve only after refinement admission.  In particular, an ended
            # Handle must reach ``BundleLifecycle.admit_refinement`` so it can return the
            # explicit-target requirement instead of being misreported as generic
            # unavailability before the lifecycle rule is evaluated.
            bundle = await self._lifecycle.resolve(scope=scope, bundle_id=bundle_id, handle=handle)
            if bundle is None:
                return self._unavailable(action=LifecycleAction.REFINE)
            state = admission.state
            submitted_operation = (
                RefinementOperation.from_text(operation_key=operation_key, text=refinement)
                if refinement is not None
                else None
            )
            operation_for_round = submitted_operation
            if refinement is None and isinstance(admission.state.admitted_refinement, RefinementOperation):
                # A textless continuation selects this existing trusted record. Keep
                # that identity only through checkpoint reconciliation so a later
                # contender can observe the same committed token without deriving a
                # new public operation or admitting another direction.
                operation_for_round = admission.state.admitted_refinement
            result_code = {
                RefinementAdmissionDisposition.PENDING: ResultCode.REFINEMENT_PENDING,
                RefinementAdmissionDisposition.APPLIED: ResultCode.REFINEMENT_APPLIED,
                RefinementAdmissionDisposition.CONFLICT: ResultCode.REFINEMENT_CONFLICT,
                RefinementAdmissionDisposition.EXHAUSTED: ResultCode.BLOCKED,
            }[admission.disposition]
            if (
                self._has_graph_executor()
                and envelope is not None
                and not state.is_active
                and admission.disposition
                in {RefinementAdmissionDisposition.PENDING, RefinementAdmissionDisposition.CONFLICT}
            ):
                # A terminal pending record can have a prepared checkpoint that is
                # not yet public State. Reconcile only that selected token; a
                # competing direction must return after this branch, never become a
                # new admission now that the first pending slot has cleared.
                executor = self._checked_graph_executor()
                reconciled = await executor.reconcile_prepared_refinement_round(
                    lifecycle=self._lifecycle,
                    scope=scope,
                    bundle=bundle,
                    submitted_operation=operation_for_round,
                )
                if reconciled is not None:
                    result_code = {
                        RefinementAdmissionDisposition.APPLIED: ResultCode.REFINEMENT_APPLIED,
                        RefinementAdmissionDisposition.CONFLICT: ResultCode.REFINEMENT_CONFLICT,
                        RefinementAdmissionDisposition.PENDING: ResultCode.REFINEMENT_PENDING,
                        RefinementAdmissionDisposition.EXHAUSTED: ResultCode.BLOCKED,
                    }[reconciled.disposition]
                    if reconciled.disposition is RefinementAdmissionDisposition.APPLIED:
                        await executor.execute_prepared_refinement_round(
                            lifecycle=self._lifecycle,
                            bundle=bundle,
                            envelope=envelope,
                        )
                    state = await self._lifecycle.read_state(bundle)
                    return self._lifecycle.result_for_state(
                        action=LifecycleAction.REFINE,
                        bundle=bundle,
                        state=state,
                        code=result_code,
                    ).model_dump(mode="json", exclude_none=True)
            if (
                self._has_graph_executor()
                and envelope is not None
                and not admission.state.is_active
                and admission.disposition is RefinementAdmissionDisposition.PENDING
                and (refinement is None or admission.newly_admitted)
            ):
                executor = self._checked_graph_executor()
                prepared = await executor.prepare_refinement_round(
                    lifecycle=self._lifecycle,
                    scope=scope,
                    bundle=bundle,
                    submitted_operation=operation_for_round,
                )
                result_code = {
                    RefinementAdmissionDisposition.APPLIED: ResultCode.REFINEMENT_APPLIED,
                    RefinementAdmissionDisposition.CONFLICT: ResultCode.REFINEMENT_CONFLICT,
                    RefinementAdmissionDisposition.PENDING: ResultCode.REFINEMENT_PENDING,
                    RefinementAdmissionDisposition.EXHAUSTED: ResultCode.BLOCKED,
                }[prepared.disposition]
                if prepared.disposition is RefinementAdmissionDisposition.APPLIED:
                    await executor.execute_prepared_refinement_round(
                        lifecycle=self._lifecycle,
                        bundle=bundle,
                        envelope=envelope,
                    )
                state = await self._lifecycle.read_state(bundle)
            elif (
                self._has_graph_executor()
                and envelope is not None
                and not state.is_active
                and admission.disposition is RefinementAdmissionDisposition.APPLIED
                and submitted_operation is not None
                and state.current_refinement is not None
                and state.current_refinement.operation_key == submitted_operation.operation_key
                and state.current_refinement.text_digest == submitted_operation.text_digest
            ):
                # Recovery after Bundle-State CAS must re-read the checkpoint under
                # execution exclusion. The executor refuses an already-completed or
                # mismatched task, so this cannot replay a later round.
                await self._checked_graph_executor().execute_prepared_refinement_round(
                    lifecycle=self._lifecycle,
                    bundle=bundle,
                    envelope=envelope,
                )
                state = await self._lifecycle.read_state(bundle)
            return self._lifecycle.result_for_state(
                action=LifecycleAction.REFINE,
                bundle=bundle,
                state=state,
                code=result_code,
            ).model_dump(mode="json", exclude_none=True)
        except BundleAlreadyActive as exc:
            try:
                state = await self._lifecycle.read_state(exc.bundle)
            except BundleLifecycleError:
                return self._unavailable(action=LifecycleAction.REFINE)
            return self._lifecycle.result_for_state(
                action=LifecycleAction.REFINE,
                bundle=exc.bundle,
                state=state,
                code=ResultCode.ACTIVE_BUNDLE_EXISTS,
            ).model_dump(mode="json", exclude_none=True)
        except BundleLifecycleError as exc:
            if exc.code == "explicit_bundle_id_required":
                return self._unavailable(action=LifecycleAction.REFINE, code=ResultCode.EXPLICIT_BUNDLE_ID_REQUIRED)
            return self._unavailable(action=LifecycleAction.REFINE)
        except ValueError:
            return self._unavailable(action=LifecycleAction.REFINE, code=ResultCode.INVALID_TRANSITION)

    async def _recover_textless_post_commit_task(
        self,
        *,
        scope: tuple[str, str],
        bundle_id: BundleId | None,
        envelope: Any | None,
    ) -> dict[str, Any] | None:
        """Continue only a current token's already-authorized queued graph task.

        This is the narrow post-CAS recovery path for an explicit textless retry. It
        does not admit a direction: the executor rechecks the selected Bundle's
        current token and checkpoint task under its execution exclusion.
        """

        if bundle_id is None or not self._has_graph_executor() or envelope is None:
            return None
        bundle = await self._lifecycle.resolve(scope=scope, bundle_id=bundle_id, handle=None)
        if bundle is None:
            return None
        state = await self._lifecycle.read_state(bundle)
        if (
            not state.is_active
            or state.pending_request_id is not None
            or state.admitted_refinement is not None
            or state.current_refinement is None
        ):
            return None
        executed = await self._checked_graph_executor().execute_prepared_refinement_round(
            lifecycle=self._lifecycle,
            bundle=bundle,
            envelope=envelope,
        )
        if not executed:
            return None
        current = await self._lifecycle.read_state(bundle)
        return self._lifecycle.result_for_state(
            action=LifecycleAction.REFINE,
            bundle=bundle,
            state=current,
            code=ResultCode.REFINEMENT_APPLIED,
        ).model_dump(mode="json", exclude_none=True)

    @staticmethod
    def _bundle_id(value: str | None) -> BundleId | None:
        return None if value is None else BundleId(value)

    def _checked_graph_executor(self) -> BundleGraphExecutor:
        """Validate the trusted composition only when graph work is needed."""

        executor = self._graph_executor
        if executor is None:
            factory = self._graph_executor_factory
            if factory is None:
                raise RuntimeError("graph_executor_required")
            executor = factory()
            self._graph_executor = executor
        if executor.full_rerun_policy != self._lifecycle.rerun_policy:
            raise ValueError("rerun_policy_composition_mismatch")
        return executor

    def _has_graph_executor(self) -> bool:
        """Report trusted graph availability without constructing graph dependencies."""

        return self._graph_executor is not None or self._graph_executor_factory is not None

    @staticmethod
    def _response_from_messages(*, messages: Sequence[Any], state: Any) -> AcceptedHumanResponse:
        replay_request_ids = dict(zip(state.consumed_message_ids, state.consumed_request_ids, strict=True))
        expected_request_id = state.pending_request_id
        cursor = state.pending_cursor
        cursor_index = next(
            (
                index
                for index, message in enumerate(messages)
                if isinstance(message, HumanMessage) and str(message.id) == cursor
            ),
            None,
        )
        candidates = messages[cursor_index + 1 :] if cursor_index is not None else messages
        message = next(
            (
                item
                for item in reversed(candidates)
                if isinstance(item, HumanMessage) and item.id and not item.additional_kwargs.get("hide_from_ui")
            ),
            None,
        )
        if message is None:
            raise HumanInputError("response_mismatch", "No correlated response is available")
        if expected_request_id is None:
            expected_request_id = replay_request_ids.get(str(message.id))
            if expected_request_id is None:
                raise HumanInputError("response_mismatch", "Bundle has no matching consumed response")
        payload = message.additional_kwargs.get("human_input_response")
        if isinstance(payload, dict):
            if (
                payload.get("version") != 1
                or payload.get("kind") != "human_input_response"
                or payload.get("source") != "deep_research"
                or payload.get("request_id") != expected_request_id
            ):
                raise HumanInputError("response_mismatch", "Response correlation does not match the Bundle")
            try:
                return AcceptedHumanResponse(
                    request_id=expected_request_id,
                    message_id=str(message.id),
                    value=payload.get("value"),
                    response_kind=payload.get("response_kind"),
                    option_id=payload.get("option_id"),
                    action_id=payload.get("action_id"),
                )
            except (TypeError, ValueError) as exc:
                raise HumanInputError("response_invalid", "Response payload is invalid") from exc
        try:
            value = text_only_content(message.content)
        except ValueError as exc:
            raise HumanInputError("response_invalid", "Response content is invalid") from exc
        return AcceptedHumanResponse(
            request_id=expected_request_id,
            message_id=str(message.id),
            value=value,
            response_kind=ResponseKind.TEXT,
        )

    @staticmethod
    def _unavailable(
        *,
        action: LifecycleAction,
        code: ResultCode | InfrastructureResultCode = ResultCode.UNAVAILABLE,
    ) -> dict[str, Any]:
        return BundleControlResult(
            action=action,
            code=code,
            availability=BundleAvailability.UNAVAILABLE,
            durability=Durability.UNAVAILABLE,
            legal_next_action=LegalNextAction.START,
        ).model_dump(mode="json", exclude_none=True)


__all__ = ["BUNDLE_ID_PATTERN", "BundleControl"]
