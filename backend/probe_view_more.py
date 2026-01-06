"""Probe for View More buttons and Theater counts."""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

def probe_view_more():
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
        
        # Count Theaters
        theaters = driver.find_elements(By.CSS_SELECTOR, "[class*='sc-1qdowf4-0']")
        print(f"Theaters found: {len(theaters)}")
        
        # Check for View More
        keywords = ["View More", "Show All", "+", "More"]
        buttons = driver.find_elements(By.TAG_NAME, "div") # Searching divs/spans
        
        candidates = []
        for btn in buttons:
            try:
                txt = btn.text.strip()
                if txt in keywords or "View more" in txt.lower():
                    candidates.append(txt)
            except: pass
            
        print(f"Potential expansion buttons: {candidates}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    probe_view_more()
