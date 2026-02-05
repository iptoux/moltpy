from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, ClassVar

try:
    from rich.console import Console
    from rich.text import Text
except Exception:
    Console = None  # type: ignore[assignment]
    Text = None  # type: ignore[assignment]


class LogLevel:
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40

    _names: ClassVar[dict[int, str]] = {
        DEBUG: "DEBUG",
        INFO: "INFO",
        WARNING: "WARNING",
        ERROR: "ERROR",
    }

    @classmethod
    def name(cls, level: int) -> str:
        return cls._names.get(level, f"LEVEL_{level}")


@dataclass
class MoltpyLogger:
    name: str
    min_level: int = LogLevel.INFO

    _instances: ClassVar[dict[str, "MoltpyLogger"]] = {}
    _console: ClassVar["Console | None"] = None
    _use_rich: ClassVar[bool] = True
    _emit_to_console: ClassVar[bool] = True
    _sinks: ClassVar[list[Callable[[int, str, "Text | None"], None]]] = []
    _default_min_level: ClassVar[int] = LogLevel.INFO
    
    @classmethod
    def get(cls, name: str, min_level: int | None = None) -> "MoltpyLogger":
        if name not in cls._instances:
            level = cls._default_min_level if min_level is None else min_level
            cls._instances[name] = cls(name=name, min_level=level)
        if min_level is not None:
            cls._instances[name].min_level = min_level
        return cls._instances[name]

    @classmethod
    def for_class(cls, obj_or_cls: Any, min_level: int | None = None) -> "MoltpyLogger":
        if isinstance(obj_or_cls, type):
            name = obj_or_cls.__name__
        else:
            name = obj_or_cls.__class__.__name__
        return cls.get(name=name, min_level=min_level)

    @classmethod
    def configure(
        cls,
        use_rich: bool | None = None,
        emit_to_console: bool | None = None,
        sink: Callable[[int, str, "Text | None"], None] | None = None,
        min_level: int | None = None,
    ) -> None:
        if use_rich is not None:
            cls._use_rich = use_rich
        if emit_to_console is not None:
            cls._emit_to_console = emit_to_console
        if sink is not None:
            cls._sinks = [sink]
        if min_level is not None:
            cls._default_min_level = min_level
            for logger in cls._instances.values():
                logger.min_level = min_level

    @classmethod
    def add_sink(cls, sink: Callable[[int, str, "Text | None"], None]) -> None:
        cls._sinks.append(sink)

    @classmethod
    def remove_sink(cls, sink: Callable[[int, str, "Text | None"], None]) -> None:
        cls._sinks = [s for s in cls._sinks if s is not sink]

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._log(LogLevel.DEBUG, message, *args, **kwargs)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._log(LogLevel.INFO, message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._log(LogLevel.WARNING, message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._log(LogLevel.ERROR, message, *args, **kwargs)

    @classmethod
    def _get_console(cls) -> "Console | None":
        if cls._console is None and cls._use_rich and Console is not None:
            cls._console = Console()
        return cls._console

    def _log(self, level: int, message: str, *args: Any, **kwargs: Any) -> None:
        if level < self.min_level:
            return
        if args or kwargs:
            message = message.format(*args, **kwargs)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level_name = LogLevel.name(level)
        console = self._get_console()
        if console is not None and Text is not None:
            level_style = {
                LogLevel.DEBUG: "dim",
                LogLevel.INFO: "cyan",
                LogLevel.WARNING: "yellow",
                LogLevel.ERROR: "bold red",
            }.get(level, "white")
            text = Text()
            text.append(timestamp, style="dim")
            text.append(" [")
            text.append(level_name, style=level_style)
            text.append("] ")
            text.append(self.name, style="bold dark_green")
            text.append(": ")
            text.append(message)
            for sink in self.__class__._sinks:
                sink(level, f"{timestamp} [{level_name}] {self.name}: {message}", text)
            if self.__class__._emit_to_console:
                console.print(text)
            return
        line = f"{timestamp} [{level_name}] {self.name}: {message}"
        for sink in self.__class__._sinks:
            sink(level, line, None)
        if self.__class__._emit_to_console:
            print(line)
