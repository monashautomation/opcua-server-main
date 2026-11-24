"""Frozen legacy interface: static source vs. golden runtime manifest vs. v2.

This is the release gate.  The static extraction must match the runtime export
used to generate configuration, and the new server must reproduce that export
field-for-field for the 18 legacy objects, 488 variables and their references.
"""

from __future__ import annotations

import json

import pytest
from asyncua import ua

from glados_opcua.legacy_parser import differences, parse_legacy_source
from scripts.export_nodes import export

from .conftest import REPO

GOLDEN = REPO / "tests" / "fixtures" / "legacy_nodes.json"
SOURCE = REPO / "legacy" / "server_opcua.py"
COMPARED_ATTRIBUTES = ("DataType", "ValueRank", "AccessLevel", "UserAccessLevel", "Value")


def test_static_extraction_matches_runtime_baseline():
    objects = parse_legacy_source(SOURCE)
    assert len(objects) == 18
    assert sum(len(item.variables) for item in objects) == 488
    assert sum(1 for item in objects for variable in item.variables if variable.writable) == 482
    assert differences(objects, GOLDEN) == []


def test_golden_manifest_is_complete():
    data = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert len([n for n in data["nodes"] if n["node_class"] == "Object"]) == 18
    assert len([n for n in data["nodes"] if n["node_class"] == "Variable"]) == 488


def _custom_nodes(manifest: dict) -> dict[str, dict]:
    nodes = manifest["nodes"]
    roots = {
        node["node_id"]
        for node in nodes
        if node["parent"] == "i=85"
        and node["node_class"] == "Object"
        and ua.NodeId.from_string(node["node_id"]).NamespaceIndex >= 1
    }
    return {node["node_id"]: node for node in nodes if node["node_id"] in roots or node["parent"] in roots}


async def test_address_space_matches_golden_manifest(legacy_bundle):
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    actual = await export(legacy_bundle.manifest.server.endpoint)
    expected_nodes = _custom_nodes(golden)
    actual_nodes = _custom_nodes(actual)

    assert set(actual_nodes) == set(expected_nodes)
    for node_id, expected in expected_nodes.items():
        found = actual_nodes[node_id]
        assert found["browse_name"] == expected["browse_name"], node_id
        assert found["display_name"] == expected["display_name"], node_id
        assert found["node_class"] == expected["node_class"], node_id
        assert found["parent"] == expected["parent"], node_id
        assert found["references"] == expected["references"], node_id
        for attribute in COMPARED_ATTRIBUTES:
            assert found["attributes"].get(attribute) == expected["attributes"].get(attribute), (node_id, attribute)


async def test_endpoint_name_and_namespace_prefix(legacy_bundle, legacy_client):
    namespaces = await legacy_client.get_namespace_array()
    assert namespaces[:2] == ["http://opcfoundation.org/UA/", "urn:freeopcua:python:server"]
    assert len(namespaces) == 54
    assert legacy_bundle.server.name == "DTL Local OPC UA Server Test"
    assert legacy_bundle.manifest.server.endpoint.endswith("/server/")


async def test_no_health_namespace_in_strict_parity_mode(legacy_client):
    namespaces = await legacy_client.get_namespace_array()
    assert "urn:glados:opcua:health" not in namespaces
    # Health index 54 must not exist when disabled.
    with pytest.raises(ua.uaerrors.UaStatusCodeError):
        await legacy_client.get_node("ns=54;s=Health").read_browse_name()
