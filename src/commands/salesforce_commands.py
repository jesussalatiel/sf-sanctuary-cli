"""Salesforce CLI Tool: Manage Salesforce interactions via CLI."""

import subprocess

import click
from rich.console import Console

from utils.sf_command_executor import _run_sf_command, _run_command
from utils.table import print_table

console = Console()
ERROR_STYLE = "bold red"
SUCCESS_STYLE = "bold green"
WARNING_STYLE = "bold yellow"

ENVIRONMENTS = {
    "commondev": "https://sanctuary--commondev.sandbox.my.salesforce.com/",
    "qa": "https://sanctuary--qa.sandbox.my.salesforce.com/",
    "poc": "https://sanctuary--poc.sandbox.lightning.force.com/",
}


@click.group()
@click.pass_context
def salesforce(ctx: click.Context):
    """Manage Salesforce interactions."""
    ctx.ensure_object(dict)


@salesforce.command()
@click.option(
    "--alias",
    required=True,
    type=click.Choice(ENVIRONMENTS.keys(), case_sensitive=False),
    help=f"Environment to login to: {', '.join(ENVIRONMENTS.keys())}",
)
def login(alias):
    """Login to a specified Salesforce environment using Salesforce CLI."""
    alias = alias.lower()
    if alias in ENVIRONMENTS:
        console.print(
            f"Attempting login to [bold blue]{alias}[/bold blue]...",
            style=WARNING_STYLE,
        )
        try:
            cmd = f"org login web --instance-url {ENVIRONMENTS[alias]}"
            result = _run_sf_command(cmd)

            console.print(
                f"[bold green]Successfully initiated login for '{ENVIRONMENTS[alias]}'.[/bold green]"
            )
            console.print(
                "[italic]A browser window should open for authentication.[/italic]"
            )
            if result.get("result"):
                console.print(f"CLI Output:\n{result['result']}")
            if result.get("warnings"):
                console.print(
                    f"[bold yellow]CLI Warnings:\n{result['warnings']}[/bold yellow]"
                )
        except subprocess.CalledProcessError as error:
            console.print(
                f"[bold red]Error during login to '{alias}':[/bold red] {error}",
                style=ERROR_STYLE,
            )
            if error.stdout:
                console.print(f"CLI Output:\n{error.stdout}")
            if error.stderr:
                console.print(f"CLI Errors:\n{error.stderr}", style=ERROR_STYLE)
        except FileNotFoundError:
            console.print(
                "[bold red]Error:[/bold red] 'sf' command not found. Make sure Salesforce CLI is installed and in your PATH.",
                style=ERROR_STYLE,
            )
    else:
        console.print(
            f"[bold red]Error:[/bold red] Invalid environment '{alias}'.",
            style=ERROR_STYLE,
        )
        console.print(f"Choose from: {', '.join(ENVIRONMENTS.keys())}")


@salesforce.command()
@click.option(
    "--format", "output_format", type=click.Choice(["table", "json"]), default="table"
)
def org(output_format: str):
    """List active Salesforce orgs."""
    cmd = "org list"
    result = _run_sf_command(cmd)
    columns_to_show = ["alias", "username", "instanceUrl"]
    print_table(result, columns=columns_to_show)


@salesforce.command()
@click.option(
    "--alias", required=True, help="Alias of the Salesforce org to logout from."
)
def logout(alias):
    """Logout from a Salesforce org using its alias."""
    console.print(
        f"Attempting to logout from [bold blue]{alias}[/bold blue]...",
        style=WARNING_STYLE,
    )
    try:
        cmd = f"org logout --target-org {alias} --no-prompt"
        result = _run_sf_command(cmd)

        console.print(
            f"[bold green]Successfully logged out from '{alias}'.[/bold green]"
        )
        if result.get("result"):
            console.print(f"CLI Output:\n{result['result']}")
        if result.get("warnings"):
            console.print(
                f"[bold yellow]CLI Warnings:\n{result['warnings']}[/bold yellow]"
            )
    except subprocess.CalledProcessError as error:
        console.print(
            f"[bold red]Error during logout from '{alias}':[/bold red] {error}",
            style=ERROR_STYLE,
        )
        if error.stdout:
            console.print(f"CLI Output:\n{error.stdout}")
        if error.stderr:
            console.print(f"CLI Errors:\n{error.stderr}", style=ERROR_STYLE)
    except FileNotFoundError:
        console.print(
            "[bold red]Error:[/bold red] 'sf' command not found. Make sure Salesforce CLI is installed and in your PATH.",
            style=ERROR_STYLE,
        )
