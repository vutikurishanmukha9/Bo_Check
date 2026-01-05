"""Bo_Check CLI - Beautiful command-line interface for movie stats."""

import asyncio
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from app.scrapers import BookMyShowScraper

# Create CLI app
app = typer.Typer(
    name="bo-check",
    help="🎬 Movie Booking Statistics for India",
    add_completion=False,
)

console = Console()

# Supported cities
CITIES = {
    "MUM": "Mumbai",
    "DEL": "Delhi NCR",
    "BLR": "Bangalore",
    "HYD": "Hyderabad",
    "CHE": "Chennai",
    "KOL": "Kolkata",
    "PUN": "Pune",
    "AHM": "Ahmedabad",
}


@app.command()
def cities():
    """List all supported cities."""
    table = Table(title="🏙️ Supported Metropolitan Cities")
    table.add_column("Code", style="cyan", justify="center")
    table.add_column("City", style="green")
    
    for code, name in CITIES.items():
        table.add_row(code, name)
    
    console.print(table)


@app.command()
def movies(
    city: str = typer.Option(..., "--city", "-c", help="City code (e.g., MUM, DEL)"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of movies to show"),
):
    """
    Get currently showing movies in a city.
    
    Example: bo-check movies --city MUM
    """
    city_upper = city.upper()
    if city_upper not in CITIES:
        console.print(f"[red]Error: Unknown city code '{city}'. Use 'bo-check cities' to see available cities.[/red]")
        raise typer.Exit(1)
    
    console.print(f"\n🎬 [bold]Movies in {CITIES[city_upper]}[/bold]\n")
    
    async def fetch_movies():
        async with BookMyShowScraper() as scraper:
            return await scraper.get_movies(city_upper)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Fetching movies...", total=None)
        movies_list = asyncio.run(fetch_movies())
    
    if not movies_list:
        console.print("[yellow]No movies found. This could be a scraping issue.[/yellow]")
        return
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4)
    table.add_column("Movie", style="cyan", no_wrap=True)
    table.add_column("Language", style="green")
    table.add_column("Genre", style="yellow")
    table.add_column("Rating", justify="center")
    
    for i, movie in enumerate(movies_list[:limit], 1):
        rating = f"⭐ {movie.rating}" if movie.rating else "-"
        genres = ", ".join(movie.genres[:2]) if movie.genres else "-"
        table.add_row(
            str(i),
            movie.name[:40],
            movie.language or "-",
            genres,
            rating,
        )
    
    console.print(table)
    console.print(f"\n[dim]Showing {min(limit, len(movies_list))} of {len(movies_list)} movies[/dim]")


@app.command()
def shows(
    movie: str = typer.Argument(..., help="Movie name to search"),
    city: str = typer.Option(..., "--city", "-c", help="City code"),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)"),
):
    """
    Get show timings for a movie.
    
    Example: bo-check shows "Pushpa 2" --city DEL
    """
    city_upper = city.upper()
    if city_upper not in CITIES:
        console.print(f"[red]Error: Unknown city code '{city}'[/red]")
        raise typer.Exit(1)
    
    console.print(f"\n🎬 [bold]Shows for '{movie}' in {CITIES[city_upper]}[/bold]")
    if date:
        console.print(f"📅 Date: {date}")
    console.print()
    
    async def fetch_shows():
        async with BookMyShowScraper() as scraper:
            # First get movies to find the ID
            movies_list = await scraper.get_movies(city_upper)
            
            # Find matching movie
            matching = [m for m in movies_list if movie.lower() in m.name.lower()]
            if not matching:
                return None, []
            
            target_movie = matching[0]
            shows = await scraper.get_shows(city_upper, target_movie.external_id, date)
            return target_movie, shows
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Fetching show timings...", total=None)
        target_movie, shows_list = asyncio.run(fetch_shows())
    
    if not target_movie:
        console.print(f"[red]Movie '{movie}' not found in {CITIES[city_upper]}[/red]")
        return
    
    if not shows_list:
        console.print("[yellow]No shows found for this movie.[/yellow]")
        return
    
    # Group by theater
    from collections import defaultdict
    theaters = defaultdict(list)
    for show in shows_list:
        theaters[show.theater_id].append(show)
    
    console.print(Panel(f"[bold cyan]{target_movie.name}[/bold cyan]", subtitle=target_movie.language or ""))
    
    for theater_id, theater_shows in theaters.items():
        show_times = " | ".join([
            f"[green]{s.showtime.strftime('%H:%M')}[/green] ({s.format})"
            for s in sorted(theater_shows, key=lambda x: x.showtime)
        ])
        console.print(f"\n🎭 [bold]{theater_id}[/bold]")
        console.print(f"   {show_times}")


@app.command()
def prices(
    movie: str = typer.Argument(..., help="Movie name"),
    city: str = typer.Option(..., "--city", "-c", help="City code"),
):
    """
    Compare ticket prices across theaters.
    
    Example: bo-check prices "Pushpa 2" --city MUM
    """
    console.print(f"\n💰 [bold]Price Comparison for '{movie}' in {CITIES.get(city.upper(), city)}[/bold]\n")
    
    # TODO: Implement price comparison
    console.print("[yellow]Price comparison feature coming soon![/yellow]")
    console.print("[dim]This will show ticket prices across different theaters.[/dim]")


@app.command()
def export(
    data_type: str = typer.Argument(..., help="Type of data (movies, shows, theaters)"),
    city: str = typer.Option(..., "--city", "-c", help="City code"),
    format: str = typer.Option("json", "--format", "-f", help="Output format (json, csv)"),
    output: str = typer.Option("output", "--output", "-o", help="Output filename"),
):
    """
    Export data to JSON or CSV file.
    
    Example: bo-check export movies --city MUM --format csv -o mumbai_movies.csv
    """
    import json
    import csv
    
    console.print(f"\n📁 Exporting {data_type} for {CITIES.get(city.upper(), city)}...\n")
    
    async def fetch_data():
        async with BookMyShowScraper() as scraper:
            if data_type == "movies":
                return await scraper.get_movies(city.upper())
            elif data_type == "theaters":
                return await scraper.get_theaters(city.upper())
            else:
                console.print(f"[red]Unknown data type: {data_type}[/red]")
                return []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(f"Fetching {data_type}...", total=None)
        data = asyncio.run(fetch_data())
    
    if not data:
        console.print("[yellow]No data to export.[/yellow]")
        return
    
    # Ensure correct extension
    if not output.endswith(f".{format}"):
        output = f"{output}.{format}"
    
    if format == "json":
        with open(output, "w", encoding="utf-8") as f:
            json.dump([d.model_dump() for d in data], f, indent=2, default=str)
    elif format == "csv":
        if data:
            keys = list(data[0].model_dump().keys())
            with open(output, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for item in data:
                    writer.writerow(item.model_dump())
    
    console.print(f"[green]✓ Exported {len(data)} items to {output}[/green]")


@app.command()
def version():
    """Show version information."""
    console.print(Panel.fit(
        "[bold cyan]Bo_Check[/bold cyan] v0.1.0\n"
        "[dim]Movie Booking Statistics for India[/dim]\n\n"
        "📦 Built with FastAPI + Next.js\n"
        "🔧 CLI powered by Typer + Rich",
        title="🎬 About",
    ))


if __name__ == "__main__":
    app()
