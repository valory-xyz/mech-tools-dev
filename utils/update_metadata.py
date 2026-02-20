# -*- coding: utf-8 -*-
"""Backward-compatible wrapper for metadata on-chain update."""

from pathlib import Path

from mtd.services.metadata.update_onchain import update_metadata_onchain


def main() -> None:
    """Run metadata hash on-chain update."""
    success, tx_hash = update_metadata_onchain(
        env_path=Path(".env"),
        private_key_path=Path("ethereum_private_key.txt"),
    )
    print(f"Success: {success}")
    print(f"Tx Hash: {tx_hash}")


if __name__ == "__main__":
    main()
