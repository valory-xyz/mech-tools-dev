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
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import click
from dotenv import dotenv_values, set_key
from operate.cli import OperateApp
from operate.keys import KeysManager
from operate.quickstart.run_service import ask_password_if_needed, run_service

from mtd.context import MtdContext
from mtd.resources import read_text_resource
from mtd.services.metadata.generate import generate_metadata
from mtd.services.metadata.publish import publish_metadata_to_ipfs
from mtd.services.metadata.update_onchain import update_metadata_onchain


SUPPORTED_CHAINS = ("gnosis", "base", "polygon", "optimism")
OPERATE_CONFIG_PATH = "services/sc-*/config.json"
AGENT_KEY = "ethereum_private_key.txt"
SERVICE_KEY = "keys.json"


@contextmanager
def _workspace_cwd(context: MtdContext) -> Iterator[None]:
    """Run operations from workspace root."""
    previous = Path.cwd()
    os.chdir(context.workspace_path)
    try:
        yield
    finally:
        os.chdir(previous)


def _deploy_mech(operate: OperateApp) -> None:
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


def _get_password(operate: OperateApp, context: MtdContext) -> str:
    """Load password from workspace .env if present, otherwise prompt and persist."""
    if context.env_path.exists():
        env_values = dotenv_values(context.env_path)
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
    set_key(str(context.env_path), "OPERATE_PASSWORD", os.environ["OPERATE_PASSWORD"])
    return os.environ["OPERATE_PASSWORD"]


def _configure_quickstart_env(operate: OperateApp, context: MtdContext) -> None:
    """Configure middleware env for interactive quickstart setup."""
    password = _get_password(operate=operate, context=context)
    os.environ["OPERATE_PASSWORD"] = password
    os.environ["ATTENDED"] = "true"
    click.echo("Using interactive setup flow (ATTENDED=true)")


def _read_and_update_env(data: dict, context: MtdContext) -> None:
    """Read generated env from operate and create required workspace .env file."""
    template_text = read_text_resource("mtd.templates.runtime", ".example.env")
    lines = [line if line.endswith("\n") else f"{line}\n" for line in template_text.splitlines()]

    existing_env = dotenv_values(context.env_path)
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
    parsed = json.loads(var_data or "{}")
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
        "MECHX_CHAIN_RPC": chain_rpc,
        "MECHX_LEDGER_ADDRESS": chain_rpc,
        "MECHX_CHAIN_CONFIG": home_chain,
        "MECHX_MECH_OFFCHAIN_URL": "http://localhost:8000/",
    }

    def _format_env_value(value: object) -> str:
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
            continue

        filled_lines.append(line)

    for key, value in mechx_env_data.items():
        if value not in ("", None, {}, []):
            filled_lines.append(f"{key}={_format_env_value(value)}\n")

    if existing_operate_password not in ("", None) and "OPERATE_PASSWORD" not in written_keys:
        filled_lines.append(f"OPERATE_PASSWORD={_format_env_value(existing_operate_password)}\n")

    context.env_path.write_text("".join(filled_lines), encoding="utf-8")


def _setup_env(context: MtdContext) -> None:
    """Set up env from generated operate config."""
    matching_paths = context.operate_dir.glob(OPERATE_CONFIG_PATH)
    data = {}
    for file_path in matching_paths:
        click.echo(f"Reading from: {file_path}")
        data = json.loads(file_path.read_text(encoding="utf-8"))

    if not data:
        raise FileNotFoundError(
            f"No operate config found under {context.operate_dir / 'services'} matching {OPERATE_CONFIG_PATH}."
        )

    _read_and_update_env(data=data, context=context)


def _create_private_key_files(data: dict, context: MtdContext) -> None:
    """Create keys.json and ethereum_private_key.txt from decrypted key data."""
    context.keys_dir.mkdir(parents=True, exist_ok=True)

    agent_key_path = context.keys_dir / AGENT_KEY
    if agent_key_path.exists():
        click.echo(f"Agent key found at: {agent_key_path}. Skipping creation")
    else:
        agent_key_path.write_text(data["private_key"], encoding="utf-8")

    service_key_path = context.keys_dir / SERVICE_KEY
    if service_key_path.exists():
        click.echo(f"Service key found at: {service_key_path}. Skipping creation")
    else:
        service_key_path.write_text(json.dumps([data], indent=2), encoding="utf-8")


def _setup_private_keys(context: MtdContext) -> None:
    """Set up private key files from operate key store."""
    keys_dir = context.operate_dir / "keys"
    if keys_dir.is_dir():
        key_file = next(keys_dir.glob("*"), None)
        if key_file and key_file.is_file():
            click.echo(f"Key file found at: {key_file}")
            password = os.environ.get("OPERATE_PASSWORD", "")
            if not password:
                raise ValueError("OPERATE_PASSWORD is required to decrypt keys.")

            manager = KeysManager(
                path=keys_dir,
                logger=logging.getLogger(__name__),
                password=password,
            )
            data = manager.get_decrypted(key_file.name)
            _create_private_key_files(data=data, context=context)


def run_setup(chain_config: str, context: MtdContext) -> None:
    """Run the full setup flow for the given chain and workspace context."""
    config_path = context.config_dir / f"config_mech_{chain_config}.json"
    if not config_path.exists():
        raise click.ClickException(f"Missing template config: {config_path}")

    with _workspace_cwd(context):
        operate = OperateApp()
        operate.setup()

        _get_password(operate=operate, context=context)

        services, _ = operate.service_manager().get_all_services()
        needs_setup = (
            not services
            or services[0].chain_configs.get(services[0].home_chain, {}).chain_data.multisig
            is None
        )

        if needs_setup:
            click.echo("Setting up operate...")
            _configure_quickstart_env(operate=operate, context=context)
            run_service(
                operate=operate,
                config_path=config_path,
                build_only=True,
                skip_dependency_check=False,
            )

        click.echo("Deploying mech on marketplace...")
        _deploy_mech(operate)

        click.echo("Setting up env...")
        _setup_env(context=context)

        click.echo("Setting up private keys...")
        _setup_private_keys(context=context)

        click.echo("Generating metadata...")
        generate_metadata(packages_dir=context.packages_dir, metadata_path=context.metadata_path)

        click.echo("Publishing metadata to IPFS...")
        metadata_hash = publish_metadata_to_ipfs(metadata_path=context.metadata_path)
        set_key(str(context.env_path), "METADATA_HASH", metadata_hash)

        click.echo("Updating metadata hash on-chain...")
        success, tx_hash = update_metadata_onchain(
            env_path=context.env_path,
            private_key_path=context.keys_dir / AGENT_KEY,
        )
        click.echo(f"Metadata update status: success={success}, tx_hash={tx_hash}")

        click.echo("Setup complete.")
