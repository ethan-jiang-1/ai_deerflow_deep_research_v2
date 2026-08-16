#!/usr/bin/env python3
"""Manage isolated local DeerFlow configuration profiles.

@impl LCP-001
@impl LCP-002
@impl LCP-003
@impl LCP-004
@impl LCP-005
"""

from __future__ import annotations

import argparse
import fcntl
import importlib.util
import io
import json
import os
import re
import stat
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from io import BufferedWriter
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

_PROFILE_NAME = re.compile(r"^[a-z][a-z0-9-]{0,31}$")
_DOTENV_ASSIGNMENT = re.compile(r"^(?:export[ \t]+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
_EMPTY_EXTENSIONS = {"mcpServers": {}, "skills": {}}
PUBLIC_GATEWAY_HEALTH_URL = "http://127.0.0.1:8001/health"
_CAPTURE_MAX_BYTES = 10 * 1024 * 1024
_CAPTURE_MAX_INACTIVE_FILES = 8
_DOTENV_SELECTOR_KEYS = frozenset(
    {
        "DEER_FLOW_CONFIG_PATH",
        "DEER_FLOW_EXTENSIONS_CONFIG_PATH",
        "DEER_FLOW_HOME",
        "DEER_FLOW_PROJECT_ROOT",
        "DEER_FLOW_SKILLS_PATH",
    }
)


class ProfileError(RuntimeError):
    """A bounded, user-safe profile operation failure."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"[{code}] {detail}")
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class ProfilePaths:
    name: str
    project_root: Path
    agent_root: Path
    profiles_root: Path
    profile_dir: Path
    config_path: Path
    extensions_path: Path
    runtime_root: Path
    home_dir: Path
    sqlite_dir: Path


@dataclass(frozen=True)
class InitializeResult:
    name: str
    created: bool


@dataclass(frozen=True)
class ProfileValidation:
    name: str
    paths: ProfilePaths
    environment: dict[str, str]
    storage_kind: str


@dataclass(frozen=True)
class ObserverProfileReadiness:
    """Safe selected-profile fact admitted to the Gateway observer entrypoints."""

    name: str
    ready: bool = True


@dataclass(frozen=True)
class ProfileListEntry:
    name: str
    ready: bool
    code: str | None = None


Executor = Callable[[list[str], dict[str, str]], None]
EntryChecker = Callable[[Path, Mapping[str, str]], tuple[bool, str]]
HealthChecker = Callable[[str], bool]
StderrWriter = Callable[[bytes], None]
CaptureAnnouncer = Callable[[Path], None]


def _agent_root(value: Path) -> Path:
    try:
        root = value.resolve(strict=True)
    except OSError as exc:
        raise ProfileError("profile_project_invalid", "agent project is unavailable") from exc
    if not root.is_dir() or root.is_symlink():
        raise ProfileError("profile_project_invalid", "agent project is unavailable")
    return root


def _validate_name(name: str) -> str:
    if not _PROFILE_NAME.fullmatch(name):
        raise ProfileError("profile_name_invalid", "profile names use lowercase letters, digits, and hyphens")
    return name


def profile_paths(agent_root: Path, name: str) -> ProfilePaths:
    """Return project-owned paths after validating the profile label."""

    root = _agent_root(agent_root)
    project_root = root.parent
    safe_name = _validate_name(name)
    profiles_root = project_root / "profiles"
    profile_dir = profiles_root / safe_name
    return ProfilePaths(
        name=safe_name,
        project_root=project_root,
        agent_root=root,
        profiles_root=profiles_root,
        profile_dir=profile_dir,
        config_path=profile_dir / "config.yaml",
        extensions_path=profile_dir / "extensions_config.json",
        runtime_root=profiles_root,
        home_dir=profile_dir / ".deer-flow",
        sqlite_dir=profile_dir / ".deer-flow" / "data",
    )


def _contained(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _assert_existing_regular(path: Path, *, code: str) -> None:
    try:
        status = path.lstat()
    except FileNotFoundError as exc:
        raise ProfileError(code, "required profile file is missing") from exc
    except OSError as exc:
        raise ProfileError("profile_path_unsafe", "profile path cannot be inspected") from exc
    if stat.S_ISLNK(status.st_mode) or not stat.S_ISREG(status.st_mode):
        raise ProfileError("profile_path_unsafe", "profile paths must be regular files")


def _assert_existing_directory(path: Path) -> None:
    try:
        status = path.lstat()
    except FileNotFoundError:
        return
    except OSError as exc:
        raise ProfileError("profile_path_unsafe", "profile directory cannot be inspected") from exc
    if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
        raise ProfileError("profile_path_unsafe", "profile directories must not be symlinks")


def _assert_safe_parent_chain(path: Path, root: Path) -> None:
    if not _contained(path, root):
        raise ProfileError("profile_path_unsafe", "profile path escapes the project")
    current = root
    for part in path.relative_to(root).parts:
        current = current / part
        if current.exists() or current.is_symlink():
            _assert_existing_directory(current)


def _yaml() -> YAML:
    parser = YAML(typ="rt")
    parser.preserve_quotes = True
    parser.indent(mapping=2, sequence=4, offset=2)
    return parser


def _load_yaml(path: Path) -> tuple[dict[str, Any], YAML]:
    parser = _yaml()
    try:
        loaded = parser.load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ProfileError("profile_config_invalid", "profile config is not valid YAML") from exc
    if not isinstance(loaded, dict):
        raise ProfileError("profile_config_invalid", "profile config root must be a mapping")
    return loaded, parser


def _dump_yaml(data: dict[str, Any], parser: YAML) -> bytes:
    stream = io.StringIO()
    parser.dump(data, stream)
    return stream.getvalue().encode("utf-8")


def _write_new_file(path: Path, data: bytes) -> None:
    try:
        with path.open("xb") as handle:
            handle.write(data)
    except FileExistsError as exc:
        raise ProfileError("profile_pair_partial", "profile configuration pair is incomplete") from exc
    except OSError as exc:
        raise ProfileError("profile_write_failed", "profile files could not be created") from exc


def _root_config_path(root: Path) -> Path:
    path = root / "config.yaml"
    try:
        _assert_existing_regular(path, code="profile_root_config_missing")
    except ProfileError as exc:
        if exc.code == "profile_root_config_missing":
            raise ProfileError(
                "profile_root_config_missing", "run make setup or make config before profile initialization"
            ) from exc
        raise
    return path


def _root_extensions(path: Path) -> bytes:
    if not path.exists() and not path.is_symlink():
        return (json.dumps(_EMPTY_EXTENSIONS, indent=2) + "\n").encode("utf-8")
    _assert_existing_regular(path, code="profile_extensions_invalid")
    try:
        raw = path.read_bytes()
        loaded = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProfileError("profile_extensions_invalid", "extensions configuration is not valid JSON") from exc
    if not isinstance(loaded, dict):
        raise ProfileError("profile_extensions_invalid", "extensions configuration root must be an object")
    return raw


def initialize_profile(project_root: Path, name: str) -> InitializeResult:
    """Create a complete profile pair, without creating its runtime state."""

    paths = profile_paths(project_root, name)
    _assert_safe_parent_chain(paths.profiles_root, paths.project_root)
    if paths.profile_dir.exists() or paths.profile_dir.is_symlink():
        _assert_existing_directory(paths.profile_dir)
        config_exists = paths.config_path.exists() or paths.config_path.is_symlink()
        extensions_exists = paths.extensions_path.exists() or paths.extensions_path.is_symlink()
        if config_exists and extensions_exists:
            _assert_existing_regular(paths.config_path, code="profile_pair_missing")
            _assert_existing_regular(paths.extensions_path, code="profile_pair_missing")
            return InitializeResult(name=paths.name, created=False)
        raise ProfileError("profile_pair_partial", "profile configuration pair is incomplete")

    root_config = _root_config_path(paths.project_root)
    root_data, parser = _load_yaml(root_config)
    root_data.pop("checkpointer", None)
    root_data["database"] = {"backend": "sqlite", "sqlite_dir": str(paths.sqlite_dir)}
    extensions = _root_extensions(paths.project_root / "extensions_config.json")

    try:
        paths.profiles_root.mkdir(mode=0o700, exist_ok=True)
        _assert_existing_directory(paths.profiles_root)
        paths.profile_dir.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise ProfileError("profile_pair_partial", "profile configuration pair is incomplete") from exc
    except OSError as exc:
        raise ProfileError("profile_write_failed", "profile directory could not be created") from exc

    try:
        _write_new_file(paths.config_path, _dump_yaml(root_data, parser))
        _write_new_file(paths.extensions_path, extensions)
    except Exception:
        for candidate in (paths.config_path, paths.extensions_path):
            try:
                candidate.unlink(missing_ok=True)
            except OSError:
                pass
        try:
            paths.profile_dir.rmdir()
        except OSError:
            pass
        raise
    return InitializeResult(name=paths.name, created=True)


def _profile_pair(paths: ProfilePaths) -> None:
    if not paths.profile_dir.exists() and not paths.profile_dir.is_symlink():
        raise ProfileError("profile_unknown", "profile has not been initialized")
    _assert_existing_directory(paths.profiles_root)
    _assert_existing_directory(paths.profile_dir)
    config_exists = paths.config_path.exists() or paths.config_path.is_symlink()
    extensions_exists = paths.extensions_path.exists() or paths.extensions_path.is_symlink()
    if not config_exists and not extensions_exists:
        raise ProfileError("profile_pair_missing", "profile configuration pair is missing")
    if not config_exists or not extensions_exists:
        raise ProfileError("profile_pair_partial", "profile configuration pair is incomplete")
    _assert_existing_regular(paths.config_path, code="profile_pair_missing")
    _assert_existing_regular(paths.extensions_path, code="profile_pair_missing")


def validate_profile(project_root: Path, name: str) -> ProfileValidation:
    """Validate profile isolation before any service or runtime-state operation."""

    paths = profile_paths(project_root, name)
    _profile_pair(paths)
    _assert_safe_parent_chain(paths.home_dir, paths.project_root)
    _assert_safe_parent_chain(paths.sqlite_dir, paths.project_root)
    if paths.home_dir == paths.sqlite_dir or not _contained(paths.home_dir, paths.profile_dir):
        raise ProfileError("profile_sqlite_isolation", "profile runtime state is not isolated")
    if not _contained(paths.sqlite_dir, paths.profile_dir):
        raise ProfileError("profile_sqlite_isolation", "profile SQLite state is not isolated")

    data, _ = _load_yaml(paths.config_path)
    if data.get("checkpointer") is not None:
        raise ProfileError("profile_legacy_checkpointer", "remove the legacy checkpointer section from this profile")
    database = data.get("database")
    if not isinstance(database, dict):
        raise ProfileError("profile_database_backend", "local profiles require SQLite or memory database state")
    backend = database.get("backend")
    if backend == "sqlite":
        raw_sqlite_dir = database.get("sqlite_dir")
        if not isinstance(raw_sqlite_dir, str) or not Path(raw_sqlite_dir).is_absolute():
            raise ProfileError("profile_sqlite_isolation", "profile SQLite state must use its isolated location")
        try:
            actual_sqlite_dir = Path(raw_sqlite_dir).resolve(strict=False)
        except OSError as exc:
            raise ProfileError(
                "profile_sqlite_isolation", "profile SQLite state must use its isolated location"
            ) from exc
        if actual_sqlite_dir != paths.sqlite_dir.resolve(strict=False):
            raise ProfileError("profile_sqlite_isolation", "profile SQLite state must use its isolated location")
        storage_kind = "sqlite"
    elif backend == "memory":
        storage_kind = "memory"
    else:
        raise ProfileError("profile_database_backend", "local profiles require SQLite or memory database state")

    environment = {
        "DEER_FLOW_PROJECT_ROOT": str(paths.project_root),
        "DEER_FLOW_CONFIG_PATH": str(paths.config_path),
        "DEER_FLOW_EXTENSIONS_CONFIG_PATH": str(paths.extensions_path),
        "DEER_FLOW_HOME": str(paths.home_dir),
    }
    return ProfileValidation(name=paths.name, paths=paths, environment=environment, storage_kind=storage_kind)


def _configuration_module() -> Any:
    module_name = "deep_research_profile_configure"
    module = sys.modules.get(module_name)
    if module is not None:
        return module
    source = Path(__file__).with_name("configure.py")
    spec = importlib.util.spec_from_file_location(module_name, source)
    if spec is None or spec.loader is None:
        raise ProfileError("profile_observer_entry", "run the selected profile configuration check")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _configuration_entry_check(project_root: Path, environment: Mapping[str, str]) -> tuple[bool, str]:
    """Assess only the selected profile's public entry through configure check mode."""

    try:
        result = _configuration_module().execute_configuration(project_root, dict(environment), mode="check")
    except Exception as exc:
        raise ProfileError("profile_observer_entry", "run the selected profile configuration check") from exc
    return bool(getattr(result, "runtime_config_ready", False)), str(getattr(result, "entry_status", ""))


def _gateway_health_reachable(url: str) -> bool:
    try:
        request = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(request, timeout=0.5) as response:
            return 200 <= response.status < 300
    except (OSError, urllib.error.URLError):
        return False


def _observer_logging_ready(data: Mapping[str, Any]) -> bool:
    logging = data.get("logging")
    if not isinstance(logging, Mapping):
        return False
    enhance = logging.get("enhance")
    return isinstance(enhance, Mapping) and enhance.get("enabled") is True and enhance.get("format") == "json"


def validate_observer_profile(
    project_root: Path,
    name: str,
    *,
    entry_checker: EntryChecker | None = None,
    health_checker: HealthChecker | None = None,
) -> ObserverProfileReadiness:
    """Admit a selected profile for the fixed local public Gateway observer only."""

    profile = validate_profile(project_root, name)
    config, _ = _load_yaml(profile.paths.config_path)
    if not _observer_logging_ready(config):
        raise ProfileError(
            "profile_observer_logging",
            "enable JSON enhanced logging in the selected profile and restart the Gateway",
        )
    if profile.storage_kind != "sqlite":
        raise ProfileError(
            "profile_observer_durable_history",
            "select isolated local SQLite history before starting the Gateway observer",
        )
    try:
        runtime_config_ready, entry_status = (entry_checker or _configuration_entry_check)(
            profile.paths.project_root,
            dict(profile.environment),
        )
    except ProfileError:
        raise
    except Exception as exc:
        raise ProfileError("profile_observer_entry", "run the selected profile configuration check") from exc
    if not runtime_config_ready or entry_status != "ready":
        raise ProfileError("profile_observer_entry", "run the selected profile configuration check")
    if not (health_checker or _gateway_health_reachable)(PUBLIC_GATEWAY_HEALTH_URL):
        raise ProfileError("profile_observer_health", "start the selected profile Gateway and retry the observer")
    return ObserverProfileReadiness(name=profile.name)


def list_profiles(agent_root: Path) -> tuple[ProfileListEntry, ...]:
    """List known profile labels without exposing profile locations."""

    root = _agent_root(agent_root)
    profiles_root = root.parent / "profiles"
    if not profiles_root.exists() and not profiles_root.is_symlink():
        return ()
    _assert_existing_directory(profiles_root)
    entries: list[ProfileListEntry] = []
    for candidate in sorted(profiles_root.iterdir(), key=lambda path: path.name):
        if candidate.name in {"README.md", ".gitignore"} or not candidate.is_dir() or candidate.is_symlink():
            continue
        if not _PROFILE_NAME.fullmatch(candidate.name):
            continue
        try:
            validate_profile(root, candidate.name)
        except ProfileError as exc:
            entries.append(ProfileListEntry(candidate.name, False, exc.code))
        else:
            entries.append(ProfileListEntry(candidate.name, True))
    return tuple(entries)


def format_profile_check(result: ProfileValidation) -> str:
    storage = "Isolated local SQLite state" if result.storage_kind == "sqlite" else "Ephemeral memory database state"
    return (
        f"Profile '{result.name}' is ready. {storage} is selected. "
        "Restart required after startup-only configuration changes."
    )


def format_profile_list(entries: Sequence[ProfileListEntry]) -> str:
    if not entries:
        return "No local profiles are initialized. Run make profile-init PROFILE=demo from deep_research_harness/."
    lines = ["Local profiles:"]
    for entry in entries:
        state = "ready" if entry.ready else "needs attention"
        lines.append(f"- {entry.name}: {state}")
    return "\n".join(lines)


def _capture_log_root(agent_root: Path) -> Path:
    root = _agent_root(agent_root)
    run_root = root / ".deep-research-demo-runs"
    log_root = run_root / "logs"
    for directory in (run_root, log_root):
        directory.mkdir(mode=0o700, exist_ok=True)
        status = directory.lstat()
        if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
            raise OSError("process log directories must not be symlinks")
        os.chmod(directory, 0o700)
    return log_root


def _open_capture_file(log_root: Path, name: str) -> tuple[Path, BufferedWriter]:
    path = log_root / name
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        os.fchmod(descriptor, 0o600)
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return path, os.fdopen(descriptor, "ab", buffering=0)
    except Exception:
        os.close(descriptor)
        raise


def _capture_name() -> str:
    return f"gateway-{os.getpid()}-{time.time_ns()}-{uuid.uuid4().hex}.stderr.log"


def _is_capture_file(path: Path) -> bool:
    name = path.name
    return name.endswith(".stderr.log") or ".stderr.log." in name


def _retain_inactive_captures(log_root: Path, *, active_path: Path) -> None:
    """Keep a bounded inactive capture set without touching live process files."""

    active = active_path.resolve(strict=False)
    candidates: list[Path] = []
    for candidate in log_root.iterdir():
        if not _is_capture_file(candidate):
            continue
        status = candidate.lstat()
        if stat.S_ISLNK(status.st_mode) or not stat.S_ISREG(status.st_mode):
            continue
        candidates.append(candidate)
    candidates.sort(key=lambda candidate: candidate.stat().st_mtime_ns, reverse=True)

    retained = 0
    for candidate in candidates:
        if candidate.resolve(strict=False) == active or candidate.name.startswith(f"{active.name}."):
            continue
        if retained < _CAPTURE_MAX_INACTIVE_FILES:
            retained += 1
            continue
        descriptor = os.open(candidate, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                retained += 1
                continue
            candidate.unlink()
        finally:
            os.close(descriptor)


class _StderrCapture:
    """One locked process log whose rotation never changes child execution."""

    def __init__(self, log_root: Path, path: Path, handle: BufferedWriter) -> None:
        self._log_root = log_root
        self.path = path
        self._handle = handle
        self._closed = False

    def write(self, chunk: bytes) -> None:
        if self._closed:
            raise OSError("stderr capture is closed")
        self._handle.write(chunk)
        if self.path.stat().st_size > _CAPTURE_MAX_BYTES:
            self._rotate()

    def _rotate(self) -> None:
        self._handle.close()
        rotated = self.path.with_name(f"{self.path.name}.{time.time_ns()}-{uuid.uuid4().hex}")
        os.replace(self.path, rotated)
        path, handle = _open_capture_file(self._log_root, self.path.name)
        self.path = path
        self._handle = handle
        _retain_inactive_captures(self._log_root, active_path=self.path)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._handle.close()


def _open_stderr_capture(agent_root: Path) -> _StderrCapture:
    log_root = _capture_log_root(agent_root)
    for _ in range(8):
        try:
            path, handle = _open_capture_file(log_root, _capture_name())
        except FileExistsError:
            continue
        capture = _StderrCapture(log_root, path, handle)
        try:
            _retain_inactive_captures(log_root, active_path=path)
        except Exception:
            capture.close()
            raise
        return capture
    raise OSError("could not allocate a unique stderr capture")


def _write_inherited_stderr(chunk: bytes) -> None:
    stream = getattr(sys.stderr, "buffer", None)
    if stream is not None:
        stream.write(chunk)
        stream.flush()
        return
    sys.stderr.write(chunk.decode("utf-8", errors="replace"))
    sys.stderr.flush()


def _announce_capture(path: Path) -> None:
    print(f"Gateway stderr capture: {path}", file=sys.stderr, flush=True)


def _normal_exit_code(returncode: int) -> int:
    return returncode if returncode >= 0 else 128 + abs(returncode)


def _run_profile_child(
    argv: list[str],
    env: dict[str, str],
    agent_root: Path,
    *,
    popen_factory: Callable[..., Any] = subprocess.Popen,
    stderr_writer: StderrWriter = _write_inherited_stderr,
    announce: CaptureAnnouncer = _announce_capture,
) -> int:
    """Launch Gateway unchanged while making an advisory stderr capture when possible."""

    capture: _StderrCapture | None = None
    try:
        capture = _open_stderr_capture(agent_root)
        announce(capture.path)
    except Exception:
        if capture is not None:
            try:
                capture.close()
            except OSError:
                pass
        capture = None

    child = popen_factory(argv, env=env, stderr=subprocess.PIPE if capture is not None else None)
    try:
        if capture is not None and child.stderr is not None:
            while chunk := child.stderr.read(64 * 1024):
                try:
                    stderr_writer(chunk)
                except Exception:
                    pass
                try:
                    capture.write(chunk)
                except Exception:
                    try:
                        capture.close()
                    except OSError:
                        pass
                    capture = None
    finally:
        if capture is not None:
            try:
                capture.close()
            except OSError:
                pass
    return _normal_exit_code(child.wait())


def _validate_root_dotenv(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    _assert_existing_regular(path, code="profile_dotenv_invalid")
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ProfileError("profile_dotenv_invalid", "root .env must use direct literal dotenv values") from exc
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = _DOTENV_ASSIGNMENT.fullmatch(stripped)
        if match is None or not _is_literal_dotenv_value(match.group(2)):
            raise ProfileError("profile_dotenv_invalid", "root .env must use direct literal dotenv values")
        if match.group(1) in _DOTENV_SELECTOR_KEYS:
            raise ProfileError(
                "profile_dotenv_conflict",
                f"remove {match.group(1)} from root .env; keep API keys and other secrets there",
            )


def _is_literal_dotenv_value(value: str) -> bool:
    if value.startswith("'"):
        return len(value) >= 2 and value.endswith("'") and "'" not in value[1:-1]
    if value.startswith('"') or any(character in value for character in "$`;&|<>()\\ \t"):
        return False
    return True


def launch_profile(
    project_root: Path,
    name: str,
    *,
    executor: Executor | None = None,
    base_env: Mapping[str, str] | None = None,
) -> int:
    """Launch the unchanged local-dev server after profile validation succeeds."""

    result = validate_profile(project_root, name)
    _validate_root_dotenv(result.paths.project_root / ".env")
    environment = dict(os.environ if base_env is None else base_env)
    environment.update(result.environment)
    environment.pop("DEER_FLOW_SKILLS_PATH", None)
    environment.pop("BASH_ENV", None)
    environment.pop("DEERFLOW_PROFILE_ROOT_ENV", None)
    argv = [
        str(result.paths.project_root / "deerflow" / "scripts" / "serve.sh"),
        "--dev",
        "--skip-install",
    ]
    if executor is not None:
        executor(argv, environment)
        return 0
    return _run_profile_child(argv, environment, result.paths.agent_root)


def _run_cli(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage isolated local DeerFlow profiles.")
    parser.add_argument("command", choices=("list", "init", "check", "launch"))
    parser.add_argument("profile", nargs="?")
    parser.add_argument("launcher_args", nargs=argparse.REMAINDER)
    parser.add_argument("--agent-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            if args.profile is not None:
                raise ProfileError("profile_command_invalid", "list does not take a profile name")
            print(format_profile_list(list_profiles(args.agent_root)))
        elif args.command == "init":
            if args.profile is None:
                raise ProfileError("profile_name_invalid", "provide a profile name")
            result = initialize_profile(args.agent_root, args.profile)
            state = "created" if result.created else "ready"
            print(f"Profile '{result.name}' is {state}. Next: cd agent && make profile-dev PROFILE={result.name}")
        elif args.command == "check":
            if args.profile is None:
                raise ProfileError("profile_name_invalid", "provide a profile name")
            print(format_profile_check(validate_profile(args.agent_root, args.profile)))
        else:
            if args.profile is None:
                raise ProfileError("profile_name_invalid", "provide a profile name")
            if args.launcher_args:
                raise ProfileError("profile_command_invalid", "profile launch accepts no launcher arguments")
            return launch_profile(args.agent_root, args.profile)
    except ProfileError as exc:
        print(f"{exc.code}: {exc.detail}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_run_cli())
