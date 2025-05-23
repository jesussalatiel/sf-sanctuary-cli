import click
from jira import JIRA
from dotenv import load_dotenv
import os
from rich.console import Console
from rich.table import Table
from typing import List, Dict

load_dotenv()

jira_server = os.environ.get("JIRA_SERVER")
jira_email = os.environ.get("JIRA_EMAIL")
jira_token = os.environ.get("JIRA_TOKEN")

console = Console()


def print_colored_table(
    data: List[Dict], columns: List[str], title: str = "Jira Issues"
):
    """Prints a list of dictionaries in a colored table using rich."""
    if not data:
        console.print("No issues to display.")
        return

    table = Table(title=title)
    colors = ["cyan", "magenta", "yellow", "green", "blue", "red"]
    color_index = 0

    for header in columns:
        table.add_column(f"[{colors[color_index % len(colors)]}]{header}[/]")
        color_index += 1

    for item in data:
        row = [str(item.get(header, "N/A")) for header in columns]
        table.add_row(*row)

    console.print(table)


@click.group()
@click.pass_context
def qa(ctx: click.Context):
    """Manage Jira Reports."""
    ctx.ensure_object(dict)


@qa.command()
@click.option(
    "--fields",
    default="key,summary,status,assignee",
    help="Comma-separated list of issue fields to display",
)
@click.option("--status", help="Filter issues by status (e.g., 'To Do', 'In Progress')")
@click.option("--project-key", required=True, help="Select Project")
@click.option(
    "--assignee", help="Filter issues by assignee (Jira username or display name)"
)
def get_project_issues(project_key, fields, status, assignee):
    """Retrieves and displays issues for a project, optionally filtered by status and assignee, with status summary if assignee is used."""
    options = {"server": jira_server}
    jira = JIRA(options, basic_auth=(jira_email, jira_token))
    jql_parts = [f'project = "{project_key}"']
    if status:
        jql_parts.append(f'status = "{status}"')
    if assignee:
        jql_parts.append(f'assignee = "{assignee}"')
    jql = " AND ".join(jql_parts)
    field_list = [f.strip() for f in fields.split(",")]

    jira_fields = ",".join(field_list + (["status"] if assignee else []))
    issues = jira.search_issues(jql, maxResults=1000, fields=jira_fields)

    extracted_data = []
    status_counts = {}

    for issue in issues:
        item = {"key": issue.key}
        for field_name in field_list:
            if field_name == "summary":
                item["summary"] = getattr(issue.fields, "summary", "N/A")
            elif field_name == "status":
                item["status"] = getattr(issue.fields.status, "name", "N/A")
                if assignee:
                    status_name = getattr(issue.fields.status, "name", "N/A")
                    status_counts[status_name] = status_counts.get(status_name, 0) + 1
            elif field_name == "assignee":
                item["assignee"] = (
                    getattr(issue.fields.assignee, "displayName", "N/A")
                    if hasattr(issue.fields, "assignee")
                    else "N/A"
                )
            elif hasattr(issue.fields, field_name):
                item[field_name] = getattr(issue.fields, field_name)
            else:
                custom_field_id = f'customfield_{field_name.lower().replace(" ", "_")}'
                item[field_name] = getattr(issue.fields, custom_field_id, "N/A")

        extracted_data.append(item)

    if extracted_data:
        print_colored_table(
            extracted_data, field_list, title=f"Issues for Project '{project_key}'"
        )
        if assignee and status_counts:
            summary_data = [
                {"Status": status, "Count": count}
                for status, count in status_counts.items()
            ]
            print_colored_table(
                summary_data,
                ["Status", "Count"],
                title=f"Summary '{assignee}'",
            )
    else:
        console.print(
            f"No issues found for project '{project_key}' with the specified filters.",
            style="red",
        )


@qa.command()
def get_project_keys():
    """Retrieves and displays the key, name, and ID of all Jira projects."""
    options = {"server": jira_server}
    jira = JIRA(options, basic_auth=(jira_email, jira_token))
    project_list = jira.projects()
    extracted_data = []
    columns = ["id", "key", "name"]

    for project in project_list:
        extracted_data.append(
            {"id": project.id, "key": project.key, "name": project.name}
        )

    if extracted_data:
        print_colored_table(extracted_data, columns)
    else:
        console.print("No projects found in Jira.", style="info")
