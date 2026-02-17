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

from mtd.commands.setup_cmd import setup


MOCK_OPERATE_PATH = "mtd.commands.setup_cmd"


class TestSetupCommand:
    """Tests for setup command."""

    @patch(f"{MOCK_OPERATE_PATH}.update_main")
    @patch(f"{MOCK_OPERATE_PATH}.push_metadata_to_ipfs")
    @patch(f"{MOCK_OPERATE_PATH}.generate_main")
    @patch(f"{MOCK_OPERATE_PATH}.setup_private_keys")
    @patch(f"{MOCK_OPERATE_PATH}.setup_env")
    @patch(f"{MOCK_OPERATE_PATH}.run_service")
    @patch(f"{MOCK_OPERATE_PATH}.OperateApp")
    def test_setup_success_needs_setup(
        self,
        mock_operate: MagicMock,
        mock_run_service: MagicMock,
        mock_setup_env: MagicMock,
        mock_setup_keys: MagicMock,
        mock_generate: MagicMock,
        mock_push: MagicMock,
        mock_update: MagicMock,
    ) -> None:
        """Test full setup flow when service needs setup."""
        mock_app = MagicMock()
        mock_operate.return_value = mock_app
        mock_manager = MagicMock()
        mock_app.service_manager.return_value = mock_manager
        mock_manager.get_all_services.return_value = ([], None)

        runner = CliRunner()
        result = runner.invoke(setup, ["-c", "gnosis"])

        assert result.exit_code == 0
        assert "Setting up operate" in result.output
        assert "Setting up env" in result.output
        assert "Setting up private keys" in result.output
        assert "Generating metadata" in result.output
        assert "Publishing metadata to IPFS" in result.output
        assert "Updating metadata hash on-chain" in result.output
        assert "Setup complete" in result.output

        mock_operate.assert_called_once()
        mock_app.setup.assert_called_once()
        mock_run_service.assert_called_once()
        mock_setup_env.assert_called_once()
        mock_setup_keys.assert_called_once()
        mock_generate.assert_called_once()
        mock_push.assert_called_once()
        mock_update.assert_called_once()

    @patch(f"{MOCK_OPERATE_PATH}.update_main")
    @patch(f"{MOCK_OPERATE_PATH}.push_metadata_to_ipfs")
    @patch(f"{MOCK_OPERATE_PATH}.generate_main")
    @patch(f"{MOCK_OPERATE_PATH}.setup_private_keys")
    @patch(f"{MOCK_OPERATE_PATH}.setup_env")
    @patch(f"{MOCK_OPERATE_PATH}.run_service")
    @patch(f"{MOCK_OPERATE_PATH}.OperateApp")
    def test_setup_skips_operate_when_already_setup(
        self,
        mock_operate: MagicMock,
        mock_run_service: MagicMock,
        mock_setup_env: MagicMock,
        mock_setup_keys: MagicMock,
        mock_generate: MagicMock,
        mock_push: MagicMock,
        mock_update: MagicMock,
    ) -> None:
        """Test setup skips operate build when service already exists."""
        mock_app = MagicMock()
        mock_operate.return_value = mock_app
        mock_service = MagicMock()
        mock_service.home_chain = "gnosis"
        mock_chain_data = MagicMock()
        mock_chain_data.multisig = "0x1234"
        mock_chain_config = MagicMock()
        mock_chain_config.chain_data = mock_chain_data
        mock_service.chain_configs = {"gnosis": mock_chain_config}
        mock_manager = MagicMock()
        mock_manager.get_all_services.return_value = ([mock_service], None)
        mock_app.service_manager.return_value = mock_manager

        runner = CliRunner()
        result = runner.invoke(setup, ["-c", "gnosis"])

        assert result.exit_code == 0
        mock_run_service.assert_not_called()
        mock_setup_env.assert_called_once()
        mock_setup_keys.assert_called_once()
        mock_generate.assert_called_once()
        mock_push.assert_called_once()
        mock_update.assert_called_once()

    def test_setup_missing_chain_config(self) -> None:
        """Test setup without required chain-config option."""
        runner = CliRunner()
        result = runner.invoke(setup, [])

        assert result.exit_code != 0
        assert "Missing option" in result.output or "chain-config" in result.output

    def test_setup_invalid_chain_config(self) -> None:
        """Test setup with invalid chain config."""
        runner = CliRunner()
        result = runner.invoke(setup, ["-c", "invalid_chain"])

        assert result.exit_code != 0
        assert "Invalid value" in result.output or "invalid_chain" in result.output

    def test_setup_help(self) -> None:
        """Test setup help output."""
        runner = CliRunner()
        result = runner.invoke(setup, ["--help"])

        assert result.exit_code == 0
        assert "chain-config" in result.output
        assert "Setup on-chain requirements" in result.output

    @patch(f"{MOCK_OPERATE_PATH}.update_main")
    @patch(f"{MOCK_OPERATE_PATH}.push_metadata_to_ipfs")
    @patch(f"{MOCK_OPERATE_PATH}.generate_main")
    @patch(f"{MOCK_OPERATE_PATH}.setup_private_keys")
    @patch(f"{MOCK_OPERATE_PATH}.setup_env")
    @patch(f"{MOCK_OPERATE_PATH}.run_service")
    @patch(f"{MOCK_OPERATE_PATH}.OperateApp")
    def test_setup_all_supported_chains(
        self,
        mock_operate: MagicMock,
        mock_run_service: MagicMock,
        mock_setup_env: MagicMock,
        mock_setup_keys: MagicMock,
        mock_generate: MagicMock,
        mock_push: MagicMock,
        mock_update: MagicMock,
    ) -> None:
        """Test setup works for all supported chains."""
        mock_app = MagicMock()
        mock_operate.return_value = mock_app
        mock_manager = MagicMock()
        mock_manager.get_all_services.return_value = ([], None)
        mock_app.service_manager.return_value = mock_manager

        for chain in ("gnosis", "base", "polygon", "optimism"):
            runner = CliRunner()
            result = runner.invoke(setup, ["-c", chain])
            assert result.exit_code == 0, f"Failed for chain {chain}: {result.output}"

    @patch(f"{MOCK_OPERATE_PATH}.setup_env")
    @patch(f"{MOCK_OPERATE_PATH}.run_service")
    @patch(f"{MOCK_OPERATE_PATH}.OperateApp")
    def test_setup_env_failure_stops_execution(
        self,
        mock_operate: MagicMock,
        mock_run_service: MagicMock,
        mock_setup_env: MagicMock,
    ) -> None:
        """Test that env setup failure stops the rest of the flow."""
        mock_app = MagicMock()
        mock_operate.return_value = mock_app
        mock_manager = MagicMock()
        mock_manager.get_all_services.return_value = ([], None)
        mock_app.service_manager.return_value = mock_manager
        mock_setup_env.side_effect = Exception("env setup failed")

        runner = CliRunner()
        result = runner.invoke(setup, ["-c", "gnosis"])

        assert result.exit_code != 0
        assert "env setup failed" in result.output
