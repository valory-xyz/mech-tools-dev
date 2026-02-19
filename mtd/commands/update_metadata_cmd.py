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

"""Update-metadata command for updating the metadata hash on-chain."""

import click


@click.command(name="update-metadata")
def update_metadata() -> None:
    """Update the metadata hash on-chain via Safe transaction.

    Example: mtd update-metadata
    """
    from utils.update_metadata import main as update_main  # pylint: disable=import-outside-toplevel

    click.echo("Updating metadata hash on-chain...")
    update_main()
