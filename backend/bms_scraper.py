"""Bo_Analytics - Unified BMS Scraper with Fast Status & Deep Seat Analysis."""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import re

# Configure logging (file + console)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ShowStatus(Enum):
    """Showtime status enumeration."""
    FAST_FILLING = "FAST FILLING"
    AVAILABLE = "AVAILABLE"
    SOLD_OUT = "SOLD OUT"
    UNKNOWN = "UNKNOWN"


@dataclass
class ShowTime:
    """Individual showtime data."""
    time: str
    status: ShowStatus
    cinema: Optional[str] = None


@dataclass 
class SeatData:
    """Seat availability data (for deep scan)."""
    showtime: str
    cinema: Optional[str]
    total_seats: int
    booked_seats: int
    available_seats: int
    occupancy_percentage: float


@dataclass
class MovieStats:
    """Movie statistics from scraping."""
    movie: str
    url: str
    city: str
    scrape_time: str
    total_shows: int
    fast_filling: int
    available: int
    sold_out: int
    unknown: int
    fast_filling_percentage: float
    occupancy_rate: float
    shows: List[Dict]
    cinemas_count: int
    seat_data: Optional[List[Dict]] = None
    total_seats_scanned: Optional[int] = None


class BMSScraper:
    """
    BookMyShow scraper with two modes:
    - quick_scan(): Fast status detection (Fast Filling, Available, Sold Out)
    - deep_scan(): Detailed seat count extraction via Konva.js canvas
    """
    
    def __init__(self, city: str = "hyderabad", headless: bool = False, 
                 timeout: int = 10, max_retries: int = 3):
        """Initialize scraper."""
        self.city = city
        self.headless = headless
        self.timeout = timeout
        self.max_retries = max_retries
        self.driver = None
        self.wait = None
        
        self.output_dir = Path("scraper_results")
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info(f"BMSScraper initialized for city: {city}")
    
    def start(self) -> bool:
        """Start browser with stealth options."""
        if self.driver:
            self.stop()
        
        try:
            options = uc.ChromeOptions()
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-notifications")
            
            if self.headless:
                options.add_argument("--headless=new")
            
            options.page_load_strategy = 'eager'
            
            self.driver = uc.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, self.timeout)
            
            logger.info("Browser started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False
    
    def stop(self):
        """Stop browser."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser stopped")
            except Exception as e:
                logger.warning(f"Error stopping browser: {e}")
        self.driver = None
        self.wait = None
    
    def _js_click(self, element) -> bool:
        """Click element using JavaScript."""
        try:
            self.driver.execute_script("arguments[0].click();", element)
            return True
        except:
            return False
    
    def _handle_popups(self):
        """Handle BMS popups."""
        selectors = [
            (By.XPATH, "//div[text()='Continue']"),
            (By.XPATH, "//button[contains(text(), 'Continue')]"),
            (By.XPATH, "//button[contains(text(), 'Got it')]"),
            (By.CSS_SELECTOR, "[aria-label='Close']"),
        ]
        
        for by, selector in selectors:
            try:
                element = self.driver.find_element(by, selector)
                self._js_click(element)
                time.sleep(0.5)
            except:
                continue
    
    def _search_movie(self, movie_name: str) -> Optional[str]:
        """
        Search for a movie on BMS and return its URL.
        
        Args:
            movie_name: Name of the movie to search for
            
        Returns:
            Movie URL if found, None otherwise
        """
        try:
            # Go directly to movies listing page for the city
            movies_url = f"https://in.bookmyshow.com/explore/movies-{self.city}"
            self.driver.get(movies_url)
            time.sleep(4)
            
            self._handle_popups()
            
            # Scroll to load more movies
            for _ in range(3):
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(0.5)
            
            # Prepare movie name for matching
            movie_slug = movie_name.lower().replace(' ', '-').replace("'", '')
            movie_words = movie_name.lower().split()
            
            # Find movie links on the page
            movie_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/movies/')]")
            
            for link in movie_links:
                href = (link.get_attribute('href') or '').lower()
                link_text = (link.text or '').lower()
                
                # Check if movie name matches
                if movie_slug in href or all(word in href for word in movie_words[:2]):
                    logger.info(f"Found movie: {href}")
                    self._js_click(link)
                    time.sleep(2)
                    return self.driver.current_url
                    
                # Also check link text
                if all(word in link_text for word in movie_words[:2]):
                    logger.info(f"Found movie by text: {link_text}")
                    self._js_click(link)
                    time.sleep(2)
                    return self.driver.current_url
            
            logger.warning(f"Movie '{movie_name}' not found on movies page")
            return None
            
        except Exception as e:
            logger.error(f"Movie search failed: {e}")
            return None
    
    def _select_language(self, preferred_language: str = "TELUGU") -> bool:
        """Select movie language by clicking the format button under it."""
        try:
            time.sleep(2)
            
            # BMS dialog structure (from XPath):
            # ul/li[1]/section[2]/div = Telugu 2D button
            # ul/li[2]/section[2]/div = Hindi 2D button
            # etc.
            
            # Map language to li index
            language_index_map = {
                "TELUGU": 1,
                "HINDI": 2,
                "TAMIL": 3,
                "KANNADA": 4,
                "MALAYALAM": 5,
                "ENGLISH": 6
            }
            
            # Get the index for preferred language (default to 1 for Telugu)
            li_index = language_index_map.get(preferred_language.upper(), 1)
            
            # Try the exact XPath for the preferred language
            xpath = f"//ul/li[{li_index}]/section[2]/div"
            try:
                button = self.driver.find_element(By.XPATH, xpath)
                self._js_click(button)
                time.sleep(2)
                logger.info(f"Selected: {preferred_language} 2D (li[{li_index}])")
                return True
            except:
                pass
            
            # Fallback: Try li[1] (first language available)
            try:
                button = self.driver.find_element(By.XPATH, "//ul/li[1]/section[2]/div")
                self._js_click(button)
                time.sleep(2)
                logger.info("Selected: First available language 2D")
                return True
            except:
                # No language dialog found - this is OK for single-language movies
                logger.debug("No language dialog - movie may have single language")
                return True  # Continue anyway
                    
        except Exception as e:
            logger.debug(f"Language selection: {e}")
        return True  # Don't block on language selection failure
    
    def _select_format(self, preferred_format: str = "2D") -> bool:
        """Select movie format (2D/3D/IMAX)."""
        try:
            time.sleep(2)
            options = self.driver.find_elements(By.CSS_SELECTOR, "ul li, div[role='button']")
            
            for opt in options:
                if preferred_format.upper() in opt.text.upper():
                    self._js_click(opt)
                    time.sleep(2)
                    logger.info(f"Selected format: {preferred_format}")
                    return True
            
            if options:
                self._js_click(options[0])
                time.sleep(2)
                return True
                
        except Exception as e:
            logger.warning(f"Format selection failed: {e}")
        return False

    def _navigate_to_showtimes(self, movie_url: str, preferred_format: str = "2D", 
                               preferred_language: str = "TELUGU") -> bool:
        """Navigate to movie's showtime page."""
        try:
            self.driver.get(movie_url)
            time.sleep(3)
            
            # Click Book tickets
            for selector in ["//button[contains(., 'Book tickets')]", "//a[contains(., 'Book tickets')]"]:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    element.click()
                    break
                except:
                    continue
            else:
                logger.error("No Book tickets button found")
                return False
            
            time.sleep(3)
            self._handle_popups()
            self._select_language(preferred_language)  # Select preferred language
            self._select_format(preferred_format)
            time.sleep(3)
            return True
            
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False

    # =========================================================================
    # QUICK SCAN - Fast status detection
    # =========================================================================
    
    def quick_scan(self, movie_url: str, movie_title: str, 
                   preferred_format: str = "2D", preferred_language: str = "TELUGU") -> Optional[MovieStats]:
        """
        Fast scan: Get status counts (Fast Filling, Available, Sold Out).
        Does NOT enter seat layout - just analyzes CSS colors.
        """
        logger.info(f"Quick Scan: {movie_title}")
        
        if not self._navigate_to_showtimes(movie_url, preferred_format, preferred_language):
            return None
        
        logger.info("Scrolling page to load all theaters...")
        
        all_shows = {}  # (time, absY) -> show data
        page_height = self.driver.execute_script("return document.body.scrollHeight")
        logger.info(f"Page height: {page_height}px")
        
        # Scroll and collect
        current_scroll = 0
        while current_scroll < page_height + 1000:
            shows = self.driver.execute_script("""
                var shows = [];
                var timeRegex = /^\\d{1,2}:\\d{2}\\s*(AM|PM)?$/i;
                var scrollY = window.scrollY;
                
                // Check for orange colors (Fast Filling)
                var isOrange = function(c) { 
                    return c.includes("232, 169, 0") || c.includes("244, 130, 32") ||
                           c.includes("228, 150, 51") || c.includes("231, 162, 51");
                };
                
                document.querySelectorAll("div[class*='sc-1vhizuf-2']").forEach(function(el) {
                    var text = el.innerText.trim();
                    if (timeRegex.test(text)) {
                        var rect = el.getBoundingClientRect();
                        var absY = Math.round((scrollY + rect.top) / 50) * 50;
                        
                        var parent = el.parentElement;  // sc-1vhizuf-1 container
                        var parentClass = parent ? parent.className : '';
                        var parentStyle = parent ? window.getComputedStyle(parent) : null;
                        var parentBorder = parentStyle ? parentStyle.borderColor : '';
                        
                        var status = "AVAILABLE";
                        
                        // Check for Fast Filling badge (sc-1hrr1fj with color="#E8A900")
                        // This is a separate element near the showtime container
                        var grandparent = parent ? parent.parentElement : null;
                        var container = grandparent ? grandparent.parentElement : null;
                        var hasFastFillingBadge = false;
                        
                        // Look for the orange badge in parent hierarchy
                        var checkEl = el;
                        for (var d = 0; d < 5; d++) {
                            checkEl = checkEl.parentElement;
                            if (!checkEl) break;
                            // Look for badge element with sc-1hrr1fj class or color attr
                            var badges = checkEl.querySelectorAll("[class*='sc-1hrr1fj'], [color='#E8A900']");
                            if (badges.length > 0) {
                                hasFastFillingBadge = true;
                                break;
                            }
                        }
                        
                        // Check for disabled/sold out
                        // Class 'kwVuiS' indicates sold out (grey styling)
                        if (el.disabled || el.hasAttribute('disabled') || 
                            el.classList.contains('disabled') || el.classList.contains('sold-out') ||
                            parentClass.includes('disabled') || parentClass.includes('sold-out') ||
                            parentClass.includes('kwVuiS')) {
                            status = "SOLD OUT";
                        }
                        // Check for Fast Filling by badge, class, or orange border
                        else if (hasFastFillingBadge || 
                                 parentClass.includes('jmtHNK') || 
                                 isOrange(parentBorder)) {
                            status = "FAST FILLING";
                        }
                        
                        // Find cinema name
                        var cinemaName = "";
                        var searchEl = el;
                        for (var i = 0; i < 10; i++) {
                            searchEl = searchEl.parentElement;
                            if (!searchEl) break;
                            var links = searchEl.querySelectorAll('a');
                            for (var li = 0; li < links.length; li++) {
                                var href = links[li].getAttribute('href') || '';
                                if (href.includes('/venue')) {
                                    cinemaName = links[li].innerText.trim().split('\\n')[0];
                                    break;
                                }
                            }
                            if (cinemaName) break;
                        }
                        
                        shows.push({time: text, absY: absY, status: status, cinema: cinemaName});
                    }
                });
                return shows;
            """)
            
            for s in shows:
                key = (s['time'], s['absY'])
                if key not in all_shows:
                    all_shows[key] = s
            
            self.driver.execute_script("window.scrollBy(0, 200);")
            current_scroll += 200
            time.sleep(0.1)
        
        collected_shows = list(all_shows.values())
        logger.info(f"Collected {len(collected_shows)} shows")
        
        try:
            showtimes = []
            for show in collected_shows:
                status = ShowStatus.AVAILABLE
                if show['status'] == "FAST FILLING":
                    status = ShowStatus.FAST_FILLING
                elif show['status'] == "SOLD OUT":
                    status = ShowStatus.SOLD_OUT
                
                showtimes.append(ShowTime(
                    time=show['time'],
                    status=status,
                    cinema=show.get('cinema', '')
                ))
            
            # Calculate stats
            total = len(showtimes)
            fast_filling = sum(1 for s in showtimes if s.status == ShowStatus.FAST_FILLING)
            available = sum(1 for s in showtimes if s.status == ShowStatus.AVAILABLE)
            sold_out = sum(1 for s in showtimes if s.status == ShowStatus.SOLD_OUT)
            unknown = sum(1 for s in showtimes if s.status == ShowStatus.UNKNOWN)
            
            cinemas = set(s.cinema for s in showtimes if s.cinema)
            ff_pct = (fast_filling / total * 100) if total > 0 else 0
            occ_rate = ((fast_filling + sold_out) / total * 100) if total > 0 else 0
            
            logger.info(f"Total: {total}, Fast Filling: {fast_filling}, Available: {available}, Sold Out: {sold_out}")
            
            return MovieStats(
                movie=movie_title,
                url=movie_url,
                city=self.city,
                scrape_time=datetime.now().isoformat(),
                total_shows=total,
                fast_filling=fast_filling,
                available=available,
                sold_out=sold_out,
                unknown=unknown,
                fast_filling_percentage=round(ff_pct, 2),
                occupancy_rate=round(occ_rate, 2),
                shows=[asdict(s) for s in showtimes],
                cinemas_count=len(cinemas)
            )
            
        except Exception as e:
            logger.error(f"Quick scan failed: {e}", exc_info=True)
            return None

    # =========================================================================
    # DEEP SCAN - Seat count extraction via Konva.js
    # =========================================================================
    
    def _get_seat_counts(self) -> Optional[Dict]:
        """Extract seat data from Konva.js canvas."""
        time.sleep(5)
        return self.driver.execute_script("""
            if (typeof Konva === 'undefined' || !Konva.stages || !Konva.stages.length) {
                return null;
            }
            
            var seats = {total: 0, booked: 0, available: 0};
            
            function countSeats(node) {
                if (node.className === 'Rect' || node.className === 'Circle') {
                    var fill = '';
                    try { fill = node.fill ? node.fill() : ''; } catch(e) {}
                    
                    if (fill && fill !== 'transparent') {
                        seats.total++;
                        fill = fill.toLowerCase();
                        if (fill.includes('#e5e5e5') || fill.includes('#1ea83c') || 
                            fill.includes('#4caf50') || fill.includes('green')) {
                            seats.available++;
                        } else {
                            seats.booked++;
                        }
                    }
                }
                if (node.children) {
                    node.children.forEach(function(c) { countSeats(c); });
                }
            }
            
            Konva.stages.forEach(function(s) { countSeats(s); });
            return seats;
        """)
    
    def deep_scan(self, movie_url: str, movie_title: str, 
                  max_shows: int = 3, preferred_format: str = "2D") -> Optional[MovieStats]:
        """
        Deep scan: Enter seat layout and get exact seat counts.
        Slower but provides precise availability data.
        """
        logger.info(f"Deep Scan: {movie_title} (max {max_shows} shows)")
        
        if not self._navigate_to_showtimes(movie_url, preferred_format):
            return None
        
        time_regex = re.compile(r'^\d{1,2}:\d{2}\s*(AM|PM)?$', re.I)
        
        try:
            divs = self.driver.find_elements(By.CSS_SELECTOR, "[class*='sc-1vhizuf-2']")
            valid_divs = [d for d in divs if time_regex.match(d.text.strip())]
            total_shows = len(valid_divs)
            logger.info(f"Total showtimes found: {total_shows}")
        except:
            logger.error("Could not find showtimes")
            return None
        
        seat_data_list = []
        total_seats = 0
        
        for idx in range(min(max_shows, total_shows)):
            if idx > 0:
                logger.info(f"Reloading for show {idx + 1}/{min(max_shows, total_shows)}...")
                if not self._navigate_to_showtimes(movie_url, preferred_format):
                    continue
            
            try:
                divs = self.driver.find_elements(By.CSS_SELECTOR, "[class*='sc-1vhizuf-2']")
                current_valid = [d for d in divs if time_regex.match(d.text.strip())]
                
                if idx >= len(current_valid):
                    continue
                
                target = current_valid[idx]
                show_time = target.text.strip()
                logger.info(f"Processing {show_time}...")
                
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)
                time.sleep(1)
                self._js_click(target)
                time.sleep(3)
                
                # Select seat count
                try:
                    items = self.driver.find_elements(By.CSS_SELECTOR, "li")
                    for item in items:
                        if "2" in item.text.strip():
                            self._js_click(item)
                            time.sleep(1)
                            break
                except: pass
                
                # Click Select Seats
                try:
                    btns = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Select Seats')]")
                    for btn in btns:
                        if btn.is_displayed():
                            self._js_click(btn)
                            break
                except: pass
                
                time.sleep(10)
                seats = self._get_seat_counts()
                
                if seats and seats.get('total', 0) > 0:
                    occ_pct = (seats['booked'] / seats['total'] * 100) if seats['total'] > 0 else 0
                    
                    seat_data_list.append(SeatData(
                        showtime=show_time,
                        cinema=None,
                        total_seats=seats['total'],
                        booked_seats=seats['booked'],
                        available_seats=seats['available'],
                        occupancy_percentage=round(occ_pct, 2)
                    ))
                    
                    total_seats += seats['total']
                    logger.info(f"{seats['available']}/{seats['total']} available ({occ_pct:.1f}% occupied)")
                else:
                    logger.warning(f"No seat data for {show_time}")
                    
            except Exception as e:
                logger.error(f"Error processing show: {e}")
        
        return MovieStats(
            movie=movie_title,
            url=movie_url,
            city=self.city,
            scrape_time=datetime.now().isoformat(),
            total_shows=total_shows,
            fast_filling=0, available=0, sold_out=0, unknown=0,
            fast_filling_percentage=0, occupancy_rate=0,
            shows=[], cinemas_count=0,
            seat_data=[asdict(s) for s in seat_data_list],
            total_seats_scanned=total_seats
        )

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def save_results(self, stats: MovieStats, prefix: str = '') -> Path:
        """Save results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in stats.movie if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = self.output_dir / f"{prefix}{safe_title}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(asdict(stats), f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Saved to {filename}")
        return filename
    
    def generate_report(self, stats_list: List[MovieStats]) -> str:
        """Generate text report."""
        if not stats_list:
            return "No data to report"
        
        lines = [
            "=" * 60,
            "BO_ANALYTICS - SCREENING STATUS REPORT",
            "=" * 60,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"City: {self.city.upper()}",
            "=" * 60
        ]
        
        for stats in stats_list:
            lines.append(f"\n{stats.movie}")
            lines.append(f"   Total Showtimes: {stats.total_shows}")
            lines.append(f"   Fast Filling: {stats.fast_filling} ({stats.fast_filling_percentage}%)")
            lines.append(f"   Available: {stats.available}")
            lines.append(f"   Sold Out: {stats.sold_out}")
            
            if stats.seat_data:
                lines.append("   --- Deep Scan Data ---")
                lines.append(f"   Total Seats Scanned: {stats.total_seats_scanned}")
                for sd in stats.seat_data:
                    lines.append(f"      {sd['showtime']}: {sd['available_seats']}/{sd['total_seats']} available")
            
            lines.append("-" * 60)
        
        return "\n".join(lines)


def main():
    """Run scraper with command-line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(description='BookMyShow Scraper - Get show availability')
    
    # Movie selection - either by URL or by name
    parser.add_argument('--url', '-u', default=None,
                        help='BMS movie URL (optional if --movie is provided)')
    parser.add_argument('--movie', '-m', default=None,
                        help='Movie name to search for (e.g., "The Raja Saab")')
    
    # City selection - single or multiple
    parser.add_argument('--city', '-c', default='hyderabad',
                        help='City name (e.g., hyderabad, mumbai)')
    parser.add_argument('--cities', default=None,
                        help='Comma-separated list of cities (e.g., "hyderabad,vizag,vijayawada")')
    
    # Other options
    parser.add_argument('--title', '-t', default=None,
                        help='Movie title (auto-detected from URL/search)')
    parser.add_argument('--format', '-f', default='2D',
                        help='Preferred format (2D, 3D, IMAX, DOLBY)')
    parser.add_argument('--language', '-l', default='TELUGU',
                        help='Preferred language (TELUGU, HINDI, TAMIL, KANNADA, ENGLISH)')
    parser.add_argument('--deep', '-d', action='store_true',
                        help='Run deep scan (seat counts) instead of quick scan')
    parser.add_argument('--headless', action='store_true',
                        help='Run browser in headless mode')
    
    args = parser.parse_args()
    
    # Determine cities to scan
    if args.cities:
        cities = [c.strip() for c in args.cities.split(',')]
    else:
        cities = [args.city]
    
    # Determine movie title
    if args.title:
        movie_title = args.title
    elif args.movie:
        movie_title = args.movie
    elif args.url:
        parts = args.url.rstrip('/').split('/')
        movie_title = parts[-2].replace('-', ' ').title() if len(parts) > 2 else "Unknown"
    else:
        movie_title = "Unknown"
    
    print(f"\n{'='*60}")
    print(f"BookMyShow Scraper")
    print(f"{'='*60}")
    print(f"Movie: {movie_title}")
    print(f"Cities: {', '.join(cities)}")
    print(f"Mode: {'Deep Scan' if args.deep else 'Quick Scan'}")
    if args.movie:
        print(f"Search Mode: Auto-discover URL by movie name")
    print(f"{'='*60}\n")
    
    all_results = []
    
    for city in cities:
        print(f"\n--- Scanning {city.upper()} ---")
        
        scraper = BMSScraper(city=city, headless=args.headless)
        
        try:
            if not scraper.start():
                continue
            
            # Determine URL - either provided or search for it
            if args.url:
                movie_url = args.url
            elif args.movie:
                logger.info(f"Searching for '{args.movie}' in {city}...")
                movie_url = scraper._search_movie(args.movie)
                if not movie_url:
                    logger.warning(f"Movie not found in {city}, skipping...")
                    continue
            else:
                logger.error("Either --url or --movie must be provided")
                continue
            
            # Run scan
            if args.deep:
                result = scraper.deep_scan(movie_url, movie_title, preferred_format=args.format)
            else:
                result = scraper.quick_scan(movie_url, movie_title, preferred_format=args.format,
                                           preferred_language=args.language.upper())
            
            if result:
                prefix = f"{city}_" + ("deep_" if args.deep else "quick_")
                scraper.save_results(result, prefix=prefix)
                all_results.append(result)
                print(f"  Total: {result.total_shows}, FF: {result.fast_filling}, Avail: {result.available}, Sold: {result.sold_out}")
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            break
        finally:
            scraper.stop()
    
    # Print combined report
    if all_results:
        print("\n" + "="*60)
        print("COMBINED REPORT")
        print("="*60)
        for result in all_results:
            print(f"\n{result.city.upper()} - {result.movie_title}")
            print(f"  Shows: {result.total_shows} | FF: {result.fast_filling} | Avail: {result.available} | Sold: {result.sold_out}")


if __name__ == "__main__":
    main()
