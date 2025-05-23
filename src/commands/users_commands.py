import click
from rich.console import Console
from rich.table import Table
import json
from managers.user_manager import UserManager
from models.user_model import CreateUserParams, UserRole, User
from utils.logger import configure_logger

console = Console()
ERROR_STYLE = "bold red"
SUCCESS_STYLE = "bold green"
WARNING_STYLE = "bold yellow"

logger = configure_logger(__name__)


@click.group()
@click.pass_context
def users(ctx: click.Context):
    """Manage Salesforce users."""
    ctx.ensure_object(dict)
    ctx.obj["user_manager"] = UserManager(ctx.obj["org"])


@users.command()
@click.option("--email", required=True, help="User's email")
@click.option("--first-name", help="User's first name")
@click.option("--last-name", required=True, help="User's last name")
@click.option(
    "--role",
    type=click.Choice([role.name.lower() for role in UserRole]),
    default="standard",
    help="User's role",
)
@click.option("--username", help="Username (default: email)")
@click.option("--phone", help="User's phone number")
@click.option("--title", help="User's job title")
@click.option("--department", help="User's department")
@click.option("--company", help="User's company name")
@click.pass_context
def create(ctx: click.Context, **kwargs) -> None:
    """Create a new user."""
    manager: UserManager = ctx.obj["user_manager"]
    params = CreateUserParams(**kwargs)
    user_role = UserRole[params.role.upper()]

    user = User(
        email=params.email,
        username=params.username or params.email,
        first_name=params.first_name,
        last_name=params.last_name,
        role=user_role,
    )

    if ctx.obj["verbose"]:
        console.print("Creating user:", style=WARNING_STYLE)
        console.print(user)

    created_user = manager.create_user(user)

    logger.info(f"User created successfully with ID: {created_user.id}")


@users.command()
@click.option("--active-only", is_flag=True, help="Show only active users")
@click.option(
    "--format", "output_format", type=click.Choice(["table", "json"]), default="table"
)
@click.pass_context
def list_users(ctx: click.Context, active_only: bool, output_format: str):
    """List all users."""
    manager: UserManager = ctx.obj["user_manager"]
    users = manager.list_users(active_only)
    if output_format == "json":
        # Convert User dataclasses to dict, handle datetime serialization
        click.echo(json.dumps([u.__dict__ for u in users], indent=2, default=str))
    else:
        table = Table(title="Salesforce Users")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Username", style="magenta")
        table.add_column("Email", style="green")
        table.add_column("Name", style="yellow")
        table.add_column("Role", style="blue")
        table.add_column("Active", style="red")

        for user in users:
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            table.add_row(
                user.id or "",
                user.username or "",
                user.email or "",
                name,
                user.role.value,
                "Yes" if user.is_active else "No",
            )
        console.print(table)
