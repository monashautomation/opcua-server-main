"""Protocol behaviour: read/write, subscriptions, reconnect and safe restart."""

from __future__ import annotations

import asyncio
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

from asyncua import Client, ua

from glados_opcua.server import build_server

from .conftest import copy_config, free_port, manifest_for


class CollectingHandler:
    def __init__(self) -> None:
        self.values: list[object] = []

    def datachange_notification(self, node, value, data) -> None:
        self.values.append(value)


async def test_read_write_and_subscription(legacy_bundle):
    async with Client(url=legacy_bundle.manifest.server.endpoint) as client:
        node = client.get_node("ns=21;s=R1c_Start;")
        await node.write_value(True)
        assert await node.read_value() is True

        handler = CollectingHandler()
        subscription = await client.create_subscription(100, handler)
        await subscription.subscribe_data_change(node)
        for _ in range(50):
            if handler.values:
                break
            await asyncio.sleep(0.1)
        assert handler.values, "subscription did not publish its initial value"

        await node.write_value(False)
        for _ in range(50):
            if handler.values[-1] is False:
                break
            await asyncio.sleep(0.1)
        assert handler.values[-1] is False
        await subscription.delete()


async def test_reconnect_keeps_written_value(legacy_bundle):
    for _ in range(2):
        async with Client(url=legacy_bundle.manifest.server.endpoint) as client:
            node = client.get_node("ns=21;s=R1c_ProgID;")
            if _ == 0:
                await node.write_value(42, ua.VariantType.Int32)
            else:
                assert await node.read_value() == 42


async def test_bind_address_can_differ_from_advertised_endpoint(tmp_path: Path):
    advertised = free_port()
    bind = free_port()
    config_dir = copy_config(
        tmp_path,
        url=f"opc.tcp://127.0.0.1:{advertised}/server/",
        server={"bind_address": "127.0.0.1", "bind_port": bind},
    )
    manifest = manifest_for(config_dir)
    bundle = await build_server(manifest)
    assert bundle.server.socket_address == ("127.0.0.1", bind)
    async with bundle.server:
        try:
            async with Client(url=f"opc.tcp://127.0.0.1:{bind}/server/") as client:
                assert await client.get_node("ns=21;s=R1c_Start;").read_value() is False
        finally:
            bundle.audit.stop()


async def test_restart_does_not_replay_commands(tmp_path: Path):
    """Commands are not persisted; a restart starts from approved defaults."""
    config_dir = copy_config(tmp_path)
    manifest = manifest_for(config_dir)
    bundle = await build_server(manifest)
    async with bundle.server:
        try:
            async with Client(url=manifest.server.endpoint) as client:
                await client.get_node("ns=21;s=R1c_Start;").write_value(True)
                assert await client.get_node("ns=21;s=R1c_Start;").read_value() is True
        finally:
            bundle.audit.stop()

    restarted = await build_server(manifest)
    async with restarted.server:
        try:
            async with Client(url=manifest.server.endpoint) as client:
                assert await client.get_node("ns=21;s=R1c_Start;").read_value() is False
        finally:
            restarted.audit.stop()


def _wait_for_port(port: int, timeout: float = 15.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.1)
    raise TimeoutError(f"server did not listen on {port}")


def test_sigterm_shuts_down_cleanly(tmp_path: Path):
    port = free_port()
    config_dir = copy_config(tmp_path, url=f"opc.tcp://127.0.0.1:{port}/server/")
    env = {**os.environ, "GLADOS_CONFIG_DIR": str(config_dir)}
    env.pop("GLADOS_SERVER_URL", None)
    process = subprocess.Popen(
        [sys.executable, "-m", "glados_opcua"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
    try:
        _wait_for_port(port)
        process.terminate()
        output, _ = process.communicate(timeout=20)
    finally:
        if process.poll() is None:
            process.kill()
    assert process.returncode == 0
    assert "Shutdown signal received" in output
