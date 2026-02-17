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

"""Tests for run command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from mtd.commands.run_cmd import run


MOCK_PATH = "mtd.commands.run_cmd"


class TestRunCommand:
    """Tests for run command."""

    @patch(f"{MOCK_PATH}.run_service")
    @patch(f"{MOCK_PATH}.OperateApp")
    def test_run_success(
        self, mock_operate: MagicMock, mock_run_service: MagicMock
    ) -> None:
        """Test successful run."""
        mock_app = MagicMock()
        mock_operate.return_value = mock_app

        runner = CliRunner()
        result = runner.invoke(run, ["-c", "gnosis"])

        assert result.exit_code == 0
        mock_operate.assert_called_once()
        mock_app.setup.assert_called_once()
        mock_run_service.assert_called_once()

        call_kwargs = mock_run_service.call_args[1]
        assert call_kwargs["operate"] is mock_app
        assert call_kwargs["build_only"] is False
        assert call_kwargs["skip_dependency_check"] is False
        assert "config_mech_gnosis.json" in str(call_kwargs["config_path"])

    @patch(f"{MOCK_PATH}.run_service")
    @patch(f"{MOCK_PATH}.OperateApp")
    def test_run_all_chains(
        self, mock_operate: MagicMock, mock_run_service: MagicMock
    ) -> None:
        """Test run works for all supported chains."""
        mock_app = MagicMock()
        mock_operate.return_value = mock_app

        for chain in ("gnosis", "base", "polygon", "optimism"):
            runner = CliRunner()
            result = runner.invoke(run, ["-c", chain])
            assert result.exit_code == 0, f"Failed for chain {chain}: {result.output}"

            call_kwargs = mock_run_service.call_args[1]
            assert f"config_mech_{chain}.json" in str(call_kwargs["config_path"])

    def test_run_missing_chain_config(self) -> None:
        """Test run without required chain-config option."""
        runner = CliRunner()
        result = runner.invoke(run, [])

        assert result.exit_code != 0

    def test_run_invalid_chain_config(self) -> None:
        """Test run with invalid chain config."""
        runner = CliRunner()
        result = runner.invoke(run, ["-c", "invalid_chain"])

        assert result.exit_code != 0
        assert "Invalid value" in result.output or "invalid_chain" in result.output

    @patch(f"{MOCK_PATH}.run_service")
    @patch(f"{MOCK_PATH}.OperateApp")
    def test_run_service_failure(
        self, mock_operate: MagicMock, mock_run_service: MagicMock
    ) -> None:
        """Test run when run_service raises an error."""
        mock_app = MagicMock()
        mock_operate.return_value = mock_app
        mock_run_service.side_effect = Exception("Service failed to start")

        runner = CliRunner()
        result = runner.invoke(run, ["-c", "gnosis"])

        assert result.exit_code != 0
        assert "Service failed to start" in result.output

    def test_run_help(self) -> None:
        """Test run help output."""
        runner = CliRunner()
        result = runner.invoke(run, ["--help"])

        assert result.exit_code == 0
        assert "chain-config" in result.output
        assert "Run the mech agent service" in result.output
