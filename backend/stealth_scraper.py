"""Bo_Analytics - Scrape ALL showtimes from ALL theaters (Final Production)."""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import re
import json
import os

class BoAnalyticsScraper:
    """Production-ready scraper for BookMyShow multi-movie, multi-showtime data."""
    
    def __init__(self, city="hyderabad"):
        self.city = city
        self.driver = None
    
    def start(self):
        """Initialize browser with stealth settings."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
                
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.page_load_strategy = 'eager'
        
        self.driver = uc.Chrome(options=options)
        print("✅ Browser started")
    
    def stop(self):
        """Clean shutdown."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def js_click(self, element):
        self.driver.execute_script("arguments[0].click();", element)
    
    def get_seat_counts(self):
        """Extracts seat data from Konva.js canvas."""
        time.sleep(5) # Wait for canvas render
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
                        // Check for available colors (greens, grays)
                        if (fill.includes('#e5e5e5') || fill.includes('#1ea83c') || fill.includes('#4caf50') || fill.includes('green')) {
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
    
    def _nav_and_handle_popups(self, movie_url):
        """Internal helper to navigate and clear popups."""
        try:
            self.driver.get(movie_url)
            time.sleep(4)
            
            # Click Book tickets
            try:
                btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Book tickets')] | //a[contains(., 'Book tickets')]")
                self.js_click(btn)
                time.sleep(3)
            except:
                print("   ❌ No Book tickets button")
                return False
            
            # Continue Popup
            try:
                cont = self.driver.find_element(By.XPATH, "//div[text()='Continue']")
                self.js_click(cont)
                time.sleep(2)
            except:
                pass
            
            # Language/Format Filter
            try:
                opts = self.driver.find_elements(By.CSS_SELECTOR, "ul li")
                for o in opts[:5]:
                    if "2D" in o.text or "Telugu" in o.text or "Hindi" in o.text:
                        self.js_click(o)
                        time.sleep(2)
                        break
            except:
                pass
                
            time.sleep(3)
            return True
        except Exception as e:
            print(f"   ⚠️ Nav error: {e}")
            return False

    def scrape_movie(self, movie_url, movie_title, max_shows=3):
        """Scrape multiple showtimes for a movie."""
        print(f"\n🎬 {movie_title}")
        
        # 1. Initial Load to count showtimes
        if not self._nav_and_handle_popups(movie_url):
            return None
            
        time_re = re.compile(r'^\d{1,2}:\d{2}\s*(AM|PM)?$', re.I)
        total_shows = 0
        
        try:
            divs = self.driver.find_elements(By.CSS_SELECTOR, "[class*='sc-1vhizuf-2']")
            valid_indices = [i for i, d in enumerate(divs) if time_re.match(d.text.strip())]
            total_shows = len(valid_indices)
            print(f"   🎟️ Total showtimes found: {total_shows}")
        except:
            print("   ❌ Could not find showtimes")
            return None
            
        all_shows = []
        shows_processed = 0
        totals = {"total_seats": 0, "total_booked": 0, "total_available": 0}
        
        # 2. Loop through showtimes (Reloading each time)
        indices_to_scrape = valid_indices[:max_shows]
        
        for loop_idx, target_index in enumerate(indices_to_scrape):
            # Reload page for every showtime (including first, to be safe/consistent, or skip first if we are already there?)
            # Safer to reload if loop_idx > 0.
            
            if loop_idx > 0:
                print(f"   🔄 Reloading for show {loop_idx+1}/{len(indices_to_scrape)}...")
                if not self._nav_and_handle_popups(movie_url):
                    continue
            
            try:
                # Find elements again
                divs = self.driver.find_elements(By.CSS_SELECTOR, "[class*='sc-1vhizuf-2']")
                current_valid_divs = [d for d in divs if time_re.match(d.text.strip())]
                
                if loop_idx >= len(current_valid_divs):
                     print(f"      ❌ Index match failed")
                     continue
                     
                target_el = current_valid_divs[loop_idx] # Simple sequential access to valid shows
                show_time = target_el.text.strip()
                
                print(f"      📍 Processing {show_time}...", end=" ")
                
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_el)
                time.sleep(1)
                self.js_click(target_el)
                time.sleep(3)
                
                # Handle "How many seats"
                try:
                    items = self.driver.find_elements(By.CSS_SELECTOR, "li")
                    for item in items:
                        if "2" in item.text.strip():
                            self.js_click(item)
                            time.sleep(1)
                            break
                except: pass
                
                # Click Select Seats
                try:
                    btns = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Select Seats')]")
                    clicked = False
                    for btn in btns:
                        if btn.is_displayed():
                            self.js_click(btn)
                            clicked = True
                            break
                except: pass
                
                # Wait for seat layout
                time.sleep(10)
                
                seats = self.get_seat_counts()
                
                if seats and seats.get('total', 0) > 0:
                    all_shows.append({
                        "showtime": show_time,
                        "total": seats['total'],
                        "booked": seats['booked'],
                        "available": seats['available']
                    })
                    totals["total_seats"] += seats['total']
                    totals["total_booked"] += seats['booked']
                    totals["total_available"] += seats['available']
                    print(f"✅ {seats['available']}/{seats['total']} available")
                    shows_processed += 1
                else:
                    print("❌ No data")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
        
        return {
            "movie": movie_title,
            "shows_scraped": shows_processed,
            "total_showtimes_found": total_shows,
            "shows": all_shows,
            "aggregate": totals
        }

def main():
    print("=" * 60)
    print("🎬 Bo_Analytics - Final Production Run")
    print("=" * 60)
    
    scraper = BoAnalyticsScraper(city="hyderabad")
    
    try:
        scraper.start()
        
        # Scrape Dhurandhar - 2 Shows
        result = scraper.scrape_movie(
            "https://in.bookmyshow.com/movies/hyderabad/dhurandhar/ET00452447",
            "Dhurandhar",
            max_shows=2
        )
        
        if result:
            with open("final_multishow_results.json", "w") as f:
                json.dump(result, f, indent=2)
            print("\n💾 Saved: final_multishow_results.json")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.stop()
        print("\n✅ Done")

if __name__ == "__main__":
    main()
