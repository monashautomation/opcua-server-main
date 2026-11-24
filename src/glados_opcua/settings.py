"""Environment overlay and profile rules.

Precedence is explicit: environment variable > YAML > model default.  Only
operational settings are overridable so a lost environment variable can never
silently weaken authentication.

| Variable | Effect |
|---|---|
| ``GLADOS_SERVER_URL`` | Advertised endpoint; legacy-compatible. |
| ``GLADOS_BIND_ADDRESS`` / ``GLADOS_BIND_PORT`` | Listen socket, separate from the advertised endpoint. |
| ``GLADOS_PROFILE`` | ``legacy`` or ``production``. |
| ``GLADOS_LOG_LEVEL`` / ``GLADOS_LOG_JSON`` | Logging. |
| ``GLADOS_HEALTH_ENABLED`` | Toggle the additive health namespace. |
"""

from __future__ import annotations

import os
from collections.abc import Mapping

from .models import Profile, ServerConfig


def _bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"expected a boolean, got {value!r}")


def apply_environment(config: ServerConfig, environ: Mapping[str, str] | None = None) -> ServerConfig:
    """Return a copy of ``config`` with documented environment overrides."""
    env = os.environ if environ is None else environ
    updates: dict[str, object] = {}

    if value := env.get("GLADOS_SERVER_URL"):
        updates["endpoint"] = value
    if value := env.get("GLADOS_PROFILE"):
        try:
            updates["profile"] = Profile(value.lower())
        except ValueError as exc:
            raise ValueError(f"GLADOS_PROFILE must be legacy or production, got {value!r}") from exc
    if value := env.get("GLADOS_BIND_ADDRESS"):
        updates["bind_address"] = value
    if value := env.get("GLADOS_BIND_PORT"):
        try:
            updates["bind_port"] = int(value)
        except ValueError as exc:
            raise ValueError(f"GLADOS_BIND_PORT must be an integer, got {value!r}") from exc
    if value := env.get("GLADOS_LOG_LEVEL"):
        updates["log_level"] = value.upper()
    if value := env.get("GLADOS_LOG_JSON"):
        updates["log_json"] = _bool(value)
    if value := env.get("GLADOS_HEALTH_ENABLED"):
        health = config.health.model_copy(update={"enabled": _bool(value)})
        updates["health"] = health.model_dump()

    if not updates:
        return config
    return ServerConfig.model_validate({**config.model_dump(), **updates})
