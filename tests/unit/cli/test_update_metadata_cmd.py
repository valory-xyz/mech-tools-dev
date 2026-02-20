# -*- coding: utf-8 -*-
"""Tests for update-metadata command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from mtd.commands.update_metadata_cmd import update_metadata


MOCK_PATH = "mtd.commands.update_metadata_cmd"


class TestUpdateMetadataCommand:
    """Tests for update-metadata command."""

    @patch(f"{MOCK_PATH}.update_metadata_onchain", return_value=(True, "0xtx"))
    @patch(f"{MOCK_PATH}.require_initialized")
    @patch(f"{MOCK_PATH}.get_mtd_context")
    def test_update_metadata_success(
        self,
        mock_get_context: MagicMock,
        mock_require_initialized: MagicMock,
        mock_update: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test successful update-metadata."""
        context = MagicMock()
        context.env_path = tmp_path / ".env"
        context.keys_dir = tmp_path / "keys"
        mock_get_context.return_value = context

        runner = CliRunner()
        result = runner.invoke(update_metadata, [])

        assert result.exit_code == 0
        mock_require_initialized.assert_called_once_with(context)
        mock_update.assert_called_once_with(
            env_path=context.env_path,
            private_key_path=context.keys_dir / "ethereum_private_key.txt",
        )

    def test_update_metadata_help(self) -> None:
        """Test update-metadata help output."""
        runner = CliRunner()
        result = runner.invoke(update_metadata, ["--help"])

        assert result.exit_code == 0
        assert "Update the metadata hash on-chain" in result.output
