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

"""Push-metadata command for generating and publishing metadata to IPFS."""

import click

from utils.generate_metadata import main as generate_main
from utils.publish_metadata import DEFAULT_IPFS_NODE, push_metadata_to_ipfs


@click.command(name="push-metadata")
@click.option(
    "--ipfs-node",
    type=str,
    default=DEFAULT_IPFS_NODE,
    help="IPFS node address.",
)
def push_metadata(ipfs_node: str) -> None:
    """Generate metadata.json from packages and publish to IPFS.

    Example: mtd push-metadata
    """
    click.echo("Generating metadata...")
    generate_main()

    click.echo("Publishing metadata to IPFS...")
    push_metadata_to_ipfs(ipfs_node=ipfs_node)
