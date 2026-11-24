"""Additive health namespace: unknown until telemetry, stale detection, read-only."""

from __future__ import annotations

import time
from pathlib import Path

import pytest
from asyncua import Client, ua

from glados_opcua.server import build_server

from .conftest import copy_config, manifest_for


async def test_health_lifecycle(tmp_path: Path):
    config = copy_config(tmp_path, health=True)
    manifest = manifest_for(config)
    bundle = await build_server(manifest)
    async with bundle.server:
        try:
            assert bundle.health is not None
            async with Client(url=manifest.server.endpoint) as client:
                namespaces = await client.get_namespace_array()
                assert namespaces[54] == "urn:glados:opcua:health"

                def node(field: str):
                    return client.get_node(f"ns=54;s=robot1.{field}")

                assert await node("Status").read_value() == "Unknown"
                assert await node("DataValid").read_value() is False
                assert await node("ErrorCode").read_value() == 1
                assert await node("LastSeen").read_value() is None

                # Legitimate device telemetry marks the equipment online.
                await client.get_node("ns=21;s=R1d_Joi1;").write_value(1.5)
                await bundle.health.refresh_once()
                assert await node("Status").read_value() == "Online"
                assert await node("DataValid").read_value() is True
                assert await node("ErrorCode").read_value() == 0
                assert await node("LastSeen").read_value() is not None
                assert await node("Heartbeat").read_value() >= 1

                # Simulate the configured timeout elapsing (monotonic clock).
                bundle.health._last_seen["robot1"] = time.monotonic() - manifest.server.health.stale_after_seconds - 1
                await bundle.health.refresh_once()
                assert await node("Status").read_value() == "Stale"
                assert await node("DataValid").read_value() is False
                assert await node("ErrorCode").read_value() == 2
                assert "No authorized write" in await node("ErrorMessage").read_value()

                # Recovery: fresh authorized telemetry makes it valid again.
                await client.get_node("ns=21;s=R1d_Joi1;").write_value(2.0)
                await bundle.health.refresh_once()
                assert await node("Status").read_value() == "Online"
                assert await node("DataValid").read_value() is True

                # Health nodes are server-managed and must not accept writes.
                with pytest.raises(ua.uaerrors.UaStatusCodeError):
                    await node("Status").write_value("Online")
        finally:
            if bundle.health is not None:
                await bundle.health.stop()
            bundle.audit.stop()


async def test_health_disabled_by_default(legacy_bundle, legacy_client):
    assert legacy_bundle.health is None
    assert "urn:glados:opcua:health" not in await legacy_client.get_namespace_array()
