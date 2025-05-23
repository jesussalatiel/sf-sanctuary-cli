import click
from typing import Optional, Dict, List
from models.user_model import User, UserRole
from utils.sf_command_executor import _run_sf_command


class UserManager:
    """Business logic for managing Salesforce users."""

    def __init__(self, target_org: str = "default") -> None:
        self.target_org = target_org

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
        result = _run_sf_command(cmd)
        user.id = result["result"]["id"]
        return user

    def list_users(self, active_only: bool = True) -> List[User]:
        """Lists Salesforce users, optionally filtering by active status."""
        where_clause = "WHERE IsActive = true" if active_only else ""
        query = (
            "SELECT Id, Username, Email, FirstName, LastName, Profile.Name, IsActive "
            f"FROM User {where_clause} ORDER BY LastName"
        )

        result = _run_sf_command(f'data query --query "{query}"')
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
        result = _run_sf_command(f'data query --query "{query}"')
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
