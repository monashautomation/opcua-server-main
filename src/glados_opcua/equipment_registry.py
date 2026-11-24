"""Built equipment registry and NodeId ownership lookup.

The registry is the single place that knows which equipment owns a NodeId.  It
is built once during startup and used by permissions and health monitoring; it
contains no hardware logic.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from asyncua import Server, ua
from asyncua.common.node import Node

from .models import Manifest, VariableSpec
from .node_factory import CreatedEquipment, create_all

_logger = logging.getLogger(__name__)


@dataclass
class EquipmentRegistry:
    manifest: Manifest
    equipment: dict[str, CreatedEquipment]
    variable_specs: dict[ua.NodeId, VariableSpec]
    node_owner: dict[ua.NodeId, str]

    @classmethod
    async def build(cls, server: Server, manifest: Manifest) -> EquipmentRegistry:
        created = await create_all(server, manifest.equipment)
        variable_specs: dict[ua.NodeId, VariableSpec] = {}
        node_owner: dict[ua.NodeId, str] = {}
        for name, item in created.items():
            node_owner[ua.NodeId.from_string(item.spec.node_id)] = name
            for variable in item.spec.variables:
                node_id = ua.NodeId.from_string(variable.node_id)
                if node_id in variable_specs:
                    raise ValueError(f"duplicate NodeId while building registry: {node_id}")
                variable_specs[node_id] = variable
                node_owner[node_id] = name
        registry = cls(
            manifest=manifest,
            equipment=created,
            variable_specs=variable_specs,
            node_owner=node_owner,
        )
        expected = manifest.total_variables()
        if len(variable_specs) != expected:
            raise ValueError(f"created {len(variable_specs)} variables, manifest declares {expected}")
        _logger.info(
            "Address space ready: %d objects, %d variables (%d writable)",
            len(created),
            len(variable_specs),
            sum(1 for spec in variable_specs.values() if spec.writable),
        )
        return registry

    def owner(self, node_id: ua.NodeId) -> str | None:
        return self.node_owner.get(node_id)

    def node(self, node_id: ua.NodeId) -> Node | None:
        owner = self.owner(node_id)
        if owner is None:
            return None
        spec = self.variable_specs.get(node_id)
        if spec is None:
            return self.equipment[owner].node
        return self.equipment[owner].variables[spec.browse_name]

    def variables(self) -> list[tuple[str, VariableSpec, Node]]:
        result: list[tuple[str, VariableSpec, Node]] = []
        for name, item in self.equipment.items():
            for variable in item.spec.variables:
                result.append((name, variable, item.variables[variable.browse_name]))
        return result
