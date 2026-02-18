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

"""Tests for setup command."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from mtd.commands.setup_cmd import setup as setup_command


MOD = "mtd.commands.setup_cmd"


class TestSetupCommand:
    """Tests for setup command."""

    @patch(f"{MOD}.run_setup")
    def test_setup_success(self, mock_run_setup: MagicMock) -> None:
        """Test setup delegates to setup flow with selected chain."""
        runner = CliRunner()
        result = runner.invoke(setup_command, ["-c", "gnosis"])

        assert result.exit_code == 0
        mock_run_setup.assert_called_once_with(chain_config="gnosis")

    @patch(f"{MOD}.run_setup")
    def test_setup_all_supported_chains(self, mock_run_setup: MagicMock) -> None:
        """Test setup works for all supported chains."""
        for chain in ("gnosis", "base", "polygon", "optimism"):
            runner = CliRunner()
            result = runner.invoke(setup_command, ["-c", chain])
            assert result.exit_code == 0, f"Failed for chain {chain}: {result.output}"

    @patch(f"{MOD}.run_setup")
    def test_setup_propagates_errors(self, mock_run_setup: MagicMock) -> None:
        """Test setup surfaces underlying setup flow errors."""
        mock_run_setup.side_effect = Exception("setup failed")

        runner = CliRunner()
        result = runner.invoke(setup_command, ["-c", "gnosis"])

        assert result.exit_code != 0
        assert result.exception is not None
        assert "setup failed" in str(result.exception)

    def test_setup_missing_chain_config(self) -> None:
        """Test setup without required chain-config option."""
        runner = CliRunner()
        result = runner.invoke(setup_command, [])

        assert result.exit_code != 0
        assert "Missing option" in result.output or "chain-config" in result.output

    def test_setup_invalid_chain_config(self) -> None:
        """Test setup with invalid chain config."""
        runner = CliRunner()
        result = runner.invoke(setup_command, ["-c", "invalid_chain"])

        assert result.exit_code != 0
        assert "Invalid value" in result.output or "invalid_chain" in result.output

    def test_setup_help(self) -> None:
        """Test setup help output."""
        runner = CliRunner()
        result = runner.invoke(setup_command, ["--help"])

        assert result.exit_code == 0
        assert "chain-config" in result.output
        assert "Setup on-chain requirements" in result.output
