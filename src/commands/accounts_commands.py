import click
from rich.console import Console

# from rich.table import Table

# from ..managers.account_manager import AccountManager
# from ..models.account_model import Account, CreateAccountParams

console = Console()
ERROR_STYLE = "bold red"
SUCCESS_STYLE = "bold green"
WARNING_STYLE = "bold yellow"


@click.group()
@click.pass_context
def accounts(ctx: click.Context):
    """Manage Salesforce accounts."""
    ctx.ensure_object(dict)
    # ctx.obj["account_manager"] = AccountManager(ctx.obj["org"])


@accounts.command()
@click.option("--name", required=True, help="Account name")
def create(name):
    """Create a new account."""
    click.echo(f"Creating account: {name}")
    # ... (Lógica de creación de cuenta) ...


@accounts.command()
def list_accounts():
    """List all accounts."""
    click.echo("Listing accounts...")
    # ... (Lógica de listado de cuentas) ...
