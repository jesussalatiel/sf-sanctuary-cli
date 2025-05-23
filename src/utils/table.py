from typing import Dict, List
from rich.console import Console
from rich.table import Table

console = Console()


def print_table(data: Dict, columns: List[str] = None):
    """Prints specified key information from the JSON in a colored table without lines."""
    results = data.get("result", {})
    other_orgs = results.get("other", [])
    non_scratch_orgs = results.get("nonScratchOrgs", [])

    all_orgs = other_orgs + non_scratch_orgs

    if not all_orgs:
        console.print("No organization details found.")
        return

    if columns is None:
        headers = set()
        for org in all_orgs:
            headers.update(org.keys())
        columns = sorted(list(headers))

    table = Table(title="Salesforce Organizations", show_lines=False)
    colors = ["cyan", "magenta", "yellow", "green", "blue", "red"]
    color_index = 0

    for header in columns:
        table.add_column(f"[{colors[color_index % len(colors)]}]{header}[/]")
        color_index += 1

    for org in all_orgs:
        row = [str(org.get(header, "N/A")) for header in columns]
        table.add_row(*row)

    console.print(table)
