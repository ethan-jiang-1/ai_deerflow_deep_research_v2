"""Execute the real research graph through one selected Run Bundle.

This adapter is deliberately runtime-owned and injectable only through trusted
composition.  It never derives a research identity, accepts a path, opens a generic
checkpoint provider, or retains a graph between actions.  The selected Bundle owns
the SQLite checkpoint, lifecycle State, evidence ledger, and produced content.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from langgraph.types import Command

from deerflow_deep_research.domain.bundle import RunBundleRef, run_bundle_root
from deerflow_deep_research.domain.context import GraphContextView, SelectedBundleContext
from deerflow_deep_research.domain.invocation import GraphInvocationContext, WorkUnitControllerDependencies
from deerflow_deep_research.domain.lifecycle import (
    MAX_RERUN_GENERATIONS,
    AcceptedHumanResponse,
    CurrentRoundDirection,
    Durability,
    ImplementationMode,
    LifecycleAction,
    LifecycleStatus,
    LogicalPhase,
    RefinementAdmissionDisposition,
    RefinementOperation,
    RunRefinementSource,
)
from deerflow_deep_research.domain.run_experience import (
    FailureCertainty,
    RunFailureCode,
    TerminalIncidentProjection,
)
from deerflow_deep_research.domain.state import BundleLocalState, CheckpointStateBoundExceeded, PhaseStatus
from deerflow_deep_research.graph.rerun import FullRerunPolicy, compile_run_refinement_update
from deerflow_deep_research.runtime.bootstrap_bundle import BootstrapBundleStore
from deerflow_deep_research.runtime.bundle_lifecycle import (
    BundleAlreadyActive,
    BundleLifecycle,
    BundleLifecycleError,
)
from deerflow_deep_research.runtime.bundle_transition import BundleTransitionLease
from deerflow_deep_research.runtime.events import RuntimeObservationProjection
from deerflow_deep_research.runtime.human_input import SelectedStartMessage, pending_from_snapshot, project_suspension
from deerflow_deep_research.runtime.non_interactive import StartActionInput
from deerflow_deep_research.runtime.projection import RuntimeWorkUnitDependencyResolver
from deerflow_deep_research.runtime.request_bundle import RequestBundleStore
from deerflow_deep_research.runtime.research import (
    ResearchGraphRecipe,
    RuntimeNodeDependencyResolver,
    _build_final_delivery_capabilities,
    _build_hitl1_capabilities,
    _build_readiness_capabilities,
    _build_topic_planning_capabilities,
    _build_wave0_capabilities,
    _build_wave1_capabilities,
    _build_wave2_synthesis_capabilities,
    policy_envelope_table,
)
from deerflow_deep_research.runtime.run_observation import RunObservationRecorder, RunObservationStore
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore


@dataclass(frozen=True)
class RefinementRoundPreparation:
    """Internal result for one checkpoint-prepared, Bundle-State-committed direction."""

    state: BundleLocalState
    disposition: RefinementAdmissionDisposition
    round_token: str


class BundleGraphExecutor:
    """Run one recipe without creating a second lifecycle authority.

    The constructor is a trusted runtime/test-composition seam.  Public callers pass
    neither a recipe nor a graph checkpoint through the reflected tool.
    """

    def __init__(
        self,
        *,
        recipe: ResearchGraphRecipe | None = None,
        full_rerun_policy: FullRerunPolicy | None = None,
    ) -> None:
        self._recipe = recipe or ResearchGraphRecipe.all_real()
        self._full_rerun_policy = full_rerun_policy or FullRerunPolicy()
        if self._full_rerun_policy.max_rerun_generations > MAX_RERUN_GENERATIONS:
            raise ValueError("public_generation_ceiling_exceeded")

    @property
    def full_rerun_policy(self) -> FullRerunPolicy:
        """Expose the immutable composition input for compatibility checks only."""

        return self._full_rerun_policy

    @property
    def implementation_mode(self) -> ImplementationMode:
        """Expose the selected recipe mode for trusted lifecycle projection."""

        return self._recipe.implementation_mode

    async def prepare_refinement_round(
        self,
        *,
        lifecycle: BundleLifecycle,
        scope: tuple[str, str],
        bundle: RunBundleRef,
        submitted_operation: RefinementOperation | None,
    ) -> RefinementRoundPreparation:
        """Prepare the exact rerun writer update, then CAS one pending direction.

        This is an internal lifecycle/graph seam.  It does not invoke a graph node;
        the queued graph task is continued separately only after the Bundle State CAS.
        """

        if lifecycle.rerun_policy != self._full_rerun_policy:
            raise ValueError("rerun_policy_composition_mismatch")
        if bundle.scope_bucket != lifecycle._bucket_for(scope):
            raise BundleLifecycleError("bundle_unavailable")
        # This lock has no lifecycle facts. It only makes fresh publication and an
        # ended Bundle's terminal-to-active CAS one linearizable scope decision.
        async with lifecycle.scope_exclusion(scope=scope) as scope_lease:
            active = await lifecycle.discover_active(scope=scope)
            if active is not None and active != bundle:
                raise BundleAlreadyActive(active)
            scope_lease.ensure_live()
            prepared = await self._prepare_refinement_round_under_transition(
                lifecycle=lifecycle,
                bundle=bundle,
                submitted_operation=submitted_operation,
            )
            scope_lease.ensure_live()
            return prepared

    async def reconcile_prepared_refinement_round(
        self,
        *,
        lifecycle: BundleLifecycle,
        scope: tuple[str, str],
        bundle: RunBundleRef,
        submitted_operation: RefinementOperation | None,
    ) -> RefinementRoundPreparation | None:
        """Commit only an already-prepared matching checkpoint transition.

        This recovery path deliberately does not compile or write a new checkpoint.
        It exists so a selected retry can close the one known pre-CAS gap without
        turning a competing text-bearing request into ordinary admission.
        """

        if lifecycle.rerun_policy != self._full_rerun_policy:
            raise ValueError("rerun_policy_composition_mismatch")
        if bundle.scope_bucket != lifecycle._bucket_for(scope):
            raise BundleLifecycleError("bundle_unavailable")
        async with lifecycle.scope_exclusion(scope=scope) as scope_lease:
            active = await lifecycle.discover_active(scope=scope)
            if active is not None and active != bundle:
                raise BundleAlreadyActive(active)
            scope_lease.ensure_live()
            reconciled = await self._reconcile_prepared_refinement_round_under_transition(
                lifecycle=lifecycle,
                bundle=bundle,
                submitted_operation=submitted_operation,
            )
            scope_lease.ensure_live()
            return reconciled

    async def _prepare_refinement_round_under_transition(
        self,
        *,
        lifecycle: BundleLifecycle,
        bundle: RunBundleRef,
        submitted_operation: RefinementOperation | None,
    ) -> RefinementRoundPreparation:
        """Prepare and commit one round while the caller owns its scope decision."""

        store = lifecycle._state_store(bundle)
        async with store.transition() as lease:
            state = await store.read(lease=lease)
            replay = self._committed_replay(state=state, submitted_operation=submitted_operation)
            if replay is not None:
                return replay
            reconciled = await self._reconcile_prepared_checkpoint(
                lifecycle=lifecycle,
                bundle=bundle,
                state=state,
                lease=lease,
                submitted_operation=submitted_operation,
            )
            if reconciled is not None:
                return reconciled
            pending = state.admitted_refinement
            if not isinstance(pending, RefinementOperation):
                raise BundleLifecycleError("refinement_transition_invalid")
            if state.is_active or state.terminal_status is None:
                raise BundleLifecycleError("refinement_transition_invalid")
            if submitted_operation is None:
                disposition = RefinementAdmissionDisposition.APPLIED
            elif self._same_operation(pending, submitted_operation):
                disposition = RefinementAdmissionDisposition.APPLIED
            else:
                disposition = RefinementAdmissionDisposition.CONFLICT

            source = RunRefinementSource(
                direction=CurrentRoundDirection(
                    text=pending.text,
                    round=state.refinement_round + 1,
                    generation=state.generation + 1,
                ),
                round_token=self._round_token(bundle=bundle, state=state),
            )
            await self._prepare_refinement_checkpoint(
                lifecycle=lifecycle,
                bundle=bundle,
                state=state,
                lease=lease,
                source=source,
            )
            lifecycle._fault("after_refinement_checkpoint_prepared")
            lifecycle._fault("before_refinement_bundle_cas")
            committed = await lifecycle.commit_prepared_refinement_round(
                bundle=bundle,
                expected_state=state,
                lease=lease,
            )
            if committed.current_refinement is None or committed.current_refinement.round_token != source.round_token:
                raise BundleLifecycleError("refinement_transition_invalid")
            lifecycle._fault("after_refinement_bundle_cas")
            return RefinementRoundPreparation(
                state=committed,
                disposition=disposition,
                round_token=source.round_token,
            )

    async def _reconcile_prepared_refinement_round_under_transition(
        self,
        *,
        lifecycle: BundleLifecycle,
        bundle: RunBundleRef,
        submitted_operation: RefinementOperation | None,
    ) -> RefinementRoundPreparation | None:
        """Read the selected pending record and commit it only if checkpointed."""

        store = lifecycle._state_store(bundle)
        async with store.transition() as lease:
            state = await store.read(lease=lease)
            replay = self._committed_replay(state=state, submitted_operation=submitted_operation)
            if replay is not None:
                return replay
            return await self._reconcile_prepared_checkpoint(
                lifecycle=lifecycle,
                bundle=bundle,
                state=state,
                lease=lease,
                submitted_operation=submitted_operation,
            )

    async def _reconcile_prepared_checkpoint(
        self,
        *,
        lifecycle: BundleLifecycle,
        bundle: RunBundleRef,
        state: BundleLocalState,
        lease: BundleTransitionLease,
        submitted_operation: RefinementOperation | None,
    ) -> RefinementRoundPreparation | None:
        """Return ``None`` unless the selected pending operation is already prepared."""

        pending = state.admitted_refinement
        if not isinstance(pending, RefinementOperation) or state.is_active or state.terminal_status is None:
            return None
        source = RunRefinementSource(
            direction=CurrentRoundDirection(
                text=pending.text,
                round=state.refinement_round + 1,
                generation=state.generation + 1,
            ),
            round_token=self._round_token(bundle=bundle, state=state),
        )
        if not await self._checkpoint_matches_prepared_refinement(
            lifecycle=lifecycle,
            bundle=bundle,
            lease=lease,
            source=source,
        ):
            return None
        if submitted_operation is None or self._same_operation(pending, submitted_operation):
            disposition = RefinementAdmissionDisposition.APPLIED
        else:
            disposition = RefinementAdmissionDisposition.CONFLICT
        committed = await lifecycle.commit_prepared_refinement_round(
            bundle=bundle,
            expected_state=state,
            lease=lease,
        )
        if committed.current_refinement is None or committed.current_refinement.round_token != source.round_token:
            raise BundleLifecycleError("refinement_transition_invalid")
        return RefinementRoundPreparation(
            state=committed,
            disposition=disposition,
            round_token=source.round_token,
        )

    async def start(
        self,
        *,
        lifecycle: BundleLifecycle,
        bundle: RunBundleRef,
        envelope: Any,
        start_message: SelectedStartMessage,
        tool_call_id: str,
        start_input: StartActionInput | None = None,
    ) -> dict[str, Any] | Command:
        async with lifecycle.execution_exclusion(bundle) as execution_lease:
            execution_lease.ensure_live()
            async with lifecycle.open_graph_checkpoint(bundle) as saver:
                graph = self._recipe.builder.compile(checkpointer=saver)
                config = self._config(bundle)
                snapshot = await graph.aget_state(config)
                if snapshot and snapshot.values:
                    result = await self._project(
                        lifecycle=lifecycle,
                        bundle=bundle,
                        envelope=envelope,
                        action=LifecycleAction.START,
                        graph=graph,
                        config=config,
                        tool_call_id=tool_call_id,
                    )
                else:
                    state = await lifecycle.read_state(bundle)
                    journal_envelope = await self._journal_envelope(
                        lifecycle=lifecycle,
                        bundle=bundle,
                        state=state,
                        envelope=envelope,
                    )
                    execution_lease.ensure_live()
                    try:
                        await graph.ainvoke(
                            self._initial_graph_state(
                                bundle=bundle,
                                state=state,
                                start_message=start_message,
                                start_input=start_input,
                            ),
                            config=config,
                            context=await self._context(envelope=journal_envelope, bundle=bundle),
                        )
                    except CheckpointStateBoundExceeded as exc:
                        await self._raise_bound_breach(lifecycle=lifecycle, bundle=bundle, exc=exc)
                    execution_lease.ensure_live()
                    result = await self._project(
                        lifecycle=lifecycle,
                        bundle=bundle,
                        envelope=envelope,
                        action=LifecycleAction.START,
                        graph=graph,
                        config=config,
                        tool_call_id=tool_call_id,
                    )
            return await self._continue_completed_refinement_if_eligible(
                lifecycle=lifecycle,
                bundle=bundle,
                envelope=envelope,
                action=LifecycleAction.START,
                initial_result=result,
                execution_lease=execution_lease,
            )

    async def execute_prepared_refinement_round(
        self,
        *,
        lifecycle: BundleLifecycle,
        bundle: RunBundleRef,
        envelope: Any,
        execution_lease: BundleTransitionLease | None = None,
    ) -> bool:
        """Run a matching queued refinement task once under the execution exclusion."""

        if execution_lease is not None:
            return await self._execute_prepared_refinement_round_under_exclusion(
                lifecycle=lifecycle,
                bundle=bundle,
                envelope=envelope,
                execution_lease=execution_lease,
            )
        async with lifecycle.execution_exclusion(bundle) as acquired_lease:
            return await self._execute_prepared_refinement_round_under_exclusion(
                lifecycle=lifecycle,
                bundle=bundle,
                envelope=envelope,
                execution_lease=acquired_lease,
            )

    async def _execute_prepared_refinement_round_under_exclusion(
        self,
        *,
        lifecycle: BundleLifecycle,
        bundle: RunBundleRef,
        envelope: Any,
        execution_lease: BundleTransitionLease,
    ) -> bool:
        """Continue the one queued task after the caller owns execution exclusion."""

        execution_lease.ensure_live()
        state = await lifecycle.read_state(bundle)
        current = state.current_refinement
        if current is None:
            return False
        source = RunRefinementSource(
            direction=CurrentRoundDirection(
                text=current.text,
                round=current.round,
                generation=current.generation,
            ),
            round_token=current.round_token,
        )
        journal_envelope = await self._journal_envelope(
            lifecycle=lifecycle,
            bundle=bundle,
            state=state,
            envelope=envelope,
        )
        config = self._config(bundle)
        async with lifecycle.open_graph_checkpoint(bundle) as saver:
            graph = self._recipe.builder.compile(checkpointer=saver)
            snapshot = await graph.aget_state(config)
            if snapshot is None or not snapshot.values:
                raise BundleLifecycleError("bundle_graph_missing")
            if not self._matches_prepared_refinement(
                values=dict(snapshot.values),
                bundle=bundle,
                source=source,
            ):
                return False
            if tuple(task.name for task in snapshot.tasks) != ("topic_planning",):
                return False
            execution_lease.ensure_live()
            try:
                await graph.ainvoke(
                    None,
                    config=config,
                    context=await self._context(envelope=journal_envelope, bundle=bundle),
                )
            except CheckpointStateBoundExceeded as exc:
                await self._raise_bound_breach(lifecycle=lifecycle, bundle=bundle, exc=exc)
            execution_lease.ensure_live()
            completed = await graph.aget_state(config)
        if completed is None or not completed.values:
            raise BundleLifecycleError("bundle_graph_missing")
        await lifecycle.sync_graph_progress(
            bundle=bundle,
            values=dict(completed.values),
            pending=None,
            log_outer_thread_id=getattr(envelope, "outer_thread_id", None),
            log_outer_run_id=getattr(envelope, "outer_run_id", None),
        )
        await self._continue_completed_refinement_if_eligible(
            lifecycle=lifecycle,
            bundle=bundle,
            envelope=envelope,
            action=LifecycleAction.REFINE,
            initial_result=None,
            execution_lease=execution_lease,
        )
        return True

    async def _continue_completed_refinement_if_eligible(
        self,
        *,
        lifecycle: BundleLifecycle,
        bundle: RunBundleRef,
        envelope: Any,
        action: LifecycleAction,
        initial_result: dict[str, Any] | Command | None,
        execution_lease: BundleTransitionLease,
    ) -> dict[str, Any] | Command | None:
        """Consume only a graph-synchronized completed terminal pending direction."""

        state = await lifecycle.read_state(bundle)
        pending = state.admitted_refinement
        if (
            state.is_active
            or state.terminal_status is not LifecycleStatus.COMPLETED
            or not isinstance(pending, RefinementOperation)
        ):
            return initial_result
        scope = self._scope_from_envelope(envelope)
        try:
            prepared = await self.prepare_refinement_round(
                lifecycle=lifecycle,
                scope=scope,
                bundle=bundle,
                submitted_operation=pending,
            )
        except BundleAlreadyActive:
            return initial_result
        if prepared.disposition is not RefinementAdmissionDisposition.APPLIED:
            return initial_result
        await self.execute_prepared_refinement_round(
            lifecycle=lifecycle,
            bundle=bundle,
            envelope=envelope,
            execution_lease=execution_lease,
        )
        if initial_result is None:
            return None
        current = await lifecycle.read_state(bundle)
        return lifecycle.result_for_state(action=action, bundle=bundle, state=current).model_dump(
            mode="json",
            exclude_none=True,
        )

    @staticmethod
    def _scope_from_envelope(envelope: Any) -> tuple[str, str]:
        """Read only the trusted runtime scope used for the selected Bundle."""

        effective_user_id = getattr(envelope, "effective_user_id", None)
        outer_thread_id = getattr(envelope, "outer_thread_id", None)
        if not isinstance(effective_user_id, str) or not isinstance(outer_thread_id, str):
            raise BundleLifecycleError("bundle_unavailable")
        return (effective_user_id, outer_thread_id)

    async def _prepare_refinement_checkpoint(
        self,
        *,
        lifecycle: BundleLifecycle,
        bundle: RunBundleRef,
        state: BundleLocalState,
        lease: BundleTransitionLease,
        source: RunRefinementSource,
    ) -> None:
        """Use only the shared compiler output through the production rerun writer."""

        config = self._config(bundle)
        lifecycle._fault("before_refinement_checkpoint_preparation")
        if await self._checkpoint_matches_prepared_refinement(
            lifecycle=lifecycle,
            bundle=bundle,
            lease=lease,
            source=source,
        ):
            return
        async with lifecycle.open_graph_checkpoint(bundle, lease=lease) as saver:
            graph = self._recipe.builder.compile(checkpointer=saver)
            snapshot = await graph.aget_state(config)
            if snapshot is None or not snapshot.values:
                raise BundleLifecycleError("bundle_graph_missing")
            values = dict(snapshot.values)
            self._require_terminal_snapshot(values=values, bundle=bundle, state=state)
            compiled = compile_run_refinement_update(
                values,
                policy=self._full_rerun_policy,
                run_refinement=source,
            )
            if compiled.is_replay or compiled.plan.route != "topic_planning":
                raise BundleLifecycleError("refinement_transition_invalid")
            lease.ensure_live()
            await graph.aupdate_state(config, compiled.to_state_update(), as_node="rerun")
            lease.ensure_live()
            prepared = await graph.aget_state(config)
            if prepared is None or not self._matches_prepared_refinement(
                values=dict(prepared.values), bundle=bundle, source=source
            ):
                raise BundleLifecycleError("refinement_transition_invalid")

    async def _checkpoint_matches_prepared_refinement(
        self,
        *,
        lifecycle: BundleLifecycle,
        bundle: RunBundleRef,
        lease: BundleTransitionLease,
        source: RunRefinementSource,
    ) -> bool:
        """Read the Bundle-contained checkpoint without invoking a graph node."""

        config = self._config(bundle)
        async with lifecycle.open_graph_checkpoint(bundle, lease=lease) as saver:
            graph = self._recipe.builder.compile(checkpointer=saver)
            snapshot = await graph.aget_state(config)
        return snapshot is not None and self._matches_prepared_refinement(
            values=dict(snapshot.values),
            bundle=bundle,
            source=source,
        )

    @staticmethod
    def _same_operation(first: RefinementOperation, second: RefinementOperation) -> bool:
        return first.operation_key == second.operation_key and first.text_digest == second.text_digest

    @staticmethod
    def _round_token(*, bundle: RunBundleRef, state: BundleLocalState) -> str:
        pending = state.admitted_refinement
        if not isinstance(pending, RefinementOperation):
            raise BundleLifecycleError("refinement_transition_invalid")
        from deerflow_deep_research.domain.lifecycle import refinement_round_token

        return refinement_round_token(
            bundle_id=bundle.bundle_id.value,
            operation_key=pending.operation_key,
            text_digest=pending.text_digest,
            round=state.refinement_round + 1,
            generation=state.generation + 1,
        )

    @classmethod
    def _committed_replay(
        cls,
        *,
        state: BundleLocalState,
        submitted_operation: RefinementOperation | None,
    ) -> RefinementRoundPreparation | None:
        current = state.current_refinement
        if current is None:
            return None
        if submitted_operation is None:
            raise BundleLifecycleError("refinement_transition_invalid")
        if cls._same_operation(current, submitted_operation):
            return RefinementRoundPreparation(
                state=state,
                disposition=RefinementAdmissionDisposition.APPLIED,
                round_token=current.round_token,
            )
        if state.admitted_refinement is None:
            return RefinementRoundPreparation(
                state=state,
                disposition=RefinementAdmissionDisposition.CONFLICT,
                round_token=current.round_token,
            )
        return None

    @staticmethod
    def _matches_prepared_refinement(
        *,
        values: dict[str, Any],
        bundle: RunBundleRef,
        source: RunRefinementSource,
    ) -> bool:
        raw_direction = values.get("current_refinement")
        return (
            values.get("bundle_id") == bundle.bundle_id.value
            and values.get("generation") == source.direction.generation
            and values.get("phase") == LogicalPhase.RERUN.value
            and values.get("route") == "topic_planning"
            and values.get("refinement_round_token") == source.round_token
            and raw_direction == source.direction.model_dump(mode="json")
        )

    @staticmethod
    def _require_terminal_snapshot(
        *,
        values: dict[str, Any],
        bundle: RunBundleRef,
        state: BundleLocalState,
    ) -> None:
        if (
            values.get("bundle_id") != bundle.bundle_id.value
            or values.get("generation") != state.generation
            or values.get("phase_status") != PhaseStatus.TERMINAL.value
            or values.get("terminal_status") != state.terminal_status.value
        ):
            raise BundleLifecycleError("bundle_graph_invalid")

    async def resume(
        self,
        *,
        lifecycle: BundleLifecycle,
        bundle: RunBundleRef,
        envelope: Any,
        response: AcceptedHumanResponse,
        tool_call_id: str,
    ) -> dict[str, Any] | Command:
        async with lifecycle.execution_exclusion(bundle) as execution_lease:
            execution_lease.ensure_live()
            async with lifecycle.open_graph_checkpoint(bundle) as saver:
                graph = self._recipe.builder.compile(checkpointer=saver)
                config = self._config(bundle)
                snapshot = await graph.aget_state(config)
                if not snapshot or not snapshot.values:
                    raise BundleLifecycleError("bundle_graph_missing")
                state = await lifecycle.read_state(bundle)
                journal_envelope = await self._journal_envelope(
                    lifecycle=lifecycle,
                    bundle=bundle,
                    state=state,
                    envelope=envelope,
                )
                try:
                    await graph.ainvoke(
                        Command(resume=response.model_dump(mode="json")),
                        config=config,
                        context=await self._context(envelope=journal_envelope, bundle=bundle),
                    )
                except CheckpointStateBoundExceeded as exc:
                    await self._raise_bound_breach(lifecycle=lifecycle, bundle=bundle, exc=exc)
                execution_lease.ensure_live()
                result = await self._project(
                    lifecycle=lifecycle,
                    bundle=bundle,
                    envelope=envelope,
                    action=LifecycleAction.RESUME,
                    graph=graph,
                    config=config,
                    tool_call_id=tool_call_id,
                )
            return await self._continue_completed_refinement_if_eligible(
                lifecycle=lifecycle,
                bundle=bundle,
                envelope=envelope,
                action=LifecycleAction.RESUME,
                initial_result=result,
                execution_lease=execution_lease,
            )

    async def continue_run(
        self,
        *,
        lifecycle: BundleLifecycle,
        bundle: RunBundleRef,
        envelope: Any,
        tool_call_id: str,
    ) -> dict[str, Any] | Command:
        """Continue a process-death orphan from its durable checkpoint (REG-023).

        No human response is constructed or required: the graph re-enters at its
        persisted checkpoint under the execution exclusion lease and proceeds
        through its normal phase machinery to a natural terminal.
        """
        async with lifecycle.execution_exclusion(bundle) as execution_lease:
            execution_lease.ensure_live()
            async with lifecycle.open_graph_checkpoint(bundle) as saver:
                graph = self._recipe.builder.compile(checkpointer=saver)
                config = self._config(bundle)
                snapshot = await graph.aget_state(config)
                if not snapshot or not snapshot.values:
                    raise BundleLifecycleError("bundle_graph_missing")
                state = await lifecycle.read_state(bundle)
                journal_envelope = await self._journal_envelope(
                    lifecycle=lifecycle,
                    bundle=bundle,
                    state=state,
                    envelope=envelope,
                )
                try:
                    await graph.ainvoke(
                        None,
                        config=config,
                        context=await self._context(envelope=journal_envelope, bundle=bundle),
                    )
                except CheckpointStateBoundExceeded as exc:
                    await self._raise_bound_breach(lifecycle=lifecycle, bundle=bundle, exc=exc)
                execution_lease.ensure_live()
                result = await self._project(
                    lifecycle=lifecycle,
                    bundle=bundle,
                    envelope=envelope,
                    action=LifecycleAction.RESUME,
                    graph=graph,
                    config=config,
                    tool_call_id=tool_call_id,
                )
            return await self._continue_completed_refinement_if_eligible(
                lifecycle=lifecycle,
                bundle=bundle,
                envelope=envelope,
                action=LifecycleAction.RESUME,
                initial_result=result,
                execution_lease=execution_lease,
            )

    async def reproject(
        self,
        *,
        lifecycle: BundleLifecycle,
        bundle: RunBundleRef,
        action: LifecycleAction,
        tool_call_id: str,
    ) -> dict[str, Any] | Command:
        """Reproject committed graph/Bundle facts after outer delivery failure."""

        async with lifecycle.open_graph_checkpoint(bundle) as saver:
            graph = self._recipe.builder.compile(checkpointer=saver)
            return await self._project(
                lifecycle=lifecycle,
                bundle=bundle,
                envelope=None,
                action=action,
                graph=graph,
                config=self._config(bundle),
                tool_call_id=tool_call_id,
            )

    @staticmethod
    def _config(bundle: RunBundleRef) -> dict[str, dict[str, str]]:
        return {"configurable": {"thread_id": bundle.bundle_id.value, "checkpoint_ns": ""}}

    @staticmethod
    def _bound_breach_incident(exc: CheckpointStateBoundExceeded) -> TerminalIncidentProjection:
        try:
            return TerminalIncidentProjection(
                code=RunFailureCode.CHECKPOINT_INCONSISTENT,
                phase=exc.phase,
                certainty=FailureCertainty.DIRECT,
            )
        except ValueError:
            return TerminalIncidentProjection(
                code=RunFailureCode.CHECKPOINT_INCONSISTENT,
                certainty=FailureCertainty.DIRECT,
            )

    async def _raise_bound_breach(
        self,
        *,
        lifecycle: BundleLifecycle,
        bundle: RunBundleRef,
        exc: CheckpointStateBoundExceeded,
    ) -> None:
        """Persist the blocked terminal, then surface a bounded lifecycle error.

        The over-bound bytes were rejected before persistence, so the graph checkpoint
        carries no terminal facts; the Bundle-local State owns the honest outcome.

        @impl REG-008
        """

        await lifecycle.record_internal_block(bundle=bundle, incident=self._bound_breach_incident(exc))
        raise BundleLifecycleError("bundle_graph_over_bound")

    @staticmethod
    def _initial_graph_state(
        *,
        bundle: RunBundleRef,
        state: BundleLocalState,
        start_message: SelectedStartMessage,
        start_input: StartActionInput | None = None,
    ) -> dict[str, Any]:
        """Create the graph's bounded working payload from authoritative Bundle State.

        ``bundle_id`` remains an internal graph-field spelling while its value is the
        opaque Bundle id.  It is never accepted, projected, or used to resolve a path;
        the compatibility field is retired with the graph-state contract migration.
        """

        if state.bundle_id != bundle.bundle_id:
            raise BundleLifecycleError("bundle_state_identity_mismatch")
        # Keep this graph payload deliberately partial: graph reducers supply their
        # own defaults, while lifecycle/request facts come from the already-published
        # Bundle State.  No compatibility checkpoint object is instantiated here.
        initial_state = {
            "schema_version": 3,
            "bundle_id": bundle.bundle_id.value,
            "generation": state.generation,
            "start_message_id": start_message.message_id,
            "request_digest": state.start_request_digest,
            "request_text": start_message.text,
            "phase": LogicalPhase.BOOTSTRAP.value,
            "phase_status": PhaseStatus.IN_PROGRESS.value,
            "waiting_for": None,
            "terminal_status": None,
            "terminal_reason": None,
            "gate_attempts_by_phase": {},
            "repair_budget_by_phase": {},
            "work_specs_by_id": {},
            "attempts_by_id": {},
            "work_status_by_id": {},
            "active_attempt_by_work_id": {},
            "terminal_failures_by_attempt_id": {},
            "accepted_submission_refs": (),
            "content_refs": (),
            "execution_trace": (),
        }
        if start_input is not None and start_input.non_interactive_policy is not None:
            initial_state["non_interactive_policy"] = start_input.non_interactive_policy.graph_value()
        return initial_state

    async def _project(
        self,
        *,
        lifecycle: BundleLifecycle,
        bundle: RunBundleRef,
        envelope: Any | None,
        action: LifecycleAction,
        graph: Any,
        config: dict[str, Any],
        tool_call_id: str,
    ) -> dict[str, Any] | Command:
        snapshot = await graph.aget_state(config)
        if not snapshot or not snapshot.values:
            raise BundleLifecycleError("bundle_graph_missing")
        values = dict(snapshot.values)
        pending = pending_from_snapshot(snapshot)
        state = await lifecycle.sync_graph_progress(
            bundle=bundle,
            values=values,
            pending=pending,
            log_outer_thread_id=getattr(envelope, "outer_thread_id", None),
            log_outer_run_id=getattr(envelope, "outer_run_id", None),
        )
        result = lifecycle.result_for_state(action=action, bundle=bundle, state=state)
        if pending is not None and state.is_active:
            return project_suspension(pending=pending, result=result, tool_call_id=tool_call_id)
        return result.model_dump(mode="json", exclude_none=True)

    async def _context(self, *, envelope: Any, bundle: RunBundleRef) -> GraphInvocationContext:
        selected = SelectedBundleContext(bundle=bundle)
        root = run_bundle_root(bundle)
        graph_context = GraphContextView(
            research_scope_id=bundle.bundle_id.value,
            workspace_root=f"/mnt/user-data/{root}",
            uploads_root="/mnt/user-data/uploads",
            outputs_root=f"/mnt/user-data/outputs/{root}",
        )
        adapter_kinds = dict(self._recipe.adapter_kinds)

        def is_real(logical_name: str) -> bool:
            return adapter_kinds[logical_name].value == "real"

        bridge_factory = self._recipe.node_agent_bridge_factory
        hitl1 = _build_hitl1_capabilities(envelope, graph_context, bridge_factory) if is_real("hitl1") else None
        topic_planning = (
            _build_topic_planning_capabilities(envelope, graph_context, bridge_factory)
            if is_real("topic_planning")
            else None
        )
        wave0 = _build_wave0_capabilities(envelope, graph_context, bridge_factory) if is_real("wave0") else None
        wave1 = _build_wave1_capabilities(envelope, graph_context, bridge_factory) if is_real("wave1") else None
        wave2 = (
            _build_wave2_synthesis_capabilities(envelope, graph_context, bridge_factory)
            if is_real("wave2_synthesis")
            else None
        )
        readiness = (
            _build_readiness_capabilities(envelope, graph_context, bridge_factory) if is_real("readiness") else None
        )
        final_delivery = (
            _build_final_delivery_capabilities(envelope, graph_context, bridge_factory)
            if is_real("final_delivery")
            else None
        )
        base_resolver = RuntimeNodeDependencyResolver(
            graph_context,
            hitl1 or topic_planning,
            capabilities_by_node={
                name: capability
                for name, capability in {
                    "topic_planning": topic_planning,
                    "wave2_synthesis": wave2,
                    "readiness": readiness,
                    "final_delivery": final_delivery,
                }.items()
                if capability is not None
            },
            selected_bundle=selected,
            full_rerun_policy=self._full_rerun_policy,
        )
        worker_resolver = RuntimeNodeDependencyResolver(
            graph_context,
            wave0 or wave1,
            capabilities_by_node={
                name: capability
                for name, capability in {
                    "wave0": wave0,
                    "targeted_evidence": wave0,
                    "wave1": wave1,
                }.items()
                if capability is not None
            },
            selected_bundle=selected,
            full_rerun_policy=self._full_rerun_policy,
        )
        store_factory = self._recipe.work_unit_store_factory or WorkUnitStore.create
        store = await store_factory(envelope, bundle=bundle)
        work_units = WorkUnitControllerDependencies(
            store=store,
            resolver=RuntimeWorkUnitDependencyResolver(graph_context, worker_resolver, store),
        )
        bootstrap = (
            await BootstrapBundleStore.create(envelope, bundle=bundle)
            if self._recipe.requires_bootstrap_bundle
            else None
        )
        request_factory = self._recipe.request_bundle_store_factory or RequestBundleStore.create
        request = await request_factory(envelope, bundle=bundle) if self._recipe.requires_request_bundle else None
        return GraphInvocationContext(
            graph_context=graph_context,
            dependency_resolver=base_resolver,
            work_units=work_units,
            bootstrap_bundle=bootstrap,
            request_bundle=request,
            synthesis_bundle=store,
            publication_bundle=store,
            final_delivery_bundle=store,
            event_recorder=(
                envelope.event_recorder_factory(bundle.bundle_id.value)
                if getattr(envelope, "event_recorder_factory", None) is not None
                else None
            ),
            observation_projection=RuntimeObservationProjection(
                bundle_id=bundle.bundle_id.value,
                outer_thread_id=getattr(envelope, "outer_thread_id", None),
                outer_run_id=getattr(envelope, "outer_run_id", None),
                event_sink=getattr(envelope, "live_event_sink", None),
            ),
        )

    @staticmethod
    async def _journal_envelope(
        *,
        lifecycle: BundleLifecycle,
        bundle: RunBundleRef,
        state: BundleLocalState,
        envelope: Any,
    ) -> Any:
        """Establish one Bundle-local Journal before a graph producer can run."""

        if not isinstance(envelope, TrustedRuntimeEnvelope):
            return envelope
        # BUG-048 item 2: bind the assembled per-phase envelope table (same
        # graph-context projection the capability builders use) so the run
        # summary can carry each executed phase's policy envelope.
        root = run_bundle_root(bundle)
        envelope = replace(
            envelope,
            policy_envelopes=policy_envelope_table(
                GraphContextView(
                    research_scope_id=bundle.bundle_id.value,
                    workspace_root=f"/mnt/user-data/{root}",
                    uploads_root="/mnt/user-data/uploads",
                    outputs_root=f"/mnt/user-data/outputs/{root}",
                )
            ),
        )
        recorder = RunObservationRecorder(
            store=RunObservationStore(
                bundle_root=lifecycle.private_root(bundle),
                bundle_id=bundle.bundle_id.value,
                policy_envelopes=getattr(envelope, "policy_envelopes", ()) or (),
            ),
            bundle_id=bundle.bundle_id.value,
            execution_profile=envelope.execution_profile,
        )
        await recorder.establish(
            generation=state.generation,
            phase=state.phase.value,
            durability=Durability.RESTART_DURABLE.value,
        )
        return replace(
            envelope,
            event_recorder_factory=lambda bundle_id: recorder if bundle_id == bundle.bundle_id.value else None,
        )


__all__ = ["BundleGraphExecutor"]
