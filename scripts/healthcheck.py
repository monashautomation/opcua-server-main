"""OPC UA-aware container health check.

Exits 0 only when a real OPC UA session can read ``ServerStatus.State`` and the
server reports ``Running``.  It never treats an open TCP port as healthy.

Environment:
    GLADOS_HEALTH_URL       endpoint (default: GLADOS_SERVER_URL with 0.0.0.0
                            rewritten to 127.0.0.1, else opc.tcp://127.0.0.1:4841/server/)
    GLADOS_HEALTH_USER      username for production
    GLADOS_HEALTH_PASSWORD  password for production
    GLADOS_HEALTH_CERT      client certificate (PEM) for encrypted endpoints
    GLADOS_HEALTH_KEY       client private key (PEM)
    GLADOS_HEALTH_POLICY    security policy name, default Basic256Sha256
    GLADOS_HEALTH_MODE      Sign or SignAndEncrypt, default SignAndEncrypt

Encrypted endpoints require a client certificate and key; use a dedicated
health-client certificate, never the server key.
"""

from __future__ import annotations

import asyncio
import os
import sys

from asyncua import Client, ua
from asyncua.crypto import security_policies
from asyncua.crypto.uacrypto import CertProperties


def health_url() -> str:
    explicit = os.environ.get("GLADOS_HEALTH_URL")
    if explicit:
        return explicit
    endpoint = os.environ.get("GLADOS_SERVER_URL", "opc.tcp://127.0.0.1:4841/server/")
    return endpoint.replace("0.0.0.0", "127.0.0.1")


async def check() -> int:
    client = Client(url=health_url())
    username = os.environ.get("GLADOS_HEALTH_USER")
    if username:
        client.set_user(username)
        client.set_password(os.environ.get("GLADOS_HEALTH_PASSWORD", ""))

    certificate = os.environ.get("GLADOS_HEALTH_CERT")
    private_key = os.environ.get("GLADOS_HEALTH_KEY")
    if certificate and private_key:
        policy_name = os.environ.get("GLADOS_HEALTH_POLICY", "Basic256Sha256")
        mode_name = os.environ.get("GLADOS_HEALTH_MODE", "SignAndEncrypt")
        policy = getattr(security_policies, f"SecurityPolicy{policy_name}")
        await client.set_security(
            policy,
            certificate,
            CertProperties(private_key, "pem"),
            server_certificate=None,
            mode=getattr(ua.MessageSecurityMode, mode_name),
        )

    async with client:
        state = await client.get_node(ua.NodeId(ua.ObjectIds.Server_ServerStatus_State)).read_value()
    if state != ua.ServerState.Running:
        print(f"server state is {state!r}, expected Running", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    try:
        return asyncio.run(asyncio.wait_for(check(), timeout=5))
    except Exception as exc:
        print(f"health check failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
