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

"""Tests for run command."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from mtd.commands.run_cmd import run


MOCK_PATH = "mtd.commands.run_cmd"


class TestRunCommand:
    """Tests for run command."""

    @patch(f"{MOCK_PATH}.run_service")
    @patch(f"{MOCK_PATH}.OperateApp")
    def test_run_success(
        self,
        mock_operate: MagicMock,
        mock_run_service: MagicMock,
    ) -> None:
        """Test successful run in production mode."""
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
        self,
        mock_operate: MagicMock,
        mock_run_service: MagicMock,
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
        self,
        mock_operate: MagicMock,
        mock_run_service: MagicMock,
    ) -> None:
        """Test run when run_service raises an error."""
        mock_app = MagicMock()
        mock_operate.return_value = mock_app
        mock_run_service.side_effect = Exception("Service failed to start")

        runner = CliRunner()
        result = runner.invoke(run, ["-c", "gnosis"])

        assert result.exit_code != 0
        assert result.exception is not None
        assert "Service failed to start" in str(result.exception)

    def test_run_help(self) -> None:
        """Test run help output."""
        runner = CliRunner()
        result = runner.invoke(run, ["--help"])

        assert result.exit_code == 0
        assert "chain-config" in result.output
        assert "--dev" in result.output
        assert "Run the mech agent service" in result.output


class TestRunDevMode:
    """Tests for run --dev mode."""

    @patch(f"{MOCK_PATH}._run_dev_mode")
    def test_run_dev_flag_delegates(self, mock_dev_mode: MagicMock) -> None:
        """Test that --dev flag delegates to _run_dev_mode."""
        runner = CliRunner()
        result = runner.invoke(run, ["-c", "gnosis", "--dev"])

        assert result.exit_code == 0
        mock_dev_mode.assert_called_once()

    @patch(f"{MOCK_PATH}.run_service")
    @patch(f"{MOCK_PATH}.OperateApp")
    @patch(f"{MOCK_PATH}._get_latest_service_hash", return_value="bafybei123")
    @patch(f"{MOCK_PATH}.subprocess")
    def test_run_dev_mode_full_flow(
        self,
        mock_subprocess: MagicMock,
        mock_get_hash: MagicMock,
        mock_operate: MagicMock,
        mock_run_service: MagicMock,
    ) -> None:
        """Test dev mode pushes packages and runs with use_docker=False."""
        mock_app = MagicMock()
        mock_operate.return_value = mock_app
        mock_subprocess.run.return_value = MagicMock(returncode=0)

        runner = CliRunner()
        result = runner.invoke(run, ["-c", "gnosis", "--dev"])

        assert result.exit_code == 0
        assert "Pushing local packages" in result.output
        assert "dev mode" in result.output

        mock_run_service.assert_called_once()
        call_kwargs = mock_run_service.call_args[1]
        assert call_kwargs["build_only"] is False
        assert call_kwargs["use_docker"] is False

        assert mock_subprocess.run.call_count == 1
        first_call = mock_subprocess.run.call_args_list[0]
        assert first_call.args[0] == ["autonomy", "push-all"]

    @patch(f"{MOCK_PATH}.run_service")
    @patch(f"{MOCK_PATH}.OperateApp")
    @patch(f"{MOCK_PATH}._push_all_packages")
    def test_run_without_dev_does_not_push_or_pass_use_docker(
        self,
        mock_push_all: MagicMock,
        mock_operate: MagicMock,
        mock_run_service: MagicMock,
    ) -> None:
        """Test production mode does not push packages or pass use_docker."""
        mock_app = MagicMock()
        mock_operate.return_value = mock_app

        runner = CliRunner()
        result = runner.invoke(run, ["-c", "gnosis"])

        assert result.exit_code == 0
        call_kwargs = mock_run_service.call_args[1]
        assert "use_docker" not in call_kwargs
        mock_push_all.assert_not_called()
