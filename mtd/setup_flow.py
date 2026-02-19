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

"""Setup flow for mech agent service configuration and metadata deployment."""

import json
import logging
import os
from pathlib import Path

import click
from dotenv import dotenv_values, set_key
from operate.cli import OperateApp
from operate.keys import KeysManager
from operate.quickstart.run_service import ask_password_if_needed, run_service


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
SUPPORTED_CHAINS = ("gnosis", "base", "polygon", "optimism")
OPERATE_DIR = BASE_DIR / ".operate"
OPERATE_CONFIG_PATH = "services/sc-*/config.json"
AGENT_KEY = "ethereum_private_key.txt"
SERVICE_KEY = "keys.json"


def _generate_metadata() -> None:
    """Generate metadata.json from packages."""
    from utils.generate_metadata import main  # pylint: disable=import-outside-toplevel

    main()


def _push_metadata() -> None:
    """Push metadata.json to IPFS."""
    from utils.publish_metadata import push_metadata_to_ipfs  # pylint: disable=import-outside-toplevel

    push_metadata_to_ipfs()


def _update_metadata() -> None:
    """Update metadata hash on-chain via Safe transaction."""
    from utils.update_metadata import main  # pylint: disable=import-outside-toplevel

    main()


def _deploy_mech(operate: OperateApp, chain_config: str) -> None:
    """Deploy mech on the marketplace if needed."""
    from mtd.deploy_mech import (  # pylint: disable=import-outside-toplevel
        deploy_mech,
        needs_mech_deployment,
        update_service_after_deploy,
    )

    manager = operate.service_manager()
    services, _ = manager.get_all_services()
    if not services:
        return
    service = services[0]
    if not needs_mech_deployment(service):
        click.echo("Mech already deployed, skipping.")
        return
    ledger_config = service.chain_configs[service.home_chain].ledger_config
    sftxb = manager.get_eth_safe_tx_builder(ledger_config)
    mech_address, agent_id = deploy_mech(sftxb=sftxb, service=service)
    update_service_after_deploy(service, mech_address, agent_id)
    click.echo(f"Mech deployed at {mech_address} (agent_id={agent_id})")


def _get_password(operate: OperateApp) -> str:
    """Load password from .env if present, otherwise prompt and persist."""
    env_path = BASE_DIR / ".env"

    if env_path.exists():
        env_values = dotenv_values(env_path)
        password = (env_values.get("OPERATE_PASSWORD") or "").strip()
        if password:
            os.environ["OPERATE_PASSWORD"] = password
            operate.password = password
            return password

    os.environ["ATTENDED"] = "true"
    ask_password_if_needed(operate)
    if not operate.password:
        raise click.ClickException("Password could not be set for Operate.")

    os.environ["OPERATE_PASSWORD"] = operate.password
    env_path.parent.mkdir(parents=True, exist_ok=True)
    set_key(str(env_path), "OPERATE_PASSWORD", os.environ["OPERATE_PASSWORD"])
    return os.environ["OPERATE_PASSWORD"]


def _configure_quickstart_env(operate: OperateApp, chain_config: str, config_path: Path) -> None:
    """Configure middleware env for interactive quickstart setup."""
    del chain_config  # not needed in interactive mode
    del config_path

    password = _get_password(operate)

    os.environ["OPERATE_PASSWORD"] = password
    os.environ["ATTENDED"] = "true"

    click.echo("Using interactive setup flow (ATTENDED=true)")


def _read_and_update_env(data: dict) -> None:
    """Read generated env from operate and create required .env file."""
    with open(".example.env", "r", encoding="utf-8") as f:
        lines = f.readlines()

    existing_env = dotenv_values(".env")
    existing_operate_password = existing_env.get("OPERATE_PASSWORD") or os.environ.get(
        "OPERATE_PASSWORD", ""
    )

    home_chain = data.get("home_chain")
    if not home_chain:
        raise ValueError("Missing `home_chain` in operate service config.")
    if home_chain not in SUPPORTED_CHAINS:
        raise ValueError(
            f"Unsupported home chain `{home_chain}`. Supported chains: {', '.join(SUPPORTED_CHAINS)}."
        )

    chain_configs = data.get("chain_configs", {})
    safe_contract_address = (
        chain_configs.get(home_chain, {}).get("chain_data", {}).get("multisig", "")
    )
    if not safe_contract_address:
        raise ValueError(
            f"Missing safe address for `{home_chain}` in operate chain config."
        )

    all_participants = json.dumps(data["agent_addresses"])

    var_data = data["env_variables"].get("MECH_TO_MAX_DELIVERY_RATE", {}).get("value", "")
    try:
        parsed = json.loads(var_data or "{}")
    except json.JSONDecodeError as e:
        raise ValueError("Invalid MECH_TO_MAX_DELIVERY_RATE JSON in operate config.") from e

    parsed_dict = {k: int(v) for k, v in parsed.items()}
    mech_to_max_delivery_rate = json.dumps(parsed_dict, separators=(",", ":"))

    computed_env_data = {
        "SAFE_CONTRACT_ADDRESS": safe_contract_address,
        "ALL_PARTICIPANTS": all_participants,
        "MECH_TO_MAX_DELIVERY_RATE": mech_to_max_delivery_rate,
    }

    chain_rpc_env_var = f"{home_chain.upper()}_LEDGER_RPC_0"
    chain_rpc = data["env_variables"].get(chain_rpc_env_var, {}).get("value", "")
    if not chain_rpc:
        raise ValueError(
            f"Missing `{chain_rpc_env_var}` in operate env variables for chain `{home_chain}`."
        )

    mechx_env_data = {
        "MECHX_RPC_URL": chain_rpc,
        "MECHX_LEDGER_ADDRESS": chain_rpc,
        "MECHX_CHAIN_CONFIG": home_chain,
        "MECHX_MECH_OFFCHAIN_URL": "http://localhost:8000/",
    }

    def _format_env_value(value: object) -> str:
        """Serialize env values without Python repr wrappers."""
        if isinstance(value, (dict, list)):
            return json.dumps(value, separators=(",", ":"))
        return str(value)

    filled_lines = []
    written_keys = set()
    for line in lines:
        if "=" in line:
            key = line.split("=")[0].strip()
            value = computed_env_data.get(key)

            if value is None:
                value = data["env_variables"].get(key, {}).get("value", "")

            if value not in ("", None, {}, []):
                filled_lines.append(f"{key}={_format_env_value(value)}\n")
                written_keys.add(key)
        else:
            filled_lines.append(line)

    for key, value in mechx_env_data.items():
        if value not in ("", None, {}, []):
            filled_lines.append(f"{key}={_format_env_value(value)}\n")

    if (
        existing_operate_password not in ("", None)
        and "OPERATE_PASSWORD" not in written_keys
    ):
        filled_lines.append(f"OPERATE_PASSWORD={_format_env_value(existing_operate_password)}\n")

    with open(".env", "w", encoding="utf-8") as f:
        f.writelines(filled_lines)


def _setup_env() -> None:
    """Set up env from generated operate config."""
    matching_paths = OPERATE_DIR.glob(OPERATE_CONFIG_PATH)
    data = {}
    for file_path in matching_paths:
        click.echo(f"Reading from: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            data = json.loads(content)

    if not data:
        raise FileNotFoundError(
            f"No operate config found under {OPERATE_DIR / 'services'} matching {OPERATE_CONFIG_PATH}."
        )

    _read_and_update_env(data)


def _create_private_key_files(data: dict) -> None:
    """Create keys.json and ethereum_private_key.txt from decrypted key data."""
    agent_key_path = BASE_DIR / AGENT_KEY
    if agent_key_path.exists():
        click.echo(f"Agent key found at: {agent_key_path}. Skipping creation")
    else:
        agent_key_path.write_text(data["private_key"], encoding="utf-8")

    service_key_path = BASE_DIR / SERVICE_KEY
    if service_key_path.exists():
        click.echo(f"Service key found at: {service_key_path}. Skipping creation")
    else:
        service_key_path.write_text(json.dumps([data], indent=2), encoding="utf-8")


def _setup_private_keys() -> None:
    """Set up private key files from operate key store."""
    keys_dir = OPERATE_DIR / "keys"
    if keys_dir.is_dir():
        key_file = next(keys_dir.glob("*"), None)
        if key_file and key_file.is_file():
            click.echo(f"Key file found at: {key_file}")
            password = os.environ.get("OPERATE_PASSWORD", "")
            if not password:
                raise ValueError("OPERATE_PASSWORD is required to decrypt keys.")

            try:
                manager = KeysManager(
                    path=keys_dir,
                    logger=logging.getLogger(__name__),
                    password=password,
                )
                data = manager.get_decrypted(key_file.name)
                _create_private_key_files(data)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to setup private keys from {key_file}"
                ) from e


def run_setup(chain_config: str) -> None:
    """Run the full setup flow for the given chain."""
    config_path = CONFIG_DIR / f"config_mech_{chain_config}.json"
    if not config_path.exists():
        raise click.ClickException(f"Missing template config: {config_path}")

    operate = OperateApp()
    operate.setup()

    # Ensure wallet operations work even when setup is skipped.
    _get_password(operate)

    services, _ = operate.service_manager().get_all_services()
    needs_setup = (
        not services
        or services[0].chain_configs.get(services[0].home_chain, {}).chain_data.multisig
        is None
    )

    if needs_setup:
        click.echo("Setting up operate...")
        _configure_quickstart_env(operate, chain_config, config_path)
        run_service(
            operate=operate,
            config_path=config_path,
            build_only=True,
            skip_dependency_check=False,
        )

    click.echo("Deploying mech on marketplace...")
    _deploy_mech(operate, chain_config)

    click.echo("Setting up env...")
    _setup_env()

    click.echo("Setting up private keys...")
    _setup_private_keys()

    click.echo("Generating metadata...")
    _generate_metadata()

    click.echo("Publishing metadata to IPFS...")
    _push_metadata()

    click.echo("Updating metadata hash on-chain...")
    _update_metadata()

    click.echo("Setup complete.")
