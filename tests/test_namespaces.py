"""Namespace indexes are part of the wire contract and must not drift."""

from __future__ import annotations

from pathlib import Path

import pytest

from glados_opcua.namespaces import RESERVED_URI, STANDARD_URI, NamespaceRegistry
from glados_opcua.validation import ConfigurationError, load_manifest

from .conftest import copy_config, manifest_for, read_yaml, write_yaml


def test_exact_legacy_indexes(tmp_path: Path):
    manifest = manifest_for(copy_config(tmp_path))
    registry = NamespaceRegistry.build(manifest.namespaces.namespaces, manifest.server)
    assert len(registry.uris) == 54
    assert registry.uris[0] == STANDARD_URI
    assert registry.uris[1] == "urn:freeopcua:python:server"
    assert registry.uris[2] == "urn:glados:opcua:communication"
    assert registry.uris[21] == "urn:glados:opcua:robot1"
    assert registry.uris[53] == "urn:glados:opcua:rgb-leds"
    assert registry.uris[4] == RESERVED_URI.format(index=4)
    assert registry.uris[30] == RESERVED_URI.format(index=30)
    assert registry.uris[40] == RESERVED_URI.format(index=40)
    assert len(set(registry.uris)) == len(registry.uris)


def test_health_namespace_is_additive(tmp_path: Path):
    manifest = manifest_for(copy_config(tmp_path, health=True))
    registry = NamespaceRegistry.build(manifest.namespaces.namespaces, manifest.server)
    assert len(registry.uris) == 55
    assert registry.uris[54] == "urn:glados:opcua:health"
    assert registry.index_of("urn:glados:opcua:health") == 54


def test_duplicate_namespace_index_rejected(tmp_path: Path):
    root = copy_config(tmp_path)
    data = read_yaml(root / "namespaces.yaml")
    data["namespaces"].append(dict(data["namespaces"][-1]))
    write_yaml(root / "namespaces.yaml", data)
    with pytest.raises(ConfigurationError, match="duplicate namespace indexes"):
        load_manifest(root, environ={})


def test_application_uri_mismatch_rejected(tmp_path: Path):
    root = copy_config(tmp_path)
    server = read_yaml(root / "server.yaml")
    server["application_uri"] = "urn:example:changed"
    write_yaml(root / "server.yaml", server)
    with pytest.raises(ConfigurationError, match="does not match"):
        load_manifest(root, environ={})


async def test_namespace_array_is_written(legacy_bundle, legacy_client):
    registry = legacy_bundle.namespaces
    assert await legacy_client.get_namespace_array() == list(registry.uris)
