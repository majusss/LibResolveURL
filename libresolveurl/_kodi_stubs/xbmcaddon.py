"""
Stub for the ``xbmcaddon.Addon`` Kodi class.

Settings are persisted to ``~/.config/libresolveurl/settings.json`` so that
debrid tokens and other resolver configuration survive between Python sessions.

The addon path returned by ``getAddonInfo('path')`` is driven by the
``LIBRESOLVEURL_CONFIG_DIR`` environment variable (set by libresolveurl
before any stubs are imported).
"""
import json
import logging
import os
import threading

_logger = logging.getLogger("libresolveurl")

# Resolved at import time — env vars are set by libresolveurl/__init__.py
# before any stub is first imported.
_CONFIG_DIR: str = os.environ.get(
    "LIBRESOLVEURL_CONFIG_DIR",
    os.path.join(os.path.expanduser("~"), ".config", "libresolveurl"),
)

_SETTINGS_FILE: str = os.path.join(_CONFIG_DIR, "settings.json")
_settings: dict = {}
_lock = threading.Lock()


def _load() -> None:
    global _settings
    if os.path.exists(_SETTINGS_FILE):
        try:
            with open(_SETTINGS_FILE, "r", encoding="utf-8") as fh:
                _settings = json.load(fh)
        except Exception as exc:
            _logger.warning("xbmcaddon: failed to load settings: %s", exc)
            _settings = {}


def _save() -> None:
    os.makedirs(_CONFIG_DIR, exist_ok=True)
    with open(_SETTINGS_FILE, "w", encoding="utf-8") as fh:
        json.dump(_settings, fh, indent=2)


# Load persisted settings eagerly so resolvers pick them up immediately.
_load()


class Addon:
    """Minimal Addon stub backed by a JSON settings file."""

    # Static addon metadata — values that don't change between instances.
    _ADDON_INFO: dict = {
        "name": "ResolveURL",
        "version": "5.1.0",
        "id": "script.module.resolveurl",
        "path": _CONFIG_DIR,
        "profile": _CONFIG_DIR,
        "changelog": "",
        "description": "ResolveURL Python library",
        "disclaimer": "",
        "fanart": "",
        "icon": "",
        "stars": "-1",
        "summary": "Resolves hosting page URLs to direct media streams",
        "type": "xbmc.python.module",
    }

    def __init__(self, addon_id: str = "script.module.resolveurl") -> None:
        self._id = addon_id

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def getSetting(self, key: str) -> str:
        with _lock:
            return str(_settings.get(key, ""))

    def setSetting(self, key: str, value: str) -> None:
        with _lock:
            _settings[key] = value
            try:
                _save()
            except Exception as exc:
                _logger.warning("xbmcaddon: failed to save settings: %s", exc)

    # ------------------------------------------------------------------
    # Addon info
    # ------------------------------------------------------------------

    def getAddonInfo(self, key: str) -> str:
        # kodi.kodi_version() queries 'xbmc.addon' for the Kodi player version.
        # We return 19.0 (Kodi Matrix) so all PY3 code paths are taken.
        if key == "version" and self._id == "xbmc.addon":
            return "19.0"
        return self._ADDON_INFO.get(key, "")

    def getLocalizedString(self, string_id) -> str:
        # Outside Kodi there is no translation; return the raw ID as a string
        # so callers that embed it in XML don't crash.
        return str(string_id)

    def openSettings(self) -> None:
        """No-op: settings UI is not available outside Kodi."""
        pass
