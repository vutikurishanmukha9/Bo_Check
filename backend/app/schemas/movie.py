"""Pydantic schemas for movie-related API endpoints."""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CityResponse(BaseModel):
    """City information response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    code: str
    state: str


class SeatCategoryResponse(BaseModel):
    """Seat category with pricing and availability."""
    
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    price: Decimal
    total_seats: int
    available_seats: int
    occupancy_percent: float = Field(default=0.0)


class TheaterResponse(BaseModel):
    """Theater information response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    address: Optional[str] = None
    chain: Optional[str] = None
    city_code: Optional[str] = None


class ShowResponse(BaseModel):
    """Show/screening information response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    showtime: datetime
    format: str
    language: Optional[str] = None
    is_available: bool
    booking_url: Optional[str] = None
    theater: TheaterResponse
    seat_categories: list[SeatCategoryResponse] = []


class MovieBase(BaseModel):
    """Base movie fields."""
    
    name: str
    language: Optional[str] = None
    genres: list[str] = []
    duration_mins: Optional[int] = None
    rating: Optional[float] = None
    release_date: Optional[date] = None
    certification: Optional[str] = None


class MovieResponse(MovieBase):
    """Full movie response with details."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    external_id: str
    poster_url: Optional[str] = None
    synopsis: Optional[str] = None
    source: str


class MovieListResponse(BaseModel):
    """Paginated list of movies."""
    
    movies: list[MovieResponse]
    total: int
    page: int
    per_page: int
    city: str


class MovieWithShowsResponse(MovieResponse):
    """Movie with all its shows."""
    
    shows: list[ShowResponse] = []


class TheaterWithShowsResponse(TheaterResponse):
    """Theater with all its shows."""
    
    shows: list[ShowResponse] = []


class StatsResponse(BaseModel):
    """Statistics response for analytics."""
    
    total_shows: int
    total_theaters: int
    avg_price: Decimal
    min_price: Decimal
    max_price: Decimal
    avg_occupancy: float
    price_by_category: dict[str, Decimal] = {}
    occupancy_by_time: dict[str, float] = {}


class TrendingMovieResponse(BaseModel):
    """Trending movie with stats."""
    
    movie: MovieResponse
    total_shows: int
    avg_occupancy: float
    cities_available: list[str]
