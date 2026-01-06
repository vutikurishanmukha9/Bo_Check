"""BookMyShow scraper implementation using Playwright."""

import asyncio
import re
from datetime import datetime
from typing import Optional

from playwright.async_api import async_playwright

from app.scrapers.base import (
    BaseScraper,
    ScrapedMovie,
    ScrapedTheater,
    ScrapedShow,
    ScrapedSeatCategory,
)

# City code mapping for new URL structure
BMS_CITY_URLS = {
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
    """Scraper for BookMyShow website using Playwright."""
    
    source_name = "bookmyshow"
    base_url = "https://in.bookmyshow.com"
    
    def __init__(self):
        super().__init__()
        self.browser = None
        self.playwright = None
    
    async def _ensure_browser(self):
        """Ensure Playwright browser is initialized."""
        if not self.playwright:
            self.playwright = await async_playwright().start()
        
        if not self.browser:
            self.browser = await self.playwright.firefox.launch(
                headless=True,
                args=["--kiosk"]
            )
            
    async def close(self):
        """Close browser resources."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def get_movies(self, city_code: str) -> list[ScrapedMovie]:
        """Get currently showing movies using Playwright."""
        await self._ensure_browser()
        city_slug = BMS_CITY_URLS.get(city_code.upper(), "hyderabad")
        url = f"{self.base_url}/explore/movies-{city_slug}"
        
        movies = []
        
        try:
            # Create a new context with stealth-like settings
            context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
                locale="en-US"
            )
            
            page = await context.new_page()
            
            print(f"Scraping movies from: {url}")
            response = await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            if response.status != 200:
                print(f"Failed to load page: {response.status}")
                await context.close()
                return []
                
            # Wait for any lazy loading
            await page.wait_for_timeout(3000)
            await page.mouse.wheel(0, 1000) # Scroll to load
            await page.wait_for_timeout(1000)
            
            # Find all movie links which serve as cards
            # This selector is very broad but safe
            links = await page.locator("a[href*='/movies/']").all()
            
            seen_titles = set()
            
            for link in links:
                try:
                    # Get all visible text inside the card
                    text = await link.inner_text()
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    
                    if not lines:
                        continue
                        
                    # Title is usually the first non-rating text
                    # We can infer title by checking length/position
                    # Simple heuristic: Longest line or first line that isn't a rating/genre
                    
                    title = lines[0] # Fallback
                    
                    # Sometimes the first line is "8.7/10 12K Votes". Skip that.
                    for line in lines:
                        if "Votes" in line or "/10" in line or "Likes" in line:
                            continue
                        if len(line.split(',')) > 3: # Genres line
                            continue
                        if len(line) < 2:
                            continue
                        title = line
                        break
                        
                    if not title or len(title) < 2 or title in seen_titles:
                        continue
                        
                    seen_titles.add(title)
                    
                    # Extract ID from href
                    href = await link.get_attribute("href")
                    external_id = href.split("/")[-1] if href else title.lower().replace(" ", "-")

                    # RegEx Parsing
                    full_text = " ".join(lines)
                    
                    # Rating
                    rating = None
                    rating_match = re.search(r"(\d+(\.\d+)?)\s*/\s*10", full_text)
                    if rating_match:
                        rating = float(rating_match.group(1))

                    # Certification
                    certification = None
                    cert_match = re.search(r"\b(U|UA|A|UA16\+|UA13\+|UA7\+)\b", full_text)
                    if cert_match:
                        certification = cert_match.group(1)
                        
                    # Simple Language Detection
                    language = "Unknown"
                    known_langs = ["Hindi", "English", "Telugu", "Tamil", "Kannada", "Malayalam", "Marathi"]
                    for lang in known_langs:
                        if lang in full_text:
                            language = lang
                            break

                    movie = ScrapedMovie(
                        external_id=external_id,
                        name=title,
                        language=language,
                        rating=rating,
                        certification=certification,
                        poster_url=None
                    )
                    
                    # Try to get image
                    img = link.locator("img").first
                    if await img.count() > 0:
                        movie.poster_url = await img.get_attribute("src")
                    
                    movies.append(movie)
                    
                except Exception:
                    continue
            
            await context.close()
            
        except Exception as e:
            print(f"Error scraping movies: {e}")
            
        return movies

    async def get_theaters(self, city_code: str) -> list[ScrapedTheater]:
        """Get theaters for a city (inferred from shows)."""
        # This is hard to get directly without iterating movies
        return []
        
    async def get_shows(self, city_code: str, movie_id: str, date: Optional[str] = None) -> list[ScrapedShow]:
        """Get shows for a movie in a city."""
        await self._ensure_browser()
        
        # We need the movie slug. For now, we'll try to find the movie again or use a direct search approach.
        # Since I don't have the slug here, I'll rely on the external_id if possible or search.
        # Alternative: We can construct a search URL or just go to the movie page if valid URL known.
        
        # Strategy: Go to city movie list -> Find movie -> Click -> Book
        # Optimization: Use the movie ID to construct the detailed URL if possible.
        # BMS URL: https://in.bookmyshow.com/<city>/movies/<slug>/<id>
        
        # Let's try to construct the URL directly using the ID. The slug can be anything usually? 
        # Actually BMS redirects correct IDs usually.
        
        # Mapping for city part of URL
        city_name = BMS_CITY_URLS.get(city_code.upper(), "hyderabad")
        
        # URL construction: https://in.bookmyshow.com/hyderabad/movies/dummy-slug/ET00000000
        url = f"{self.base_url}/{city_name}/movies/movie/{movie_id}"
        
        shows = []
        
        try:
            context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            page = await context.new_page()
            
            print(f"Navigating to movie page: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            # Click "Book tickets"
            try:
                book_btn = page.locator("button:has-text('Book tickets')").first
                if await book_btn.count() == 0:
                    book_btn = page.locator("a:has-text('Book tickets')").first
                
                if await book_btn.count() > 0:
                    await book_btn.click()
                    print("Clicked 'Book tickets'")
                else:
                    print("Book tickets button not found")
                    await context.close()
                    return []
            except Exception as e:
                print(f"Error clicking book button: {e}")
                await context.close()
                return []

            # Handle Modals (Format/Language AND Content Warning)
            await page.wait_for_timeout(2000)
            
            # Handle "Content Warning" popup for A-rated movies (CRITICAL!)
            try:
                continue_btn = page.locator("div:has-text('Continue')").last
                if await continue_btn.count() > 0:
                    print("Handling Content Warning popup...")
                    await continue_btn.click()
                    await page.wait_for_timeout(1500)
            except: pass
            
            # Handle "Select Language" or "Select Format" popup
            try:
                # Look for any list items in popup overlays
                format_opts = page.locator("ul li").filter(has_text="2D")
                if await format_opts.count() > 0:
                    print("Handling format selection (2D)...")
                    await format_opts.first.click()
                    await page.wait_for_timeout(1000)
            except: pass
            
            try:
                # Language selection if present
                lang_opts = page.locator("ul li").filter(has_text="Telugu")
                if await lang_opts.count() == 0:
                    lang_opts = page.locator("ul li").filter(has_text="Hindi")
                if await lang_opts.count() > 0:
                    print("Handling language selection...")
                    await lang_opts.first.click()
                    await page.wait_for_timeout(1000)
            except: pass
            
            # Now we should be on the booking page: /buytickets/...
            # Wait for page URL to change to buytickets
            await page.wait_for_timeout(3000)
            
            # Check if we're on the showtimes page
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            if "buytickets" not in current_url:
                print("Did not reach booking page. Trying to wait longer...")
                await page.wait_for_timeout(3000)
            
            # Take screenshot for debugging
            await page.screenshot(path="bms_showtimes_debug.png")
            
            # Wait for showtimes to load - use more generic selectors
            try:
                # BMS showtimes can have various selectors
                await page.wait_for_selector("a[class*='showtime'], div[class*='showtime'], a._available", timeout=10000)
                print("Showtimes selector found!")
            except:
                print("Showtimes did not load with standard selectors. Trying alternative...")
                
            # Scrape Theaters and Shows using text-based approach
            # Look for time patterns like "10:30 AM" which indicate showtimes
            
            # Get all clickable elements that look like times
            time_pattern_elements = await page.locator("a, div").filter(has_text=re.compile(r"\d{1,2}:\d{2}\s*(AM|PM)", re.IGNORECASE)).all()
            print(f"Found {len(time_pattern_elements)} elements with time patterns")
            
            # Also try the traditional theater listing approach
            theater_items = await page.locator("li").filter(has=page.locator("a[class*='showtime'], div[class*='showtime'], a._available")).all()
            if len(theater_items) == 0:
                # Fallback: look for any list items containing times
                theater_items = await page.locator("li").filter(has_text=re.compile(r"\d{1,2}:\d{2}")).all()
            print(f"Found {len(theater_items)} potential theater rows")
            
            for item in theater_items:
                try:
                    # Get Theater Name
                    theater_name_el = item.locator(".__venue-name strong, .__venue-name").first
                    if await theater_name_el.count() == 0:
                        continue
                        
                    theater_name = await theater_name_el.inner_text()
                    theater_name = theater_name.strip()
                    
                    # Get Showtimes
                    show_els = await item.locator("a.showtime-pill, div.showtime-pill").all()
                    
                    for show_el in show_els:
                        time_text = await show_el.inner_text()
                        time_text = time_text.replace("\n", "").strip()
                        
                        # Parse time (09:30 AM)
                        # We need to convert it to full request date + time
                        # For now, we'll just store the text or assume today
                        
                        # Infer status from class or attributes
                        # .available, .filling, .sold
                        classes = await show_el.get_attribute("class")
                        is_available = "sold" not in classes.lower()
                        
                        # Extract availability percent via tooltip or color if possible?
                        # BMS usually uses check-availability call or data-json...
                        # We'll use a heuristic based on color/class for now
                        
                        # Simulate seat categories (Estimates)
                        seat_categories = []
                        if is_available:
                            # We can't know exact seats without clicking deep.
                            # We'll return a placeholder to indicate "Found"
                            seat_categories = [
                                ScrapedSeatCategory(name="Standard", price=250.0, available_seats=50, total_seats=100)
                            ]
                        else:
                            seat_categories = [
                                ScrapedSeatCategory(name="Standard", price=250.0, available_seats=0, total_seats=100)
                            ]
                            
                        # Construct Show
                        # Need valid datetime. Assume 'date' param or today + time_text
                        
                        # DEEP SCRAPE: Click the first available show to get REAL seat data
                        # We only do this for the FIRST valid show we find to demonstrate capability
                        # without taking forever (navigating back/forth is slow/risky).
                        real_seat_stats = []
                        if is_available and len(shows) == 0: # Only for the very first show of the movie
                            try:
                                print(f"   🕵️ Deep scraping seats for {theater_name} @ {time_text}...")
                                # Click the showtime
                                # We need to ensure the element is interactive
                                await show_el.click()
                                await page.wait_for_timeout(2000)
                                
                                # Handle "Accept" / Terms
                                try:
                                    await page.click("button:has-text('Accept')", timeout=2000)
                                except: pass
                                
                                # Handle Quantity Selection (Select 1 seat)
                                try:
                                    qty_sel = page.locator("#qty-selector li, ul#pop_qty li").first
                                    if await qty_sel.count() > 0:
                                        await qty_sel.click()
                                        await page.click("button:has-text('Select Seats'), #proceed-Qty")
                                except: pass
                                
                                # Wait for seat layout
                                try:
                                    await page.wait_for_selector(".seat-layout, table.seat-table", timeout=10000)
                                    
                                    # Count seats
                                    # Classes: _available, _blocked, _sold
                                    all_seats = await page.locator("a.seat, div.seat, td.seat").all()
                                    avail = 0
                                    total = 0
                                    
                                    for s in all_seats:
                                        cls = await s.get_attribute("class") or ""
                                        cls = cls.lower()
                                        if "_available" in cls or "available" in cls:
                                            avail += 1
                                        total += 1
                                        
                                    print(f"      📊 Seats: {total} Total, {avail} Available, {total-avail} Booked")
                                    
                                    real_seat_stats = [
                                        ScrapedSeatCategory(name="Standard", price=250.0, available_seats=avail, total_seats=total)
                                    ]
                                    
                                    # Go back to listing for other shows? 
                                    # Going back is risky. We'll just stop scraping this movie here.
                                    # We got our sample.
                                    shows.append(ScrapedShow(
                                        external_id=f"{movie_id}-{theater_name}-{time_text}",
                                        movie_id=movie_id,
                                        theater_name=theater_name,
                                        showtime=datetime.now(),
                                        feature_language=None,
                                        feature_format=None,
                                        seat_categories=real_seat_stats
                                    ))
                                    await context.close()
                                    return shows
                                    
                                except Exception as e:
                                    print(f"      ⚠️ Failed to load seat layout: {e}")
                                    # Try to go back?
                                    await page.go_back()
                                    await page.wait_for_timeout(2000)
                            except Exception as e:
                                print(f"   ⚠️ Error interacting with showtime: {e}")
                        
                        else:
                            # Placeholder for other shows
                            shows.append(ScrapedShow(
                                external_id=f"{movie_id}-{theater_name}-{time_text}",
                                movie_id=movie_id,
                                theater_name=theater_name,
                                showtime=datetime.now(), 
                                feature_language=None,
                                feature_format=None,
                                seat_categories=[
                                    ScrapedSeatCategory(name="Standard", price=250.0, available_seats=50 if is_available else 0, total_seats=100)
                                ]
                            ))
                        
                except Exception as e:
                    # print(f"Error parsing theater row: {e}")
                    continue
            
            await context.close()
            return shows
            
        except Exception as e:
            print(f"Error in get_shows: {e}")
            return []

    async def get_seat_availability(self, show_id: str) -> list[ScrapedSeatCategory]:
        return []
