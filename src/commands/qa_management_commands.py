"""Jira CLI QA Tool: Retrieves and displays Jira issues by project or sprint."""

import os
from typing import List, Dict, Optional, Any

import click
from dotenv import load_dotenv
from jira import JIRA
from rich.console import Console
from rich.table import Table

load_dotenv()

JIRA_SERVER: Optional[str] = os.environ.get("JIRA_SERVER")
JIRA_EMAIL: Optional[str] = os.environ.get("JIRA_EMAIL")
JIRA_TOKEN: Optional[str] = os.environ.get("JIRA_TOKEN")

console = Console()


@click.group()
@click.pass_context
def qa(ctx: click.Context) -> None:
    """Manage Jira reports.

    Examples:
        $ python cli.py qa get-project-keys
        $ python cli.py qa get-project-issues --project-key CXP
    """
    ctx.ensure_object(dict)
    ctx.obj["jira_server"] = JIRA_SERVER
    ctx.obj["jira_email"] = JIRA_EMAIL
    ctx.obj["jira_token"] = JIRA_TOKEN


@qa.command()
@click.option(
    "--fields",
    default="key,summary,status,assignee",
    help="Comma-separated list of issue fields to display",
)
@click.option("--status", help="Filter issues by status (e.g., 'To Do', 'In Progress')")
@click.option("--project-key", required=True, help="Select Jira project key")
@click.option("--assignee", help="Filter by assignee (username or display name)")
def get_project_issues(
    project_key: str, fields: str, status: Optional[str], assignee: Optional[str]
) -> None:
    """Show issues for a project, optionally filtered by status and assignee."""
    if not all([JIRA_SERVER, JIRA_EMAIL, JIRA_TOKEN]):
        console.print(
            "JIRA_SERVER, JIRA_EMAIL, and JIRA_TOKEN environment variables must be set.",
            style="red",
        )
        return

    jira = JIRA({"server": JIRA_SERVER}, basic_auth=(JIRA_EMAIL, JIRA_TOKEN))
    jql = build_jql(project_key, status=status, assignee=assignee)

    field_list = [f.strip() for f in fields.split(",")]
    if "status" not in field_list and assignee:
        field_list.append("status")
    jira_fields = ",".join(set(field_list))

    issues = jira.search_issues(jql, maxResults=1000, fields=jira_fields)
    extracted_data = [extract_issue_data(issue, field_list) for issue in issues]

    if extracted_data:
        print_colored_table(
            extracted_data, field_list, title=f"Issues for '{project_key}'"
        )

        if assignee:
            status_counts: Dict[str, int] = {}
            for issue_data in extracted_data:
                status_name = issue_data.get("status", "-")
                status_counts[status_name] = status_counts.get(status_name, 0) + 1

            summary_data = [{"Status": k, "Count": v} for k, v in status_counts.items()]
            print_colored_table(
                summary_data, ["Status", "Count"], title=f"Summary for '{assignee}'"
            )
    else:
        console.print(f"No issues found for project '{project_key}'.", style="red")


@qa.command()
def get_project_keys() -> None:
    """Display the key, name, and ID of all Jira projects.

    Example:
        $ python cli.py qa get-project-keys
    """
    if not all([JIRA_SERVER, JIRA_EMAIL, JIRA_TOKEN]):
        console.print(
            "JIRA_SERVER, JIRA_EMAIL, and JIRA_TOKEN environment variables must be set.",
            style="red",
        )
        return

    jira = JIRA({"server": JIRA_SERVER}, basic_auth=(JIRA_EMAIL, JIRA_TOKEN))
    project_list = jira.projects()
    columns = ["id", "key", "name"]
    data = [{"id": p.id, "key": p.key, "name": p.name} for p in project_list]

    if data:
        print_colored_table(data, columns)
    else:
        console.print("No projects found in Jira.", style="info")


@qa.command()
@click.option("--project-key", default="CXP", help="The Jira project key")
@click.option("--sprint-name", default="Sprint 1", help="The name of the sprint")
@click.option("--status", help="Filter issues by status")
@click.pass_context
def get_sprint_issues(
    ctx: click.Context,
    project_key: str,
    sprint_name: str,
    status: Optional[str],
) -> None:
    """Retrieve issues from a sprint with optional filters.

    Examples:
        $ python cli.py qa get-sprint-issues --sprint-name "Sprint 5"
        $ python cli.py qa get-sprint-issues --status "QA in Progress"
    """
    if not all(
        [
            ctx.obj.get("jira_server"),
            ctx.obj.get("jira_email"),
            ctx.obj.get("jira_token"),
        ]
    ):
        console.print(
            "Jira credentials not properly initialized in context.", style="red"
        )
        return

    jira_options = {"server": ctx.obj["jira_server"]}
    jira_auth = (ctx.obj["jira_email"], ctx.obj["jira_token"])
    jira = JIRA(jira_options, basic_auth=jira_auth)

    jql_parts = [f'project = "{project_key}"', f'sprint = "{sprint_name}"']
    if status:
        jql_parts.append(f'status = "{status}"')
    jql = " AND ".join(jql_parts)

    fields_to_fetch = "key,summary,status,assignee"
    field_list = [f.strip() for f in fields_to_fetch.split(",")]
    jira_fields = ",".join(set(field_list + ["key", "summary", "status", "assignee"]))

    issues = jira.search_issues(jql, maxResults=1000, fields=jira_fields)
    extracted_data: List[Dict[str, Any]] = []

    def _extract_field_value(fields_data: Any, field_name: str) -> Any:
        """Helper to extract field values safely."""
        if field_name == "summary":
            return getattr(fields_data, "summary", "-")
        if field_name == "status":
            return getattr(fields_data.status, "name", "-")
        if field_name == "assignee":
            return (
                getattr(fields_data.assignee, "displayName", "-")
                if fields_data.assignee
                else "-"
            )
        if hasattr(fields_data, field_name):
            return getattr(fields_data, field_name)
        return getattr(
            fields_data, f'customfield_{field_name.lower().replace(" ", "_")}', "-"
        )

    for issue in issues:
        fields_data = issue.fields
        item: Dict[str, Any] = {"key": issue.key}
        for field_name in field_list:
            item[field_name] = _extract_field_value(fields_data, field_name)
        item["link"] = f"{ctx.obj['jira_server']}/browse/{issue.key}"
        extracted_data.append(item)

    if extracted_data:
        if "link" not in field_list:
            field_list.append("link")
        print_colored_table(
            extracted_data,
            field_list,
            title=f"Issues for Project '{project_key}' in Sprint '{sprint_name}'",
        )
    else:
        console.print(
            f"No issues found for project '{project_key}', sprint '{sprint_name}'.",
            style="red",
        )


def extract_issue_data(issue, field_list: List[str]) -> Dict:
    """Extract relevant fields from a Jira issue."""
    data: Dict[str, Any] = {"key": issue.key}
    fields_data = issue.fields

    for field in field_list:
        if field == "summary":
            data["summary"] = getattr(fields_data, "summary", "-")
        elif field == "status":
            data["status"] = getattr(fields_data.status, "name", "-")
        elif field == "assignee":
            data["assignee"] = (
                getattr(fields_data.assignee, "displayName", "-")
                if fields_data.assignee
                else "-"
            )
        elif hasattr(fields_data, field):
            data[field] = getattr(fields_data, field)
        else:
            data[field] = getattr(
                fields_data, f'customfield_{field.lower().replace(" ", "_")}', "-"
            )

    return data


def build_jql(
    project_key: str,
    sprint_name: Optional[str] = None,
    status: Optional[str] = None,
    assignee: Optional[str] = None,
) -> str:
    """Builds a JQL string from optional parameters."""
    jql_parts = [f'project = "{project_key}"']
    if sprint_name:
        jql_parts.append(f'sprint = "{sprint_name}"')
    if status:
        jql_parts.append(f'status = "{status}"')
    if assignee:
        jql_parts.append(f'assignee = "{assignee}"')
    return " AND ".join(jql_parts)


def print_colored_table(
    data: List[Dict], columns: List[str], title: str = "Jira Issues"
) -> None:
    """Prints a list of dictionaries in a colored table using rich.

    Args:
        data (List[Dict]): List of issue data dictionaries.
        columns (List[str]): List of fields to show.
        title (str): Title for the table.
    """
    if not data:
        console.print("No issues to display.")
        return

    table = Table(title=title)
    colors = ["cyan", "magenta", "yellow", "green", "blue", "red"]
    for index, header in enumerate(columns):
        table.add_column(f"[{colors[index % len(colors)]}]{header}[/]")

    for item in data:
        row = [str(item.get(header, "N/A")) for header in columns]
        table.add_row(*row)

    console.print(table)
