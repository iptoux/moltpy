import json
import os
import time
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .. import ConfigObject, EnvObject, DataObject, MoltpyLogger, LogLevel
from ..heartbeat import MoltpyHeartbeat
from ..tools import MoltpyToolRegistry

class MoltpyRuntime:
    _instance = None
    _initialized = False
    _loader = None
    _logger = None
    _you = None

    config: ConfigObject
    you: DataObject
    ui: "UIState"
    base_path: Path
    data: DataObject
    tools: MoltpyToolRegistry

    def __init__(self) -> None:
        self.ui = UIState()
        self._heartbeat = MoltpyHeartbeat(self)
        self._file_sink = None
        self._log_enabled = False
        self._log_path: Path | None = None
        self._log_level_name = "INFO"
        self.tools = MoltpyToolRegistry()

    class Loader:

        def configObject(self, path: Path | None = None) -> ConfigObject:
            data: dict[str, Any] = {}

            # Example: ENV
            data["env"] = os.getenv("APP_ENV", "dev")

            # Default config path (e.g. ~/.moltpy/config.json)
            if path is None:
                path = Path.home() / ".moltpy" / "config.json"
            if path.exists():
                with path.open("r", encoding="utf-8") as f:
                    data.update(json.load(f))

            # Example: Optional JSON file
            path = os.getenv("CONFIG_PATH")
            if path:
                with open(path, "r", encoding="utf-8") as f:
                    data.update(json.load(f))

            return ConfigObject(data=data)

        def dataObjectFromFile(self, path: Path | None = None) -> DataObject:
            data: dict[str, Any] = {}
            if path is None:
                path = Path.home() / ".moltpy" / "data.json"
            if path.exists():
                with path.open("r", encoding="utf-8") as f:
                    data.update(json.load(f))
            return DataObject(data=data)
        
        def envObject(self) -> EnvObject:
            data: dict[str, Any] = {}

            # Example: ENV
            data["env"] = os.getenv("APP_ENV", "dev")

            # Example: Optional JSON file
            path = os.getenv("CONFIG_PATH")
            if path:
                with open(path, "r", encoding="utf-8") as f:
                    data.update(json.load(f))

            return EnvObject(data=data)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def loader(self) -> "MoltpyRuntime.Loader":
        if self._loader is None:
            self._loader = self.Loader()
        return self._loader

    def logger(self) -> MoltpyLogger:
        if self._logger is None:
            self._logger = MoltpyLogger.for_class(self)
        return self._logger
    
    def firstRun(self, path: Path):
        # Perform first-run setup tasks


        # Create a lock file to indicate first run has been completed
        lock_path = path / "moltpy.lock"
        try:
            lock_path.write_text("initialized", encoding="utf-8")
            self.logger().info("Created first-run lock at {path}", path=lock_path)
        except OSError as exc:
            self.logger().error(
                "Failed to create first-run lock at {path}: {error}",
                path=lock_path,
                error=exc,
            )
            raise

    def firstRunCheck(self, path: Path) -> bool:
        return not os.path.exists(path / "moltpy.lock")

    def initialize(self, config: ConfigObject | None = None) -> "MoltpyRuntime":
        if self._initialized:
            return self
        self._initialized = True
        base_path = Path.home() / ".moltpy"
        you_path = Path("moltpy.json")

        try:
            self._you = self.loader().dataObjectFromFile(you_path)
            self.you = self._you
            self.logger().info("Loaded AI profile from {path}", path=you_path)
        except (OSError, json.JSONDecodeError) as exc:
            self.logger().error(
                "Failed to load AI profile from {path}: {error}",
                path=you_path,
                error=exc,
            )
            raise

        override = self.you.get("override")
        if isinstance(override, dict):
            override_path = override.get("moltpy_path")
            if isinstance(override_path, str) and override_path.strip():
                candidate = Path(override_path).expanduser()
                if not candidate.is_absolute():
                    candidate = (Path.cwd() / candidate).resolve()
                base_path = candidate
        elif isinstance(override, str) and override.strip():
            candidate = Path(override).expanduser()
            if not candidate.is_absolute():
                candidate = (Path.cwd() / candidate).resolve()
            base_path = candidate

        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)
        tools_path = self.base_path / "tools"
        tools_path.mkdir(parents=True, exist_ok=True)

        if self.firstRunCheck(self.base_path):
            self.firstRun(self.base_path)
            self.logger().info("MoltpyRuntime first run setup completed")

        if config is None:
            config = self.loader().configObject(self.base_path / "config.json")
        self.config = config
        if not isinstance(self.config.data.get("override"), dict):
            self.config.data["override"] = {}
        self.config.data["override"]["moltpy_path"] = str(self.base_path)
        self.configure_logging()
        self.logger().info("MoltpyRuntime configuration loaded")

        runtime_cfg = self.config.get("runtime", {}) or {}
        self._heartbeat.set_interval(
            float(runtime_cfg.get("heartbeat_interval", self._heartbeat.interval()))
        )

        self.data = self.loader().dataObjectFromFile(self.base_path / "data.json")
        self.logger().info("MoltpyRuntime data loaded from {path}", path=self.base_path / "data.json")

        repo_tools_path = Path.cwd() / "src" / "tools"
        self.tools.load_tools([repo_tools_path, tools_path])
        self.logger().info(
            "MoltpyRuntime tools loaded ({count} total) from {repo} and {user}",
            count=len(self.tools.all()),
            repo=repo_tools_path,
            user=tools_path,
        )

        self._heartbeat.ensure_thread()
        if self._heartbeat.running():
            self._heartbeat.activate()
            self._heartbeat.ensure_uptime_started()

        self.logger().info("MoltpyRuntime initialized")
        return self

    def uptime_seconds(self) -> int:
        return self._heartbeat.uptime_seconds()

    def uptime_text(self) -> str:
        return self._heartbeat.uptime_text()

    def reload_config(self) -> None:
        self.config = self.loader().configObject(self.base_path / "config.json")
        self.configure_logging()
        runtime_cfg = self.config.get("runtime", {}) or {}
        self._heartbeat.set_interval(
            float(runtime_cfg.get("heartbeat_interval", self._heartbeat.interval()))
        )
        self.logger().info("MoltpyRuntime configuration reloaded")

    def start_heartbeat(self) -> None:
        self._heartbeat.start()

    def resume_heartbeat(self) -> None:
        self._heartbeat.resume()

    def pause_heartbeat(self) -> None:
        self._heartbeat.pause()

    def stop_heartbeat(self) -> None:
        self._heartbeat.stop()

    def restart_heartbeat(self) -> None:
        self._heartbeat.restart()

    def heartbeat(self):
        self._heartbeat.run_cycle()

    def status_line(self) -> str:
        state = "paused" if self._heartbeat.state() == "paused" else "running"
        return (
            f"heartbeat={state if self._heartbeat.running() else 'stopped'}; "
            f"thread={'alive' if self.heartbeat_thread_alive() else 'dead'}; "
            f"interval={self._heartbeat.interval():.2f}s"
        )
    
    def shutdown(self):
        self.logger().info("MoltpyRuntime shutting down")
        self._heartbeat.shutdown()
        MoltpyRuntime._instance = None

    def heartbeat_running(self) -> bool:
        return self._heartbeat.running()

    def heartbeat_state(self) -> str:
        return self._heartbeat.state()

    def heartbeat_thread_alive(self) -> bool:
        return self._heartbeat.thread_alive()

    def heartbeat_interval(self) -> float:
        return self._heartbeat.interval()

    def last_heartbeat_at(self) -> datetime | None:
        return self._heartbeat.last_heartbeat_at()

    def config_path(self) -> Path:
        return self.base_path / "config.json"

    def data_path(self) -> Path:
        return self.base_path / "data.json"

    def logging_enabled(self) -> bool:
        return self._log_enabled

    def log_path(self) -> Path | None:
        return self._log_path

    def log_level_name(self) -> str:
        return self._log_level_name

    def configure_logging(self) -> None:
        logging_cfg = self.config.get("logging", {}) or {}
        enabled = bool(logging_cfg.get("log_enabled", False))
        level_name = str(logging_cfg.get("log_level", "INFO")).upper()
        level_map = {
            "DEBUG": LogLevel.DEBUG,
            "INFO": LogLevel.INFO,
            "WARNING": LogLevel.WARNING,
            "ERROR": LogLevel.ERROR,
        }
        MoltpyLogger.configure(min_level=level_map.get(level_name, LogLevel.INFO))
        self._log_enabled = enabled
        self._log_level_name = level_name
        if self._file_sink is not None:
            MoltpyLogger.remove_sink(self._file_sink)
            self._file_sink = None
        self._log_path = None
        if not enabled:
            return
        log_dir = self.base_path / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = str(logging_cfg.get("log_file", "moltpy.log"))
        log_path = Path(log_file)
        if not log_path.is_absolute():
            log_path = log_dir / log_path
        self._log_path = log_path
        log_format = str(logging_cfg.get("log_format", "[{asctime}] [{levelname}] {message}"))
        date_format = str(logging_cfg.get("log_date_format", "%Y-%m-%d %H:%M:%S"))
        log_split = str(logging_cfg.get("log_split", "size")).lower()
        max_bytes = int(logging_cfg.get("log_max_bytes", 0) or 0)
        backup_count = int(logging_cfg.get("log_backup_count", 0) or 0)
        rotation_enabled = log_split == "size" and max_bytes > 0 and backup_count > 0

        def rotate_logs() -> None:
            if not log_path.exists():
                return
            for index in range(backup_count - 1, 0, -1):
                src = log_path.with_suffix(log_path.suffix + f".{index}")
                dst = log_path.with_suffix(log_path.suffix + f".{index + 1}")
                if src.exists():
                    if dst.exists():
                        dst.unlink()
                    src.rename(dst)
            first = log_path.with_suffix(log_path.suffix + ".1")
            if first.exists():
                first.unlink()
            log_path.rename(first)
        def file_sink(level: int, line: str, _rich: Any) -> None:
            asctime = datetime.now().strftime(date_format)
            levelname = LogLevel.name(level)
            rendered = log_format.format(asctime=asctime, levelname=levelname, message=line)
            if rotation_enabled and log_path.exists():
                try:
                    current_size = log_path.stat().st_size
                except OSError:
                    current_size = 0
                if current_size + len(rendered.encode("utf-8")) + 1 > max_bytes:
                    rotate_logs()
            with log_path.open("a", encoding="utf-8") as f:
                f.write(rendered + "\n")

        self._file_sink = file_sink
        MoltpyLogger.add_sink(file_sink)


@dataclass
class UIState:
    header_title: str = "Moltpy"
    header_subtitle: str = "Runtime Console"
    status_text: str = "running"
    status_level: str = "ok"
    progress_total: int = 100
    progress_value: int = 0
    footer_note: str = ""
    output_title: str = "HeartbeatLog"

    def set_header(self, title: str | None = None, subtitle: str | None = None) -> None:
        if title is not None:
            self.header_title = title
        if subtitle is not None:
            self.header_subtitle = subtitle

    def set_status(self, text: str, level: str = "ok") -> None:
        self.status_text = text
        self.status_level = level

    def set_progress(self, value: int, total: int | None = None) -> None:
        if total is not None and total > 0:
            self.progress_total = total
        self.progress_value = max(0, min(value, self.progress_total))

    def set_footer_note(self, note: str) -> None:
        self.footer_note = note

    def set_output_title(self, title: str) -> None:
        if title:
            self.output_title = title
