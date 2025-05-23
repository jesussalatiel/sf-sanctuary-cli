import click
from commands.users_commands import users
from commands.accounts_commands import accounts
from commands.qa_management_commands import qa
from commands.salesforce_commands import salesforce


@click.group()
@click.option("--org", default="default", help="Salesforce org alias")
@click.option("--verbose", is_flag=True, help="Show execution details")
@click.pass_context
def cli(ctx: click.Context, org: str, verbose: bool) -> None:
    """CLI tool for managing Salesforce entities."""
    ctx.ensure_object(dict)
    ctx.obj["org"] = org
    ctx.obj["verbose"] = verbose


cli.add_command(salesforce)
cli.add_command(users)
cli.add_command(accounts)
cli.add_command(qa)

if __name__ == "__main__":
    cli.main()
