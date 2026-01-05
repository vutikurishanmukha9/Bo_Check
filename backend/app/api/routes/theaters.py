"""Theaters API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models import Theater, City, Show
from app.schemas import TheaterResponse

router = APIRouter(prefix="/theaters", tags=["Theaters"])


@router.get("", response_model=list[TheaterResponse])
async def get_theaters(
    city: str = Query(..., description="City code"),
    chain: Optional[str] = Query(None, description="Filter by chain (PVR, INOX, etc.)"),
    db: AsyncSession = Depends(get_db),
) -> list[TheaterResponse]:
    """
    Get list of theaters in a city.
    
    - **city**: City code (MUM, DEL, BLR, etc.)
    - **chain**: Optional filter by theater chain
    """
    query = (
        select(Theater)
        .join(City)
        .where(City.code == city.upper())
    )
    
    if chain:
        query = query.where(Theater.chain.ilike(f"%{chain}%"))
    
    result = await db.execute(query)
    theaters = result.scalars().all()
    
    return [TheaterResponse.model_validate(t) for t in theaters]


@router.get("/{theater_id}")
async def get_theater(
    theater_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get theater details by ID."""
    result = await db.execute(
        select(Theater)
        .options(selectinload(Theater.city))
        .where(Theater.id == theater_id)
    )
    theater = result.scalar_one_or_none()
    
    if not theater:
        raise HTTPException(status_code=404, detail="Theater not found")
    
    return {
        "id": theater.id,
        "name": theater.name,
        "address": theater.address,
        "chain": theater.chain,
        "city": {
            "name": theater.city.name,
            "code": theater.city.code,
        },
        "amenities": theater.amenities or [],
        "location": {
            "lat": theater.latitude,
            "lng": theater.longitude,
        } if theater.latitude else None,
    }


@router.get("/{theater_id}/shows")
async def get_theater_shows(
    theater_id: int,
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
):
    """Get all shows at a theater."""
    # Verify theater exists
    theater_result = await db.execute(
        select(Theater).where(Theater.id == theater_id)
    )
    theater = theater_result.scalar_one_or_none()
    
    if not theater:
        raise HTTPException(status_code=404, detail="Theater not found")
    
    # Get shows
    query = (
        select(Show)
        .options(selectinload(Show.movie), selectinload(Show.seat_categories))
        .where(Show.theater_id == theater_id)
        .where(Show.is_available == True)
    )
    
    if date:
        from datetime import datetime
        from sqlalchemy import func
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        query = query.where(func.date(Show.showtime) == target_date)
    
    query = query.order_by(Show.showtime)
    
    result = await db.execute(query)
    shows = result.scalars().all()
    
    # Group by movie
    movies_dict = {}
    for show in shows:
        movie_id = show.movie_id
        if movie_id not in movies_dict:
            movies_dict[movie_id] = {
                "movie": {
                    "id": show.movie.id,
                    "name": show.movie.name,
                    "language": show.movie.language,
                    "duration": show.movie.duration_mins,
                    "rating": show.movie.rating,
                    "poster": show.movie.poster_url,
                },
                "shows": []
            }
        movies_dict[movie_id]["shows"].append({
            "id": show.id,
            "showtime": show.showtime.isoformat(),
            "format": show.format,
            "seats": [
                {
                    "category": sc.name,
                    "price": float(sc.price),
                    "available": sc.available_seats,
                }
                for sc in show.seat_categories
            ],
        })
    
    return {
        "theater": TheaterResponse.model_validate(theater),
        "date": date or "today",
        "movies": list(movies_dict.values()),
    }
