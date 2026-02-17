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

"""Run command for starting the mech agent service."""

from pathlib import Path

import click
from operate.cli import OperateApp
from operate.quickstart.run_service import run_service


CURRENT_DIR = Path(__file__).parent.parent
BASE_DIR = CURRENT_DIR.parent
CONFIG_DIR = BASE_DIR / "config"
SUPPORTED_CHAINS = ("gnosis", "base", "polygon", "optimism")


@click.command()
@click.option(
    "-c",
    "--chain-config",
    type=click.Choice(SUPPORTED_CHAINS, case_sensitive=False),
    required=True,
    help="Target chain for the mech service.",
)
def run(chain_config: str) -> None:
    """Run the mech agent service.

    Example: mtd run -c gnosis
    """
    config_path = CONFIG_DIR / f"config_mech_{chain_config}.json"
    if not config_path.exists():
        raise click.ClickException(f"Missing template config: {config_path}")

    operate = OperateApp()
    operate.setup()
    run_service(
        operate=operate,
        config_path=config_path,
        build_only=False,
        skip_dependency_check=False,
    )
