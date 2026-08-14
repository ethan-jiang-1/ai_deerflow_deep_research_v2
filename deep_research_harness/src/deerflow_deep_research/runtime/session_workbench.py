"""Presentation-only local inspection over a selected Run Bundle.

The historical workbench name remains for local tooling, but it has no session,
checkpoint, or retained-observation recovery path. Every control and artifact read
reauthorizes the opaque Bundle id through the trusted-scope lifecycle boundary.

@impl RWB-001
@impl RWB-002
@impl RWB-003
@impl RWB-005
@impl RWB-006
@impl RWB-008
@impl RSV-001
@impl RSV-002
@impl RSV-003
@impl RSV-004
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import os
import stat
from pathlib import Path

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef
from deerflow_deep_research.domain.lifecycle import (
    AcceptedHumanResponse,
    BundleAvailability,
    BundleControlResult,
    Durability,
    LegalNextAction,
    LifecycleAction,
    LifecycleStatus,
    ResponseKind,
    ResultCode,
)
from deerflow_deep_research.domain.run_observation import ObservationInspectability
from deerflow_deep_research.domain.session_workbench import (
    MAX_WORKBENCH_ARTIFACT_BYTES,
    ArtifactCatalogKey,
    WorkbenchArtifactMetadata,
    WorkbenchArtifactView,
    WorkbenchAvailability,
    WorkbenchCatalogView,
    WorkbenchDiagnosisView,
    WorkbenchDiscoveryView,
    WorkbenchSessionView,
    WorkbenchTimelineView,
    artifact_catalog_media_type,
    artifact_catalog_path,
)
from deerflow_deep_research.runtime.bundle_lifecycle import (
    BundleAlreadyActive,
    BundleLifecycle,
    BundleLifecycleError,
    CurrentBundleHandle,
)
from deerflow_deep_research.runtime.run_observation import RunObservationStore


class BundleWorkbench:
    """Inspect and control only Bundles validated by one lifecycle boundary."""

    def __init__(
        self,
        *,
        lifecycle: BundleLifecycle | None = None,
        scope: tuple[str, str] | None = None,
        current_bundle_handle: CurrentBundleHandle | None = None,
    ) -> None:
        self._lifecycle = lifecycle
        self._scope = scope
        self._current_bundle_handle = current_bundle_handle

    async def discover(self) -> tuple[BundleControlResult, ...]:
        """Discover at most one active Bundle through trusted scoped State."""

        if self._lifecycle is None or self._scope is None:
            return ()
        try:
            bundle = await self._lifecycle.resolve_active(
                scope=self._scope,
                handle=self._current_bundle_handle,
            )
            if bundle is None:
                return ()
            state = await self._lifecycle.read_state(bundle)
            return (self._lifecycle.result_for_state(action=LifecycleAction.STATUS, bundle=bundle, state=state),)
        except (BundleLifecycleError, TypeError, ValueError):
            return ()

    async def open(self, *, bundle_id: str) -> BundleControlResult:
        """Read a selected Bundle without graph, provider, or content work."""

        return await self.result(bundle_id=bundle_id)

    async def status(self, *, bundle_id: str) -> BundleControlResult:
        """Return the shared lifecycle result without a workbench-specific overlay."""

        return await self.result(bundle_id=bundle_id)

    async def result(self, *, bundle_id: str) -> BundleControlResult:
        """Reauthorize an explicit Bundle without using a retained observation."""

        if self._lifecycle is None or self._scope is None:
            return _unavailable_result()
        try:
            return await self._lifecycle.status(scope=self._scope, bundle_id=BundleId(bundle_id))
        except (BundleLifecycleError, TypeError, ValueError):
            return _unavailable_result()

    async def resume(
        self,
        *,
        bundle_id: str,
        expected_request_id: str,
        answer: str,
        action_id: str | None = None,
        option_id: str | None = None,
    ) -> BundleControlResult:
        bundle = await self._selected_bundle(bundle_id)
        if bundle is None or self._lifecycle is None or self._scope is None:
            return _unavailable_result(LifecycleAction.RESUME)
        try:
            state = await self._lifecycle.read_state(bundle)
            if state.pending_request_id != expected_request_id:
                return self._lifecycle.result_for_state(
                    action=LifecycleAction.RESUME,
                    bundle=bundle,
                    state=state,
                    code=ResultCode.RESPONSE_MISMATCH,
                )
            response_kind = (
                ResponseKind.ACTION
                if action_id is not None
                else ResponseKind.OPTION
                if option_id is not None
                else ResponseKind.TEXT
            )
            value = action_id or option_id or answer
            response = AcceptedHumanResponse(
                request_id=expected_request_id,
                message_id=self._message_id(bundle.bundle_id.value, expected_request_id, value),
                value=value,
                response_kind=response_kind,
                action_id=action_id,
                option_id=option_id,
            )
            updated = await self._lifecycle.resume(scope=self._scope, response=response, bundle_id=bundle.bundle_id)
            if updated.is_active and updated.pending_request_id is None:
                updated = await self._lifecycle.end(bundle=bundle, terminal_status=LifecycleStatus.COMPLETED)
            return self._lifecycle.result_for_state(action=LifecycleAction.RESUME, bundle=bundle, state=updated)
        except BundleLifecycleError as exc:
            if exc.code == "response_mismatch":
                try:
                    state = await self._lifecycle.read_state(bundle)
                    return self._lifecycle.result_for_state(
                        action=LifecycleAction.RESUME,
                        bundle=bundle,
                        state=state,
                        code=ResultCode.RESPONSE_MISMATCH,
                    )
                except BundleLifecycleError:
                    pass
            return _unavailable_result(LifecycleAction.RESUME)
        except (TypeError, ValueError):
            return _unavailable_result(LifecycleAction.RESUME)

    async def select_control(
        self,
        *,
        bundle_id: str,
        expected_request_id: str,
        control_id: str,
    ) -> BundleControlResult:
        if control_id != "accept_current_proposal":
            return _unavailable_result(LifecycleAction.RESUME)
        return await self.resume(
            bundle_id=bundle_id,
            expected_request_id=expected_request_id,
            answer="accept_suggestion",
            action_id="accept_suggestion",
        )

    async def cancel(self, *, bundle_id: str) -> BundleControlResult:
        bundle = await self._selected_bundle(bundle_id)
        if bundle is None or self._lifecycle is None or self._scope is None:
            return _unavailable_result(LifecycleAction.CANCEL)
        try:
            state = await self._lifecycle.cancel(scope=self._scope, bundle_id=bundle.bundle_id)
            return self._lifecycle.result_for_state(action=LifecycleAction.CANCEL, bundle=bundle, state=state)
        except BundleLifecycleError:
            return _unavailable_result(LifecycleAction.CANCEL)

    async def refine(self, *, bundle_id: str, text: str, operation_key: str) -> BundleControlResult:
        bundle = await self._selected_bundle(bundle_id)
        if bundle is None or self._lifecycle is None or self._scope is None:
            return _unavailable_result(LifecycleAction.REFINE)
        try:
            admission = await self._lifecycle.admit_refinement(
                scope=self._scope,
                bundle_id=bundle.bundle_id,
                text=text,
                operation_key=operation_key,
            )
            return self._lifecycle.result_for_state(
                action=LifecycleAction.REFINE,
                bundle=bundle,
                state=admission.state,
            )
        except BundleAlreadyActive as exc:
            try:
                state = await self._lifecycle.read_state(exc.bundle)
            except BundleLifecycleError:
                return _unavailable_result(LifecycleAction.REFINE)
            return self._lifecycle.result_for_state(
                action=LifecycleAction.REFINE,
                bundle=exc.bundle,
                state=state,
                code=ResultCode.ACTIVE_BUNDLE_EXISTS,
            )
        except (BundleLifecycleError, TypeError, ValueError):
            return _unavailable_result(LifecycleAction.REFINE)

    async def catalog(self, *, bundle_id: str) -> WorkbenchCatalogView:
        bundle = await self._available_bundle(bundle_id)
        if bundle is None:
            return WorkbenchCatalogView(availability=WorkbenchAvailability.UNAVAILABLE)
        try:
            entries = await asyncio.to_thread(self._catalog_sync, bundle)
            return WorkbenchCatalogView(availability=WorkbenchAvailability.AVAILABLE, entries=entries)
        except (OSError, ValueError):
            return WorkbenchCatalogView(availability=WorkbenchAvailability.UNAVAILABLE)

    async def view_artifact(self, *, bundle_id: str, key: ArtifactCatalogKey | str) -> WorkbenchArtifactView:
        try:
            key = key if isinstance(key, ArtifactCatalogKey) else ArtifactCatalogKey(key)
        except (TypeError, ValueError):
            # A fixed key is required before lifecycle or filesystem work starts.
            return WorkbenchArtifactView(availability=WorkbenchAvailability.UNAVAILABLE)
        bundle = await self._available_bundle(bundle_id)
        if bundle is None:
            return WorkbenchArtifactView(availability=WorkbenchAvailability.UNAVAILABLE)
        try:
            metadata = await asyncio.to_thread(self._metadata_sync, bundle, key)
        except (OSError, ValueError):
            return WorkbenchArtifactView(availability=WorkbenchAvailability.UNAVAILABLE)
        if metadata is None:
            return WorkbenchArtifactView(availability=WorkbenchAvailability.UNAVAILABLE)
        return WorkbenchArtifactView(availability=WorkbenchAvailability.AVAILABLE, metadata=metadata)

    async def timeline(self, *, bundle_id: str) -> WorkbenchTimelineView:
        """Do not infer a timeline from arbitrary Bundle files."""

        if await self._available_bundle(bundle_id) is None:
            return WorkbenchTimelineView(availability=WorkbenchAvailability.UNAVAILABLE)
        return WorkbenchTimelineView(availability=WorkbenchAvailability.UNAVAILABLE)

    async def diagnosis(self, *, bundle_id: str) -> WorkbenchDiagnosisView:
        """Read only the selected available Bundle's contained Journal."""

        bundle = await self._available_bundle(bundle_id)
        if bundle is None or self._lifecycle is None:
            return WorkbenchDiagnosisView(availability=WorkbenchAvailability.UNAVAILABLE)
        try:
            inspection = await RunObservationStore(
                bundle_root=self._lifecycle.private_root(bundle),
                bundle_id=bundle.bundle_id.value,
            ).inspect(bundle_id=bundle.bundle_id.value)
        except (OSError, RuntimeError, TypeError, ValueError):
            return WorkbenchDiagnosisView(availability=WorkbenchAvailability.UNAVAILABLE)
        if inspection.inspectability is not ObservationInspectability.AVAILABLE:
            return WorkbenchDiagnosisView(availability=WorkbenchAvailability.UNAVAILABLE)
        return WorkbenchDiagnosisView(
            availability=WorkbenchAvailability.AVAILABLE,
            summary=inspection.summary,
            events=inspection.events[-8:],
            incomplete_reasons=inspection.incomplete_reasons,
        )

    async def _selected_bundle(self, bundle_id: str) -> RunBundleRef | None:
        if self._lifecycle is None or self._scope is None:
            return None
        try:
            return await self._lifecycle.resolve(scope=self._scope, bundle_id=BundleId(bundle_id))
        except (BundleLifecycleError, TypeError, ValueError):
            return None

    async def _available_bundle(self, bundle_id: str) -> RunBundleRef | None:
        result = await self.result(bundle_id=bundle_id)
        if result.availability is not BundleAvailability.AVAILABLE or result.bundle_id is None:
            return None
        bundle = await self._selected_bundle(result.bundle_id)
        if bundle is None or self._lifecycle is None:
            return None
        try:
            # Recheck immediately before contained I/O so a lost Bundle is not read
            # through an earlier status projection.
            await self._lifecycle.read_state(bundle)
        except BundleLifecycleError:
            return None
        return bundle

    def _catalog_sync(self, bundle: RunBundleRef) -> tuple[WorkbenchArtifactMetadata, ...]:
        entries: list[WorkbenchArtifactMetadata] = []
        for key in ArtifactCatalogKey:
            metadata = self._metadata_sync(bundle, key)
            if metadata is not None:
                entries.append(metadata)
        return tuple(entries)

    def _metadata_sync(self, bundle: RunBundleRef, key: ArtifactCatalogKey) -> WorkbenchArtifactMetadata | None:
        if self._lifecycle is None:
            return None
        root = self._lifecycle.private_root(bundle)
        file_stat = self._contained_regular_file(root, artifact_catalog_path(key))
        if file_stat is None:
            return None
        if file_stat.st_size > MAX_WORKBENCH_ARTIFACT_BYTES:
            raise ValueError("artifact_too_large")
        return WorkbenchArtifactMetadata(
            key=key,
            relative_path=artifact_catalog_path(key),
            media_type=artifact_catalog_media_type(key),
            byte_size=file_stat.st_size,
        )

    @staticmethod
    def _contained_regular_file(root: Path, relative_path: str) -> os.stat_result | None:
        """Read fixed metadata with no symlink, traversal, or permission widening."""

        try:
            root_stat = root.lstat()
        except OSError:
            return None
        if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode) or root_stat.st_mode & 0o077:
            return None
        current = root
        components = relative_path.split("/")
        for component in components[:-1]:
            current = current / component
            try:
                current_stat = current.lstat()
            except FileNotFoundError:
                return None
            if (
                stat.S_ISLNK(current_stat.st_mode)
                or not stat.S_ISDIR(current_stat.st_mode)
                or current_stat.st_mode & 0o077
            ):
                raise ValueError("artifact_parent_unsafe")
        path = current / components[-1]
        try:
            expected = path.lstat()
        except FileNotFoundError:
            return None
        if stat.S_ISLNK(expected.st_mode) or not stat.S_ISREG(expected.st_mode) or expected.st_mode & 0o077:
            raise ValueError("artifact_unsafe")
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        except FileNotFoundError:
            return None
        try:
            opened = os.fstat(fd)
        finally:
            os.close(fd)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_mode & 0o077
            or opened.st_dev != expected.st_dev
            or opened.st_ino != expected.st_ino
        ):
            raise ValueError("artifact_replaced")
        return opened

    @staticmethod
    def _message_id(bundle_id: str, request_id: str, value: str) -> str:
        payload = "|".join((bundle_id, request_id, value)).encode("utf-8")
        return "local_" + base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).decode().rstrip("=")


class LocalBundleWorkbench:
    """Compose direct Bundle controls with inert contained inspection metadata."""

    def __init__(self, *, bundle_workbench: BundleWorkbench | None = None) -> None:
        self._bundle_workbench = bundle_workbench or BundleWorkbench()

    async def discover(self) -> WorkbenchDiscoveryView:
        return WorkbenchDiscoveryView(entries=await self._bundle_workbench.discover())

    async def open(self, bundle_id: str) -> WorkbenchSessionView:
        return await self._session(bundle_id)

    async def status(self, bundle_id: str) -> WorkbenchSessionView:
        return await self._session(bundle_id)

    async def timeline(self, bundle_id: str) -> WorkbenchTimelineView:
        return await self._bundle_workbench.timeline(bundle_id=bundle_id)

    async def diagnosis(self, bundle_id: str) -> WorkbenchDiagnosisView:
        return await self._bundle_workbench.diagnosis(bundle_id=bundle_id)

    async def catalog(self, bundle_id: str) -> WorkbenchCatalogView:
        return await self._bundle_workbench.catalog(bundle_id=bundle_id)

    async def view_artifact(self, bundle_id: str, key: ArtifactCatalogKey | str) -> WorkbenchArtifactView:
        return await self._bundle_workbench.view_artifact(bundle_id=bundle_id, key=key)

    async def resume(
        self,
        bundle_id: str,
        *,
        expected_request_id: str,
        answer: str,
        action_id: str | None = None,
    ) -> BundleControlResult:
        return await self._bundle_workbench.resume(
            bundle_id=bundle_id,
            expected_request_id=expected_request_id,
            answer=answer,
            action_id=action_id,
        )

    async def select_control(
        self,
        bundle_id: str,
        *,
        expected_request_id: str,
        control_id: str,
    ) -> BundleControlResult:
        return await self._bundle_workbench.select_control(
            bundle_id=bundle_id,
            expected_request_id=expected_request_id,
            control_id=control_id,
        )

    async def cancel(self, bundle_id: str) -> BundleControlResult:
        return await self._bundle_workbench.cancel(bundle_id=bundle_id)

    async def refine(self, bundle_id: str, *, text: str, operation_key: str) -> BundleControlResult:
        return await self._bundle_workbench.refine(
            bundle_id=bundle_id,
            text=text,
            operation_key=operation_key,
        )

    async def _session(self, bundle_id: str) -> WorkbenchSessionView:
        result = await self._bundle_workbench.open(bundle_id=bundle_id)
        if result.availability is not BundleAvailability.AVAILABLE or result.bundle_id is None:
            return WorkbenchSessionView(
                operation=result,
                timeline=WorkbenchTimelineView(availability=WorkbenchAvailability.UNAVAILABLE),
                catalog=WorkbenchCatalogView(availability=WorkbenchAvailability.UNAVAILABLE),
                diagnosis=WorkbenchDiagnosisView(availability=WorkbenchAvailability.UNAVAILABLE),
            )
        return WorkbenchSessionView(
            operation=result,
            timeline=await self._bundle_workbench.timeline(bundle_id=result.bundle_id),
            catalog=await self._bundle_workbench.catalog(bundle_id=result.bundle_id),
            diagnosis=await self._bundle_workbench.diagnosis(bundle_id=result.bundle_id),
        )


def _unavailable_result(action: LifecycleAction = LifecycleAction.STATUS) -> BundleControlResult:
    return BundleControlResult(
        action=action,
        code=ResultCode.UNAVAILABLE,
        availability=BundleAvailability.UNAVAILABLE,
        durability=Durability.UNAVAILABLE,
        legal_next_action=LegalNextAction.START,
    )


__all__ = ["BundleWorkbench", "LocalBundleWorkbench"]
