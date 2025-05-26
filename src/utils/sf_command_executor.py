import subprocess
import json
from typing import Dict
import click


def _run_command(command: str) -> Dict:
    """Executes a Salesforce CLI command and returns parsed JSON output."""
    try:
        result = subprocess.run(
            f"{command}",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error executing CLI command: {e}")
        if e.stderr:
            try:
                error_json = json.loads(e.stderr)
                raise click.ClickException(
                    error_json.get("message", "CLI command failed.")
                )
            except json.JSONDecodeError:
                raise click.ClickException(f"CLI command failed with error: {e.stderr}")
        else:
            raise click.ClickException("CLI command failed.")
    except FileNotFoundError:
        raise click.ClickException(
            "The 'sf' command was not found. Please ensure Salesforce CLI is installed and in your PATH."
        )
    except json.JSONDecodeError as e:
        raise click.ClickException(
            f"Error parsing JSON output from Salesforce CLI: {e}"
        )
    except Exception as e:
        raise click.ClickException(f"An unexpected error occurred: {e}")


def _run_sf_command(command: str) -> Dict:
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
        click.echo(f"Error executing Salesforce CLI command: {e}")
        if e.stderr:
            try:
                error_json = json.loads(e.stderr)
                raise click.ClickException(
                    error_json.get("message", "Salesforce CLI command failed.")
                )
            except json.JSONDecodeError:
                raise click.ClickException(
                    f"Salesforce CLI command failed with error: {e.stderr}"
                )
        else:
            raise click.ClickException("Salesforce CLI command failed.")
    except FileNotFoundError:
        raise click.ClickException(
            "The 'sf' command was not found. Please ensure Salesforce CLI is installed and in your PATH."
        )
    except json.JSONDecodeError as e:
        raise click.ClickException(
            f"Error parsing JSON output from Salesforce CLI: {e}"
        )
    except Exception as e:
        raise click.ClickException(f"An unexpected error occurred: {e}")
