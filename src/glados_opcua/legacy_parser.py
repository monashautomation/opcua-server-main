"""Static extraction of the frozen legacy interface.

The legacy server executed 488 ``add_variable`` calls and 18 ``add_object``
calls.  This module reads the archived source with :mod:`ast` only — no legacy
code is imported or executed — and records the exact NodeIDs, browse names,
defaults and writable declarations.  The result is compared against a runtime
export from an isolated legacy instance; a mismatch is a release blocker.

Type inference mirrors ``asyncua`` 1.1.8's ``_guess_datatype``: bare ``int`` is
``Int64``, bare ``float`` is ``Double``.  That is not a convenience: the legacy
wire types include exactly four Int64 variables created from bare integers.
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from asyncua import ua

from .models import DataType, VariableCategory, WriterRole

_DATA_TYPE_BY_ATTR = {
    "Boolean": DataType.Boolean,
    "Int32": DataType.Int32,
    "Int64": DataType.Int64,
    "UInt32": DataType.UInt32,
    "Float": DataType.Float,
    "Double": DataType.Double,
    "String": DataType.String,
    "ByteString": DataType.ByteString,
}

#: Variables whose ownership is not evidenced by the legacy source.  They are
#: admin-only until a client review confirms who writes them.
UNVERIFIED_VARIABLES = {
    "LabCount": "Communication counter ownership unconfirmed",
    "MagCount": "Magnet controller counter ownership unconfirmed",
    "MagInfo": "Magnet controller info ownership unconfirmed",
}

#: Read-only or device-owned variables that share the command naming prefix.
_DEVICE_OWNED_EXCEPTIONS = {
    "wrapperDisconnect",
    "R1c_Connected",
    "R2c_Connected",
    "R3c_Connected",
    "R4c_Connected",
    "R4c_err",
    "R4c_sev",
}

_NAME_MARKER = re.compile(r"[0-9A-Za-z]([cdf])_")

_EQUIPMENT_DESCRIPTIONS = {
    "Communication": "Legacy communication group (LabCount, wrapperDisconnect)",
    "Operator": "Legacy operator group",
    "MagnetEE": "Magnet end-effector controller",
    "robot1": "KUKA KMR iiwa 14 R820",
    "robot2": "KUKA KMR iiwa 14 R820",
    "robot3": "KUKA KMR iiwa 14 R820",
    "robot4": "FlexFellow iiwa 14 R820",
    "Printer1": "Creality Ender 3 v2",
    "Printer2": "Creality Ender 3 v2",
    "Printer3": "Creality Ender 3 v2",
    "Printer4": "Creality Ender 3 v2",
    "RobotDog1": "Quadruped robot dog",
    "Camera1": "JAI camera",
    "AirPurifier1": "Air purifier (Perry)",
    "AirPurifier2": "Air purifier (Kermit)",
    "Glove 1 (Left)": "Haptic glove, left",
    "Glove 2 (Right)": "Haptic glove, right",
    "500 RGB LEDs": "LED strip controller",
}


@dataclass
class LegacyVariable:
    browse_name: str
    node_id: str
    data_type: DataType
    default: Any
    writable: bool = False
    order: int = 0


@dataclass
class LegacyObject:
    name: str
    namespace: int
    variables: list[LegacyVariable] = field(default_factory=list)
    node_id: str | None = None


def _literal(node: ast.expr) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if (
        isinstance(node, ast.UnaryOp)
        and isinstance(node.op, ast.USub)
        and isinstance(node.operand, ast.Constant)
        and isinstance(node.operand.value, (int, float))
        and not isinstance(node.operand.value, bool)
    ):
        return -node.operand.value
    if isinstance(node, ast.List):
        return [_literal(item) for item in node.elts]
    raise ValueError(f"unsupported default expression at line {node.lineno}: {ast.dump(node)}")


def _parse_default(node: ast.expr) -> tuple[DataType, Any]:
    """Return the exact wire data type and value for a legacy default."""
    if isinstance(node, ast.Constant):
        value = node.value
        if isinstance(value, bool):
            return DataType.Boolean, value
        if isinstance(value, int):
            return DataType.Int64, value
        if isinstance(value, float):
            return DataType.Double, value
        if isinstance(value, str):
            return DataType.String, value
        raise ValueError(f"unsupported literal at line {node.lineno}: {value!r}")
    if isinstance(node, ast.UnaryOp):
        return DataType.Double, float(_literal(node))
    if isinstance(node, ast.Call):
        function = node.func
        name = function.attr if isinstance(function, ast.Attribute) else getattr(function, "id", None)
        if name not in _DATA_TYPE_BY_ATTR:
            raise ValueError(f"unsupported default constructor {name!r} at line {node.lineno}")
        if len(node.args) != 1:
            raise ValueError(f"{name} default at line {node.lineno} must have one argument")
        return _DATA_TYPE_BY_ATTR[name], _literal(node.args[0])
    raise ValueError(f"unsupported default node at line {node.lineno}: {type(node).__name__}")


def _call_name(node: ast.Call) -> str | None:
    function = node.func
    if isinstance(function, ast.Attribute):
        return function.attr
    return getattr(function, "id", None)


def parse_legacy_source(path: str | Path) -> list[LegacyObject]:
    """Extract objects, variables and writable declarations in source order."""
    tree = ast.parse(Path(path).read_text(encoding="utf-8"), filename=str(path))
    main = next(
        (node for node in tree.body if isinstance(node, ast.AsyncFunctionDef) and node.name == "main"),
        None,
    )
    if main is None:
        raise ValueError(f"{path} has no async main() function")

    objects: list[LegacyObject] = []
    current: LegacyObject | None = None
    by_variable_name: dict[str, LegacyVariable] = {}
    writable_names: list[str] = []
    order = 0

    def handle_assignment(value: ast.AST, target_name: str) -> None:
        nonlocal current, order
        if not isinstance(value, ast.Await) or not isinstance(value.value, ast.Call):
            return
        call = value.value
        name = _call_name(call)
        if name == "add_object":
            if len(call.args) < 2:
                raise ValueError(f"add_object at line {call.lineno} needs namespace and name")
            namespace = _literal(call.args[0])
            object_name = _literal(call.args[1])
            if not isinstance(namespace, int) or not isinstance(object_name, str):
                raise ValueError(f"invalid add_object at line {call.lineno}")
            current = LegacyObject(name=object_name, namespace=namespace)
            objects.append(current)
        elif name == "add_variable":
            if current is None:
                raise ValueError(f"add_variable at line {call.lineno} has no containing object")
            if len(call.args) < 3:
                raise ValueError(f"add_variable at line {call.lineno} needs nodeid, name and default")
            node_id = _literal(call.args[0])
            browse_name = _literal(call.args[1])
            if not isinstance(node_id, str) or not isinstance(browse_name, str):
                raise ValueError(f"invalid add_variable at line {call.lineno}")
            data_type, default = _parse_default(call.args[2])
            variable = LegacyVariable(
                browse_name=browse_name,
                node_id=node_id,
                data_type=data_type,
                default=default,
                order=order,
            )
            order += 1
            current.variables.append(variable)
            by_variable_name[target_name] = variable

    for statement in main.body:
        if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
            target = statement.targets[0]
            if isinstance(target, ast.Name):
                handle_assignment(statement.value, target.id)
            elif isinstance(target, ast.Attribute):
                handle_assignment(statement.value, target.attr)
        elif (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Await)
            and isinstance(statement.value.value, ast.Call)
            and _call_name(statement.value.value) == "set_writable"
        ):
            function = statement.value.value.func
            if isinstance(function, ast.Attribute) and isinstance(function.value, ast.Name):
                writable_names.append(function.value.id)

    for variable_name in writable_names:
        variable = by_variable_name.get(variable_name)
        if variable is None:
            raise ValueError(f"set_writable references unknown variable {variable_name!r}")
        variable.writable = True
    return objects


def baseline_objects(baseline_path: str | Path) -> dict[tuple[int, str], dict[str, Any]]:
    """Index a runtime export by ``(namespace index, browse name)``."""
    data = json.loads(Path(baseline_path).read_text(encoding="utf-8"))
    objects: dict[tuple[int, str], dict[str, Any]] = {}
    parents = {node["parent"] for node in data["nodes"]}
    for node in data["nodes"]:
        if node["node_id"] not in parents or node["node_class"] != "Object":
            continue
        node_id = ua.NodeId.from_string(node["node_id"])
        if node_id.NamespaceIndex < 1:
            continue
        objects[(node["browse_name"]["namespace"], node["browse_name"]["name"])] = node
    return objects


def _baseline_variables(baseline_path: str | Path) -> dict[str, dict[str, Any]]:
    data = json.loads(Path(baseline_path).read_text(encoding="utf-8"))
    return {node["node_id"]: node for node in data["nodes"] if node["node_class"] == "Variable"}


def normalize_default(data_type: DataType, value: Any) -> Any:
    if data_type is DataType.ByteString:
        return {"__bytes__": bytes(value).hex()}
    return value


def differences(static: list[LegacyObject], baseline_path: str | Path) -> list[str]:
    """Compare the static extraction with the runtime export."""
    problems: list[str] = []
    objects = baseline_objects(baseline_path)
    variables = _baseline_variables(baseline_path)
    if len(static) != 18:
        problems.append(f"static object count {len(static)} != expected 18")
    if len(objects) != len(static):
        problems.append(f"runtime object count {len(objects)} != static {len(static)}")

    static_variables = 0
    for obj in static:
        match = objects.get((obj.namespace, obj.name))
        if match is None:
            problems.append(f"object {obj.name!r} ns={obj.namespace} missing from baseline")
            continue
        obj.node_id = match["node_id"]
        static_variables += len(obj.variables)
        for variable in obj.variables:
            actual = variables.get(variable.node_id)
            if actual is None:
                problems.append(f"variable {variable.node_id!r} missing from baseline")
                continue
            if actual["browse_name"]["name"] != variable.browse_name:
                problems.append(
                    f"{variable.node_id}: browse name {actual['browse_name']['name']!r} "
                    f"!= static {variable.browse_name!r}"
                )
            actual_type = actual["attributes"]["DataType"]["value"]["__nodeid__"]
            expected_type = ua.NodeId(variable.data_type.data_type_id, 0).to_string()
            if actual_type != expected_type:
                problems.append(
                    f"{variable.node_id}: runtime type {actual_type} != static "
                    f"{variable.data_type.value} ({expected_type})"
                )
            actual_value = actual["attributes"]["Value"]["value"]
            expected_value = normalize_default(variable.data_type, variable.default)
            if actual_value != expected_value:
                problems.append(
                    f"{variable.node_id}: runtime default {actual_value!r} != static {expected_value!r}"
                )
            access = actual["attributes"]["AccessLevel"]["value"]
            actual_writable = bool(isinstance(access, int) and access & ua.AccessLevel.CurrentWrite.mask)
            if actual_writable != variable.writable:
                problems.append(
                    f"{variable.node_id}: runtime writable={actual_writable} != static {variable.writable}"
                )

    runtime_object_ids = {obj["node_id"] for obj in objects.values()}
    runtime_variables = {
        node_id: node for node_id, node in variables.items() if node["parent"] in runtime_object_ids
    }
    if len(runtime_variables) != static_variables:
        problems.append(
            f"runtime variable count {len(runtime_variables)} != static {static_variables}"
        )
    static_ids = {variable.node_id for obj in static for variable in obj.variables}
    for extra in sorted(set(runtime_variables) - static_ids):
        problems.append(f"variable {extra!r} exists at runtime but not in the static extraction")
    return problems


def classify(variable_name: str) -> tuple[VariableCategory, WriterRole, str | None]:
    """Assign documentation category and production write owner.

    The legacy naming convention is ``<device>[c|d|f]_`` for command data,
    device data and feedback.  Ownership is written into YAML and reviewed;
    scripts never re-infer it at runtime.  Ambiguous variables are admin-only.
    """
    if variable_name in UNVERIFIED_VARIABLES:
        return VariableCategory.UNVERIFIED, WriterRole.ADMIN, UNVERIFIED_VARIABLES[variable_name]
    if variable_name in _DEVICE_OWNED_EXCEPTIONS:
        return VariableCategory.STATUS, WriterRole.DEVICE, None
    marker = _NAME_MARKER.search(variable_name)
    if marker and marker.group(1) == "c":
        return VariableCategory.COMMAND, WriterRole.CONTROLLER, None
    if marker and marker.group(1) == "d":
        return VariableCategory.TELEMETRY, WriterRole.DEVICE, None
    if marker and marker.group(1) == "f":
        return VariableCategory.FEEDBACK, WriterRole.DEVICE, None
    return VariableCategory.UNVERIFIED, WriterRole.ADMIN, "naming convention does not establish an owner"


def equipment_description(name: str) -> str:
    return _EQUIPMENT_DESCRIPTIONS.get(name, f"Legacy equipment group {name}")
