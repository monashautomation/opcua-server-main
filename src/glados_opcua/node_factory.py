"""Typed address-space creation from validated configuration.

Only public ``asyncua`` APIs are used.  NodeIds and browse names come from the
manifest; nothing is inferred from a variable name.  Access levels are set by
``Node.set_writable`` exactly as the legacy server did, so the 482 writable and
6 read-only legacy variables keep their observable behaviour.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from asyncua import Server, ua
from asyncua.common.node import Node

from .models import EquipmentSpec, VariableSpec

_logger = logging.getLogger(__name__)


@dataclass
class CreatedEquipment:
    """A created object and its variables, addressable by browse name."""

    spec: EquipmentSpec
    node: Node
    variables: dict[str, Node] = field(default_factory=dict)


async def create_equipment(parent: Node, spec: EquipmentSpec) -> CreatedEquipment:
    """Create one equipment object and its variables under ``parent``.

    The object is created with an explicit NodeId (``ns=<idx>;i=1`` in the
    legacy manifest) so object IDs do not depend on allocation order.  Browse
    names use the legacy namespace index, which for objects equals the object
    namespace and for variables is 0.
    """
    object_node = await parent.add_object(
        ua.NodeId.from_string(spec.node_id),
        ua.QualifiedName(spec.name, spec.browse_namespace if spec.browse_namespace is not None else spec.namespace),
    )
    if spec.description:
        await object_node.write_attribute(
            ua.AttributeIds.Description,
            ua.DataValue(ua.Variant(ua.LocalizedText(spec.description), ua.VariantType.LocalizedText)),
        )

    created = CreatedEquipment(spec=spec, node=object_node)
    for variable in spec.variables:
        created.variables[variable.browse_name] = await create_variable(object_node, variable)
    _logger.debug("Created %s (%s) with %d variables", spec.name, spec.node_id, len(spec.variables))
    return created


async def create_variable(parent: Node, spec: VariableSpec) -> Node:
    """Create a variable with exact NodeId, data type, rank, default and access."""
    node = await parent.add_variable(
        ua.NodeId.from_string(spec.node_id),
        ua.QualifiedName(spec.browse_name, spec.browse_namespace),
        spec.data_type.coerce(spec.default),
        varianttype=spec.data_type.variant_type,
        datatype=ua.NodeId(spec.data_type.data_type_id, 0),
    )
    # ``add_variable`` derives ValueRank from the typed Variant: every legacy
    # variable is a scalar, so ValueRank is -1 and ArrayDimensions is null.
    # The manifest validator rejects non-scalar legacy variables until array
    # support is explicitly introduced.
    if spec.writable:
        await node.set_writable()
    return node


async def create_all(server: Server, specs: list[EquipmentSpec]) -> dict[str, CreatedEquipment]:
    """Create equipment in manifest order, preserving legacy creation order."""
    created: dict[str, CreatedEquipment] = {}
    for spec in specs:
        created[spec.name] = await create_equipment(server.nodes.objects, spec)
    return created
