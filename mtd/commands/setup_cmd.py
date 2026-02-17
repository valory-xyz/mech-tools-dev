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

"""Setup command for mech agent service configuration and metadata deployment."""

from pathlib import Path

import click
from operate.cli import OperateApp
from operate.quickstart.run_service import run_service

from utils.setup import setup_env, setup_private_keys


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
def setup(chain_config: str) -> None:
    """Setup on-chain requirements for running a mech agent.

    Runs the full setup flow: operate build, env configuration,
    private key setup, metadata generation, IPFS publish, and
    on-chain metadata hash update.

    Example: mtd setup -c gnosis
    """
    config_path = CONFIG_DIR / f"config_mech_{chain_config}.json"
    if not config_path.exists():
        raise click.ClickException(f"Missing template config: {config_path}")

    # 1. Setup operate
    operate = OperateApp()
    operate.setup()

    services, _ = operate.service_manager().get_all_services()
    needs_setup = (
        not services
        or services[0].chain_configs.get(services[0].home_chain, {}).chain_data.multisig
        is None
    )

    if needs_setup:
        click.echo("Setting up operate...")
        run_service(
            operate=operate,
            config_path=config_path,
            build_only=True,
            skip_dependency_check=False,
        )

    # 2. Setup env and private keys
    click.echo("Setting up env...")
    setup_env()

    click.echo("Setting up private keys...")
    setup_private_keys()

    # 3. Generate metadata, push to IPFS, update on-chain
    from utils.generate_metadata import main as generate_main  # pylint: disable=import-outside-toplevel
    from utils.publish_metadata import push_metadata_to_ipfs  # pylint: disable=import-outside-toplevel
    from utils.update_metadata import main as update_main  # pylint: disable=import-outside-toplevel

    click.echo("Generating metadata...")
    generate_main()

    click.echo("Publishing metadata to IPFS...")
    push_metadata_to_ipfs()

    click.echo("Updating metadata hash on-chain...")
    update_main()

    click.echo("Setup complete.")
