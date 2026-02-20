# -*- coding: utf-8 -*-
"""Tests for push-metadata command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from mtd.commands.push_metadata_cmd import push_metadata


MOCK_PATH = "mtd.commands.push_metadata_cmd"


class TestPushMetadataCommand:
    """Tests for push-metadata command."""

    @patch(f"{MOCK_PATH}.set_key")
    @patch(f"{MOCK_PATH}.publish_metadata_to_ipfs", return_value="f0170abc")
    @patch(f"{MOCK_PATH}.generate_metadata")
    @patch(f"{MOCK_PATH}.require_initialized")
    @patch(f"{MOCK_PATH}.get_mtd_context")
    def test_push_metadata_success(
        self,
        mock_get_context: MagicMock,
        mock_require_initialized: MagicMock,
        mock_generate: MagicMock,
        mock_publish: MagicMock,
        mock_set_key: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test successful push-metadata."""
        context = MagicMock()
        context.packages_dir = tmp_path / "packages"
        context.metadata_path = tmp_path / "metadata.json"
        context.env_path = tmp_path / ".env"
        mock_get_context.return_value = context

        runner = CliRunner()
        result = runner.invoke(push_metadata, [])

        assert result.exit_code == 0
        mock_require_initialized.assert_called_once_with(context)
        mock_generate.assert_called_once_with(
            packages_dir=context.packages_dir,
            metadata_path=context.metadata_path,
        )
        mock_publish.assert_called_once()
        mock_set_key.assert_called_once_with(str(context.env_path), "METADATA_HASH", "f0170abc")
