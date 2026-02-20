# -*- coding: utf-8 -*-
"""Tests for packaged runtime resources."""

from mtd.context import build_context
from mtd.resources import (
    copy_runtime_templates_to_workspace,
    iter_runtime_templates,
    read_text_resource,
)


def test_read_text_resource() -> None:
    """Runtime env template should be loadable from package resources."""
    content = read_text_resource("mtd.templates.runtime", ".example.env")
    assert "DEFAULT_CHAIN_ID" in content


def test_iter_runtime_templates_contains_chain_configs() -> None:
    """Runtime templates iterator should include chain config templates."""
    template_names = {name for name, _ in iter_runtime_templates()}
    assert "config_mech_gnosis.json" in template_names
    assert "config_mech_base.json" in template_names


def test_copy_runtime_templates_to_workspace(tmp_path, monkeypatch) -> None:
    """Copying runtime templates should materialize expected files."""
    monkeypatch.setenv("HOME", str(tmp_path))
    context = build_context()
    copy_runtime_templates_to_workspace(context)

    assert (context.config_dir / "config_mech_gnosis.json").exists()
    assert (context.workspace_path / ".example.env").exists()
