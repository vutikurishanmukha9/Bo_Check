"""Probe for Date Tabs."""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

def probe_dates():
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
        
        # Look for Date Container
        # Usually a list of dates at the top
        dates = driver.find_elements(By.CSS_SELECTOR, "div[class*='date-numeric'], div[class*='dates-wrapper'] li, a[class*='date']")
        
        # Try generic search for dates like "06", "07", "SUN", "MON"
        if not dates:
             dates = driver.find_elements(By.CSS_SELECTOR, ".slick-slide, [class*='date']")
             
        print(f"Potential Date Elements: {len(dates)}")
        for d in dates[:5]:
            print(f"Date: {d.text.replace(chr(10), ' ')}")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    probe_dates()
