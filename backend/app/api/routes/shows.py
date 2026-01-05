"""Shows API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models import Show, SeatCategory
from app.schemas import ShowResponse, SeatCategoryResponse

router = APIRouter(prefix="/shows", tags=["Shows"])


@router.get("/{show_id}")
async def get_show(
    show_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get show details with seat availability."""
    result = await db.execute(
        select(Show)
        .options(
            selectinload(Show.movie),
            selectinload(Show.theater),
            selectinload(Show.seat_categories),
        )
        .where(Show.id == show_id)
    )
    show = result.scalar_one_or_none()
    
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
    
    return {
        "id": show.id,
        "showtime": show.showtime.isoformat(),
        "format": show.format,
        "language": show.language,
        "is_available": show.is_available,
        "booking_url": show.booking_url,
        "movie": {
            "id": show.movie.id,
            "name": show.movie.name,
            "poster": show.movie.poster_url,
            "duration": show.movie.duration_mins,
        },
        "theater": {
            "id": show.theater.id,
            "name": show.theater.name,
            "address": show.theater.address,
        },
        "seat_categories": [
            {
                "name": sc.name,
                "price": float(sc.price),
                "total_seats": sc.total_seats,
                "available_seats": sc.available_seats,
                "occupancy_percent": sc.occupancy_percent,
            }
            for sc in show.seat_categories
        ],
    }


@router.get("/{show_id}/seats")
async def get_show_seats(
    show_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed seat availability for a show."""
    result = await db.execute(
        select(SeatCategory).where(SeatCategory.show_id == show_id)
    )
    categories = result.scalars().all()
    
    if not categories:
        raise HTTPException(status_code=404, detail="Show not found or no seat data")
    
    total_available = sum(c.available_seats for c in categories)
    total_seats = sum(c.total_seats for c in categories)
    
    return {
        "show_id": show_id,
        "total_seats": total_seats,
        "available_seats": total_available,
        "overall_occupancy": ((total_seats - total_available) / total_seats * 100) if total_seats > 0 else 0,
        "categories": [
            {
                "name": c.name,
                "price": float(c.price),
                "total": c.total_seats,
                "available": c.available_seats,
                "booked": c.total_seats - c.available_seats,
                "occupancy": c.occupancy_percent,
            }
            for c in categories
        ],
    }
