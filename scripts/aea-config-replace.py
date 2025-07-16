#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2021-2025 Valory AG
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


"""Updates fetched agent with correct config"""
import os
import re
from pathlib import Path

import yaml
from dotenv import load_dotenv


AGENT_NAME = "impact_evaluator"

PATH_TO_VAR = {
    # Ledgers
    "config/ledger_apis/ethereum/address": "ETHEREUM_LEDGER_RPC_0",
    "config/ledger_apis/ethereum/chain_id": "ETHEREUM_LEDGER_CHAIN_ID",
    "config/ledger_apis/gnosis/address": "GNOSIS_LEDGER_RPC_0",

    # Agent
    "models/params/args/setup/all_participants": "ALL_PARTICIPANTS",
    "models/params/args/setup/safe_contract_address": "SAFE_CONTRACT_ADDRESS",
    "models/params/args/on_chain_service_id": "ON_CHAIN_SERVICE_ID",
    "models/params/args/num_agents": "NUM_AGENTS",
    "models/params/args/reset_pause_duration": "RESET_PAUSE_DURATION",

    # Tools
    "models/params/args/setup/tools_to_package_hash": "TOOLS_TO_PACKAGE_HASH",
    "models/params/args/setup/api_keys": "API_KEYS",

    # Mech
    "models/params/args/setup/mech_to_config": "MECH_TO_CONFIG",
    "models/params/args/setup/mech_marketplace_address": "MECH_MARKETPLACE_ADDRESS",
    "models/params/args/setup/checkpoint_address": "CHECKPOINT_ADDRESS",
    "models/params/args/setup/agent_registry_address": "AGENT_REGISTRY_ADDRESS",
}

CONFIG_REGEX = r"\${.*?:(.*)}"


def find_and_replace(config, path, new_value):
    """Find and replace a variable"""

    # Find the correct section where this variable fits
    section_index = None
    for i, section in enumerate(config):
        value = section
        try:
            for part in path:
                value = value[part]
            section_index = i
        except KeyError:
            continue

    # To persist the changes in the config variable,
    # access iterating the path parts but the last part
    sub_dic = config[section_index]
    for part in path[:-1]:
        sub_dic = sub_dic[part]

    # Now, get the whole string value
    old_str_value = sub_dic[path[-1]]

    # Extract the old variable value
    match = re.match(CONFIG_REGEX, old_str_value)
    old_var_value = match.groups()[0]

    # Replace the old variable with the secret value in the complete string
    new_str_value = old_str_value.replace(old_var_value, new_value)
    sub_dic[path[-1]] = new_str_value

    return config


def main() -> None:
    """Main"""
    load_dotenv(override=True)

    # Load the aea config
    with open(Path(AGENT_NAME, "aea-config.yaml"), "r", encoding="utf-8") as file:
        config = list(yaml.safe_load_all(file))

    # Search and replace all the secrets
    for path, var in PATH_TO_VAR.items():
        try:
            config = find_and_replace(
                config,
                path.split("/"),
                os.getenv(var)
            )
        except Exception as e:
            print(f"Exception while replacing {path}:\n{e}")
            raise ValueError from e

    # Dump the updated config
    with open(Path(AGENT_NAME, "aea-config.yaml"), "w", encoding="utf-8") as file:
        yaml.dump_all(config, file, sort_keys=False)


if __name__ == "__main__":
    main()
