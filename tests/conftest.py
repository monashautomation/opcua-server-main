"""Shared fixtures: isolated configuration copies and live server bundles."""

from __future__ import annotations

import shutil
import socket
from pathlib import Path

import pytest
import yaml
from asyncua import Client

from glados_opcua.models import Manifest, Profile
from glados_opcua.server import ServerBundle, build_server
from glados_opcua.validation import load_manifest

REPO = Path(__file__).resolve().parents[1]
BASE_CONFIG = REPO / "config"


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def endpoint() -> str:
    return f"opc.tcp://127.0.0.1:{free_port()}/server/"


def read_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def copy_config(
    tmp_path: Path,
    *,
    url: str | None = None,
    profile: str = "legacy",
    health: bool = False,
    security: dict | None = None,
    server: dict | None = None,
    permissions: dict | None = None,
) -> Path:
    """Copy the shipped configuration and apply test-specific overrides."""
    root = tmp_path / "config"
    shutil.copytree(BASE_CONFIG, root, ignore=shutil.ignore_patterns("examples"))
    server_data = read_yaml(root / "server.yaml")
    server_data.update(
        {
            "profile": profile,
            "endpoint": url or endpoint(),
            "health": {**server_data["health"], "enabled": health},
        }
    )
    if profile == Profile.PRODUCTION.value:
        server_data["security"].update(
            {
                "policies": ["Basic256Sha256_SignAndEncrypt"],
                "identity_tokens": ["Username"],
                "allow_anonymous": False,
                "allow_insecure_legacy": False,
            }
        )
    if security:
        server_data["security"].update(security)
    if server:
        server_data.update(server)
    write_yaml(root / "server.yaml", server_data)

    permissions_data = read_yaml(root / "permissions.yaml")
    permissions_data["enforced"] = profile == Profile.PRODUCTION.value
    if permissions:
        permissions_data.update(permissions)
    write_yaml(root / "permissions.yaml", permissions_data)
    return root


def manifest_for(config_dir: Path) -> Manifest:
    return load_manifest(config_dir, environ={})


@pytest.fixture
async def legacy_bundle(tmp_path: Path):
    """A started legacy-compatible server on a free loopback port."""
    config_dir = copy_config(tmp_path)
    manifest = manifest_for(config_dir)
    bundle: ServerBundle = await build_server(manifest)
    async with bundle.server:
        try:
            yield bundle
        finally:
            if bundle.health is not None:
                await bundle.health.stop()
            bundle.audit.stop()


@pytest.fixture
async def legacy_client(legacy_bundle: ServerBundle):
    async with Client(url=legacy_bundle.manifest.server.endpoint) as client:
        yield client
