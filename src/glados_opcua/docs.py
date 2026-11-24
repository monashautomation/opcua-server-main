"""Deterministic, self-documenting reference generator.

The generated page is derived from the live validated manifest, so it cannot
drift from the address space: every NodeId, data type, default, access level,
namespace and permission owner is rendered from the same objects the server
uses.  Module docstrings are included so the architecture section stays
accurate as code changes.

Usage:
    python -m glados_opcua.docs --config config --output docs/index.md
    python -m glados_opcua.docs --check      # fail if the page is stale
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import os
import pkgutil
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .models import DataType, Manifest
from .validation import ConfigurationError, load_manifest


def _cell(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def _table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    lines.extend("| " + " | ".join(_cell(value) for value in row) + " |" for row in rows)
    return lines


def _default_text(data_type: DataType, value: Any) -> str:
    if data_type is DataType.ByteString:
        return f"`{bytes(value).hex()}` ({len(value)} bytes)"
    if isinstance(value, bool):
        return "true" if value else "false"
    if value == "":
        return '`""`'
    return f"`{value}`"


def _module_map() -> list[list[str]]:
    package = importlib.import_module("glados_opcua")
    rows: list[list[str]] = []
    for module_info in sorted(pkgutil.iter_modules(package.__path__), key=lambda item: item.name):
        try:
            module = importlib.import_module(f"glados_opcua.{module_info.name}")
        except Exception as exc:  # pragma: no cover - defensive for optional deps
            rows.append([f"`{module_info.name}`", f"(import failed: {exc})"])
            continue
        summary = inspect.getdoc(module) or ""
        first = summary.splitlines()[0] if summary else ""
        rows.append([f"`{module_info.name}.py`", first])
    return rows


def build_docs(manifest: Manifest) -> str:
    """Render the complete documentation page as Markdown."""
    server = manifest.server
    namespaces = manifest.namespaces.namespaces
    summary = manifest.summary()
    lines: list[str] = [
        "# GLaDOS OPC UA server reference",
        "",
        f"Generated from `config/` by `python -m glados_opcua.docs`. Package version **{__version__}**.",
        "Do not edit by hand: edit configuration or code, then regenerate.",
        "",
        "> This server is a communication layer, not a safety system. Interlocks,",
        "> emergency stops and motion validation must remain in independent",
        "> safety-rated systems.",
        "",
        "## Server",
        "",
        *_table(
            ["Setting", "Value"],
            [
                ["Profile", f"`{server.profile.value}`"],
                ["Endpoint", f"`{server.endpoint}`"],
                ["Server name", f"`{server.name}`"],
                ["Application URI", f"`{server.application_uri}`"],
                ["Bind override", f"`{server.bind_address or 'from endpoint'}:{server.bind_port or 'from endpoint'}`"],
                ["Objects", summary["objects"]],
                ["Variables", summary["variables"]],
                ["Writable variables", summary["writable"]],
                ["Health namespace", "enabled" if server.health.enabled else "disabled"],
                ["Permissions enforced", "yes" if manifest.permissions.enforced else "no"],
            ],
        ),
        "",
        "## Security posture",
        "",
        *_table(
            ["Setting", "Value"],
            [
                ["Policies", ", ".join(f"`{policy.value}`" for policy in server.security.policies)],
                ["Identity tokens", ", ".join(f"`{token.value}`" for token in server.security.identity_tokens)],
                ["Anonymous allowed", "yes" if server.security.allow_anonymous else "no"],
                ["Insecure legacy acknowledged", "yes" if server.security.allow_insecure_legacy else "no"],
                ["Server certificate", f"`{server.security.certificate}`"],
                ["Configured users", len(server.security.users)],
            ],
        ),
        "",
        "Production requires `Basic256Sha256_SignAndEncrypt` or stronger, configured",
        "users with `password_env`/client certificates, and `permissions.enforced: true`.",
        "The legacy profile disables password validation by design and must be isolated.",
        "",
        "## Namespaces",
        "",
        *_table(
            ["Index", "URI", "Kind", "Description"],
            [[entry.index, f"`{entry.uri}`", entry.kind.value, entry.description or ""] for entry in namespaces],
        ),
        "",
    ]
    reserved = sorted(set(range(max(entry.index for entry in namespaces) + 2)) - {entry.index for entry in namespaces})
    if reserved:
        lines += [
            f"Indexes {reserved} are reserved placeholders (`urn:glados:opcua:reserved:<index>`) so numeric",
            "indexes never shift. Health index 54 is registered when health is enabled.",
            "",
        ]

    lines += [
        "## Equipment",
        "",
        *_table(
            ["Object", "Namespace", "NodeId", "Variables", "Writable", "Description"],
            [
                [
                    item.name,
                    item.namespace,
                    f"`{item.node_id}`",
                    len(item.variables),
                    sum(1 for variable in item.variables if variable.writable),
                    item.description or "",
                ]
                for item in manifest.equipment
            ],
        ),
        "",
        "## Node reference",
        "",
        "Browse names use namespace 0 unless stated otherwise. NodeIds are exact and",
        "include legacy punctuation such as trailing semicolons.",
        "",
    ]
    for item in manifest.equipment:
        lines += [f"### {item.name}", "", f"Object NodeId `{item.node_id}`, namespace `{item.namespace}`.", ""]
        lines += _table(
            ["Browse name", "NodeId", "Data type", "Default", "Writable", "Category", "Writer"],
            [
                [
                    variable.browse_name,
                    f"`{variable.node_id}`",
                    variable.data_type.value,
                    _default_text(variable.data_type, variable.default),
                    "yes" if variable.writable else "no",
                    variable.category.value,
                    variable.writer.value,
                ]
                for variable in item.variables
            ],
        )
        notes = [f"- **{variable.browse_name}**: {variable.note}" for variable in item.variables if variable.note]
        if notes:
            lines += ["", *notes]
        lines.append("")

    if server.health.enabled:
        lines += [
            "## Health namespace",
            "",
            f"Namespace `{server.health.namespace}` (`{server.health.uri}`) publishes per-equipment:",
            "",
            *_table(
                ["Node", "Data type", "Meaning"],
                [
                    ["`Health/<Equipment>.Status`", "String", "Unknown, Online or Stale"],
                    ["`Health/<Equipment>.Heartbeat`", "Int32", "Device-owned writes observed"],
                    ["`Health/<Equipment>.LastSeen`", "DateTime", "UTC time of last authorized write"],
                    ["`Health/<Equipment>.DataValid`", "Boolean", "False until telemetry arrives and while stale"],
                    ["`Health/<Equipment>.ErrorCode`", "Int32", "0 none, 1 no data, 2 stale"],
                    ["`Health/<Equipment>.ErrorMessage`", "String", "Human-readable detail"],
                ],
            ),
            "",
            f"A device becomes stale after {server.health.stale_after_seconds:g}s without an authorized write; "
            f"polling runs every {server.health.poll_interval_seconds:g}s. Timing uses a monotonic clock.",
            "",
        ]

    lines += [
        "## Permissions",
        "",
        f"Enforcement: {'enabled' if manifest.permissions.enforced else 'disabled (legacy profile)'}. "
        "A batched write containing any unauthorized NodeId is rejected as a whole.",
        "",
        *_table(
            ["Role", "Read", "Writable owners"],
            [
                [
                    name,
                    "yes" if permission.read else "no",
                    "all writable variables"
                    if permission.write_all
                    else (", ".join(owner.value for owner in permission.write_by_writer) or "none"),
                ]
                for name, permission in sorted(manifest.permissions.roles.items())
            ],
        ),
        "",
    ]
    if manifest.permissions.denied:
        lines += ["Explicitly denied patterns: " + ", ".join(f"`{p}`" for p in manifest.permissions.denied), ""]
    users = server.security.users
    if users:
        lines += [
            *_table(
                ["User", "Role", "Equipment scope", "Credential"],
                [
                    [
                        user.username,
                        user.role.value,
                        ", ".join(user.equipment) if user.equipment else "all",
                        f"env `{user.password_env}`" if user.password_env else f"cert `{user.certificate}`",
                    ]
                    for user in users
                ],
            ),
            "",
        ]

    lines += [
        "## Package modules",
        "",
        *_table(["Module", "Responsibility"], _module_map()),
        "",
        "## Configuration and commands",
        "",
        "| Path | Purpose |",
        "|---|---|",
        "| `config/server.yaml` | Endpoint, profile, security, health |",
        "| `config/namespaces.yaml` | Generated exact legacy namespace indexes and URIs |",
        "| `config/namespaces.extra.yaml` | Optional additive namespaces for new equipment |",
        "| `config/devices/*.yaml` | Generated legacy inventory (objects and variables) |",
        "| `config/permissions.yaml` | Role matrix and denied patterns |",
        "| `legacy/server_opcua.py` | Archived original implementation |",
        "| `scripts/migrate_legacy.py` | AST extraction and static/runtime comparison |",
        "| `scripts/export_nodes.py` | Address-space export used for parity fixtures |",
        "| `scripts/generate_certificates.py` | Self-signed server certificate (0600 key) |",
        "| `scripts/healthcheck.py` | OPC UA-aware container health check |",
        "",
        "```bash",
        "python -m glados_opcua --validate              # load and validate configuration",
        "python -m glados_opcua --docs docs/index.md    # regenerate this page",
        "python -m glados_opcua.docs --check            # fail if this page is stale",
        "python -m glados_opcua                          # run the server",
        "pytest                                          # compatibility and security tests",
        "```",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate or verify the GLaDOS OPC UA docs page.")
    parser.add_argument(
        "--config", default=None, help="configuration directory (default: $GLADOS_CONFIG_DIR or config)"
    )
    parser.add_argument("--output", type=Path, default=Path("docs/index.md"))
    parser.add_argument("--check", action="store_true", help="exit non-zero if the page is stale")
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest(args.config or os.environ.get("GLADOS_CONFIG_DIR", "config"))
    except (ConfigurationError, ValueError) as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2
    rendered = build_docs(manifest)
    if args.check:
        existing = args.output.read_text(encoding="utf-8") if args.output.exists() else ""
        if existing != rendered:
            print(f"{args.output} is stale; run: python -m glados_opcua.docs --output {args.output}", file=sys.stderr)
            return 1
        print(f"{args.output} is up to date")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"wrote {args.output} ({len(rendered.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
