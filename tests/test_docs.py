"""The generated documentation page must track configuration exactly."""

from __future__ import annotations

from glados_opcua.docs import build_docs
from glados_opcua.docs import main as docs_main

from .conftest import REPO, manifest_for


def test_docs_page_is_current():
    manifest = manifest_for(REPO / "config")
    rendered = build_docs(manifest)
    page = REPO / "docs" / "index.md"
    assert page.is_file(), "generate docs/index.md with: python -m glados_opcua --docs docs/index.md"
    assert page.read_text(encoding="utf-8") == rendered


def test_docs_contain_every_legacy_node():
    manifest = manifest_for(REPO / "config")
    rendered = build_docs(manifest)
    for equipment in manifest.equipment:
        assert equipment.name in rendered
        for variable in equipment.variables:
            assert f"`{variable.node_id}`" in rendered
    assert rendered.count("| `ns=") >= 488


def test_docs_check_cli_passes():
    assert docs_main(["--config", str(REPO / "config"), "--check"]) == 0
