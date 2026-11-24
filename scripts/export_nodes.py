"""Export an OPC UA server address space to a deterministic JSON manifest.

Usage: python scripts/export_nodes.py opc.tcp://host:port/server/ out.json
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime
from enum import Enum
from typing import Any

from asyncua import Client, ua

SKIP_ATTRIBUTES = {
    ua.AttributeIds.NodeId,
    ua.AttributeIds.NodeClass,
    ua.AttributeIds.BrowseName,
    ua.AttributeIds.DisplayName,
    ua.AttributeIds.Description,
    ua.AttributeIds.WriteMask,
    ua.AttributeIds.UserWriteMask,
}


def normalize(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"__bytes__": value.hex()}
    if isinstance(value, datetime):
        return {"__datetime__": value.isoformat()}
    if isinstance(value, ua.NodeId):
        return {"__nodeid__": value.to_string()}
    if isinstance(value, ua.QualifiedName):
        return {"__qname__": [value.NamespaceIndex, value.Name]}
    if isinstance(value, ua.LocalizedText):
        return value.Text
    if isinstance(value, Enum):
        return value.name
    if isinstance(value, (list, tuple)):
        return [normalize(v) for v in value]
    if isinstance(value, dict):
        return {str(k): normalize(v) for k, v in sorted(value.items())}
    if isinstance(value, (bool, int, float, str)) or value is None:
        return value
    return {"__repr__": repr(value)}


def variant_manifest(value: ua.Variant | None, status: ua.StatusCode | None) -> dict[str, Any]:
    if value is None:
        return {"type": None, "value": None, "status": status.name if status else None}
    return {
        "type": value.VariantType.name,
        "value": normalize(value.Value),
        "status": status.name if status else None,
    }


async def export(url: str) -> dict[str, Any]:
    async with Client(url=url) as client:
        ns_array = await client.nodes.namespace_array.read_value()
        objects = client.nodes.objects

        async def visit(node, parent: str) -> list[dict[str, Any]]:
            browse_name = await node.read_browse_name()
            entry: dict[str, Any] = {
                "node_id": node.nodeid.to_string(),
                "browse_name": {"name": browse_name.Name, "namespace": browse_name.NamespaceIndex},
                "display_name": (await node.read_display_name()).Text,
                "node_class": (await node.read_node_class()).name,
                "parent": parent,
            }
            attributes: dict[str, Any] = {}
            for attr in ua.AttributeIds:
                if attr in SKIP_ATTRIBUTES:
                    continue
                try:
                    dv = await node.read_attribute(attr, raise_on_bad_status=False)
                except Exception:  # attribute not implemented by the node
                    continue
                if dv is None or dv.Value is None:
                    continue
                if dv.StatusCode is not None and not dv.StatusCode.is_good():
                    continue
                attributes[attr.name] = variant_manifest(dv.Value, dv.StatusCode)
            entry["attributes"] = attributes
            entry["references"] = [
                {
                    "type": ref.ReferenceTypeId.to_string(),
                    "is_forward": ref.IsForward,
                    "target": ref.NodeId.to_string(),
                }
                for ref in sorted(await node.get_references(), key=lambda r: r.NodeId.to_string())
            ]
            entries = [entry]
            if entry["node_class"] == "Object":
                for child in sorted(await node.get_children(), key=lambda c: c.nodeid.to_string()):
                    entries.extend(await visit(child, node.nodeid.to_string()))
            return entries

        nodes: list[dict[str, Any]] = []
        for child in sorted(await objects.get_children(), key=lambda c: c.nodeid.to_string()):
            nodes.extend(await visit(child, objects.nodeid.to_string()))
        return {
            "endpoint": url,
            "namespace_array": ns_array,
            "nodes": nodes,
        }


async def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    manifest = await export(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    asyncio.run(main())
