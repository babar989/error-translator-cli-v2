"""
Auto-translator hook module.

When imported, this module sets a custom sys.excepthook handler to intercept
unhandled exceptions, translate the traceback into structured advice, and render
it before process termination.
"""

import sys
import traceback

from .core import translate_error
from .ui import print_result


def exception_hook(exc_type, exc_value, tb):
    """
    Custom exception hook that intercepts unhandled Python exceptions.
    Formats the traceback, translates the error into actionable advice,
    and displays the diagnostic panel.

    Args:
        exc_type: The type of the exception.
        exc_value: The exception instance.
        tb: The traceback object containing the call stack.
    """
    # Ctrl+C / sys.exit() must behave exactly as without the hook installed.
    if issubclass(exc_type, (KeyboardInterrupt, SystemExit)):
        sys.__excepthook__(exc_type, exc_value, tb)
        return

    # 1. Always show the real traceback first (stderr, like Python itself).
    traceback.print_exception(exc_type, exc_value, tb)

    # 2. Then the translation — but a broken translation must never
    #    destroy the error reporting above.
    try:
        tb_string = "".join(traceback.format_exception(exc_type, exc_value, tb))
        result = translate_error(tb_string)
        print_result(result)
    except Exception:
        pass


# Alias for backward compatibility if referenced internally
magic_hook = exception_hook

# Override default exception handler
sys.excepthook = exception_hook
