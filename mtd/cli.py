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

import click


@click.group()
def cli() -> None:
    """Dev CLI tool."""


@cli.command()
@click.argument("author", type=str)
@click.argument("tool_name", type=str)
def add_tool(author: str, tool_name: str) -> None:
    """Add a tool by name."""
    click.echo(f"Adding tool: {author}/{tool_name}")
