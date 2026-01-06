"""Debug script to inspect BMS HTML structure and screenshot."""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def main():
    print("Debugging BMS Ratings...")
    
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        # Use a large viewport to ensure desktop view
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        # Go to Hyderabad movies page
        url = "https://in.bookmyshow.com/explore/movies-hyderabad"
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000) # Wait for hydration
        
        # Scroll a bit to ensure lazy loading
        await page.mouse.wheel(0, 500)
        await page.wait_for_timeout(2000)
        
        # Take screenshot to verify VISUAL presence of ratings
        await page.screenshot(path="bms_list_view.png", full_page=False)
        print("Captured bms_list_view.png")
        
        # Get content
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")
        
        # Find all card-like text to see if rating numbers exist ANYWHERE
        text_dump = soup.get_text(" | ", strip=True)
        with open("bms_text_dump.txt", "w", encoding="utf-8") as f:
            f.write(text_dump)
            
        # Specific check for known rating patterns
        import re
        ratings = re.findall(r"(\d+(\.\d)?)/10", text_dump)
        print(f"Regex found {len(ratings)} potential ratings in page text: {ratings[:5]}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
