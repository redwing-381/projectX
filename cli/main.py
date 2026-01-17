"""ProjectX CLI - Smart notification bridge command-line interface."""

import json
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from cli.config import load_config, save_config, CLIConfig, get_server_url, set_server_url, get_api_key, set_api_key, is_logged_in
from cli.client import ProjectXClient, APIError, ConnectionError

# Create Typer app
app = typer.Typer(
    name="projectx",
    help="Smart notification bridge - monitors email, detects urgency with AI, sends SMS alerts",
    add_completion=False,
)

# Config subcommand group
config_app = typer.Typer(help="Manage CLI configuration")
app.add_typer(config_app, name="config")

# Monitor subcommand group
monitor_app = typer.Typer(help="Control scheduled email monitoring")
app.add_typer(monitor_app, name="monitor")

# Rich console for formatted output
console = Console()


@app.command()
def help(
    ctx: typer.Context = typer.Option(None, hidden=True),
):
    """Show all available commands."""
    console.print("\n[bold blue]ProjectX CLI[/bold blue] - Smart notification bridge\n")
    
    console.print("[bold]Authentication:[/bold]")
    table0 = Table(show_header=False, box=None, padding=(0, 2))
    table0.add_column("Command", style="cyan")
    table0.add_column("Description")
    table0.add_row("projectx login", "Authenticate with your API key")
    table0.add_row("projectx logout", "Remove saved API key")
    console.print(table0)
    
    console.print("\n[bold]Main Commands:[/bold]")
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Command", style="cyan")
    table.add_column("Description")
    table.add_row("projectx status", "Check server health and pipeline status")
    table.add_row("projectx check", "Trigger email check and display results")
    table.add_row("projectx test", "Test classification with sample urgent email")
    console.print(table)
    
    console.print("\n[bold]Config Commands:[/bold]")
    table2 = Table(show_header=False, box=None, padding=(0, 2))
    table2.add_column("Command", style="cyan")
    table2.add_column("Description")
    table2.add_row("projectx config show", "Display current configuration")
    table2.add_row("projectx config set-url <url>", "Set the server URL")
    console.print(table2)
    
    console.print("\n[bold]Monitor Commands:[/bold]")
    table3 = Table(show_header=False, box=None, padding=(0, 2))
    table3.add_column("Command", style="cyan")
    table3.add_column("Description")
    table3.add_row("projectx monitor status", "Show monitoring status (email + mobile)")
    table3.add_row("projectx monitor start", "Enable email monitoring")
    table3.add_row("projectx monitor start --all", "Enable ALL monitoring (email + mobile)")
    table3.add_row("projectx monitor stop", "Disable email monitoring")
    table3.add_row("projectx monitor stop --all", "Disable ALL monitoring (email + mobile)")
    table3.add_row("projectx monitor set-interval <min>", "Set check interval (1-1440 minutes)")
    console.print(table3)
    
    console.print("\n[dim]All commands support --json / -j flag for machine-readable output[/dim]")
    console.print()


@app.command()
def login():
    """Authenticate with your API key."""
    console.print("\n[bold]ProjectX Login[/bold]")
    console.print("Enter your API key to authenticate with the server.")
    console.print("[dim]You can find your API key in your server's environment variables (API_KEY)[/dim]\n")
    
    # Prompt for API key (hidden input like password)
    api_key = typer.prompt("API Key", hide_input=True)
    
    if not api_key or not api_key.strip():
        console.print("[red]✗[/red] API key cannot be empty")
        raise typer.Exit(code=1)
    
    # Test the API key by making a request
    client = ProjectXClient(get_server_url(), api_key.strip())
    
    try:
        with console.status("[bold blue]Verifying API key...[/bold blue]"):
            result = client.health()
        
        # Save the API key
        set_api_key(api_key.strip())
        console.print(f"[green]✓[/green] Logged in successfully!")
        console.print(f"  Server: {get_server_url()}")
        console.print()
        
    except APIError as e:
        if e.status_code in (401, 403):
            console.print(f"[red]✗[/red] Invalid API key")
        else:
            console.print(f"[red]✗[/red] Server error: {e.message}")
        raise typer.Exit(code=1)
    except ConnectionError as e:
        console.print(f"[red]✗[/red] Could not connect to server: {e.message}")
        raise typer.Exit(code=1)


@app.command()
def logout():
    """Remove saved API key."""
    if not is_logged_in():
        console.print("\n[yellow]○[/yellow] Not logged in")
        console.print()
        return
    
    set_api_key("")
    console.print("\n[green]✓[/green] Logged out successfully")
    console.print()


def get_client() -> ProjectXClient:
    """Get configured API client."""
    return ProjectXClient(get_server_url(), get_api_key())


def handle_error(e: Exception, json_output: bool = False) -> None:
    """Handle errors consistently.

    Args:
        e: Exception to handle.
        json_output: If True, output JSON format.
    
    Raises:
        typer.Exit: Always exits with code 1.
    """
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
def status(
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Check if the ProjectX server is running."""
    client = get_client()
    server_url = get_server_url()

    try:
        health = client.health()
        detailed = client.status()

        if json_output:
            result = {
                "success": True,
                "server_url": server_url,
                "health": health,
                "status": detailed,
            }
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
            result = {"success": False, "server_url": server_url, "error": str(e)}
            console.print(json.dumps(result, indent=2))
            raise typer.Exit(code=1)
        else:
            console.print(f"\n[bold]Server:[/bold] {server_url}")
            console.print(f"[red]✗[/red] Server is offline")
            console.print(f"  Error: {e}")
            console.print()
            raise typer.Exit(code=1)


@app.command()
def check(
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
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


# Context manager for optional spinner
from contextlib import nullcontext



@app.command()
def test(
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
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


# Config subcommands
@config_app.command("show")
def config_show(
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Display current configuration."""
    config = load_config()

    if json_output:
        # Don't expose API key in JSON output
        output = {"server_url": config.server_url, "logged_in": bool(config.api_key)}
        console.print(json.dumps(output, indent=2))
    else:
        console.print("\n[bold]ProjectX Configuration[/bold]")
        console.print(f"  Server URL: {config.server_url}")
        if config.api_key:
            console.print(f"  Auth: [green]✓ Logged in[/green]")
        else:
            console.print(f"  Auth: [yellow]○ Not logged in[/yellow] (run 'projectx login')")
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


# Monitor subcommands
@monitor_app.command("status")
def monitor_status(
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Show current monitoring status (email + mobile)."""
    client = get_client()

    try:
        # Try unified status first
        try:
            result = client._get("/api/monitoring/unified")
            
            if json_output:
                console.print(json.dumps(result, indent=2))
            else:
                console.print("\n[bold]Unified Monitoring Status[/bold]")
                
                # Email monitoring
                email = result.get("email_monitoring", {})
                email_enabled = email.get("enabled", False)
                email_running = email.get("running", False)
                interval = email.get("interval_minutes", 5)
                
                console.print(f"\n[bold]📧 Email Monitoring[/bold]")
                if email_enabled:
                    console.print(f"  [green]✓[/green] Enabled (every {interval} min)")
                    console.print(f"  Running: {'Yes' if email_running else 'No'}")
                else:
                    console.print(f"  [yellow]○[/yellow] Disabled")
                
                # Mobile monitoring
                mobile = result.get("mobile_monitoring", {})
                total = mobile.get("total_devices", 0)
                enabled = mobile.get("enabled_devices", 0)
                
                console.print(f"\n[bold]📱 Mobile Monitoring[/bold]")
                if total > 0:
                    if enabled == total:
                        console.print(f"  [green]✓[/green] All {total} devices enabled")
                    elif enabled > 0:
                        console.print(f"  [yellow]○[/yellow] {enabled}/{total} devices enabled")
                    else:
                        console.print(f"  [red]✗[/red] All {total} devices disabled")
                else:
                    console.print(f"  [dim]No devices connected[/dim]")
                
                console.print()
            return
        except Exception:
            pass  # Fall back to basic status
        
        # Basic status fallback
        result = client._get("/api/monitoring")

        if json_output:
            console.print(json.dumps(result, indent=2))
        else:
            enabled = result.get("enabled", False)
            running = result.get("running", False)
            interval = result.get("interval_minutes", 5)

            console.print("\n[bold]Scheduled Monitoring Status[/bold]")
            
            if enabled:
                console.print(f"[green]✓[/green] Enabled")
                console.print(f"  Interval: {interval} minutes")
                console.print(f"  Running: {'Yes' if running else 'No'}")
            else:
                console.print(f"[yellow]○[/yellow] Disabled")
                console.print(f"  Interval: {interval} minutes (when enabled)")
            
            console.print()

    except (ConnectionError, APIError) as e:
        handle_error(e, json_output)


@monitor_app.command("start")
def monitor_start(
    all_platforms: bool = typer.Option(False, "--all", "-a", help="Start monitoring on all platforms (email + mobile)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Enable scheduled email monitoring."""
    client = get_client()

    try:
        if all_platforms:
            result = client._post("/api/monitoring/start-all")
        else:
            result = client._post("/api/monitoring/start")

        if json_output:
            console.print(json.dumps(result, indent=2))
        else:
            if result.get("success"):
                console.print(f"\n[green]✓[/green] {result.get('message', 'Monitoring enabled')}")
            else:
                console.print(f"\n[red]✗[/red] {result.get('error', 'Failed to enable monitoring')}")
            console.print()

    except (ConnectionError, APIError) as e:
        handle_error(e, json_output)


@monitor_app.command("stop")
def monitor_stop(
    all_platforms: bool = typer.Option(False, "--all", "-a", help="Stop monitoring on all platforms (email + mobile)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Disable scheduled email monitoring."""
    client = get_client()

    try:
        if all_platforms:
            result = client._post("/api/monitoring/stop-all")
        else:
            result = client._post("/api/monitoring/stop")

        if json_output:
            console.print(json.dumps(result, indent=2))
        else:
            if result.get("success"):
                console.print(f"\n[green]✓[/green] {result.get('message', 'Monitoring disabled')}")
            else:
                console.print(f"\n[red]✗[/red] {result.get('error', 'Failed to disable monitoring')}")
            console.print()

    except (ConnectionError, APIError) as e:
        handle_error(e, json_output)


@monitor_app.command("set-interval")
def monitor_set_interval(
    minutes: int = typer.Argument(..., help="Check interval in minutes (1-1440)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Set the email check interval."""
    if minutes < 1 or minutes > 1440:
        if json_output:
            console.print(json.dumps({"success": False, "error": "Interval must be between 1 and 1440 minutes"}))
        else:
            console.print(f"\n[red]✗[/red] Interval must be between 1 and 1440 minutes")
            console.print()
        raise typer.Exit(code=1)

    client = get_client()

    try:
        result = client._post("/api/monitoring/interval", data={"minutes": minutes})

        if json_output:
            console.print(json.dumps(result, indent=2))
        else:
            if result.get("success"):
                console.print(f"\n[green]✓[/green] {result.get('message', f'Interval set to {minutes} minutes')}")
            else:
                console.print(f"\n[red]✗[/red] {result.get('error', 'Failed to set interval')}")
            console.print()

    except (ConnectionError, APIError) as e:
        handle_error(e, json_output)


if __name__ == "__main__":
    app()
