"""Role matrix and service-boundary ruleset behaviour."""

from __future__ import annotations

from pathlib import Path

from asyncua import ua
from asyncua.common.utils import Buffer
from asyncua.crypto.permission_rules import User
from asyncua.crypto.permission_rules import UserRole as UARole
from asyncua.ua.ua_binary import struct_to_binary

from glados_opcua.models import Profile
from glados_opcua.permissions import GladosPermissionRuleset, LegacyRoleRuleset, PermissionMatrix

from .conftest import copy_config, manifest_for

USERS = [
    {"username": "admin", "role": "admin", "password_env": "P1"},
    {"username": "ctrl", "role": "controller", "password_env": "P2"},
    {"username": "dev1", "role": "device", "password_env": "P3", "equipment": ["robot1"]},
    {"username": "mon", "role": "monitor", "password_env": "P4"},
]


def matrix(tmp_path: Path) -> PermissionMatrix:
    config = copy_config(
        tmp_path,
        profile=Profile.PRODUCTION.value,
        security={"certificate": "unused.pem", "private_key": "unused.key", "users": USERS},
    )
    return PermissionMatrix(manifest_for(config))


def test_role_matrix_ownership(tmp_path: Path):
    permissions = matrix(tmp_path)
    start = ua.NodeId.from_string("ns=21;s=R1c_Start;")
    telemetry = ua.NodeId.from_string("ns=21;s=R1d_Joi1;")
    other_device = ua.NodeId.from_string("ns=22;s=R2d_Joi1;")
    read_only = ua.NodeId.from_string("ns=22;s=R2c_int4;")

    assert permissions.can_write("admin", start)
    assert permissions.can_write("admin", telemetry)
    assert not permissions.can_write("admin", read_only)
    assert permissions.can_write("ctrl", start)
    assert not permissions.can_write("ctrl", telemetry)
    assert permissions.can_write("dev1", telemetry)
    assert not permissions.can_write("dev1", other_device)
    assert not permissions.can_write("dev1", start)
    assert not permissions.can_write("mon", telemetry)
    assert permissions.can_read("mon", telemetry)
    assert not permissions.can_write("unknown", telemetry)


def test_denied_pattern_wins(tmp_path: Path):
    config = copy_config(
        tmp_path,
        profile=Profile.PRODUCTION.value,
        security={"certificate": "unused.pem", "private_key": "unused.key", "users": USERS},
        permissions={"denied": ["ns=21;s=R1d_*"]},
    )
    permissions = PermissionMatrix(manifest_for(config))
    assert not permissions.can_write("dev1", ua.NodeId.from_string("ns=21;s=R1d_Joi1;"))
    assert not permissions.can_read("mon", ua.NodeId.from_string("ns=21;s=R1d_Joi1;"))


def _write_params(*nodes: tuple[str, object]) -> Buffer:
    params = ua.WriteParameters()
    params.NodesToWrite = [
        ua.WriteValue(
            NodeId_=ua.NodeId.from_string(node_id),
            AttributeId=ua.AttributeIds.Value,
            Value=ua.DataValue(ua.Variant(value)),
        )
        for node_id, value in nodes
    ]
    return Buffer(struct_to_binary(params))


def test_ruleset_allows_and_denies_writes(tmp_path: Path):
    ruleset = GladosPermissionRuleset(matrix(tmp_path))
    write_type = ua.NodeId(ua.ObjectIds.WriteRequest_Encoding_DefaultBinary)

    assert ruleset.check_validity(User(UARole.User, "ctrl"), write_type, _write_params(("ns=21;s=R1c_Start;", True)))
    assert not ruleset.check_validity(
        User(UARole.User, "ctrl"), write_type, _write_params(("ns=21;s=R1d_Joi1;", 1.0))
    )
    # A batch with one unauthorized node is rejected as a whole.
    assert not ruleset.check_validity(
        User(UARole.User, "ctrl"),
        write_type,
        _write_params(("ns=21;s=R1c_Start;", True), ("ns=21;s=R1d_Joi1;", 1.0)),
    )


def test_ruleset_denies_calls_and_node_management(tmp_path: Path):
    ruleset = GladosPermissionRuleset(matrix(tmp_path))
    assert not ruleset.check_validity(
        User(UARole.User, "admin"), ua.NodeId(ua.ObjectIds.CallRequest_Encoding_DefaultBinary), Buffer(b"")
    )
    assert not ruleset.check_validity(
        User(UARole.User, "ctrl"), ua.NodeId(ua.ObjectIds.AddNodesRequest_Encoding_DefaultBinary), Buffer(b"")
    )
    assert ruleset.check_validity(
        User(UARole.User, "admin"), ua.NodeId(ua.ObjectIds.AddNodesRequest_Encoding_DefaultBinary), Buffer(b"")
    )


def test_legacy_ruleset_preserves_anonymous_access():
    ruleset = LegacyRoleRuleset()
    write_type = ua.NodeId(ua.ObjectIds.WriteRequest_Encoding_DefaultBinary)
    anonymous = User(UARole.Anonymous, "anonymous")
    assert ruleset.check_validity(anonymous, write_type, _write_params(("ns=21;s=R1c_Start;", True)))
    assert not ruleset.check_validity(
        anonymous, ua.NodeId(ua.ObjectIds.AddNodesRequest_Encoding_DefaultBinary), Buffer(b"")
    )
