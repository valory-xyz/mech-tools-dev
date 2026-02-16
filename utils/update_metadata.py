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
"""The script allows the user to update mech's metadata hash onchain"""

import json
import os
from pathlib import Path
from typing import Optional, Tuple

import dotenv
from multibase import multibase
from multicodec import multicodec
from safe_eth.eth import EthereumClient  # pylint:disable=import-error
from safe_eth.safe import Safe  # pylint:disable=import-error
from web3 import Web3
from web3.constants import ADDRESS_ZERO
from web3.contract import Contract
from web3.types import TxReceipt


dotenv.load_dotenv(dotenv_path=".env", override=True)

DEFAULT_CHAIN_ID = os.environ.get("DEFAULT_CHAIN_ID", "").strip().upper()
if not DEFAULT_CHAIN_ID:
    raise ValueError("Missing DEFAULT_CHAIN_ID in environment.")
CHAIN_RPC = os.environ.get(f"{DEFAULT_CHAIN_ID}_LEDGER_RPC_0", "")
CHAIN_ID = os.environ.get(f"{DEFAULT_CHAIN_ID}_LEDGER_CHAIN_ID", "")
if not CHAIN_RPC:
    raise ValueError(f"Missing RPC for chain {DEFAULT_CHAIN_ID}: {DEFAULT_CHAIN_ID}_LEDGER_RPC_0")
if not CHAIN_ID:
    raise ValueError(
        f"Missing chain id for chain {DEFAULT_CHAIN_ID}: {DEFAULT_CHAIN_ID}_LEDGER_CHAIN_ID"
    )
COMPLEMENTARY_SERVICE_METADATA_ADDRESS = os.environ[
    "COMPLEMENTARY_SERVICE_METADATA_ADDRESS"
]
METADATA_HASH = os.environ["METADATA_HASH"]
ON_CHAIN_SERVICE_ID = os.environ["ON_CHAIN_SERVICE_ID"]
SAFE_CONTRACT_ADDRESS = os.environ["SAFE_CONTRACT_ADDRESS"]
for required_key, value in (
    ("COMPLEMENTARY_SERVICE_METADATA_ADDRESS", COMPLEMENTARY_SERVICE_METADATA_ADDRESS),
    ("METADATA_HASH", METADATA_HASH),
    ("ON_CHAIN_SERVICE_ID", ON_CHAIN_SERVICE_ID),
    ("SAFE_CONTRACT_ADDRESS", SAFE_CONTRACT_ADDRESS),
):
    if not value:
        raise ValueError(f"Missing {required_key} in environment.")


CURR_DIR = Path(__file__).resolve().parent
BASE_DIR = CURR_DIR.parent


# Instantiate the web3 provider and ethereum client
web3 = Web3(Web3.HTTPProvider(CHAIN_RPC))
ethereum_client = EthereumClient(CHAIN_RPC)


def load_contract(
    contract_address: str, abi_file: str, has_abi_key: bool = True
) -> Contract:
    """Load a smart contract"""
    abi_path = CURR_DIR / "abis" / f"{abi_file}.json"
    with open(abi_path, "r", encoding="utf-8") as abi:
        contract_abi = json.load(abi)
        if has_abi_key:
            contract_abi = contract_abi["abi"]

    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    return contract


def fetch_metadata_hash() -> bytes:
    """To multihash string."""
    # Decode the Base32 CID to bytes
    cid_bytes = multibase.decode(METADATA_HASH)
    if not cid_bytes:
        return b""
    # Remove the multicodec prefix (0x01) from the bytes
    multihash_bytes = multicodec.remove_prefix(cid_bytes)
    # Convert the multihash bytes to a hexadecimal string
    hex_multihash = multihash_bytes.hex()
    metadata_str = hex_multihash[6:]
    metadata = bytes.fromhex(metadata_str)
    return metadata


def send_safe_tx(
    tx_data: str,
    to_adress: str,
    safe_address: str,
    signer_pkey: str,
    gas: int,
    value: int = 0,
) -> Optional[TxReceipt]:
    # pylint: disable=too-many-positional-arguments
    """Send a Safe transaction"""
    # Get the safe
    safe = Safe(  # pylint:disable=abstract-class-instantiated
        safe_address, ethereum_client
    )

    # Build, sign and send the safe transaction
    safe_tx = safe.build_multisig_tx(
        to=to_adress,
        value=value,
        data=bytes.fromhex(tx_data[2:]),
        operation=0,
        safe_tx_gas=gas,
        base_gas=0,
        gas_price=0,
        gas_token=ADDRESS_ZERO,
        refund_receiver=ADDRESS_ZERO,
    )
    safe_tx.sign(signer_pkey)
    try:
        tx_hash, _ = safe_tx.execute(signer_pkey)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt
    except Exception as e:
        print(f"Exception while sending a safe transaction: {e}")
        return None


def get_safe_nonce(safe_address: str) -> int:
    """Get the Safe nonce"""
    safe = Safe(  # pylint:disable=abstract-class-instantiated
        safe_address, ethereum_client
    )
    return safe.retrieve_nonce()


def update_metadata_hash_from_safe(
    safe_address: str,
    signer_pkey: str,
) -> Tuple[bool, bytes]:
    """Update metadata hash"""

    safe_address = web3.to_checksum_address(safe_address)

    metadata_hash_contract = load_contract(
        COMPLEMENTARY_SERVICE_METADATA_ADDRESS,
        "ComplementaryServiceMetadata",
        True,
    )
    metadata = fetch_metadata_hash()

    print(
        f"Updating metadata hash {metadata.hex()} for onchain service id {ON_CHAIN_SERVICE_ID} from {safe_address} on {COMPLEMENTARY_SERVICE_METADATA_ADDRESS}"
    )

    safe_nonce = get_safe_nonce(safe_address)

    # Build the update transaction
    function = metadata_hash_contract.functions.changeHash(
        int(ON_CHAIN_SERVICE_ID), metadata
    )
    transaction = function.build_transaction(
        {
            "chainId": int(CHAIN_ID),
            "gas": 100000,
            "gasPrice": web3.to_wei("3", "gwei"),
            "nonce": safe_nonce,
        }
    )

    tx_receipt = send_safe_tx(
        tx_data=transaction["data"],
        to_adress=COMPLEMENTARY_SERVICE_METADATA_ADDRESS,
        safe_address=safe_address,
        signer_pkey=signer_pkey,
        gas=100000,
    )
    if tx_receipt is None:
        raise RuntimeError("Safe transaction execution failed; no transaction receipt returned.")

    return (tx_receipt.status, tx_receipt.transactionHash)


def main() -> None:
    """Run the publish_metadata script."""
    agent_key_path = BASE_DIR / "ethereum_private_key.txt"
    if not agent_key_path.exists():
        raise FileNotFoundError(
            f"Private key file not found: {agent_key_path}. Run setup first."
        )

    with open(agent_key_path, "r", encoding="utf-8") as data:
        signer_pkey = data.read().strip()
        if not signer_pkey:
            raise ValueError("Private key file is empty.")
        success, tx_hash = update_metadata_hash_from_safe(
            SAFE_CONTRACT_ADDRESS, signer_pkey
        )
        print(f"Success: {success}")
        print(f"Tx Hash: {tx_hash.hex()}")


if __name__ == "__main__":
    main()
