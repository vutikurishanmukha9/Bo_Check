"""Bo_Analytics - Fast Filling Status Scraper (Computed Style)."""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import re
import json

class FastStatusScraper:
    """Scrapes showtime status using computed styles (color/border)."""
    
    def __init__(self, city="hyderabad"):
        self.city = city
        self.driver = None
    
    def start(self):
        if self.driver:
            try: self.driver.quit()
            except: pass
        
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.page_load_strategy = 'eager'
        
        self.driver = uc.Chrome(options=options)
        print("✅ Browser started (Fast Mode)")
    
    def stop(self):
        if self.driver:
            try: self.driver.quit()
            except: pass
        self.driver = None
        
    def js_click(self, element):
        self.driver.execute_script("arguments[0].click();", element)

    def scrape_status(self, movie_url, movie_title):
        print(f"\n⚡ Scanning Status: {movie_title}")
        self.driver.get(movie_url)
        time.sleep(4)
        
        # Click Book tickets
        try:
            btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Book tickets')] | //a[contains(., 'Book tickets')]")
            self.js_click(btn)
            time.sleep(3)
        except:
            print("   ❌ No Book tickets button")
            return None
        
        # Popups
        try:
            self.driver.find_element(By.XPATH, "//div[text()='Continue']").click()
            time.sleep(1)
        except: pass
        
        try:
            opts = self.driver.find_elements(By.CSS_SELECTOR, "ul li")
            for o in opts[:3]:
                if "2D" in o.text: o.click(); time.sleep(2); break
        except: pass
        
        time.sleep(3)
        
        # JS Script to analyze all showtimes in one go
        # We traverse the DOM looking for the time elements
        # And check their computed styles against known status colors
        # Orange/Fast Filling: rgb(232, 169, 0)
        # Green/Available: rgb(64, 212, 97)
        
        results = self.driver.execute_script("""
            var results = [];
            var timeRegex = /^\\d{1,2}:\\d{2}\\s*(AM|PM)?$/i;
            
            // Find all potential showtime pills (using the class user identified as well)
            // sc-1vhizuf-2 is the text, sc-1vhizuf-1 is likely the container
            var elements = document.querySelectorAll("div[class*='sc-1vhizuf-2']");
            
            elements.forEach(function(el) {
                var text = el.innerText.trim();
                if (timeRegex.test(text)) {
                    var style = window.getComputedStyle(el);
                    var color = style.color;
                    var borderColor = style.borderColor;
                    
                    // Check parent for border color too
                    var parent = el.parentElement;
                    var parentStyle = window.getComputedStyle(parent);
                    var parentColor = parentStyle.color;
                    var parentBorder = parentStyle.borderColor;
                    
                    var status = "AVAILABLE"; // Default assumption if visible
                    
                    // Helper to check for orange (Fast Filling)
                    // rgb(232, 169, 0) is #E8A900
                    var isOrange = function(c) { 
                        return c.includes("232, 169, 0") || c.includes("232, 169, 0"); 
                    };
                    
                    // Helper to check for Green (Available explicitly)
                    // rgb(64, 212, 97) is #40D461
                    var isGreen = function(c) {
                        return c.includes("64, 212, 97") || c.includes("31, 173, 62");
                    };
                    
                    if (isOrange(color) || isOrange(borderColor) || isOrange(parentColor) || isOrange(parentBorder)) {
                        status = "FAST FILLING";
                    } else if (isGreen(color) || isGreen(borderColor) || isGreen(parentColor) || isGreen(parentBorder)) {
                        status = "AVAILABLE (Green)";
                    }
                    
                    results.push({
                        time: text,
                        status: status,
                        debug_color: color,
                        debug_parent_border: parentBorder
                    });
                }
            });
            return results;
        """)
        
        fast_filling_count = 0
        total_count = len(results)
        
        print(f"   🎟️ Found {total_count} showtimes")
        
        for show in results:
            if show['status'] == "FAST FILLING":
                fast_filling_count += 1
                
        print(f"   🔥 Fast Filling: {fast_filling_count}")
        print(f"   ✅ Available: {total_count - fast_filling_count}")
        
        # Debug print first few
        if results:
            print("   🔍 Sample Data:", results[0])
            
        return {
            "movie": movie_title,
            "total_shows": total_count,
            "fast_filling": fast_filling_count,
            "shows": results
        }

def main():
    scraper = FastStatusScraper()
    try:
        scraper.start()
        result = scraper.scrape_status(
            "https://in.bookmyshow.com/movies/hyderabad/dhurandhar/ET00452447",
            "Dhurandhar"
        )
        if result:
            with open("fast_status_computed_results.json", "w") as f:
                json.dump(result, f, indent=2)
            print("Saved results.")
    finally:
        scraper.stop()

if __name__ == "__main__":
    main()
