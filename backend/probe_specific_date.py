"""Probe for Specific Date Text (e.g. tomorrow)."""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import datetime

def probe_specific_date():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.page_load_strategy = 'eager'
    
    driver = uc.Chrome(options=options)
    
    try:
        url = "https://in.bookmyshow.com/movies/hyderabad/dhurandhar/ET00452447"
        driver.get(url)
        time.sleep(5)
        
        # Click Book tickets
        try:
            driver.find_element(By.XPATH, "//button[contains(., 'Book tickets')] | //a[contains(., 'Book tickets')]").click()
        except: pass
        time.sleep(3)
        try:
            driver.execute_script("document.querySelector('div[text=\"Continue\"]').click()") 
        except: pass
        try:
            driver.execute_script("document.querySelector('ul li').click()")
        except: pass
        time.sleep(3)
        
        # Get Tomorrow's Day/Date
        # Today is Jan 6 (Tue) 2026? 
        # Wait, the user metadata says 2026-01-06.
        # So tomorrow is Jan 7.
        
        targets = ["07", "Wed", "Jan"]
        
        print(f"Searching for targets: {targets}")
        
        # Find ANY element with this text
        candidates = []
        all_els = driver.find_elements(By.XPATH, "//*[text()]")
        
        for el in all_els:
            try:
                txt = el.text.strip()
                if any(t in txt for t in targets) and len(txt) < 20:
                    candidates.append({
                        "text": txt,
                        "tag": el.tag_name,
                        "class": el.get_attribute("class"),
                        "outerHTML": el.get_attribute("outerHTML")
                    })
            except: pass
            
        print(f"Found {len(candidates)} candidates")
        for c in candidates[:10]:
            print(c)
            
    finally:
        driver.quit()

if __name__ == "__main__":
    probe_specific_date()
