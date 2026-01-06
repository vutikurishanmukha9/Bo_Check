"""Probe script to check for scroll loading and missing showtimes."""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import re
import json

def probe_scroll_loading():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.page_load_strategy = 'eager'
    
    driver = uc.Chrome(options=options)
    
    try:
        url = "https://in.bookmyshow.com/movies/hyderabad/dhurandhar/ET00452447"
        print(f"Navigating to {url}")
        driver.get(url)
        time.sleep(5)
        
        # Click Book tickets
        try:
            btn = driver.find_element(By.XPATH, "//button[contains(., 'Book tickets')] | //a[contains(., 'Book tickets')]")
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(3)
        except:
            print("No book tickets button found")
            return

        # Popups
        try:
            driver.execute_script("document.evaluate(\"//div[text()='Continue']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()")
            time.sleep(1)
        except: pass
        try:
            driver.execute_script("document.querySelector('ul li').click()")
            time.sleep(2)
        except: pass
        
        time.sleep(3)
        
        # Initial Count
        initial_shows = len(driver.find_elements(By.CSS_SELECTOR, "div[class*='sc-1vhizuf-2']"))
        print(f"Shows before scroll: {initial_shows}")
        
        # Scroll Loop
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4) # Wait for page to load
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            print("Scrolled...")
            
        # Count again
        final_shows = driver.find_elements(By.CSS_SELECTOR, "div[class*='sc-1vhizuf-2']")
        print(f"Shows after scroll: {len(final_shows)}")
        
        # Also check for "Fast Filling" text specifically in the whole body
        body_text = driver.find_element(By.TAG_NAME, "body").text
        match_ff = re.findall(r"FAST FILLING", body_text, re.I)
        print(f"Found 'FAST FILLING' text matches in body: {len(match_ff)}")
        
        # Dump all times found via Regex on body text to compare with our selector count
        times_in_text = re.findall(r"\d{1,2}:\d{2}\s*(?:AM|PM)?", body_text)
        print(f"Regex found {len(times_in_text)} time strings in visible text")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    probe_scroll_loading()
