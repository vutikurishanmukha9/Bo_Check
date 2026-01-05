"""Movies API endpoints."""

from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models import Movie, Show, Theater, City
from app.schemas import MovieResponse, MovieListResponse, MovieWithShowsResponse
from app.scrapers import BookMyShowScraper

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("", response_model=MovieListResponse)
async def get_movies(
    city: str = Query(..., description="City code (e.g., MUM, DEL)"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    language: Optional[str] = Query(None, description="Filter by language"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    db: AsyncSession = Depends(get_db),
) -> MovieListResponse:
    """
    Get list of currently showing movies in a city.
    
    - **city**: City code (MUM, DEL, BLR, HYD, CHE, KOL, PUN, AHM)
    - **page**: Page number for pagination
    - **per_page**: Number of movies per page (max 50)
    - **language**: Optional language filter
    - **genre**: Optional genre filter
    """
    # Build query
    query = select(Movie)
    
    if language:
        query = query.where(Movie.language.ilike(f"%{language}%"))
    
    # Get total count
    count_query = select(func.count()).select_from(Movie)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated results
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    movies = result.scalars().all()
    
    # If no movies in database, try scraping
    if not movies:
        movies = await _scrape_movies(city.upper())
    
    return MovieListResponse(
        movies=[MovieResponse.model_validate(m) if hasattr(m, '__table__') else MovieResponse(**m.model_dump()) for m in movies],
        total=total if total > 0 else len(movies),
        page=page,
        per_page=per_page,
        city=city.upper(),
    )


async def _scrape_movies(city_code: str) -> list:
    """Scrape movies from BookMyShow."""
    try:
        async with BookMyShowScraper() as scraper:
            scraped = await scraper.get_movies(city_code)
            return scraped
    except Exception as e:
        # Log error
        return []


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
) -> MovieResponse:
    """Get movie details by ID."""
    result = await db.execute(
        select(Movie).where(Movie.id == movie_id)
    )
    movie = result.scalar_one_or_none()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    return MovieResponse.model_validate(movie)


@router.get("/{movie_id}/shows")
async def get_movie_shows(
    movie_id: int,
    city: str = Query(..., description="City code"),
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all shows for a movie in a city.
    
    Returns show timings grouped by theater with seat availability.
    """
    # Get movie
    movie_result = await db.execute(
        select(Movie).where(Movie.id == movie_id)
    )
    movie = movie_result.scalar_one_or_none()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Get shows with theater info
    query = (
        select(Show)
        .options(selectinload(Show.theater), selectinload(Show.seat_categories))
        .join(Theater)
        .join(City)
        .where(Show.movie_id == movie_id)
        .where(City.code == city.upper())
    )
    
    if date:
        from datetime import datetime
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        query = query.where(func.date(Show.showtime) == target_date)
    
    result = await db.execute(query)
    shows = result.scalars().all()
    
    # Group by theater
    theaters_dict = {}
    for show in shows:
        theater_id = show.theater_id
        if theater_id not in theaters_dict:
            theaters_dict[theater_id] = {
                "theater": {
                    "id": show.theater.id,
                    "name": show.theater.name,
                    "address": show.theater.address,
                    "chain": show.theater.chain,
                },
                "shows": []
            }
        theaters_dict[theater_id]["shows"].append({
            "id": show.id,
            "showtime": show.showtime.isoformat(),
            "format": show.format,
            "language": show.language,
            "is_available": show.is_available,
            "seat_categories": [
                {
                    "name": sc.name,
                    "price": float(sc.price),
                    "available": sc.available_seats,
                    "total": sc.total_seats,
                }
                for sc in show.seat_categories
            ],
        })
    
    return {
        "movie": MovieResponse.model_validate(movie),
        "city": city.upper(),
        "date": date or "today",
        "theaters": list(theaters_dict.values()),
    }


@router.get("/search/{query}")
async def search_movies(
    query: str,
    city: str = Query(..., description="City code"),
    db: AsyncSession = Depends(get_db),
):
    """Search movies by name."""
    result = await db.execute(
        select(Movie).where(Movie.name.ilike(f"%{query}%")).limit(10)
    )
    movies = result.scalars().all()
    
    return [MovieResponse.model_validate(m) for m in movies]
