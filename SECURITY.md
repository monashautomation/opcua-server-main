# Security policy

This repository implements an OPC UA server for lab equipment. It is a
communication layer, **not** a safety system. Physical interlocks, emergency
stops and motion validation must remain in independently safety-rated systems.

## Supported versions

| Version | Supported |
|---|---|
| 2.x | Yes |
| Legacy `legacy/server_opcua.py` | No — archived reference only |

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Use GitHub's private
vulnerability reporting for
`monashautomation/opcua-server-main` (Security → Report a vulnerability).
Include affected version, reproduction steps and impact. We aim to acknowledge
within 5 business days.

## Secure deployment requirements

- Run `GLADOS_PROFILE=production`. It refuses anonymous sessions, `NoSecurity`
  and missing certificates at startup.
- Provide credentials only through environment variables named by
  `security.users[].password_env`; passwords and private keys are git-ignored.
- Mount configuration and certificates read-only. Run the container as the
  non-root user defined in the `Dockerfile`.
- Publish the OPC UA port to loopback, or restrict it with host/network
  firewall rules. OPC UA has no built-in brute-force protection.
- Keep `security.allow_insecure_legacy: false` outside isolated test networks.
  The legacy profile intentionally disables password validation and anonymous
  restrictions and logs a warning on every startup.
- Rotate certificates before expiry. `scripts/generate_certificates.py` writes
  a key with mode 0600 and refuses to overwrite existing files.
- Review `config/permissions.yaml` and per-variable `writer` ownership before
  production cutover. Unconfirmed ownership is admin-only by design.

## What this project does not protect against

- Malicious operators with valid credentials and network access. Role scoping
  limits devices but does not replace network segmentation or safety systems.
- Denial of service. Resource limits belong to the container/host.
- Vulnerabilities in third-party dependencies. Dependencies are pinned in
  `requirements.lock`; run `pip-audit` as part of release checks.
