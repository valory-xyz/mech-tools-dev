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
"""Helpers for setting up env and private keys from operate service config."""

import json
import logging
import os
from pathlib import Path

from dotenv import dotenv_values
from operate.keys import KeysManager


CURR_DIR = Path(__file__).resolve().parent
BASE_DIR = CURR_DIR.parent
SUPPORTED_CHAINS = ("gnosis", "base", "polygon", "optimism")
OPERATE_DIR = BASE_DIR / ".operate"
OPERATE_CONFIG_PATH = "services/sc-*/config.json"
AGENT_KEY = "ethereum_private_key.txt"
SERVICE_KEY = "keys.json"


def read_and_update_env(data: dict) -> None:
    """Reads the generated env from operate and creates the required .env"""
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

    filled_lines = []
    written_keys = set()
    for line in lines:
        if "=" in line:
            key = line.split("=")[0].strip()
            value = computed_env_data.get(key)

            if value is None:
                value = data["env_variables"].get(key, {}).get("value", "")

            # remove vars that are not used. Creates issues during run_service
            if value not in ("", None, {}, []):
                filled_lines.append(f"{key}={value!r}\n")
                written_keys.add(key)
        else:
            filled_lines.append(line)

    for key in mechx_env_data.keys():
        value = mechx_env_data.get(key)
        if value not in ("", None, {}, []):
            filled_lines.append(f"export {key}={value!r}\n")

    if (
        existing_operate_password not in ("", None)
        and "OPERATE_PASSWORD" not in written_keys
    ):
        filled_lines.append(f"OPERATE_PASSWORD={existing_operate_password!r}\n")

    with open(".env", "w", encoding="utf-8") as f:
        f.writelines(filled_lines)


def setup_env() -> None:
    """Setups the env"""
    matching_paths = OPERATE_DIR.glob(OPERATE_CONFIG_PATH)
    data = {}
    for file_path in matching_paths:
        print(f"Reading from: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            data = json.loads(content)

    if not data:
        raise FileNotFoundError(
            f"No operate config found under {OPERATE_DIR / 'services'} matching {OPERATE_CONFIG_PATH}."
        )

    read_and_update_env(data)


def create_private_key_files(data: dict) -> None:
    """Reads the generated env from operate and creates the required keys.json and ethereum_private_key.txt. Skips if files already exists"""
    agent_key_path = BASE_DIR / AGENT_KEY
    if agent_key_path.exists():
        print(f"Agent key found at: {agent_key_path}. Skipping creation")
    else:
        agent_key_path.write_text(data["private_key"], encoding="utf-8")

    service_key_path = BASE_DIR / SERVICE_KEY
    if service_key_path.exists():
        print(f"Service key found at: {service_key_path}. Skipping creation")
    else:
        service_key_path.write_text(json.dumps([data], indent=2), encoding="utf-8")


def setup_private_keys() -> None:
    """Setups the private keys"""
    keys_dir = OPERATE_DIR / "keys"
    if keys_dir.is_dir():
        key_file = next(keys_dir.glob("*"), None)
        if key_file and key_file.is_file():
            print(f"Key file found at: {key_file}")
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
                create_private_key_files(data)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to setup private keys from {key_file}"
                ) from e
