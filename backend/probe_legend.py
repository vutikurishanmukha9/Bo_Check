"""Probe script to reverse-engineer status classes from the Legend."""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import json

def probe_legend():
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
        
        # Click Book tickets to see showtimes + legend
        try:
            btn = driver.find_element(By.XPATH, "//button[contains(., 'Book tickets')]")
            driver.execute_script("arguments[0].click();", btn)
        except: pass
            
        time.sleep(3)
        try:
            driver.execute_script("document.evaluate(\"//div[text()='Continue']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()")
            time.sleep(2)
        except: pass
        
        try:
            driver.execute_script("document.querySelector('ul li').click()")
            time.sleep(2)
        except: pass
        
        time.sleep(3)
        
        # Locate Legend Items
        # Look for text "FAST FILLING"
        legend_info = {}
        
        try:
            # Find element with text 'FAST FILLING'
            ff_el = driver.find_element(By.XPATH, "//*[contains(text(), 'FAST FILLING') or contains(text(), 'Fast Filling')]")
            # The dot is likely a sibling or pseudo element of the parent
            parent = ff_el.find_element(By.XPATH, "..")
            
            legend_info["FAST_FILLING"] = {
                "text_html": ff_el.get_attribute('outerHTML'),
                "parent_html": parent.get_attribute('outerHTML'),
                "parent_class": parent.get_attribute('class')
            }
        except Exception as e:
            legend_info["FAST_FILLING_ERROR"] = str(e)
            
        try:
            # Find element with text 'AVAILABLE'
            av_el = driver.find_element(By.XPATH, "//*[contains(text(), 'AVAILABLE') or contains(text(), 'Available')]")
            parent = av_el.find_element(By.XPATH, "..")
            
            legend_info["AVAILABLE"] = {
                "text_html": av_el.get_attribute('outerHTML'),
                "parent_html": parent.get_attribute('outerHTML'),
                "parent_class": parent.get_attribute('class')
            }
        except Exception as e:
            legend_info["AVAILABLE_ERROR"] = str(e)
            
        with open("legend_dump.json", "w", encoding='utf-8') as f:
            json.dump(legend_info, f, indent=2)
            
        print("Dumped Legend info to legend_dump.json")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    probe_legend()
