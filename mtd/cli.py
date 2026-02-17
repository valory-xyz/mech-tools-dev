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

"""The mech tools dev CLI's entry point."""

from pathlib import Path
from string import Template
from time import localtime
from typing import Dict

import click
from aea.cli.packages import package_type_selector_prompt
from autonomy.cli.packages import get_package_manager
import json
from operate.cli import OperateApp
from operate.quickstart.run_service import run_service
from utils.setup import setup_env, setup_private_keys

    

CURRENT_DIR = Path(__file__).parent
BASE_DIR = CURRENT_DIR.parent
PACKAGES_DIR = BASE_DIR / "packages"
CONFIG_DIR = BASE_DIR / "config"
SUPPORTED_CHAINS = ("gnosis", "base", "polygon", "optimism")
CUSTOMS_DIR = "customs"
PY_SUFFIX = ".py"
INIT_FILENAME = f"__init__{PY_SUFFIX}"
CONFIG_FILENAME = "component.yaml"
TEMPLATE_SUFFIX = ".template"
TEMPLATES_PATH = CURRENT_DIR / "templates"
INIT_TEMPLATE = f"init{TEMPLATE_SUFFIX}"
CONFIG_TEMPLATE = f"config{TEMPLATE_SUFFIX}"
TOOL_TEMPLATE = f"tool{TEMPLATE_SUFFIX}"
WRITE_MODE = "w"
READ_MODE = "r"


def generate_tool_file(
    template_name: str, template_params: Dict[str, str], filename: str, tool_path: Path
) -> None:
    """Generate a file from a template."""
    with open(TEMPLATES_PATH / template_name, READ_MODE) as file:
        template = Template(file.read())
    content = template.substitute(**template_params)

    if filename != INIT_FILENAME:
        with open(tool_path / filename, WRITE_MODE) as file:
            file.write(content)
            return

    # create `__init__.py` in each part of the path
    current = tool_path
    while current != PACKAGES_DIR:
        with open(current / filename, WRITE_MODE) as file:
            file.write(content)
            current = current.parent


def generate_tool(author: str, tool_name: str, tool_description: str) -> None:
    """Generate the tool files."""
    template_to_file = {
        INIT_TEMPLATE: INIT_FILENAME,
        CONFIG_TEMPLATE: CONFIG_FILENAME,
        TOOL_TEMPLATE: f"{tool_name}{PY_SUFFIX}",
    }

    template_params = {
        "year": str(localtime().tm_year),
        "authorname": author,
        "tool_name": tool_name,
        "tool_description": tool_description,
    }

    tool_path = PACKAGES_DIR / author / CUSTOMS_DIR / tool_name
    tool_path.mkdir(parents=True, exist_ok=True)

    for template, filename in template_to_file.items():
        generate_tool_file(template, template_params, filename, tool_path)


@click.group()
def cli() -> None:
    """Dev CLI tool."""


@cli.command()
@click.argument("author", type=str)
@click.argument("tool_name", type=str)
@click.option(
    "-d",
    "--tool-description",
    type=str,
    default="A mech tool.",
    required=False,
    help="The tool's description.",
)
@click.option(
    "-s",
    "--skip-lock",
    type=bool,
    is_flag=True,
    default=False,
    required=False,
    help="Whether the lock of the packages should be skipped after creating the tool's template.",
)
def add_tool(
    author: str, tool_name: str, tool_description: str, skip_lock: bool
) -> None:
    """Add a new mech tool."""
    click.echo(f"Adding tool: {author}/{tool_name}.")
    generate_tool(author, tool_name, tool_description)
    click.echo(f"Tool {author}/{tool_name} added.")

    if skip_lock:
        return

    click.echo("Locking packages...")
    get_package_manager(PACKAGES_DIR).update_package_hashes(
        package_type_selector_prompt
    ).dump()
    click.echo("Packages locked.")


@cli.command()
@click.option(
    "-c",
    "--chain-config",
    type=click.Choice(SUPPORTED_CHAINS, case_sensitive=False),
    required=True,
    help="Target chain for the mech service.",
)
def setup(chain_config: str) -> None:
    """Setup on-chain requirements for running a mech agent."""
    config_path = CONFIG_DIR / f"config_mech_{chain_config}.json"
    if not config_path.exists():
        raise click.ClickException(f"Missing template config: {config_path}")

    # Extract staking program from template if present
    with open(config_path, "r", encoding="utf-8") as f:
        template = json.load(f)
    staking_program_id = (
        template.get("configurations", {})
        .get(chain_config, {})
        .get("staking_program_id")
    )

    # Setup operate
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
            staking_program_id=staking_program_id,
        )

    click.echo("Setting up env...")
    setup_env()

    click.echo("Setting up private keys...")
    setup_private_keys()
