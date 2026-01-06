"""Screenshot probe."""
import undetected_chromedriver as uc
import time

def probe_screen():
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
            driver.find_elements_by_xpath("//button[contains(., 'Book tickets')]")[0].click() 
        except: 
            # Try JS click if standard fails
             driver.execute_script("document.querySelectorAll('button').forEach(b => b.innerText.includes('Book tickets') && b.click())")
        
        time.sleep(3)
        # Handle popups blindly
        try: driver.execute_script("document.querySelector('div[text=\"Continue\"]').click()") 
        except: pass
        
        time.sleep(3)
        driver.save_screenshot("page_debug.png")
        print("Saved page_debug.png")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    probe_screen()
