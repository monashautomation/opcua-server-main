"""Command and security event auditing.

Audit records intentionally omit values: image ByteStrings and command payloads
can be large or sensitive.  The username, NodeId and OPC UA status are enough to
reconstruct who attempted what.  Denials are logged by the permission ruleset;
this module records authorized writes asynchronously via the public PostWrite
callback.
"""

from __future__ import annotations

import logging

from asyncua import Server, ua
from asyncua.common.callback import CallbackType

_logger = logging.getLogger(__name__)


class AuditLogger:
    """Log one line per write attempt without recording written values."""

    def __init__(self, server: Server):
        self._server = server

    def start(self) -> None:
        self._server.iserver.subscribe_server_callback(CallbackType.PostWrite, self._on_post_write)

    def stop(self) -> None:
        self._server.iserver.unsubscribe_server_callback(CallbackType.PostWrite, self._on_post_write)

    async def _on_post_write(self, event, callback_service) -> None:
        if event.request_params is None or not event.is_external:
            return
        user = getattr(event.user, "name", None) or "unknown"
        results = event.response_params or []
        for item, status in zip(event.request_params.NodesToWrite, results, strict=False):
            code = status if isinstance(status, ua.StatusCode) else ua.StatusCode(status)
            try:
                attribute = ua.AttributeIds(item.AttributeId).name
            except ValueError:
                attribute = str(item.AttributeId)
            if code.is_good():
                _logger.info(
                    "audit write user=%s node=%s attribute=%s",
                    user,
                    item.NodeId.to_string(),
                    attribute,
                )
            else:
                _logger.warning(
                    "audit write-failed user=%s node=%s attribute=%s status=%s",
                    user,
                    item.NodeId.to_string(),
                    attribute,
                    code.name,
                )
