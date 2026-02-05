from core import MoltpyLogger
from core.bootstrap import MoltpyRuntime
from tui import MoltpyTui

Moltpy = MoltpyRuntime.get_instance()
Moltpy.initialize()
Logger = MoltpyLogger.for_class(Moltpy)

tui = MoltpyTui(Moltpy, Logger)
tui.run()
