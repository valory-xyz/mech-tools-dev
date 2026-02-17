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

"""Tests for add-tool command."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from mtd.commands.add_tool_cmd import add_tool


MOCK_PATH = "mtd.commands.add_tool_cmd"


class TestAddToolCommand:
    """Tests for add-tool command."""

    @patch(f"{MOCK_PATH}.get_package_manager")
    @patch(f"{MOCK_PATH}.generate_tool")
    def test_add_tool_success(
        self, mock_generate: MagicMock, mock_pkg_manager: MagicMock
    ) -> None:
        """Test successful tool addition."""
        mock_manager_instance = MagicMock()
        mock_pkg_manager.return_value = mock_manager_instance
        mock_manager_instance.update_package_hashes.return_value = (
            mock_manager_instance
        )

        runner = CliRunner()
        result = runner.invoke(add_tool, ["myauthor", "mytool"])

        assert result.exit_code == 0
        assert "Adding tool: myauthor/mytool" in result.output
        assert "Tool myauthor/mytool added" in result.output
        assert "Locking packages" in result.output
        mock_generate.assert_called_once_with("myauthor", "mytool", "A mech tool.")

    @patch(f"{MOCK_PATH}.generate_tool")
    def test_add_tool_with_skip_lock(self, mock_generate: MagicMock) -> None:
        """Test tool addition with --skip-lock."""
        runner = CliRunner()
        result = runner.invoke(add_tool, ["myauthor", "mytool", "--skip-lock"])

        assert result.exit_code == 0
        assert "Locking packages" not in result.output
        mock_generate.assert_called_once()

    @patch(f"{MOCK_PATH}.get_package_manager")
    @patch(f"{MOCK_PATH}.generate_tool")
    def test_add_tool_with_description(
        self, mock_generate: MagicMock, mock_pkg_manager: MagicMock
    ) -> None:
        """Test tool addition with custom description."""
        mock_manager_instance = MagicMock()
        mock_pkg_manager.return_value = mock_manager_instance
        mock_manager_instance.update_package_hashes.return_value = (
            mock_manager_instance
        )

        runner = CliRunner()
        result = runner.invoke(
            add_tool, ["myauthor", "mytool", "-d", "My custom tool."]
        )

        assert result.exit_code == 0
        mock_generate.assert_called_once_with("myauthor", "mytool", "My custom tool.")

    def test_add_tool_missing_author(self) -> None:
        """Test add-tool without author argument."""
        runner = CliRunner()
        result = runner.invoke(add_tool, [])

        assert result.exit_code != 0

    def test_add_tool_missing_tool_name(self) -> None:
        """Test add-tool without tool_name argument."""
        runner = CliRunner()
        result = runner.invoke(add_tool, ["myauthor"])

        assert result.exit_code != 0

    def test_add_tool_help(self) -> None:
        """Test add-tool help output."""
        runner = CliRunner()
        result = runner.invoke(add_tool, ["--help"])

        assert result.exit_code == 0
        assert "Add a new mech tool" in result.output
        assert "tool-description" in result.output
        assert "skip-lock" in result.output

    @patch(f"{MOCK_PATH}.generate_tool")
    def test_add_tool_generate_failure(self, mock_generate: MagicMock) -> None:
        """Test add-tool when generation fails."""
        mock_generate.side_effect = Exception("Template not found")

        runner = CliRunner()
        result = runner.invoke(add_tool, ["myauthor", "mytool", "--skip-lock"])

        assert result.exit_code != 0
        assert result.exception is not None
        assert "Template not found" in str(result.exception)
