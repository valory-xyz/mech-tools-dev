# -*- coding: utf-8 -*-
"""Tests for mtd context helpers."""

from pathlib import Path

from mtd.context import build_context, get_default_workspace, resolve_workspace_path


def test_get_default_workspace() -> None:
    """Default workspace should point to ~/.operate_mtd."""
    assert get_default_workspace() == Path("~/.operate_mtd").expanduser().resolve()


def test_resolve_workspace_path_uses_default() -> None:
    """Workspace resolver should always return default workspace."""
    assert resolve_workspace_path() == get_default_workspace()


def test_context_is_initialized_false_then_true(tmp_path, monkeypatch) -> None:
    """Context init flag should reflect marker/config/env presence."""
    monkeypatch.setenv("HOME", str(tmp_path))
    context = build_context()
    context.ensure_workspace_exists()

    assert context.is_initialized() is False

    context.config_dir.mkdir(parents=True, exist_ok=True)
    context.env_path.write_text("", encoding="utf-8")
    context.initialized_marker_path.write_text("initialized\n", encoding="utf-8")

    assert context.is_initialized() is True
