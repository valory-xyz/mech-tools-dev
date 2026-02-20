# -*- coding: utf-8 -*-
"""Backward-compatible wrapper for metadata publish."""

from pathlib import Path

from mtd.services.metadata.publish import DEFAULT_IPFS_NODE, publish_metadata_to_ipfs


METADATA_FILE_PATH = "metadata.json"


def push_metadata_to_ipfs(ipfs_node: str = DEFAULT_IPFS_NODE) -> None:
    """Push metadata to IPFS."""
    metadata_hash = publish_metadata_to_ipfs(
        metadata_path=Path(METADATA_FILE_PATH), ipfs_node=ipfs_node
    )
    print(
        f"Metadata successfully pushed to ipfs. The metadata hash is: {metadata_hash}"
    )


def main() -> None:
    """Run the publish_metadata script."""
    push_metadata_to_ipfs()


if __name__ == "__main__":
    main()
