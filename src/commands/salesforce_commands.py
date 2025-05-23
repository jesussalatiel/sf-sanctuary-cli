import click
from rich.console import Console
import subprocess
from utils.sf_command_executor import _run_sf_command
from utils.table import print_table
from rich.table import Table
import json

console = Console()
ERROR_STYLE = "bold red"
SUCCESS_STYLE = "bold green"
WARNING_STYLE = "bold yellow"

ENVIRONMENTS = {
    "dev": "https://sanctuary--commondev.sandbox.my.salesforce.com/",
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
    "--env",
    required=True,
    type=click.Choice(ENVIRONMENTS.keys(), case_sensitive=False),
    help=f"Environment to login to: {', '.join(ENVIRONMENTS.keys())}",
)
def login(env):
    """Login to a specified Salesforce environment using Salesforce CLI."""
    if env.lower() in ENVIRONMENTS:
        alias = env.lower()
        console.print(
            f"Attempting login to [bold blue]{alias}[/bold blue]...",
            style=WARNING_STYLE,
        )
        try:
            cmd = "org login web --alias commondev"
            result = _run_sf_command(cmd)

            console.print(
                f"[bold green]Successfully initiated login for '{alias}'.[/bold green]"
            )
            console.print(
                "[italic]A browser window should open for authentication.[/italic]"
            )
            if result.stdout:
                console.print(f"CLI Output:\n{result.stdout}")
            if result.stderr:
                console.print(
                    f"[bold yellow]CLI Errors/Warnings:\n{result.stderr}[/bold yellow]"
                )
        except subprocess.CalledProcessError as e:
            console.print(
                f"[bold red]Error during login to '{alias}':[/bold red] {e}",
                style=ERROR_STYLE,
            )
            if e.stdout:
                console.print(f"CLI Output:\n{e.stdout}")
            if e.stderr:
                console.print(f"CLI Errors:\n{e.stderr}", style=ERROR_STYLE)
        except FileNotFoundError:
            console.print(
                "[bold red]Error:[/bold red] 'sf' command not found. Make sure Salesforce CLI is installed and in your PATH.",
                style=ERROR_STYLE,
            )
    else:
        console.print(
            f"[bold red]Error:[/bold red] Invalid environment '{env}'.",
            style=ERROR_STYLE,
        )
        console.print(f"Choose from: {', '.join(ENVIRONMENTS.keys())}")


@salesforce.command()
@click.option(
    "--format", "output_format", type=click.Choice(["table", "json"]), default="table"
)
def org(output_format: str):
    # sf org list
    cmd = "org list"
    result = _run_sf_command(cmd)
    columns_to_show = ["alias", "username", "instanceUrl"]
    print_table(result, columns=columns_to_show)
