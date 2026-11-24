"""Additive equipment health and stale-data detection (Phase 6).

The legacy address space is never modified.  When enabled, a separate ``Health``
object is registered in its own namespace:

    Health/<Equipment>.Status       String   Online | Stale | Offline | Unknown
    Health/<Equipment>.Heartbeat    Int32    device-owned writes observed
    Health/<Equipment>.LastSeen     DateTime UTC time of the last authorized write
    Health/<Equipment>.DataValid    Boolean  false until confirmed and while stale
    Health/<Equipment>.ErrorCode    Int32    0 none, 1 no data, 2 stale
    Health/<Equipment>.ErrorMessage String   human-readable detail

Staleness is measured with ``time.monotonic`` (immune to wall-clock changes) and
only authorized device-owned writes count as activity, observed through the public
server PreWrite callback.  Availability starts as ``Unknown``; the server never
pretends a device is healthy before telemetry arrives.

The monitor only publishes state.  It never replays commands or writes legacy
nodes.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from collections.abc import Callable
from datetime import UTC, datetime

from asyncua import Server, ua
from asyncua.common.callback import CallbackType
from asyncua.common.node import Node

from .equipment_registry import EquipmentRegistry
from .models import DataType, HealthConfig, WriterRole

_logger = logging.getLogger(__name__)

STATUS_UNKNOWN = "Unknown"
STATUS_ONLINE = "Online"
STATUS_STALE = "Stale"

ERROR_NONE = 0
ERROR_NO_DATA = 1
ERROR_STALE = 2

_FIELDS: tuple[tuple[str, DataType, object], ...] = (
    ("Status", DataType.String, STATUS_UNKNOWN),
    ("Heartbeat", DataType.Int32, 0),
    ("LastSeen", DataType.DateTime, None),
    ("DataValid", DataType.Boolean, False),
    ("ErrorCode", DataType.Int32, ERROR_NO_DATA),
    ("ErrorMessage", DataType.String, "No telemetry received since server start"),
)


def _variant_type(value: object, data_type: DataType) -> ua.VariantType:
    """Use a Null variant for "no data yet"; DateTime cannot carry Python None."""
    return ua.VariantType.Null if value is None else data_type.variant_type


class HealthMonitor:
    """Publish per-equipment health without touching the legacy interface."""

    def __init__(
        self,
        registry: EquipmentRegistry,
        config: HealthConfig,
        server: Server,
        *,
        clock: Callable[[], float] = time.monotonic,
        wall_clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ):
        self._registry = registry
        self._config = config
        self._server = server
        self._clock = clock
        self._wall_clock = wall_clock
        self._last_seen: dict[str, float] = {}
        self._last_seen_wall: dict[str, datetime] = {}
        self._heartbeats: dict[str, int] = {}
        self._nodes: dict[str, dict[str, Node]] = {}
        self._published: dict[tuple[str, str], object] = {}
        self._task: asyncio.Task | None = None
        self._running = False
        self.health_node: Node | None = None

    async def start(self) -> None:
        await self._create_nodes()
        self._running = True
        self._server.iserver.subscribe_server_callback(CallbackType.PreWrite, self._on_write)
        await self._refresh()
        self._task = asyncio.create_task(self._poll_loop(), name="glados-health")

    async def stop(self) -> None:
        self._running = False
        if self._task is not None:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
        self._server.iserver.unsubscribe_server_callback(CallbackType.PreWrite, self._on_write)

    async def _create_nodes(self) -> None:
        index = self._config.namespace
        self.health_node = await self._server.nodes.objects.add_object(
            ua.NodeId.from_string(f"ns={index};s=Health"),
            ua.QualifiedName("Health", index),
        )
        for equipment in self._registry.equipment:
            children: dict[str, Node] = {}
            for field_name, data_type, initial in _FIELDS:
                node = await self.health_node.add_variable(
                    ua.NodeId.from_string(f"ns={index};s={equipment}.{field_name}"),
                    ua.QualifiedName(f"{equipment}.{field_name}", index),
                    initial,
                    varianttype=_variant_type(initial, data_type),
                    datatype=ua.NodeId(data_type.data_type_id, 0),
                )
                await node.write_attribute(
                    ua.AttributeIds.ValueRank,
                    ua.DataValue(ua.Variant(-1, ua.VariantType.Int32)),
                )
                children[field_name] = node
                self._published[(equipment, field_name)] = initial
            self._nodes[equipment] = children
        _logger.info("Health namespace ready at index %d (%d devices)", index, len(self._nodes))

    async def _on_write(self, event, callback_service) -> None:
        params = event.request_params
        if params is None:
            return
        for item in params.NodesToWrite:
            spec = self._registry.variable_specs.get(item.NodeId)
            if spec is None or spec.writer is not WriterRole.DEVICE:
                # Controller commands are not evidence that a device is alive.
                continue
            owner = self._registry.owner(item.NodeId)
            if owner is not None:
                self._last_seen[owner] = self._clock()
                self._last_seen_wall[owner] = self._wall_clock()
                self._heartbeats[owner] = self._heartbeats.get(owner, 0) + 1

    async def _poll_loop(self) -> None:
        while self._running:
            await asyncio.sleep(self._config.poll_interval_seconds)
            try:
                await self._refresh()
            except Exception:
                _logger.exception("Health refresh failed")

    def status_for(self, equipment: str) -> tuple[str, bool, int, str]:
        """Return ``(status, data_valid, error_code, message)`` for one device."""
        seen = self._last_seen.get(equipment)
        if seen is None:
            return STATUS_UNKNOWN, False, ERROR_NO_DATA, "No telemetry received since server start"
        age = self._clock() - seen
        if age > self._config.stale_after_seconds:
            return (
                STATUS_STALE,
                False,
                ERROR_STALE,
                f"No authorized write for {age:.1f}s (limit {self._config.stale_after_seconds:.1f}s)",
            )
        return STATUS_ONLINE, True, ERROR_NONE, ""

    async def _refresh(self) -> None:
        for equipment, nodes in self._nodes.items():
            status, valid, error_code, message = self.status_for(equipment)
            values: dict[str, object] = {
                "Status": status,
                "Heartbeat": self._heartbeats.get(equipment, 0),
                "LastSeen": self._last_seen_wall.get(equipment),
                "DataValid": valid,
                "ErrorCode": error_code,
                "ErrorMessage": message,
            }
            for field_name, value in values.items():
                key = (equipment, field_name)
                if self._published.get(key) == value:
                    continue
                node = nodes[field_name]
                data_type = next(dt for name, dt, _ in _FIELDS if name == field_name)
                await node.write_value(ua.Variant(value, _variant_type(value, data_type)))
                self._published[key] = value

    async def refresh_once(self) -> None:
        """Force a status refresh; exposed for deterministic tests."""
        await self._refresh()
