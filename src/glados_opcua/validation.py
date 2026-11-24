"""Configuration loading and validation.

Files under ``config/`` are the source of truth; environment variables override
only a small, documented set (see :mod:`glados_opcua.settings`).  Loading is
fail-fast: every cross-reference, duplicate NodeId and profile rule is checked
before the server binds a socket.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ValidationError

from .models import EquipmentSpec, Manifest, NamespaceFile, PermissionsConfig, ServerConfig
from .settings import apply_environment

_logger = logging.getLogger(__name__)

DEVICE_GLOB = "*.yaml"


class ConfigurationError(ValueError):
    """Raised when configuration cannot be loaded or validated."""


def _read_yaml(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except FileNotFoundError as exc:
        raise ConfigurationError(f"missing configuration file: {path}") from exc
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"invalid YAML in {path}: {exc}") from exc


def _load_model(path: Path, model: type[BaseModel], **kwargs: Any):
    data = _read_yaml(path)
    if not isinstance(data, dict):
        raise ConfigurationError(f"{path} must contain a YAML mapping")
    try:
        return model.model_validate(data, **kwargs)
    except ValidationError as exc:
        raise ConfigurationError(f"invalid {path}:\n{exc}") from exc


def load_manifest(config_dir: str | Path, environ: Mapping[str, str] | None = None) -> Manifest:
    """Load ``config_dir`` into a fully validated :class:`Manifest`.

    Device files are read in lexical filename order, which keeps generated
    output and error messages deterministic.  Object and variable order inside
    a file is preserved exactly as written.
    """
    root = Path(config_dir)
    server = _load_model(root / "server.yaml", ServerConfig)
    namespaces = _load_model(root / "namespaces.yaml", NamespaceFile)
    extra_namespaces = root / "namespaces.extra.yaml"
    if extra_namespaces.exists():
        added = _load_model(extra_namespaces, NamespaceFile)
        try:
            namespaces = NamespaceFile(
                namespaces=[*namespaces.namespaces, *added.namespaces]
            )
        except ValidationError as exc:
            raise ConfigurationError(f"invalid {extra_namespaces}:\n{exc}") from exc
    permissions = _load_model(root / "permissions.yaml", PermissionsConfig)

    device_dir = root / "devices"
    if not device_dir.is_dir():
        raise ConfigurationError(f"missing device configuration directory: {device_dir}")
    equipment: list[EquipmentSpec] = []
    for path in sorted(device_dir.glob(DEVICE_GLOB)):
        data = _read_yaml(path)
        if not isinstance(data, dict) or "equipment" not in data:
            raise ConfigurationError(f"{path} must contain an 'equipment' list")
        version = data.get("config_version", 1)
        if version != 1:
            raise ConfigurationError(f"{path}: unsupported config_version {version!r} (expected 1)")
        unexpected = set(data) - {"config_version", "equipment"}
        if unexpected:
            raise ConfigurationError(f"{path}: unexpected keys {sorted(unexpected)}")
        try:
            equipment.extend(EquipmentSpec.model_validate(item) for item in data["equipment"])
        except ValidationError as exc:
            raise ConfigurationError(f"invalid {path}:\n{exc}") from exc

    try:
        server = apply_environment(server, environ)
    except ValueError as exc:
        raise ConfigurationError(f"invalid environment override: {exc}") from exc
    try:
        manifest = Manifest(
            server=server,
            namespaces=namespaces,
            equipment=equipment,
            permissions=permissions,
        )
    except ValidationError as exc:
        raise ConfigurationError(f"invalid configuration:\n{exc}") from exc
    _logger.debug("Loaded configuration from %s", root)
    return manifest
