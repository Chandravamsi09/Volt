"""
Volt Command Line Interface (Typer & Rich)
"""

import json
from typing import Optional
from rich import print as rprint
from rich.console import Console
from rich.table import Table
import typer
from sdk.python.volt_sdk.client import VoltClient

app = typer.Typer(
    name="volt",
    help="⚡ Volt Enterprise AI/ML & Data Platform CLI",
    add_completion=False,
)
console = Console()


@app.command()
def health(
    url: str = typer.Option("http://localhost:8000", help="Volt API base URL"),
):
    """Check the health status of Volt Platform services."""
    client = VoltClient(base_url=url)
    try:
        data = client.health()
        table = Table(title="⚡ Volt Platform Status")
        table.add_column("Component", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Status", data.get("status", "unknown"))
        table.add_row("Version", data.get("version", "unknown"))
        table.add_row("Environment", data.get("environment", "unknown"))
        table.add_row("Database", data.get("database", "unknown"))
        table.add_row("Redis", data.get("redis", "unknown"))
        console.print(table)
    except Exception as exc:
        rprint(f"[bold red]Failed to connect to Volt API:[/bold red] {exc}")


@app.command()
def tables(
    url: str = typer.Option("http://localhost:8000", help="Volt API base URL"),
):
    """List all lakehouse tables."""
    client = VoltClient(base_url=url)
    try:
        items = client.list_tables()
        table = Table(title="📊 Lakehouse Tables")
        table.add_column("Table Name", style="cyan")
        table.add_column("Current Version", style="magenta")
        table.add_column("Total Rows", style="green")

        for item in items:
            table.add_row(
                item.get("table_name", ""),
                str(item.get("current_version", 0)),
                str(item.get("total_rows", 0)),
            )
        console.print(table)
    except Exception as exc:
        rprint(f"[bold red]Error listing tables:[/bold red] {exc}")


@app.command()
def query(
    sql: str = typer.Argument(..., help="SQL query to execute"),
    url: str = typer.Option("http://localhost:8000", help="Volt API base URL"),
):
    """Execute analytical SQL query."""
    client = VoltClient(base_url=url)
    try:
        res = client.query_sql(sql)
        rprint(f"[green]Query Executed! Rows returned: {res.get('row_count')}[/green]")
        console.print(res.get("records", [])[:10])
    except Exception as exc:
        rprint(f"[bold red]Query failed:[/bold red] {exc}")


@app.command()
def rag(
    prompt: str = typer.Argument(..., help="Query to pass to RAG system"),
    url: str = typer.Option("http://localhost:8000", help="Volt API base URL"),
):
    """Query the RAG Knowledge Base."""
    client = VoltClient(base_url=url)
    try:
        res = client.query_rag(prompt)
        rprint(f"[bold cyan]Answer:[/bold cyan] {res.get('answer')}")
        rprint(f"[bold magenta]Context Sources:[/bold magenta] {len(res.get('sources', []))}")
    except Exception as exc:
        rprint(f"[bold red]RAG Query failed:[/bold red] {exc}")


if __name__ == "__main__":
    app()
