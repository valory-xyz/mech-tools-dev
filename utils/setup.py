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
"""The script allows the user to setup onchain requirements for running mechs"""

import json
from pathlib import Path

from operate.cli import OperateApp, run_service


CURR_DIR = Path(__file__).resolve().parent
BASE_DIR = CURR_DIR.parent
GNOSIS_TEMPLATE_CONFIG_PATH = BASE_DIR / "config" / "config_mech_gnosis.json"
OPERATE_DIR = BASE_DIR / ".operate"
OPERATE_CONFIG_PATH = "services/sc-*/config.json"
AGENT_KEY = "ethereum_private_key.txt"
SERVICE_KEY = "keys.json"


def read_and_update_env(data: dict) -> None:
    """Reads the generated env from operate and creates the required .env"""
    with open(".example.env", "r", encoding="utf-8") as f:
        lines = f.readlines()

    safe_contract_address = data["chain_configs"]["gnosis"]["chain_data"]["multisig"]
    all_participants = json.dumps(data["agent_addresses"])

    var_data = (
        data["env_variables"].get("MECH_TO_MAX_DELIVERY_RATE", {}).get("value", "")
    )
    parsed = json.loads(var_data)
    parsed_dict = {k: int(v) for k, v in parsed.items()}
    mech_to_max_delivery_rate = json.dumps(parsed_dict, separators=(",", ":"))

    computed_env_data = {
        "SAFE_CONTRACT_ADDRESS": safe_contract_address,
        "ALL_PARTICIPANTS": all_participants,
        "MECH_TO_MAX_DELIVERY_RATE": mech_to_max_delivery_rate,
    }

    mechx_env_data = {
        "MECHX_RPC_URL": data["env_variables"]
        .get("GNOSIS_LEDGER_RPC_0", {})
        .get("value", ""),
        "MECHX_LEDGER_ADDRESS": data["env_variables"]
        .get("GNOSIS_LEDGER_RPC_0", {})
        .get("value", ""),
        "MECHX_WSS_ENDPOINT": data["env_variables"]
        .get("MECHX_WSS_ENDPOINT", {})
        .get("value", ""),
        "MECHX_MECH_OFFCHAIN_URL": "http://localhost:8000/",
    }

    filled_lines = []
    for line in lines:
        if "=" in line:
            key = line.split("=")[0].strip()
            value = computed_env_data.get(key)

            if value is None:
                value = data["env_variables"].get(key, {}).get("value", "")

            # remove vars that are not used. Creates issues during run_service
            if value not in ("", None, {}, []):
                filled_lines.append(f"{key}={value!r}\n")
        else:
            filled_lines.append(line)

    for key in mechx_env_data.keys():
        value = mechx_env_data.get(key)
        if value not in ("", None, {}, []):
            filled_lines.append(f"export {key}={value!r}\n")

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

    read_and_update_env(data)


def create_private_key_files(data: dict) -> None:
    """Reads the generated env from operate and creates the required keys.json and ethereum_private_key.txt. Skips if files already exists"""
    agent_key_path = BASE_DIR / AGENT_KEY
    if agent_key_path.exists():
        print(f"Agent key found at: {agent_key_path}. Skipping creation")
    else:
        agent_key_path.write_text(data["private_key"])

    service_key_path = BASE_DIR / SERVICE_KEY
    if service_key_path.exists():
        print(f"Service key found at: {service_key_path}. Skipping creation")
    else:
        service_key_path.write_text(json.dumps([data], indent=2))


def setup_private_keys() -> None:
    """Setups the private keys"""
    keys_dir = OPERATE_DIR / "keys"
    if keys_dir.is_dir():
        key_file = next(keys_dir.glob("*"), None)
        if key_file and key_file.is_file():
            print(f"Key file found at: {key_file}")
            with open(key_file, "r", encoding="utf-8") as f:
                content = f.read()
                data = json.loads(content)

        create_private_key_files(data)


def setup_operate() -> None:
    """Setups the operate"""
    operate = OperateApp()
    operate.setup()

    run_service(
        operate=operate,
        config_path=GNOSIS_TEMPLATE_CONFIG_PATH,
        build_only=True,
        skip_dependency_check=False,
    )


def main() -> None:
    """Runs the script"""
    if not OPERATE_DIR.is_dir():
        print("Setting up operate...")
        setup_operate()

    print("Setting up env...")
    setup_env()

    print("Setting up private keys...")
    setup_private_keys()


if __name__ == "__main__":
    main()
