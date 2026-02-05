from __future__ import annotations

import threading
from datetime import datetime


class MoltpyHeartbeat:
    def __init__(self, runtime, interval: float = 0.1) -> None:
        self._runtime = runtime
        self._running = True
        self._paused = False
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._active = threading.Event()
        self._interval = interval
        self._uptime_started_at: datetime | None = None
        self._uptime_accumulated = 0.0
        self._last_heartbeat_at: datetime | None = None

    def ensure_thread(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        if self._stop.is_set():
            self._stop.clear()
        self._thread = threading.Thread(
            target=self._heartbeat_loop,
            name="moltpy-heartbeat",
            daemon=True,
        )
        self._thread.start()

    def activate(self) -> None:
        self._active.set()

    def run_cycle(self) -> None:
        if not self._running:
            return
        self._last_heartbeat_at = datetime.now()
        self._runtime.logger().info("MoltpyRuntime heartbeat cycle executed")

    def _heartbeat_loop(self) -> None:
        while not self._stop.is_set():
            if not self._active.is_set():
                self._active.wait(timeout=0.2)
                continue
            self.run_cycle()
            if self._stop.wait(self._interval):
                break

    def ensure_uptime_started(self) -> None:
        if self._uptime_started_at is None:
            self._uptime_started_at = datetime.now()

    def start(self) -> None:
        if not self._running:
            self._running = True
            self._paused = False
            self._active.set()
            self.ensure_thread()
            self.ensure_uptime_started()
            self._runtime.ui.set_status("running", "ok")
            self._runtime.logger().info("MoltpyRuntime heartbeat started")
            return
        if self._paused:
            self._paused = False
            self.ensure_uptime_started()
            self._runtime.ui.set_status("running", "ok")
            self._runtime.logger().info("MoltpyRuntime heartbeat resumed")
        self._active.set()
        self.ensure_thread()

    def resume(self) -> None:
        self.start()

    def pause(self) -> None:
        if not self._running or self._paused:
            return
        self._paused = True
        if self._uptime_started_at is not None:
            self._uptime_accumulated += (
                datetime.now() - self._uptime_started_at
            ).total_seconds()
            self._uptime_started_at = None
        self._active.clear()
        self._runtime.ui.set_status("paused", "idle")
        self._runtime.logger().info("MoltpyRuntime heartbeat paused")

    def stop(self) -> None:
        if self._running:
            self._running = False
            self._paused = False
            self._uptime_started_at = None
            self._uptime_accumulated = 0.0
            self._active.clear()
            self._stop.set()
            self._active.set()
            if self._thread is not None and self._thread.is_alive():
                self._thread.join(timeout=1.0)
            self._thread = None
            self._runtime.ui.set_status("stopped", "idle")
            self._runtime.logger().info("MoltpyRuntime heartbeat stopped")

    def restart(self) -> None:
        self._uptime_accumulated = 0.0
        self._uptime_started_at = None
        self._paused = False
        self.stop()
        self.start()

    def shutdown(self) -> None:
        self._stop.set()
        self._active.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._thread = None

    def uptime_seconds(self) -> int:
        total = self._uptime_accumulated
        if self._uptime_started_at is not None:
            total += (datetime.now() - self._uptime_started_at).total_seconds()
        return int(total)

    def uptime_text(self) -> str:
        total = self.uptime_seconds()
        hours = total // 3600
        minutes = (total % 3600) // 60
        seconds = total % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def running(self) -> bool:
        return self._running

    def state(self) -> str:
        if not self._running:
            return "stopped"
        if self._paused:
            return "paused"
        return "running"

    def thread_alive(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def interval(self) -> float:
        return self._interval

    def set_interval(self, interval: float) -> None:
        self._interval = interval

    def last_heartbeat_at(self) -> datetime | None:
        return self._last_heartbeat_at
