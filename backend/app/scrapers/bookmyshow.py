"""BookMyShow scraper implementation."""

import re
from datetime import datetime, date
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.scrapers.base import (
    BaseScraper,
    ScrapedMovie,
    ScrapedTheater,
    ScrapedShow,
    ScrapedSeatCategory,
)


# City code mapping for BookMyShow
BMS_CITY_CODES = {
    "MUM": "mumbai",
    "DEL": "delhi-ncr", 
    "BLR": "bengaluru",
    "HYD": "hyderabad",
    "CHE": "chennai",
    "KOL": "kolkata",
    "PUN": "pune",
    "AHM": "ahmedabad",
}


class BookMyShowScraper(BaseScraper):
    """Scraper for BookMyShow website."""
    
    source_name = "bookmyshow"
    base_url = "https://in.bookmyshow.com"
    explore_url = "https://in.bookmyshow.com/explore/home"  # e.g., /explore/home/hyderabad
    api_url = "https://in.bookmyshow.com/api"
    
    def _get_city_url(self, city_code: str) -> str:
        """Get BMS city identifier from our city code."""
        return BMS_CITY_CODES.get(city_code.upper(), city_code.lower())
    
    def _get_headers(self) -> dict[str, str]:
        """Get headers specific to BookMyShow."""
        headers = super()._get_headers()
        headers.update({
            "Referer": self.base_url,
            "Origin": self.base_url,
        })
        return headers
    
    async def get_movies(self, city_code: str) -> list[ScrapedMovie]:
        """
        Get list of currently showing movies in a city.
        
        Uses BMS explore API to get movie listings.
        """
        city = self._get_city_url(city_code)
        movies: list[ScrapedMovie] = []
        
        # BMS API endpoint for movie listings
        url = f"{self.api_url}/explore/v1/discover/movie"
        params = {
            "region": city,
            "lang": "en",
            "page": 1,
            "size": 50,
        }
        
        try:
            response = await self.get(url, params=params)
            data = response.json()
            
            if "data" in data and "movies" in data["data"]:
                for movie_data in data["data"]["movies"]:
                    movie = self._parse_movie(movie_data)
                    if movie:
                        movies.append(movie)
        except Exception as e:
            # Fallback to HTML scraping if API fails
            movies = await self._scrape_movies_html(city)
        
        return movies
    
    async def _scrape_movies_html(self, city: str) -> list[ScrapedMovie]:
        """Fallback HTML scraping for movies."""
        movies: list[ScrapedMovie] = []
        url = f"{self.base_url}/{city}/movies"
        
        try:
            response = await self.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find movie cards
            movie_cards = soup.select("[data-movie-code]")
            
            for card in movie_cards[:30]:  # Limit to 30 movies
                try:
                    title_elem = card.select_one(".style-title")
                    movie = ScrapedMovie(
                        external_id=card.get("data-movie-code", ""),
                        name=title_elem.text.strip() if title_elem else "Unknown",
                        language=self._extract_language(card),
                        genres=self._extract_genres(card),
                        rating=self._extract_rating(card),
                        poster_url=self._extract_poster(card),
                    )
                    movies.append(movie)
                except Exception:
                    continue
        except Exception:
            pass
        
        return movies
    
    def _parse_movie(self, data: dict) -> Optional[ScrapedMovie]:
        """Parse movie data from API response."""
        try:
            # Parse duration if available
            duration = None
            if "duration" in data:
                duration_str = data["duration"]
                # Parse "2h 30m" format
                match = re.match(r"(\d+)h\s*(\d*)m?", duration_str)
                if match:
                    hours = int(match.group(1))
                    mins = int(match.group(2)) if match.group(2) else 0
                    duration = hours * 60 + mins
            
            # Parse release date
            release_date = None
            if "releaseDate" in data:
                try:
                    release_date = data["releaseDate"]
                except Exception:
                    pass
            
            return ScrapedMovie(
                external_id=data.get("code", data.get("id", "")),
                name=data.get("name", data.get("title", "Unknown")),
                language=data.get("language"),
                genres=data.get("genres", []),
                duration_mins=duration,
                rating=data.get("rating"),
                release_date=release_date,
                poster_url=data.get("posterUrl", data.get("poster")),
                synopsis=data.get("synopsis"),
                certification=data.get("certification"),
            )
        except Exception:
            return None
    
    def _extract_language(self, card) -> Optional[str]:
        """Extract language from movie card."""
        lang_elem = card.select_one(".style-language")
        return lang_elem.text.strip() if lang_elem else None
    
    def _extract_genres(self, card) -> list[str]:
        """Extract genres from movie card."""
        genre_elem = card.select_one(".style-genre")
        if genre_elem:
            return [g.strip() for g in genre_elem.text.split(",")]
        return []
    
    def _extract_rating(self, card) -> Optional[float]:
        """Extract rating from movie card."""
        rating_elem = card.select_one(".style-rating")
        if rating_elem:
            try:
                return float(rating_elem.text.strip().split("/")[0])
            except ValueError:
                pass
        return None
    
    def _extract_poster(self, card) -> Optional[str]:
        """Extract poster URL from movie card."""
        img = card.select_one("img")
        return img.get("src") or img.get("data-src") if img else None
    
    async def get_theaters(self, city_code: str) -> list[ScrapedTheater]:
        """Get list of theaters in a city."""
        city = self._get_city_url(city_code)
        theaters: list[ScrapedTheater] = []
        
        url = f"{self.api_url}/explore/v1/venues"
        params = {
            "region": city,
            "type": "MT",  # Movie Theater
        }
        
        try:
            response = await self.get(url, params=params)
            data = response.json()
            
            if "venues" in data:
                for venue in data["venues"]:
                    theater = ScrapedTheater(
                        external_id=venue.get("code", ""),
                        name=venue.get("name", "Unknown"),
                        address=venue.get("address"),
                        chain=self._extract_chain(venue.get("name", "")),
                        latitude=venue.get("lat"),
                        longitude=venue.get("lng"),
                    )
                    theaters.append(theater)
        except Exception:
            # Fallback or empty list
            pass
        
        return theaters
    
    def _extract_chain(self, theater_name: str) -> Optional[str]:
        """Extract theater chain from name."""
        chains = ["PVR", "INOX", "Cinepolis", "Carnival", "Miraj", "SPI", "Wave", "Fun"]
        for chain in chains:
            if chain.lower() in theater_name.lower():
                return chain
        return None
    
    async def get_shows(
        self,
        city_code: str,
        movie_id: str,
        date: Optional[str] = None
    ) -> list[ScrapedShow]:
        """Get shows for a movie in a city on a specific date."""
        city = self._get_city_url(city_code)
        shows: list[ScrapedShow] = []
        
        if not date:
            date = datetime.now().strftime("%Y%m%d")
        
        url = f"{self.api_url}/explore/v1/showtimes"
        params = {
            "region": city,
            "movieCode": movie_id,
            "date": date,
        }
        
        try:
            response = await self.get(url, params=params)
            data = response.json()
            
            if "venues" in data:
                for venue in data["venues"]:
                    theater_id = venue.get("code", "")
                    
                    for showtime in venue.get("showtimes", []):
                        show = ScrapedShow(
                            external_id=showtime.get("showId", ""),
                            movie_id=movie_id,
                            theater_id=theater_id,
                            showtime=self._parse_showtime(showtime.get("showTime", "")),
                            format=showtime.get("dimension", "2D"),
                            language=showtime.get("language"),
                            booking_url=showtime.get("bookingUrl"),
                            seats=self._parse_seat_categories(showtime.get("categories", [])),
                        )
                        shows.append(show)
        except Exception:
            pass
        
        return shows
    
    def _parse_showtime(self, time_str: str) -> datetime:
        """Parse showtime string to datetime."""
        try:
            # Try different formats
            for fmt in ["%Y-%m-%dT%H:%M:%S", "%H:%M", "%I:%M %p"]:
                try:
                    parsed = datetime.strptime(time_str, fmt)
                    if parsed.year == 1900:  # Only time, no date
                        today = datetime.now()
                        parsed = parsed.replace(year=today.year, month=today.month, day=today.day)
                    return parsed
                except ValueError:
                    continue
        except Exception:
            pass
        return datetime.now()
    
    def _parse_seat_categories(self, categories: list) -> list[ScrapedSeatCategory]:
        """Parse seat category data."""
        seats = []
        for cat in categories:
            try:
                seats.append(ScrapedSeatCategory(
                    name=cat.get("name", "Standard"),
                    price=float(cat.get("price", 0)),
                    total_seats=cat.get("totalSeats", 0),
                    available_seats=cat.get("availableSeats", 0),
                ))
            except Exception:
                continue
        return seats
    
    async def get_seat_availability(self, show_id: str) -> list[ScrapedSeatCategory]:
        """Get detailed seat availability for a show."""
        url = f"{self.api_url}/explore/v1/seats/{show_id}"
        
        try:
            response = await self.get(url)
            data = response.json()
            
            return self._parse_seat_categories(data.get("categories", []))
        except Exception:
            return []
