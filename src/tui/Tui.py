from __future__ import annotations

import os
import random
import time
from collections import deque
from typing import Deque

import msvcrt
from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from core import MoltpyLogger

try:
    import psutil  # type: ignore
except Exception:
    psutil = None


class LogBuffer:
    def __init__(self, max_lines: int = 200) -> None:
        self._lines: Deque[Text] = deque(maxlen=max_lines)
        self.scroll_offset = 0

    def append(self, line: str, rich_text: Text | None) -> None:
        if rich_text is not None:
            self._lines.append(rich_text)
            return
        self._lines.append(Text(line))

    def render(self, max_lines: int | None = None, title: str = "HeartbeatLog") -> Panel:
        if not self._lines:
            body = Text("Waiting for output...", style="dim")
        else:
            lines = list(self._lines)
            if max_lines is not None and max_lines > 0:
                max_scroll = max(0, len(lines) - max_lines)
                if self.scroll_offset > max_scroll:
                    self.scroll_offset = max_scroll
                end_index = len(lines) - self.scroll_offset
                start_index = max(0, end_index - max_lines)
                lines = lines[start_index:end_index]
            body = Group(*lines)
        return Panel(body, title=title, border_style="cyan")

    def scroll_up(self, lines: int) -> None:
        if lines <= 0:
            return
        self.scroll_offset += lines

    def scroll_down(self, lines: int) -> None:
        if lines <= 0:
            return
        self.scroll_offset = max(0, self.scroll_offset - lines)

    def scroll_to_bottom(self) -> None:
        self.scroll_offset = 0


class ReplBuffer:
    def __init__(self, commands: list[str], arg_suggestions: dict[str, list[str]]) -> None:
        self.buffer = ""
        self.commands: Deque[str] = deque()
        self.history: Deque[str] = deque(maxlen=200)
        self.history_index: int | None = None
        self.idle_hint = ""
        self.idle_hint_until = 0.0
        self._tab_matches: list[str] = []
        self._tab_index: int = 0
        self._tab_seed: str = ""
        self.scroll_delta = 0
        self._commands = commands
        self._arg_suggestions = arg_suggestions

    def poll_input(self) -> None:
        while msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                if self.buffer.strip():
                    self.commands.append(self.buffer.strip())
                    self.history.append(self.buffer.strip())
                    self.history_index = None
                self.buffer = ""
            elif ch == "\t":
                self.autocomplete()
            elif ch == "\b":
                self.buffer = self.buffer[:-1]
            elif ch in ("\x00", "\xe0"):
                key = msvcrt.getwch()
                self.handle_special(key)
            else:
                if ch.isprintable():
                    self.buffer += ch

    def next_command(self) -> str | None:
        if self.commands:
            return self.commands.popleft()
        return None

    def autocomplete(self) -> None:
        if not self.buffer:
            return
        raw = self.buffer
        tokens = raw.strip().split()
        if not tokens:
            return
        if len(tokens) == 1 and not raw.endswith(" "):
            token = tokens[0].lower()
            matches = [c for c in self._commands if c.startswith(token)]
            if not matches:
                return
            seed = f"cmd:{token}"
            if seed != self._tab_seed:
                self._tab_seed = seed
                self._tab_matches = matches
                self._tab_index = 0
            if len(self._tab_matches) == 1:
                self.buffer = self._tab_matches[0]
            else:
                self.buffer = self._tab_matches[self._tab_index]
                self._tab_index = (self._tab_index + 1) % len(self._tab_matches)
            return
        cmd = tokens[0].lower()
        arg_token = tokens[-1] if not raw.endswith(" ") else ""
        suggestions = self._arg_suggestions.get(cmd, [])
        matches = [a for a in suggestions if a.startswith(arg_token.lower())]
        if not matches:
            return
        seed = f"arg:{cmd}:{arg_token.lower()}"
        if seed != self._tab_seed:
            self._tab_seed = seed
            self._tab_matches = matches
            self._tab_index = 0
        prefix = " ".join(tokens[:-1]) if arg_token else " ".join(tokens)
        if len(self._tab_matches) == 1:
            self.buffer = f"{prefix} {self._tab_matches[0]}".strip()
        else:
            self.buffer = f"{prefix} {self._tab_matches[self._tab_index]}".strip()
            self._tab_index = (self._tab_index + 1) % len(self._tab_matches)

    def handle_special(self, key: str) -> None:
        if not self.history:
            if key == "I":  # PageUp
                self.scroll_delta += 1
            elif key == "Q":  # PageDown
                self.scroll_delta -= 1
            return
        if key == "H":  # Up
            if self.history_index is None:
                self.history_index = len(self.history) - 1
            else:
                self.history_index = max(0, self.history_index - 1)
            self.buffer = self.history[self.history_index]
        elif key == "P":  # Down
            if self.history_index is None:
                return
            if self.history_index >= len(self.history) - 1:
                self.history_index = None
                self.buffer = ""
            else:
                self.history_index += 1
                self.buffer = self.history[self.history_index]
        elif key == "I":  # PageUp
            self.scroll_delta += 1
        elif key == "Q":  # PageDown
            self.scroll_delta -= 1

    def idle_hint_text(self) -> str:
        now = time.time()
        if not self.idle_hint or now >= self.idle_hint_until:
            idle_hints = [
                "Enter help for info",
                "Tip: Type 'help' to see commands",
                "Use Tab to autocomplete",
                "Try: status full",
            ]
            self.idle_hint = random.choice(idle_hints)
            self.idle_hint_until = now + 5.0
        return self.idle_hint


class MoltpyTui:
    COMMANDS = ["reload", "stop", "start", "restart", "pause", "resume", "status", "tools", "help", "exit", "quit"]
    ARG_SUGGESTIONS = {
        "status": ["short", "full"],
    }

    def __init__(self, runtime, logger) -> None:
        self.runtime = runtime
        self.logger = logger
        self.console = Console()
        self.layout = Layout()
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=4),
        )
        self.log_buffer = LogBuffer()
        self.repl = ReplBuffer(self.COMMANDS, self.ARG_SUGGESTIONS)
        self._running = True
        MoltpyLogger.configure(emit_to_console=False)
        MoltpyLogger.add_sink(self._logger_sink)

    def _logger_sink(self, level: int, line: str, rich_text: Text | None) -> None:
        self.log_buffer.append(line, rich_text)

    def render_header(self) -> Panel:
        name = self.runtime.you.get("name", self.runtime.ui.header_title)
        short_desc = self.runtime.you.get(
            "kurzbeschereibung",
            self.runtime.you.get("kurzbeschreibung", ""),
        )
        title = Text(name, style="bold white")
        if short_desc:
            title.append("  ·  ", style="dim")
            title.append(short_desc, style="white")
        subtitle = Text(self.runtime.ui.header_subtitle, style="dim")
        status_style = {
            "ok": "green",
            "warn": "yellow",
            "error": "bold red",
            "idle": "dim",
        }.get(self.runtime.ui.status_level, "green")
        status_text = self.runtime.ui.status_text.capitalize()
        thread_state = "alive" if self.runtime.heartbeat_thread_alive() else "dead"
        uptime_part = f" | Up: {self.runtime.uptime_text()}" if self.runtime.heartbeat_thread_alive() else ""
        status = Text(f"{status_text} · Thread: {thread_state}{uptime_part}", style=status_style)
        grid = Table.grid(expand=True)
        grid.add_column(justify="left")
        grid.add_column(justify="right")
        grid.add_row(title, status)
        header = Group(grid, Align.left(subtitle))
        return Panel(header, border_style="bright_magenta")

    def render_footer(self) -> Panel:
        prompt = Text("$:> ", style="bold cyan")
        input_text = Text(self.repl.buffer, style="white")
        blink_on = int(time.time() * 2) % 2 == 0
        cursor = Text("_" if blink_on else " ", style="bold white")
        line = Text.assemble(prompt, input_text, cursor)

        hint = Text("")
        raw = self.repl.buffer
        tokens = raw.strip().split()
        if tokens and not raw.endswith(" "):
            if len(tokens) == 1:
                token = tokens[0].lower()
                matches = [c for c in self.COMMANDS if c.startswith(token)]
                if len(matches) >= 1:
                    hint = Text("Suggestions: " + ", ".join(matches), style="dim")
            else:
                cmd = tokens[0].lower()
                arg_token = tokens[-1].lower()
                suggestions = self.ARG_SUGGESTIONS.get(cmd, [])
                matches = [a for a in suggestions if a.startswith(arg_token)]
                if len(matches) >= 1:
                    hint = Text("Suggestions: " + ", ".join(matches), style="dim")
        if not hint.plain and not self.repl.buffer:
            hint = Text(self.repl.idle_hint_text(), style="dim")

        footer = Group(Align.left(line), Align.left(hint))
        return Panel(footer, border_style="bright_magenta")

    def handle_command(self, command: str) -> None:
        parts = command.strip().split()
        cmd = parts[0].lower() if parts else ""
        args = [p.lower() for p in parts[1:]]
        if cmd == "reload":
            self.runtime.reload_config()
            self.logger.info("Reloaded configuration")
        elif cmd == "stop":
            self.runtime.stop_heartbeat()
            self.stop()
        elif cmd == "start":
            self.runtime.start_heartbeat()
        elif cmd == "restart":
            self.runtime.restart_heartbeat()
        elif cmd == "pause":
            self.runtime.pause_heartbeat()
        elif cmd == "resume":
            self.runtime.resume_heartbeat()
        elif cmd == "status":
            detail = " ".join(args).strip()
            if detail == "full":
                last_hb = self.runtime.last_heartbeat_at()
                last_hb_text = last_hb.strftime("%Y-%m-%d %H:%M:%S") if last_hb else "n/a"
                log_enabled = "yes" if self.runtime.logging_enabled() else "no"
                log_path = str(self.runtime.log_path()) if self.runtime.log_path() is not None else "n/a"
                log_file = "yes" if self.runtime.log_path() is not None else "no"
                cpu_text = "n/a"
                mem_text = "n/a"
                if psutil is not None:
                    try:
                        proc = psutil.Process(os.getpid())
                        cpu_text = f"{proc.cpu_percent(interval=0.0):.1f}%"
                        mem_text = f"{proc.memory_info().rss / (1024 * 1024):.1f} MB"
                    except Exception:
                        pass
                self.logger.info(
                    "Runtime status: {status}",
                    status=self.runtime.status_line(),
                )
                self.logger.info(
                    "State: {state} | Thread: {thread} | Interval: {interval:.2f}s | Last heartbeat: {last}",
                    state=self.runtime.heartbeat_state(),
                    thread="alive" if self.runtime.heartbeat_thread_alive() else "dead",
                    interval=self.runtime.heartbeat_interval(),
                    last=last_hb_text,
                )
                self.logger.info(
                    "Uptime: {uptime} | CPU: {cpu} | MEM: {mem}",
                    uptime=self.runtime.uptime_text(),
                    cpu=cpu_text,
                    mem=mem_text,
                )

                def rel_path(path: object) -> str:
                    if path is None:
                        return "n/a"
                    try:
                        return os.path.relpath(str(path), os.getcwd())
                    except Exception:
                        return str(path)

                self.logger.info(
                    "Paths: base={base} | config={config} | data={data}",
                    base=rel_path(self.runtime.base_path),
                    config=rel_path(self.runtime.config_path()),
                    data=rel_path(self.runtime.data_path()),
                )
                self.logger.info(
                    "Logging: enabled={enabled} | level={log_level} | file={file} | path={path}",
                    enabled=log_enabled,
                    log_level=self.runtime.log_level_name(),
                    file=log_file,
                    path=rel_path(log_path),
                )
                self.logger.info("Env: {env}", env=self.runtime.config.get("env", "unknown"))
            else:
                self.logger.info("Runtime status: {status}", status=self.runtime.status_line())
        elif cmd == "tools":
            tools = sorted(self.runtime.tools.all(), key=lambda tool: tool.tool_name.lower())
            if not tools:
                self.logger.info("Tools: none loaded")
            else:
                self.logger.info("Tools loaded: {count}", count=len(tools))
                for tool in tools:
                    description = tool.description.strip() if tool.description else ""
                    if description:
                        self.logger.info("- {name}: {desc}", name=tool.tool_name, desc=description)
                    else:
                        self.logger.info("- {name}", name=tool.tool_name)
        elif cmd == "help":
            self.logger.info(
                "Commands: reload, stop, start, restart, pause, resume, status, tools, help, exit, quit (Tab=autocomplete, Up/Down=history)"
            )
        elif cmd in {"exit", "quit"}:
            self.stop()
            self.runtime.shutdown()
        else:
            self.logger.warning("Unknown command: {cmd}", cmd=command)

    def run(self) -> None:
        try:
            with Live(self.layout, refresh_per_second=10, screen=True, console=self.console):
                self.handle_command("status full")
                while self._running:
                    self.repl.poll_input()
                    cmd = self.repl.next_command()
                    if cmd is not None:
                        self.handle_command(cmd)
                    state = self.runtime.heartbeat_state()
                    if state == "running":
                        self.runtime.ui.set_status("running", "ok")
                    elif state == "paused":
                        self.runtime.ui.set_status("paused", "idle")
                    else:
                        self.runtime.ui.set_status("stopped", "idle")
                    self.layout["header"].update(self.render_header())
                    body_height = self.console.size.height - self.layout["header"].size - self.layout["footer"].size
                    visible_lines = max(1, body_height - 2)
                    if self.repl.scroll_delta:
                        if self.repl.scroll_delta > 0:
                            self.log_buffer.scroll_up(visible_lines * self.repl.scroll_delta)
                        else:
                            self.log_buffer.scroll_down(visible_lines * (-self.repl.scroll_delta))
                        self.repl.scroll_delta = 0
                    self.layout["body"].update(
                        self.log_buffer.render(
                            max_lines=visible_lines,
                            title=self.runtime.ui.output_title,
                        )
                    )
                    self.layout["footer"].update(self.render_footer())
                    time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()
            self.logger.info("Moltpy execution interrupted by user.")
            self.runtime.shutdown()

    def stop(self) -> None:
        self._running = False
