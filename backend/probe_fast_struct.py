"""Probe to find the elusive Fast Filling element."""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import json

def probe_fast_filling_dom():
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
        
        # Find element containing specific text
        # Since we know it exists from previous probe
        try:
            # XPath to find text node containing 'FAST FILLING' that is NOT the legend
            # Legend usually is at the top. Let's get ALL elements and filter.
            
            els = driver.find_elements(By.XPATH, "//*[contains(text(), 'FAST FILLING') or contains(text(), 'Fast Filling')]")
            
            dump = []
            for i, el in enumerate(els):
                parent = el.find_element(By.XPATH, "..")
                grandparent = parent.find_element(By.XPATH, "..")
                
                dump.append({
                    "index": i,
                    "tag": el.tag_name,
                    "text": el.text,
                    "outerHTML": el.get_attribute('outerHTML'),
                    "parent_html": parent.get_attribute('outerHTML'),
                    "grandparent_class": grandparent.get_attribute('class'),
                    "location": el.location
                })
                
            with open("fast_filling_dom.json", "w", encoding='utf-8') as f:
                json.dump(dump, f, indent=2)
                
            print(f"Found {len(els)} elements with 'FAST FILLING'. Dumped to JSON.")
            
            # Also dump the body text count again
            print(f"Body text count: {driver.find_element(By.TAG_NAME, 'body').text.count('FAST FILLING')}")
            
        except Exception as e:
            print(f"Error: {e}")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    probe_fast_filling_dom()
