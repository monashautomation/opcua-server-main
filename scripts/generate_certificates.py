"""Generate a self-signed server certificate for OPC UA TLS.

The private key is written with mode 0600 and existing files are never
overwritten without ``--force``.  Certificates are development/deployment
artifacts and are git-ignored.

Usage:
    python scripts/generate_certificates.py --hostname opcua.lab.example \
        --ip 127.0.0.1 --ip 172.20.0.152
"""

from __future__ import annotations

import argparse
import ipaddress
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID


def generate(
    output: Path,
    common_name: str,
    dns_names: list[str],
    ips: list[str],
    app_uri: str,
    days: int,
    force: bool,
) -> tuple[Path, Path]:
    output.mkdir(parents=True, exist_ok=True)
    cert_path = output / "server.pem"
    key_path = output / "server.key"
    if not force and (cert_path.exists() or key_path.exists()):
        raise SystemExit(f"refusing to overwrite {cert_path} or {key_path}; pass --force to replace")

    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "GLaDOS"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ]
    )
    alt_names: list[x509.GeneralName] = [x509.UniformResourceIdentifier(app_uri)]
    alt_names.extend(x509.DNSName(name) for name in dns_names)
    alt_names.extend(x509.IPAddress(ipaddress.ip_address(ip)) for ip in ips)
    now = datetime.now(timezone.utc)  # noqa: UP017 - keep the script usable on Python 3.10 hosts
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=days))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=True,
                key_encipherment=True,
                data_encipherment=True,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH, ExtendedKeyUsageOID.CLIENT_AUTH]),
            critical=False,
        )
        .add_extension(x509.SubjectAlternativeName(alt_names), critical=False)
        .sign(key, hashes.SHA256())
    )

    key_path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    os.chmod(key_path, 0o600)
    cert_path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    os.chmod(cert_path, 0o644)
    return cert_path, key_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("certificates"))
    parser.add_argument("--common-name", default="glados-opcua")
    parser.add_argument("--hostname", action="append", default=[], help="DNS SAN; repeatable (defaults to common name)")
    parser.add_argument("--ip", action="append", default=[], help="IP SAN; repeatable")
    parser.add_argument("--application-uri", default="urn:freeopcua:python:server")
    parser.add_argument("--days", type=int, default=825)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    dns_names = args.hostname or [args.common_name, "localhost"]
    cert, key = generate(args.output, args.common_name, dns_names, args.ip, args.application_uri, args.days, args.force)
    print(f"certificate: {cert}\nprivate key: {key} (mode 0600)")
    print("Mount read-only and ensure the container user can read the key.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
