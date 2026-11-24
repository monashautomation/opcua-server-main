"""Configuration must fail before startup on every ambiguity or typo."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from glados_opcua.models import Profile
from glados_opcua.validation import ConfigurationError, load_manifest

from .conftest import copy_config, manifest_for, read_yaml, write_yaml


def test_shipped_configuration_is_complete():
    manifest = manifest_for(Path("config"))
    assert manifest.summary() == {
        "endpoint": "opc.tcp://0.0.0.0:4840/server/",
        "health": False,
        "namespaces": 19,
        "objects": 18,
        "permissions_enforced": False,
        "profile": "legacy",
        "server_name": "DTL Local OPC UA Server Test",
        "variables": 488,
        "writable": 482,
    }


def _first_device(root: Path) -> tuple[Path, dict]:
    path = next((root / "devices").glob("*.yaml"))
    data = read_yaml(path)
    return path, data


def test_duplicate_node_id_rejected(tmp_path):
    root = copy_config(tmp_path)
    _, data = _first_device(root)
    source = data["equipment"][0]
    namespace = source["namespace"]
    duplicate = {
        "name": source["name"] + "-copy",
        "namespace": namespace,
        "node_id": f"ns={namespace};i=9999",
        "browse_namespace": namespace,
        "variables": [dict(source["variables"][0])],
    }
    (root / "devices" / "99_duplicate.yaml").write_text(
        "config_version: 1\nequipment:\n  - " + json.dumps(duplicate) + "\n", encoding="utf-8"
    )
    with pytest.raises(ConfigurationError, match="duplicate NodeId"):
        load_manifest(root, environ={})


def test_undefined_namespace_rejected(tmp_path):
    root = copy_config(tmp_path)
    path, data = _first_device(root)
    old = data["equipment"][0]["namespace"]
    data["equipment"][0]["namespace"] = 90
    data["equipment"][0]["node_id"] = data["equipment"][0]["node_id"].replace(f"ns={old};", "ns=90;")
    for variable in data["equipment"][0]["variables"]:
        variable["node_id"] = variable["node_id"].replace(f"ns={old};", "ns=90;")
    write_yaml(path, data)
    with pytest.raises(ConfigurationError, match="undefined namespace"):
        load_manifest(root, environ={})


def test_malformed_data_type_rejected(tmp_path):
    root = copy_config(tmp_path)
    path, data = _first_device(root)
    data["equipment"][0]["variables"][0]["data_type"] = "Floaty"
    write_yaml(path, data)
    with pytest.raises(ConfigurationError, match="data_type"):
        load_manifest(root, environ={})


def test_default_must_match_type(tmp_path):
    root = copy_config(tmp_path)
    path, data = _first_device(root)
    variable = next(v for v in data["equipment"][0]["variables"] if v["data_type"] == "Int32")
    variable["default"] = "zero"
    write_yaml(path, data)
    with pytest.raises(ConfigurationError, match="Int32 default"):
        load_manifest(root, environ={})


def test_array_variables_rejected(tmp_path):
    root = copy_config(tmp_path)
    path, data = _first_device(root)
    data["equipment"][0]["variables"][0]["value_rank"] = 1
    write_yaml(path, data)
    with pytest.raises(ConfigurationError, match="scalar variables"):
        load_manifest(root, environ={})


def test_unknown_keys_rejected(tmp_path):
    root = copy_config(tmp_path)
    path, data = _first_device(root)
    data["equipment"][0]["unexpected"] = True
    write_yaml(path, data)
    with pytest.raises(ConfigurationError, match="Extra inputs"):
        load_manifest(root, environ={})


def test_legacy_requires_explicit_acknowledgement(tmp_path):
    root = copy_config(tmp_path)
    server = read_yaml(root / "server.yaml")
    server["security"]["allow_insecure_legacy"] = False
    write_yaml(root / "server.yaml", server)
    with pytest.raises(ConfigurationError, match="allow_insecure_legacy"):
        load_manifest(root, environ={})


def test_production_rejects_anonymous(tmp_path):
    root = copy_config(tmp_path, profile="production", security={"allow_anonymous": True})
    with pytest.raises(ConfigurationError, match="anonymous"):
        load_manifest(root, environ={})


def test_production_rejects_nosecurity(tmp_path):
    root = copy_config(tmp_path, profile="production", security={"policies": ["NoSecurity"]})
    with pytest.raises(ConfigurationError, match="NoSecurity"):
        load_manifest(root, environ={})


def test_production_requires_users(tmp_path):
    root = copy_config(tmp_path, profile="production", security={"users": []})
    with pytest.raises(ConfigurationError, match="at least one configured user"):
        load_manifest(root, environ={})


def test_production_user_token_must_be_enabled(tmp_path):
    root = copy_config(
        tmp_path,
        profile="production",
        security={
            "identity_tokens": ["Username"],
            "users": [{"username": "cert", "role": "admin", "certificate": "client.pem"}],
        },
    )
    with pytest.raises(ConfigurationError, match="add X509"):
        load_manifest(root, environ={})


def test_production_requires_certificate_paths(tmp_path):
    root = copy_config(
        tmp_path,
        profile="production",
        security={
            "certificate": "",
            "private_key": "",
            "users": [{"username": "admin", "role": "admin", "password_env": "P"}],
        },
    )
    with pytest.raises(ConfigurationError, match="certificate"):
        load_manifest(root, environ={})


def test_legacy_cannot_enforce_permissions(tmp_path):
    root = copy_config(tmp_path, permissions={"enforced": True})
    with pytest.raises(ConfigurationError, match="must set permissions.enforced: false"):
        load_manifest(root, environ={})


def test_environment_overrides_are_validated(tmp_path):
    root = copy_config(tmp_path)
    manifest = load_manifest(root, environ={"GLADOS_SERVER_URL": "opc.tcp://127.0.0.1:9999/other/"})
    assert manifest.server.endpoint == "opc.tcp://127.0.0.1:9999/other/"
    with pytest.raises(ConfigurationError, match="opc.tcp"):
        load_manifest(root, environ={"GLADOS_SERVER_URL": "http://example.com"})
    with pytest.raises(ConfigurationError, match="GLADOS_PROFILE"):
        load_manifest(root, environ={"GLADOS_PROFILE": "staging"})


def test_unknown_permission_role_rejected(tmp_path):
    root = copy_config(tmp_path, permissions={"roles": {"admin": {"write_all": True}, "wizard": {"read": True}}})
    with pytest.raises(ConfigurationError, match="unknown roles"):
        load_manifest(root, environ={})


def test_profile_env_switch_is_not_silently_insecure(tmp_path):
    root = copy_config(tmp_path)
    with pytest.raises(ConfigurationError, match="production"):
        load_manifest(root, environ={"GLADOS_PROFILE": Profile.PRODUCTION.value})
