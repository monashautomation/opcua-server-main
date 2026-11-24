# GLaDOS OPC UA server v2

Configuration-driven replacement for the legacy GLaDOS OPC UA server. The legacy
wire interface is frozen and verified against a runtime export: **18 objects,
488 variables, 482 writable**, with exact NodeIDs, browse names, namespace
indexes, data types, defaults and access levels.

> This is a communication layer, **not** a safety system. Interlocks, emergency
> stops and motion validation belong in independently safety-rated systems.

- Generated reference: [`docs/index.md`](docs/index.md)
- Security policy: [`SECURITY.md`](SECURITY.md)
- License: MIT

## Quick start (isolated legacy parity)

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
python -m glados_opcua --validate        # 18 objects / 488 variables / 482 writable
python -m glados_opcua                   # legacy profile, opc.tcp://0.0.0.0:4840/server/
pytest -q
```

The shipped `config/server.yaml` selects the **legacy** profile and requires
`security.allow_insecure_legacy: true`. It accepts anonymous clients and does
not validate passwords. Use it only on an isolated test network.

## Production

```bash
cp config/examples/server.production.yaml config/server.yaml
cp config/examples/permissions.production.yaml config/permissions.yaml
python scripts/generate_certificates.py --hostname opcua.lab.example --ip 172.20.0.152
export GLADOS_PASSWORD_ADMIN='…' GLADOS_PASSWORD_HEALTH='…'
cp .env.example .env                       # set the same values, never commit
docker compose up -d
```

Production requires `Basic256Sha256_SignAndEncrypt` or stronger, configured
users, no anonymous access, no `NoSecurity`, and enforced permissions. Startup
fails closed if any of those are missing. See [`docs/deployment.md`](docs/deployment.md).

## How compatibility is proven

| Check | Command |
|---|---|
| AST extraction vs. runtime legacy export | `python scripts/migrate_legacy.py` |
| Generated config vs. manifest / namespaces | `pytest tests/test_compatibility.py` |
| Full address-space diff (NodeIDs, types, values, refs) | `pytest tests/test_compatibility.py` |
| Production auth and role boundaries | `pytest tests/test_security.py tests/test_permissions.py` |

`tests/fixtures/legacy_nodes.json` is the frozen golden manifest exported from
an isolated instance of `legacy/server_opcua.py` running on `asyncua 1.1.8`.

## Layout

```text
config/              server, namespaces, permissions, generated device inventory
src/glados_opcua/    server, validation, security, permissions, health, docs
legacy/              archived original server and checksum
scripts/             migration, export, certificates, health check
tests/               configuration, parity, protocol, security, health tests
docs/                generated reference and operator guides
```

## Adding a device

Device configuration is a flat inventory generated from legacy source. Adding an
equipment group of an existing type is a YAML-only change: copy an object block,
give it a new object NodeId in its own namespace, and declare each variable's
exact NodeId, type, default, writability and `writer`. Regenerate docs and run
the suite. See [`docs/adding_devices.md`](docs/adding_devices.md).
