# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2025-2026 Valory AG
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
