"""GLaDOS OPC UA server v2.

A configuration-driven replacement for ``legacy/server_opcua.py``.  The public
interface (NodeIDs, browse names, namespaces, data types, defaults and access
levels) is treated as a frozen contract; everything in this package exists to
serve that contract safely and testably.

Layout:
    settings.py            Environment overlay and profile rules.
    models.py              Validated configuration and manifest models.
    validation.py          YAML loading, cross-reference checks, CLI summary.
    namespaces.py          Exact NamespaceArray construction (no index drift).
    node_factory.py        Typed address-space creation from a manifest.
    equipment_registry.py  Built equipment and NodeId lookup.
    permissions.py         Role matrix and service-boundary enforcement.
    security.py            Certificates, identity tokens, user managers.
    health.py              Additive heartbeat/staleness monitor.
    server.py              Startup ordering and graceful shutdown.
    logging_config.py      Text or JSON structured logs.
    docs.py                Deterministic documentation generator.
"""

__version__ = "2.0.0"

SERVER_PRODUCT_URI = "urn:glados:opcua:server"
