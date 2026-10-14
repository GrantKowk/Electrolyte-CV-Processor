from __future__ import annotations

from typing import Callable, Optional

_LOG_CALLBACK = None

def set_log_callback(callback=None):
    global _LOG_CALLBACK
    _LOG_CALLBACK = callback

def _emit_log(level, msg):
    if _LOG_CALLBACK is not None:
        try:
            _LOG_CALLBACK(level, str(msg))
            return
        except Exception:
            pass
    print(f"[{level}] {msg}")

def log_info(msg):
    _emit_log("INFO", msg)

def log_warning(msg):
    _emit_log("WARNING", msg)

def log_error(msg):
    _emit_log("ERROR", msg)
