"""Authentication, transport security, certificates and role enforcement."""

from __future__ import annotations

from pathlib import Path

import pytest
from asyncua import Client, ua
from asyncua.crypto.permission_rules import UserRole as UARole
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256
from asyncua.crypto.uacrypto import CertProperties
from cryptography import x509
from cryptography.hazmat.primitives import serialization

from glados_opcua.models import Profile
from glados_opcua.security import GladosUserManager
from scripts.generate_certificates import generate

from .conftest import copy_config, manifest_for

USERS = [
    {"username": "admin", "role": "admin", "password_env": "TEST_ADMIN"},
    {"username": "ctrl", "role": "controller", "password_env": "TEST_CTRL"},
    {"username": "dev1", "role": "device", "password_env": "TEST_DEV1", "equipment": ["robot1"]},
    {"username": "mon", "role": "monitor", "password_env": "TEST_MON"},
]
PASSWORDS = {
    "TEST_ADMIN": "admin-password",
    "TEST_CTRL": "ctrl-password",
    "TEST_DEV1": "dev-password",
    "TEST_MON": "mon-password",
}


def production_config(tmp_path: Path, cert_dir: Path) -> Path:
    return copy_config(
        tmp_path,
        profile=Profile.PRODUCTION.value,
        security={
            "certificate": str(cert_dir / "server.pem"),
            "private_key": str(cert_dir / "server.key"),
            "users": USERS,
        },
    )


def test_certificate_generation_is_private_and_scoped(tmp_path: Path):
    cert_dir = tmp_path / "certs"
    cert_path, key_path = generate(
        cert_dir, "glados-test", ["localhost"], ["127.0.0.1"], "urn:freeopcua:python:server", 30, force=False
    )
    assert cert_path.is_file() and key_path.is_file()
    assert (key_path.stat().st_mode & 0o777) == 0o600
    certificate = x509.load_pem_x509_certificate(cert_path.read_bytes())
    san = certificate.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    assert "127.0.0.1" in [str(ip) for ip in san.get_values_for_type(x509.IPAddress)]
    uris = [str(uri) for uri in san.get_values_for_type(x509.UniformResourceIdentifier)]
    assert "urn:freeopcua:python:server" in uris
    with pytest.raises(SystemExit):
        generate(cert_dir, "glados-test", ["localhost"], [], "urn:freeopcua:python:server", 30, force=False)


async def test_user_manager_rejects_bad_and_anonymous_credentials(tmp_path: Path, monkeypatch):
    for key, value in PASSWORDS.items():
        monkeypatch.setenv(key, value)
    manifest = manifest_for(production_config(tmp_path, tmp_path / "certs"))
    manager = GladosUserManager(manifest)
    await manager.prepare()
    user = manager.get_user(None, username="admin", password="admin-password")
    assert user is not None and user.role is UARole.Admin
    assert manager.get_user(None, username="admin", password="wrong") is None
    assert manager.get_user(None, username="nobody", password="x") is None
    assert manager.get_user(None) is None


async def test_short_password_rejected_in_production(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("TEST_ADMIN", "short")
    for key in ("TEST_CTRL", "TEST_DEV1", "TEST_MON"):
        monkeypatch.setenv(key, "long-enough-password")
    manifest = manifest_for(production_config(tmp_path, tmp_path / "certs"))
    manager = GladosUserManager(manifest)
    with pytest.raises(RuntimeError, match="at least 12 characters"):
        await manager.prepare()


async def test_certificate_identity_is_exact_der(tmp_path: Path, monkeypatch):
    cert_dir = tmp_path / "client"
    cert_path, _ = generate(
        cert_dir, "wrapper-robot1", ["localhost"], [], "urn:glados:client", 30, force=False
    )
    for key, value in PASSWORDS.items():
        monkeypatch.setenv(key, value)
    manifest = manifest_for(
        copy_config(
            tmp_path,
            profile=Profile.PRODUCTION.value,
            security={
                "certificate": str(tmp_path / "unused.pem"),
                "private_key": str(tmp_path / "unused.key"),
                "identity_tokens": ["Username", "X509"],
                "users": [
                    {"username": "admin", "role": "admin", "password_env": "TEST_ADMIN"},
                    {"username": "cert-wrapper", "role": "device", "certificate": str(cert_path)},
                ],
            },
        )
    )
    manager = GladosUserManager(manifest)
    await manager.prepare()
    der = x509.load_pem_x509_certificate(cert_path.read_bytes()).public_bytes(serialization.Encoding.DER)
    user = manager.get_user(None, certificate=der)
    assert user is not None and user.name == "cert-wrapper"
    other = generate(tmp_path / "other", "other", ["localhost"], [], "urn:other", 30, force=False)[0]
    other_der = x509.load_pem_x509_certificate(other.read_bytes()).public_bytes(serialization.Encoding.DER)
    assert manager.get_user(None, certificate=other_der) is None


async def test_missing_password_environment_fails_fast(tmp_path: Path, monkeypatch):
    for key in PASSWORDS:
        monkeypatch.delenv(key, raising=False)
    manifest = manifest_for(production_config(tmp_path, tmp_path / "certs"))
    manager = GladosUserManager(manifest)
    with pytest.raises(RuntimeError, match="TEST_ADMIN|TEST_CTRL|TEST_DEV1|TEST_MON"):
        await manager.prepare()


async def test_legacy_user_manager_accepts_anything(tmp_path: Path):
    manifest = manifest_for(copy_config(tmp_path))
    manager = GladosUserManager(manifest)
    await manager.prepare()
    user = manager.get_user(None, username="anyone", password="ignored")
    assert user is not None
    assert user.role is UARole.Anonymous
    admin = manager.get_user(None, username="admin")
    assert admin is not None and admin.role is UARole.Admin


async def _secure_client(url: str, cert_dir: Path, username: str | None = None, password: str | None = None) -> Client:
    client = Client(url=url)
    await client.set_security(
        SecurityPolicyBasic256Sha256,
        str(cert_dir / "server.pem"),
        CertProperties(str(cert_dir / "server.key"), "pem"),
        server_certificate=None,
        mode=ua.MessageSecurityMode.SignAndEncrypt,
    )
    if username:
        client.set_user(username)
        client.set_password(password or "")
    return client


async def test_production_end_to_end_authentication_and_roles(tmp_path: Path, monkeypatch):
    cert_dir = tmp_path / "certs"
    generate(cert_dir, "glados-test", ["localhost"], ["127.0.0.1"], "urn:freeopcua:python:server", 30, force=False)
    for key, value in PASSWORDS.items():
        monkeypatch.setenv(key, value)
    manifest = manifest_for(production_config(tmp_path, cert_dir))
    from glados_opcua.server import build_server

    bundle = await build_server(manifest)
    async with bundle.server:
        try:
            # Anonymous over an encrypted channel is rejected by identity tokens.
            client = await _secure_client(manifest.server.endpoint, cert_dir)
            with pytest.raises(ua.uaerrors.UaStatusCodeError):
                await client.connect()

            client = await _secure_client(manifest.server.endpoint, cert_dir, "admin", "wrong")
            with pytest.raises(ua.uaerrors.UaStatusCodeError):
                await client.connect()

            async with await _secure_client(manifest.server.endpoint, cert_dir, "admin", "admin-password") as client:
                await client.get_node("ns=21;s=R1c_Start;").write_value(True)
                with pytest.raises(ua.uaerrors.UaStatusCodeError):
                    await client.get_node("ns=22;s=R2c_int4;").write_value(1)

            async with await _secure_client(manifest.server.endpoint, cert_dir, "dev1", "dev-password") as client:
                await client.get_node("ns=21;s=R1d_Joi1;").write_value(3.5)
                with pytest.raises(ua.uaerrors.UaStatusCodeError):
                    await client.get_node("ns=22;s=R2d_Joi1;").write_value(3.5)

            async with await _secure_client(manifest.server.endpoint, cert_dir, "mon", "mon-password") as client:
                assert await client.get_node("ns=21;s=R1d_Joi1;").read_value() == 3.5
                with pytest.raises(ua.uaerrors.UaStatusCodeError):
                    await client.get_node("ns=21;s=R1d_Joi1;").write_value(9.0)
        finally:
            bundle.audit.stop()


async def test_expired_certificate_is_rejected(tmp_path: Path, monkeypatch):
    cert_dir = tmp_path / "expired"
    generate(cert_dir, "glados-test", ["localhost"], ["127.0.0.1"], "urn:freeopcua:python:server", -1, force=False)
    for key, value in PASSWORDS.items():
        monkeypatch.setenv(key, value)
    manifest = manifest_for(production_config(tmp_path, cert_dir))
    from glados_opcua.server import build_server

    with pytest.raises(RuntimeError, match="expired"):
        await build_server(manifest)
