"""
CLI tool for managing Salesforce users.
"""

import json
import subprocess
from enum import Enum
from typing import Optional, Dict, List
from datetime import datetime
from dataclasses import dataclass

import click
from rich.console import Console
from rich.table import Table

# Console configuration
console = Console()
ERROR_STYLE = "bold red"
SUCCESS_STYLE = "bold green"
WARNING_STYLE = "bold yellow"


class UserRole(Enum):
    """User roles mapping to Salesforce profiles."""

    STANDARD = "Standard User"
    ADMIN = "System Administrator"
    READ_ONLY = "Read Only"


@dataclass
class UserBase:
    """Base data model for a Salesforce user."""

    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.STANDARD
    is_active: bool = True


@dataclass
class User(UserBase):
    """Complete data model for a Salesforce user."""

    id: Optional[str] = None
    created_date: Optional[datetime] = None


@dataclass
class CreateUserParams:
    """Parameters for creating a new user."""

    email: str
    last_name: str
    first_name: Optional[str] = None
    role: str = "standard"
    username: Optional[str] = None


class UserManager:
    """Business logic for managing Salesforce users."""

    def __init__(self, target_org: str = "default") -> None:
        self.target_org = target_org

    def _run_sf_command(self, command: str) -> Dict:
        """Executes a Salesforce CLI command and returns parsed JSON output."""
        try:
            result = subprocess.run(
                f"sf {command} --json",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            error = json.loads(e.stderr) if e.stderr else {"message": "Unknown error"}
            raise click.ClickException(error.get("message", "Command failed"))

    def create_user(self, user: User) -> User:
        """Creates a new Salesforce user and returns the updated User object."""
        values = [
            f"Username={user.email}",
            f"Email={user.email}",
            f"FirstName={user.first_name}" if user.first_name else "",
            f"LastName={user.last_name}",
            f"Alias={user.username[:5]}" if user.username else "",
            f"ProfileId={self._get_profile_id(user.role)}",
            "TimeZoneSidKey=America/New_York",
            "LocaleSidKey=en_US",
            "EmailEncodingKey=UTF-8",
            "LanguageLocaleKey=en_US",
        ]

        cmd = (
            f"data create record --sobject User --values "
            f"\"{' '.join(value for value in values if value)}\""
        )
        result = self._run_sf_command(cmd)
        user.id = result["result"]["id"]
        return user

    def list_users(self, active_only: bool = True) -> List[User]:
        """Lists Salesforce users, optionally filtering by active status."""
        where_clause = "WHERE IsActive = true" if active_only else ""
        query = (
            "SELECT Id, Username, Email, FirstName, LastName, Profile.Name, IsActive "
            f"FROM User {where_clause} ORDER BY LastName"
        )

        result = self._run_sf_command(f'data query --query "{query}"')
        records = result.get("result", {}).get("records", [])
        users = []
        for record in records:
            profile_name = (
                record.get("Profile", {}).get("Name") if record.get("Profile") else None
            )
            users.append(
                User(
                    id=record.get("Id"),
                    username=record.get("Username"),
                    email=record.get("Email"),
                    first_name=record.get("FirstName"),
                    last_name=record.get("LastName"),
                    role=self._parse_role(profile_name),
                    is_active=record.get("IsActive", False),
                )
            )
        return users

    def _get_profile_id(self, role: UserRole) -> str:
        """Fetches the Salesforce Profile Id for a given user role."""
        query = f"SELECT Id FROM Profile WHERE Name = '{role.value}'"
        result = self._run_sf_command(f'data query --query "{query}"')
        records = result.get("result", {}).get("records")
        if not records:
            raise click.ClickException(f"Profile not found for role: {role.value}")
        return records[0]["Id"]

    @staticmethod
    def _parse_role(profile_name: Optional[str]) -> UserRole:
        """Converts Salesforce profile name to UserRole enum."""
        if not profile_name:
            return UserRole.STANDARD
        if "Administrator" in profile_name:
            return UserRole.ADMIN
        if "Read Only" in profile_name:
            return UserRole.READ_ONLY
        return UserRole.STANDARD


@click.group()
@click.option("--org", default="default", help="Salesforce org alias")
@click.option("--verbose", is_flag=True, help="Show execution details")
@click.pass_context
def cli(ctx: click.Context, org: str, verbose: bool) -> None:
    """CLI tool for managing Salesforce users."""
    ctx.ensure_object(dict)
    ctx.obj["manager"] = UserManager(org)
    ctx.obj["verbose"] = verbose


@cli.command()
@click.option("--email", required=True, help="User's email")
@click.option("--first-name", help="User's first name")
@click.option("--last-name", required=True, help="User's last name")
@click.option(
    "--role",
    type=click.Choice(["standard", "admin", "readonly"]),
    default="standard",
    help="User's role",
)
@click.option("--username", help="Username (default: email)")
@click.pass_context
def create(ctx: click.Context, **kwargs) -> None:
    """Create a new user."""
    try:
        manager: UserManager = ctx.obj["manager"]
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
        console.print(
            f"User created with ID: [bold]{created_user.id}[/bold]", style=SUCCESS_STYLE
        )

    except Exception as e:
        console.print(f"Error: {str(e)}", style=ERROR_STYLE)
        raise click.Abort()


@cli.command()
@click.option("--active-only", is_flag=True, help="Show only active users")
@click.option(
    "--format", "output_format", type=click.Choice(["table", "json"]), default="table"
)
@click.pass_context
def list_users(ctx: click.Context, active_only: bool, output_format: str) -> None:
    """List all users."""
    manager: UserManager = ctx.obj["manager"]
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


if __name__ == "__main__":
    cli.main(standalone_mode=False)
