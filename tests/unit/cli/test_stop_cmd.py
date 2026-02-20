# -*- coding: utf-8 -*-
"""Tests for stop command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from mtd.commands.stop_cmd import stop


MOCK_PATH = "mtd.commands.stop_cmd"


class TestStopCommand:
    """Tests for stop command."""

    @patch(f"{MOCK_PATH}.stop_service")
    @patch(f"{MOCK_PATH}.OperateApp")
    @patch(f"{MOCK_PATH}.require_initialized")
    @patch(f"{MOCK_PATH}.get_mtd_context")
    def test_stop_success(
        self,
        mock_get_context: MagicMock,
        mock_require_initialized: MagicMock,
        mock_operate: MagicMock,
        mock_stop_service: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test successful stop."""
        context = MagicMock()
        context.workspace_path = tmp_path
        context.config_dir = tmp_path / "config"
        context.config_dir.mkdir(parents=True)
        (context.config_dir / "config_mech_gnosis.json").write_text("{}", encoding="utf-8")
        mock_get_context.return_value = context

        mock_app = MagicMock()
        mock_operate.return_value = mock_app

        runner = CliRunner()
        result = runner.invoke(stop, ["-c", "gnosis"])

        assert result.exit_code == 0
        mock_require_initialized.assert_called_once_with(context)
        mock_stop_service.assert_called_once()

    def test_stop_missing_chain_config(self) -> None:
        """Test stop without required chain-config option."""
        runner = CliRunner()
        result = runner.invoke(stop, [])
        assert result.exit_code != 0
