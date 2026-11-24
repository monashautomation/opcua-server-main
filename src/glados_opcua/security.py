"""Authentication and transport security.

The legacy server did not validate passwords and attempted to enable secure
policies with no certificate.  That behaviour is available only as an explicit
``legacy`` compatibility profile on an isolated network; ``production`` requires
a certificate, forbids anonymous/NoSecurity and validates credentials.

Username passwords come from environment variables named by
``security.users[].password_env``.  Client certificates are matched by exact DER
bytes through ``asyncua``'s public ``CertificateUserManager``.
"""

from __future__ import annotations

import hmac
import logging
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

from asyncua import Server
from asyncua.crypto.permission_rules import User
from asyncua.crypto.permission_rules import UserRole as UARole
from asyncua.server.user_managers import CertificateUserManager, UserManager

from .models import Manifest, Profile, UserRole

_logger = logging.getLogger(__name__)


class GladosUserManager(UserManager):
    """Username/password and X.509 authentication for both profiles."""

    def __init__(self, manifest: Manifest):
        self._manifest = manifest
        self._profile = manifest.server.profile
        self._users = {user.username: user for user in manifest.server.security.users}
        self._certificates: CertificateUserManager | None = None
        self._passwords: dict[str, str] = {}

    async def prepare(self) -> None:
        """Resolve password environment variables and client certificates.

        Called during startup so missing secrets fail before listening.
        """
        for user in self._users.values():
            if user.password_env:
                password = os.environ.get(user.password_env)
                if not password:
                    raise RuntimeError(
                        f"missing credential for {user.username!r}: environment variable "
                        f"{user.password_env!r} is unset or empty"
                    )
                if self._profile is Profile.PRODUCTION and len(password) < 12:
                    raise RuntimeError(
                        f"password for {user.username!r} from {user.password_env!r} "
                        "must be at least 12 characters"
                    )
                self._passwords[user.username] = password
            if user.certificate:
                if self._certificates is None:
                    self._certificates = CertificateUserManager()
                await self._certificates.add_role(
                    Path(user.certificate),
                    UARole.Admin if user.role is UserRole.ADMIN else UARole.User,
                    name=user.username,
                )
        if self._profile is Profile.LEGACY:
            _logger.warning(
                "Legacy compatibility profile: passwords are not validated and anonymous "
                "access is accepted. Run only on an isolated test network."
            )

    def _ua_role(self, role: UserRole) -> UARole:
        return UARole.Admin if role is UserRole.ADMIN else UARole.User

    def get_user(
        self,
        iserver,
        username: str | None = None,
        password: str | None = None,
        certificate: bytes | None = None,
    ) -> User | None:
        # A secure channel always presents a peer certificate.  Only treat it as
        # an identity when no username token was supplied; otherwise password
        # authentication would be impossible on encrypted endpoints.
        if certificate and not username:
            if self._certificates is None:
                return None
            return self._certificates.get_user(iserver, certificate=certificate)

        if self._profile is Profile.LEGACY:
            # Exact legacy behaviour: admin by name, everyone else anonymous.
            role = UARole.Admin if username in ("admin", "Admin") else UARole.Anonymous
            return User(role=role, name=username or "anonymous")

        if not username:
            return None
        user = self._users.get(username)
        if user is None or not user.password_env:
            return None
        supplied = password or ""
        if not hmac.compare_digest(supplied.encode("utf-8"), self._passwords[username].encode("utf-8")):
            _logger.warning("Rejected credentials for user %s", username)
            return None
        return User(role=self._ua_role(user.role), name=username)


def _check_expiry(certificate, path: Path) -> None:
    """Refuse expired certificates and warn before the trust cliff."""
    expiry = getattr(certificate, "not_valid_after_utc", None)
    if expiry is None:  # older cryptography releases expose a naive datetime
        expiry = certificate.not_valid_after.replace(tzinfo=UTC)
    now = datetime.now(UTC)
    if expiry <= now:
        raise RuntimeError(f"server certificate {path} expired at {expiry.isoformat()}")
    if expiry - now < timedelta(days=30):
        _logger.warning("Server certificate %s expires soon at %s", path, expiry.isoformat())


def needs_certificate(manifest: Manifest) -> bool:
    """True when any endpoint policy requires a certificate."""
    return any(policy.value != "NoSecurity" for policy in manifest.server.security.policies)


async def configure_security(server: Server, manifest: Manifest, ruleset) -> GladosUserManager:
    """Apply policies, identity tokens, certificate and user manager.

    ``asyncua`` silently downgrades secure endpoints when no certificate is
    configured.  This function refuses to start instead, so a production
    deployment cannot accidentally advertise only NoSecurity.
    """
    security = manifest.server.security
    server.set_security_policy([policy.ua_type for policy in security.policies], permission_ruleset=ruleset)
    server.set_identity_tokens([token.ua_type for token in security.identity_tokens])

    needs_cert = needs_certificate(manifest)
    if needs_cert:
        certificate = Path(security.certificate)
        private_key = Path(security.private_key)
        if not certificate.is_file() or not private_key.is_file():
            raise RuntimeError(
                f"secure policies {[p.value for p in security.policies]} require "
                f"{certificate} and {private_key}; provision them outside source control"
            )
        await server.load_certificate(certificate)
        key_format = "pem" if private_key.read_bytes().lstrip().startswith(b"-----BEGIN") else None
        await server.load_private_key(private_key, format=key_format)
        _check_expiry(server.iserver.certificate, certificate)
        _logger.info("Loaded server certificate %s", certificate)

    manager = GladosUserManager(manifest)
    await manager.prepare()
    server.iserver.set_user_manager(manager)
    return manager
