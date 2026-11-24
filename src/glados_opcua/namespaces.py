"""Exact namespace construction.

Legacy clients address nodes by numeric namespace index (``ns=21``), so indexes
are part of the frozen contract.  ``asyncua.register_namespace`` only appends,
which cannot express the gaps 4-10, 15-20, 25-28, 30, 32-40, 43-50.  This module
builds the complete NamespaceArray explicitly, fills gaps with deterministic
reserved URIs and asserts the final array on every startup.

Index 0 is the OPC UA standard namespace.  Index 1 is the server application
namespace (legacy default ``urn:freeopcua:python:server``) and also hosts the
legacy ``Operator`` object.  Do not move ``Operator``: clients resolve it by
index.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from asyncua import Server, ua

from .models import NamespaceEntry, NamespaceKind, ServerConfig

_logger = logging.getLogger(__name__)

STANDARD_URI = "http://opcfoundation.org/UA/"
RESERVED_URI = "urn:glados:opcua:reserved:{index}"


@dataclass(frozen=True)
class NamespaceRegistry:
    """The complete NamespaceArray and URI lookup for one server instance."""

    entries: tuple[NamespaceEntry, ...]
    uris: tuple[str, ...]

    @classmethod
    def build(cls, entries: list[NamespaceEntry], server: ServerConfig) -> NamespaceRegistry:
        health = server.health
        configured = {entry.index: entry for entry in entries}
        if health.enabled:
            if health.namespace in configured:
                raise ValueError(f"health namespace {health.namespace} collides with namespaces.yaml")
            configured[health.namespace] = NamespaceEntry(
                index=health.namespace,
                uri=health.uri,
                kind=NamespaceKind.EQUIPMENT,
                description="Additive health and stale-data nodes",
            )
        max_index = max(configured)
        uris = [RESERVED_URI.format(index=index) for index in range(max_index + 1)]
        for index, entry in configured.items():
            uris[index] = entry.uri
        uris[0] = STANDARD_URI
        if uris[1] != server.application_uri:
            # Namespace 1 is the application URI; namespaces.yaml must agree.
            raise ValueError(
                f"namespace 1 URI {uris[1]!r} does not match application_uri {server.application_uri!r}"
            )
        if len(set(uris)) != len(uris):
            duplicates = {uri for uri in uris if uris.count(uri) > 1}
            raise ValueError(f"duplicate namespace URIs: {sorted(duplicates)}")
        return cls(entries=tuple(configured[index] for index in sorted(configured)), uris=tuple(uris))

    async def apply(self, server: Server) -> None:
        """Write the NamespaceArray and verify it survived the write."""
        await server.set_application_uri(self.uris[1])
        node = server.nodes.namespace_array
        await node.write_value(ua.Variant(list(self.uris), ua.VariantType.String))
        actual = await node.read_value()
        if tuple(actual) != self.uris:
            raise RuntimeError(f"NamespaceArray mismatch after write: expected {self.uris!r}, got {actual!r}")
        _logger.info(
            "Registered %d namespace indexes (max %d, health=%s)",
            len(self.uris),
            len(self.uris) - 1,
            any(entry.description == "Additive health and stale-data nodes" for entry in self.entries),
        )

    def index_of(self, uri: str) -> int:
        return self.uris.index(uri)

    def reserved_indexes(self) -> list[int]:
        reserved = {entry.index for entry in self.entries}
        return [index for index in range(len(self.uris)) if index not in reserved]
