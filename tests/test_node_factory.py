"""Exact wire types, values, NodeIDs and access levels created from config."""

from __future__ import annotations

from asyncua import ua

INT32 = ua.NodeId(ua.ObjectIds.Int32)
INT64 = ua.NodeId(ua.ObjectIds.Int64)
DOUBLE = ua.NodeId(ua.ObjectIds.Double)
BOOLEAN = ua.NodeId(ua.ObjectIds.Boolean)
BYTESTRING = ua.NodeId(ua.ObjectIds.ByteString)


async def test_int64_inference_is_preserved(legacy_client):
    """Bare legacy integers became Int64, not Int32. Do not "fix" them."""
    for node_id in ("ns=23;s=R3d_BaseA;", "ns=31;s=C1d_Img_h;", "ns=31;s=C1d_Img_w;", "ns=53;s=RGBc_ProgID;"):
        node = legacy_client.get_node(node_id)
        assert await node.read_data_type() == INT64
        assert await node.read_value() == 0


async def test_int32_and_double_are_exact(legacy_client):
    assert await legacy_client.get_node("ns=21;s=R1d_Joi1;").read_data_type() == DOUBLE
    assert await legacy_client.get_node("ns=21;s=R1d_Joi1;").read_value() == -15.0
    assert await legacy_client.get_node("ns=22;s=R2c_int1;").read_data_type() == INT32
    assert await legacy_client.get_node("ns=2;s=LabCount").read_data_type() == INT32
    assert await legacy_client.get_node("ns=1;s=wrapperDisconnect").read_data_type() == BOOLEAN


async def test_bytestring_default_is_bytes(legacy_client):
    node = legacy_client.get_node("ns=31;s=C1d_Img;")
    assert await node.read_data_type() == BYTESTRING
    assert await node.read_value() == b"\x00\x00\x00\x00"
    assert await legacy_client.get_node("ns=53;s=RGBc_Img;").read_value() == b"\x00\x00\x00\x00"


async def test_access_levels_match_legacy(legacy_client):
    writable = await legacy_client.get_node("ns=21;s=R1c_Start;").read_attribute(ua.AttributeIds.AccessLevel)
    assert writable.Value.Value & ua.AccessLevel.CurrentWrite.mask
    read_only = await legacy_client.get_node("ns=22;s=R2c_int4;").read_attribute(ua.AttributeIds.AccessLevel)
    assert not read_only.Value.Value & ua.AccessLevel.CurrentWrite.mask
    for name in ("R2c_int4", "R2c_int5", "R2c_int6", "R2c_Bool1", "R2c_Bool2", "R2c_Bool3"):
        node = legacy_client.get_node(f"ns=22;s={name};")
        level = await node.read_attribute(ua.AttributeIds.UserAccessLevel)
        assert not level.Value.Value & ua.AccessLevel.CurrentWrite.mask


async def test_nodeids_and_browse_names_are_literal(legacy_client):
    assert await legacy_client.get_node("ns=2;s=LabCount").read_browse_name() == ua.QualifiedName("LabCount", 0)
    assert await legacy_client.get_node("ns=21;s=R1d_Joi1;").read_browse_name() == ua.QualifiedName("R1d_Joi1", 0)
    assert await legacy_client.get_node("ns=11;s=P1d_APIresp").read_browse_name() == ua.QualifiedName("P1d_APIresp", 0)
    # The object browse name uses the object namespace, as in the legacy server.
    assert await legacy_client.get_node("ns=11;i=1").read_browse_name() == ua.QualifiedName("Printer1", 11)
    assert await legacy_client.get_node("ns=1;i=2001").read_browse_name() == ua.QualifiedName("Operator", 1)


async def test_scalar_value_rank(legacy_client):
    attribute = await legacy_client.get_node("ns=21;s=R1d_Joi1;").read_attribute(ua.AttributeIds.ValueRank)
    assert attribute.Value.Value == -1


async def test_glove_duplicate_names_are_namespaced(legacy_client):
    left = await legacy_client.get_node("ns=51;s=Gd_LockStatus;").read_browse_name()
    right = await legacy_client.get_node("ns=52;s=Gd_LockStatus;").read_browse_name()
    assert left == right == ua.QualifiedName("Gd_LockStatus", 0)
    assert (await legacy_client.get_node("ns=51;i=1").read_browse_name()).Name == "Glove 1 (Left)"
    assert (await legacy_client.get_node("ns=52;i=1").read_browse_name()).Name == "Glove 2 (Right)"
