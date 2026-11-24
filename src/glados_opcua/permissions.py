"""Production authorization at the OPC UA service boundary.

``asyncua`` 1.1.8 exposes a public ``PermissionRuleset`` hook that is consulted
by ``UaProcessor`` before a request is executed.  The ruleset receives the
session user, the service type id and the raw request body, which is exactly the
boundary this deployment needs: a denied write is rejected before the value is
stored, and a batched write containing any unauthorized node fails as a whole.

Roles are fixed (admin/controller/device/monitor); per-variable ownership lives
in the device YAML as ``writer``.  Identity scoping to one or more equipment
names is optional on each configured user.  The compatibility profile uses
``LegacyRoleRuleset`` instead, preserving anonymous read/write for isolated
legacy clients.
"""

from __future__ import annotations

import fnmatch
import logging
from dataclasses import dataclass

from asyncua import ua
from asyncua.crypto.permission_rules import ADMIN_TYPES, USER_TYPES, PermissionRuleset, SimpleRoleRuleset, User
from asyncua.crypto.permission_rules import UserRole as UARole
from asyncua.ua.ua_binary import struct_from_binary

from .models import Manifest, UserRole, VariableSpec

_logger = logging.getLogger(__name__)

_SERVICE = ua.ObjectIds
_WRITE_TYPES = {ua.NodeId(_SERVICE.WriteRequest_Encoding_DefaultBinary)}
_CALL_TYPES = {ua.NodeId(_SERVICE.CallRequest_Encoding_DefaultBinary)}
_ADMIN_TYPES = {ua.NodeId(identifier) for identifier in ADMIN_TYPES}


def _decode(body, cls):
    """Decode a request body without consuming the server's shared stream.

    ``UaProcessor`` has already consumed the TypeId and RequestHeader; the
    stream is positioned at the service parameters.  The subsequent handler
    reads the same stream, so restore its position after inspection.
    """
    # ``asyncua`` passes a Buffer positioned after the RequestHeader.  Its
    # ``copy()`` returns a shadow view so the service handler still receives
    # the full remaining request.
    if hasattr(body, "copy"):
        stream = body.copy()
    else:
        import io

        stream = io.BytesIO(bytes(body))
    return struct_from_binary(cls, stream)


def _decode_write(body) -> ua.WriteParameters:
    return _decode(body, ua.WriteParameters)


def _decode_read(body) -> ua.ReadParameters:
    return _decode(body, ua.ReadParameters)


def _decode_monitored(body) -> ua.CreateMonitoredItemsParameters:
    return _decode(body, ua.CreateMonitoredItemsParameters)


@dataclass(frozen=True)
class IdentityPolicy:
    role: UserRole
    equipment: frozenset[str] | None


class PermissionMatrix:
    """Resolve users to roles and decide node-level read/write authorization."""

    def __init__(self, manifest: Manifest):
        self._manifest = manifest
        self._identities: dict[str, IdentityPolicy] = {
            user.username: IdentityPolicy(
                role=user.role,
                equipment=frozenset(user.equipment) if user.equipment is not None else None,
            )
            for user in manifest.server.security.users
        }
        self._roles = manifest.permissions.roles
        self._denied = tuple(manifest.permissions.denied)
        self._owners = {
            ua.NodeId.from_string(variable.node_id): equipment.name
            for equipment in manifest.equipment
            for variable in equipment.variables
        }
        self._specs = {
            ua.NodeId.from_string(variable.node_id): variable
            for equipment in manifest.equipment
            for variable in equipment.variables
        }

    def role_of(self, username: str | None) -> UserRole | None:
        if username is None:
            return None
        policy = self._identities.get(username)
        return policy.role if policy else None

    def _denied_node(self, node_id: ua.NodeId) -> bool:
        canonical = node_id.to_string()
        return any(fnmatch.fnmatchcase(canonical, pattern) for pattern in self._denied)

    def can_read(self, username: str | None, node_id: ua.NodeId) -> bool:
        policy = self._identities.get(username or "")
        if policy is None:
            return False
        if self._denied_node(node_id):
            return False
        if node_id in self._specs:  # legacy equipment: readable by all configured roles
            return self._roles[policy.role.value].read
        return True  # standard diagnostics/server nodes

    def can_write(self, username: str | None, node_id: ua.NodeId) -> bool:
        policy = self._identities.get(username or "")
        if policy is None:
            return False
        if self._denied_node(node_id):
            return False
        spec: VariableSpec | None = self._specs.get(node_id)
        if spec is None:
            # Nothing outside the frozen equipment manifest is client-writable.
            # Health nodes are server-managed; service-managed nodes are not
            # writable over OPC UA in production.
            return False
        if not spec.writable:
            return False
        role = self._roles[policy.role.value]
        if policy.equipment is not None and self._owners[node_id] not in policy.equipment:
            return False
        return role.write_all or spec.writer in role.write_by_writer

    def write_denials(self, username: str | None, params: ua.WriteParameters) -> list[str]:
        denied: list[str] = []
        for item in params.NodesToWrite:
            if item.AttributeId != ua.AttributeIds.Value:
                denied.append(f"{item.NodeId.to_string()} (attribute {item.AttributeId.name})")
                continue
            if not self.can_write(username, item.NodeId):
                denied.append(item.NodeId.to_string())
        return denied

    def read_denials(self, username: str | None, node_ids: list[ua.NodeId]) -> list[str]:
        return [node_id.to_string() for node_id in node_ids if not self.can_read(username, node_id)]


class GladosPermissionRuleset(PermissionRuleset):
    """Deny-by-default role enforcement for the production profile."""

    def __init__(self, matrix: PermissionMatrix):
        self.matrix = matrix

    def check_validity(self, user: User | None, action_type_id: ua.NodeId, body) -> bool:
        if user is None or user.name is None:
            return False
        if action_type_id in _WRITE_TYPES:
            try:
                params = _decode_write(body)
            except Exception as exc:
                _logger.warning("Could not decode WriteRequest for user %s: %r", user.name, exc)
                return False
            denied = self.matrix.write_denials(user.name, params)
            if denied:
                _logger.warning("Denied write for user %s to %s", user.name, denied)
                return False
            return True
        if action_type_id in _CALL_TYPES:
            _logger.warning("Denied method call for user %s (no client-callable methods)", user.name)
            return False
        if action_type_id in _ADMIN_TYPES:
            return self.matrix.role_of(user.name) is UserRole.ADMIN
        if action_type_id == ua.NodeId(_SERVICE.ReadRequest_Encoding_DefaultBinary):
            try:
                read_params = _decode_read(body)
            except Exception:
                return False
            denied = self.matrix.read_denials(user.name, [item.NodeId for item in read_params.NodesToRead])
            if denied:
                _logger.warning("Denied read for user %s of %s", user.name, denied)
                return False
        if action_type_id == ua.NodeId(_SERVICE.CreateMonitoredItemsRequest_Encoding_DefaultBinary):
            try:
                items: ua.CreateMonitoredItemsParameters = _decode_monitored(body)
            except Exception:
                return False
            denied = self.matrix.read_denials(
                user.name, [item.ItemToMonitor.NodeId for item in items.ItemsToCreate]
            )
            if denied:
                _logger.warning("Denied monitored item for user %s on %s", user.name, denied)
                return False
        return True


class LegacyRoleRuleset(SimpleRoleRuleset):
    """Legacy compatibility: all roles may use the user service set.

    The original server accepted every username (and anonymous sessions) and
    relied on node ``UserAccessLevel`` alone.  Reproducing that is only safe on
    an isolated test network; ``Profile.PRODUCTION`` never selects this class.
    """

    def __init__(self) -> None:
        super().__init__()
        self._permission_dict[UARole.Anonymous] = {ua.NodeId(identifier) for identifier in USER_TYPES}

    def check_validity(self, user: User | None, action_type_id: ua.NodeId, body) -> bool:
        if user is None:
            return False
        if action_type_id in _ADMIN_TYPES and user.role is not UARole.Admin:
            return False
        return action_type_id in self._permission_dict.get(user.role, set())


def build_ruleset(manifest: Manifest) -> PermissionRuleset:
    """Select the enforcement policy for the configured profile."""
    if manifest.permissions.enforced:
        return GladosPermissionRuleset(PermissionMatrix(manifest))
    return LegacyRoleRuleset()
