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
            
            // Find all potential showtime pills
            var elements = document.querySelectorAll("div[class*='sc-1vhizuf-2']");
            
            elements.forEach(function(el) {
                var text = el.innerText.trim();
                if (timeRegex.test(text)) {
                    var style = window.getComputedStyle(el);
                    var color = style.color;
                    var borderColor = style.borderColor;
                    
                    var parent = el.parentElement;
                    var parentStyle = window.getComputedStyle(parent);
                    var parentColor = parentStyle.color;
                    var parentBorder = parentStyle.borderColor;
                    var parentBg = parentStyle.backgroundColor;
                    
                    var status = "AVAILABLE"; // Default
                    
                    var isOrange = function(c) { return c.includes("232, 169, 0") || c.includes("232, 169, 0"); };
                    var isGreen = function(c) { return c.includes("64, 212, 97") || c.includes("31, 173, 62"); };
                    var isGrey = function(c) { 
                        // Generic grey check (often 102, 102, 102 or similar, or 153...)
                        // BMS often uses #999 or #666 for disabled
                        return c.includes("153, 153, 153") || c.includes("102, 102, 102"); 
                    };
                    
                    if (isOrange(color) || isOrange(borderColor) || isOrange(parentColor) || isOrange(parentBorder)) {
                        status = "FAST FILLING";
                    } else if (isGreen(color) || isGreen(borderColor) || isGreen(parentColor) || isGreen(parentBorder)) {
                        status = "AVAILABLE";
                    } else if (isGrey(color) || isGrey(parentColor) || isGrey(parentBorder) || parentBg.includes("238, 238, 238")) {
                        status = "SOLD OUT";
                    }
                    
                    results.push({
                        time: text,
                        status: status,
                        debug_color: color
                    });
                }
            });
            return results;
        """)
        
        counts = {
            "fast_filling": 0,
            "available": 0,
            "sold_out": 0,
            "total": len(results)
        }
        
        for show in results:
            if show['status'] == "FAST FILLING":
                counts["fast_filling"] += 1
            elif show['status'] == "SOLD OUT":
                counts["sold_out"] += 1
            else:
                counts["available"] += 1
                
        print(f"   🎟️ Total: {counts['total']}")
        print(f"   🔥 Fast Filling: {counts['fast_filling']}")
        print(f"   ❌ Sold Out: {counts['sold_out']}")
        print(f"   ✅ Available: {counts['available']}")
            
        return {
            "movie": movie_title,
            "stats": counts,
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
