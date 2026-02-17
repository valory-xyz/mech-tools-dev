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

"""Tests for stop command."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from mtd.commands.stop_cmd import stop


MOCK_PATH = "mtd.commands.stop_cmd"


class TestStopCommand:
    """Tests for stop command."""

    @patch(f"{MOCK_PATH}.stop_service")
    @patch(f"{MOCK_PATH}.OperateApp")
    def test_stop_success(
        self, mock_operate: MagicMock, mock_stop_service: MagicMock
    ) -> None:
        """Test successful stop."""
        mock_app = MagicMock()
        mock_operate.return_value = mock_app

        runner = CliRunner()
        result = runner.invoke(stop, ["-c", "gnosis"])

        assert result.exit_code == 0
        mock_operate.assert_called_once()
        mock_app.setup.assert_called_once()
        mock_stop_service.assert_called_once()

        call_kwargs = mock_stop_service.call_args[1]
        assert call_kwargs["operate"] is mock_app
        assert "config_mech_gnosis.json" in str(call_kwargs["config_path"])

    @patch(f"{MOCK_PATH}.stop_service")
    @patch(f"{MOCK_PATH}.OperateApp")
    def test_stop_all_chains(
        self, mock_operate: MagicMock, mock_stop_service: MagicMock
    ) -> None:
        """Test stop works for all supported chains."""
        mock_app = MagicMock()
        mock_operate.return_value = mock_app

        for chain in ("gnosis", "base", "polygon", "optimism"):
            runner = CliRunner()
            result = runner.invoke(stop, ["-c", chain])
            assert result.exit_code == 0, f"Failed for chain {chain}: {result.output}"

    def test_stop_missing_chain_config(self) -> None:
        """Test stop without required chain-config option."""
        runner = CliRunner()
        result = runner.invoke(stop, [])

        assert result.exit_code != 0

    def test_stop_invalid_chain_config(self) -> None:
        """Test stop with invalid chain config."""
        runner = CliRunner()
        result = runner.invoke(stop, ["-c", "invalid_chain"])

        assert result.exit_code != 0

    @patch(f"{MOCK_PATH}.stop_service")
    @patch(f"{MOCK_PATH}.OperateApp")
    def test_stop_service_failure(
        self, mock_operate: MagicMock, mock_stop_service: MagicMock
    ) -> None:
        """Test stop when stop_service raises an error."""
        mock_app = MagicMock()
        mock_operate.return_value = mock_app
        mock_stop_service.side_effect = Exception("Service failed to stop")

        runner = CliRunner()
        result = runner.invoke(stop, ["-c", "gnosis"])

        assert result.exit_code != 0
        assert "Service failed to stop" in result.output

    def test_stop_help(self) -> None:
        """Test stop help output."""
        runner = CliRunner()
        result = runner.invoke(stop, ["--help"])

        assert result.exit_code == 0
        assert "chain-config" in result.output
        assert "Stop the mech agent service" in result.output
