"""Probe all text to find dates."""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import json

def probe_all_text():
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
            driver.execute_script("document.evaluate(\"//div[text()='Continue']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()")
            time.sleep(1)
        except: pass
        try:
            driver.execute_script("document.querySelector('ul li').click()")
            time.sleep(2)
        except: pass
        time.sleep(3)
        
        # Get all text from typical nav elements
        elements = driver.find_elements(By.CSS_SELECTOR, "div, span, li, a")
        
        candidates = []
        for el in elements:
            try:
                txt = el.text.strip()
                # fast check for date-like strings
                if len(txt) < 15 and (
                    "TODAY" in txt.upper() or 
                    "TOMORROW" in txt.upper() or 
                    any(x in txt.upper() for x in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"])
                ):
                    candidates.append({
                        "text": txt,
                        "tag": el.tag_name,
                        "class": el.get_attribute("class")
                    })
            except: pass
            
        with open("date_candidates.json", "w", encoding='utf-8') as f:
            json.dump(candidates, f, indent=2)
            
        print(f"Found {len(candidates)} date candidates")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    probe_all_text()
