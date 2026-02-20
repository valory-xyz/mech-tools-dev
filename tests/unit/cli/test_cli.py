# -*- coding: utf-8 -*-
"""Tests for the CLI entry point."""

from click.testing import CliRunner

from mtd.cli import cli
class TestCli:
    """Tests for the CLI group."""

    def test_help(self) -> None:
        """Test CLI help output lists all commands."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "init" not in result.output
        assert "add-tool" in result.output
        assert "deploy-mech" in result.output
        assert "setup" in result.output
        assert "run" in result.output
        assert "stop" in result.output
        assert "push-metadata" in result.output
        assert "update-metadata" in result.output

    def test_no_workspace_option(self) -> None:
        """CLI help should not expose workspace override option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "--workspace" not in result.output

    def test_no_command(self) -> None:
        """Test CLI with no subcommand shows help."""
        runner = CliRunner()
        result = runner.invoke(cli, [])

        assert result.exit_code == 0
        assert "Usage" in result.output

    def test_invalid_command(self) -> None:
        """Test CLI with unknown command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["nonexistent"])

        assert result.exit_code != 0
