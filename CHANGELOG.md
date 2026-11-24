# Changelog

## 2.0.0 — 2026-11-24

Rewrite of the monolithic legacy server into a configuration-driven package.
The OPC UA interface is unchanged for the 18 legacy objects.

### Compatibility evidence

- Static AST extraction of `legacy/server_opcua.py`: 18 `add_object`, 488
  `add_variable`, 482 `set_writable` calls.
- Runtime baseline exported from an isolated legacy instance on `asyncua 1.1.8`.
- New server address-space export diffed field-for-field against the baseline:
  506 nodes (18 objects, 488 variables) with zero differences in NodeIDs, browse
  names, display names, parents, references, data types, value ranks, access
  levels and defaults.
- Four variables are intentionally `Int64` (`R3d_BaseA`, `C1d_Img_h`, `C1d_Img_w`,
  `RGBc_ProgID`); six Robot 2 variables remain read-only.

### Changed

- YAML configuration with Pydantic validation; malformed configuration fails
  before the socket opens.
- Exact NamespaceArray construction with deterministic placeholders for gaps.
  Index 1 remains the application namespace hosting `Operator`.
- Supported security APIs replace private attributes. Production requires
  certificates, validated credentials and per-node write authorization at the
  service boundary.
- Additive health namespace (`Health/<Equipment>.{Status,Heartbeat,LastSeen,
  DataValid,ErrorCode,ErrorMessage}`) with monotonic stale detection.
- Graceful SIGINT/SIGTERM shutdown, structured logging, audit logging.
- Docker packaging, health check, CI, generated documentation.

### Known compatibility notes

- The NamespaceArray now registers URIs for indexes 2–53 (previously only 0 and
  1 existed). Indexes are unchanged; this is additive.
- Equipment object `Description` attributes are populated (additive metadata).
- No command values are persisted or replayed across restart.
- Ownership of `LabCount`, `MagCount` and `MagInfo` is unconfirmed; they are
  admin-only in production until reviewed.
- Client configuration must be migrated for secure endpoints before cutover.
