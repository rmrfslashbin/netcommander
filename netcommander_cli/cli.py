#!/usr/bin/env python3
"""
NetCommander CLI - Command-line interface for Synaccess netCommander PDUs.

Usage examples:
    netcommander status
    netcommander outlet 1 on
    netcommander outlet 1 off
    netcommander all on
    netcommander all off
    netcommander status --output json
"""

import asyncio
import sys
import os
import json
import yaml
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich import box

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from netcommander import NetCommanderClient
from netcommander.exceptions import NetCommanderError

console = Console()


def load_config() -> dict:
    """Load configuration from environment or .env file."""
    from dotenv import load_dotenv
    load_dotenv()

    return {
        "host": os.getenv("NETCOMMANDER_HOST"),
        "username": os.getenv("NETCOMMANDER_USER", "admin"),
        "password": os.getenv("NETCOMMANDER_PASSWORD", "admin"),
    }


@click.group()
@click.option("--host", envvar="NETCOMMANDER_HOST", help="Device IP address")
@click.option("--username", "-u", envvar="NETCOMMANDER_USER", default="admin", help="Username")
@click.option("--password", "-p", envvar="NETCOMMANDER_PASSWORD", help="Password")
@click.pass_context
def cli(ctx, host, username, password):
    """NetCommander CLI - Control Synaccess netCommander PDUs."""
    ctx.ensure_object(dict)

    if not host:
        console.print("[red]Error: Host not specified. Use --host or set NETCOMMANDER_HOST[/red]")
        sys.exit(1)

    if not password:
        console.print("[yellow]Warning: Using default password 'admin'[/yellow]")
        password = "admin"

    ctx.obj["host"] = host
    ctx.obj["username"] = username
    ctx.obj["password"] = password


@cli.command()
@click.option("--output", "-o", type=click.Choice(["table", "json", "yaml"]), default="table", help="Output format")
@click.pass_context
def status(ctx, output):
    """Show status of all outlets."""
    async def _status():
        async with NetCommanderClient(
            ctx.obj["host"],
            ctx.obj["username"],
            ctx.obj["password"]
        ) as client:
            try:
                device_status = await client.get_status()

                if output == "json":
                    data = {
                        "outlets": {k: v for k, v in device_status.outlets.items()},
                        "total_current_amps": device_status.total_current_amps,
                        "temperature": device_status.temperature,
                    }
                    console.print_json(json.dumps(data, indent=2))

                elif output == "yaml":
                    data = {
                        "outlets": {k: v for k, v in device_status.outlets.items()},
                        "total_current_amps": device_status.total_current_amps,
                        "temperature": device_status.temperature,
                    }
                    print(yaml.dump(data, default_flow_style=False))

                else:  # table
                    table = Table(title="NetCommander Status", box=box.ROUNDED)
                    table.add_column("Outlet", justify="center", style="cyan")
                    table.add_column("State", justify="center")

                    for outlet_num in range(1, 6):
                        state = device_status.outlets[outlet_num]
                        state_str = "[green]ON[/green]" if state else "[red]OFF[/red]"
                        table.add_row(str(outlet_num), state_str)

                    console.print(table)
                    console.print(f"\n[bold]Total Current:[/bold] {device_status.total_current_amps}A")
                    console.print(f"[bold]Temperature:[/bold] {device_status.temperature}")

            except NetCommanderError as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)

    asyncio.run(_status())


@cli.command()
@click.argument("outlet_number", type=click.IntRange(1, 5))
@click.argument("action", type=click.Choice(["on", "off", "toggle"]))
@click.pass_context
def outlet(ctx, outlet_number, action):
    """Control a specific outlet.

    \b
    Examples:
        netcommander outlet 1 on
        netcommander outlet 5 off
        netcommander outlet 3 toggle
    """
    async def _outlet():
        async with NetCommanderClient(
            ctx.obj["host"],
            ctx.obj["username"],
            ctx.obj["password"]
        ) as client:
            try:
                if action == "on":
                    await client.turn_on(outlet_number)
                    console.print(f"[green]✓[/green] Outlet {outlet_number} turned ON")
                elif action == "off":
                    await client.turn_off(outlet_number)
                    console.print(f"[green]✓[/green] Outlet {outlet_number} turned OFF")
                elif action == "toggle":
                    await client.toggle_outlet(outlet_number)
                    console.print(f"[green]✓[/green] Outlet {outlet_number} toggled")

            except NetCommanderError as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)

    asyncio.run(_outlet())


@cli.command()
@click.argument("action", type=click.Choice(["on", "off"]))
@click.pass_context
def all(ctx, action):
    """Turn all outlets on or off.

    \b
    Examples:
        netcommander all on
        netcommander all off
    """
    async def _all():
        async with NetCommanderClient(
            ctx.obj["host"],
            ctx.obj["username"],
            ctx.obj["password"]
        ) as client:
            try:
                if action == "on":
                    results = await client.turn_on_all()
                    console.print("[green]✓[/green] All outlets turned ON")
                elif action == "off":
                    results = await client.turn_off_all()
                    console.print("[green]✓[/green] All outlets turned OFF")

                # Show any failures
                failures = [num for num, success in results.items() if not success]
                if failures:
                    console.print(f"[yellow]⚠ Failed outlets: {failures}[/yellow]")

            except NetCommanderError as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)

    asyncio.run(_all())


@cli.command()
@click.option("--interval", "-i", default=2, help="Update interval in seconds")
@click.pass_context
def monitor(ctx, interval):
    """Monitor outlet status in real-time.

    Press Ctrl+C to stop.
    """
    async def _monitor():
        from rich.live import Live

        async with NetCommanderClient(
            ctx.obj["host"],
            ctx.obj["username"],
            ctx.obj["password"]
        ) as client:
            try:
                with Live(console=console, refresh_per_second=1) as live:
                    while True:
                        device_status = await client.get_status()

                        table = Table(title="NetCommander Monitor", box=box.ROUNDED)
                        table.add_column("Outlet", justify="center", style="cyan")
                        table.add_column("State", justify="center")

                        for outlet_num in range(1, 6):
                            state = device_status.outlets[outlet_num]
                            state_str = "[green]●  ON[/green]" if state else "[red]●  OFF[/red]"
                            table.add_row(str(outlet_num), state_str)

                        table.add_row("", "")
                        table.add_row(
                            "[bold]Current[/bold]",
                            f"{device_status.total_current_amps}A"
                        )
                        table.add_row(
                            "[bold]Temp[/bold]",
                            device_status.temperature or "N/A"
                        )

                        live.update(table)
                        await asyncio.sleep(interval)

            except KeyboardInterrupt:
                console.print("\n[yellow]Monitoring stopped[/yellow]")
            except NetCommanderError as e:
                console.print(f"\n[red]Error: {e}[/red]")
                sys.exit(1)

    asyncio.run(_monitor())


@cli.command()
@click.pass_context
def info(ctx):
    """Show device and connection information."""
    async def _info():
        config = load_config()

        # Connection info
        conn_table = Table(title="Connection", box=box.ROUNDED)
        conn_table.add_column("Setting", style="cyan")
        conn_table.add_column("Value")

        conn_table.add_row("Host", ctx.obj.get("host") or config.get("host") or "[red]Not set[/red]")
        conn_table.add_row("Username", ctx.obj.get("username") or config.get("username") or "admin")
        conn_table.add_row("Password", "***" if ctx.obj.get("password") or config.get("password") else "[red]Not set[/red]")

        console.print(conn_table)

        # Try to get device info
        try:
            async with NetCommanderClient(
                ctx.obj["host"],
                ctx.obj["username"],
                ctx.obj["password"]
            ) as client:
                # Get device info
                device_info = await client.get_device_info()

                # Device info table
                dev_table = Table(title="Device Information", box=box.ROUNDED)
                dev_table.add_column("Property", style="cyan")
                dev_table.add_column("Value")

                dev_table.add_row("Model", device_info.model)
                if device_info.hardware_version:
                    dev_table.add_row("Hardware Version", device_info.hardware_version)
                if device_info.firmware_version:
                    dev_table.add_row("Firmware Version", device_info.firmware_version)
                if device_info.bootloader_version:
                    dev_table.add_row("Bootloader", device_info.bootloader_version)
                if device_info.mac_address:
                    dev_table.add_row("MAC Address", device_info.mac_address)

                console.print("\n")
                console.print(dev_table)

                # Get current status for summary
                status = await client.get_status()

                # Status summary
                summary_table = Table(title="Current Status", box=box.ROUNDED)
                summary_table.add_column("Metric", style="cyan")
                summary_table.add_column("Value")

                outlets_on = len(status.outlets_on)
                summary_table.add_row("Outlets ON", f"{outlets_on}/5")
                summary_table.add_row("Total Current", f"{status.total_current_amps}A")
                if status.temperature and status.temperature != "XX":
                    summary_table.add_row("Temperature", f"{status.temperature}°C")

                console.print("\n")
                console.print(summary_table)

        except NetCommanderError as e:
            console.print(f"\n[yellow]⚠ Could not get device info: {e}[/yellow]")

    asyncio.run(_info())


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
