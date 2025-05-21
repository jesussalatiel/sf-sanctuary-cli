#!/usr/bin/env python3
import click
import json
import subprocess
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table

# Console configuration
console = Console()
ERROR_STYLE = "bold red"
SUCCESS_STYLE = "bold green"
WARNING_STYLE = "bold yellow"


# --------------------------------------------------
# Data Models
# --------------------------------------------------
class UserRole(Enum):
    STANDARD = "Standard User"
    ADMIN = "System Administrator"
    READ_ONLY = "Read Only"


@dataclass
class User:
    id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.STANDARD
    is_active: bool = True
    created_date: Optional[datetime] = None


# --------------------------------------------------
# Business Logic
# --------------------------------------------------
class UserManager:
    def __init__(self, target_org: str = "default"):
        self.target_org = target_org

    def _run_sf_command(self, command: str) -> Dict:
        """Executes a Salesforce CLI command"""
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
        """Creates a new user in Salesforce"""
        values = [
            f"Username={user.email}",
            f"Email={user.email}",
            f"FirstName={user.first_name}" if user.first_name else "",
            f"LastName={user.last_name}",
            f"Alias={user.username[:5]}",
            f"ProfileId={self._get_profile_id(user.role)}",
            "TimeZoneSidKey=America/New_York",
            "LocaleSidKey=en_US",
            "EmailEncodingKey=UTF-8",
            "LanguageLocaleKey=en_US",
        ]

        cmd = f"data create record --sobject User --values \"{' '.join(v for v in values if v)}\""
        result = self._run_sf_command(cmd)

        user.id = result["result"]["id"]
        return user

    def list_users(self, active_only: bool = True) -> List[User]:
        """Lists users with optional active filter"""
        where = "WHERE IsActive = true" if active_only else ""
        query = f"SELECT Id, Username, Email, FirstName, LastName, Profile.Name, IsActive FROM User {where} ORDER BY LastName"

        result = self._run_sf_command(f'data query --query "{query}"')
        return [
            User(
                id=record.get("Id"),
                username=record.get("Username"),
                email=record.get("Email"),
                first_name=record.get("FirstName"),
                last_name=record.get("LastName"),
                role=self._parse_role(
                    record.get("Profile", {}).get("Name")
                    if record.get("Profile")
                    else None
                ),
                is_active=record.get("IsActive", False),
            )
            for record in result.get("result", {}).get("records", [])
        ]

    def _get_profile_id(self, role: UserRole) -> str:
        """Gets profile ID based on user role"""
        query = f"SELECT Id FROM Profile WHERE Name = '{role.value}'"
        result = self._run_sf_command(f'data query --query "{query}"')

        if not result.get("result", {}).get("records"):
            raise click.ClickException(f"Profile not found for role: {role.value}")

        return result["result"]["records"][0]["Id"]

    @staticmethod
    def _parse_role(profile_name: Optional[str]) -> UserRole:
        """Converts profile name to UserRole enum"""
        if not profile_name:
            return UserRole.STANDARD
        if "Administrator" in profile_name:
            return UserRole.ADMIN
        elif "Read Only" in profile_name:
            return UserRole.READ_ONLY
        return UserRole.STANDARD


# --------------------------------------------------
# CLI Commands
# --------------------------------------------------
@click.group()
@click.option("--org", default="default", help="Salesforce org alias")
@click.option("--verbose", is_flag=True, help="Show execution details")
@click.pass_context
def cli(ctx, org, verbose):
    """CLI tool for managing Salesforce users"""
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
def create(ctx, email, first_name, last_name, role, username):
    """Create a new user"""
    try:
        manager = ctx.obj["manager"]

        user = User(
            email=email,
            username=username or email,
            first_name=first_name,
            last_name=last_name,
            role=UserRole[role.upper()],
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
@click.option("--format", type=click.Choice(["table", "json"]), default="table")
@click.pass_context
def list(ctx, active_only, format):
    """List all users"""
    manager = ctx.obj["manager"]
    users = manager.list_users(active_only)

    if format == "json":
        click.echo(json.dumps([u.__dict__ for u in users], indent=2, default=str))
    else:
        table = Table(title="Salesforce Users")
        table.add_column("ID", style="cyan")
        table.add_column("Name")
        table.add_column("Email")
        table.add_column("Role")
        table.add_column("Status")

        for user in users:
            status = "[green]✓[/green]" if user.is_active else "[red]✗[/red]"
            table.add_row(
                user.id or "",
                f"{user.first_name or ''} {user.last_name}",
                user.email,
                user.role.name,
                status,
            )

        console.print(table)


@cli.command()
@click.argument("user_id")
@click.option("--deactivate", is_flag=True, help="Deactivate user")
@click.option("--activate", is_flag=True, help="Activate user")
@click.pass_context
def update(ctx, user_id, deactivate, activate):
    """Update an existing user"""
    if deactivate and activate:
        raise click.BadParameter("You can't activate and deactivate at the same time")

    manager = ctx.obj["manager"]

    try:
        if deactivate or activate:
            value = "false" if deactivate else "true"
            cmd = f'data update record --sobject User --record-id {user_id} --values "IsActive={value}"'
            manager._run_sf_command(cmd)

            action = "deactivated" if deactivate else "activated"
            console.print(f"User successfully {action}", style=SUCCESS_STYLE)
        else:
            console.print("No update action specified", style=WARNING_STYLE)

    except Exception as e:
        console.print(f"Error updating user: {str(e)}", style=ERROR_STYLE)
        raise click.Abort()


# --------------------------------------------------
# Main Execution
# --------------------------------------------------
if __name__ == "__main__":
    cli()
