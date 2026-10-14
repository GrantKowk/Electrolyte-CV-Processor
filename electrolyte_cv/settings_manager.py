from __future__ import annotations

import copy
import json
from typing import Any, Mapping

SETTINGS_ORGANIZATION = "OpenAI"
SETTINGS_APPLICATION = "ElectrolyteCVProcessor"
PROFILE_SCHEMA_VERSION = 1
DEFAULTS_KEY = "preferences/default_profile"
LAST_SESSION_KEY = "preferences/last_session_profile"

TAB_IDS = ("cv", "charge", "peak", "onset", "shift", "qc")

SOFTWARE_DEFAULTS: dict[str, Any] = {
    "schema_version": PROFILE_SCHEMA_VERSION,
    "startup_behavior": "defaults",  # defaults | last_session
    "default_tab": "cv",
    "theme": "light",
    "log_expanded": False,
    "analysis": {
        "mode": "max",
        "start_voltage": 2.7,
        "end_voltage": 4.5,
        "scan_rate_mv": 5.0,
        "precision_mv": 5.0,
    },
    "output": {
        "selection_mode": "manual",
        "auto_target": 5,
        "preset": "二十圈选点",
        "manual_cycles": "1, 5, 10, 15, 20",
        "cut_only": True,
        "verify_file": False,
        "original_dir": True,
        "custom_dir": "",
    },
    "display": {
        "cv": {
            "curve": "raw",  # raw | smooth | both
            "scan": "analysis",  # analysis | full
            "peak": True,
            "threshold_onset": True,
            "tangent_onset": False,
            "legend": True,
        },
        "charge": {"style": "bar", "labels": False, "table": True},
        "peak": {"metric": "potential", "labels": False, "table": True},
        "onset": {"threshold": True, "tangent": True, "labels": False, "table": True},
        "shift": {
            "peak": True,
            "threshold": True,
            "tangent": True,
            "zero_line": True,
            "labels": False,
            "table": True,
        },
        "qc": {
            "status_ok": True,
            "status_review": True,
            "status_boundary": True,
            "status_failed": True,
            "only_abnormal": False,
        },
    },
}


def software_defaults() -> dict[str, Any]:
    return copy.deepcopy(SOFTWARE_DEFAULTS)


def _merge(default: Any, value: Any) -> Any:
    if isinstance(default, dict):
        result = copy.deepcopy(default)
        if isinstance(value, Mapping):
            for key, child in default.items():
                if key in value:
                    result[key] = _merge(child, value[key])
        return result
    return copy.deepcopy(value if value is not None else default)


def normalize_profile(value: Any) -> dict[str, Any]:
    profile = _merge(SOFTWARE_DEFAULTS, value if isinstance(value, Mapping) else {})
    profile["schema_version"] = PROFILE_SCHEMA_VERSION
    if profile.get("startup_behavior") not in ("defaults", "last_session"):
        profile["startup_behavior"] = "defaults"
    if profile.get("default_tab") not in TAB_IDS:
        profile["default_tab"] = "cv"
    if profile.get("theme") not in ("light", "dark"):
        profile["theme"] = "light"
    analysis = profile["analysis"]
    if analysis.get("mode") not in ("max", "min"):
        analysis["mode"] = "max"
    output = profile["output"]
    if output.get("selection_mode") not in ("auto", "manual"):
        output["selection_mode"] = "manual"
    cv = profile["display"]["cv"]
    if cv.get("curve") not in ("raw", "smooth", "both"):
        cv["curve"] = "raw"
    if cv.get("scan") not in ("analysis", "full"):
        cv["scan"] = "analysis"
    if profile["display"]["charge"].get("style") not in ("bar", "line"):
        profile["display"]["charge"]["style"] = "bar"
    if profile["display"]["peak"].get("metric") not in ("potential", "current"):
        profile["display"]["peak"]["metric"] = "potential"
    return profile


class SettingsManager:
    """Centralized persistence for global defaults and non-file last-session UI state."""

    def __init__(self, qsettings: Any):
        self.settings = qsettings

    def _read_profile(self, key: str) -> dict[str, Any] | None:
        raw = self.settings.value(key, "")
        if not raw:
            return None
        try:
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            value = json.loads(str(raw))
            return normalize_profile(value)
        except Exception:
            return None

    def _write_profile(self, key: str, profile: Mapping[str, Any]) -> dict[str, Any]:
        normalized = normalize_profile(profile)
        self.settings.setValue(key, json.dumps(normalized, ensure_ascii=False, separators=(",", ":")))
        try:
            self.settings.sync()
        except Exception:
            pass
        return normalized

    def load_defaults(self) -> dict[str, Any]:
        profile = self._read_profile(DEFAULTS_KEY)
        if profile is not None:
            return profile
        # Preserve theme from old v2.0 QSettings so upgrading does not silently reset it.
        profile = software_defaults()
        legacy_theme = str(self.settings.value("theme", "light") or "light")
        if legacy_theme in ("light", "dark"):
            profile["theme"] = legacy_theme
        return profile

    def save_defaults(self, profile: Mapping[str, Any]) -> dict[str, Any]:
        normalized = self._write_profile(DEFAULTS_KEY, profile)
        # Keep the legacy theme key synchronized for backward compatibility.
        self.settings.setValue("theme", normalized["theme"])
        return normalized

    def load_last_session(self) -> dict[str, Any] | None:
        return self._read_profile(LAST_SESSION_KEY)

    def save_last_session(self, profile: Mapping[str, Any]) -> dict[str, Any]:
        return self._write_profile(LAST_SESSION_KEY, profile)

    def startup_profile(self) -> dict[str, Any]:
        defaults = self.load_defaults()
        if defaults.get("startup_behavior") == "last_session":
            session = self.load_last_session()
            if session is not None:
                # Startup mode is a user preference, not transient session state.
                session["startup_behavior"] = "last_session"
                return session
        return defaults

    def restore_software_defaults(self) -> dict[str, Any]:
        defaults = software_defaults()
        self.save_defaults(defaults)
        self.settings.remove(LAST_SESSION_KEY)
        return defaults
