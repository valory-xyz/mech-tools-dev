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

"""Deploy-mech command for deploying a mech on the marketplace."""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import click
from operate.cli import OperateApp

from mtd.commands.context_utils import get_mtd_context
from mtd.context import MtdContext
from mtd.deploy_mech import deploy_mech, needs_mech_deployment, update_service_after_deploy


SUPPORTED_CHAINS = ("gnosis", "base", "polygon", "optimism")


@contextmanager
def _workspace_cwd(context: MtdContext) -> Iterator[None]:
    """Run operations from workspace root."""
    previous = Path.cwd()
    previous_operate_home = os.environ.get("OPERATE_HOME")
    context.ensure_workspace_exists()
    os.environ["OPERATE_HOME"] = str(context.operate_dir)
    os.chdir(context.workspace_path)
    try:
        yield
    finally:
        os.chdir(previous)
        if previous_operate_home is None:
            os.environ.pop("OPERATE_HOME", None)
        else:
            os.environ["OPERATE_HOME"] = previous_operate_home


@click.command(name="deploy-mech")
@click.option(
    "-c",
    "--chain-config",
    type=click.Choice(SUPPORTED_CHAINS, case_sensitive=False),
    required=True,
    help="Target chain for the mech deployment.",
)
@click.pass_context
def deploy_mech_command(ctx: click.Context, chain_config: str) -> None:
    """Deploy a mech on the marketplace for an existing service."""
    context = get_mtd_context(ctx)
    with _workspace_cwd(context):
        operate = OperateApp(home=context.operate_dir)
        operate.setup()

        manager = operate.service_manager()
        services, _ = manager.get_all_services()
        if not services:
            raise click.ClickException("No service found. Run 'mech setup' first.")

        service = services[0]
        if not needs_mech_deployment(service):
            click.echo("Mech already deployed, skipping.")
            return

        ledger_config = service.chain_configs[service.home_chain].ledger_config
        sftxb = manager.get_eth_safe_tx_builder(ledger_config)

        click.echo("Deploying mech on marketplace...")
        mech_address, agent_id = deploy_mech(sftxb=sftxb, service=service)
        update_service_after_deploy(service, mech_address, agent_id)
        click.echo(f"Mech deployed at {mech_address} (agent_id={agent_id})")
