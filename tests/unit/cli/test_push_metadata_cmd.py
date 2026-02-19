# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2025-2026 Valory AG
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

"""Tests for push-metadata command."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from mtd.commands.push_metadata_cmd import push_metadata


MOCK_PATH = "mtd.commands.push_metadata_cmd"


class TestPushMetadataCommand:
    """Tests for push-metadata command."""

    @patch(f"{MOCK_PATH}.push_metadata_to_ipfs")
    @patch(f"{MOCK_PATH}.generate_main")
    def test_push_metadata_success(
        self, mock_generate: MagicMock, mock_push: MagicMock
    ) -> None:
        """Test successful push-metadata."""
        runner = CliRunner()
        result = runner.invoke(push_metadata, [])

        assert result.exit_code == 0
        assert "Generating metadata" in result.output
        assert "Publishing metadata to IPFS" in result.output
        mock_generate.assert_called_once()
        mock_push.assert_called_once()

    @patch(f"{MOCK_PATH}.push_metadata_to_ipfs")
    @patch(f"{MOCK_PATH}.generate_main")
    def test_push_metadata_with_custom_ipfs_node(
        self, mock_generate: MagicMock, mock_push: MagicMock
    ) -> None:
        """Test push-metadata with custom IPFS node."""
        custom_node = "/dns/custom.node/tcp/5001/http"
        runner = CliRunner()
        result = runner.invoke(push_metadata, ["--ipfs-node", custom_node])

        assert result.exit_code == 0
        mock_push.assert_called_once_with(ipfs_node=custom_node)

    @patch(f"{MOCK_PATH}.push_metadata_to_ipfs")
    @patch(f"{MOCK_PATH}.generate_main")
    def test_push_metadata_uses_default_ipfs_node(
        self, mock_generate: MagicMock, mock_push: MagicMock
    ) -> None:
        """Test push-metadata uses default IPFS node when none specified."""
        from utils.publish_metadata import DEFAULT_IPFS_NODE

        runner = CliRunner()
        result = runner.invoke(push_metadata, [])

        assert result.exit_code == 0
        mock_push.assert_called_once_with(ipfs_node=DEFAULT_IPFS_NODE)

    @patch(f"{MOCK_PATH}.push_metadata_to_ipfs")
    @patch(f"{MOCK_PATH}.generate_main")
    def test_push_metadata_generate_failure(
        self, mock_generate: MagicMock, mock_push: MagicMock
    ) -> None:
        """Test push-metadata when generate fails."""
        mock_generate.side_effect = Exception("Failed to generate metadata")

        runner = CliRunner()
        result = runner.invoke(push_metadata, [])

        assert result.exit_code != 0
        assert result.exception is not None
        assert "Failed to generate metadata" in str(result.exception)
        mock_push.assert_not_called()

    @patch(f"{MOCK_PATH}.push_metadata_to_ipfs")
    @patch(f"{MOCK_PATH}.generate_main")
    def test_push_metadata_ipfs_failure(
        self, mock_generate: MagicMock, mock_push: MagicMock
    ) -> None:
        """Test push-metadata when IPFS push fails."""
        mock_push.side_effect = Exception("IPFS connection failed")

        runner = CliRunner()
        result = runner.invoke(push_metadata, [])

        assert result.exit_code != 0
        assert result.exception is not None
        assert "IPFS connection failed" in str(result.exception)

    def test_push_metadata_help(self) -> None:
        """Test push-metadata help output."""
        runner = CliRunner()
        result = runner.invoke(push_metadata, ["--help"])

        assert result.exit_code == 0
        assert "ipfs-node" in result.output
        assert "Generate metadata.json" in result.output
