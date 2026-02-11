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
from typing import Tuple

import dotenv
from aea_ledger_ethereum import EthereumCrypto
from multibase import multibase
from multicodec import multicodec
from safe_eth.eth import EthereumClient  # pylint:disable=import-error
from safe_eth.safe import Safe  # pylint:disable=import-error
from web3 import Web3
from web3.constants import ADDRESS_ZERO
from web3.contract import Contract
from web3.types import TxReceipt


dotenv.load_dotenv(dotenv_path=".env", override=True)

GNOSIS_RPC = os.environ["GNOSIS_LEDGER_RPC_0"]
GNOSIS_CHAIN_ID = os.environ["GNOSIS_LEDGER_CHAIN_ID"]
COMPLEMENTARY_SERVICE_METADATA_ADDRESS = os.environ[
    "COMPLEMENTARY_SERVICE_METADATA_ADDRESS"
]
METADATA_HASH = os.environ["METADATA_HASH"]
ON_CHAIN_SERVICE_ID = os.environ["ON_CHAIN_SERVICE_ID"]
SAFE_CONTRACT_ADDRESS = os.environ["SAFE_CONTRACT_ADDRESS"]


CURR_DIR = Path(__file__).resolve().parent
BASE_DIR = CURR_DIR.parent


# Instantiate the web3 provider and ethereum client
web3 = Web3(Web3.HTTPProvider(GNOSIS_RPC))
ethereum_client = EthereumClient(GNOSIS_RPC)


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
) -> TxReceipt:
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
        return False


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
            "chainId": int(GNOSIS_CHAIN_ID),
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

    return (tx_receipt.status, tx_receipt.transactionHash)


def main() -> None:
    """Run the publish_metadata script."""
    agent_key_path = BASE_DIR / "ethereum_private_key.txt"
    password = os.environ.get("OPERATE_PASSWORD", "")
    crypto = EthereumCrypto(private_key_path=str(agent_key_path), password=password)
    signer_pkey = crypto.private_key
    success, tx_hash = update_metadata_hash_from_safe(
        SAFE_CONTRACT_ADDRESS, signer_pkey
    )
    print(f"Success: {success}")
    print(f"Tx Hash: {tx_hash.hex()}")


if __name__ == "__main__":
    main()
