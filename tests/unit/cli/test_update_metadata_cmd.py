# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2025 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""Tests for update-metadata command."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from mtd.commands.update_metadata_cmd import update_metadata


MOCK_PATH = "mtd.commands.update_metadata_cmd"


class TestUpdateMetadataCommand:
    """Tests for update-metadata command."""

    @patch(f"{MOCK_PATH}.update_main")
    def test_update_metadata_success(self, mock_update: MagicMock) -> None:
        """Test successful update-metadata."""
        runner = CliRunner()
        result = runner.invoke(update_metadata, [])

        assert result.exit_code == 0
        assert "Updating metadata hash on-chain" in result.output
        mock_update.assert_called_once()

    @patch(f"{MOCK_PATH}.update_main")
    def test_update_metadata_failure(self, mock_update: MagicMock) -> None:
        """Test update-metadata when update fails."""
        mock_update.side_effect = Exception("Transaction failed")

        runner = CliRunner()
        result = runner.invoke(update_metadata, [])

        assert result.exit_code != 0
        assert result.exception is not None
        assert "Transaction failed" in str(result.exception)

    def test_update_metadata_help(self) -> None:
        """Test update-metadata help output."""
        runner = CliRunner()
        result = runner.invoke(update_metadata, ["--help"])

        assert result.exit_code == 0
        assert "Update the metadata hash on-chain" in result.output

    def test_update_metadata_no_args_required(self) -> None:
        """Test update-metadata takes no arguments."""
        runner = CliRunner()
        result = runner.invoke(update_metadata, ["extra_arg"])

        assert result.exit_code != 0
