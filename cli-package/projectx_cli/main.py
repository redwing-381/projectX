"""ProjectX CLI - Smart notification bridge command-line interface."""

import json
from contextlib import nullcontext

import typer
from rich.console import Console
from rich.table import Table

from projectx_cli.config import load_config, get_server_url, set_server_url
from projectx_cli.client import ProjectXClient, APIError, ConnectionError

app = typer.Typer(
    name="projectx",
    help="Smart notification bridge - monitors email, detects urgency with AI, sends SMS alerts",
    add_completion=False,
)

config_app = typer.Typer(help="Manage CLI configuration")
app.add_typer(config_app, name="config")

console = Console()


def get_client() -> ProjectXClient:
    """Get configured API client."""
    return ProjectXClient(get_server_url())


def handle_error(e: Exception, json_output: bool = False) -> None:
    """Handle errors consistently."""
    if isinstance(e, ConnectionError):
        message = f"Connection failed: {e.message}"
    elif isinstance(e, APIError):
        message = f"Server error: {e.message}"
    else:
        message = f"Error: {str(e)}"

    if json_output:
        console.print(json.dumps({"success": False, "error": message}))
    else:
        console.print(f"[red]✗[/red] {message}")
    raise typer.Exit(code=1)


@app.command()
def status(json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON")):
    """Check if the ProjectX server is running."""
    client = get_client()
    server_url = get_server_url()

    try:
        health = client.health()
        detailed = client.status()

        if json_output:
            result = {"success": True, "server_url": server_url, "health": health, "status": detailed}
            console.print(json.dumps(result, indent=2))
        else:
            console.print(f"\n[bold]Server:[/bold] {server_url}")
            console.print(f"[green]✓[/green] Server is running")
            console.print(f"  App: {health.get('app_name', 'Unknown')}")
            console.print(f"  Pipeline ready: {detailed.get('pipeline_ready', False)}")
            if detailed.get("startup_error"):
                console.print(f"  [yellow]Warning:[/yellow] {detailed['startup_error']}")
            console.print()

    except (ConnectionError, APIError) as e:
        if json_output:
            console.print(json.dumps({"success": False, "server_url": server_url, "error": str(e)}, indent=2))
            raise typer.Exit(code=1)
        else:
            console.print(f"\n[bold]Server:[/bold] {server_url}")
            console.print(f"[red]✗[/red] Server is offline")
            console.print(f"  Error: {e}")
            console.print()
            raise typer.Exit(code=1)



@app.command()
def check(json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON")):
    """Trigger an email check and display results."""
    client = get_client()

    try:
        with console.status("[bold blue]Checking emails...[/bold blue]") if not json_output else nullcontext():
            result = client.check()

        if json_output:
            console.print(json.dumps(result, indent=2))
        else:
            data = result.get("data", {})
            emails_checked = data.get("emails_checked", 0)
            alerts_sent = data.get("alerts_sent", 0)
            results = data.get("results", [])

            console.print(f"\n[green]✓[/green] {result.get('message', 'Check complete')}")
            console.print(f"  Emails checked: {emails_checked}")
            console.print(f"  Alerts sent: {alerts_sent}")

            if alerts_sent > 0 and results:
                console.print("\n[bold]Urgent emails:[/bold]")
                table = Table(show_header=True, header_style="bold")
                table.add_column("Sender", style="cyan")
                table.add_column("Subject")
                table.add_column("SMS", style="green")

                for r in results:
                    if r.get("urgency") == "URGENT":
                        sms_status = "✓" if r.get("sms_sent") else "✗"
                        table.add_row(r.get("sender", ""), r.get("subject", ""), sms_status)
                console.print(table)
            elif alerts_sent == 0:
                console.print("\n[dim]No urgent emails found[/dim]")
            console.print()

    except (ConnectionError, APIError) as e:
        handle_error(e, json_output)


@app.command()
def test(json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON")):
    """Test the urgency classification with a sample email."""
    client = get_client()

    try:
        with console.status("[bold blue]Testing classification...[/bold blue]") if not json_output else nullcontext():
            result = client.test_urgent()

        if json_output:
            console.print(json.dumps(result, indent=2))
        else:
            data = result.get("data", {})
            email = data.get("email", {})
            classification = data.get("classification", {})
            sms_sent = data.get("sms_sent", False)
            sms_error = data.get("sms_error")

            console.print("\n[bold]Test Email:[/bold]")
            console.print(f"  From: {email.get('sender', 'Unknown')}")
            console.print(f"  Subject: {email.get('subject', 'Unknown')}")

            urgency = classification.get("urgency", "Unknown")
            reason = classification.get("reason", "No reason")

            if urgency == "URGENT":
                console.print(f"\n[bold red]Classification: {urgency}[/bold red]")
            else:
                console.print(f"\n[bold green]Classification: {urgency}[/bold green]")
            console.print(f"  Reason: {reason}")

            if sms_sent:
                console.print(f"\n[green]✓[/green] SMS sent to your phone")
            elif sms_error:
                console.print(f"\n[red]✗[/red] SMS failed: {sms_error}")
            else:
                console.print(f"\n[dim]No SMS sent (not urgent or SMS disabled)[/dim]")
            console.print()

    except (ConnectionError, APIError) as e:
        handle_error(e, json_output)


@config_app.command("show")
def config_show(json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON")):
    """Display current configuration."""
    config = load_config()
    if json_output:
        console.print(config.model_dump_json(indent=2))
    else:
        console.print("\n[bold]ProjectX Configuration[/bold]")
        console.print(f"  Server URL: {config.server_url}")
        console.print()


@config_app.command("set-url")
def config_set_url(
    url: str = typer.Argument(..., help="Server URL to set"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Set the server URL."""
    set_server_url(url)
    if json_output:
        console.print(json.dumps({"success": True, "server_url": url}))
    else:
        console.print(f"\n[green]✓[/green] Server URL set to: {url}")
        console.print()


if __name__ == "__main__":
    app()
