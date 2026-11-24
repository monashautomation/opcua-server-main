# Deployment

## Profiles

| | `legacy` | `production` |
|---|---|---|
| Anonymous | Allowed by explicit acknowledgement | Forbidden |
| NoSecurity | Allowed (isolated network only) | Forbidden |
| Passwords | Not validated | Validated against environment secrets |
| Permissions | Not enforced; legacy access levels only | Enforced per role/node |
| Certificate | Optional | Required, expiry checked |
| Health namespace | Optional (disabled in parity mode) | Recommended |
| Use | Isolated compatibility testing | Real deployments |

The profile comes from `GLADOS_PROFILE` (highest precedence) or
`config/server.yaml`. The legacy profile refuses to start without
`security.allow_insecure_legacy: true`; production refuses anonymous access,
`NoSecurity`, missing users, missing certificates and `permissions.enforced: false`.

## Configuration precedence

`environment variable > config/server.yaml > model default`.

| Variable | Purpose |
|---|---|
| `GLADOS_SERVER_URL` | Advertised endpoint, legacy-compatible |
| `GLADOS_BIND_ADDRESS`, `GLADOS_BIND_PORT` | Listen socket separate from advertised endpoint |
| `GLADOS_PROFILE` | `legacy` or `production` |
| `GLADOS_CONFIG_DIR` | Configuration directory (CLI default) |
| `GLADOS_LOG_LEVEL`, `GLADOS_LOG_JSON` | Logging |
| `GLADOS_HEALTH_ENABLED` | Toggle additive health namespace |
| `GLADOS_HEALTH_USER`, `GLADOS_HEALTH_PASSWORD` | Container health check identity |

Passwords are never read from YAML. `security.users[].password_env` names the
environment variable. Client certificates are trusted by exact DER bytes.

## Production checklist

1. Copy examples:
   ```bash
   cp config/examples/server.production.yaml config/server.yaml
   cp config/examples/permissions.production.yaml config/permissions.yaml
   ```
2. Generate a certificate whose SAN includes the DNS name and IP clients use:
   ```bash
   python scripts/generate_certificates.py \
     --hostname opcua.lab.example --ip 127.0.0.1 --ip 172.20.0.152
   python scripts/generate_certificates.py --output certificates/health \
     --common-name health-client --hostname health-client
   chmod 640 certificates/server.key certificates/health/server.key
   chown 10001:10001 certificates/server.key certificates/health/server.key
   ```
   The key is created with mode 0600; grant the container UID (10001) read
   access without making it world-readable. Certificates are git-ignored.
3. Set real passwords in the environment/`.env`; `.env` is git-ignored.
4. Set `endpoint` and, if needed, `bind_address`/`bind_port`. Publish only to a
   loopback or firewalled interface.
5. Review `config/permissions.yaml` and every variable's `writer` ownership.
   The health check uses a dedicated `health-client` certificate and a
   read-only `monitor` identity; never reuse the server key for clients.
6. Run `python -m glados_opcua --validate`, then `pytest -q`.
7. Start, verify `Health/<Equipment>.Status`, then reconnect clients.

## Docker

```bash
cp .env.example .env    # set real values
docker compose up -d
docker compose logs -f
```

Compose defaults are fail-closed: production profile, loopback port publish,
read-only root/config/certificates, `no-new-privileges`, all capabilities
dropped, tmpfs for `/tmp`, resource logging limits and a 30 s stop grace period.
It also requires `GLADOS_PASSWORD_ADMIN` and `GLADOS_PASSWORD_HEALTH` to be set.

The binary protocol uses one port for both listening and advertised endpoints.
Publish and advertise the same port; otherwise OPC UA discovery returns an
unreachable URL. Compose uses 4841 during staging; move to 4840 only at cutover.

## Health check

`scripts/healthcheck.py` opens an OPC UA session, reads
`ServerStatus.State` and requires `Running`. An open TCP port is never treated
as healthy. Use a restricted read-only identity (`monitor` role) in production.

## Operations

- Logs: text or JSON (`GLADOS_LOG_JSON=true`); Compose rotates at 10 MB × 3.
- Shutdown: SIGTERM/SIGINT stops health/audit then the server; allow 30 s.
- Restart: command values reset to approved defaults. Nothing is replayed.
- Certificate expiry: startup refuses expired certificates and warns within 30 days.
- UaExpert: connect to `opc.tcp://<advertised-host>:<port>/server/`, accept the
  certificate, then browse Objects and verify representative NodeIDs.

## Rollback

See [migration.md](migration.md#rollback). Quiesce equipment, stop the new
server, restore the previous deployment and client configuration, verify, then
resume. Do not restore stale command values.
