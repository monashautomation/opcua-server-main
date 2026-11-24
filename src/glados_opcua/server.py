"""Server assembly, startup ordering and graceful shutdown.

Startup order is deliberate and must not be reordered casually:

    load configuration -> validate -> init server -> configure security ->
    register namespaces -> create equipment -> attach health/audit ->
    listen -> wait for SIGINT/SIGTERM -> stop health -> stop server

Binding is separate from the advertised endpoint so Docker/NAT clients receive
a reachable URL.  ``GLADOS_SERVER_URL`` remains the legacy-compatible override.
"""

from __future__ import annotations

import asyncio
import logging
import signal
from dataclasses import dataclass
from urllib.parse import urlparse

from asyncua import Server

from .audit import AuditLogger
from .equipment_registry import EquipmentRegistry
from .health import HealthMonitor
from .models import Manifest
from .namespaces import NamespaceRegistry
from .permissions import build_ruleset
from .security import configure_security

_logger = logging.getLogger(__name__)


@dataclass
class ServerBundle:
    manifest: Manifest
    server: Server
    registry: EquipmentRegistry
    namespaces: NamespaceRegistry
    health: HealthMonitor | None
    audit: AuditLogger


async def build_server(manifest: Manifest) -> ServerBundle:
    """Build the address space and configure security without listening."""
    ruleset = build_ruleset(manifest)
    server = Server()
    await server.init()
    server.set_endpoint(manifest.server.endpoint)
    server.set_server_name(manifest.server.name)
    await server.set_application_uri(manifest.server.application_uri)

    endpoint = urlparse(manifest.server.endpoint)
    bind_address = manifest.server.bind_address or endpoint.hostname
    bind_port = manifest.server.bind_port or endpoint.port
    if (bind_address, bind_port) != (endpoint.hostname, endpoint.port):
        server.socket_address = (bind_address, bind_port)

    await configure_security(server, manifest, ruleset)
    namespaces = NamespaceRegistry.build(manifest.namespaces.namespaces, manifest.server)
    await namespaces.apply(server)

    registry = await EquipmentRegistry.build(server, manifest)
    health = None
    if manifest.server.health.enabled:
        health = HealthMonitor(registry, manifest.server.health, server)
        await health.start()
    audit = AuditLogger(server)
    audit.start()
    return ServerBundle(
        manifest=manifest,
        server=server,
        registry=registry,
        namespaces=namespaces,
        health=health,
        audit=audit,
    )


async def run(manifest: Manifest, *, handle_signals: bool = True) -> None:
    """Serve until SIGINT/SIGTERM, then stop health and the OPC UA server."""
    bundle = await build_server(manifest)
    stop_event = asyncio.Event()
    installed: list[signal.Signals] = []
    if handle_signals:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, stop_event.set)
                installed.append(sig)
            except NotImplementedError:  # pragma: no cover - Windows
                _logger.warning("Signal %s is not supported on this platform", sig)

    summary = manifest.summary()
    loop = asyncio.get_running_loop()
    bind_address, bind_port = bundle.server.socket_address or (
        urlparse(manifest.server.endpoint).hostname,
        urlparse(manifest.server.endpoint).port,
    )
    try:
        async with bundle.server:
            try:
                _logger.info(
                    "OPC UA server listening endpoint=%s bind=%s:%s name=%r profile=%s objects=%d variables=%d",
                    manifest.server.endpoint,
                    bind_address,
                    bind_port,
                    manifest.server.name,
                    manifest.server.profile.value,
                    summary["objects"],
                    summary["variables"],
                )
                if manifest.server.profile.value == "legacy":
                    _logger.warning(
                        "Legacy compatibility profile is active: anonymous access and unauthenticated "
                        "writes are enabled. Use only on an isolated network."
                    )
                await stop_event.wait()
                _logger.info("Shutdown signal received")
            finally:
                if bundle.health is not None:
                    await bundle.health.stop()
                bundle.audit.stop()
    finally:
        for sig in installed:
            loop.remove_signal_handler(sig)
