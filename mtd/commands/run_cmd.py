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

import json
import subprocess
from pathlib import Path

import click
from operate.cli import OperateApp
from operate.quickstart.run_service import run_service


CURRENT_DIR = Path(__file__).parent.parent
BASE_DIR = CURRENT_DIR.parent
CONFIG_DIR = BASE_DIR / "config"
SUPPORTED_CHAINS = ("gnosis", "base", "polygon", "optimism")


def _push_all_packages() -> None:
    """Push local packages to IPFS so service hashes resolve during runtime."""
    click.echo("Pushing local packages...")
    subprocess.run(
        ["autonomy", "push-all"],
        check=True,
        cwd=str(BASE_DIR),
    )


def _get_latest_service_hash() -> str:
    """Get the latest service hash from autonomy packages."""
    subprocess.run(
        ["autonomy", "packages", "lock", "--check"],
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR),
    )
    # Fall back to reading packages.json if lock check fails
    packages_file = BASE_DIR / "packages" / "packages.json"
    if packages_file.exists():
        packages = json.loads(packages_file.read_text())
        for key, hash_val in packages.get("dev", {}).items():
            if "service" in key and "mech" in key:
                return hash_val
    raise click.ClickException("Could not determine latest service hash.")


def _run_dev_mode(config_path: Path) -> None:
    """Dev mode: push local packages, update config hash, run via middleware."""
    _push_all_packages()

    new_hash = _get_latest_service_hash()

    click.echo(f"Updating config template with hash: {new_hash}")
    config = json.loads(config_path.read_text())
    config["hash"] = new_hash
    config_path.write_text(json.dumps(config, indent=2))

    click.echo("Starting service in dev mode (host deployment)...")
    operate = OperateApp()
    operate.setup()
    run_service(
        operate=operate,
        config_path=config_path,
        build_only=False,
        skip_dependency_check=False,
        use_docker=False,
    )


@click.command()
@click.option(
    "-c",
    "--chain-config",
    type=click.Choice(SUPPORTED_CHAINS, case_sensitive=False),
    required=True,
    help="Target chain for the mech service.",
)
@click.option(
    "--dev",
    is_flag=True,
    default=False,
    help="Dev mode: push local packages, then run via host deployment.",
)
def run(chain_config: str, dev: bool) -> None:
    """Run the mech agent service.

    In production mode (default), runs via Docker deployment.
    In dev mode (--dev), pushes local packages to IPFS and runs
    via host deployment (Tendermint + agent process).

    Examples:
        mtd run -c gnosis
        mtd run -c gnosis --dev
    """
    config_path = CONFIG_DIR / f"config_mech_{chain_config}.json"
    if not config_path.exists():
        raise click.ClickException(f"Missing template config: {config_path}")

    if dev:
        _run_dev_mode(config_path)
        return

    operate = OperateApp()
    operate.setup()
    run_service(
        operate=operate,
        config_path=config_path,
        build_only=False,
        skip_dependency_check=False,
    )
