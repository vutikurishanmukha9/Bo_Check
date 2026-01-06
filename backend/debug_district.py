"""Debug script to inspect District (Zomato) for movie data."""

import asyncio
from playwright.async_api import async_playwright

async def main():
    print("Debugging District (Zomato) Scraping...")
    
    # Target: Shambhala in Hyderabad
    # URL structure guess: https://www.zomato.com/district/movies/hyderabad/shambhala
    # Or just search
    
    cities = ["hyderabad"]
    
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()
        
        # Try main movies landing
        url = "https://www.zomato.com/events/hyderabad" # District redirects here often
        print(f"Navigating to {url}...")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            print(f"URL: {page.url}")
            await page.screenshot(path="district_home.png")
            
            # Check for movie cards
            cards = await page.locator("a[href*='/movies/']").all() # Guess
            print(f"Found {len(cards)} movie links.")
            
            if cards:
                # Click first one
                await cards[0].click()
                await page.wait_for_timeout(3000)
                print(f"Movie URL: {page.url}")
                await page.screenshot(path="district_movie.png")
                
                # Check for "Book" button and Price?
                text = await page.inner_text("body")
                if "₹" in text:
                    print("✅ Found Price symbol!")
                else:
                    print("❌ No price found.")
                    
        except Exception as e:
            print(f"Error: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
