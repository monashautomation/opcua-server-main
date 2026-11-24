# Migration and compatibility

## Evidence chain

| Stage | Artefact | Result |
|---|---|---|
| Archived source | `legacy/server_opcua.py` + SHA-256 | `15c30f8b…6d0487` |
| Static extraction | `src/glados_opcua/legacy_parser.py` | 18 objects, 488 variables, 482 writable |
| Runtime baseline | `tests/fixtures/legacy_nodes.json` | 506 custom nodes (18 objects + 488 variables) |
| Generated config | `config/devices/*.yaml`, `config/namespaces.yaml` | Reproducible via `scripts/migrate_legacy.py` |
| Parity gate | `tests/test_compatibility.py` | Zero differences in compared attributes/references |

The legacy server was run unmodified against `asyncua==1.1.8` on an isolated
loopback port, then exported with `scripts/export_nodes.py`. The static AST
extraction is compared against that export by `scripts/migrate_legacy.py`; any
discrepancy aborts generation.

To refresh the baseline (isolated network only):

```bash
GLADOS_SERVER_URL='opc.tcp://127.0.0.1:4841/server/' python legacy/server_opcua.py &
python scripts/export_nodes.py 'opc.tcp://127.0.0.1:4841/server/' /tmp/legacy.json
python scripts/migrate_legacy.py --baseline /tmp/legacy.json --output /tmp/config
```

> The exported baseline includes standard server nodes. `legacy_nodes.json` is
> filtered to objects whose NodeId namespace index is non-zero and their
> children, which is the compatibility contract.

## Approved differences (additive only)

1. **NamespaceArray URIs.** Legacy registered only indexes 0 and 1; the rewrite
   registers stable URIs for the used indexes and reserved placeholders for
   gaps. Numeric indexes, object IDs and NodeIDs are unchanged.
2. **Equipment descriptions.** Object `Description` attributes are populated
   from configuration. Existing clients resolving NodeIDs/browse paths are not
   affected.
3. **Optional health namespace.** Disabled in strict legacy parity mode; when
   enabled it is a new namespace index (54) with new nodes only.
4. **Audit logs and structured logging.** Operational output only.

No legacy data type, default, value encoding, access level, browse name or
NodeID has been changed.

## Unconfirmed legacy ownership

- `LabCount`, `MagCount`, `MagInfo`: no naming or source evidence identifies the
  writer. They are `writer: admin` in generated YAML and therefore admin-only in
  production until a client review confirms ownership.
- Six Robot 2 variables were never writable (`R2c_int4`, `R2c_int5`, `R2c_int6`,
  `R2c_Bool1`, `R2c_Bool2`, `R2c_Bool3`). They remain read-only. Confirm whether
  equipment wrappers depend on writes before changing this.

## Client migration

Legacy clients using `NoSecurity`/anonymous must be reconfigured for
`Basic256Sha256_SignAndEncrypt` and username or X.509 identity before production
cutover. There is no automatic downgrade. Inventory clients first and record
their endpoint, identity and expected handshake.

## Cutover

1. Approve the compatibility report, security test report and client list.
2. Back up images, configuration, certificates and deployment metadata.
3. Place equipment in a verified safe state and quiesce controllers.
4. Run the new server on an isolated port (4841) and verify with UaExpert and
   representative clients.
5. Only then move the production endpoint/port (4840) during maintenance.
6. Reconnect clients in a controlled order and verify telemetry and authorized
   handshakes before resuming operation.

Never connect two active control systems to the same physical equipment for
comparison testing. Never replay buffered or persisted commands.

## Rollback

If compatibility, connectivity, security or operational checks fail: quiesce
equipment, stop the new server, restore the previous deployment and client
configuration, and verify the old service before resuming. Retain the previous
container and configuration until acceptance. Restore whichever server actually
served the affected clients; do not assume open62541. Do not restore stale
command values.

## Change policy

Configuration schemas and the golden manifest are versioned (`config_version: 1`).
Every difference from the golden manifest requires review. New nodes go in a
new stable namespace, never reused legacy IDs. Breaking interface changes require
an explicitly approved major version and a documented client migration window.
