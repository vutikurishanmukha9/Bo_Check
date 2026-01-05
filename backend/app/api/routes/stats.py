"""Statistics and Analytics API endpoints."""

from typing import Optional
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models import Movie, Show, Theater, City, SeatCategory
from app.schemas import StatsResponse

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/overview")
async def get_overview_stats(
    city: str = Query(..., description="City code"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get overview statistics for a city.
    
    Returns total movies, theaters, shows, and price ranges.
    """
    # Get city
    city_result = await db.execute(
        select(City).where(City.code == city.upper())
    )
    city_obj = city_result.scalar_one_or_none()
    
    if not city_obj:
        return {
            "city": city.upper(),
            "total_movies": 0,
            "total_theaters": 0,
            "total_shows": 0,
            "message": "No data available for this city"
        }
    
    # Count theaters
    theater_count = await db.execute(
        select(func.count()).select_from(Theater).where(Theater.city_id == city_obj.id)
    )
    
    # Count shows for today
    today = datetime.now().date()
    show_count = await db.execute(
        select(func.count())
        .select_from(Show)
        .join(Theater)
        .where(Theater.city_id == city_obj.id)
        .where(func.date(Show.showtime) == today)
    )
    
    # Get price stats
    price_stats = await db.execute(
        select(
            func.min(SeatCategory.price),
            func.max(SeatCategory.price),
            func.avg(SeatCategory.price),
        )
        .select_from(SeatCategory)
        .join(Show)
        .join(Theater)
        .where(Theater.city_id == city_obj.id)
    )
    min_price, max_price, avg_price = price_stats.one()
    
    return {
        "city": city.upper(),
        "city_name": city_obj.name,
        "total_theaters": theater_count.scalar() or 0,
        "total_shows_today": show_count.scalar() or 0,
        "price_range": {
            "min": float(min_price) if min_price else 0,
            "max": float(max_price) if max_price else 0,
            "avg": round(float(avg_price), 2) if avg_price else 0,
        },
    }


@router.get("/movie/{movie_id}")
async def get_movie_stats(
    movie_id: int,
    city: Optional[str] = Query(None, description="City code for city-specific stats"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get statistics for a specific movie.
    
    Returns occupancy rates, price distribution, and availability trends.
    """
    # Base query for shows
    query = (
        select(Show, SeatCategory)
        .join(SeatCategory)
        .where(Show.movie_id == movie_id)
    )
    
    if city:
        query = query.join(Theater).join(City).where(City.code == city.upper())
    
    result = await db.execute(query)
    data = result.all()
    
    if not data:
        return {
            "movie_id": movie_id,
            "message": "No show data available"
        }
    
    # Calculate stats
    total_shows = len(set(row[0].id for row in data))
    
    # Price by category
    price_by_category = {}
    occupancy_by_category = {}
    
    for show, seat in data:
        cat_name = seat.name
        if cat_name not in price_by_category:
            price_by_category[cat_name] = []
            occupancy_by_category[cat_name] = []
        
        price_by_category[cat_name].append(float(seat.price))
        occupancy_by_category[cat_name].append(seat.occupancy_percent)
    
    # Calculate averages
    avg_prices = {
        cat: round(sum(prices) / len(prices), 2)
        for cat, prices in price_by_category.items()
    }
    
    avg_occupancy = {
        cat: round(sum(occ) / len(occ), 1)
        for cat, occ in occupancy_by_category.items()
    }
    
    # Overall stats
    all_prices = [p for prices in price_by_category.values() for p in prices]
    all_occupancy = [o for occ in occupancy_by_category.values() for o in occ]
    
    return {
        "movie_id": movie_id,
        "city": city.upper() if city else "all",
        "total_shows": total_shows,
        "price_stats": {
            "min": min(all_prices) if all_prices else 0,
            "max": max(all_prices) if all_prices else 0,
            "avg": round(sum(all_prices) / len(all_prices), 2) if all_prices else 0,
            "by_category": avg_prices,
        },
        "occupancy_stats": {
            "avg": round(sum(all_occupancy) / len(all_occupancy), 1) if all_occupancy else 0,
            "by_category": avg_occupancy,
        },
    }


@router.get("/trending")
async def get_trending_movies(
    city: str = Query(..., description="City code"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Get trending movies based on show count and occupancy.
    
    Movies with more shows and higher occupancy are ranked higher.
    """
    # Get movies with show counts
    query = (
        select(
            Movie,
            func.count(Show.id).label("show_count"),
            func.avg(SeatCategory.available_seats / SeatCategory.total_seats * 100).label("avg_availability"),
        )
        .join(Show, Movie.id == Show.movie_id)
        .join(Theater)
        .join(City)
        .join(SeatCategory, Show.id == SeatCategory.show_id)
        .where(City.code == city.upper())
        .where(Show.showtime >= datetime.now())
        .group_by(Movie.id)
        .order_by(func.count(Show.id).desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    trending = result.all()
    
    return {
        "city": city.upper(),
        "trending": [
            {
                "rank": i + 1,
                "movie": {
                    "id": movie.id,
                    "name": movie.name,
                    "language": movie.language,
                    "rating": movie.rating,
                    "poster": movie.poster_url,
                },
                "show_count": show_count,
                "avg_availability": round(100 - (avg_avail or 0), 1),  # Convert to occupancy
            }
            for i, (movie, show_count, avg_avail) in enumerate(trending)
        ],
    }


@router.get("/price-comparison")
async def get_price_comparison(
    movie_id: int,
    city: str = Query(..., description="City code"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get price comparison across theaters for a movie.
    
    Useful for finding the best deals.
    """
    query = (
        select(Theater, SeatCategory)
        .join(Show, Theater.id == Show.theater_id)
        .join(SeatCategory, Show.id == SeatCategory.show_id)
        .join(City)
        .where(Show.movie_id == movie_id)
        .where(City.code == city.upper())
        .where(Show.showtime >= datetime.now())
    )
    
    result = await db.execute(query)
    data = result.all()
    
    # Group by theater
    theater_prices = {}
    for theater, seat in data:
        if theater.id not in theater_prices:
            theater_prices[theater.id] = {
                "theater": {
                    "id": theater.id,
                    "name": theater.name,
                    "chain": theater.chain,
                },
                "prices": {},
            }
        
        cat = seat.name
        price = float(seat.price)
        if cat not in theater_prices[theater.id]["prices"]:
            theater_prices[theater.id]["prices"][cat] = []
        theater_prices[theater.id]["prices"][cat].append(price)
    
    # Calculate min price per category per theater
    comparison = []
    for tid, data in theater_prices.items():
        min_prices = {
            cat: min(prices) for cat, prices in data["prices"].items()
        }
        comparison.append({
            **data["theater"],
            "min_prices": min_prices,
            "cheapest": min(min_prices.values()) if min_prices else 0,
        })
    
    # Sort by cheapest
    comparison.sort(key=lambda x: x["cheapest"])
    
    return {
        "movie_id": movie_id,
        "city": city.upper(),
        "theaters": comparison,
    }
