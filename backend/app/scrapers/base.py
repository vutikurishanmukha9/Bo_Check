"""Base scraper class with common functionality."""

import asyncio
import random
from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import datetime

import httpx
from pydantic import BaseModel

from app.config import settings


class ScrapedMovie(BaseModel):
    """Scraped movie data."""
    external_id: str
    name: str
    language: Optional[str] = None
    genres: list[str] = []
    duration_mins: Optional[int] = None
    rating: Optional[float] = None
    release_date: Optional[str] = None
    poster_url: Optional[str] = None
    synopsis: Optional[str] = None
    certification: Optional[str] = None


class ScrapedTheater(BaseModel):
    """Scraped theater data."""
    external_id: str
    name: str
    address: Optional[str] = None
    chain: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ScrapedShow(BaseModel):
    """Scraped show data."""
    external_id: str
    movie_id: str
    theater_id: str
    showtime: datetime
    format: str = "2D"
    language: Optional[str] = None
    booking_url: Optional[str] = None
    seats: list["ScrapedSeatCategory"] = []


class ScrapedSeatCategory(BaseModel):
    """Scraped seat category data."""
    name: str
    price: float
    total_seats: int = 0
    available_seats: int = 0


# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]


class BaseScraper(ABC):
    """Base class for all scrapers with common functionality."""
    
    source_name: str = "unknown"
    base_url: str = ""
    
    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
        self._request_count = 0
        self._last_request_time: Optional[datetime] = None
    
    async def __aenter__(self) -> "BaseScraper":
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers=self._get_headers(),
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
    
    def _get_headers(self) -> dict[str, str]:
        """Get request headers with rotated user agent."""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
    
    async def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        if self._last_request_time:
            elapsed = (datetime.now() - self._last_request_time).total_seconds()
            if elapsed < settings.scrape_delay:
                await asyncio.sleep(settings.scrape_delay - elapsed)
        self._last_request_time = datetime.now()
    
    async def _request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """Make HTTP request with rate limiting and error handling."""
        await self._rate_limit()
        
        if not self.client:
            raise RuntimeError("Scraper not initialized. Use async context manager.")
        
        # Rotate user agent occasionally
        if self._request_count % 10 == 0:
            self.client.headers["User-Agent"] = random.choice(USER_AGENTS)
        
        self._request_count += 1
        
        response = await self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    
    async def get(self, url: str, **kwargs) -> httpx.Response:
        """Make GET request."""
        return await self._request("GET", url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> httpx.Response:
        """Make POST request."""
        return await self._request("POST", url, **kwargs)
    
    @abstractmethod
    async def get_movies(self, city_code: str) -> list[ScrapedMovie]:
        """Get list of movies for a city."""
        pass
    
    @abstractmethod
    async def get_theaters(self, city_code: str) -> list[ScrapedTheater]:
        """Get list of theaters for a city."""
        pass
    
    @abstractmethod
    async def get_shows(
        self,
        city_code: str,
        movie_id: str,
        date: Optional[str] = None
    ) -> list[ScrapedShow]:
        """Get shows for a movie in a city."""
        pass
    
    @abstractmethod
    async def get_seat_availability(
        self,
        show_id: str
    ) -> list[ScrapedSeatCategory]:
        """Get seat availability for a show."""
        pass
